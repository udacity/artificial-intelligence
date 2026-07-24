from __future__ import annotations

import hashlib

from sqlalchemy import func, select

from .competition import run_round
from .config import Settings
from .database import Database
from .models import Agent, Fixture, Submission, utcnow

SEED_AGENTS = (
    (
        "31111111-1111-4111-8111-111111111111",
        "41111111-1111-4111-8111-111111111111",
        "oualid",
        "Atlas-AB",
        "minimax",
    ),
    (
        "32222222-2222-4222-8222-222222222222",
        "42222222-2222-4222-8222-222222222222",
        "oualid",
        "PartitionScout",
        "greedy",
    ),
    (
        "33333333-3333-4333-8333-333333333333",
        "43333333-3333-4333-8333-333333333333",
        "starter-kit",
        "GreedyFox",
        "greedy",
    ),
    (
        "34444444-4444-4444-8444-444444444444",
        "44444444-4444-4444-8444-444444444444",
        "starter-kit",
        "RandomKnight",
        "random",
    ),
)


def seed_database(database: Database, settings: Settings) -> dict[str, int]:
    with database.sessions.begin() as session:
        for agent_id, submission_id, owner_name, name, execution_kind in SEED_AGENTS:
            if session.get(Agent, agent_id) is not None:
                continue
            source_hash = hashlib.sha256(f"trusted:{execution_kind}:1".encode()).hexdigest()
            agent = Agent(
                id=agent_id,
                owner_name=owner_name,
                name=name,
                active_submission_id=submission_id,
            )
            submission = Submission(
                id=submission_id,
                agent_id=agent_id,
                number=1,
                source_hash=source_hash,
                source_path=f"builtin://{execution_kind}",
                execution_kind=execution_kind,
                validation_result={
                    "accepted": True,
                    "trusted_builtin": True,
                    "controller": execution_kind,
                },
                created_at=utcnow(),
            )
            session.add_all([agent, submission])

    with database.sessions() as session:
        fixture_count = session.scalar(select(func.count(Fixture.id))) or 0
    if fixture_count == 0:
        run_round(database, settings)

    with database.sessions() as session:
        return {
            "agents": session.scalar(select(func.count(Agent.id))) or 0,
            "submissions": session.scalar(select(func.count(Submission.id))) or 0,
            "fixtures": session.scalar(select(func.count(Fixture.id))) or 0,
        }
