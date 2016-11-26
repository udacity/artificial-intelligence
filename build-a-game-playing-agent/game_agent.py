"""
This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using run_tournament.py and include the results in your
report.
"""

class Timeout(Exception):
    """ Subclass base exception for code clarity. """
    pass


class CustomEval():
    """
    Custom evaluation function that acts however you think it should.
    """

    def score(self, game, player):
        """
        Calculate the heuristic value of a game state from the point of view of
        the given player.

        Args:
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        player : hashable
            One of the objects registered by the game object as a valid player.
            (i.e., `player` should be either game.__player_1__ or
            game.__player_2__).

        Returns:
        ----------
        float
            The heuristic value of the current game state.
        """

        # TODO: finish this function!
        raise NotImplementedError


class CustomPlayer():
    """
    Game-playing agent that chooses a move using your evaluation function and a
    depth-limited minimax algorithm with alpha-beta pruning. You must finish
    and test this player to make sure it properly uses minimax and alpha-beta
    to return a good move before the search time limit expires.

    Args:
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. This is
        defined such that a depth of one (1) would only explore the immediate
        sucessors of the current state.

    eval_fn : class (optional)
        List of the legal moves available to the player with initiative to
        move in the current game state (this player).

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().
    """

    def __init__(self, search_depth=3, eval_fn=CustomEval(), iterative=False, method='minimax'):
        """
        You MAY modify this function, but the interface must remain compatible
        with the version provided.
        """
        self.eval_fn = eval_fn
        self.search_depth = search_depth
        self.iterative = iterative
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = 10  # time (in ms) to leave on the clock when terminating search

    def get_move(self, game, legal_moves, time_left):
        """
        Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return before the
              timer reaches 0.
        **********************************************************************

        Args:
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns:
        ----------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # TODO: finish this function!

        # Perform any required initializations

        try:

            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            pass

        except Timeout:

            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration

        raise NotImplementedError

    def minimax(self, game, depth, maximizing_player=True):
        """
        Implement the minimax search algorithm as described in the lectures.

        **********************************************************************
        NOTE: You may modify the function signature and/or output, but the
              signature must remain compatible with the version provided.
              (i.e., if you add parameters, you must also set defaults.) The
              project reviewers will evaluate your code with a test suite
              that depends on the provided input interface. (The output
              signature can be changed, as it is not used for testing.)
        **********************************************************************

        Args:
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns:
        ----------
        float
            By default, the output at least returns the floating point value
            for the min or max score associated with the moves in this branch
            of the game tree.

            YOU ARE ALLOWED TO CHANGE THE OUTPUT INTERFACE OF THIS FUNCTION
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
        raise NotImplementedError

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """
        Implement minimax search with alpha-beta pruning as described in the
        lectures.

        **********************************************************************
        NOTE: You may modify the function signature and/or output, but the
              signature must remain compatible with the version provided.
              (i.e., if you add parameters, you must also set defaults.) The
              project reviewers will evaluate your code with a test suite
              that depends on the provided input interface. (The output
              signature can be changed, as it is not used for testing.)
        **********************************************************************

        Args:
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns:
        ----------
        float
            By default, the output at least returns the floating point value
            for the min or max score associated with the moves in this branch
            of the game tree.

            YOU ARE ALLOWED TO CHANGE THE OUTPUT INTERFACE OF THIS FUNCTION
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
        raise NotImplementedError
