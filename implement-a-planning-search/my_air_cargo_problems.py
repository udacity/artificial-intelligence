
from helpers.planning_problem import PlanningProblem
from helpers.lp_utils import FluentState, encode_state, decode_state, run_search

from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import InstrumentedProblem, Node
from aimacode.search import breadth_first_search, astar_search, breadth_first_tree_search
from aimacode.search import depth_first_graph_search, uniform_cost_search, greedy_best_first_graph_search
from aimacode.search import depth_limited_search, recursive_best_first_search
from aimacode.utils import expr

from my_planning_graph import PlanningGraph


class AirCargoProblem(PlanningProblem):

    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        PlanningProblem.__init__(self, initial, goal)

    def get_actions(self):
        '''
        This method creates concrete actions for all actions in the problem
        domain. It is computationally expensive to call this method directly;
        however, it is called in the PlanningProblem constructor and the
        results cached in the `actions_list` property inherited by all
        PlanningProblem subclasses.

        Returns:
        ----------
        list<Action>
            list of Action objects
        '''
        #TODO Part 2 create concrete actions for the problem instance based on the domain actions: Load, Unload, and Fly

        def load_actions():
            '''Create all concrete Load actions and return a list

            :return: list of Action objects
            '''
            loads = []
            # TODO Part 2 using instance variables, create all load ground actions from the domain Load action
            return loads

        def unload_actions():
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            unloads = []
            # TODO Part 2 using instance variables, create all Unload ground actions from the domain Unload action
            return unloads

        def fly_actions():
            '''Create all concrete Fly actions and return a list

            :return: list of Action objects
            '''
            flys = []
            # TODO Part 2 using instance variables, create all Fly ground actions from the domain Fly action
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        # TODO Part 2 implement (see PlanningProblem in helpers.planning_problem)
        possible_actions = []
        return possible_actions

    def result(self, state: str, action: Action):
        # TODO implement (see PlanningProblem in helpers.planning_problem)
        new_state = FluentState([], [])
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    def h_pg_setlevel(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions.
        '''
        # TODO: Complete the implmentation of this heuristic in the 
        # PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_setlevel = pg.h_setlevel()
        return pg_setlevel

    def h_pg_levelsum(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        '''
        # TODO: Complete the implmentation of this heuristic in the 
        # PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    def h_ignore_preconditions(self, node: Node):
        '''
        This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        '''
        # TODO Part 3 implement (see Russell-Norvig Edition-3 10.2.3  or Russell-Norvig Edition-2 11.2)
        count = 0
        return count

def air_cargo_p1()->AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

def air_cargo_p2()->AirCargoProblem:
    # TODO Part 2 implement Problem 2 definition
    pass

def air_cargo_p3()->AirCargoProblem:
    # TODO Part 2 implement Problem 3 definition
    pass
