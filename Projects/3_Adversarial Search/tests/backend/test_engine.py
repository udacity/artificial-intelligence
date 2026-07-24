from __future__ import annotations

from time import sleep

import pytest
from isolation_engine import (
    BLANK_BOARD,
    BaselineController,
    Isolation,
    MoveResponse,
    play_game,
    score_fixture,
)

from tests.conftest import FirstLegalController


def test_bitboard_opening_and_knight_actions() -> None:
    state = Isolation()
    assert state.board == BLANK_BOARD
    assert len(state.actions()) == 99
    opened = state.result(57).result(0)
    assert set(opened.actions()) == {25, 11, -15, -27, -25, -11, 15, 27}
    assert not opened.board & (1 << 57)
    assert not opened.board & 1


def test_result_is_immutable_and_hashable() -> None:
    state = Isolation()
    moved = state.result(57)
    assert state.ply_count == 0
    assert moved.ply_count == 1
    assert hash(state) != hash(moved)
    with pytest.raises(AttributeError):
        state.board = 0  # type: ignore[misc]


def test_terminal_utility_and_state_round_trip() -> None:
    state = Isolation()
    while not state.terminal_test():
        state = state.result(state.actions()[0])
    assert state.utility(0) in {float("inf"), float("-inf")}
    assert state.utility(0) == -state.utility(1)
    assert Isolation.from_dict(state.to_dict()) == state


@pytest.mark.parametrize(
    ("first", "second"),
    [("random", "greedy"), ("greedy", "minimax"), ("minimax", "random")],
)
def test_baselines_complete_games(first: str, second: str) -> None:
    result = play_game(
        BaselineController(first, seed=4),
        BaselineController(second, seed=9),
        time_limit_ms=500,
    )
    assert result.end_status == "game_over"
    assert len(result.replay) > 2
    assert result.replay[-1].outcome == "game_over"


class SlowController(FirstLegalController):
    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        sleep(0.005)
        return super().choose_action(state, timeout_ms)


class ErrorController(FirstLegalController):
    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        del state, timeout_ms
        raise RuntimeError("boom")


class EmptyController(FirstLegalController):
    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        del state, timeout_ms
        return MoveResponse(None)


class IllegalController(FirstLegalController):
    def choose_action(self, state: Isolation, timeout_ms: int) -> MoveResponse:
        del state, timeout_ms
        return MoveResponse(999)


@pytest.mark.parametrize(
    ("controller", "status"),
    [
        (SlowController(), "timeout"),
        (ErrorController(), "exception"),
        (EmptyController(), "timeout"),
        (IllegalController(), "invalid_action"),
    ],
)
def test_bad_action_outcomes(controller: FirstLegalController, status: str) -> None:
    result = play_game(controller, FirstLegalController(), time_limit_ms=1)
    assert result.end_status == status
    assert result.winner_player == 1
    assert result.replay[-1].outcome == status


@pytest.mark.parametrize(
    ("winners", "points"),
    [((0, 0), (3, 0)), ((0, 1), (1, 1)), ((1, 1), (0, 3))],
)
def test_fixture_points(winners: tuple[int, int], points: tuple[int, int]) -> None:
    result = score_fixture(winners)
    assert (result.points_a, result.points_b) == points


def test_one_replay_list_reconstructs_every_legal_move() -> None:
    result = play_game(FirstLegalController(), FirstLegalController(), time_limit_ms=150)
    state = Isolation()
    for frame in result.replay:
        assert frame.board == str(state.board)
        assert frame.player_locations == state.locs
        if frame.chosen_action is not None and frame.outcome is None:
            assert frame.chosen_action in state.actions()
            state = state.result(frame.chosen_action)
    assert result.replay[-1].outcome == "game_over"
