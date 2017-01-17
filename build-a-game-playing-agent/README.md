
# Build a Game-playing Agent

## Synopsis

This project includes skeletons for the classes and functions that you need to implement to develop an adversarial search agent to play the game "Isolation".  We have also included example players and evaluation classes for you to review and test against.

Isolation is a deterministic, two-player game of perfect information in which the players alternate turns moving a single piece from one cell to another on a board.  Whenever either player occupies a cell, that cell becomes blocked for the remainder of the game.  The first player with no remaining legal moves loses, and the opponent is declared the winner.

In this project, we will play a version of Isolation where each agent is restricted to L-shaped movements (like a knight in chess) on a rectangular grid (like a chess or checkerboard).  The agents can move to any open cell on the board that is 2-rows and 1-column or 2-columns and 1-row away from their current position on the board. (Movements are blocked at the edges of the board -- there is no wrap around.)

Additionally, agents will have a fixed time limit each turn to search for the best move and respond.  If the time limit expires during a player's turn, that player forfeits the match, and the opponent wins.

These rules are implemented for you in the `isolation.Board` class provided in the repository. The `Board` class exposes an API including `is_winner()`, `is_loser()`, `get_legal_moves()`, and other methods available for your agent to use.

You may write or modify code within each file (as long as you maintain compatibility with the function signatures provided) and you may add other classes, functions, etc., as you need.


## Implementation

### Adversarial Search

You must first implement the minimax algorithm, then implement alpha-beta pruning for minimax, and finally incorporate iterative deepening.  Detailed descriptions of these topics are presented in the lectures.  You will implement them in the `game_agent.CustomPlayer` class under the `minimax()`, `alphabeta()`, and `get_moves()` methods, respectively.  The class constructor takes arguments that specify whether to call minimax or alphabeta search, and whether to use fixed-depth search or iterative deepening. These will be used, along with a function that you will use to determine how much time remains before the search will time out, in the `get_moves()` method.

The required interface specifications can be found in the docstrings for each function.  Note that you are allowed to modify the interface of the minimax and alphabeta functions, and add new functions/methods/classes to the file.  However, if you modify the input interface of any function, it must remain compatible with the interface provided, so you will need to include suitable default parameters.


### Evaluation Functions

You will need to develop heuristic functions to inform the value judgements your AI will make when choosing moves.  We have provided implementations in sample_players.py of the heuristic functions described in lecture in the `OpenMoveEval` and `ImprovedEval` classes, as well as a `NullEval` class to use in testing.  You are required to experiment with the `custom_score` to come up with at least three distinct heuristic functions that you will compare in your report.  Please note that you are not required to find a _better_ heuristic than those provided -- but you do need to explain why your heuristics are good choices, and compare them to the baseline heuristics we provide, and each other.

We have provided a script called `tournament.py` that you will use to evaluate and compare your heuristic functions by testing your agent & heuristic against agent configuations that we specify in the tournament script.  The script plays your agent against each one of the test agents - which have all been ranked with a calibrated Elo score (a skill rating system used in many games) - to determine the relative strength of your heuristic and search algorithm.  You will need the score returned by this script for each of your evaluation functions to include in your report.

You may also modify the tournament script to compare your heuristic functions directly against one another, but those score will not be calibrated relative to the other known agents, so they aren't required for the report. (It could still prove useful for testing to build an overall stronger agent.)


## Testing

### Test Players

We have also provided `sample_players.py` containing 3 player classes for you to test against locally:

- `RandomPlayer` - randomly selects a move from among the available legal moves
- `GreedyPlayer` - selects the next legal move with the highest heuristic value
- `HumanPlayer`  - allows *YOU* to play against the AI through the terminal

You **DO NOT** need to submit these players (nor should you), however feel free to change these classes as you see fit during development. Just know that any changes you make will be solely for the benefit of your own tests, and will not be available to the project reviewers.

### Unit Tests

The `agent_test.py` script contains unittest test cases to evaluate your implementations.  The test cases evaluate your functions compared to a static set of example game trees to verify that the correct output is returned, and that each algorithm visits an expected number of nodes during search.

### Tournament

The `tournament.py` script will run a round-robin tournament between your CustomPlayer agent with itertive deepening and your custom heuristic function against several calibrated agent configurations using fixed-depth minimax and alpha-beta search with the example heuristics provided in `sample_players.py`.
