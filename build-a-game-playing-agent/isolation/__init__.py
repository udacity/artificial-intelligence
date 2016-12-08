"""
This library provides a Python implementation of the game Isolation.
Isolation is a deterministic, two-player game of perfect information in
which the players alternate turns moving between cells on a square grid
(like a checkerboard).  Whenever either player occupies a cell, that
location is blocked for the rest of the game. The first player with no
legal moves loses, and the opponent is declared the winner.
"""

import io

# Make the Board class available at the root of the module for imports
from .isolation import Board


def game_as_text(winner, move_history, termination="", board=Board(1, 2)):
    """
    Generate a printable representation for a game of isolation.

    Parameters
    ----------
    winner : hashable
        One of the objects registered by the board object as a valid player.
        (i.e., `player` should be either board.__player_1__ or
        board.__player_2__).

    move_history : list<[(int, int), (int, int)]>
        A list containing an element for each turn in the game encoding the
        move applied by each player during their initiative on that turn.
        E.g., [(3,3), (1,1)] means that player_1 moved to position (3,3) and
        player_2 responded by moving to position (1,1)

    termination : str
        String indicating the reason (if any) that the game was terminated.
        Valid reasons for termination include "" (none), "timeout", and
        "illegal move".

    board : isolation.Board
        An instance of `isolation.Board` encoding the game state (e.g., player
        locations and blocked cells) for a game of isolation.

    Returns
    ----------
    str
        A string representation of a game of isolation.
    """

    ans = io.StringIO()

    for i, move in enumerate(move_history):
        p1_move = move[0]
        ans.write("%d." % i + " (%d,%d)\r\n" % p1_move)
        if p1_move != Board.NOT_MOVED:
            board.apply_move(p1_move)
        ans.write(board.print_board())

        if len(move) > 1:
            p2_move = move[1]
            ans.write("%d. ..." % i + " (%d, %d)\r\n" % p2_move)
            if p2_move != Board.NOT_MOVED:
                board.apply_move(p2_move)
            ans.write(board.print_board())

    ans.write(termination + "\r\n")

    ans.write("Winner: " + str(winner) + "\r\n")

    return ans.getvalue()
