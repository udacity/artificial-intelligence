from copy import deepcopy
import math
import pandas as pd
import pdb
import random
import sys
import time

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
        next_action, df = self.uct_search(state)
        # Serialize the dataframe for the next turn
        self.context = df
        self.queue.put(random.choice(state.actions))


    def uct_search(self, state):
        # Serializable data frame
        if self.context:
            df = self.context
        else:
            df = pd.DataFrame(columns=['state', 'action', 'utility', 'visit'])

        start_time = time.time()
        i = 1

        def tree_policy(state):
            """
            Determine the most urgent node to expand - balancing areas not explored and areas that look promising
            """
            if state.terminal_test():
                return state

            # Unexplored nodes get priority
            untried = [a for a in state.actions() if a not in df.loc[df['state'] == state, 'action']]

            if len(untried) > 0:
                return expand(state, untried[0])
            else:
                tmp_state = tree_policy(state.result(best_child(state, 1)))
                return tmp_state

        def expand(state, action):
            """
            Returns a state resulting from taking an action from the list of untried nodes
            """
            tp.loc[len(tp)] = [state, action, 0, 1]
            return state.result(action)

        def best_child(state, c):
            """
            Returns the state resulting from taking the best action
            c value between 0 (max score) and 1 (prioritize exploration)
            """
            cs_df = deepcopy(df[df['state'] == state])
            cs_df['score'] = float(cs_df['utility']/cs_df['visit']) + float(c * math.sqrt((2 * math.log(i)/cs_df['visit'])))

            next_action = cs_df.iloc[df['score'].idxmax, 'action']
            tp.loc[len(tp)] = [state, next_action, 0, 1]

            return next_action

        def default_policy(state):
            """
            The simulation to run when visiting unexplored nodes. Defaults to uniform random moves
            """
            if state.terminal_test():
                delta = state.utility(self.player_id)
                # Normalize to [-1, 1]
                if abs(delta) == float('inf') and delta < 0:
                    delta = -1
                elif abs(delta) == float('inf') and delta > 0:
                    delta = 1
                return delta

            next_state = state.result(random.choice(state.actions()))
            value = default_policy(next_state)
            return value

        def backup_negamax(delta, df):
            """
            The utility of an action is updated here
            For negamax, ensure that the sign flipping sequence is correct (based on ply.count())
            """
            # Update the scoresheet
            if len(tp) % 2 == 0:
                # Ends with an odd index
                tp.loc[tp.index % 2 == 0, 'utility'] = -delta
                tp.loc[tp.index % 2 == 1, 'utility'] = delta
            else:
                # Ends with an even index
                tp.loc[tp.index % 2 == 0, 'utility'] = delta
                tp.loc[tp.index % 2 == 1, 'utility'] = -delta
            
            # Update the serializable data frame
            df = df.set_index(['state', 'action']).add(tp.set_index(['state', 'action']), fill_value=0).reset_index()
            return df

        # In the absence of an opening book, pick a random opening move
        # Need to do this to populate df with at least one row
        action = random.choice(state.actions())
        delta = default_policy(state.result(action))
        df.loc[len(df)] = [state, action, delta, 1]
        while time.time() - start_time < 1:
            # Temporal data frame
            tp = pd.DataFrame(columns=['state', 'action', 'utility', 'visit'])

            next_state = tree_policy(state)
            if not next_state.terminal_test():
                delta = default_policy(next_state)
                df = backup_negamax(delta, df)
                i += 1
                pdb.set_trace()
            else:
                # No point looping further if terminal state is hit
                # May explore the possibility of injecting some randomness here
                break

        return best_child(state, 0), df





