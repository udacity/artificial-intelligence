# Solve Sudoku with AI

## Synopsis

In this project, you will extend the Sudoku-solving agent developed in the classroom lectures to solve _diagonal_ Sudoku puzzles and implement a new constraint strategy called "naked twins". A diagonal Sudoku puzzle is identical to traditional Sudoku puzzles with the added constraint that the boxes on the two main diagonals of the board must also contain the digits 1-9 in each cell (just like the rows, columns, and 3x3 blocks). The naked twins strategy says that if you have two or more unallocated boxes in a unit and there are only two digits that can go in those two boxes, then those two digits can be eliminated from the possible assignments of all other boxes in the same unit.


## Quickstart Guide

**YOU ONLY NEED TO WRITE CODE IN `solution.py`.**

1. Follow the instructions in the classroom lesson to install and configure the `aind` [Anaconda](https://www.continuum.io/downloads) environment which includes several important packages that are used for the project. OS X or Unix/Linux users can activate the aind environment by running the following (Windows users simply run `activate aind`):
    
    `$ source activate aind`

2. You can run a small set of test cases using the local test suite. 

    `(aind)$ python -m unittest -v`

3. Copy your code from the classroom for the search and basic strategies, then add the diagonal units at the top of the solutions.py file and complete the `naked_twins()` function.  Pseudocode for the `naked_twins()` function is available [here](https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md).

4. Run the test suite again to check your progress. Once you pass all the test cases in the local test suite, you can submit the project to run more comprehensive tests with the remote test suite:

    `(aind)$ udacity submit`

5. You can run the code with visualization (see the last section of the readme for more information)

    `(aind)$ python solution.py`


### Notes

- You will not receive credit for the project until you submit the zip file created by `udacity submit` in your classroom.

- You must submit _exactly_ the zip file created by the CLI in step 3 to the classroom; if you make any changes to the file, you'll receive an error message when you attempt to submit in the classroom.


## Instructions

You must complete the required functions in the 'solution.py' file (copy in code from the classroom where indicated, and add or extend with new code as described below). The `test_solution.py` file includes a few unit tests for local testing, but the primary mechanism for testing your code is the Udacity Project Assistant command line utility described in the next section.

YOU SHOULD EXPECT TO MODIFY OR WRITE YOUR OWN UNIT TESTS AS PART OF COMPLETING THIS PROJECT. There is no requirement to write test cases, but the Project Assistant test suite is not shared with students so writing your own tests may be necessary to find and resolve any errors that arise there.

1. Add the two new diagonal units to the `unitlist` at the top of solution.py. Re-run the local tests with `python -m unittest` to confirm your solution. 

1. Copy your code from the classroom for the `eliminate()`, `only_choice()`, `reduce_puzzle()`, and `search()` into the corresponding functions in the `solution.py` file.

1. Implement the `naked_twins()` function (see the pseudocode [here](https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md) for help), and update `reduce_puzzle()` to call it (along with the other existing strategies). Re-run the local tests with `python -m unittest -v` to confirm your solution.

1. Run the remote tests with `udacity submit` to confirm your solution. If any of the remote test cases fail, use the feedback to write your own local test cases for debugging.


## Submission

To submit your code, run `udacity submit` from a terminal in the top-level directory of this project. You will be prompted for a username and password the first time the script is run. If you login using google or facebook, visit [this link](https://project-assistant.udacity.com/auth_tokens/jwt_login) for alternate login instructions.

The Udacity-PA CLI tool is automatically installed with the AIND conda environment provided in the classroom, but you can also install it manually by running `pip install udacity-pa`. You can submit your code for scoring by running `udacity submit`. The project assistant server has a collection of unit tests that it will execute on your code, and it will provide feedback on any successes or failures. You must pass all test cases in the project assistant to pass the project.

Once your project passes all test cases on the Project Assistant, submit the zip file created by the `udacity submit` command in the classroom to automatically receive credit for the project. NOTE: You will not receive personalized feedback for this project on submissions that pass all test cases, however, all other projects in the term do provide personalized feedback on both passing & failing submissions.


## Visualization

**Note:** The `pygame` library is required to visualize your solution -- however, the `pygame` module can be troublesome to install and configure. It should be installed by default with the AIND conda environment, but it is not reliable across all operating systems or versions. Please refer to the pygame documentation [here](http://www.pygame.org/download.shtml), or discuss among your peers in the slack group if you need help.

Running `python solution.py` will automatically attempt to visualize your solution, but you mustuse the provided `assign_value` function (defined in `utils.py`) to track the puzzle solution progress for reconstruction during visuzalization.
