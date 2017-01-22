import argparse
from timeit import default_timer as timer
from aimacode.search import InstrumentedProblem
from aimacode.search import (breadth_first_search, astar_search,
    breadth_first_tree_search, depth_first_graph_search, uniform_cost_search,
    greedy_best_first_graph_search, depth_limited_search,
    recursive_best_first_search)
from my_air_cargo_problems import air_cargo_p1, air_cargo_p2, air_cargo_p3

PROBLEM_CHOICE_MSG = """
Select from the following list of air cargo problems. You may choose more than
one by entering multiple selections separated by spaces.
"""

SEARCH_METHOD_CHOICE_MSG = """
Select from the following list of search functions. You may choose more than
one by entering multiple selections separated by spaces.
"""

INVALID_ARG_MSG = """
You must either use the -m flag to run in manual mode, or use both the -p and
-s flags to specify a list of problems and search algorithms to run. Valid
choices for each include:
"""

PROBLEMS = [["Air Cargo Problem 1", air_cargo_p1],
            ["Air Cargo Problem 2", air_cargo_p2],
            ["Air Cargo Problem 3", air_cargo_p3]]
SEARCHES = [["breadth_first_search", breadth_first_search, ""],
            ['breadth_first_tree_search', breadth_first_tree_search, ""],
            ['depth_first_graph_search', depth_first_graph_search, ""],
            ['depth_limited_search', depth_limited_search, ""],
            ['uniform_cost_search', uniform_cost_search, ""],
            ['recursive_best_first_search', recursive_best_first_search, 'h_1'],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_1'],
            ['astar_search', astar_search, 'h_1'],
            ['astar_search', astar_search, 'h_ignore_preconditions'],
            ['astar_search', astar_search, 'h_pg_levelsum'],
            ]


class PrintableProblem(InstrumentedProblem):
    """ InstrumentedProblem keeps track of stats during search, and this
    class modifies the print output of those statistics for air cargo
    problems.
    """

    def __repr__(self):
        return '{:^10d}  {:^10d}  {:^10d}'.format(self.succs, self.goal_tests, self.states)


def run_search(problem, search_function, parameter=None):

    start = timer()
    ip = PrintableProblem(problem)
    if parameter is not None:
        node = search_function(ip, parameter)
    else:
        node = search_function(ip)
    end = timer()
    print("\nExpansions   Goal Tests   New Nodes")
    print("{}\n".format(ip))
    show_solution(node, end - start)
    print()


def manual():

    print(PROBLEM_CHOICE_MSG)
    for idx, (name, _) in enumerate(PROBLEMS):
        print("    {!s}. {}".format(idx+1, name))
    p_choices = input("> ").split()

    print(SEARCH_METHOD_CHOICE_MSG)
    for idx, (name, _, heuristic) in enumerate(SEARCHES):
        print("    {!s}. {} {}".format(idx+1, name, heuristic))
    s_choices = input("> ").split()

    main(p_choices, s_choices)

    print("\nYou can run this selection again automatically from the command " +
          "line\nwith the following command:")
    print("\n  python {} -p {} -s {}\n".format(__file__,
                                               " ".join(p_choices),
                                               " ".join(s_choices)))


def main(p_choices, s_choices):

    problems = [PROBLEMS[i-1] for i in map(int, p_choices)]
    searches = [SEARCHES[i-1] for i in map(int, s_choices)]

    for pname, p in problems:

        for sname, s, h in searches:
            hstring = h if not h else " with {}".format(h)
            print("\nSolving {} using {}{}...".format(pname, sname, hstring))

            _p = p()
            _h = None if not h else getattr(_p, h)
            run_search(_p, s, _h)


def show_solution(node, elapsed_time):
    print("Plan length: {}  Time elapsed in seconds: {}".format(len(node.solution()), elapsed_time))
    for action in node.solution():
        print("{}{}".format(action.name, action.args))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Solve air cargo planning problems " + 
        "using a variety of state space search methods including uninformed, greedy, " +
        "and informed heuristic search.")
    parser.add_argument('-m', '--manual', action="store_true",
                        help="Interactively select the problems and searches to run.")
    parser.add_argument('-p', '--problems', nargs="+", choices=range(1, len(PROBLEMS)+1), type=int, metavar='',
                        help="Specify the indices of the problems to solve as a list of space separated values. Choose from: {!s}".format(list(range(1, len(PROBLEMS)+1))))
    parser.add_argument('-s', '--searches', nargs="+", choices=range(1, len(SEARCHES)+1), type=int, metavar='',
                        help="Specify the indices of the search algorithms to use as a list of space separated values. Choose from: {!s}".format(list(range(1, len(SEARCHES)+1))))
    args = parser.parse_args()

    if args.manual:
        manual()
    elif args.problems and args.searches:
        main(list(sorted(set(args.problems))), list(sorted(set((args.searches)))))
    else:
        print()
        parser.print_help()
        print(INVALID_ARG_MSG)
        print("Problems\n-----------------")
        for idx, (name, _) in enumerate(PROBLEMS):
            print("    {!s}. {}".format(idx+1, name))
        print()
        print("Search Algorithms\n-----------------")
        for idx, (name, _, heuristic) in enumerate(SEARCHES):
            print("    {!s}. {} {}".format(idx+1, name, heuristic))
        print()
        print("Use manual mode for interactive selection:\n\n\tpython run_search.py -m\n")
