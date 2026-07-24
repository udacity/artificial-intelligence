from __future__ import annotations

import hashlib

from agent_arena_api.main import create_app
from agent_arena_api.models import Base
from agent_arena_api.seed import seed_database
from agent_arena_api.submissions import PreparedSubmission
from agent_runner import DockerAgent
from fastapi.testclient import TestClient
from isolation_engine import BaselineController, play_game

from tests.conftest import FirstLegalController

SOURCE = """class CustomPlayer:
    def get_action(self, state):
        actions = state.actions()
        return actions[0] if actions else None
"""


def fake_preparation(source: str, _settings: object) -> PreparedSubmission:
    source_bytes = source.encode()
    return PreparedSubmission(
        source=source_bytes,
        source_hash=hashlib.sha256(source_bytes).hexdigest(),
        validation={
            "accepted": True,
            "static_contract": {"syntax_valid": True},
            "sample_states": {"empty": {"legal_response": True}},
            "scrimmage": {"completed_normally": True},
        },
    )


def fake_practice(_source: str, baseline: str, seed: int, settings: object) -> dict:
    result = play_game(
        FirstLegalController(),
        BaselineController(baseline, seed=seed),
        time_limit_ms=settings.move_budget_ms,
    )
    return {
        "status": "complete",
        "result": {"end_status": result.end_status, "winner": "submitted"},
        "replay": result.replay_dicts(),
        "logs": [{"level": "success", "message": "Practice completed."}],
    }


def test_source_is_not_imported_by_fastapi(test_settings, monkeypatch, tmp_path) -> None:
    app = create_app(test_settings)
    Base.metadata.create_all(app.state.database.engine)
    sentinel = tmp_path / "backend-imported-source.txt"
    malicious = f"""open(r'{sentinel.as_posix()}', 'w').write('unsafe')
class CustomPlayer:
    def get_action(self, state):
        return state.actions()[0] if state.actions() else None
"""
    monkeypatch.setattr(
        DockerAgent,
        "diagnostic",
        classmethod(
            lambda _cls, _image: {
                "available": False,
                "code": "test_unavailable",
                "message": "Docker intentionally unavailable in this test.",
            }
        ),
    )
    with TestClient(app) as client:
        response = client.post(
            "/api/agents",
            json={"owner_name": "oualid", "name": "Unsafe", "source": malicious},
        )
    assert response.status_code == 422
    assert not sentinel.exists()


def test_submit_practice_compete_leaderboard_and_replay(
    test_settings,
    monkeypatch,
) -> None:
    test_settings.minimum_ranked_fixtures = 4
    app = create_app(test_settings)
    Base.metadata.create_all(app.state.database.engine)
    seed_database(app.state.database, test_settings)
    monkeypatch.setattr("agent_arena_api.api.prepare_submission", fake_preparation)
    monkeypatch.setattr("agent_arena_api.api.run_practice", fake_practice)
    monkeypatch.setattr(
        "agent_arena_api.competition.controller_for",
        lambda _submission, _settings, seed: FirstLegalController(),
    )

    with TestClient(app) as client:
        rules = client.get("/api/rules").json()
        assert rules["move_budget_ms"] == 150
        assert rules["minimum_ranked_fixtures"] == 4
        initial_table = client.get("/api/leaderboard").json()
        assert len(initial_table) == 4
        assert all(row["qualified"] is False for row in initial_table)

        created = client.post(
            "/api/agents",
            json={"owner_name": "oualid", "name": "Smoke Agent", "source": SOURCE},
        )
        assert created.status_code == 201
        agent = created.json()
        first_submission_id = agent["active_submission_id"]
        assert agent["submissions"][0]["is_active"] is True
        assert SOURCE not in created.text
        assert "source_path" not in created.text

        versioned = client.post(
            f"/api/agents/{agent['id']}/submissions",
            json={"source": f"{SOURCE}\n# immutable version 2\n"},
        )
        assert versioned.status_code == 201
        agent = versioned.json()
        submission_id = agent["active_submission_id"]
        assert submission_id != first_submission_id
        assert [item["number"] for item in agent["submissions"]] == [2, 1]
        assert agent["submissions"][0]["is_active"] is True
        assert agent["submissions"][1]["is_active"] is False

        practice = client.post(
            "/api/practice",
            json={"source": SOURCE, "baseline": "greedy", "seed": 17},
        )
        assert practice.status_code == 200
        assert practice.json()["status"] == "complete"
        assert practice.json()["replay"]

        round_result = client.post("/api/competition/run-round")
        assert round_result.status_code == 200
        fixture_ids = round_result.json()["fixture_ids"]
        assert len(fixture_ids) == 10

        fixture = client.get(f"/api/fixtures/{fixture_ids[0]}").json()
        assert fixture["status"] == "complete"
        assert fixture["points_a"] in {0, 1, 3}
        assert len(fixture["games"]) == 2
        assert all(game["replay"] for game in fixture["games"])

        table = client.get("/api/leaderboard").json()
        smoke = next(row for row in table if row["submission_id"] == submission_id)
        assert smoke["fixtures"] == 4
        assert smoke["points"] >= 0
        assert smoke["qualified"] is True
        assert smoke["rank"] is not None
        assert smoke["points_per_fixture"] == smoke["points"] / smoke["fixtures"]

        history = client.get(f"/api/agents/{agent['id']}/fixtures")
        assert history.status_code == 200
        assert len(history.json()) == 4
        assert {item["submission_number"] for item in history.json()} == {2}
        assert all(item["opponent_name"] for item in history.json())

        featured = client.get("/api/fixtures/featured")
        assert featured.status_code == 200
        assert len(featured.json()["games"]) == 2
