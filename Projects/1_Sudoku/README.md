# Solve Sudoku with AI

## Synopsis

In this project, students will extend the Sudoku-solving agent developed in the classroom lectures to solve _diagonal_ Sudoku puzzles. A diagonal Sudoku puzzle is identical to traditional Sudoku puzzles with the added constraint that the boxes on the two main diagonals of the board must also contain the digits 1-9 in each cell (just like the rows, columns, and 3x3 blocks).

## Instructions

Follow the instructions in the classroom lesson to install and configure the AIND [Anaconda](https://www.continuum.io/downloads) environment. That environment includes several important packages that are used for the project. 

**YOU ONLY NEED TO WRITE CODE IN `solution.py`.**


## Quickstart Guide

### Activate the aind environment (OS X or Unix/Linux)
    
    `$ source activate aind`

### Activate the aind environment (Windows)

    `> activate aind`

### Run the code & visualization

    `(aind)$ python solution.py`

### Run the local test suite

    `(aind)$ python -m unittest -v`

### Run the remote test suite & submit the project

    `(aind)$ udacity submit`


## Coding

You must complete the required functions in the 'solution.py' file (copy in code from the classroom where indicated, and add or extend with new code as described below). The `test_solution.py` file includes a few unit tests for local testing (See the unittest module for information on getting started.), but the primary mechanism for testing your code is the Udacity Project Assistant command line utility described in the next section.

YOU SHOULD EXPECT TO MODIFY OR WRITE YOUR OWN UNIT TESTS AS PART OF COMPLETING THIS PROJECT. The Project Assistant test suite is not shared with students. Writing your own tests leads to a deeper understanding of the project.

1. Run the following command from inside the project folder in your terminal to verify that your system is properly configured for the project. You should see feedback in the terminal about failed test cases -- which makes sense because you haven't implemented any code yet. You will reuse this command later to execute your **local** test cases.

    `$ python -m unittest -v`

1. Run the following command from inside the project folder in your terminal to verify that the Udacity-PA tool is installed properly. You should see a list of failed test cases -- which is good because you haven't implemented any code yet. You will reuse this command later to execute the **remote** test cases and complete the project.

    `$ udacity submit`

1. Add the two new diagonal units to the `unitlist` at the top of solution.py. Re-run the local tests with `python -m unittest` to confirm your solution. 

1. Copy your code from the classroom for the `eliminate()`, `only_choice()`, `reduce_puzzle()`, and `search()` into the corresponding functions in the `solution.py` file.

1. Implement the `naked_twins()` function, and update `reduce_puzzle()` to call it (along with the other existing strategies). Re-run the local tests with `python -m unittest -v` to confirm your solution.

1. Write your own test cases to further test your code. Re-run the remote tests with `udacity submit` to confirm your solution. If any of the remote test cases fail, use the feedback to write new local test cases that you can use for debugging.


## Submission

To submit your code, run `udacity submit` from a terminal in the top-level directory of this project. You will be prompted for a username and password the first time the script is run. If you login using google or facebook, visit [this link](https://project-assistant.udacity.com/auth_tokens/jwt_login) for alternate login instructions.

The Udacity-PA CLI tool is automatically installed with the AIND conda environment provided in the classroom, but you can also install it manually by running `pip install udacity-pa`. You can submit your code for scoring by running `udacity submit`. The project assistant server has a collection of unit tests that it will execute on your code, and it will provide feedback on any successes or failures. You must pass all test cases in the project assistant to pass the project.

Once your project passes all test cases on the Project Assistant, submit the zip file created by the `udacity submit` command in the classroom to automatically receive credit for the project. NOTE: You will not receive personalized feedback for this project on submissions that pass all test cases, however, all other projects in the term do provide personalized feedback on both passing & failing submissions.


## Troubleshooting

Your classroom mentor may be able to provide some guidance on the project, but the [discussion forums](https://discussions.udacity.com/c/nd889-intro-sudoku) or [slack team](https://ai-nd.slack.com) (especially the #p-sudoku channel) should be your primary support resources. The instructors hold regularly scheduled office hours in the Slack community. (The schedule is posted in the description of the #office-hours channel.)

Contact ai-support@udacity.com if you don't have access to the forums or Slack team.


## Visualization

**Note:** The `pygame` library is required to visualize your solution -- however, the `pygame` module can be troublesome to install and configure. It should be installed by default with the AIND conda environment, but it is not reliable across all operating systems or versions. Please refer to the pygame documentation [here](http://www.pygame.org/download.shtml), or discuss among your peers in the slack group or discussion forum if you need help.

Running `python solution.py` will automatically attempt to visualize your solution, but you mustuse the provided `assign_value` function (defined in `utils.py`) to track the puzzle solution progress for reconstruction during visuzalization.
