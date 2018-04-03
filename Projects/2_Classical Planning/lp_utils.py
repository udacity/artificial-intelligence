from aimacode.logic import associate
from aimacode.utils import expr


class FluentState:
    """ state object for planning problems as positive and negative fluents

    """

    def __init__(self, pos_list, neg_list):
        self.pos = set(pos_list)
        self.neg = set(neg_list)

    def sentence(self):
        return expr(conjunctive_sentence(self.pos, self.neg))

    def pos_sentence(self):
        return expr(conjunctive_sentence(self.pos, []))


def conjunctive_sentence(pos_list, neg_list):
    """ returns expr conjuntive sentence given positive and negative fluent lists

    :param pos_list: list of fluents
    :param neg_list: list of fluents
    :return: expr sentence of fluent conjunction
        e.g. "At(C1, SFO) ∧ ~At(P1, SFO)"
    """
    clauses = []
    for f in pos_list:
        clauses.append(expr("{}".format(f)))
    for f in neg_list:
        clauses.append(expr("~{}".format(f)))
    return associate('&', clauses)


def encode_state(fs: FluentState, fluent_map: list) -> str:
    """ encode fluents to a string of T/F using mapping

    :param fs: FluentState object
    :param fluent_map: ordered list of possible fluents for the problem
    :return: str eg. "TFFTFT" string of mapped positive and negative fluents
    """
    return tuple([f in fs.pos for f in fluent_map])


def decode_state(state: str, fluent_map: list) -> FluentState:
    """ decode string of T/F as fluent per mapping

    :param state: str eg. "TFFTFT" string of mapped positive and negative fluents
    :param fluent_map: ordered list of possible fluents for the problem
    :return: fs: FluentState object

    lengths of state string and fluent_map list must be the same
    """
    # a, b = itertools.tee((state[i] == 'T', fluent_map[i]) for i in range(len(state)))
    # return FluentState([item for pred, item in a if pred], [item for pred, item in b if not pred])
    fs = FluentState(set(), set())
    for idx, char in enumerate(state):
        if char:
            fs.pos.add(fluent_map[idx])
        else:
            fs.neg.add(fluent_map[idx])
    return fs
