"""Knight Isolation bitboard state.

Copyright (c) 2018 Udacity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, NamedTuple

WIDTH = 11
HEIGHT = 9
PADDED_WIDTH = WIDTH + 2
BITBOARD_SIZE = PADDED_WIDTH * HEIGHT - 2
ENGINE_VERSION = "agent-arena-isolation-1.0.0"
RULESET_VERSION = "knight-isolation-11x9-150ms-v1"

BLANK_BOARD = 0
_row = (1 << WIDTH) - 1
for _ in range(HEIGHT):
    BLANK_BOARD = (BLANK_BOARD << PADDED_WIDTH) | _row

SOUTH, NORTH, WEST, EAST = -PADDED_WIDTH, PADDED_WIDTH, 1, -1


class Action(IntEnum):
    """The eight legal knight offsets in the padded bitboard."""

    NNE = NORTH + NORTH + EAST
    ENE = EAST + NORTH + EAST
    ESE = EAST + SOUTH + EAST
    SSE = SOUTH + SOUTH + EAST
    SSW = SOUTH + SOUTH + WEST
    WSW = WEST + SOUTH + WEST
    WNW = WEST + NORTH + WEST
    NNW = NORTH + NORTH + WEST


ACTION_SET = set(Action)
CELL_INDICES = tuple(
    row * PADDED_WIDTH + column for row in range(HEIGHT) for column in range(WIDTH)
)


class Isolation(NamedTuple):
    """Immutable and hashable Knight Isolation state adapted from Udacity."""

    board: int = BLANK_BOARD
    ply_count: int = 0
    locs: tuple[int | None, int | None] = (None, None)

    def player(self) -> int:
        return self.ply_count % 2

    def actions(self) -> list[int]:
        location = self.locs[self.player()]
        if location is None:
            return self.liberties(None)
        return [
            int(action)
            for action in Action
            if location + int(action) >= 0 and self.board & (1 << (location + int(action)))
        ]

    def result(self, action: int) -> Isolation:
        current_player = self.player()
        location = self.locs[current_player]
        if location is not None and action not in ACTION_SET:
            raise ValueError(f"{action} is not a knight action")
        destination = int(action) if location is None else location + int(action)
        if destination < 0 or not self.board & (1 << destination):
            raise ValueError("invalid action: destination is blocked or off board")
        next_locs = list(self.locs)
        next_locs[current_player] = destination
        return Isolation(
            board=self.board ^ (1 << destination),
            ply_count=self.ply_count + 1,
            locs=(next_locs[0], next_locs[1]),
        )

    def terminal_test(self) -> bool:
        return not (self._has_liberties(0) and self._has_liberties(1))

    def utility(self, player_id: int) -> float:
        if not self.terminal_test():
            return 0.0
        player_is_active = player_id == self.player()
        active_has_liberties = self._has_liberties(self.player())
        active_player_wins = active_has_liberties == player_is_active
        return float("inf") if active_player_wins else float("-inf")

    def liberties(self, location: int | None) -> list[int]:
        cells = (
            range(BITBOARD_SIZE)
            if location is None
            else (location + int(action) for action in Action)
        )
        return [cell for cell in cells if cell >= 0 and self.board & (1 << cell)]

    def _has_liberties(self, player_id: int) -> bool:
        return any(self.liberties(self.locs[player_id]))

    def destination(self, action: int) -> int:
        location = self.locs[self.player()]
        return int(action) if location is None else location + int(action)

    def to_dict(self) -> dict[str, Any]:
        return {
            "board": str(self.board),
            "ply_count": self.ply_count,
            "locs": list(self.locs),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Isolation:
        locations = value.get("locs", [None, None])
        return cls(
            board=int(value["board"]),
            ply_count=int(value["ply_count"]),
            locs=(locations[0], locations[1]),
        )


def index_to_board_coordinates(index: int) -> tuple[int, int]:
    """Return top-left-origin row/column coordinates for a valid cell index."""

    bit_row, bit_column = divmod(index, PADDED_WIDTH)
    if bit_column >= WIDTH or bit_row >= HEIGHT:
        raise ValueError(f"{index} is a padding bit, not a board cell")
    return HEIGHT - 1 - bit_row, WIDTH - 1 - bit_column


def board_coordinates_to_index(row: int, column: int) -> int:
    if not (0 <= row < HEIGHT and 0 <= column < WIDTH):
        raise ValueError("board coordinates are out of range")
    return (HEIGHT - 1 - row) * PADDED_WIDTH + (WIDTH - 1 - column)
