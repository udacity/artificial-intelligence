
from aimacode.planning import Action
from aimacode.utils import expr
from _utils import (
    FluentState, encode_state, decode_state, create_expressions, make_relations
)

from planning_problem import BasePlanningProblem

    ##############################################################################
    #                 YOU DO NOT NEED TO MODIFY CODE IN THIS FILE                #
    ##############################################################################


class AirCargoProblem(BasePlanningProblem):
    def __init__(self, cargos, planes, airports, initial, goal):
        """
        Parameters
        ----------
        cargos : list
            A list of names for cargo entities in the problem domain

        planes : list
            A list of names for airplane entities in the problem domain

        airports : list
            A list of names for airport entities in the problem domain

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
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        """ This method creates concrete actions (no variables) for all actions
        in the problem domain action schema and turns them into complete Action
        objects as defined in the aimacode.planning module. It is computationally
        expensive to call this method directly; however, it is called in the
        constructor and the results cached in the `actions_list` property.

        Returns
        -------
            list of Action objects
        """

        def load_actions():
            """ Create all concrete Load actions

            Returns
            -------
            collection of Action objects
            """
            loads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        precond_pos = set([expr("At({}, {})".format(c, a)),
                                       expr("At({}, {})".format(p, a))
                                       ])
                        precond_neg = set([])
                        effect_add = set([expr("In({}, {})".format(c, p))])
                        effect_rem = set([expr("At({}, {})".format(c, a))])
                        load = Action(expr("Load({}, {}, {})".format(c, p, a)),
                                      [precond_pos, precond_neg],
                                      [effect_add, effect_rem])
                        loads.append(load)
            return loads

        def unload_actions():
            """Create all concrete Unload actions

            Returns
            -------
            collection of Action objects
            """
            unloads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        precond_pos = set([expr("In({}, {})".format(c, p)),
                                       expr("At({}, {})".format(p, a)),
                                       ])
                        precond_neg = set([])
                        effect_add = set([expr("At({}, {})".format(c, a))])
                        effect_rem = set([expr("In({}, {})".format(c, p))])
                        unload = Action(expr("Unload({}, {}, {})".format(c, p, a)),
                                      [precond_pos, precond_neg],
                                      [effect_add, effect_rem])
                        unloads.append(unload)
            return unloads

        def fly_actions():
            """Create all concrete Fly actions

            Returns
            -------
            collection of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = set([expr("At({}, {})".format(p, fr)),
                                           ])
                            precond_neg = set([])
                            effect_add = set([expr("At({}, {})".format(p, to))])
                            effect_rem = set([expr("At({}, {})".format(p, fr))])
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()


def air_cargo_p1():
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    at_relations = make_relations('At', cargos + planes, airports)
    in_relations = make_relations('In', cargos, planes)
    pos = create_expressions([
        'At(C1, SFO)',
        'At(C2, JFK)',
        'At(P1, SFO)',
        'At(P2, JFK)',
        ])
    init = FluentState(pos, [r for r in at_relations + in_relations if r not in pos])
    goal = create_expressions(['At(C1, JFK)', 'At(C2, SFO)'])
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2():
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']
    at_relations = make_relations('At', cargos + planes, airports)
    in_relations = make_relations('In', cargos, planes)
    pos = create_expressions([
        'At(C1, SFO)',
        'At(C2, JFK)',
        'At(C3, ATL)',
        'At(P1, SFO)',
        'At(P2, JFK)',
        'At(P3, ATL)',
    ])
    init = FluentState(pos, [r for r in at_relations + in_relations if r not in pos])
    goal = create_expressions(['At(C1, JFK)', 'At(C2, SFO)', 'At(C3, SFO)'])
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p3():
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']
    at_relations = make_relations('At', cargos + planes, airports)
    in_relations = make_relations('In', cargos, planes)
    pos = create_expressions([
        'At(C1, SFO)',
        'At(C2, JFK)',
        'At(C3, ATL)',
        'At(C4, ORD)',
        'At(P1, SFO)',
        'At(P2, JFK)',
    ])
    init = FluentState(pos, [r for r in at_relations + in_relations if r not in pos])
    goal = create_expressions(['At(C1, JFK)', 'At(C2, SFO)', 'At(C3, JFK)', 'At(C4, SFO)'])
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p4():
    cargos = ['C1', 'C2', 'C3', 'C4', 'C5']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']
    at_relations = make_relations('At', cargos + planes, airports)
    in_relations = make_relations('In', cargos, planes)
    pos = create_expressions([
        'At(C1, SFO)',
        'At(C2, JFK)',
        'At(C3, ATL)',
        'At(C4, ORD)',
        'At(C5, ORD)',
        'At(P1, SFO)',
        'At(P2, JFK)',
    ])
    init = FluentState(pos, [r for r in at_relations + in_relations if r not in pos])
    goal = create_expressions(['At(C1, JFK)', 'At(C2, SFO)', 'At(C3, JFK)', 'At(C4, SFO)', 'At(C5, JFK)'])
    return AirCargoProblem(cargos, planes, airports, init, goal)
