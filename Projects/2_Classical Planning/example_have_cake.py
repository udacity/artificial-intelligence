
from aimacode.planning import Action
from aimacode.search import (
    breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search
)
from aimacode.utils import expr

from _utils import (
    FluentState, encode_state, make_relations, run_search
)
from planning_problem import BasePlanningProblem

    ##############################################################################
    #                 YOU DO NOT NEED TO MODIFY CODE IN THIS FILE                #
    ##############################################################################


class HaveCakeProblem(BasePlanningProblem):
    def __init__(self, initial, goal):
        """
        Parameters
        ----------
        initial : FluentState
            A representation of the initial problem state as a collection
            of positive and negative literals (each literal fluent should
            be an `aimacode.utils.Expr` instance)

        goal : iterable
            A collection of literal fluents describing the goal state of
            the problem (each fluent should be an instance of the
            `aimacode.utils.Expr` class)
        """
        super().__init__(initial, goal)
        self.actions_list = self.get_actions()

    def get_actions(self):
        precond_pos = [expr("Have(Cake)")]
        precond_neg = []
        effect_add = [expr("Eaten(Cake)")]
        effect_rem = [expr("Have(Cake)")]
        eat_action = Action(expr("Eat(Cake)"),
                            [precond_pos, precond_neg],
                            [effect_add, effect_rem])
        precond_pos = []
        precond_neg = [expr("Have(Cake)")]
        effect_add = [expr("Have(Cake)")]
        effect_rem = []
        bake_action = Action(expr("Bake(Cake)"),
                             [precond_pos, precond_neg],
                             [effect_add, effect_rem])
        return [eat_action, bake_action]


def have_cake():
    cakes = ['Cake']
    have_relations = make_relations('Have', cakes)
    eaten_relations = make_relations('Eaten', cakes)
    
    def get_init():
        pos = have_relations
        neg = eaten_relations
        return FluentState(pos, neg)

    def get_goal():
        return have_relations + eaten_relations

    return HaveCakeProblem(get_init(), get_goal())


if __name__ == '__main__':
    p = have_cake()
    print("**** Have Cake example problem setup ****")
    print("Fluents in this problem are:")
    for f in p.state_map:
        print('   {}'.format(f))

    print("Initial state for this problem is {}".format(p.initial))
    print("Actions for this domain are:")
    for a in p.actions_list:
        print('   {}{}'.format(a.name, a.args))
    print("Goal requirement for this problem are:")
    for g in p.goal:
        print('   {}'.format(g))
    print()
    print("*** Breadth First Search")
    run_search(p, breadth_first_search)
    print("*** Depth First Search")
    run_search(p, depth_first_graph_search)
    print("*** Uniform Cost Search")
    run_search(p, uniform_cost_search)
    print("*** Greedy Best First Graph Search - null heuristic")
    run_search(p, greedy_best_first_graph_search, parameter=lambda x: 0)
    print("*** A-star null heuristic")
    run_search(p, astar_search, lambda x: 0)
