
import unittest

from collections import deque
from random import choice
from textwrap import dedent

from isolation import Isolation, Agent, fork_get_action, play
from sample_players import RandomPlayer
from my_custom_player import CustomPlayer


class BaseCustomPlayerTest(unittest.TestCase):
    def setUp(self):
        self.time_limit = 150
        self.move_0_state = Isolation()
        self.move_1_state = self.move_0_state.result(choice(self.move_0_state.actions()))
        self.move_2_state = self.move_1_state.result(choice(self.move_1_state.actions()))
        terminal_state = self.move_2_state
        while not terminal_state.terminal_test():
            terminal_state = terminal_state.result(choice(terminal_state.actions()))
        self.terminal_state = terminal_state


class CustomPlayerGetActionTest(BaseCustomPlayerTest):
    def _test_state(self, state):
        agent = CustomPlayer(state.ply_count % 2)
        action = fork_get_action(state, agent, self.time_limit)
        self.assertTrue(action in state.actions(), dedent("""\
            Your agent did not call self.queue.put() with a valid action \
            within {} milliseconds from state {}
        """).format(self.time_limit, state))

    def test_get_action_player1(self):
        """ get_action() calls self.queue.put() before timeout on an empty board """
        self._test_state(self.move_0_state)

    def test_get_action_player2(self):
        """ get_action() calls self.queue.put() before timeout as player 2 """
        self._test_state(self.move_1_state)

    def test_get_action_midgame(self):
        """ get_action() calls self.queue.put() before timeout in a game in progress """
        self._test_state(self.move_2_state)

    def test_get_action_terminal(self):
        """ get_action() calls self.queue.put() before timeout when the game is over """
        self._test_state(self.terminal_state)


class CustomPlayerPlayTest(BaseCustomPlayerTest):
    def test_custom_player(self):
        """ CustomPlayer successfully completes a game against itself """
        agents = (Agent(CustomPlayer, "Player 1"),
                  Agent(CustomPlayer, "Player 2"))
        initial_state = Isolation()
        winner, game_history, _ = play((agents, initial_state, self.time_limit, 0))
        
        state = initial_state
        moves = deque(game_history)
        while moves: state = state.result(moves.popleft())

        self.assertTrue(state.terminal_test(), "Your agent did not play until a terminal state.")

