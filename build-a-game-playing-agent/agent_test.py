"""
This file contains test cases to verify the correct implementation of the
functions required for this project including minimax, alphabeta, and iterative
deepening.  The heuristic function is tested for conformance to the expected
interface, but cannot be automatically assessed for correctness.
"""
import unittest
import timeit
import signal

import isolation
import game_agent

from collections import Counter
from copy import deepcopy
from copy import copy
from functools import wraps


WRONG_MOVE = "Your {} search returned an invalid move at search depth {}." + \
             "\nValid choices: {}\nYour selection: {}"

WRONG_NUM_EXPLORED = "Your {} search visited the wrong nodes at search " + \
                     "depth {}.  If the number of visits is too large, " + \
                     "make sure that iterative deepening is only running " + \
                     "when the `iterative` flag is set in the agent " + \
                     "constructor.\nMax explored size: {}\nNumber you " + \
                     "explored: {}"

UNEXPECTED_VISIT = "Your {} search did not visit the number of expected " + \
                   "unique nodes at search depth {}.\nMax explored size: " + \
                   "{}\nNumber you explored: {}"

ID_ERROR = "Your ID search returned the wrong move at a depth of {} with " + \
           "a {}ms time limit. {} {} {}"

ID_FAIL = "Your agent did not explore enough nodes during the search; it " + \
          "did not finish the first layer of available moves."

TIMER_MARGIN = 15  # time (in ms) to leave on the timer to avoid timeout


def curr_time_millis():
    return 1000 * timeit.default_timer()


def timeout(time_limit):
    """
    Function decorator for unittest test cases to specify test case timeout.
    """

    class TimeoutException(Exception):
        """ Subclass Exception to catch timer expiration during search """
        pass

    def handler(*args, **kwargs):
        """ Generic handler to raise an exception when a timer expires """
        raise TimeoutException("Test aborted due to timeout. Test was " +
            "expected to finish in less than {} second(s).".format(time_limit))

    def wrapUnitTest(testcase):

        @wraps(testcase)
        def testWrapper(self, *args, **kwargs):

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(time_limit)

            try:
                return testcase(self, *args, **kwargs)
            finally:
                signal.alarm(0)

        return testWrapper

    return wrapUnitTest


class EvalTable():

    def __init__(self, table):
        self.table = table

    def score(self, game, player):
        row, col = game.get_player_location(player)
        return self.table[row][col]


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
        eval_fn = EvalTable(value_table)

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
        eval_fn = EvalTable(value_table)

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
        eval_fn = EvalTable(value_table)
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

        w, h = 11, 11
        method = "minimax"
        value_table = [[0] * w for _ in range(h)]
        value_table[3][0] = 1
        value_table[2][3] = 1
        value_table[4][4] = 2
        value_table[7][2] = 3
        eval_fn = EvalTable(value_table)

        depths = ["7+", "6", "5", "4", "3", "2", "1"]
        exact_counts = [((4, 4), set([(2, 3), (3, 0)])),
                        ((16, 6), set([(2, 3), (3, 0)])),
                        ((68, 20), set([(2, 3), (3, 2)])),
                        ((310, 21), set([(2, 3), (3, 2)])),
                        ((1582, 45), set([(3, 0), (3, 2)])),
                        ((7534, 45), set([(3, 0), (3, 2)])),
                        ((38366, 74), set([(0, 3), (2, 3), (3, 0), (3, 2)]))]

        time_limit = 3200
        while time_limit >= TIMER_MARGIN:
            agentUT, board = self.initAUT(-1, eval_fn, True, method, (1, 1), (0, 0), w, h)

            legal_moves = board.get_legal_moves()
            timer_start = curr_time_millis()
            time_left = lambda : time_limit - (curr_time_millis() - timer_start)
            move = agentUT.get_move(board, legal_moves, time_left)
            finish_time = time_left()

            self.assertTrue(len(board.visited) > 4, ID_FAIL)

            self.assertTrue(finish_time > 0,
                "Your search failed iterative deepening due to timeout.")

            # print time_limit, board.counts, move

            time_limit /= 2
            # Skip testing if the search exceeded 7 move horizon
            if (board.counts[0] > exact_counts[-1][0][0] or
                    board.counts[1] > exact_counts[-1][0][1] or
                    finish_time < 5):
                continue

            for idx, ((n, m), c) in enumerate(exact_counts[::-1]):
                if n > board.counts[0]:
                    continue
                self.assertIn(move, c, ID_ERROR.format(depths[idx], 2 * time_limit, move, *board.counts))
                break

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
