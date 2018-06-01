
import textwrap
import unittest

from itertools import chain, combinations

from aimacode.utils import expr
from aimacode.planning import Action
from aimacode.search import Node
from example_have_cake import have_cake
from air_cargo_problems import (
    air_cargo_p1, air_cargo_p2, air_cargo_p3, air_cargo_p4
)
from my_planning_graph import PlanningGraph, LiteralLayer, ActionLayer
from layers import makeNoOp, make_node


def chain_dedent(str, *args, **kwargs):
    return textwrap.dedent(str.format(*args, **kwargs)).replace("\n", " ")


class BaseMutexTest(unittest.TestCase):
    def setUp(self):
        self.cake_problem = have_cake()
        self.cake_pg = PlanningGraph(self.cake_problem, self.cake_problem.initial, serialize=False).fill()

        self.eat_action, self.bake_action = [a for a in self.cake_pg._actionNodes if not a.no_op]
        no_ops = [a for a in self.cake_pg._actionNodes if a.no_op]
        self.null_action = make_node(Action(expr('Null()'), [set(), set()], [set(), set()]))

        # some independent nodes for testing mutexes
        at_here = expr('At(here)')
        at_there = expr('At(there)')
        self.pos_literals = [at_here, at_there]
        self.neg_literals = [~x for x in self.pos_literals]
        self.literal_layer = LiteralLayer(self.pos_literals + self.neg_literals, ActionLayer())
        self.literal_layer.update_mutexes()
        
        # independent actions for testing mutex
        self.actions = [
            make_node(Action(expr('Go(here)'), [set(), set()], [set([at_here]), set()])),
            make_node(Action(expr('Go(there)'), [set(), set()], [set([at_there]), set()]))
        ]
        self.no_ops = [make_node(x) for x in chain(*(makeNoOp(l) for l in self.pos_literals))]
        self.action_layer = ActionLayer(self.no_ops + self.actions, self.literal_layer)
        self.action_layer.update_mutexes()
        for action in self.no_ops + self.actions:
            self.action_layer.add_inbound_edges(action, action.preconditions)
            self.action_layer.add_outbound_edges(action, action.effects)


class Test_1_InconsistentEffectsMutex(BaseMutexTest):
    def setUp(self):
        super().setUp()
        # bake has the effect Have(Cake) which is the logical negation of the effect 
        # ~Have(cake) from the persistence action ~NoOp::Have(cake)
        no_ops = [a for a in self.cake_pg._actionNodes if a.no_op]
        self.inconsistent_effects_actions = [self.bake_action, no_ops[3]]

        X, Y = expr('FakeFluent_X'), expr('FakeFluent_Y')
        self.fake_not_inconsistent_effects_actions = [
            make_node(Action(expr('FakeAction(X)'), [set([X]), set()], [set([X]), set()])),
            make_node(Action(expr('FakeAction(Y)'), [set([Y]), set()], [set([Y]), set()])),
        ]

    def test_1a_inconsistent_effects_mutex(self):
        acts = [self.actions[0], self.no_ops[0]]
        self.assertFalse(self.action_layer._inconsistent_effects(*acts), chain_dedent("""
            '{!s}' and '{!s}' should NOT be mutually exclusive by inconsistent effects.
            No pair of effects from {!s} and {!s} are logical opposites.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].effects)))

    def test_1b_inconsistent_effects_mutex(self):
        acts = [self.bake_action, self.null_action]
        self.assertFalse(self.action_layer._inconsistent_effects(*acts), chain_dedent("""
            '{!s}' and '{!s}' should NOT be mutually exclusive by inconsistent effects.
            No pair of effects from {!s} and {!s} are logical opposites.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].effects)))

    def test_1c_inconsistent_effects_mutex(self):
        acts = self.fake_not_inconsistent_effects_actions
        self.assertFalse(self.action_layer._inconsistent_effects(*acts), chain_dedent("""
            '{!s}' and '{!s}' should NOT be mutually exclusive by inconsistent effects.
            No pair of effects from {!s} and {!s} are logical opposites.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].effects)))

    def test_1d_inconsistent_effects_mutex(self):
        acts = [self.actions[0], self.no_ops[1]]
        self.assertTrue(self.action_layer._inconsistent_effects(*acts), chain_dedent("""
            '{!s}' and '{!s}' should be mutually exclusive by inconsistent effects.
            At least one pair of effects from {!s} and {!s} are logical opposites.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].effects)))

    def test_1e_inconsistent_effects_mutex(self):
        # inconsistent effects mutexes are static -- if they appear in any layer,
        # then they should appear in every later layer of the planning graph
        for idx, layer in enumerate(self.cake_pg.action_layers):
            if set(self.inconsistent_effects_actions) <= layer:
                self.assertTrue(layer.is_mutex(*self.inconsistent_effects_actions),
                    ("Actions {} and {} were not mutex in layer {} of the planning graph").format(
                        self.inconsistent_effects_actions[0], self.inconsistent_effects_actions[1], idx)
                )


class Test_2_InterferenceMutex(BaseMutexTest):
    def setUp(self):
        super().setUp()
        # the persistence action ~NoOp::Have(cake) has the effect ~Have(cake), which is
        # the logical negation of Have(cake) -- the precondition for the Eat(cake) action
        no_ops = [a for a in self.cake_pg._actionNodes if a.no_op]
        self.interference_actions = [self.eat_action, no_ops[3]]

        X, Y = expr('FakeFluent_X'), expr('FakeFluent_Y')
        self.fake_interference_actions = [
            make_node(Action(expr('FakeAction(X)'), [set([X]), set()], [set([X]), set()])),
            make_node(Action(expr('FakeAction(Y)'), [set([Y]), set()], [set([Y]), set()])),
        ]

    def test_2a_interference_mutex(self):
        acts = [self.actions[0], self.actions[1]]
        self.assertFalse(self.action_layer._interference(*acts), chain_dedent("""
            '{!s}' and '{!s}' should NOT be mutually exclusive by interference.
            None of these effects {!s} negates any of these preconditions {!s}
            and none of these effects {!s} negates any of these preconditions {!s}.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].preconditions),
        acts[1].effects, acts[1].preconditions))

    def test_2b_interference_mutex(self):
        acts = [self.no_ops[0], self.no_ops[0]]
        self.assertFalse(self.action_layer._interference(*acts), chain_dedent("""
            '{!s}' should NOT be mutually exclusive with itself by interference.
            None of these effects {!s} negates any of these preconditions {!s}
            and none of these effects {!s} negates any of these preconditions {!s}.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].preconditions),
        acts[1].effects, acts[1].preconditions))

    def test_2c_interference_mutex(self):
        acts = self.fake_interference_actions
        self.assertFalse(self.action_layer._interference(*acts), chain_dedent("""
            '{!s}' should NOT be mutually exclusive with itself by interference.
            None of these effects {!s} negates any of these preconditions {!s}
            and none of these effects {!s} negates any of these preconditions {!s}.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].preconditions),
        acts[1].effects, acts[1].preconditions))
    
    def test_2d_interference_mutex(self):
        acts = [self.actions[0], self.no_ops[1]]
        self.assertTrue(self.action_layer._interference(*acts), chain_dedent("""
            '{!s}' and '{!s}' should be mutually exclusive by interference.
            At least one of these effects {!s} negates one of these preconditions {!s}
            or one of these effects {!s} negates one of these preconditions {!s}.
        """, acts[0], acts[1], list(acts[0].effects), list(acts[1].preconditions),
        acts[1].effects, acts[1].preconditions))

    def test_2e_interference_mutex(self):
        # interference mutexes are static -- if they appear in any layer,
        # then they should appear in every later layer of the planning graph
        for idx, layer in enumerate(self.cake_pg.action_layers):
            if set(self.interference_actions) <= layer:
                self.assertTrue(layer.is_mutex(*self.interference_actions), chain_dedent("""
                    Actions '{}' and '{}' were not mutex in layer {} of the planning graph
                """, self.interference_actions[0], self.interference_actions[1], idx))


class Test_3_NegationMutex(BaseMutexTest):
    def test_3a_negation_mutex(self):
        lits = [self.pos_literals[0], self.neg_literals[0]]
        self.assertTrue(self.literal_layer._negation(*lits), chain_dedent("""
            The literals '{litA!s}' and '{litB!s}' should be mutually exclusive
            by negation: ~'{litA!s}' == '{litB!s}'
            """, litA=lits[0], litB=lits[1])
        )

    def test_3b_negation_mutex(self):
        lits = [self.pos_literals[0], self.neg_literals[1]]
        self.assertFalse(self.literal_layer._negation(*lits), chain_dedent("""
            The literals '{litA!s}' and '{litB!s}' should NOT be mutually exclusive
            by negation: ~'{litA!s}' != '{litB!s}'
            """, litA=lits[0], litB=lits[1])
        )
        
    def test_3c_negation_mutex(self):
        # Negation mutexes are static, so if they appear in one layer then they
        # should appear in every later layer of the planning graph
        litlayer = self.cake_pg.literal_layers[-1]
        self.assertTrue(
            all(litlayer.is_mutex(l, ~l) for l in self.cake_problem.state_map),
            chain_dedent("""
                One or more literal was not marked as mutex with its negation
                in the last layer of the planning graph.
            """)
        )

class Test_4_CompetingNeedsMutex(BaseMutexTest):
    def setUp(self):
        super().setUp()
        # eat has precondition Have(cake) and bake has precondition ~Have(cake)
        # which are logical inverses, so eat & bake should be mutex at every
        # level of the planning graph where both actions appear
        self.competing_needs_actions = [self.eat_action, self.bake_action]

        # competing needs tests -- build two copies of the planning graph: one where
        #  A, B, and C are pairwise mutex, and another where they are not
        A, B, C = expr('FakeFluent_A'), expr('FakeFluent_B'), expr('FakeFluent_C')
        self.fake_competing_needs_actions = [
            make_node(Action(expr('FakeAction(A)'), [set([A]), set()], [set([A]), set()])),
            make_node(Action(expr('FakeAction(B)'), [set([B]), set()], [set([B]), set()])),
            make_node(Action(expr('FakeAction(C)'), [set([C]), set()], [set([C]), set()]))
        ]
        competing_layer = LiteralLayer([A, B, C], ActionLayer())
        for a1, a2 in combinations([A, B, C], 2): competing_layer.set_mutex(a1, a2)
        self.competing_action_layer = ActionLayer(competing_layer.parent_layer, competing_layer, False, True)
        for action in self.fake_competing_needs_actions:
            self.competing_action_layer.add(action)
            competing_layer |= action.effects
            competing_layer.add_outbound_edges(action, action.preconditions)
            self.competing_action_layer.add_inbound_edges(action, action.preconditions)
            self.competing_action_layer.add_outbound_edges(action, action.effects)

        not_competing_layer = LiteralLayer([A, B, C], ActionLayer())
        self.not_competing_action_layer = ActionLayer(not_competing_layer.parent_layer, not_competing_layer, False, True)
        for action in self.fake_competing_needs_actions:
            self.not_competing_action_layer.add(action)
            not_competing_layer |= action.effects
            not_competing_layer.add_outbound_edges(action, action.preconditions)
            self.not_competing_action_layer.add_inbound_edges(action, action.preconditions)
            self.not_competing_action_layer.add_outbound_edges(action, action.effects)

    def test_4a_competing_needs_mutex(self):
        acts = [self.no_ops[0], self.no_ops[2]]
        self.assertFalse(self.action_layer._competing_needs(*acts),
            "'{!s}' and '{!s}' should NOT be mutually exclusive by competing needs".format(*acts))

    def test_4b_competing_needs_mutex(self):
        acts = [self.no_ops[0], self.no_ops[1]]
        self.assertTrue(self.action_layer._competing_needs(*acts),
            "'{!s}' and '{!s}' should be mutually exclusive by competing needs".format(*acts))

    def test_4c_competing_needs_mutex(self):
        for acts in combinations(self.fake_competing_needs_actions, 2):
            self.assertFalse(self.not_competing_action_layer._competing_needs(*acts),
                ("'{!s}' and '{!s}' should NOT be mutually exclusive by competing needs unless " +
                 "every pair of actions is mutex in the parent layer").format(*acts))

    def test_4d_competing_needs_mutex(self):
        for acts in combinations(self.fake_competing_needs_actions, 2):
            self.assertTrue(self.competing_action_layer._competing_needs(*acts),
                ("'{!s}' and '{!s}' should be mutually exclusive by competing needs if every " +
                "pair of actions is mutex in the parent layer").format(*acts))

    def test_4e_competing_needs_mutex(self):
        # competing needs mutexes are dynamic -- they only appear in some levels of the planning graph
        for idx, layer in enumerate(self.cake_pg.action_layers):
            if set(self.competing_needs_actions) <= layer:
                self.assertTrue(layer.is_mutex(*self.competing_needs_actions),
                    ("Actions {} and {} were not mutex in layer {} of the planning graph").format(
                        self.competing_needs_actions[0], self.competing_needs_actions[1], idx)
                )
        

class Test_5_InconsistentSupportMutex(BaseMutexTest):
    def setUp(self):
        super().setUp()
        self.ac_problem = air_cargo_p1()
        self.ac_pg_serial = PlanningGraph(self.ac_problem, self.ac_problem.initial).fill()
        # In(C1, P2) and In(C2, P1) have inconsistent support when they first appear in
        # the air cargo problem, 
        self.inconsistent_support_literals = [expr("In(C1, P2)"), expr("In(C2, P1)")]

    def test_5a_inconsistent_support_mutex(self):
        # inconsistent support mutexes are dynamic -- they should not remain mutex at the last layer
        litA, litB = self.inconsistent_support_literals
        litlayer = self.ac_pg_serial.literal_layers[2]
        self.assertTrue(litlayer._inconsistent_support(litA, litB),
            chain_dedent("""
            The literals '{!s}' and '{!s}' should be mutually exclusive by inconsistent support
            in the second layer. All of the actions actions that produce '{!s}': {!s}
            and all of the actions that produce '{!s}': {!s} are pairwise mutex in the parent layer.
            """, litA, litB, litA, litlayer.parents[litA], litB, litlayer.parents[litB])
        )
        
    def test_5b_inconsistent_support_mutex(self):
        litA, litB = self.inconsistent_support_literals
        litlayer = self.ac_pg_serial.literal_layers[-2]
        self.assertFalse(litlayer._inconsistent_support(litA, litB), chain_dedent("""
            The literals '{!s}' and '{!s}' should NOT be mutually exclusive by inconsistent support
            in the penultimate layer. At least one of the actions that produce '{!s}': {!s}
            and one of the actions that produce '{!s}': {!s} should not be mutex in the parent layer.
            """, litA, litB, litA, litlayer.parents[litA], litB, litlayer.parents[litB])
        )

class BaseHeuristicTest(unittest.TestCase):
    def setUp(self):
        self.cake_problem = have_cake()
        self.ac_problem_1 = air_cargo_p1()
        self.ac_problem_2 = air_cargo_p2()
        self.ac_problem_3 = air_cargo_p3()
        self.ac_problem_4 = air_cargo_p4()
        self.cake_node = Node(self.cake_problem.initial)
        self.ac_node_1 = Node(self.ac_problem_1.initial)
        self.ac_node_2 = Node(self.ac_problem_2.initial)
        self.ac_node_3 = Node(self.ac_problem_3.initial)
        self.ac_node_4 = Node(self.ac_problem_4.initial)
        self.msg = "Make sure all your mutex tests pass before troubleshooting this function."


class Test_6_MaxLevelHeuristic(BaseHeuristicTest):
    def test_6a_maxlevel(self):
        self.assertEqual(self.cake_problem.h_pg_maxlevel(self.cake_node), 1, self.msg)

    def test_6b_maxlevel(self):
        self.assertEqual(self.ac_problem_1.h_pg_maxlevel(self.ac_node_1), 2, self.msg)

    def test_6c_maxlevel(self):
        self.assertEqual(self.ac_problem_2.h_pg_maxlevel(self.ac_node_2), 2, self.msg)

    def test_6d_maxlevel(self):
        self.assertEqual(self.ac_problem_3.h_pg_maxlevel(self.ac_node_3), 3, self.msg)

    def test_6e_maxlevel(self):
        self.assertEqual(self.ac_problem_4.h_pg_maxlevel(self.ac_node_4), 3, self.msg)


class Test_7_LevelSumHeuristic(BaseHeuristicTest):
    def test_7a_levelsum(self):
        self.assertEqual(self.cake_problem.h_pg_levelsum(self.cake_node), 1, self.msg)

    def test_7b_levelsum(self):
        self.assertEqual(self.ac_problem_1.h_pg_levelsum(self.ac_node_1), 4, self.msg)

    def test_7c_levelsum(self):
        self.assertEqual(self.ac_problem_2.h_pg_levelsum(self.ac_node_2), 6, self.msg)

    def test_7d_levelsum(self):
        self.assertEqual(self.ac_problem_3.h_pg_levelsum(self.ac_node_3), 10, self.msg)

    def test_7e_levelsum(self):
        self.assertEqual(self.ac_problem_4.h_pg_levelsum(self.ac_node_4), 13, self.msg)


class Test_8_SetLevelHeuristic(BaseHeuristicTest):
    def test_8a_setlevel(self):
        self.assertEqual(self.cake_problem.h_pg_setlevel(self.cake_node), 2, self.msg)

    def test_8b_setlevel(self):
        self.assertEqual(self.ac_problem_1.h_pg_setlevel(self.ac_node_1), 4, self.msg)

    def test_8c_setlevel(self):
        self.assertEqual(self.ac_problem_2.h_pg_setlevel(self.ac_node_2), 4, self.msg)

    def test_8d_setlevel(self):
        self.assertEqual(self.ac_problem_3.h_pg_setlevel(self.ac_node_3), 6, self.msg)

    def test_8e_setlevel(self):
        self.assertEqual(self.ac_problem_4.h_pg_setlevel(self.ac_node_4), 6, self.msg)


if __name__ == '__main__':
    unittest.main()
