import math
import random
import time
import logging

from copy import deepcopy
from collections import namedtuple

from sample_players import BasePlayer


class CustomPlayer(BasePlayer):
    """ Implement your own agent to play knight's Isolation
    The get_action() method is the only required method for this project.
    You can modify the interface for get_action by adding named parameters
    with default values, but the function MUST remain compatible with the
    default interface.
    **********************************************************************
    NOTES:
    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.
    - You can pass state forward to your agent on the next turn by assigning
      any pickleable object to the self.context attribute.
    **********************************************************************
    """
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least
        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller will be responsible
        for cutting off the function after the search time limit has expired.
        See RandomPlayer and GreedyPlayer in sample_players for more examples.
        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        logging.info("Move %s" % state.ply_count)
        self.queue.put(random.choice(state.actions()))
        i = 1
        statlist = []

        while (self.queue._TimedQueue__stop_time - 0.05) > time.perf_counter():
            next_action = self.uct_search(state, statlist, i)
            self.queue.put(next_action)
            i += 1


    def uct_search(self, state, statlist, i):
        plyturn = state.ply_count % 2
        Stat = namedtuple('Stat', 'state action utility visit nround')

        def tree_policy(state):
            statecopy = deepcopy(state)

            while not statecopy.terminal_test():
                # All taken actions at this depth
                tried = [s.action for s in statlist if s.state == statecopy]
                # See if there's any untried actions left
                untried = [a for a in statecopy.actions() if a not in tried]

                topop = []
                toappend = []

                if len(untried) > 0:
                    next_action = random.choice(untried)
                    statecopy = expand(statecopy, next_action)
                    break
                else:
                    next_action = best_child(statecopy, 1)

                    for k, s in enumerate(statlist):
                        if s.state == statecopy and s.action == next_action:
                            visit1 = statlist[k].visit + 1
                            news = statlist[k]._replace(visit=visit1)
                            news = news._replace(nround=i)

                            topop.append(k)
                            toappend.append(news)
                            break

                    update_scores(topop, toappend)
                    statecopy = statecopy.result(next_action)
            return statecopy


        def expand(state, action):
            """
            Returns a state resulting from taking an action from the list of untried nodes
            """
            statlist.append(Stat(state, action, 0, 1, i))
            return state.result(action)


        def best_child(state, c):
            """
            Returns the state resulting from taking the best action
            c value between 0 (max score) and 1 (prioritize exploration)
            """
            # All taken actions at this depth
            tried = [s for s in statlist if s.state == state]

            maxscore = -999
            maxaction = []
            # Compute the score
            for t in tried:
                score = (t.utility/t.visit) + c * math.sqrt(2 * math.log(i)/t.visit)
                if score > maxscore:
                    maxscore = score
                    del maxaction[:]
                    maxaction.append(t.action)
                elif score == maxscore:
                    maxaction.append(t.action)

            if len(maxaction) < 1:
                logging.error("IndexError: maxaction is empty!")

            return random.choice(maxaction)


        def default_policy(state):
            """
            The simulation to run when visiting unexplored nodes. Defaults to uniform random moves
            """
            while not state.terminal_test():
                state = state.result(random.choice(state.actions()))

            return normalize_delta(state.utility(self.player_id))


        def backup_negamax(delta):
            """
            Propagates the terminal utility up the search tree
            """
            topop = []
            toappend = []
            for k, s in enumerate(statlist):
                if s.nround == i:
                    if s.state.ply_count % 2 == plyturn:
                        utility1 = s.utility + delta
                        news = statlist[k]._replace(utility=utility1)
                    elif s.state.ply_count % 2 != plyturn:
                        utility1 = s.utility - delta
                        news = statlist[k]._replace(utility=utility1)

                    topop.append(k)
                    toappend.append(news)

            update_scores(topop, toappend)
            return


        def update_scores(topop, toappend):
            """
            Update the scoresheet
            """
            # Remove outdated tuples. Order needs to be in reverse or pop will fail!
            for p in sorted(topop, reverse=True):
                statlist.pop(p)
            # Add the updated ones
            for a in toappend:
                statlist.append(a)
            return


        def normalize_delta(delta):
            """
            Fits the utility of game states into the range between -1 and 1
            """
            if delta < 0:
                delta = -1
            elif delta > 0:
                delta = 1
            return delta


        next_state = tree_policy(state)
        if not next_state.terminal_test():
            delta = default_policy(next_state)
            backup_negamax(delta)

        return best_child(state, 0)