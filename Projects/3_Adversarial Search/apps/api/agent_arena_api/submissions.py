"""Straight-line source validation, storage, and practice operations."""

from __future__ import annotations

import ast
import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_runner import DockerAgent
from isolation_engine import BaselineController, Isolation, play_game
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import Settings
from .models import Agent, Submission, new_id

ALLOWED_IMPORT_ROOTS = {
    "collections",
    "dataclasses",
    "functools",
    "heapq",
    "itertools",
    "math",
    "operator",
    "queue",
    "random",
    "statistics",
    "typing",
    "isolation_engine",
}


@dataclass(frozen=True)
class PreparedSubmission:
    source: bytes
    source_hash: str
    validation: dict[str, Any]

    @property
    def accepted(self) -> bool:
        return bool(self.validation.get("accepted"))


def normalize_source(source: str, max_bytes: int) -> bytes:
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    encoded = normalized.encode("utf-8")
    if len(encoded) > max_bytes:
        raise ValueError(f"agent.py exceeds the {max_bytes} byte beta limit")
    if b"\x00" in encoded:
        raise ValueError("agent.py contains a null byte")
    return encoded


def static_source_checks(source: bytes) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "syntax_valid": False,
        "custom_player_present": False,
        "get_action_present": False,
        "imports_allowed": False,
    }
    try:
        tree = ast.parse(source.decode("utf-8"), filename="agent.py")
    except (SyntaxError, UnicodeDecodeError) as error:
        checks["error"] = f"{type(error).__name__}: {error}"
        return checks
    checks["syntax_valid"] = True
    player_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "CustomPlayer"
        ),
        None,
    )
    checks["custom_player_present"] = player_class is not None
    checks["get_action_present"] = bool(
        player_class
        and any(
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == "get_action"
            for node in player_class.body
        )
    )
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    rejected = sorted({name for name in imports if name not in ALLOWED_IMPORT_ROOTS})
    checks["imports_allowed"] = not rejected
    checks["rejected_imports"] = rejected
    return checks


def prepare_submission(source: str, settings: Settings) -> PreparedSubmission:
    """Validate source without importing it into this Python process."""

    source_bytes = normalize_source(source, settings.max_source_bytes)
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    static = static_source_checks(source_bytes)
    validation: dict[str, Any] = {
        "accepted": False,
        "source_hash": source_hash,
        "static_contract": static,
        "sample_states": {},
        "scrimmage": {},
        "errors": [],
    }
    required = (
        "syntax_valid",
        "custom_player_present",
        "get_action_present",
        "imports_allowed",
    )
    if not all(static.get(name) for name in required):
        validation["errors"].append("The Python contract or import policy is invalid.")
        return PreparedSubmission(source_bytes, source_hash, validation)

    diagnostic = DockerAgent.diagnostic(settings.runner_image)
    validation["runner"] = diagnostic
    if not diagnostic["available"]:
        validation["errors"].append(diagnostic["message"])
        return PreparedSubmission(source_bytes, source_hash, validation)

    with temporary_source(settings, source_bytes) as path:
        try:
            states = validation_states()
            for label, state in states.items():
                controller = DockerAgent(path, settings.runner_image)
                try:
                    controller.reset(state.player())
                    response = controller.choose_action(state, settings.move_budget_ms)
                    legal_actions = state.actions()
                    legal = (
                        response.action in legal_actions
                        if legal_actions
                        else response.action is None
                    )
                    validation["sample_states"][label] = {
                        "legal_response": legal,
                        "action": response.action,
                    }
                finally:
                    controller.close()
            samples_passed = all(
                item["legal_response"] for item in validation["sample_states"].values()
            )
            if not samples_passed:
                validation["errors"].append("The agent returned an illegal sample action.")
                return PreparedSubmission(source_bytes, source_hash, validation)

            result = play_game(
                DockerAgent(path, settings.runner_image),
                BaselineController("greedy", seed=7),
                time_limit_ms=settings.move_budget_ms,
            )
            validation["scrimmage"] = {
                "completed_normally": result.end_status == "game_over",
                "end_status": result.end_status,
                "losing_reason": result.losing_reason,
            }
            if result.end_status != "game_over":
                validation["errors"].append(f"The Greedy scrimmage ended with {result.end_status}.")
                return PreparedSubmission(source_bytes, source_hash, validation)
        except Exception as error:
            validation["errors"].append(f"{type(error).__name__}: {error}")
            return PreparedSubmission(source_bytes, source_hash, validation)

    validation["accepted"] = True
    return PreparedSubmission(source_bytes, source_hash, validation)


def save_new_agent(
    session: Session,
    settings: Settings,
    *,
    owner_name: str,
    name: str,
    prepared: PreparedSubmission,
) -> Agent:
    if not prepared.accepted:
        raise ValueError("only an accepted submission can be stored")
    clean_owner = owner_name.strip()
    clean_name = name.strip()
    existing = session.scalar(
        select(Agent).where(
            func.lower(Agent.owner_name) == clean_owner.lower(),
            func.lower(Agent.name) == clean_name.lower(),
        )
    )
    if existing is not None:
        raise ValueError("this owner already has an agent with that name")
    agent = Agent(owner_name=clean_owner, name=clean_name)
    session.add(agent)
    session.flush()
    save_submission(session, settings, agent=agent, prepared=prepared)
    return agent


def save_submission(
    session: Session,
    settings: Settings,
    *,
    agent: Agent,
    prepared: PreparedSubmission,
) -> Submission:
    if not prepared.accepted:
        raise ValueError("only an accepted submission can be stored")
    number = (
        session.scalar(select(func.max(Submission.number)).where(Submission.agent_id == agent.id))
        or 0
    ) + 1
    submission_id = new_id()
    directory = settings.source_root / agent.id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{submission_id}.py"
    path.write_bytes(prepared.source)
    submission = Submission(
        id=submission_id,
        agent_id=agent.id,
        number=number,
        source_hash=prepared.source_hash,
        source_path=str(path),
        execution_kind="docker",
        validation_result=prepared.validation,
    )
    session.add(submission)
    session.flush()
    agent.active_submission_id = submission.id
    return submission


def run_practice(
    source: str,
    baseline: str,
    seed: int,
    settings: Settings,
) -> dict[str, Any]:
    source_bytes = normalize_source(source, settings.max_source_bytes)
    static = static_source_checks(source_bytes)
    required = ("syntax_valid", "custom_player_present", "get_action_present", "imports_allowed")
    if not all(static.get(name) for name in required):
        return {
            "status": "invalid",
            "result": {"reason": "The Python contract or import policy is invalid."},
            "replay": [],
            "logs": [{"level": "error", "message": "Static source validation failed."}],
        }
    diagnostic = DockerAgent.diagnostic(settings.runner_image)
    if not diagnostic["available"]:
        return {
            "status": "runner_unavailable",
            "result": {"reason": diagnostic["message"]},
            "replay": [],
            "logs": [{"level": "error", "message": diagnostic["message"]}],
        }
    with temporary_source(settings, source_bytes) as path:
        result = play_game(
            DockerAgent(path, settings.runner_image),
            BaselineController(baseline, seed=seed),
            time_limit_ms=settings.move_budget_ms,
        )
    return {
        "status": "complete" if result.end_status == "game_over" else result.end_status,
        "result": {
            "winner": "submitted" if result.winner_player == 0 else baseline,
            "end_status": result.end_status,
            "losing_reason": result.losing_reason,
            "seed": seed,
            "engine_version": result.engine_version,
            "ruleset_version": result.ruleset_version,
        },
        "replay": result.replay_dicts(),
        "logs": [
            {"level": "info", "message": f"Opponent: {baseline.title()}."},
            {"level": "success", "message": f"Game ended: {result.end_status}."},
        ],
    }


@contextmanager
def temporary_source(settings: Settings, source: bytes) -> Iterator[Path]:
    settings.temp_root.mkdir(parents=True, exist_ok=True)
    path = settings.temp_root / f"{new_id()}.py"
    path.write_bytes(source)
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def validation_states() -> dict[str, Isolation]:
    empty = Isolation()
    opening = empty.result(57)
    midgame = opening.result(0)
    for _ in range(4):
        if midgame.terminal_test():
            break
        midgame = midgame.result(midgame.actions()[0])
    terminal = Isolation()
    while not terminal.terminal_test():
        terminal = terminal.result(terminal.actions()[0])
    return {"empty": empty, "opening": opening, "midgame": midgame, "terminal": terminal}
