"""Provides some utilities widely used by other modules"""

import bisect
import collections
import collections.abc
import operator
import os.path
import random
import math

import heapq
from functools import lru_cache
from collections import namedtuple, deque, Counter, defaultdict

# ______________________________________________________________________________
# Functions on Sequences and Iterables


def sequence(iterable):
    "Coerce iterable to sequence, if it is not already one."
    return (iterable if isinstance(iterable, collections.abc.Sequence)
            else tuple(iterable))


def removeall(item, seq):
    """Return a copy of seq (or string) with all occurences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    else:
        return [x for x in seq if x != item]


def unique(seq):  # TODO: replace with set
    """Remove duplicate elements from seq. Assumes hashable elements."""
    return list(set(seq))


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(bool(x) for x in seq)


def product(numbers):
    """Return the product of the numbers, e.g. product([2, 3, 10]) == 60"""
    result = 1
    for x in numbers:
        result *= x
    return result


def first(iterable, default=None):
    "Return the first element of an iterable or the next element of a generator; or default."
    try:
        return iterable[0]
    except IndexError:
        return default
    except TypeError:
        return next(iterable, default)


def is_in(elt, seq):
    """Similar to (elt in seq), but compares with 'is', not '=='."""
    return any(x is elt for x in seq)


# Misc Functions


# TODO: Use functools.lru_cache memoization decorator


def memoize(fn, slot=None):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, store results in a dictionary."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        def memoized_fn(*args):
            if args not in memoized_fn.cache:
                memoized_fn.cache[args] = fn(*args)
            return memoized_fn.cache[args]

        memoized_fn.cache = {}

    return memoized_fn


def name(obj):
    "Try to find some reasonable name for the object."
    return (getattr(obj, 'name', 0) or getattr(obj, '__name__', 0) or
            getattr(getattr(obj, '__class__', 0), '__name__', 0) or
            str(obj))


def isnumber(x):
    "Is x a number?"
    return hasattr(x, '__int__')


def issequence(x):
    "Is x a sequence?"
    return isinstance(x, collections.abc.Sequence)


def print_table(table, header=None, sep='   ', numfmt='%g'):
    """Print a list of lists as a table, so that columns line up nicely.
    header, if specified, will be printed as the first row.
    numfmt is the format for all numbers; you might want e.g. '%6.2f'.
    (If you want different formats in different columns,
    don't use print_table.) sep is the separator between columns."""
    justs = ['rjust' if isnumber(x) else 'ljust' for x in table[0]]

    if header:
        table.insert(0, header)

    table = [[numfmt.format(x) if isnumber(x) else x for x in row]
             for row in table]

    sizes = list(
            map(lambda seq: max(map(len, seq)),
                list(zip(*[map(str, row) for row in table]))))

    for row in table:
        print(sep.join(getattr(
            str(x), j)(size) for (j, size, x) in zip(justs, sizes, row)))


# ______________________________________________________________________________
# Expressions

# See https://docs.python.org/3/reference/expressions.html#operator-precedence
# See https://docs.python.org/3/reference/datamodel.html#special-method-names

class Expr(object):
    """A mathematical expression with an operator and 0 or more arguments.
    op is a str like '+' or 'sin'; args are Expressions.
    Expr('x') or Symbol('x') creates a symbol (a nullary Expr).
    Expr('-', x) creates a unary; Expr('+', x, 1) creates a binary."""
    __slots__ = ["op", "args", "__hash"]
    def __init__(self, op, *args):
        self.op = op
        self.args = args
        self.__hash = hash(self.op) ^ hash(self.args)

    def __eq__(self, other):
        return (isinstance(other, Expr)
                and self.op == other.op
                and self.args == other.args)

    def __hash__(self): return self.__hash

    # custom unary operator overloads to handle 
    def __pos__(self): return self
    def __neg__(self): return self.args[0] if '-' == self.op else Expr("-", self)
    def __invert__(self): return self.args[0] if '~' == self.op else Expr("~", self)

    # Operator overloads
    # def __neg__(self): return Expr('-', self)
    # def __pos__(self): return Expr('+', self)
    # def __invert__(self): return Expr('~', self)
    def __add__(self, rhs): return Expr('+', self, rhs)
    def __sub__(self, rhs): return Expr('-', self, rhs)
    def __mul__(self, rhs): return Expr('*', self, rhs)
    def __pow__(self, rhs): return Expr('**', self, rhs)
    def __mod__(self, rhs): return Expr('%', self, rhs)
    def __and__(self, rhs): return Expr('&', self, rhs)
    def __xor__(self, rhs): return Expr('^', self, rhs)
    def __rshift__(self, rhs): return Expr('>>', self, rhs)
    def __lshift__(self, rhs): return Expr('<<', self, rhs)
    def __truediv__(self, rhs): return Expr('/', self, rhs)
    def __floordiv__(self, rhs): return Expr('//', self, rhs)
    def __matmul__(self, rhs): return Expr('@', self, rhs)

    def __or__(self, rhs):
        """Allow both P | Q, and P |'==>'| Q."""
        if isinstance(rhs, Expression):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    # Reverse operator overloads
    def __radd__(self, lhs): return Expr('+', lhs, self)
    def __rsub__(self, lhs): return Expr('-', lhs, self)
    def __rmul__(self, lhs): return Expr('*', lhs, self)
    def __rdiv__(self, lhs): return Expr('/', lhs, self)
    def __rpow__(self, lhs): return Expr('**', lhs, self)
    def __rmod__(self, lhs): return Expr('%', lhs, self)
    def __rand__(self, lhs): return Expr('&', lhs, self)
    def __rxor__(self, lhs): return Expr('^', lhs, self)
    def __ror__(self, lhs): return Expr('|', lhs, self)
    def __rrshift__(self, lhs): return Expr('>>', lhs, self)
    def __rlshift__(self, lhs): return Expr('<<', lhs, self)
    def __rtruediv__(self, lhs): return Expr('/', lhs, self)
    def __rfloordiv__(self, lhs): return Expr('//', lhs, self)
    def __rmatmul__(self, lhs): return Expr('@', lhs, self)

    def __call__(self, *args):
        "Call: if 'f' is a Symbol, then f(0) == Expr('f', 0)."
        if self.args:
            raise ValueError('can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():       # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:        # -x or -(x + 1)
            return op + args[0]
        else:                       # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'

# An 'Expression' is either an Expr or a Number.
# Symbol is not an explicit type; it is any Expr with 0 args.

Number = (int, float, complex)
Expression = (Expr, Number)


def Symbol(name):
    "A Symbol is just an Expr with no args."
    return Expr(name)


def symbols(names):
    "Return a tuple of Symbols; names is a comma/whitespace delimited str."
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def subexpressions(x):
    "Yield the subexpressions of an Expression (including x itself)."
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)


def arity(expression):
    "The number of sub-expressions in this expression."
    if isinstance(expression, Expr):
        return len(expression.args)
    else:  # expression is a number
        return 0

# For operators that are not defined in Python, we allow new InfixOps:


class PartialExpr:
    """Given 'P |'==>'| Q, first form PartialExpr('==>', P), then combine with Q."""
    def __init__(self, op, lhs): self.op, self.lhs = op, lhs
    def __or__(self, rhs):       return Expr(self.op, self.lhs, rhs)
    def __repr__(self):          return "PartialExpr('{}', {})".format(self.op, self.lhs)


@lru_cache()
def expr(x):
    """Shortcut to create an Expression. x is a str in which:
    - identifiers are automatically defined as Symbols.
    - ==> is treated as an infix |'==>'|, as are <== and <=>.
    If x is already an Expression, it is returned unchanged. Example:
    >>> expr('P & Q ==> Q')
    ((P & Q) ==> Q)
    """
    if isinstance(x, str):
        return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol))
    else:
        return x

infix_ops = '==> <== <=>'.split()


def expr_handle_infix_ops(x):
    """Given a str, return a new str with ==> replaced by |'==>'|, etc.
    >>> expr_handle_infix_ops('P ==> Q')
    "P |'==>'| Q"
    """
    for op in infix_ops:
        x = x.replace(op, '|' + repr(op) + '|')
    return x


class defaultkeydict(collections.defaultdict):
    """Like defaultdict, but the default_factory is a function of the key.
    >>> d = defaultkeydict(len); d['four']
    4
    """
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


# ______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue


class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(order, f): Queue in sorted order (default min-first).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
        item in q       -- does q contain item?
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self):
        raise NotImplementedError

    def extend(self, items):
        for item in items:
            self.append(item)


def Stack():
    """Return an empty list, suitable as a Last-In-First-Out Queue."""
    return []


class FIFOQueue(Queue):
    """A First-In-First-Out Queue implemented with collections.deque
    
    MODIFIED FROM AIMA VERSION
        - Use deque
        - Use an additional dict to track membership
    """
    def __init__(self):
        self.A = deque()
        self.__keys = set()

    def append(self, item):
        self.A.append(item)
        self.__keys.add(item)

    def __len__(self):
        return len(self.A)

    def pop(self):
        key = self.A.popleft()
        self.__keys.discard(key)
        return key

    def __contains__(self, item):
        return item in self.__keys


class PriorityQueue(Queue):
    """A queue in which the minimum element (as determined by f and
    order) is returned first.  Also supports dict-like lookup.

    MODIFIED FROM AIMA VERSION
        - Use heapq
        - Use an additional dict to track membership
    """

    def __init__(self, order=None, f=lambda x: x):
        self.A = []
        self._A = Counter()
        self.f = f

    def append(self, item):
        heapq.heappush(self.A, (self.f(item), item))
        self._A[item] += 1

    def __len__(self):
        return len(self.A)

    def pop(self):
        _, item = heapq.heappop(self.A)
        self._A[item] -= 1
        return item

    def __contains__(self, item):
        return self._A[item] > 0

    def __getitem__(self, key):
        if self._A[key] > 0:
            return key

# ______________________________________________________________________________
# Useful Shorthands


class Bool(int):
    """Just like `bool`, except values display as 'T' and 'F' instead of 'True' and 'False'"""
    __str__ = __repr__ = lambda self: 'T' if self else 'F'

T = Bool(True)
F = Bool(False)
