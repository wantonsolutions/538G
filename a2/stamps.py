from z3 import *

s0, s1, s2 = Ints('s0, s1, s2')
s0 = 231
s1 = 234
s2 = 238

c0, c1, c2 = Ints('c0, c1, c2')

solve(c0 > 0, c1 > 0, c2 > 0, 5823 == c0 * s0 + c1 * s1 + c2 *s2)
solve(c0 > 0, c1 > 0, c2 > 0, 6700 == c0 * s0 + c1 * s1 + c2 *s2)


solve(c0 > 0, c1 > 0, c2 > 0, 57917 == c0 * s0 + c1 * s1 + c2 *s2)

solve(c1 > 0, c2 > 0, 57917 == c1 * s1 + c2 *s2)
solve(c0 > 0, c2 > 0, 57917 == c0 * s0 + c2 *s2)
solve(c0 > 0, c1 > 0, 57917 == c0 * s0 + c1 *s1)
