
###############################################################################
#                          DO NOT MODIFY THIS FILE                            #
###############################################################################
import inspect
import logging
import sys
import time

from collections import namedtuple
from enum import Enum
from multiprocessing import Process, Queue, Pipe
from queue import Empty

from .isolation import Isolation, DebugState

__all__ = ['Isolation', 'DebugState', 'Status', 'play', 'fork_get_action']
logger = logging.getLogger(__name__)

Agent = namedtuple("Agent", "agent_class name")

PROCESS_TIMEOUT = 2  # time to interrupt agent search processes (in seconds)
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
    EXCEPTION = 0
    TIMEOUT = 1
    INVALID_MOVE = 2
    GAME_OVER = 3


class StopSearch(Exception): pass  # Exception class used to halt search


class Countdown_Timer:  # Timer object used to monitor time spent on search
    def __init__(self, time_limit):
        self.__time_limit = time_limit / 1000.
        self.__stop_time = None

    def set_start_time(self, start_time):
        self.__stop_time = self.__time_limit + start_time

    def check_time(self):
        return (self.__stop_time - time.perf_counter()) * 1000.

    def __call__(self):
        return time.perf_counter() > self.__stop_time


def play(args): return _play(*args)  # multithreading ThreadPool.map doesn't expand args


def _play(agents, game_state, time_limit, match_id):
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
    players = [a.agent_class(player_id=i) for i, a in enumerate(agents)]
    logger.info(GAME_INFO.format(initial_state, *agents))
    while not game_state.terminal_test():
        active_idx = game_state.ply_count % 2

        try:
            action = fork_get_action(game_state, players[active_idx], time_limit)
        except Empty:
            logger.info(
                "{} get_action() method did not respond within {} milliseconds".format(
                    agents[active_idx], time_limit
            ))
            logger.info(RESULT_INFO.format(
                Status.TIMEOUT, game_state, game_history, agents[1 - active_idx], agents[active_idx]
            ))
            winner = agents[1 - active_idx]
            break
        except Exception as err:
            logger.error(ERR_INFO.format(
                err, initial_state, agents[0], agents[1], game_state, game_history
            ))
            winner = agents[1 - active_idx]
            break

        if action not in game_state.actions():
            logger.info(RESULT_INFO.format(
                Status.INVALID_MOVE, game_state, game_history, agents[1 - active_idx], agents[active_idx]
            ))
            winner = agents[1 - active_idx]
            break

        game_state = game_state.result(action)
        game_history.append(action)

    if winner is not None:  # Timeout, invalid move, or unknown exception
        pass
    elif game_state.utility(active_idx) > 0:
        logger.info(RESULT_INFO.format(
            Status.GAME_OVER, game_state, game_history, agents[active_idx], agents[1 - active_idx]
        ))
        winner = agents[active_idx]
    elif game_state.utility(1 - active_idx) > 0:
        logger.info(RESULT_INFO.format(
            Status.GAME_OVER, game_state, game_history, agents[1 - active_idx], agents[active_idx]
        ))
        winner = agents[1 - active_idx]
    else:
        raise RuntimeError(("A game ended without a winner.\n" +
            "initial game: {}\nfinal game: {}\naction history: {}\n").format(
                initial_state, game_state, game_history))

    return winner, game_history, match_id


def fork_get_action(game_state, active_player, time_limit):
    action_queue = Queue()
    listener, client = Pipe()
    active_player.queue = action_queue  # give the agent instance a threadsafe queue
    
    # comment out these lines for debugging mode
    p = Process(target=_request_action, args=(active_player, game_state, time_limit, client))
    p.start()
    p.join(timeout=PROCESS_TIMEOUT)
    if p and p.is_alive(): p.terminate()

    # Uncomment these lines to run in debug mode, which runs the search function in the
    # main process so that debuggers and profilers work properly. NOTE: calls to your
    # search methods will NOT timeout in debug mode; you must be very careful to avoid
    # calls that are not methods of your CustomPlayer class or else your agent may fail
    #
    # from copy import deepcopy
    # active_player.queue = None
    # active_player = deepcopy(active_player)
    # active_player.queue = action_queue
    # _request_action(active_player, game_state, time_limit, client)

    if listener.poll():
        active_player.context = listener.recv()  # preserve any internal state
    while True:  # treat the queue as LIFO
        action = action_queue.get_nowait()  # raises Empty if agent did not respond
        if action_queue.empty(): break
    return action


def _callable(member):
    return inspect.ismethod(member) or inspect.isfunction(member)


def _timeout(func, timer):
    """ Decorator to check for timeout each time a function is called """
    def _func(*args, **kwargs):
        if timer(): raise StopSearch
        return func(*args, **kwargs)
    return _func


def _wrap_timer(obj, timer):
    """ Wrap each method of an object with a timeout test """
    for name, method in inspect.getmembers(obj, _callable):
        setattr(obj, name, _timeout(method, timer))
    return obj


def _request_action(agent, game_state, time_limit, conn):
    """ Augment agent instances with a countdown timer on every method before
    calling the get_action() method and catch countdown timer exceptions.

    Wrapping the methods must happen here because the wrapped methods cannot
    be passed between processes 
    """
    timer = Countdown_Timer(time_limit)
    agent = _wrap_timer(agent, timer)
    timer.set_start_time(time.perf_counter())
    # Catch StopSearch exceptions on timeout, but do not catch other exceptions
    try:
        agent.get_action(game_state)
    except StopSearch:
        pass
    conn.send(agent.context) # pass updated agent back to calling process
