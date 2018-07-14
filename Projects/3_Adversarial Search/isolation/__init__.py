
###############################################################################
#                          DO NOT MODIFY THIS FILE                            #
###############################################################################
import inspect
import logging
import sys
import textwrap
import time

from collections import namedtuple
from enum import Enum
from multiprocessing import Process, Pipe
from queue import Empty

from .isolation import Isolation, DebugState

__all__ = ['Isolation', 'DebugState', 'Status', 'play', 'fork_get_action']
logger = logging.getLogger(__name__)

Agent = namedtuple("Agent", "agent_class name")

PROCESS_TIMEOUT = 5  # time to interrupt agent search processes (in seconds)
GAME_INFO = """\
Initial game state: {}
First agent: {!s}
Second agent: {!s}
"""
ERR_INFO = """\
Error playing game: {!s}
Initial state: {}
First agent: {!s}
Second agent: {!s}
Final state: {}
Action history: {!s}
"""
RESULT_INFO = """\
Status: {}
Final State: {}
History: {}
Winner: {}
Loser: {}
"""

class Status(Enum):
    NORMAL = 0
    EXCEPTION = 1
    TIMEOUT = 2
    INVALID_MOVE = 3
    GAME_OVER = 4


class StopSearch(Exception): pass  # Exception class used to halt search


class TimedQueue:
    """Modified queue class to block .put() after a time limit expires,
    and to include both a context object & action choice in the queue.
    """
    def __init__(self, receiver, sender, time_limit):
        self.__sender = sender
        self.__receiver = receiver
        self.__time_limit = time_limit / 1000
        self.__stop_time = None
        self.agent = None

    def start_timer(self):
        self.__stop_time = self.__time_limit + time.perf_counter()

    def put(self, item, block=True, timeout=None):
        if self.__stop_time and time.perf_counter() > self.__stop_time:
            raise StopSearch
        if self.__receiver.poll():
            self.__receiver.recv()
        self.__sender.send((getattr(self.agent, "context", None), item))

    def put_nowait(self, item):
        self.put(item, block=False)

    def get(self, block=True, timeout=None):
        return self.__receiver.recv()

    def get_nowait(self):
        return self.get(block=False)

    def qsize(self): return int(self.__receiver.poll())
    def empty(self): return ~self.__receiver.poll()
    def full(self): return self.__receiver.poll()


def play(args): return _play(*args)  # multithreading ThreadPool.map doesn't expand args


def _play(agents, game_state, time_limit, match_id, debug=False):
    """ Run a match between two agents by alternately soliciting them to
    select a move and applying it to advance the game state.

    Parameters
    ----------
    agents : tuple
        agents[i] is an instance of isolation.Agent class (namedtuple)

    game_state: Isolation
        an instance of Isolation.Isolation in the initial game state;
        assumes that agents[game_state.ply_count % 2] is the active
        player in the initial state

    time_limit : numeric
        The maximum number of milliseconds to allow before timeout during
        each turn (see notes)

    Returns
    -------
    (agent, list<[(int, int),]>, Status)
        Return multiple including the winning agent, the actions that
        were applied to the initial state, a status code describing the
        reason the game ended, and any error information
    """
    initial_state = game_state
    game_history = []
    winner = None
    status = Status.NORMAL
    players = [a.agent_class(player_id=i) for i, a in enumerate(agents)]
    logger.info(GAME_INFO.format(initial_state, *agents))
    while not game_state.terminal_test():
        active_idx = game_state.player()

        # any problems during get_action means the active player loses
        winner, loser = agents[1 - active_idx], agents[active_idx]

        try:
            action = fork_get_action(game_state, players[active_idx], time_limit, debug)
        except Empty:
            status = Status.TIMEOUT
            logger.warn(textwrap.dedent("""\
                The queue was empty after get_action() was called. This means that either
                the queue.put() method was not called by the get_action() method, or that
                the queue was empty after the procedure was killed due to timeout {} seconds
                after the move time limit of {} milliseconds had expired.
                """.format(players[active_idx], PROCESS_TIMEOUT, time_limit)).replace("\n", " "))
            break
        except Exception as err:
            status = Status.EXCEPTION
            logger.error(ERR_INFO.format(
                err, initial_state, agents[0], agents[1], game_state, game_history
            ))
            break

        if action not in game_state.actions():
            status = Status.INVALID_MOVE
            break

        game_state = game_state.result(action)
        game_history.append(action)
    else:
        status = Status.GAME_OVER
        if game_state.utility(active_idx) > 0:
            winner, loser = loser, winner  # swap winner/loser if active player won

    logger.info(RESULT_INFO.format(status, game_state, game_history, winner, loser))
    return winner, game_history, match_id


def fork_get_action(game_state, active_player, time_limit, debug=False):
    receiver, sender = Pipe()
    action_queue = TimedQueue(receiver, sender, time_limit)
    if debug:  # run the search in the main process and thread
        from copy import deepcopy
        active_player.queue = None
        active_player = deepcopy(active_player)
        active_player.queue = action_queue
        _request_action(active_player, action_queue, game_state)
        time.sleep(time_limit / 1000)
    else:  # spawn a new process to run the search function
        try:
            p = Process(target=_request_action, args=(active_player, action_queue, game_state))
            p.start()
            p.join(timeout=PROCESS_TIMEOUT + time_limit / 1000)
        finally:
            if p and p.is_alive(): p.terminate()
    new_context, action = action_queue.get_nowait()  # raises Empty if agent did not respond
    active_player.context = new_context
    return action


def _request_action(agent, queue, game_state):
    """ Augment agent instances with a countdown timer on every method before
    calling the get_action() method and catch countdown timer exceptions.
    """
    agent.queue = queue
    queue.agent = agent
    try:
        queue.start_timer()
        agent.get_action(game_state)
    except StopSearch:
        pass
