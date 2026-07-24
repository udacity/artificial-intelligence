from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    database: Literal["ready", "migration_required"]
    runner: dict[str, Any]


class RulesResponse(BaseModel):
    game: Literal["knight_isolation"] = "knight_isolation"
    board_width: int = 11
    board_height: int = 9
    runtime: str = "Python 3.12"
    move_budget_ms: int = 150
    minimum_ranked_fixtures: int = 10
    fixture_games: int = 2
    points: dict[str, int] = {"win": 3, "draw": 1, "loss": 0}
    engine_version: str
    ruleset_version: str
    demo_owner_name: str


class AgentCreate(BaseModel):
    owner_name: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1)


class SubmissionCreate(BaseModel):
    source: str = Field(min_length=1)


class PracticeCreate(BaseModel):
    source: str = Field(min_length=1)
    baseline: Literal["random", "greedy", "minimax"] = "greedy"
    seed: int = 17


class SubmissionResponse(BaseModel):
    id: str
    agent_id: str
    number: int
    source_hash: str
    execution_kind: str
    validation_result: dict[str, Any]
    created_at: datetime
    is_active: bool


class RecordResponse(BaseModel):
    fixtures: int
    wins: int
    draws: int
    losses: int
    points: int


class AgentResponse(BaseModel):
    id: str
    owner_name: str
    name: str
    active_submission_id: str | None
    created_at: datetime
    submissions: list[SubmissionResponse]
    record: RecordResponse | None = None


class LeaderboardEntry(BaseModel):
    rank: int | None
    agent_id: str
    agent_name: str
    owner_name: str
    submission_id: str
    submission_number: int
    fixtures: int
    wins: int
    draws: int
    losses: int
    points: int
    points_per_fixture: float
    qualified: bool
    recent_form: list[Literal["W", "D", "L"]]


class AgentFixtureHistoryEntry(BaseModel):
    id: str
    submission_number: int
    opponent_name: str
    opponent_submission_number: int
    outcome: Literal["W", "D", "L"]
    score: str
    completed_at: datetime


class PracticeResponse(BaseModel):
    status: str
    result: dict[str, Any]
    replay: list[dict[str, Any]]
    logs: list[dict[str, str]]


class GameResponse(BaseModel):
    id: str
    leg_number: int
    first_submission_id: str
    second_submission_id: str
    winner_submission_id: str | None
    end_status: str
    losing_reason: str
    replay: list[dict[str, Any]]
    engine_version: str
    ruleset_version: str
    started_at: datetime
    completed_at: datetime


class FixtureResponse(BaseModel):
    id: str
    submission_a_id: str
    submission_b_id: str
    agent_a_name: str
    agent_b_name: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    winner_submission_id: str | None
    is_draw: bool
    points_a: int
    points_b: int
    games: list[GameResponse]


class RoundResponse(BaseModel):
    fixture_ids: list[str]
    status: Literal["complete"] = "complete"
    participant_count: int
