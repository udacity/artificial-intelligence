import os
import sys

parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(parent), "aimacode"))
import unittest
from aimacode.utils import expr
from aimacode.planning import Action
from example_have_cake import have_cake
from my_planning_graph import (
    PlanningGraph, PgNode_a, PgNode_s, mutexify
)


class TestPlanningGraphLevels(unittest.TestCase):
    def setUp(self):
        self.p = have_cake()
        self.pg = PlanningGraph(self.p, self.p.initial)

    def test_add_action_level(self):
        # for level, nodeset in enumerate(self.pg.a_levels):
        #     for node in nodeset:
        #         print("Level {}: {}{})".format(level, node.action.name, node.action.args))
        self.assertEqual(len(self.pg.a_levels[0]), 3, len(self.pg.a_levels[0]))
        self.assertEqual(len(self.pg.a_levels[1]), 6, len(self.pg.a_levels[1]))

    def test_add_literal_level(self):
        # for level, nodeset in enumerate(self.pg.s_levels):
        #     for node in nodeset:
        #         print("Level {}: {})".format(level, node.literal))
        self.assertEqual(len(self.pg.s_levels[0]), 2, len(self.pg.s_levels[0]))
        self.assertEqual(len(self.pg.s_levels[1]), 4, len(self.pg.s_levels[1]))
        self.assertEqual(len(self.pg.s_levels[2]), 4, len(self.pg.s_levels[2]))


class TestPlanningGraphMutex(unittest.TestCase):
    def setUp(self):
        self.p = have_cake()
        self.pg = PlanningGraph(self.p, self.p.initial)
        # some independent nodes for testing mutex
        self.na1 = PgNode_a(Action(expr('Go(here)'),
                                   [[], []], [[expr('At(here)')], []]))
        self.na2 = PgNode_a(Action(expr('Go(there)'),
                                   [[], []], [[expr('At(there)')], []]))
        self.na3 = PgNode_a(Action(expr('Noop(At(there))'),
                                   [[expr('At(there)')], []], [[expr('At(there)')], []]))
        self.na4 = PgNode_a(Action(expr('Noop(At(here))'),
                                   [[expr('At(here)')], []], [[expr('At(here)')], []]))
        self.na5 = PgNode_a(Action(expr('Reverse(At(here))'),
                                   [[expr('At(here)')], []], [[], [expr('At(here)')]]))
        self.ns1 = PgNode_s(expr('At(here)'), True)
        self.ns2 = PgNode_s(expr('At(there)'), True)
        self.ns3 = PgNode_s(expr('At(here)'), False)
        self.ns4 = PgNode_s(expr('At(there)'), False)
        self.na1.children.add(self.ns1)
        self.ns1.parents.add(self.na1)
        self.na2.children.add(self.ns2)
        self.ns2.parents.add(self.na2)
        self.na1.parents.add(self.ns3)
        self.na2.parents.add(self.ns4)

    def test_serialize_mutex(self):
        self.assertTrue(PlanningGraph.serialize_actions(self.pg, self.na1, self.na2),
                        "Two persistence action nodes not marked as mutex")
        self.assertFalse(PlanningGraph.serialize_actions(self.pg, self.na3, self.na4), "Two No-Ops were marked mutex")
        self.assertFalse(PlanningGraph.serialize_actions(self.pg, self.na1, self.na3),
                         "No-op and persistence action incorrectly marked as mutex")

    def test_inconsistent_effects_mutex(self):
        self.assertTrue(PlanningGraph.inconsistent_effects_mutex(self.pg, self.na4, self.na5),
                        "Canceling effects not marked as mutex")
        self.assertFalse(PlanningGraph.inconsistent_effects_mutex(self.pg, self.na1, self.na2),
                         "Non-Canceling effects incorrectly marked as mutex")

    def test_interference_mutex(self):
        self.assertTrue(PlanningGraph.interference_mutex(self.pg, self.na4, self.na5),
                        "Precondition from one node opposite of effect of other node should be mutex")
        self.assertTrue(PlanningGraph.interference_mutex(self.pg, self.na5, self.na4),
                        "Precondition from one node opposite of effect of other node should be mutex")
        self.assertFalse(PlanningGraph.interference_mutex(self.pg, self.na1, self.na2),
                         "Non-interfering incorrectly marked mutex")

    def test_competing_needs_mutex(self):
        self.assertFalse(PlanningGraph.competing_needs_mutex(self.pg, self.na1, self.na2),
                         "Non-competing action nodes incorrectly marked as mutex")
        mutexify(self.ns3, self.ns4)
        self.assertTrue(PlanningGraph.competing_needs_mutex(self.pg, self.na1, self.na2),
                        "Opposite preconditions from two action nodes not marked as mutex")

    def test_negation_mutex(self):
        self.assertTrue(PlanningGraph.negation_mutex(self.pg, self.ns1, self.ns3),
                        "Opposite literal nodes not found to be Negation mutex")
        self.assertFalse(PlanningGraph.negation_mutex(self.pg, self.ns1, self.ns2),
                         "Same literal nodes found to be Negation mutex")

    def test_inconsistent_support_mutex(self):
        self.assertFalse(PlanningGraph.inconsistent_support_mutex(self.pg, self.ns1, self.ns2),
                         "Independent node paths should NOT be inconsistent-support mutex")
        mutexify(self.na1, self.na2)
        self.assertTrue(PlanningGraph.inconsistent_support_mutex(self.pg, self.ns1, self.ns2),
                        "Mutex parent actions should result in inconsistent-support mutex")

        self.na6 = PgNode_a(Action(expr('Go(everywhere)'),
                                   [[], []], [[expr('At(here)'), expr('At(there)')], []]))
        self.na6.children.add(self.ns1)
        self.ns1.parents.add(self.na6)
        self.na6.children.add(self.ns2)
        self.ns2.parents.add(self.na6)
        self.na6.parents.add(self.ns3)
        self.na6.parents.add(self.ns4)
        mutexify(self.na1, self.na6)
        mutexify(self.na2, self.na6)
        self.assertFalse(PlanningGraph.inconsistent_support_mutex(
            self.pg, self.ns1, self.ns2),
            "If one parent action can achieve both states, should NOT be inconsistent-support mutex, even if parent actions are themselves mutex")


class TestPlanningGraphHeuristics(unittest.TestCase):
    def setUp(self):
        self.p = have_cake()
        self.pg = PlanningGraph(self.p, self.p.initial)

    def test_levelsum(self):
        self.assertEqual(self.pg.h_levelsum(), 1)


if __name__ == '__main__':
    unittest.main()
