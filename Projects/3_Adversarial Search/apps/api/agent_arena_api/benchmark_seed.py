"""Seed only the isolated benchmark database with trusted comparison agents."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict

from isolation_engine import BENCHMARK_STRATEGY_LIST
from sqlalchemy import func, select

from .config import settings
from .database import Database
from .models import Agent, Fixture, Submission

BENCHMARK_OWNER = "benchmark-lab"
BENCHMARK_NAMESPACE = uuid.UUID("f0e2dbd3-9718-46ed-9890-f9dc4329886c")


def benchmark_id(kind: str, strategy_key: str) -> str:
    return str(uuid.uuid5(BENCHMARK_NAMESPACE, f"{kind}:{strategy_key}"))


def seed_benchmark_database(database: Database) -> dict[str, int]:
    with database.sessions.begin() as session:
        for strategy in BENCHMARK_STRATEGY_LIST:
            agent_id = benchmark_id("agent", strategy.key)
            submission_id = benchmark_id("submission", strategy.key)
            if session.get(Agent, agent_id) is not None:
                continue
            agent = Agent(
                id=agent_id,
                owner_name=BENCHMARK_OWNER,
                name=strategy.agent_name,
                active_submission_id=submission_id,
            )
            submission = Submission(
                id=submission_id,
                agent_id=agent_id,
                number=1,
                source_hash=hashlib.sha256(
                    f"trusted-benchmark:{strategy.key}:1".encode()
                ).hexdigest(),
                source_path=f"builtin://benchmark/{strategy.key}",
                execution_kind=strategy.key,
                validation_result={
                    "accepted": True,
                    "trusted_benchmark": True,
                    "strategy": asdict(strategy),
                },
            )
            session.add_all([agent, submission])

    with database.sessions() as session:
        return {
            "agents": session.scalar(select(func.count(Agent.id))) or 0,
            "submissions": session.scalar(select(func.count(Submission.id))) or 0,
            "fixtures": session.scalar(select(func.count(Fixture.id))) or 0,
        }


def main() -> int:
    database = Database.create(settings.database_url)
    try:
        print(json.dumps(seed_benchmark_database(database), indent=2))
    finally:
        database.engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
