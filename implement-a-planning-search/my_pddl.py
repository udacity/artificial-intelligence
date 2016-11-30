from aimacode.planning import PDLL
from aimacode.planning import Action
from aimacode.utils import expr


def acp1_pddl() -> PDLL:
    """Definition for Problem 1

        2 cargo items: {C1, C2}
        2 airplanes: {P1, P2}
        2 airports: {SFO, JFK}
        initial: C1 and P1 are at SFO, P2 and C2 are at JFK
        goal: C1 at JFK, C2 at SFO
        """

    init = [
        # TODO define the initial state as a list of fluent expressions
    ]

    def goal_test(kb):
        required = [
            # TODO define the goal test requirements as a list of fluent expressions
        ]
        for q in required:
            if kb.ask(q) is False:
                return False
        return True

    ## Actions
    # TODO define the load, Unload, and Fly actions using first order logic and the Action class
    # Hint: take a look at the aimacode.planning module in the code base

    #  Load
    # load = Action(expr("Load(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Unload
    # unload = Action(expr("Unload(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Fly
    # fly = Action(expr("Fly(p, f, t)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    # return PDLL(init, [load, unload, fly], goal_test)


def acp2_pddl() -> PDLL:
    """Definition for Problem 2

        3 cargo items: {C1, C2, C3}
        3 airplanes: {P1, P2, P3}
        3 airports: {SFO, JFK, ATL}
        initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 and P3 are at ATL
        goal: C1 at JFK, C2 at SFO, C3 at SFO
        """
    # TODO implement problem 2
    pass


def acp3_pddl() -> PDLL:
    """Definition for Problem 3

        4 cargo items: {C1, C2, C3, C4}
        2 airplanes: {P1, P2}
        4 airports: {SFO, JFK, ATL, ORD}
        initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 at ATL, C4 at ORD
        goal: C1, C3 at JFK, C2, C4 at SFO
        """
    # TODO implement problem 3
    pass
