"""
This file contains the `Board` class, which implements the rules for the
game Isolation as described in lecture, modified so that the players move
like knights in chess rather than queens.

You MAY use and modify this class, however ALL function signatures must
remain compatible with the defaults provided, and none of your changes will
be available to project reviewers.
"""

import timeit

from copy import deepcopy
from copy import copy


TIME_LIMIT_MILLIS = 200


class Board(object):
    """
    Implement a model for the game Isolation assuming each player moves like
    a knight in chess.

    Parameters
    ----------
    player_1 : object
        An object with a get_move() function. This is the only function
        directly called by the Board class for each player.

    player_2 : object
        An object with a get_move() function. This is the only function
        directly called by the Board class for each player.

    width : int (optional)
        The number of columns that the board should have.

    height : int (optional)
        The number of rows that the board should have.
    """
    BLANK = 0
    NOT_MOVED = None

    def __init__(self, player_1, player_2, width=7, height=7):
        self.width = width
        self.height = height
        self.move_count = 0
        self.__player_1__ = player_1
        self.__player_2__ = player_2
        self.__active_player__ = player_1
        self.__inactive_player__ = player_2
        self.__board_state__ = [[Board.BLANK for i in range(width)] for j in range(height)]
        self.__last_player_move__ = {player_1: Board.NOT_MOVED, player_2: Board.NOT_MOVED}
        self.__player_symbols__ = {Board.BLANK: Board.BLANK, player_1: 1, player_2: 2}

    @property
    def active_player(self):
        """
        The object registered as the player holding initiative in the
        current game state.
        """
        return self.__active_player__

    @property
    def inactive_player(self):
        """
        The object registered as the player in waiting for the current
        game state.
        """
        return self.__inactive_player__

    def get_opponent(self, player):
        """
        Return the opponent of the supplied player.

        Parameters
        ----------
        player : object
            An object registered as a player in the current game. Raises an
            error if the supplied object is not registered as a player in
            this game.

        Returns
        ----------
        object
            The opponent of the input player object.
        """
        if player == self.__active_player__:
            return self.__inactive_player__
        elif player == self.__inactive_player__:
            return self.__active_player__
        raise RuntimeError("`player` must be an object registered as a player in the current game.")

    def copy(self):
        """ Return a deep copy of the current board. """
        new_board = Board(self.__player_1__, self.__player_2__, width=self.width, height=self.height)
        new_board.move_count = self.move_count
        new_board.__active_player__ = self.__active_player__
        new_board.__inactive_player__ = self.__inactive_player__
        new_board.__last_player_move__ = copy(self.__last_player_move__)
        new_board.__player_symbols__ = copy(self.__player_symbols__)
        new_board.__board_state__ = deepcopy(self.__board_state__)
        return new_board

    def forecast_move(self, move):
        """
        Return a deep copy of the current game with an input move applied to
        advance the game one ply.

        Parameters
        ----------
        move : (int, int)
            A coordinate pair (row, column) indicating the next position for
            the active player on the board.

        Returns
        ----------
        `isolation.Board`
            A deep copy of the board with the input move applied.
        """
        new_board = self.copy()
        new_board.apply_move(move)
        return new_board

    def move_is_legal(self, move):
        """
        Test whether a move is legal in the current game state.

        Parameters
        ----------
        move : (int, int)
            A coordinate pair (row, column) indicating the next position for
            the active player on the board.

        Returns
        ----------
        bool
            Returns True if the move is legal, False otherwise
        """
        row, col = move
        return 0 <= row < self.height and \
               0 <= col < self.width and \
               self.__board_state__[row][col] == Board.BLANK

    def get_blank_spaces(self):
        """
        Return a list of the locations that are still available on the board.
        """
        return [(i, j) for j in range(self.width) for i in range(self.height)
            if self.__board_state__[i][j] == Board.BLANK]

    def get_player_location(self, player):
        """
        Find the current location of the specified player on the board.

        Parameters
        ----------
        player : object
            An object registered as a player in the current game.

        Returns
        ----------
        (int, int)
            The coordinate pair (row, column) of the input player.
        """
        return self.__last_player_move__[player]

    def get_legal_moves(self, player=None):
        """
        Return the list of all legal moves for the specified player.

        Parameters
        ----------
        player : object (optional)
            An object registered as a player in the current game. If None,
            return the legal moves for the active player on the board.

        Returns
        ----------
        list<(int, int)>
            The list of coordinate pairs (row, column) of all legal moves
            for the player constrained by the current game state.
        """
        if player is None:
            player = self.active_player
        return self.__get_moves__(self.__last_player_move__[player])

    def apply_move(self, move):
        """
        Move the active player to a specified location.

        Parameters
        ----------
        move : (int, int)
            A coordinate pair (row, column) indicating the next position for
            the active player on the board.

        Returns
        ----------
        None
        """
        row, col = move
        self.__last_player_move__[self.active_player] = move
        self.__board_state__[row][col] = self.__player_symbols__[self.active_player]
        self.__active_player__, self.__inactive_player__ = self.__inactive_player__, self.__active_player__
        self.move_count += 1

    def is_winner(self, player):
        """ Test whether the specified player has won the game. """
        return player == self.inactive_player and not self.get_legal_moves(self.active_player)

    def is_loser(self, player):
        """ Test whether the specified player has lost the game. """
        return player == self.active_player and not self.get_legal_moves(self.active_player)

    def utility(self, player):
        """
        Returns the utility of the current game state from the perspective
        of the specified player.

                    /  +infinity,   "player" wins
        utility =  |   -infinity,   "player" loses
                    \          0,    otherwise

        Parameters
        ----------
        player : object (optional)
            An object registered as a player in the current game. If None,
            return the utility for the active player on the board.

        Returns
        ----------
        float
            The utility value of the current game state for the specified
            player. The game has a utility of +inf if the player has won,
            a value of -inf if the player has lost, and a value of 0
            otherwise.
        """

        if not self.get_legal_moves(self.active_player):

            if player == self.inactive_player:
                return float("inf")

            if player == self.active_player:
                return float("-inf")

        return 0.

    def __get_moves__(self, move):
        """
        Generate the list of possible moves for an L-shaped motion (like a
        knight in chess).
        """

        if move == Board.NOT_MOVED:
            return self.get_blank_spaces()

        r, c = move

        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                      (1, -2),  (1, 2), (2, -1),  (2, 1)]

        valid_moves = [(r+dr,c+dc) for dr, dc in directions if self.move_is_legal((r+dr, c+dc))]

        return valid_moves

    def print_board(self):
        """
        Generate a string representation of the current game state, marking
        the location of each player and indicating which cells have been
        blocked, and which remain open.
        """

        p1_r, p1_c = self.__last_player_move__[self.__player_1__]
        p2_r, p2_c = self.__last_player_move__[self.__player_2__]

        out = ''

        for i in range(self.height):
            out += ' | '

            for j in range(self.width):

                if not self.__board_state__[i][j]:
                    out += ' '
                elif i == p1_r and j == p1_c:
                    out += '1'
                elif i == p2_r and j == p2_c:
                    out += '2'
                else:
                    out += '-'

                out += ' | '
            out += '\n\r'

        return out

    def play(self, time_limit=TIME_LIMIT_MILLIS):
        """
        Execute a match between the players by alternately soliciting them
        to select a move and applying it in the game.

        Parameters
        ----------
        time_limit : numeric (optional)
            The maximum number of milliseconds to allow before timeout
            during each turn.

        Returns
        ----------
        (player, list<[(int, int),]>, str)
            Return multiple including the winning player, the complete game
            move history, and a string indicating the reason for losing
            (e.g., timeout or invalid move).
        """
        move_history = []

        curr_time_millis = lambda: 1000 * timeit.default_timer()

        while True:

            legal_player_moves = self.get_legal_moves()

            game_copy = self.copy()

            move_start = curr_time_millis()
            time_left = lambda : time_limit - (curr_time_millis() - move_start)
            curr_move = self.active_player.get_move(game_copy, legal_player_moves, time_left)
            move_end = time_left()

            # print move_end

            if curr_move is None:
                curr_move = Board.NOT_MOVED

            if self.active_player == self.__player_1__:
                move_history.append([curr_move])
            else:
                move_history[-1].append(curr_move)

            if move_end < 0:
                return self.__inactive_player__, move_history, "timeout"

            if curr_move not in legal_player_moves:
                return self.__inactive_player__, move_history, "illegal move"

            self.apply_move(curr_move)
