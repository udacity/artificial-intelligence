import gc
# import logging
import math
import pandas as pd
# import pdb
import random
# import sys


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
    # logging.basicConfig(filename='matches.log',level=logging.DEBUG)

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
        i = 1
        df = pd.DataFrame(columns=['board', 'plycount', 'locs', 'action', 'utility', 'visit', 'nround', 'score'])
        plyturn = state.ply_count % 2
        # Just to prevent a forfeit due to a no-action!
        self.queue.put(random.choice(state.actions()))

        while True:
            next_action, df = self.uct_search(state, df, i, plyturn)
            self.queue.put(next_action)
            # logging.info("Play %s, Round %s\n" % (state.ply_count, i))
            # logging.info("Selected action: %s\n" % next_action)
            # logging.info(str(df))
            # logging.info("\n-------------------------------------------------\n\n")
            gc.collect()
            i += 1


    def uct_search(self, state, df, i, plyturn):
        def tree_policy(state):
            """
            Determine the most urgent node to expand - balancing areas not explored and areas that look promising
            """
            # logging.debug("Executing tree policy")
            if state.terminal_test():
                return state

            # Unexplored nodes get priority
            untried = [a for a in state.actions() if a not in list(df.loc[df['board'] == str(state.board), 'action'])]

            if len(untried) > 0:
                action = random.choice(untried)
                return expand(state, action)
            else:
                next_action = best_child(state, 1)
                # Update the visit and round statistics
                df.loc[(df['board'] == str(state.board)) & (df['action'] == next_action), 'visit'] += 1
                # Mark the path taken for the current round of iteration
                df.loc[(df['board'] == str(state.board)) & (df['action'] == next_action), 'nround'] = i
                state = tree_policy(state.result(best_child(state, 1)))
                return state

        def expand(state, action):
            """
            Returns a state resulting from taking an action from the list of untried nodes
            """
            # logging.debug("Expanding untried nodes")
            df.loc[len(df)] = [str(state.board), state.ply_count, state.locs, action, 0, 1, i, 0]
            return state.result(action)

        def best_child(state, c):
            """
            Returns the state resulting from taking the best action
            c value between 0 (max score) and 1 (prioritize exploration)
            """
            # logging.debug("Getting the best child")
            df['score'] = (df['utility'].astype('float')/df['visit'].astype('float')) + df['visit'].apply(lambda x: c * math.sqrt(2 * math.log(i)/float(x)))
            df['score'] = df['score'].astype('float')
            # Get the index and action of the row with the maximum score for the present state
            maxscoreid = df.loc[df['board'] == str(state.board), 'score'].idxmax()
            next_action = df.iloc[maxscoreid]['action']

            return next_action

        def default_policy(state):
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
            # logging.info("%s: %s" % (str(self.player_id), delta))
            return delta


        def backup_negamax(delta):
            """
            Propagates the terminal utility up the search tree
            """
            # logging.debug("Propagating terminal value up the tree")
            df.loc[(df['nround'] == i) & (df['plycount'] % 2 == plyturn), 'utility'] += delta
            df.loc[(df['nround'] == i) & (df['plycount'] % 2 != plyturn), 'utility'] -= delta
            return

        next_state = tree_policy(state)

        if not next_state.terminal_test():
            delta = default_policy(next_state)
            backup_negamax(delta)

        return best_child(state, 0), df