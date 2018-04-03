
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from sympy import *


def constraint(name, expr):
    """Augment the sympy Function class by attaching a symbolic expression
    and making the function evaluatable by patching the .subs() method.

    Parameters
    ----------
    name : str
        A string defining the name of the function

    expr : sympy.Expr
        A symbolic expression that can be evaluated for a particular
        assignment to determine whether the constraint is True, False,
        or undetermined

    Returns
    -------
    sympy.Function or sympy.Expr
        If the expression still has unassigned free variables, then a
        Function is returned with an attached Expr object; otherwise
        the expression is returned unchanged
    """
    if not len(expr.free_symbols):
        return expr
    func = Function(name)(*expr.free_symbols)
    setattr(func, "expr", expr)
    setattr(func, "subs", lambda *a, **b: constraint(name, expr.subs(*a, **b)))
    setattr(func, "_subs", lambda *a, **b: expr.subs(*a, **b))
    return func


def displayBoard(locations, shape):
    """Draw a chessboard with queens placed at each position specified
    by the assignment.

    Parameters
    ----------
    locations : list
        The locations list should contain one element for each queen
        of the chessboard containing a tuple (r, c) indicating the
        row and column coordinates of a queen to draw on the board.

    shape : integer
        The number of cells in each dimension of the board (e.g.,
        shape=3 indicates a 3x3 board)

    Returns
    -------
    matplotlib.figure.Figure
        The handle to the figure containing the board and queens
    """
    r = c = shape
    cmap = mpl.colors.ListedColormap(['#f5ecce', '#614532'])
    img = mpl.image.imread('queen.png').astype(np.float)
    boxprops = {"facecolor": "none", "edgecolor": "none"}

    x, y = np.meshgrid(range(c), range(r))
    plt.matshow(x % 2 ^ y % 2, cmap=cmap)
    plt.axis("off")  # eliminate borders from plot

    fig = plt.gcf()
    fig.set_size_inches([r, c])
    scale = fig.get_dpi() / max(img.shape)
    ax = plt.gca()
    for y, x in set(locations):
        box = mpl.offsetbox.OffsetImage(img, zoom=scale)
        ab = mpl.offsetbox.AnnotationBbox(box, (y, x), bboxprops=boxprops)
        ax.add_artist(ab)

    plt.show()
    return fig
