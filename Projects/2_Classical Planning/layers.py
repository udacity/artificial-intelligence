
from copy import deepcopy
from functools import lru_cache
from itertools import combinations
from collections import defaultdict, MutableSet

from aimacode.planning import Action
from aimacode.utils import expr, Expr

    ##############################################################################
    #                 YOU DO NOT NEED TO MODIFY CODE IN THIS FILE                #
    ##############################################################################


@lru_cache()
def make_node(action, no_op=False):
    """ Convert Action objects to planning graph nodes by creating distinct
    symbols for positive and negative fluents and then combining positive & 
    negative preconditions and effects into sets. This allows efficient membership
    testing and perserves logical negation semantics on the symbolic actions.
    """
    preconditions = set(action.precond_pos) | set([~p for p in action.precond_neg])
    effects = set(action.effect_add) | set([~e for e in action.effect_rem])
    return ActionNode(str(action), frozenset(preconditions), frozenset(effects), no_op)


@lru_cache()
def makeNoOp(literal):
    """ Create so-called 'no-op' actions, which only exist in a planning graph
    (they are not real actions in the problem domain) to persist a literal
    from one layer of the planning graph to the next.

    no-op actions are created such that logical negation is correctly evaluated.
    i.e., the no-op action of the negative literal ~At(place) is the logical
    negation of the no-op action of positive literal At(place); in other words
    NoOp::~At(place) == ~(NoOp::At(place) -- NOTE: NoOp::~At(place) is not a valid
    action, but the correct semantics are handled and enforced automatically.
    """
    action = Expr("NoOp::" + literal.op, literal.args)
    return (Action(action, [set([literal]), []], [set([literal]), []]),
            Action(~action, [set([~literal]), []], [set([~literal]), []]))


class ActionNode(object):
    """ Efficient representation of Actions for planning graph

    Attributes
    ----------
    expr : Expr
        An instance of aimacode.utils.Expr (a string-based symbolic expression)

    preconditions : set()
        A set of mixed positive and negative literal aimacode.utils.Expr
        expressions (symbolic representations like X, ~Y, etc.) that are
        preconditions of this action
        
    effects : set()
        A set of mixed positive and negative literal aimacode.utils.Expr
        expressions (symbolic representations like X, ~Y, etc.) that are
        results of applying this action

    no_op : bool
        A boolean flag indicating whether the instance is a no-op action
        (used to serialize planning graphs)
    """
    __slots__ = ['expr', 'preconditions', 'effects', 'no_op', '__hash']
    def __init__(self, symbol, preconditions, effects, no_op):
        self.expr = symbol
        self.preconditions = preconditions
        self.effects = effects
        self.no_op = no_op
        self.__hash = hash(symbol)

    def __hash__(self): return self.__hash
    def __str__(self): return str(self.expr)
    def __repr__(self): return self.__str__()
    def __eq__(self, other):
        return (isinstance(other, ActionNode)
            and self.expr == other.expr)


class BaseLayer(MutableSet):
    """ Base class for ActionLayer and LiteralLayer classes for planning graphs
    that stores actions or literals as a mutable set (which enables terse,
    efficient membership testing and expansion)

    Attributes
    ----------
    parents : dict
        Mapping from each item (action or literal) in the current layer to the
        symbolic node(s) in parent layer of the planning graph. E.g.,
        parents[actionA] is a set containing the symbolic literals (positive AND
        negative) that are preconditions of the action.

    children : dict
        Mapping from each item (action or literal) in the current layer to the
        symbolic node(s) in the child layer of the planning graph. E.g.,
        children[actionA] is a set containing the symbolic literals (positive AND
        negative) that are set by performing actionA.

    parent_layer : BaseLayer (or subclass)
        Contains a reference to the layer preceding this one in the planning graph;
        the root literal layer of a planning graph contains an empty ActionLayer as
        parent. (This ensures that parent_layer.is_mutex() is always defined for
        real layers in the planning graph) Action layers always have a literal layer
        as parent, and literal layers always have an action layer as parent.
    
    _mutexes : dict
        Mapping from each item (action or literal) to a set containing all items
        that are mutex to the key. E.g., _mutexes[literaA] is a set of literals
        that are mutex to literalA in this level of the planning graph

    _ignore_mutexes : bool
        If _ignore_mutexes is True then _dynamic_ mutexes will be ignored (static
        mutexes are *always* enforced). For example, a literal X is always mutex
        with ~X, but "competing needs" or "inconsistent support" can be skipped
    """
    def __init__(self, items=[], parent_layer=None, ignore_mutexes=False):
        """
        Parameters
        ----------
        items : iterable
            Collection of items to store in the layer (literals or actions)

        parent_layer : BaseLayer (or subclass)
            See parent_layer attribute

        ignore_mutexes : bool
            See _ignore_mutexes attribute
        """
        super().__init__()
        self.__store = set(iter(items))
        self.parents = defaultdict(set)
        self.children = defaultdict(set)
        self._mutexes = defaultdict(set)
        self.parent_layer = parent_layer
        self._ignore_mutexes = ignore_mutexes

    def __contains__(self, item):
        return item in self.__store

    def __iter__(self):
        return iter(self.__store)

    def __len__(self):
        return len(self.__store)

    def __eq__(self, other):
        return (len(self) == len(other) and
            len(self._mutexes) == len(other._mutexes) and
            0 == len(self ^ other) and self._mutexes == other._mutexes)

    def add(self, item):
        self.__store.add(item)

    def discard(self, item):
        try:
            self.__store.discard(item)
        except ValueError:
            pass

    def set_mutex(self, itemA, itemB):
        self._mutexes[itemA].add(itemB)
        self._mutexes[itemB].add(itemA)

    def is_mutex(self, itemA, itemB):
        return itemA in self._mutexes.get(itemB, [])


class BaseActionLayer(BaseLayer):
    def __init__(self, actions=[], parent_layer=None, serialize=True, ignore_mutexes=False):
        super().__init__(actions, parent_layer, ignore_mutexes)
        self._serialize=serialize
        if isinstance(actions, BaseActionLayer):
            self.parents.update({k: set(v) for k, v in actions.parents.items()})
            self.children.update({k: set(v) for k, v in actions.children.items()})

    def update_mutexes(self):
        for actionA, actionB in combinations(iter(self), 2):
            if self._serialize and actionA.no_op == actionB.no_op == False:
                self.set_mutex(actionA, actionB)
            elif (self._inconsistent_effects(actionA, actionB)
                    or self._interference(actionA, actionB)):
                self.set_mutex(actionA, actionB)
            elif self._ignore_mutexes:
                continue
            elif self._competing_needs(actionA, actionB):
                self.set_mutex(actionA, actionB)

    def add_inbound_edges(self, action, literals):
        # inbound action edges are many-to-one
        self.parents[action] |= set(literals)

    def add_outbound_edges(self, action, literals):
        # outbound action edges are one-to-many
        self.children[action] |= set(literals)


class BaseLiteralLayer(BaseLayer):
    def __init__(self, literals=[], parent_layer=None, ignore_mutexes=False):
        super().__init__(literals, parent_layer, ignore_mutexes)
        if isinstance(literals, BaseLiteralLayer):
            self.parents.update({k: set(v) for k, v in literals.parents.items()})
            self.children.update({k: set(v) for k, v in literals.children.items()})

    def update_mutexes(self):
        for literalA, literalB in combinations(iter(self), 2):
            if self._negation(literalA, literalB):
                self.set_mutex(literalA, literalB)
            elif self._ignore_mutexes:
                continue
            elif len(self.parent_layer) and self._inconsistent_support(literalA, literalB):
                self.set_mutex(literalA, literalB)

    def add_inbound_edges(self, action, literals):
        # inbound literal edges are many-to-many
        for literal in literals:
            self.parents[literal].add(action)

    def add_outbound_edges(self, action, literals):
        # outbound literal edges are many-to-many
        for literal in literals:
            self.children[literal].add(action)
