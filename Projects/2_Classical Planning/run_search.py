
import argparse

from aimacode.search import (breadth_first_search, astar_search,
    breadth_first_tree_search, depth_first_graph_search, uniform_cost_search,
    greedy_best_first_graph_search, depth_limited_search,
    recursive_best_first_search)
from air_cargo_problems import air_cargo_p1, air_cargo_p2, air_cargo_p3, air_cargo_p4

from _utils import run_search

    ##############################################################################
    #                 YOU DO NOT NEED TO MODIFY CODE IN THIS FILE                #
    ##############################################################################


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
            ["Air Cargo Problem 3", air_cargo_p3],
            ["Air Cargo Problem 4", air_cargo_p4]]
SEARCHES = [["breadth_first_search", breadth_first_search, ""],
            ['depth_first_graph_search', depth_first_graph_search, ""],
            ['uniform_cost_search', uniform_cost_search, ""],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_unmet_goals'],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_pg_levelsum'],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_pg_maxlevel'],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_pg_setlevel'],
            ['astar_search', astar_search, 'h_unmet_goals'],
            ['astar_search', astar_search, 'h_pg_levelsum'],
            ['astar_search', astar_search, 'h_pg_maxlevel'],
            ['astar_search', astar_search, 'h_pg_setlevel']
            ]


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
    print("\n  python {} -p {} -s {}\n".format(
        __file__, " ".join(p_choices), " ".join(s_choices)))


def main(p_choices, s_choices):
    problems = [PROBLEMS[i-1] for i in map(int, p_choices)]
    searches = [SEARCHES[i-1] for i in map(int, s_choices)]

    for pname, problem_fn in problems:
        for sname, search_fn, heuristic in searches:
            hstring = heuristic if not heuristic else " with {}".format(heuristic)
            print("\nSolving {} using {}{}...".format(pname, sname, hstring))

            problem_instance = problem_fn()
            heuristic_fn = None if not heuristic else getattr(problem_instance, heuristic)
            run_search(problem_instance, search_fn, heuristic_fn)


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
