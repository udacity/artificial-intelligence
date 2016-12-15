"""
This file contains test cases to verify the correct implementation of the
functions required for this project including minimax, alphabeta, and iterative
deepening.  The heuristic function is tested for conformance to the expected
interface, but cannot be automatically assessed for correctness.
"""
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
Your {} search visited the wrong nodes at search depth {}.  If the number of
visits is too large, make sure that iterative deepening is only running when
the `iterative` flag is set in the agent constructor.
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
    return 1000 * timeit.default_timer()


def handler(obj, testcase, queue):
    try:
        queue.put((None, testcase(obj)))
    except:
        queue.put((sys.exc_info(), None))


def timeout(time_limit):
    """
    Function decorator for unittest test cases to specify test case timeout.

    It is not safe to access system resources (e.g., files) within test
    cases wrapped by this timer.
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

    class EvalTable():

        def score(self, game, player):
            row, col = game.get_player_location(player)
            return table[row][col]

    return EvalTable


# class EvalTable():

#     def __init__(self, table):
#         self.table = table

#     def score(self, game, player):
#         row, col = game.get_player_location(player)
#         return self.table[row][col]


def makeEvalStop(limit, timer, value=None):

    class EvalStop():

        def __init__(self, limit=limit, timer=timer, value=value):
            self.limit = limit
            self.dv = value
            self.timer = timer

        def score(self, game, player):
            # print self.limit
            if self.limit == game.counts[0]:
                self.dv.val = 0
            elif self.timer() < 0:
                raise TimeoutError("Timer expired during search. You must " + \
                                "return an answer before the timer reaches 0.")
            return 0

    return EvalStop


class CounterBoard(isolation.Board):

    def __init__(self, *args, **kwargs):
        super(CounterBoard, self).__init__(*args, **kwargs)
        self.counter = Counter()
        self.visited = set()

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
        return new_board

    def forecast_move(self, move):
        self.counter[move] += 1
        self.visited.add(move)
        new_board = self.copy()
        new_board.apply_move(move)
        return new_board

    @property
    def counts(self):
        """ Return counts of (total, unique) nodes visited """
        return sum(self.counter.values()), len(self.visited)


class Project1Test(unittest.TestCase):

    def initAUT(self, depth, eval_fn, iterative=False, method="minimax", loc1=(3, 3), loc2=(0, 0), w=7, h=7):

        reload(game_agent)
        agentUT = game_agent.CustomPlayer(depth, eval_fn, iterative, method)

        board = CounterBoard(agentUT, 'null_agent', w, h)
        board.apply_move(loc1)
        board.apply_move(loc2)
        return agentUT, board

    @timeout(1)
    # @unittest.skip("Skip minimax test.")  # Uncomment this line to skip test
    def test_minimax(self):
        """ Test CustomPlayer.minimax """

        h, w = 7, 7
        method = "minimax"
        value_table = [[0] * w for _ in range(h)]
        value_table[1][5] = 1
        value_table[4][3] = 2
        value_table[6][6] = 3
        eval_fn = makeEvalTable(value_table)

        expected_moves = [set([(1, 5)]),
                          set([(3, 1), (3, 5)]),
                          set([(3, 5), (4, 2)])]

        counts = [(8, 8), (92, 27), (1650, 43)]

        for idx, depth in enumerate([1, 3, 5]):
            agentUT, board = self.initAUT(depth, eval_fn, False, method, loc1=(2, 3), loc2=(0, 0))
            move = agentUT.get_move(board, board.get_legal_moves(), lambda: 1e3)

            num_explored_valid = board.counts[0] == counts[idx][0]
            num_unique_valid = board.counts[1] == counts[idx][1]

            self.assertTrue(num_explored_valid,
                WRONG_NUM_EXPLORED.format(method, depth, counts[idx][0], board.counts[0]))

            self.assertTrue(num_unique_valid,
                UNEXPECTED_VISIT.format(method, depth, counts[idx][1], board.counts[1]))

            self.assertIn(move, expected_moves[idx],
                WRONG_MOVE.format(method, depth, expected_moves[idx], move))

    @timeout(1)
    # @unittest.skip("Skip alpha-beta test.")  # Uncomment this line to skip test
    def test_alphabeta(self):
        """ Test CustomPlayer.alphabeta """

        h, w = 7, 7
        method = "alphabeta"
        value_table = [[0] * w for _ in range(h)]
        value_table[2][5] = 1
        value_table[0][4] = 2
        value_table[1][0] = 3
        value_table[5][5] = 4
        eval_fn = makeEvalTable(value_table)

        expected_moves = [set([(2, 5)]),
                          set([(2, 5)]),
                          set([(1, 4)]),
                          set([(1, 4), (2, 5)])]

        counts = [(2, 2), (26, 13), (552, 36), (10564, 47)]

        for idx, depth in enumerate([1, 3, 5, 7]):
            agentUT, board = self.initAUT(depth, eval_fn, False, method, loc1=(0, 6), loc2=(0, 0))
            move = agentUT.get_move(board, board.get_legal_moves(), lambda: 1e4)

            num_explored_valid = board.counts[0] <= counts[idx][0]
            num_unique_valid = board.counts[1] <= counts[idx][1]

            self.assertTrue(num_explored_valid,
                WRONG_NUM_EXPLORED.format(method, depth, counts[idx][0], board.counts[0]))

            self.assertTrue(num_unique_valid,
                UNEXPECTED_VISIT.format(method, depth, counts[idx][1], board.counts[1]))

            self.assertIn(move, expected_moves[idx],
                WRONG_MOVE.format(method, depth, expected_moves[idx], move))

    @timeout(1)
    # @unittest.skip("Skip alpha-beta pruning test.")  # Uncomment this line to skip test
    def test_alphabeta_pruning(self):
        """ Test pruning in CustomPlayer.alphabeta """

        h, w = 15, 15
        depth = 6
        method = "alphabeta"
        value_table = [[0] * w for _ in range(h)]
        value_table[3][14] = 1
        eval_fn = makeEvalTable(value_table)
        blocked_cells = [(0, 9), (0, 13), (0, 14), (1, 8), (1, 9), (1, 14),
                         (2, 9), (2, 11), (3, 8), (3, 10), (3, 11), (3, 12),
                         (4, 9), (4, 11), (4, 13), (5, 10), (5, 12), (5, 13),
                         (5, 14), (6, 11), (6, 13), (9, 0), (9, 2), (10, 3),
                         (11, 3), (12, 0), (12, 1), (12, 3), (12, 4), (12, 5)]

        agentUT, board = self.initAUT(depth, eval_fn, False, method, (0, 14), (14, 0), w, h)
        for r, c in blocked_cells:
            board.__board_state__[r][c] = "X"
        move = agentUT.get_move(board, board.get_legal_moves(), lambda: 1e4)

        expected_move = (2, 13)
        max_visits = (40, 18)

        num_explored_valid = board.counts[0] < max_visits[0]
        num_unique_valid = board.counts[1] <= max_visits[1]

        self.assertTrue(num_explored_valid,
            WRONG_NUM_EXPLORED.format(method, depth, max_visits[0], board.counts[0]))

        self.assertTrue(num_unique_valid,
            UNEXPECTED_VISIT.format(method, depth, max_visits[1], board.counts[1]))

        self.assertEqual(move, expected_move,
            WRONG_MOVE.format(method, depth, expected_move, move))

    @timeout(10)
    # @unittest.skip("Skip iterative deepening test.")  # Uncomment this line to skip test
    def test_id(self):
        """ Test iterative deepening for CustomPlayer.minimax """

        class DVal():

            def __init__(self, val):
                self.val = val

        w, h = 11, 11
        method = "minimax"
        value_table = [[0] * w for _ in range(h)]

        origins = [(2, 3), (6, 6), (7, 4), (4, 2), (0, 5), (10, 10)]
        exact_counts = [(8, 8), (32, 10), (160, 39), (603, 35), (1861, 54), (3912, 62)]

        for idx in range(len(origins)):
            time_limit = DVal(1000)

            timer_start = curr_time_millis()
            time_left = lambda : time_limit.val - (curr_time_millis() - timer_start)
            eval_fn = makeEvalStop(exact_counts[idx][0], time_left, time_limit)
            agentUT, board = self.initAUT(-1, eval_fn, True, method, origins[idx], (0, 0), w, h)

            legal_moves = board.get_legal_moves()
            chosen_move = agentUT.get_move(board, legal_moves, time_left)

            diff_total = abs(board.counts[0] - exact_counts[idx][0])
            diff_unique = abs(board.counts[1] - exact_counts[idx][1])

            self.assertTrue(diff_total <= 1 and diff_unique == 0, ID_FAIL)

            self.assertTrue(chosen_move in legal_moves,
                INVALID_MOVE.format(legal_moves, chosen_move))


    @timeout(1)
    # @unittest.skip("Skip eval function test.")  # Uncomment this line to skip test
    def test_custom_eval(self):
        """ Test output interface of CustomEval """

        player1 = "Player1"
        player2 = "Player2"
        game = isolation.Board(player1, player2)

        heuristic = game_agent.CustomEval()

        self.assertIsInstance(heuristic.score(game, player1), float,
            "The heuristic function should return a floating point")


if __name__ == '__main__':
    unittest.main()
