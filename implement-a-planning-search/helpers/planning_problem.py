from aimacode.planning import Action
from aimacode.search import Problem
from helpers.lp_utils import (
        FluentState, encode_state
        )


class PlanningProblem(Problem):
    """
    NOTE: DO NOT MODIFY THIS CLASS DIRECTLY
    Subclassing from the aimacode-python.search abstract class for a formal problem.
    You should subclass this version for each of the planning problems provided
    and implement the methods get_actions, actions and result, and possibly
    __init__, goal_test, and path_cost. Then you can create instances
    of your subclass and solve the planning problems with various search functions.

    """

    def __init__(self, initial: FluentState, goal: list):
        """

        Args:
            initial: positive and negative literal fluents describing initial state
            goal: fluents required for goal test

        The constructor specifies the initial state as a set of fully defined fluents,
        a goal as a list of required fluents. Instance variables also include a list
        of possible actions for this problem in concrete form.
        Hint:  it is useful to convert the fluents to a more succinct state representation;
        one method is provided here
        """
        self.state_map = initial.pos + initial.neg
        Problem.__init__(self, encode_state(initial, self.state_map), goal=goal)
        self.actions_list = self.get_actions()

    def get_actions(self)->list:
        """

        Returns: list of all possible Action objects
        see aimacode-python.planning for class definition and examples

        """
        raise NotImplementedError

    def actions(self, state: str)->list:
        """ Return the actions that can be executed in the given state.

        Args:
            state:

        Returns: list of Action objects

        """
        raise NotImplementedError

    def result(self, state: str, action: Action)->str:
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        Args:
            state: state entering node
            action: Action applied

        Returns: resulting state after action

        """
        raise NotImplementedError

    def goal_test(self, state: str) -> bool:
        """Return True if the state is a goal."""
        raise NotImplementedError

