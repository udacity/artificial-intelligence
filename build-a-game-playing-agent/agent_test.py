"""
This file contains test cases to verify the correct implementation of the
functions required for this project including minimax, alphabeta, and iterative
deepening.  The heuristic function is tested for conformance to the expected
interface, but cannot be automatically assessed for correctness.

STUDENTS SHOULD NOT NEED TO MODIFY THIS CODE.  IT WOULD BE BEST TO TREAT THIS
FILE AS A BLACK BOX FOR TESTING.
"""
import random
import unittest
import timeit
import sys

import isolation
import game_agent

from collections import Counter
from copy import deepcopy
from copy import copy
from functools import wraps
from queue import Queue
from threading import Thread
from multiprocessing import TimeoutError
from queue import Empty as QueueEmptyError
from importlib import reload

WRONG_MOVE = """
The {} function failed because it returned a non-optimal move at search depth {}.
Valid choices: {}
Your selection: {}
"""

WRONG_NUM_EXPLORED = """
Your {} search visited the wrong nodes at search depth {}.  If the number
of visits is too large, make sure that iterative deepening is only
running when the `iterative` flag is set in the agent constructor.
Max explored size: {}
Number you explored: {}
"""

UNEXPECTED_VISIT = """
Your {} search did not visit the number of expected unique nodes at search
depth {}.
Max explored size: {}
Number you explored: {}
"""

ID_FAIL = """
Your agent explored the wrong number of nodes using Iterative Deepening and
minimax. Remember that ID + MM should check every node in each layer of the
game tree before moving on to the next layer.
"""

INVALID_MOVE = """
Your agent returned an invalid move. Make sure that your function returns
a selection when the search times out during iterative deepening.
Valid choices: {!s}
Your choice: {}
"""

TIMER_MARGIN = 15  # time (in ms) to leave on the timer to avoid timeout


def curr_time_millis():
    """Simple timer to return the current clock time in milliseconds."""
    return 1000 * timeit.default_timer()


def handler(obj, testcase, queue):
    """Handler to pass information between threads; used in the timeout
    function to abort long-running (i.e., probably hung) test cases.
    """
    try:
        queue.put((None, testcase(obj)))
    except:
        queue.put((sys.exc_info(), None))


def timeout(time_limit):
    """Function decorator for unittest test cases to specify test case timeout.

    The timer mechanism works by spawning a new thread for the test to run in
    and using the timeout handler for the thread-safe queue class to abort and
    kill the child thread if it doesn't return within the timeout.

    It is not safe to access system resources (e.g., files) within test cases
    wrapped by this timer.
    """

    def wrapUnitTest(testcase):

        @wraps(testcase)
        def testWrapper(self):

            queue = Queue()

            try:
                p = Thread(target=handler, args=(self, testcase, queue))
                p.daemon = True
                p.start()
                err, res = queue.get(timeout=time_limit)
                p.join()
                if err:
                    raise err[0](err[1]).with_traceback(err[2])
                return res
            except QueueEmptyError:
                raise TimeoutError("Test aborted due to timeout. Test was " +
                                   "expected to finish in less than {} second(s).".format(time_limit))

        return testWrapper

    return wrapUnitTest


def makeEvalTable(table):
    """Use a closure to create a heuristic function that returns values from
    a table that maps board locations to constant values. This supports testing
    the minimax and alphabeta search functions.

    THIS HEURISTIC IS ONLY USEFUL FOR TESTING THE SEARCH FUNCTIONALITY -
    IT IS NOT MEANT AS AN EXAMPLE OF A USEFUL HEURISTIC FOR GAME PLAYING.
    """

    def score(game, player):
        row, col = game.get_player_location(player)
        return table[row][col]

    return score


def makeEvalStop(limit, timer, value=None):
    """Use a closure to create a heuristic function that forces the search
    timer to expire when a fixed number of node expansions have been perfomred
    during the search. This ensures that the search algorithm should always be
    in a predictable state regardless of node expansion order.

    THIS HEURISTIC IS ONLY USEFUL FOR TESTING THE SEARCH FUNCTIONALITY -
    IT IS NOT MEANT AS AN EXAMPLE OF A USEFUL HEURISTIC FOR GAME PLAYING.
    """

    def score(game, player):
        if limit == game.counts[0]:
            timer.time_limit = 0
        elif timer.time_left() < 0:
            raise TimeoutError("Timer expired during search. You must " +
                               "return an answer before the timer reaches 0.")
        return 0

    return score


def makeBranchEval(first_branch):
    """Use a closure to create a heuristic function that evaluates to a nonzero
    score when the root of the search is the first branch explored, and
    otherwise returns 0.  This heuristic is used to force alpha-beta to prune
    some parts of a game tree for testing.

    THIS HEURISTIC IS ONLY USEFUL FOR TESTING THE SEARCH FUNCTIONALITY -
    IT IS NOT MEANT AS AN EXAMPLE OF A USEFUL HEURISTIC FOR GAME PLAYING.
    """

    def score(game, player):
        if not first_branch:
            first_branch.append(game.root)
        if game.root in first_branch:
            return 1.
        return 0.

    return score


class CounterBoard(isolation.Board):
    """Subclass of the isolation board that maintains counters for the number
    of unique nodes and total nodes visited during depth first search.

    Some functions from the base class must be overridden to maintain the
    counters during search.
    """

    def __init__(self, *args, **kwargs):
        super(CounterBoard, self).__init__(*args, **kwargs)
        self.counter = Counter()
        self.visited = set()
        self.root = None

    def copy(self):
        new_board = CounterBoard(self.__player_1__, self.__player_2__,
                                 width=self.width, height=self.height)
        new_board.move_count = self.move_count
        new_board.__active_player__ = self.__active_player__
        new_board.__inactive_player__ = self.__inactive_player__
        new_board.__last_player_move__ = copy(self.__last_player_move__)
        new_board.__player_symbols__ = copy(self.__player_symbols__)
        new_board.__board_state__ = deepcopy(self.__board_state__)
        new_board.counter = self.counter
        new_board.visited = self.visited
        new_board.root = self.root
        return new_board

    def forecast_move(self, move):
        self.counter[move] += 1
        self.visited.add(move)
        new_board = self.copy()
        new_board.apply_move(move)
        if new_board.root is None:
            new_board.root = move
        return new_board

    @property
    def counts(self):
        """ Return counts of (total, unique) nodes visited """
        return sum(self.counter.values()), len(self.visited)


class Project1Test(unittest.TestCase):

    def initAUT(self, depth, eval_fn, iterative=False,
                method="minimax", loc1=(3, 3), loc2=(0, 0), w=7, h=7):
        """Generate and initialize player and board objects to be used for
        testing.
        """
        reload(game_agent)
        agentUT = game_agent.CustomPlayer(depth, eval_fn, iterative, method)
        board = CounterBoard(agentUT, 'null_agent', w, h)
        board.apply_move(loc1)
        board.apply_move(loc2)
        return agentUT, board

    @timeout(1)
    # @unittest.skip("Skip eval function test.")  # Uncomment this line to skip test
    def test_heuristic(self):
        """ Test output interface of heuristic score function interface."""

        player1 = "Player1"
        player2 = "Player2"
        p1_location = (0, 0)
        p2_location = (1, 1)  # top left corner
        game = isolation.Board(player1, player2)
        game.apply_move(p1_location)
        game.apply_move(p2_location)

        self.assertIsInstance(game_agent.custom_score(game, player1), float,
            "The heuristic function should return a floating point")

    timeout(1)
    # @unittest.skip("Skip simple minimax test.")  # Uncomment this line to skip test
    def test_minimax_interface(self):
        """ Test CustomPlayer.minimax interface with simple input """
        h, w = 7, 7  # board size
        test_depth = 1
        starting_location = (5, 3)
        adversary_location = (0, 0)  # top left corner
        iterative_search = False
        search_method = "minimax"
        heuristic = lambda g, p: 0.  # return 0 everywhere

        # create a player agent & a game board
        agentUT = game_agent.CustomPlayer(
            test_depth, heuristic, iterative_search, search_method)
        agentUT.time_left = lambda: 99  # ignore timeout for fixed-depth search
        board = isolation.Board(agentUT, 'null_agent', w, h)

        # place two "players" on the board at arbitrary (but fixed) locations
        board.apply_move(starting_location)
        board.apply_move(adversary_location)

        for move in board.get_legal_moves():
            next_state = board.forecast_move(move)
            v, _ = agentUT.minimax(next_state, test_depth)

            self.assertTrue(type(v) == float,
                            ("Minimax function should return a floating " +
                             "point value approximating the score for the " +
                             "branch being searched."))

    timeout(1)
    # @unittest.skip("Skip alphabeta test.")  # Uncomment this line to skip test
    def test_alphabeta_interface(self):
        """ Test CustomPlayer.alphabeta interface with simple input """
        h, w = 9, 9  # board size
        test_depth = 1
        starting_location = (2, 7)
        adversary_location = (0, 0)  # top left corner
        iterative_search = False
        search_method = "alphabeta"
        heuristic = lambda g, p: 0.  # return 0 everywhere

        # create a player agent & a game board
        agentUT = game_agent.CustomPlayer(
            test_depth, heuristic, iterative_search, search_method)
        agentUT.time_left = lambda: 99  # ignore timeout for fixed-depth search
        board = isolation.Board(agentUT, 'null_agent', w, h)

        # place two "players" on the board at arbitrary (but fixed) locations
        board.apply_move(starting_location)
        board.apply_move(adversary_location)

        for move in board.get_legal_moves():
            next_state = board.forecast_move(move)
            v, _ = agentUT.alphabeta(next_state, test_depth)

            self.assertTrue(type(v) == float,
                            ("Alpha Beta function should return a floating " +
                             "point value approximating the score for the " +
                             "branch being searched."))

    @timeout(1)
    # @unittest.skip("Skip get_move test.")  # Uncomment this line to skip test
    def test_get_move_interface(self):
        """ Test CustomPlayer.get_move interface with simple input """
        h, w = 9, 9  # board size
        test_depth = 1
        starting_location = (2, 7)
        adversary_location = (0, 0)  # top left corner
        iterative_search = False
        search_method = "minimax"
        heuristic = lambda g, p: 0.  # return 0 everywhere

        # create a player agent & a game board
        agentUT = game_agent.CustomPlayer(
            test_depth, heuristic, iterative_search, search_method)

        # Test that get_move returns a legal choice on an empty game board
        board = isolation.Board(agentUT, 'null_agent', w, h)
        legal_moves = board.get_legal_moves()
        move = agentUT.get_move(board, legal_moves, lambda: 99)
        self.assertIn(move, legal_moves,
                      ("The get_move() function failed as player 1 on an " +
                       "empty board. It should return coordinates on the " +
                       "game board for the location of the agent's next " +
                       "move. The move must be one of the legal moves on " +
                       "the current game board."))

        # Test that get_move returns a legal choice for first move as player 2
        board = isolation.Board('null_agent', agentUT, w, h)
        board.apply_move(starting_location)
        legal_moves = board.get_legal_moves()
        move = agentUT.get_move(board, legal_moves, lambda: 99)
        self.assertIn(move, legal_moves,
                      ("The get_move() function failed making the first " +
                       "move as player 2 on a new board. It should return " +
                       "coordinates on the game board for the location " +
                       "of the agent's next move. The move must be one " +
                       "of the legal moves on the current game board."))

        # Test that get_move returns a legal choice after first move
        board = isolation.Board(agentUT, 'null_agent', w, h)
        board.apply_move(starting_location)
        board.apply_move(adversary_location)
        legal_moves = board.get_legal_moves()
        move = agentUT.get_move(board, legal_moves, lambda: 99)
        self.assertIn(move, legal_moves,
                      ("The get_move() function failed as player 1 on a " +
                       "game in progress. It should return coordinates on" +
                       "the game board for the location of the agent's " +
                       "next move. The move must be one of the legal moves " +
                       "on the current game board."))

    @timeout(1)
    # @unittest.skip("Skip minimax test.")  # Uncomment this line to skip test
    def test_minimax(self):
        """ Test CustomPlayer.minimax

        This test uses a scoring function that returns a constant value based
        on the location of the search agent on the board to force minimax to
        choose a branch that visits those cells at a specific fixed-depth.
        If minimax is working properly, it will visit a constant number of
        nodes during the search and return one of the acceptable legal moves.
        """
        h, w = 7, 7  # board size
        starting_location = (2, 3)
        adversary_location = (0, 0)  # top left corner
        iterative_search = False
        method = "minimax"

        # The agent under test starts at position (2, 3) on the board, which
        # gives eight (8) possible legal moves [(0, 2), (0, 4), (1, 1), (1, 5),
        # (3, 1), (3, 5), (4, 2), (4, 4)]. The search function will pick one of
        # those moves based on the estimated score for each branch.  The value
        # only changes on odd depths because even depths end on when the
        # adversary has initiative.
        value_table = [[0] * w for _ in range(h)]
        value_table[1][5] = 1  # depth 1 & 2
        value_table[4][3] = 2  # depth 3 & 4
        value_table[6][6] = 3  # depth 5
        heuristic = makeEvalTable(value_table)

        # These moves are the branches that will lead to the cells in the value
        # table for the search depths.
        expected_moves = [set([(1, 5)]),
                          set([(3, 1), (3, 5)]),
                          set([(3, 5), (4, 2)])]

        # Expected number of node expansions during search
        counts = [(8, 8), (24, 10), (92, 27), (418, 32), (1650, 43)]

        # Test fixed-depth search; note that odd depths mean that the searching
        # player (student agent) has the last move, while even depths mean that
        # the adversary has the last move before calling the heuristic
        # evaluation function.
        for idx in range(5):
            test_depth = idx + 1
            agentUT, board = self.initAUT(test_depth, heuristic,
                                          iterative_search, method,
                                          loc1=starting_location,
                                          loc2=adversary_location)

            # disable search timeout by returning a constant value
            agentUT.time_left = lambda: 1e3
            _, move = agentUT.minimax(board, test_depth)

            num_explored_valid = board.counts[0] == counts[idx][0]
            num_unique_valid = board.counts[1] == counts[idx][1]

            self.assertTrue(num_explored_valid, WRONG_NUM_EXPLORED.format(
                method, test_depth, counts[idx][0], board.counts[0]))

            self.assertTrue(num_unique_valid, UNEXPECTED_VISIT.format(
                method, test_depth, counts[idx][1], board.counts[1]))

            self.assertIn(move, expected_moves[idx // 2], WRONG_MOVE.format(
                method, test_depth, expected_moves[idx // 2], move))

    @timeout(10)
    # @unittest.skip("Skip alpha-beta test.")  # Uncomment this line to skip test
    def test_alphabeta(self):
        """ Test CustomPlayer.alphabeta

        This test uses a scoring function that returns a constant value based
        on the branch being searched by alphabeta in the user agent, and forces
        the search to prune on every other branch it visits. By using a huge
        board where the players are too far apart to interact and every branch
        has the same growth factor, the expansion and pruning must result in
        an exact number of expanded nodes.
        """
        h, w = 101, 101  # board size
        starting_location = (50, 50)
        adversary_location = (0, 0)  # top left corner
        iterative_search = False
        method = "alphabeta"

        # The agent under test starts in the middle of a huge board so that
        # every branch has the same number of possible moves, so pruning any
        # branch has the same effect during testing

        # These are the expected number of node expansions for alphabeta search
        # to explore the game tree to fixed depth.  The custom eval function
        # used for this test ensures that some branches must be pruned, while
        # the search should still return an optimal move.
        counts = [(8, 8), (17, 10), (74, 42), (139, 51), (540, 119)]

        for idx in range(len(counts)):
            test_depth = idx + 1  # pruning guarantee requires min depth of 3
            first_branch = []
            heuristic = makeBranchEval(first_branch)
            agentUT, board = self.initAUT(test_depth, heuristic,
                                          iterative_search, method,
                                          loc1=starting_location,
                                          loc2=adversary_location,
                                          w=w, h=h)

            # disable search timeout by returning a constant value
            agentUT.time_left = lambda: 1e3
            _, move = agentUT.alphabeta(board, test_depth)

            num_explored_valid = board.counts[0] == counts[idx][0]
            num_unique_valid = board.counts[1] == counts[idx][1]

            self.assertTrue(num_explored_valid, WRONG_NUM_EXPLORED.format(
                method, test_depth, counts[idx][0], board.counts[0]))

            self.assertTrue(num_unique_valid, UNEXPECTED_VISIT.format(
                method, test_depth, counts[idx][1], board.counts[1]))

            self.assertIn(move, first_branch, WRONG_MOVE.format(
                method, test_depth, first_branch, move))


    @timeout(10)
    # @unittest.skip("Skip iterative deepening test.")  # Uncomment this line to skip test
    def test_get_move(self):
        """ Test iterative deepening in CustomPlayer.get_move by placing an
        agent on the game board and performing ID minimax search, which
        should visit a specific number of unique nodes while expanding. By
        forcing the search to timeout when a predetermined number of nodes
        have been expanded, we can then verify that the expected number of
        unique nodes have been visited.
        """

        class DynamicTimer():
            """Dynamic Timer allows the time limit to be changed after the
            timer is initialized so that the search timeout can be triggered
            before the timer actually expires. This allows the timer to expire
            when an event occurs, regardless of the clock time required until
            the event happens.
            """
            def __init__(self, time_limit):
                self.time_limit = time_limit
                self.start_time = curr_time_millis()

            def time_left(self):
                return self.time_limit - (curr_time_millis() - self.start_time)

        w, h = 11, 11  # board size
        adversary_location = (0, 0)
        method = "minimax"

        # The agent under test starts at the positions indicated below, and
        # performs an iterative deepening minimax search (minimax is easier to
        # test because it always visits all nodes in the game tree at every
        # level).
        origins = [(2, 3), (6, 6), (7, 4), (4, 2), (0, 5), (10, 10)]
        exact_counts = [(8, 8), (32, 10), (160, 39), (603, 35), (1861, 54), (3912, 62)]

        for idx in range(len(origins)):

            # set the initial timer high enough that the search will not
            # timeout before triggering the dynamic timer to halt by visiting
            # the expected number of nodes
            time_limit = 1e4
            timer = DynamicTimer(time_limit)
            eval_fn = makeEvalStop(exact_counts[idx][0], timer, time_limit)
            agentUT, board = self.initAUT(-1, eval_fn, True, method,
                                          origins[idx], adversary_location,
                                          w, h)
            legal_moves = board.get_legal_moves()
            chosen_move = agentUT.get_move(board, legal_moves, timer.time_left)

            diff_total = abs(board.counts[0] - exact_counts[idx][0])
            diff_unique = abs(board.counts[1] - exact_counts[idx][1])

            self.assertTrue(diff_total <= 1 and diff_unique == 0, ID_FAIL)

            self.assertTrue(chosen_move in legal_moves, INVALID_MOVE.format(
                legal_moves, chosen_move))


if __name__ == '__main__':
    unittest.main()
