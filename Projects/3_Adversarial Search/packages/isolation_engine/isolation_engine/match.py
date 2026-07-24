"""Authoritative game loop, canonical replay, and fixture scoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from time import perf_counter
from typing import Any

from .providers import (
    ControllerEmptyResponseError,
    ControllerTimeoutError,
    PlayerController,
)
from .state import ENGINE_VERSION, RULESET_VERSION, Isolation

MAX_LOG_CHARS = 8_192


@dataclass(frozen=True)
class ReplayFrame:
    """One board state plus the decision made from that state."""

    ply_index: int
    active_player: int
    board: str
    player_locations: tuple[int | None, int | None]
    chosen_action: int | None = None
    chosen_destination: int | None = None
    legal_actions: list[int] = field(default_factory=list)
    elapsed_ms: float = 0.0
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    outcome: str | None = None


@dataclass
class GameResult:
    winner_player: int
    loser_player: int
    end_status: str
    losing_reason: str
    replay: list[ReplayFrame] = field(default_factory=list)
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    engine_version: str = ENGINE_VERSION
    ruleset_version: str = RULESET_VERSION

    def replay_dicts(self) -> list[dict[str, Any]]:
        return [asdict(frame) for frame in self.replay]


@dataclass(frozen=True)
class FixtureResult:
    game_winners: tuple[int, int]
    points_a: int
    points_b: int
    winner: int | None
    is_draw: bool


def score_fixture(game_winners: tuple[int, int]) -> FixtureResult:
    wins_a = game_winners.count(0)
    if wins_a == 2:
        return FixtureResult(game_winners, 3, 0, 0, False)
    if wins_a == 0:
        return FixtureResult(game_winners, 0, 3, 1, False)
    return FixtureResult(game_winners, 1, 1, None, True)


def play_game(
    first: PlayerController,
    second: PlayerController,
    *,
    initial_state: Isolation | None = None,
    time_limit_ms: int = 150,
) -> GameResult:
    """Play one game and validate every proposed action outside the controller."""

    state = initial_state or Isolation()
    controllers = (first, second)
    replay = [_empty_frame(state)]
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    winner = 1
    loser = 0
    end_status = "game_over"
    losing_reason = "no legal moves"

    try:
        first.reset(0)
        second.reset(1)
        while not state.terminal_test():
            active = state.player()
            legal_actions = [int(action) for action in state.actions()]
            started = perf_counter()
            action: int | None = None
            stdout = ""
            stderr = ""
            try:
                response = controllers[active].choose_action(state, time_limit_ms)
                elapsed_ms = (perf_counter() - started) * 1000
                action = None if response.action is None else int(response.action)
                stdout = response.stdout[-MAX_LOG_CHARS:]
                stderr = response.stderr[-MAX_LOG_CHARS:]
                if elapsed_ms > time_limit_ms:
                    raise ControllerTimeoutError(
                        f"decision exceeded {time_limit_ms} ms ({elapsed_ms:.2f} ms)"
                    )
                if action is None:
                    raise ControllerEmptyResponseError("agent produced no action")
                if action not in legal_actions:
                    end_status = "invalid_action"
                    losing_reason = f"illegal action {action}"
                    winner, loser = 1 - active, active
                    replay[-1] = _decision_frame(
                        state,
                        action,
                        None,
                        legal_actions,
                        elapsed_ms,
                        stdout,
                        stderr,
                        end_status,
                    )
                    break
            except (ControllerTimeoutError, ControllerEmptyResponseError) as error:
                elapsed_ms = (perf_counter() - started) * 1000
                end_status = "timeout"
                losing_reason = str(error)
                winner, loser = 1 - active, active
                replay[-1] = _decision_frame(
                    state,
                    action,
                    None,
                    legal_actions,
                    elapsed_ms,
                    stdout,
                    stderr,
                    end_status,
                )
                break
            except Exception as error:  # submitted controller errors lose the game
                elapsed_ms = (perf_counter() - started) * 1000
                end_status = "exception"
                losing_reason = f"{type(error).__name__}: {error}"
                winner, loser = 1 - active, active
                replay[-1] = _decision_frame(
                    state,
                    action,
                    None,
                    legal_actions,
                    elapsed_ms,
                    stdout,
                    stderr,
                    end_status,
                )
                break

            destination = state.destination(action)
            replay[-1] = _decision_frame(
                state,
                action,
                destination,
                legal_actions,
                elapsed_ms,
                stdout,
                stderr,
                None,
            )
            stdout_parts.append(stdout)
            stderr_parts.append(stderr)
            state = state.result(action)
            replay.append(_empty_frame(state))
        else:
            winner = 0 if state.utility(0) > 0 else 1
            loser = 1 - winner
            replay[-1] = replace(replay[-1], outcome="game_over")
    finally:
        first.close()
        second.close()

    return GameResult(
        winner_player=winner,
        loser_player=loser,
        end_status=end_status,
        losing_reason=losing_reason,
        replay=replay,
        stdout_excerpt="\n".join(stdout_parts)[-MAX_LOG_CHARS:],
        stderr_excerpt="\n".join(stderr_parts)[-MAX_LOG_CHARS:],
    )


def _empty_frame(state: Isolation) -> ReplayFrame:
    return ReplayFrame(
        ply_index=state.ply_count,
        active_player=state.player(),
        board=str(state.board),
        player_locations=state.locs,
        legal_actions=[int(action) for action in state.actions()],
    )


def _decision_frame(
    state: Isolation,
    action: int | None,
    destination: int | None,
    legal_actions: list[int],
    elapsed_ms: float,
    stdout: str,
    stderr: str,
    outcome: str | None,
) -> ReplayFrame:
    return ReplayFrame(
        ply_index=state.ply_count,
        active_player=state.player(),
        board=str(state.board),
        player_locations=state.locs,
        chosen_action=action,
        chosen_destination=destination,
        legal_actions=legal_actions,
        elapsed_ms=round(elapsed_ms, 3),
        stdout_excerpt=stdout,
        stderr_excerpt=stderr,
        outcome=outcome,
    )
