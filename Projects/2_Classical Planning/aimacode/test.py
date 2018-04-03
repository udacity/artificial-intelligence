
from utils import *

a = expr('Foo(A, B)')
b = ~a
c = ~b

d = expr('Foo(A, B)')

assert d == a
assert ~(~d) == a
# print("a:", a)
# print(a.op, a.args)
# print("b:", b)
# print(b.op, b.args)
# print("c:", c)
# print(c.op, c.args)

# assert ~b == a
# assert c == a

for _ in range(1000000):
    b = ~a