"""
Estimate the strength rating of student-agent with iterative deepening and
a custom heuristic evaluation function against fixed-depth minimax and
alpha-beta search agents by running a round-robin tournament for the student
agent. Note that all agents are constructed from the student CustomPlayer
implementation, so any errors present in that class will affect the outcome
here.

The student agent plays a fixed number of "fair" matches against each test
agent. The matches are fair because the board is initialized randomly for both
players, and the players play each match twice -- switching the player order
between games. This helps to correct for imbalances in the game due to both
starting position and initiative.

For example, if the random moves chosen for initialization are (5, 2) and
(1, 3), then the first match will place agentA at (5, 2) as player 1 and
agentB at (1, 3) as player 2 then play to conclusion; the agents swap
initiative in the second match with agentB at (5, 2) as player 1 and agentA at
(1, 3) as player 2.
"""

import itertools
import random
import warnings

from collections import namedtuple

from isolation import Board
from sample_players import RandomPlayer
from sample_players import NullEval
from sample_players import OpenMoveEval
from sample_players import ImprovedEval
from game_agent import CustomPlayer
from game_agent import CustomEval

NUM_MATCHES = 5  # play 5 matches against each opponent
TIME_LIMIT = 150  # number of milliseconds before timeout

TIMEOUT_WARNING = "One or more agents lost a match this round due to " + \
                  "timeout. The get_move() function must return before " + \
                  "time_left() reaches 0 ms. You will need to leave some " + \
                  "time for the function to return, and may need to " + \
                  "increase this margin to avoid timeouts during  " + \
                  "tournament play."

Agent = namedtuple("Agent", ["player", "name"])


def play_match(player1, player2):
    """
    Play a "fair" set of matches between two agents by playing two games
    between the players, forcing each agent to play from randomly selected
    positions. This should control for differences in outcome resulting from
    advantage due to starting position on the board.
    """
    num_wins = {player1: 0, player2: 0}
    num_timeouts = {player1: 0, player2: 0}
    num_invalid_moves = {player1: 0, player2: 0}
    games = [Board(player1, player2), Board(player2, player1)]

    # initialize both games with a random move and response
    for _ in range(2):
        move = random.choice(games[0].get_legal_moves())
        games[0].apply_move(move)
        games[1].apply_move(move)

    # play both games and tally the results
    for game in games:
        winner, _, termination = game.play(time_limit=TIME_LIMIT)

        if player1 == winner:
            num_wins[player1] += 1

            if termination == "timeout":
                num_timeouts[player2] += 1
            else:
                num_invalid_moves[player2] += 1

        elif player2 == winner:

            num_wins[player2] += 1

            if termination == "timeout":
                num_timeouts[player1] += 1
            else:
                num_invalid_moves[player1] += 1

    if sum(num_timeouts.values()) != 0:
        warnings.warn(TIMEOUT_WARNING)

    return num_wins[player1], num_wins[player2]


def play_round(agents, ratings, num_matches):
    """
    Play one round (i.e., a single match between each pair of opponents)
    """

    scores = dict([(a.player, 0) for a in agents])
    expectations = dict([(a.player, 0) for a in agents])

    agent_1 = agents[-1]

    print "\nPlaying Matches:"
    print "----------"

    for idx, agent_2 in enumerate(agents[:-1]):

        wins = {agent_1.player: 0., agent_2.player: 0.}

        names = [agent_1.name, agent_2.name]
        print "  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, *names),

        # Each player takes a turn going first
        for p1, p2 in itertools.permutations((agent_1.player, agent_2.player)):

            for _ in range(num_matches):

                score_1, score_2 = play_match(p1, p2)
                qa = float(10**(ratings[p1] / 400))
                qb = float(10**(ratings[p2] / 400))
                wins[p1] += score_1
                wins[p2] += score_2
                expectations[p1] += 2 * (qa / (qa + qb))
                expectations[p2] += 2 * (qb / (qa + qb))

        scores[agent_1.player] += wins[agent_1.player]
        scores[agent_2.player] += wins[agent_2.player]
        print "\tResult: {} to {}".format(int(wins[agent_1.player]),
                                          int(wins[agent_2.player]))

    # Update the elo scores after all matches
    N = 2 * len(agents) * NUM_MATCHES
    ratings[agent_1.player] += ((400. / N) * (scores[agent_1.player] - expectations[agent_1.player]))

    return ratings


def main():

    EVAL_FUNCS = [("Null", NullEval), ("Open", OpenMoveEval), ("Improved", ImprovedEval)]
    AB_ARGS = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
    MM_ARGS = {"search_depth": 3, "method": 'minimax', "iterative": False}
    CUSTOM_ARGS = {"method": 'alphabeta', 'iterative': True}
    RATINGS = {"MM_Null": 1350, "MM_Open": 1575, "MM_Improved": 1620,
               "AB_Null": 1510, "AB_Open": 1640, "AB_Improved": 1660,
               "Random": 1150, "ID_Improved": 1500, "Student": 1500}

    mm_agents = [Agent(CustomPlayer(eval_fn=fn(), **MM_ARGS), "MM_" + name) for name, fn in EVAL_FUNCS]
    ab_agents = [Agent(CustomPlayer(eval_fn=fn(), **AB_ARGS), "AB_" + name) for name, fn in EVAL_FUNCS]
    random_agents = [Agent(RandomPlayer(), "Random")]
    test_agents = [Agent(CustomPlayer(eval_fn=ImprovedEval(), **CUSTOM_ARGS), "ID_Improved"),
                   Agent(CustomPlayer(eval_fn=CustomEval(), **CUSTOM_ARGS), "Student")]

    for agentUT in test_agents:
        print ""
        print "*************************"
        print "{:^25}".format("Evaluating " + agentUT.name)
        print "*************************"

        agents =  mm_agents + ab_agents + random_agents + [agentUT]
        ratings = play_round(agents, dict([(a.player, RATINGS[a.name]) for a in agents]), NUM_MATCHES)

        ranking = sorted([(a, ratings[a.player]) for a in agents], key=lambda x: x[1])
        print "\n\nResults:"
        print "----------"
        print "{!s:<15}{!s:>10}".format("Name", "Rating")
        print "{!s:<15}{!s:>10}".format("---", "---")
        print "\n".join(["{!s:<15}{:>10.2f}".format(a.name, r) for a, r in ranking])


if __name__ == "__main__":
    main()
