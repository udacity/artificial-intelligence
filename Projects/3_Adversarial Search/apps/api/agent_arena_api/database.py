from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from fastapi import Request
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class Database:
    engine: Engine
    sessions: sessionmaker[Session]

    @classmethod
    def create(cls, url: str) -> Database:
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        engine = create_engine(url, connect_args=connect_args)
        if url.startswith("sqlite"):
            event.listen(engine, "connect", _enable_sqlite_foreign_keys)
        return cls(engine=engine, sessions=sessionmaker(engine, expire_on_commit=False))


def _enable_sqlite_foreign_keys(connection: object, _: object) -> None:
    cursor = connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session(request: Request) -> Generator[Session, None, None]:
    with request.app.state.database.sessions() as session:
        yield session
