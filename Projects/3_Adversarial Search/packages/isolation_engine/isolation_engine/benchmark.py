"""Trusted strategy variants used by the isolated local benchmark database."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import inf
from time import perf_counter
from typing import Literal

from .providers import MoveResponse
from .state import HEIGHT, WIDTH, Isolation, index_to_board_coordinates

StrategyMode = Literal["random", "weighted", "greedy", "fixed", "iterative"]
EvaluationName = Literal["mobility", "differential", "center", "territory", "partition"]


@dataclass(frozen=True)
class BenchmarkStrategy:
    key: str
    agent_name: str
    description: str
    mode: StrategyMode
    evaluation: EvaluationName = "differential"
    depth: int = 0
    alpha_beta: bool = False
    move_ordering: bool = False


BENCHMARK_STRATEGY_LIST = (
    BenchmarkStrategy(
        "bench_random",
        "Random-Uniform",
        "Uniform random legal action; establishes the lower-bound control.",
        "random",
    ),
    BenchmarkStrategy(
        "bench_weighted",
        "Random-Mobility",
        "Random action weighted by the player's mobility after the move.",
        "weighted",
        "mobility",
    ),
    BenchmarkStrategy(
        "bench_greedy_mob",
        "Greedy-Mobility",
        "One-ply choice maximizing only the player's next-move count.",
        "greedy",
        "mobility",
    ),
    BenchmarkStrategy(
        "bench_greedy_diff",
        "Greedy-Differential",
        "One-ply choice maximizing own mobility minus opponent mobility.",
        "greedy",
        "differential",
    ),
    BenchmarkStrategy(
        "bench_greedy_center",
        "Greedy-Center",
        "One-ply mobility differential with a small central-position bonus.",
        "greedy",
        "center",
    ),
    BenchmarkStrategy(
        "bench_mm1_mob",
        "Minimax-D1-Mobility",
        "Depth-1 minimax using own mobility; compares search framing with greedy play.",
        "fixed",
        "mobility",
        depth=1,
    ),
    BenchmarkStrategy(
        "bench_mm2_mob",
        "Minimax-D2-Mobility",
        "Depth-2 minimax using own mobility; isolates one extra search ply.",
        "fixed",
        "mobility",
        depth=2,
    ),
    BenchmarkStrategy(
        "bench_mm2_diff",
        "Minimax-D2-Differential",
        "Depth-2 minimax with mobility differential; isolates evaluation choice.",
        "fixed",
        "differential",
        depth=2,
    ),
    BenchmarkStrategy(
        "bench_ab2_diff",
        "AlphaBeta-D2",
        "Depth-2 alpha-beta with the same differential evaluation as minimax.",
        "fixed",
        "differential",
        depth=2,
        alpha_beta=True,
    ),
    BenchmarkStrategy(
        "bench_ab3_diff",
        "AlphaBeta-D3",
        "Depth-3 alpha-beta; isolates the value of an additional searched ply.",
        "fixed",
        "differential",
        depth=3,
        alpha_beta=True,
    ),
    BenchmarkStrategy(
        "bench_ab3_ordered",
        "AlphaBeta-D3-Ordered",
        "Depth-3 alpha-beta with heuristic move ordering for stronger pruning.",
        "fixed",
        "differential",
        depth=3,
        alpha_beta=True,
        move_ordering=True,
    ),
    BenchmarkStrategy(
        "bench_ab3_center",
        "AlphaBeta-D3-Center",
        "Strong ordered depth-3 alpha-beta with a center-aware evaluation.",
        "fixed",
        "center",
        depth=3,
        alpha_beta=True,
        move_ordering=True,
    ),
    BenchmarkStrategy(
        "bench_id_diff",
        "Iterative-AB-Differential",
        "Primary strong contender: ordered alpha-beta deepened to the safe deadline.",
        "iterative",
        "differential",
        depth=6,
        alpha_beta=True,
        move_ordering=True,
    ),
    BenchmarkStrategy(
        "bench_id_territory",
        "Territory-ID-AB",
        "Iterative ordered alpha-beta evaluating knight-reachable territory and mobility.",
        "iterative",
        "territory",
        depth=6,
        alpha_beta=True,
        move_ordering=True,
    ),
    BenchmarkStrategy(
        "bench_id_partition",
        "Partition-ID-AB",
        "Experimental iterative agent detecting separated regions and maximizing territory.",
        "iterative",
        "partition",
        depth=7,
        alpha_beta=True,
        move_ordering=True,
    ),
)
BENCHMARK_STRATEGIES = {strategy.key: strategy for strategy in BENCHMARK_STRATEGY_LIST}


class SearchDeadline(RuntimeError):
    pass


class BenchmarkController:
    """One configurable controller shared by all benchmark comparisons."""

    def __init__(self, strategy_key: str, seed: int = 0) -> None:
        try:
            self.strategy = BENCHMARK_STRATEGIES[strategy_key]
        except KeyError as error:
            raise ValueError(f"unknown benchmark strategy: {strategy_key}") from error
        self.random = random.Random(seed)
        self.player_id = 0

    def reset(self, player_id: int) -> None:
        self.player_id = player_id

    def close(self) -> None:
        return None

    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        actions = state.actions()
        if not actions:
            return MoveResponse(None)
        if self.strategy.mode == "random":
            return MoveResponse(self.random.choice(actions))
        if self.strategy.mode == "weighted":
            weights = [max(1, self._own_mobility(state.result(action))) for action in actions]
            return MoveResponse(self.random.choices(actions, weights=weights, k=1)[0])

        fallback = max(actions, key=lambda action: self._evaluate(state.result(action)))
        if state.locs[self.player_id] is None:
            return MoveResponse(self._opening_action(state, actions, fallback))
        if self.strategy.mode == "greedy":
            return MoveResponse(fallback)

        deadline = perf_counter() + max(0.001, (timeout_ms - 12) / 1000)
        if self.strategy.mode == "fixed":
            try:
                return MoveResponse(self._root_search(state, self.strategy.depth, deadline))
            except SearchDeadline:
                return MoveResponse(fallback)

        best_action = fallback
        for depth in range(1, self.strategy.depth + 1):
            try:
                best_action = self._root_search(state, depth, deadline)
            except SearchDeadline:
                break
        return MoveResponse(best_action)

    def _opening_action(self, state: Isolation, actions: list[int], fallback: int) -> int:
        center = (HEIGHT // 2, WIDTH // 2)
        ranked = sorted(
            actions,
            key=lambda action: (
                abs(index_to_board_coordinates(action)[0] - center[0])
                + abs(index_to_board_coordinates(action)[1] - center[1]),
                -self._evaluate(state.result(action)),
                action,
            ),
        )
        return ranked[0] if ranked else fallback

    def _root_search(self, state: Isolation, depth: int, deadline: float) -> int:
        self._check_deadline(deadline)
        actions = self._ordered_actions(state, deadline)
        best_action = actions[0]
        best_value = -inf
        alpha, beta = -inf, inf
        for action in actions:
            score = self._value(state.result(action), depth - 1, alpha, beta, deadline)
            if score > best_value:
                best_action, best_value = action, score
            if self.strategy.alpha_beta:
                alpha = max(alpha, best_value)
        return best_action

    def _value(
        self,
        state: Isolation,
        depth: int,
        alpha: float,
        beta: float,
        deadline: float,
    ) -> float:
        self._check_deadline(deadline)
        if state.terminal_test():
            return 1_000_000.0 if state.utility(self.player_id) > 0 else -1_000_000.0
        if depth <= 0:
            return self._evaluate(state)

        maximizing = state.player() == self.player_id
        value = -inf if maximizing else inf
        for action in self._ordered_actions(state, deadline):
            child_value = self._value(state.result(action), depth - 1, alpha, beta, deadline)
            if maximizing:
                value = max(value, child_value)
                alpha = max(alpha, value)
            else:
                value = min(value, child_value)
                beta = min(beta, value)
            if self.strategy.alpha_beta and alpha >= beta:
                break
        return value

    def _ordered_actions(self, state: Isolation, deadline: float) -> list[int]:
        actions = state.actions()
        if not self.strategy.move_ordering:
            return actions
        self._check_deadline(deadline)
        maximizing = state.player() == self.player_id
        return sorted(
            actions,
            key=lambda action: self._evaluate(state.result(action)),
            reverse=maximizing,
        )

    def _evaluate(self, state: Isolation) -> float:
        own_mobility = self._own_mobility(state)
        opponent_mobility = len(state.liberties(state.locs[1 - self.player_id]))
        if self.strategy.evaluation == "mobility":
            return float(own_mobility)
        differential = float(own_mobility - opponent_mobility)
        if self.strategy.evaluation == "differential":
            return differential
        if self.strategy.evaluation == "center":
            return differential * 2 + self._center_score(state.locs[self.player_id])

        own_region = self._reachable_region(state, state.locs[self.player_id])
        opponent_region = self._reachable_region(state, state.locs[1 - self.player_id])
        territory = float(len(own_region) - len(opponent_region))
        if self.strategy.evaluation == "territory":
            return differential * 2 + territory
        separated = own_region.isdisjoint(opponent_region)
        return territory * (8 if separated else 1) + differential * 2

    def _own_mobility(self, state: Isolation) -> int:
        return len(state.liberties(state.locs[self.player_id]))

    @staticmethod
    def _center_score(location: int | None) -> float:
        if location is None:
            return 0.0
        row, column = index_to_board_coordinates(location)
        return -(abs(row - (HEIGHT - 1) / 2) + abs(column - (WIDTH - 1) / 2))

    @staticmethod
    def _reachable_region(state: Isolation, location: int | None) -> set[int]:
        if location is None:
            return set()
        pending = list(state.liberties(location))
        reached: set[int] = set()
        while pending:
            cell = pending.pop()
            if cell in reached:
                continue
            reached.add(cell)
            pending.extend(
                next_cell for next_cell in state.liberties(cell) if next_cell not in reached
            )
        return reached

    @staticmethod
    def _check_deadline(deadline: float) -> None:
        if perf_counter() >= deadline:
            raise SearchDeadline
