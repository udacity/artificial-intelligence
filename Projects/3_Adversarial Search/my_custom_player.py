# import logging
import datetime
import math
# import pdb
import random
import time

from copy import deepcopy
from collections import namedtuple

from sample_players import DataPlayer


class CustomPlayer(DataPlayer):
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
    i = 1
    plyturn = None
    statlist = []
    modifier = -1

    Stat = namedtuple('Stat', 'board plycount locs action utility visit nround')
    #logging.basicConfig(filename='matches.log',level=#logging.NOTSET)

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
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)
        self.plyturn = state.ply_count % 2
        if self.plyturn == 1:
            self.modifier = 1
        # Just to prevent a forfeit due to a no-action!
        self.queue.put(random.choice(state.actions()))
        #logging.info("\n-------------------------------------------------\n\n")
        #logging.info("Play %s\n" % (state.ply_count))
        # pdb.set_trace()
        while (self.queue._TimedQueue__stop_time -10) > time.perf_counter():
            #logging.info("\n-------------------------------------------------\n\n")
            #logging.info("Play %s\n" % (state.ply_count))

            next_action = self.uct_search(state)
            self.queue.put(next_action)
            #logging.info("Round %s\n" % (self.i))
            #logging.info("Selected action: %s\n" % next_action)
            #logging.info(str(self.statlist))
            #logging.info("\n-------------------------------------------------\n\n")
            self.i += 1

        #logging.info("Selected action: %s\n" % next_action)
        #logging.info("Rounds Simulated %s\n" % (self.i))
        #logging.info(str(self.statlist))
        #logging.info("\n-------------------------------------------------\n\n")


    def uct_search(self, state):
        #logging.debug("UCT Begin:%s" % str(state))
        next_state = self.tree_policy(state)

        if not next_state.terminal_test():
            delta = self.default_policy(next_state)
            self.backup_negamax(delta)

        #logging.debug("UCT End:%s" % str(state))
        return self.best_child(state, 0)


    def tree_policy(self, state):
        statecopy = deepcopy(state) # State 0

        while not statecopy.terminal_test():
            #logging.debug("Start: %s" % str(statecopy))
            # All taken actions at this depth
            tried = [s.action for s in self.statlist if s.board == str(statecopy.board)]
            #logging.debug("Tried: %s" % str(tried))
            # See if there's any untried actions left
            untried = [a for a in statecopy.actions() if a not in tried]
            #logging.debug("Available actions %s\n Untried %s" % (str(statecopy.actions()), str(untried)))

            topop = []
            toappend = []

            if len(untried) > 0:
                next_action = random.choice(untried)
                statecopy = self.expand(statecopy, next_action)
                break
            else:
                next_action = self.best_child(statecopy, 1)

                for k, s in enumerate(self.statlist):
                    if s.board == str(statecopy.board) and s.action == next_action:
                        visit1 = self.statlist[k].visit + 1
                        news = self.statlist[k]._replace(visit=visit1)
                        news = news._replace(nround=self.i)

                        topop.append(k)
                        toappend.append(news)
                        break

                self.update_scores(topop, toappend)
                #logging.debug(str(self.statlist))
                statecopy = statecopy.result(next_action)

            #logging.debug("\nEnd: %s" % str(statecopy))
        return statecopy


    def expand(self, state, action):
        """
        Returns a state resulting from taking an action from the list of untried nodes
        """
        self.statlist.append(self.Stat(str(state.board), state.ply_count, state.locs, action, 0, 1, self.i))
        return state.result(action)


    def best_child(self, state, c):
        """
        Returns the state resulting from taking the best action
        c value between 0 (max score) and 1 (prioritize exploration)
        """
        # All taken actions at this depth
        tried = [s for s in self.statlist if s.board == str(state.board)]
        #logging.debug("Tried: %s" % str(tried))

        maxscore = -999
        maxaction = []
        # Compute the score
        for t in tried:
            score = (t.utility/t.visit) + c * math.sqrt(2 * math.log(self.i)/t.visit)
            #logging.debug("Action %s Score %s" % (t.action, str(score)))
            if score > maxscore:
                maxscore = score
                del maxaction[:]
                maxaction.append(t.action)
            elif score == maxscore:
                maxaction.append(t.action)

        return random.choice(maxaction)


    def default_policy(self, state):
        """
        The simulation to run when visiting unexplored nodes. Defaults to uniform random moves
        """
        while not state.terminal_test():
            state = state.result(random.choice(state.actions()))

        delta = state.utility(self.player_id)
        if abs(delta) == float('inf') and delta < 0:
            delta = -1
        elif abs(delta) == float('inf') and delta > 0:
            delta = 1
        #logging.debug("%s: %s" % (str(self.player_id), delta))
        return delta


    def backup_negamax(self, delta):
        """
        Propagates the terminal utility up the search tree
        """
        topop = []
        toappend = []
        for k, s in enumerate(self.statlist):
            if s.nround == self.i:
                if s.plycount % 2 == self.plyturn:
                    utility1 = s.utility + delta * self.modifier
                    news = self.statlist[k]._replace(utility=utility1)
                elif s.plycount % 2 != self.plyturn:
                    utility1 = s.utility - delta * self.modifier
                    news = self.statlist[k]._replace(utility=utility1)

                topop.append(k)
                toappend.append(news)

        self.update_scores(topop, toappend)

        return


    def update_scores(self, topop, toappend):
        # Remove outdated tuples. Order needs to be in reverse or pop will fail!
        for p in sorted(topop, reverse=True):
            self.statlist.pop(p)
        # Add the updated ones
        for a in toappend:
            self.statlist.append(a)

        return