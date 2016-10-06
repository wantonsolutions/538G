from z3 import *



x = Int('x')
y = Int('y')
solve(x == x/2 + y/2, x>=0, y>=0, y <= x)
#f = Function('f', IntSort(), IntSort())
#solve(f(f(x)) == x, f(x) == y, x != y)

