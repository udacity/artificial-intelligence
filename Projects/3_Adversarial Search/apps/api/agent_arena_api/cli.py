from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from agent_runner import DockerAgent

from .competition import run_round
from .config import settings
from .database import Database
from .seed import seed_database


def main() -> int:
    parser = argparse.ArgumentParser(prog="agent-arena")
    parser.add_argument("command", choices=("seed", "run-round", "doctor"))
    args = parser.parse_args()

    if args.command == "doctor":
        print(
            json.dumps(
                {
                    "database": _database_diagnostic(),
                    "runner": DockerAgent.diagnostic(settings.runner_image),
                },
                indent=2,
            )
        )
        return 0

    database = Database.create(settings.database_url)
    try:
        if args.command == "seed":
            print(json.dumps(seed_database(database, settings), indent=2))
        elif args.command == "run-round":
            fixture_ids = run_round(database, settings)
            print(json.dumps({"fixtures": fixture_ids, "status": "complete"}, indent=2))
    finally:
        database.engine.dispose()
    return 0


def _database_diagnostic() -> dict[str, object]:
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        return {"available": True, "url": settings.database_url}
    path = Path(settings.database_url.removeprefix(prefix))
    if not path.exists():
        return {
            "available": False,
            "path": str(path),
            "message": "Run the Alembic migration first.",
        }
    expected = {"alembic_version", "agents", "submissions", "fixtures", "games"}
    try:
        with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
            rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in rows}
    except sqlite3.Error as error:
        return {"available": False, "path": str(path), "message": str(error)}
    if not expected.issubset(tables):
        return {
            "available": False,
            "path": str(path),
            "message": "The earlier beta schema is present; back it up and run the new migration.",
        }
    return {
        "available": True,
        "path": str(path),
        "message": "Simplified database schema is ready.",
    }


if __name__ == "__main__":
    raise SystemExit(main())
