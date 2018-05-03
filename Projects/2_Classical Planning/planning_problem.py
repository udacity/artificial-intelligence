
from functools import lru_cache

from aimacode.logic import PropKB
from aimacode.search import Node, Problem

from _utils import encode_state, decode_state
from my_planning_graph import PlanningGraph

    ##############################################################################
    #                 YOU DO NOT NEED TO MODIFY CODE IN THIS FILE                #
    ##############################################################################


class BasePlanningProblem(Problem):
    def __init__(self, initial, goal):
        self.state_map = sorted(initial.pos + initial.neg, key=str)
        self.initial_state_TF = encode_state(initial, self.state_map)
        super().__init__(self.initial_state_TF, goal=goal)

    @lru_cache()
    def h_unmet_goals(self, node):
        """ This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        return sum(1 for i, f in enumerate(self.state_map) if not node.state[i] and f in self.goal)

    @lru_cache()
    def h_pg_levelsum(self, node):
        """ This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of the number of actions that must be
        carried out from the current state in order to satisfy each individual
        goal condition.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        pg = PlanningGraph(self, node.state, serialize=True, ignore_mutexes=True)
        score = pg.h_levelsum()
        return score

    @lru_cache()
    def h_pg_maxlevel(self, node):
        """ This heuristic uses a planning graph representation of the problem
        to estimate the maximum level cost out of all the individual goal literals.
        The level cost is the first level where a goal literal appears in the
        planning graph.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        pg = PlanningGraph(self, node.state, serialize=True, ignore_mutexes=True)
        score = pg.h_maxlevel()
        return score

    @lru_cache()
    def h_pg_setlevel(self, node):
        """ This heuristic uses a planning graph representation of the problem
        to estimate the level cost in the planning graph to achieve all of the
        goal literals such that none of them are mutually exclusive.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        pg = PlanningGraph(self, node.state, serialize=True)
        score = pg.h_setlevel()
        return score

    def actions(self, state):
        """ Return the actions that can be executed in the given state. """
        possible_actions = []
        fluent = decode_state(state, self.state_map)
        for action in self.actions_list:
            is_possible = True
            for clause in action.precond_pos:
                if clause not in fluent.pos:
                    is_possible = False
                    break
            if not is_possible: continue
            for clause in action.precond_neg:
                if clause not in fluent.neg:
                    is_possible = False
                    break
            if is_possible: possible_actions.append(action)
        return possible_actions

    def result(self, state, action):
        """ Return the state that results from executing the given action in the
        given state. The action must be one of self.actions(state).
        """
        return tuple([
            (f and s not in action.effect_rem) or (s in action.effect_add)
            for f, s in zip(state, self.state_map)
        ])

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached """
        return all(f for f, c in zip(state, self.state_map) if c in self.goal)
