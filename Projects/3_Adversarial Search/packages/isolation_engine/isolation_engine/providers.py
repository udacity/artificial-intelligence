"""Trusted controllers used by the Knight Isolation match loop.

The game rules are derived from the Udacity AIND Isolation project and remain
available under its MIT license; see ``state.py`` for the complete notice.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from .state import Isolation


class ControllerTimeoutError(TimeoutError):
    """Raised when a controller misses the external move deadline."""


class ControllerEmptyResponseError(RuntimeError):
    """Raised when a controller returns no action on a non-terminal state."""


@dataclass(frozen=True)
class MoveResponse:
    action: int | None
    stdout: str = ""
    stderr: str = ""


class PlayerController(Protocol):
    """The small interface shared by trusted baselines and Docker agents."""

    def reset(self, player_id: int) -> None: ...

    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse: ...

    def close(self) -> None: ...


class BaselineController:
    """A trusted Random, Greedy, or fixed-depth Minimax opponent."""

    def __init__(self, name: str, seed: int = 0, minimax_depth: int = 2) -> None:
        normalized = name.lower()
        if normalized not in {"random", "greedy", "minimax"}:
            raise ValueError(f"unknown baseline: {name}")
        self.name = normalized
        self.random = random.Random(seed)
        self.player_id = 0
        self.minimax_depth = minimax_depth

    def reset(self, player_id: int) -> None:
        self.player_id = player_id

    def close(self) -> None:
        return None

    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        del timeout_ms
        actions = state.actions()
        if not actions:
            return MoveResponse(None)
        if self.name == "random":
            return MoveResponse(self.random.choice(actions))
        if self.name == "greedy":
            return MoveResponse(
                max(actions, key=lambda action: self._mobility(state.result(action)))
            )
        if state.ply_count < 2:
            center = 57
            return MoveResponse(center if center in actions else actions[len(actions) // 2])
        return MoveResponse(self._minimax(state, self.minimax_depth))

    def _mobility(self, state: Isolation) -> int:
        return len(state.liberties(state.locs[self.player_id]))

    def _score(self, state: Isolation) -> int:
        own = len(state.liberties(state.locs[self.player_id]))
        other = len(state.liberties(state.locs[1 - self.player_id]))
        return own - other

    def _minimax(self, state: Isolation, depth: int) -> int:
        def value(position: Isolation, remaining: int) -> float:
            if position.terminal_test():
                return position.utility(self.player_id)
            if remaining == 0:
                return float(self._score(position))
            candidates = [
                value(position.result(action), remaining - 1) for action in position.actions()
            ]
            return max(candidates) if position.player() == self.player_id else min(candidates)

        return max(
            state.actions(),
            key=lambda action: value(state.result(action), depth - 1),
        )
