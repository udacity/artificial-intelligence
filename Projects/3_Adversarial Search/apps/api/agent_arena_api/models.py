from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Agent(Base):
    """Stable public identity for one competitor."""

    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("owner_name", "name", name="uq_owner_agent_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_name: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(100))
    active_submission_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Submission(Base):
    """Immutable source used by historical games."""

    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("agent_id", "number", name="uq_agent_submission"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    source_hash: Mapped[str] = mapped_column(String(64))
    source_path: Mapped[str] = mapped_column(Text)
    execution_kind: Mapped[str] = mapped_column(String(20), default="docker")
    validation_result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Fixture(Base):
    """Two mirrored games between the same submissions."""

    __tablename__ = "fixtures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    submission_a_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), index=True)
    submission_b_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="running", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Game(Base):
    """One leg and its single canonical replay."""

    __tablename__ = "games"
    __table_args__ = (UniqueConstraint("fixture_id", "leg_number", name="uq_fixture_leg"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    fixture_id: Mapped[str] = mapped_column(ForeignKey("fixtures.id"), index=True)
    leg_number: Mapped[int] = mapped_column(Integer)
    first_submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"))
    second_submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"))
    winner_submission_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    end_status: Mapped[str] = mapped_column(String(30))
    losing_reason: Mapped[str] = mapped_column(Text, default="")
    replay: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    engine_version: Mapped[str] = mapped_column(String(80))
    ruleset_version: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
