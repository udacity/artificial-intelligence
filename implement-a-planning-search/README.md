
# Implement a Planning Search

## Synopsis

This project includes skeletons for the Python classes and functions that you need to implement to develop a planner for an Air Cargo Transport system.  In addition to the starter code provided, you will interface with [companion code](https://github.com/aimacode) associated with the Stuart Russel and Peter Norvig text, "Artificial Intelligence: A Modern Approach".  A copy of the code has been provided within this project codebase.

In the lectures, you have learned about various search techniques, as well as logic and classical planning representations.  Now it is time to put it all together in a deterministic problem.  Planning can be accomplished by searching over a set of nodes and edges, where the nodes are "states" and the edges are "actions".  The resulting plan is then the series of edges (actions) that were picked in the search to the goal state.  The difficulty is in accomplishing this task optimally and efficiently.  In this project, you will define a group of problems in classical PDDL (Planning Domain Definition Language) for the Air Cargo domain discussed in the lectures.  

You will then proceed to set up the problems for search, and experiment with various automatically generated heuristics, including Planning Graph heuristics, to solve the problems.  These heuristics are discussed in detail in the Russell-Norvig book, especially chapter 10.  If the current 3rd edition version is not available to you, the information needed for this project can be found in the previous 2nd edition Chapter 11 on Planning, available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf)

You may write or modify code within each file as long as you maintain compatibility with the function signatures provided, and you may add other classes, functions, etc., as needed.

Finally, you will provide an analysis of the results as a report.  Additionally, you will provide a report on significant research in the field of Planning.

Upon completion, submit the following in a zipped file:

* `my_pddl.py`
* `my_air_cargo_problems.py`
* `my_planning_graph.py`
*  analysis report in pdf format
*  research report in pdf format

## Environment requirements
This project requires Python 3.4 or higher. Python annotations for functions are included to aid you if you are making use of an integrated development environment (IDE), for example, that can interpret them.  


## Implementation
### The Domain

The Air Cargo Transport system consists of airplanes, cargo items, and airports.  Each problem will have a different combination of ground fluents defining the initial state and goal test for the planner.  Planes and cargo may be "at" an airport and cargo may be "in" a plane.  If it is "in" a plane, it is no longer considered "at" an airport.  Here are some examples of admissible literal fluents where `P1` is a plane, `C1` is a cargo item, `SFO` is San Francisco airport, and `JFK` is Kennedy airport in New York:

*  *At(P1, SFO)*
*  *At(C1, JFK)*
*  *In(C1, P1)*

Permissible actions in this domain are `Load`, `Unload`, and `Fly`.  Concrete examples of actions include:

*  *Load(C1, P1, SFO)*
*  *Unload(C1, P1, SFO)*
*  *Fly(P1, SFO, JFK)*

### The Planning Problems
#### Problem 1

```
2 cargo items: {C1, C2}
2 airplanes: {P1, P2}
2 airports: {SFO, JFK}
initial: C1 and P1 are at SFO, P2 and C2 are at JFK
goal: C1 at JFK, C2 at SFO
```

#### Problem 2

```
3 cargo items: {C1, C2, C3}
3 airplanes: {P1, P2, P3}
3 airports: {SFO, JFK, ATL}
initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 and P3 are at ATL 
goal: C1 at JFK, C2 at SFO, C3 at SFO
```

#### Problem 3

```
4 cargo items: {C1, C2, C3, C4}
2 airplanes: {P1, P2}
4 airports: {SFO, JFK, ATL, ORD}
initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 at ATL, C4 at ORD
goal: C1, C3 at JFK, C2, C4 at SFO
```

### Part 1: PDDL Representations - `my_pddl.py`
For each of the problems above, write out the PDDL planning language representation for the problem. Code the problems above as definitions in `my_pddl.py` using the `PDLL` class (note spelling) provided in `aimacode.planning` module.  There are examples in that module to help you get started.  Once coded, you will be able to use these representations to test your plans for accuracy (though not optimality) in Parts 2 and 3.  Some tests for Problem 1 are provided for you as an example.  

###### Student tasks:
* Implement the PDDL definitions for each problem in the `my_pddl.py` module
   * `acp1_pddl()`
   * `acp2_pddl()`
   * `acp3_pddl()`
* Test `acp1_pddl()` with the  `test_acp1()` method in the `test_my_pddl` module. Note that the other two functions can be similarly tested once a valid planning solution is determined in the next section.
   * To run the tests, execute from the terminal command line:  `python -m unittest tests.test_my_pddl`
* Submit the completed module `my_pddl.py`

### Part 2: Uninformed search for Planning - `my_air_cargo_problems.py`
In order to take advantage of the various search search algorithms already provided in the `aimacode.search` module, subclass the `PlanningProblem` class provided in `helpers.planning_problem` as a generic `AirCargoProblem` for the domain.  This has been started for you in `my_air_cargo_problems.py`.  You will complete the domain methods.  Next, create `AirCargoProblem` instances for Problem 1, Problem 2, and Problem 3 by defining the instance variables, inital state, and goal test.  Once the problem instances are defined, they can be run with the planning searches.  A definition for the Problem 1 instance has been provided for you (`air_cargo_p1`) as an example.  Follow this pattern to implement Problem 2 and Problem 3 instances.  

Note that for the planning problem searches to work correctly, states will have to be defined, which means that all fluents must be ground, functionless atoms. Some helper classes are provided for encoding and decoding the states so they will work properly with the `aimacode.search` module code.  An example of a defined problem with several planning searches is provided for the "Have Cake and Eat it" problem in `example_have_cake.py`.

###### Student tasks:
* Implement the `AirCargoProblem` and class methods in `my_air_cargo_problems.py` (used for all problems)
   * `get_actions()` and sub-methods `load_actions()`, `unload_actions()`, `fly_actions()`
   * `actions()`
   * `result()`
* Implement the problem instance definitions for Problem 2 and Problem 3 in `my_air_cargo_problems.py` (Problem 1 is implemented as an example)
   * `air_cargo_p2()`
   * `air_cargo_p3()`
* During implementation of the methods and instance definitions, make use of the unit tests provided to check your work.  They can be executed from the command line with `python -m unittest tests.test_my_air_cargo_problems`
* Run uninformed planning searches for `air_cargo_p1` and `air_cargo_p2` and provide metrics on number of node expansions required, number of goal tests, time elapsed, and optimality of solution for each search algorithm. Include the result of at least three of these searches for Problem 1 and Problem 2, including breadth-first and depth-first, in your write-up. 
* Take a step back and implement unit tests for the solutions you just found against the `acp2_pddl` and `acp3_pddl` definitions created previously by implementing `test_my_pddl.py` methods:
   * `test_acp2()`
   * `test_acp3()`
   * To run the PDDL solution tests, execute from the terminal command line `python -m unittest tests.test_my_pddl`   
* Note that it is not required to run the uninformed searches for Problem 3 for submission as it may take a very long time, (but feel free to do so!).
* Submit the completed module `my_air_cargo_problems.py` module.

### Part 3: Heuristics and informed search for Planning - `my_planning_graph.py`
As problems become more complex, searching for an optimal solution becomes more difficult.  As seen in the lectures, the most optimal and efficient search, generally, is one that can leverage heuristics as optimistic estimates of the remaining distance from a state node to the planning goal.  In the lectures, this was demonstrated with plans for finding the best route on the Romanian map, using a "distance as the crow flies" heuristic from each town to the goal.  What heuristics can we use for the Air Cargo problem to find an optimal plan?  How do we come up with an optimistic estimate of the distance to the goal state for a plan where the edges are actions rather than roads? Various domain independent automated heuristics are discussed in the text in chapter 10 (3rd Ed) and chapter 11 (2nd Ed). You will implement three of these:
   1. *ignore-preconditions* heuristic described in Russell-Norvig 3rd Ed 10.2.3 or 2nd Ed 11.2
      * for our purposes, assume subgoal independence, in which case this heuristic is exactly the number of unsatisfied goals
   2. *level-sum* heuristic derived from a Planning Graph described in 10.3 or 2nd Ed 11.4
      * for our purposes, assume that the graph is a *serial planning graph*, where only one action can occur per step.  This assumption has already been implemented for you
      * this heuristic follows the subgoal independence assumption and is the sum of the level costs of the goals
   3. *set-level* heuristic derived from a Planning Graph described in 10.3 or 2nd Ed 11.4
      * this heuristic does NOT assume goal independence. It is the level at which all the literals in the goal appear in the planning graph without  mutual exclusion.

In all cases, the heuristics you employ should be calculated automatically based on the problem.  The signatures for methods to facilitate this are provided in the `AirCargoProblem` and `PlanningGraph` classes.

The planning graph is somewhat complex, but is useful in planning because it is a polynomial-size approximation of the exponential tree that represents all possible paths. The planning graph can be used to provide automated admissible heuristics for any domain.  It can also be used as the first step in implementing GRAPHPLAN, a direct planning algorithm that you may wish to learn more about on your own (but we will not address it here).

After implementation of the heuristics, run the heuristic-based A* search algorithms for all three problems.  Depending upon your implementation of the planning graph and the heuristics, the time required may vary.  Run your methods with the "Have Cake" example and Problem 1 first to test them.  None of the heuristics should take more than a few seconds to run for either of these problems.  Problem 2 will take a bit longer, but no heuristic should take longer than 30 minutes to run for Problem 2. Depending on your machine and implementation, Problem 3 may take 1-5 hours to run the longest-running heuristic.  You should save the data from your runs to include in a comparison for the written analysis.  

###### Student tasks:
* Implement the *ignore-preconditions* heuristic in the `AirCargoProblem` in `my_air_cargo_problems.py`
   * `h_ignore_preconditions()`
* Implement the `PlanningGraph` class and its class methods in `my_planning_graph.py` (used for all problems).  There are a number of terms in the planning graph discussion in the text that you may wish to become familiar with.  One such is "mutex".  Two sibling nodes in a planning graph are "mutex" if they are mutually exclusive of each other.  You will implement several "mutex" tests between nodes.
   * Building the Planning Graph:
      * `add_action_level()`
      * `add_literal_level()`
   * Testing for Mutex:
      * `inconsistent_effects_mutex()`
      * `interference_mutex()`
      * `competing_needs_mutex()`
      * `negation_mutex()`
      * `inconsistent_support_mutex()`
   * Heuristics:
      * `h_pg_levelsum()`
      * `h_pg_setlevel()`
* Test the implemented methods in `PlanningGraph` by running the unit tests provided in `test_my_planning_graph.py`.  From the command line enter `python -m unittests tests.test_my_planning_graph`
* Run A* planning searches using the three automated heuristics described above on each of the three problems.  Collect metrics on number of node expansions required, number of goal tests, time elapsed, and optimality of solution for each search algorithm for use in the written analysis.  
* Test the Problem 3 solutions against the `acp3_pddl` definition created previously.
* Submit the completed `my_planning_graph.py` module.


### Part 4: Written Analysis
As you test your planning searches with and without heuristics, collect data on the optimality and efficiency of the various solutions.  The `run_search()` helper function provided in run_search.py should be used to gather this information.  
Compare and contrast the various planning algorithms used for the three problems, and respond to the following prompts in your written analysis.  Provide tables or other visual aids as needed for clarity in your discussion.
   1.  Provide an optimal plan for Problems 1, 2, and 3.
   2.  Compare and contrast uninformed search result metrics for Problem 1 and Problem 2. Include breadth-first, depth-first, and at least one other uninformed non-heuristic search in your comparison.
   3.  Provide a brief explanation of the automatic heuristics you implemented; discuss the advantages and disadvantages of each.
   4.  Compare and contrast informed search result metrics for Problems 1, 2, and 3
   5.  What was the best heuristic used in these problems?  Was it better than uninformed search planning methods for all problems?  Why or why not?


## Tips and Hints
*   Read the Russell-Norvig book, especially chapter 10.  If the current 3rd edition version is not available to you, the information needed for this project can be found in the previous 2nd edition Chapter 11 on Planning, available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf)
*   The Object Oriented Programming (OOP) principle of Inheritance is used in a number of places in both the aimacode library and the starter code presented.  Students unfamiliar with this may need further outside review.  Note in particular, that the `AirCargoProblem` is inherited from the `PlanningProblem` class provided in the `helpers.planning_problem` module, and that it, in turn, is inherited from the abstract `Problem` class in the `aimacode.search` module.  This may seem a bit convoluted, but makes it easy to run the many `search` algorithms that take the `Problem` class object as an argument.
    * Look closely at the `PlanningProblem` instance variables `state_map` and `actions_list` that are inherited by `AirCargoProblem`.
*   Study the `aimacode` classes used for this project.  especially the relevant classes and definitions included in the `search`, `logic`, and `planning` modules.
*   It may be helpful to look at the the `aimacode.tests` package to understand some of the code, and especially `aimacode.tests.test_planning` to get started for Part 1.
*   Since the "Have a cake" example problem is provided for you in `example_have_cake.py`, this is a good way to test your implementation of Planning Graph; note that the Planning Graph for "Have a cake" is described in detail in the book in section 10.3 or the 3rd edition, and section 11.4 of the 2nd edition.
*   Although you cannot share code with classmates, feel free to create your own Air Cargo practice problems and share the plan results with classmates for testing purposes.
*   Before submitting your project to the review team, be sure that it passes all the tests provided!
*   Before submitting your project to the review team, be sure you are addressing all the rubric items!

