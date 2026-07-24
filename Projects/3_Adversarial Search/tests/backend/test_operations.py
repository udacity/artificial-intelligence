from __future__ import annotations

import hashlib

from agent_arena_api.competition import build_leaderboard, run_round
from agent_arena_api.database import Database
from agent_arena_api.models import Agent, Base, Submission
from agent_arena_api.seed import seed_database
from agent_arena_api.submissions import PreparedSubmission, save_new_agent, save_submission


def accepted(source: str) -> PreparedSubmission:
    source_bytes = source.encode()
    return PreparedSubmission(
        source=source_bytes,
        source_hash=hashlib.sha256(source_bytes).hexdigest(),
        validation={"accepted": True},
    )


def test_new_valid_submission_becomes_active_without_mutating_previous(test_settings) -> None:
    database = Database.create(test_settings.database_url)
    Base.metadata.create_all(database.engine)
    with database.sessions.begin() as session:
        agent = save_new_agent(
            session,
            test_settings,
            owner_name="oualid",
            name="SimpleAgent",
            prepared=accepted("class CustomPlayer: pass"),
        )
        first_id = agent.active_submission_id
        first_hash = session.get(Submission, first_id).source_hash
        second = save_submission(
            session,
            test_settings,
            agent=agent,
            prepared=accepted("class CustomPlayer:\n    pass\n"),
        )
        assert agent.active_submission_id == second.id
        assert session.get(Submission, first_id).source_hash == first_hash
    with database.sessions() as session:
        stored = session.get(Agent, agent.id)
        assert stored.active_submission_id == second.id


def test_round_is_balanced_and_leaderboard_is_derived_from_games(test_settings) -> None:
    database = Database.create(test_settings.database_url)
    Base.metadata.create_all(database.engine)
    seed_database(database, test_settings)
    fixture_ids = run_round(database, test_settings)
    assert len(fixture_ids) == 6
    with database.sessions() as session:
        table = build_leaderboard(session)
    assert len(table) == 4
    assert {entry["fixtures"] for entry in table} == {6}
    assert all(entry["points"] >= 0 for entry in table)
    assert all(entry["rank"] is None for entry in table)

    with database.sessions() as session:
        qualified_table = build_leaderboard(session, minimum_ranked_fixtures=6)
    assert [entry["rank"] for entry in qualified_table] == [1, 2, 3, 4]
    ordering_keys = [
        (
            -entry["points_per_fixture"],
            -entry["points"],
            -entry["wins"],
            entry["agent_name"].lower(),
        )
        for entry in qualified_table
    ]
    assert ordering_keys == sorted(ordering_keys)
