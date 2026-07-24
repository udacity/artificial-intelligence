from __future__ import annotations

from typing import Annotated

from agent_runner import DockerAgent
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from isolation_engine import ENGINE_VERSION, RULESET_VERSION
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .competition import agent_fixture_history, build_leaderboard, fixture_details, run_round
from .database import get_session
from .models import Agent, Fixture, Submission
from .schemas import (
    AgentCreate,
    AgentFixtureHistoryEntry,
    AgentResponse,
    FixtureResponse,
    HealthResponse,
    LeaderboardEntry,
    PracticeCreate,
    PracticeResponse,
    RecordResponse,
    RoundResponse,
    RulesResponse,
    SubmissionCreate,
    SubmissionResponse,
)
from .submissions import prepare_submission, run_practice, save_new_agent, save_submission

router = APIRouter(prefix="/api")
SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    database_status = "ready"
    try:
        with request.app.state.database.sessions() as session:
            session.scalar(select(Agent.id).limit(1))
    except OperationalError:
        database_status = "migration_required"
    return HealthResponse(
        database=database_status,
        runner=DockerAgent.diagnostic(settings.runner_image),
    )


@router.get("/rules", response_model=RulesResponse)
def rules(request: Request) -> RulesResponse:
    settings = request.app.state.settings
    return RulesResponse(
        move_budget_ms=settings.move_budget_ms,
        minimum_ranked_fixtures=settings.minimum_ranked_fixtures,
        engine_version=ENGINE_VERSION,
        ruleset_version=RULESET_VERSION,
        demo_owner_name=settings.demo_owner_name,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(request: Request, session: SessionDependency) -> list[LeaderboardEntry]:
    rows = build_leaderboard(session, request.app.state.settings.minimum_ranked_fixtures)
    return [LeaderboardEntry.model_validate(row) for row in rows]


@router.get("/agents", response_model=list[AgentResponse])
def agents(
    session: SessionDependency,
    owner_name: Annotated[str | None, Query(max_length=80)] = None,
) -> list[AgentResponse]:
    statement = select(Agent).order_by(Agent.owner_name, Agent.name)
    if owner_name:
        statement = statement.where(Agent.owner_name == owner_name)
    return [_agent_response(session, item) for item in session.scalars(statement)]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def agent(agent_id: str, session: SessionDependency) -> AgentResponse:
    item = session.get(Agent, agent_id)
    if item is None:
        raise HTTPException(status_code=404, detail="agent was not found")
    return _agent_response(session, item)


@router.get(
    "/agents/{agent_id}/fixtures",
    response_model=list[AgentFixtureHistoryEntry],
)
def agent_fixtures(
    agent_id: str,
    session: SessionDependency,
) -> list[AgentFixtureHistoryEntry]:
    if session.get(Agent, agent_id) is None:
        raise HTTPException(status_code=404, detail="agent was not found")
    return [
        AgentFixtureHistoryEntry.model_validate(item)
        for item in agent_fixture_history(session, agent_id)
    ]


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    payload: AgentCreate,
    request: Request,
    session: SessionDependency,
) -> AgentResponse:
    settings = request.app.state.settings
    try:
        prepared = prepare_submission(payload.source, settings)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not prepared.accepted:
        raise HTTPException(status_code=422, detail=prepared.validation)
    try:
        item = save_new_agent(
            session,
            settings,
            owner_name=payload.owner_name,
            name=payload.name,
            prepared=prepared,
        )
        session.commit()
        session.refresh(item)
        return _agent_response(session, item)
    except ValueError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post(
    "/agents/{agent_id}/submissions",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    agent_id: str,
    payload: SubmissionCreate,
    request: Request,
    session: SessionDependency,
) -> AgentResponse:
    item = session.get(Agent, agent_id)
    if item is None:
        raise HTTPException(status_code=404, detail="agent was not found")
    settings = request.app.state.settings
    try:
        prepared = prepare_submission(payload.source, settings)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not prepared.accepted:
        raise HTTPException(status_code=422, detail=prepared.validation)
    save_submission(session, settings, agent=item, prepared=prepared)
    session.commit()
    session.refresh(item)
    return _agent_response(session, item)


@router.post("/practice", response_model=PracticeResponse)
def practice(payload: PracticeCreate, request: Request) -> PracticeResponse:
    try:
        result = run_practice(
            payload.source,
            payload.baseline,
            payload.seed,
            request.app.state.settings,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return PracticeResponse.model_validate(result)


@router.get("/fixtures/featured", response_model=FixtureResponse | None)
def featured_fixture(session: SessionDependency) -> FixtureResponse | None:
    item = session.scalar(
        select(Fixture)
        .where(Fixture.status == "complete")
        .order_by(Fixture.completed_at.desc(), Fixture.id)
        .limit(1)
    )
    return FixtureResponse.model_validate(fixture_details(session, item)) if item else None


@router.get("/fixtures/{fixture_id}", response_model=FixtureResponse)
def fixture(fixture_id: str, session: SessionDependency) -> FixtureResponse:
    item = session.get(Fixture, fixture_id)
    if item is None:
        raise HTTPException(status_code=404, detail="fixture was not found")
    return FixtureResponse.model_validate(fixture_details(session, item))


@router.post("/competition/run-round", response_model=RoundResponse)
def run_competition_round(request: Request) -> RoundResponse:
    database = request.app.state.database
    try:
        fixture_ids = run_round(database, request.app.state.settings)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return RoundResponse(
        fixture_ids=fixture_ids,
        participant_count=_participant_count(len(fixture_ids)),
    )


def _agent_response(session: Session, item: Agent) -> AgentResponse:
    submissions = list(
        session.scalars(
            select(Submission)
            .where(Submission.agent_id == item.id)
            .order_by(Submission.number.desc())
        )
    )
    table = build_leaderboard(session)
    active_record = next(
        (row for row in table if row["submission_id"] == item.active_submission_id),
        None,
    )
    record = None
    if active_record:
        record = RecordResponse(
            fixtures=active_record["fixtures"],
            wins=active_record["wins"],
            draws=active_record["draws"],
            losses=active_record["losses"],
            points=active_record["points"],
        )
    return AgentResponse(
        id=item.id,
        owner_name=item.owner_name,
        name=item.name,
        active_submission_id=item.active_submission_id,
        created_at=item.created_at,
        submissions=[
            SubmissionResponse(
                id=submission.id,
                agent_id=submission.agent_id,
                number=submission.number,
                source_hash=submission.source_hash,
                execution_kind=submission.execution_kind,
                validation_result=submission.validation_result,
                created_at=submission.created_at,
                is_active=submission.id == item.active_submission_id,
            )
            for submission in submissions
        ],
        record=record,
    )


def _participant_count(fixture_count: int) -> int:
    count = 0
    while count * (count - 1) // 2 < fixture_count:
        count += 1
    return count
