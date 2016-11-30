from aimacode.search import InstrumentedProblem
from aimacode.utils import expr
from aimacode.logic import associate
from timeit import default_timer as timer


class SuccessorAxiom():
    def __init__(self, fluent_string, act_cause_list, act_cause_not_list):
        # where the cause lists are disjunction lists of conjunction lists
        self.fluent_string = fluent_string
        self.act_cause_list = act_cause_list
        self.act_cause_not_list = act_cause_not_list

    def __str__(self):
        return("fluent: {}\n   pos: {}\n   neg: {}".format(self.fluent_string, self.act_cause_list, self.act_cause_not_list))


class PreconditionAxiom():
    def __init__(self, action_string, precondition_pos_list, precondition_neg_list):
        self.action_string = action_string
        self.pos_list = precondition_pos_list
        self.neg_list = precondition_neg_list

    def __str__(self):
        return("action: {}\n   pos: {}\n   neg: {}".format(self.action_string, self.pos_list, self.neg_list))


class FluentState():

    def __init__(self, pos_list, neg_list):
        self.pos = pos_list
        self.neg = neg_list

    def sentence(self):
        return expr(conjunctive_sentence(self.pos, self.neg))

    def pos_sentence(self):
        return expr(conjunctive_sentence(self.pos, []))

def conjunctive_sentence(pos_list, neg_list):
    clauses = []
    for f in pos_list:
        clauses.append(expr("{}".format(f)))
    for f in neg_list:
        clauses.append(expr("~{}".format(f)))
    return associate('&', clauses)


def encode_state(fs: FluentState, fluent_map: list) -> str:
    # encode a string that represents a state of ordered fluents as true or false
    state_tf = []
    for fluent in fluent_map:
        if fluent in fs.pos:
            state_tf.append('T')
        else:
            state_tf.append('F')
    return "".join(state_tf)


def decode_state(state: str, fluent_map: list) -> FluentState:
    # assume lengths the same
    fs = FluentState([], [])
    for idx, char in enumerate(state):
        if char == 'T':
            fs.pos.append(fluent_map[idx])
        else:
            fs.neg.append(fluent_map[idx])
    return fs


class LiteralSet():
    def __init__(self, pos_iter, neg_iter):
        self.pos = set(pos_iter)
        self.neg = set(neg_iter)


def show_solution(node, elapsed_time):
    print("Plan length: {}  Time elapsed in seconds: {}".format(len(node.solution()), elapsed_time))
    for action in node.solution():
        print("{}{}".format(action.name, action.args))


def run_search(problem, message, search_function, parameter=None):
    start = timer()
    ip = InstrumentedProblem(problem)
    if parameter is not None:
        node = search_function(ip, parameter)
    else:
        node = search_function(ip)
    end = timer()
    print("\n{} {}".format(message,ip))
    show_solution(node, end - start)