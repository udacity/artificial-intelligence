import os
import sys
parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(parent), "aimacode"))
import unittest
from aimacode.utils import expr
from my_pddl import acp1_pddl, acp2_pddl, acp3_pddl

class TestPddlACP1(unittest.TestCase):

    def test_acp1(self):
        p = acp1_pddl()
        self.assertFalse(p.goal_test(),"P1 goal test should fail at start")
        solution = [
            expr("Load(C1 , P1, SFO)"),
            expr("Fly(P1, SFO, JFK)"),
            expr("Unload(C1, P1, JFK)"),
            expr("Load(C2, P2, JFK)"),
            expr("Fly(P2, JFK, SFO)"),
            expr("Unload (C2, P2, SFO)")
            ]
        for action in solution:
            p.act(action)

        self.assertTrue(p.goal_test(), "P1 goal not reached by solution steps")

    def test_acp2(self):
        p = acp2_pddl()
        self.assertFalse(p.goal_test(),"P2 goal test should fail at start")
        solution = [
            # TODO: (optional) Add a valid plan (sequence of actions) to test the problem definition and solution
        ]
        for action in solution:
            p.act(action)

        self.assertTrue(p.goal_test(), "P2 goal not reached by solution steps")


    def test_acp3(self):
        p = acp3_pddl()
        self.assertFalse(p.goal_test(),"P3 goal test should fail at start")
        solution = [
            # TODO: (optional) Add a valid plan (sequence of actions) to test the problem definition and solution
        ]
        for action in solution:
            p.act(action)

        self.assertTrue(p.goal_test(), "P3 goal not reached by solution steps")



if __name__ == '__main__':
    unittest.main()
