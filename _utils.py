
from itertools import product
from timeit import default_timer as timer

from aimacode.logic import associate
from aimacode.search import InstrumentedProblem
from aimacode.utils import expr


class PrintableProblem(InstrumentedProblem):
    """ InstrumentedProblem keeps track of stats during search, and this class
    modifies the print output of those statistics for air cargo problems.
    """
    def __repr__(self):
        return '{:^10d}  {:^10d}  {:^10d}  {:^10d}'.format(
            len(self.problem.actions_list), self.succs, self.goal_tests, self.states)


def run_search(problem, search_function, parameter=None):
    ip = PrintableProblem(problem)
    start = timer()
    if parameter is not None:
        node = search_function(ip, parameter)
    else:
        node = search_function(ip)
    end = timer()
    print("\n# Actions   Expansions   Goal Tests   New Nodes")
    print("{}\n".format(ip))
    show_solution(node, end - start)
    print()


def show_solution(node, elapsed_time):
    print("Plan length: {}  Time elapsed in seconds: {}".format(len(node.solution()), elapsed_time))
    for action in node.solution():
        print("{}{}".format(action.name, action.args))


def create_expressions(str_list):
    """ Converts a list of strings into a list of Expr objects """
    return [expr(s) for s in str_list]


def make_relations(name, *args, key=lambda x: True):
    """ Map the arguments to expressions. the first positional arg is used as the expression name
    and all remaining expressions are used as arguments.

    Expressions are made over the cartesian product of the positional arguments after the name.
    The expressions can be filtered by supplying a function `key` that takes a length k tuple
    and returns a boolean False for the elements that should be excluded, where k is the number
    of positional arguments after "name".

    Example
    -------
    
    >>> make_relations("At", ["Cargo1", "PlaneA"], ["Airport1"])

        [expr(At(Cargo1, Airport1)), expr(At(PlaneA, Airport1))]

    To filter out the expressions for Airport1, use:

    >>> make_relations("At", ["Cargo1", "PlaneA"], ["Airport1", "Airport2"], key=lambda x: x[-1].endswith("2"))

        [expr(At(Cargo1, Airport2)), expr(At(PlaneA, Airport2))]

    See additional examples in example_have_cake.py and air_cargo_problems.py 
    """
    return create_expressions("{}({})".format(name, ", ".join(c)) for c in product(*args) if key(c))


class FluentState:
    """ Represent planning problem states as positive and negative fluents """
    def __init__(self, pos_list, neg_list):
        self.pos = list(pos_list)
        self.neg = list(neg_list)

    def sentence(self):
        return expr(conjunctive_sentence(self.pos, self.neg))

    def pos_sentence(self):
        return expr(conjunctive_sentence(self.pos, []))


def conjunctive_sentence(pos_list, neg_list):
    """ Express a state as a conjunctive sentence from positive and negative fluent lists

    Parameters
    ----------
    pos_list:
        an iterable collection of strings or Expr representing fluent literals that
        are True in the current state

    neg_list:
        an iterable collection of strings or Expr representing fluent literals that
        are False in the current state

    Returns
    -------
    A conjunctive sentence (i.e., a sequence of clauses connected by logical AND)
    e.g. "At(C1, SFO) ∧ ~At(P1, SFO)"
    """
    clauses = []
    for f in pos_list:
        clauses.append(expr("{}".format(f)))
    for f in neg_list:
        clauses.append(expr("~{}".format(f)))
    return associate('&', clauses)


def encode_state(fs, fluent_map):
    """ Convert a FluentState (list of positive fluents and negative fluents) into
    an ordered sequence of True/False values.

    It is sometimes convenient to encode a problem in terms of the specific
    fluents that are True or False in a state, but other times it is easier (or faster)
    to perform computations on an an array of booleans.

    Parameters
    ----------
    fs: FluentState
        A state object represented as a FluentState

    fluent_map:
        An ordered sequence of fluents
    
    Returns
    -------
    tuple of True/False elements corresponding to the fluents in fluent_map
    """
    return tuple([f in fs.pos for f in fluent_map])


def decode_state(state, fluent_map):
    """ Convert an ordered list of True/False values into a FluentState
    (list of positive fluents and negative fluents)

    It is sometimes convenient to encode a problem in terms of the specific
    fluents that are True or False in a state, but other times it is easier (or faster)
    to perform computations on an an array of booleans.

    Parameters
    ----------
    state:
        A state represented as an ordered sequence of True/False values

    fluent_map:
        An ordered sequence of fluents

    Returns
    -------
    FluentState instance containing the fluents from fluent_map corresponding to True
    entries from the input state in the pos_list, and containing the fluents from
    fluent_map corresponding to False entries in the neg_list
    """
    fs = FluentState(set(), set())
    for idx, elem in enumerate(state):
        if elem:
            fs.pos.append(fluent_map[idx])
        else:
            fs.neg.append(fluent_map[idx])
    return fs
