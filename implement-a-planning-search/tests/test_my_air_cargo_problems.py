import os
import sys
parent = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(parent), "aimacode"))
from aimacode.planning import Action
from aimacode.utils import expr
from aimacode.search import Node
import unittest
from lp_utils import decode_state
from my_air_cargo_problems import (
    air_cargo_p1, air_cargo_p2, air_cargo_p3,
)

class TestAirCargoProb1(unittest.TestCase):

    def setUp(self):
        self.p1 = air_cargo_p1()

    def test_ACP1_num_fluents(self):
        self.assertEqual(len(self.p1.initial), 12)

    def test_ACP1_num_requirements(self):
        self.assertEqual(len(self.p1.goal),2)


class TestAirCargoProb2(unittest.TestCase):

    def setUp(self):
        self.p2 = air_cargo_p2()

    def test_ACP2_num_fluents(self):
        self.assertEqual(len(self.p2.initial), 27)

    def test_ACP2_num_requirements(self):
        self.assertEqual(len(self.p2.goal),3)


class TestAirCargoProb3(unittest.TestCase):

    def setUp(self):
        self.p3 = air_cargo_p3()

    def test_ACP3_num_fluents(self):
        self.assertEqual(len(self.p3.initial), 32)

    def test_ACP3_num_requirements(self):
        self.assertEqual(len(self.p3.goal),4)


class TestAirCargoMethods(unittest.TestCase):

    def setUp(self):
        self.p1 = air_cargo_p1()
        self.act1 = Action(
            expr('Load(C1, P1, SFO)'),
            [[expr('At(C1, SFO)'), expr('At(P1, SFO)')], []],
            [[expr('In(C1, P1)')], [expr('At(C1, SFO)')]]
        )

    def test_AC_get_actions(self):
        # to see a list of the actions, uncomment below
        # print("\nactions for problem")
        # for action in self.p1.actions_list:
        #     print("{}{}".format(action.name, action.args))
        self.assertEqual(len(self.p1.actions_list), 20)

    def test_AC_actions(self):
        # to see list of possible actions, uncomment below
        # print("\npossible actions:")
        # for action in self.p1.actions(self.p1.initial):
        #     print("{}{}".format(action.name, action.args))
        self.assertEqual(len(self.p1.actions(self.p1.initial)), 4)

    def test_AC_result(self):
        fs = decode_state(self.p1.result(self.p1.initial, self.act1), self.p1.state_map)
        self.assertTrue(expr('In(C1, P1)') in fs.pos)
        self.assertTrue(expr('At(C1, SFO)') in fs.neg)

    def test_h_ignore_preconditions(self):
        n = Node(self.p1.initial)
        self.assertEqual(self.p1.h_ignore_preconditions(n),2)

if __name__ == '__main__':
    unittest.main()
