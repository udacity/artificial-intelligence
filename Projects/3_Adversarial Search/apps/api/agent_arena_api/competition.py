"""Mirrored fixtures, persisted games, and leaderboard calculation."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Any

from agent_runner import DockerAgent
from isolation_engine import (
    BENCHMARK_STRATEGIES,
    BaselineController,
    BenchmarkController,
    GameResult,
    play_game,
    score_fixture,
)
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .config import Settings
from .database import Database
from .models import Agent, Fixture, Game, Submission, utcnow


def run_round(database: Database, settings: Settings) -> list[str]:
    """Synchronously play one fixture for every pair of active submissions."""

    with database.sessions() as session:
        agents = list(
            session.scalars(
                select(Agent).where(Agent.active_submission_id.is_not(None)).order_by(Agent.name)
            )
        )
        submissions = [session.get(Submission, agent.active_submission_id) for agent in agents]
        active = [submission for submission in submissions if submission is not None]
    if len(active) < 2:
        raise ValueError("at least two active submissions are required")

    fixture_ids: list[str] = []
    for submission_a, submission_b in combinations(active, 2):
        with database.sessions.begin() as session:
            fixture = Fixture(
                submission_a_id=submission_a.id,
                submission_b_id=submission_b.id,
                status="running",
            )
            session.add(fixture)
            session.flush()
            fixture_ids.append(fixture.id)
        _play_fixture(database, settings, fixture.id, submission_a, submission_b)
    return fixture_ids


def _play_fixture(
    database: Database,
    settings: Settings,
    fixture_id: str,
    submission_a: Submission,
    submission_b: Submission,
) -> None:
    try:
        game_a = play_game(
            controller_for(submission_a, settings, seed=101),
            controller_for(submission_b, settings, seed=202),
            time_limit_ms=settings.move_budget_ms,
        )
        game_b = play_game(
            controller_for(submission_b, settings, seed=303),
            controller_for(submission_a, settings, seed=404),
            time_limit_ms=settings.move_budget_ms,
        )
        with database.sessions.begin() as session:
            fixture = session.get(Fixture, fixture_id)
            assert fixture is not None
            session.add_all(
                [
                    game_model(fixture.id, 1, submission_a.id, submission_b.id, game_a),
                    game_model(fixture.id, 2, submission_b.id, submission_a.id, game_b),
                ]
            )
            fixture.status = "complete"
            fixture.completed_at = utcnow()
    except Exception:
        with database.sessions.begin() as session:
            fixture = session.get(Fixture, fixture_id)
            assert fixture is not None
            fixture.status = "failed"
            fixture.completed_at = utcnow()
        raise


def controller_for(submission: Submission, settings: Settings, seed: int) -> Any:
    if submission.execution_kind in {"random", "greedy", "minimax"}:
        return BaselineController(submission.execution_kind, seed=seed)
    if submission.execution_kind in BENCHMARK_STRATEGIES:
        return BenchmarkController(submission.execution_kind, seed=seed)
    return DockerAgent(Path(submission.source_path), settings.runner_image)


def game_model(
    fixture_id: str,
    leg_number: int,
    first_id: str,
    second_id: str,
    result: GameResult,
) -> Game:
    winner_id = first_id if result.winner_player == 0 else second_id
    return Game(
        fixture_id=fixture_id,
        leg_number=leg_number,
        first_submission_id=first_id,
        second_submission_id=second_id,
        winner_submission_id=winner_id,
        end_status=result.end_status,
        losing_reason=result.losing_reason,
        replay=result.replay_dicts(),
        engine_version=result.engine_version,
        ruleset_version=result.ruleset_version,
    )


def fixture_score(session: Session, fixture: Fixture) -> Any | None:
    games = list(
        session.scalars(select(Game).where(Game.fixture_id == fixture.id).order_by(Game.leg_number))
    )
    if len(games) != 2 or any(game.winner_submission_id is None for game in games):
        return None
    winners = tuple(
        0 if game.winner_submission_id == fixture.submission_a_id else 1 for game in games
    )
    return score_fixture((winners[0], winners[1]))


def build_leaderboard(
    session: Session,
    minimum_ranked_fixtures: int = 10,
) -> list[dict[str, Any]]:
    """Calculate points directly from completed fixtures at read time."""

    agents = list(session.scalars(select(Agent).order_by(Agent.name)))
    active_agents = [agent for agent in agents if agent.active_submission_id]
    entries: dict[str, dict[str, Any]] = {}
    for agent in active_agents:
        submission = session.get(Submission, agent.active_submission_id)
        if submission is None:
            continue
        entries[submission.id] = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "owner_name": agent.owner_name,
            "submission_id": submission.id,
            "submission_number": submission.number,
            "fixtures": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0,
            "recent_fixtures": [],
        }

    all_submissions = {item.id: item for item in session.scalars(select(Submission))}
    all_agents = {item.id: item for item in agents}
    fixtures = list(
        session.scalars(
            select(Fixture)
            .where(Fixture.status == "complete")
            .order_by(Fixture.completed_at.desc(), Fixture.id)
        )
    )
    for fixture in fixtures:
        scored = fixture_score(session, fixture)
        if scored is None or fixture.completed_at is None:
            continue
        for submission_id, points, opponent_id in (
            (fixture.submission_a_id, scored.points_a, fixture.submission_b_id),
            (fixture.submission_b_id, scored.points_b, fixture.submission_a_id),
        ):
            entry = entries.get(submission_id)
            if entry is None:
                continue
            entry["fixtures"] += 1
            entry["points"] += points
            if scored.is_draw:
                entry["draws"] += 1
                outcome = "D"
            elif points == 3:
                entry["wins"] += 1
                outcome = "W"
            else:
                entry["losses"] += 1
                outcome = "L"
            opponent_submission = all_submissions[opponent_id]
            opponent = all_agents[opponent_submission.agent_id]
            opponent_points = (
                scored.points_b if submission_id == fixture.submission_a_id else scored.points_a
            )
            entry["recent_fixtures"].append(
                {
                    "id": fixture.id,
                    "opponent_name": opponent.name,
                    "outcome": outcome,
                    "score": f"{points}-{opponent_points}",
                    "completed_at": fixture.completed_at,
                }
            )

    for entry in entries.values():
        fixtures_played = entry["fixtures"]
        entry["points_per_fixture"] = entry["points"] / fixtures_played if fixtures_played else 0.0
        entry["qualified"] = fixtures_played >= minimum_ranked_fixtures

    ordered = sorted(
        entries.values(),
        key=lambda item: (
            not item["qualified"],
            -item["points_per_fixture"],
            -item["points"],
            -item["wins"],
            item["agent_name"].lower(),
        ),
    )
    rank = 0
    for entry in ordered:
        if entry["qualified"]:
            rank += 1
            entry["rank"] = rank
        else:
            entry["rank"] = None
        entry["recent_fixtures"] = entry["recent_fixtures"][:5]
        entry["recent_form"] = [item["outcome"] for item in entry["recent_fixtures"]]
        del entry["recent_fixtures"]
    return ordered


def agent_fixture_history(session: Session, agent_id: str) -> list[dict[str, Any]]:
    submissions = list(
        session.scalars(
            select(Submission).where(Submission.agent_id == agent_id).order_by(Submission.number)
        )
    )
    submission_by_id = {submission.id: submission for submission in submissions}
    if not submission_by_id:
        return []
    submission_ids = tuple(submission_by_id)
    fixtures = list(
        session.scalars(
            select(Fixture)
            .where(
                Fixture.status == "complete",
                or_(
                    Fixture.submission_a_id.in_(submission_ids),
                    Fixture.submission_b_id.in_(submission_ids),
                ),
            )
            .order_by(Fixture.completed_at.desc(), Fixture.id)
        )
    )
    history: list[dict[str, Any]] = []
    for fixture in fixtures:
        scored = fixture_score(session, fixture)
        if scored is None or fixture.completed_at is None:
            continue
        agent_is_a = fixture.submission_a_id in submission_by_id
        own_id = fixture.submission_a_id if agent_is_a else fixture.submission_b_id
        opponent_id = fixture.submission_b_id if agent_is_a else fixture.submission_a_id
        own_points = scored.points_a if agent_is_a else scored.points_b
        opponent_points = scored.points_b if agent_is_a else scored.points_a
        outcome = "D" if scored.is_draw else "W" if own_points == 3 else "L"
        opponent_submission = session.get(Submission, opponent_id)
        assert opponent_submission is not None
        opponent = session.get(Agent, opponent_submission.agent_id)
        assert opponent is not None
        history.append(
            {
                "id": fixture.id,
                "submission_number": submission_by_id[own_id].number,
                "opponent_name": opponent.name,
                "opponent_submission_number": opponent_submission.number,
                "outcome": outcome,
                "score": f"{own_points}-{opponent_points}",
                "completed_at": fixture.completed_at,
            }
        )
    return history


def fixture_details(session: Session, fixture: Fixture) -> dict[str, Any]:
    submission_a = session.get(Submission, fixture.submission_a_id)
    submission_b = session.get(Submission, fixture.submission_b_id)
    assert submission_a is not None and submission_b is not None
    agent_a = session.get(Agent, submission_a.agent_id)
    agent_b = session.get(Agent, submission_b.agent_id)
    assert agent_a is not None and agent_b is not None
    games = list(
        session.scalars(select(Game).where(Game.fixture_id == fixture.id).order_by(Game.leg_number))
    )
    scored = fixture_score(session, fixture)
    winner_submission_id = None
    is_draw = False
    points_a = points_b = 0
    if scored is not None:
        points_a, points_b = scored.points_a, scored.points_b
        is_draw = scored.is_draw
        if scored.winner == 0:
            winner_submission_id = fixture.submission_a_id
        elif scored.winner == 1:
            winner_submission_id = fixture.submission_b_id
    return {
        "id": fixture.id,
        "submission_a_id": fixture.submission_a_id,
        "submission_b_id": fixture.submission_b_id,
        "agent_a_name": agent_a.name,
        "agent_b_name": agent_b.name,
        "status": fixture.status,
        "created_at": fixture.created_at,
        "completed_at": fixture.completed_at,
        "winner_submission_id": winner_submission_id,
        "is_draw": is_draw,
        "points_a": points_a,
        "points_b": points_b,
        "games": [
            {
                "id": game.id,
                "leg_number": game.leg_number,
                "first_submission_id": game.first_submission_id,
                "second_submission_id": game.second_submission_id,
                "winner_submission_id": game.winner_submission_id,
                "end_status": game.end_status,
                "losing_reason": game.losing_reason,
                "replay": game.replay,
                "engine_version": game.engine_version,
                "ruleset_version": game.ruleset_version,
                "started_at": game.started_at,
                "completed_at": game.completed_at,
            }
            for game in games
        ],
    }
