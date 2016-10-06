from z3 import *
from z3mat import *
import numpy

A = z3matrix('A', 3)
x = z3matrix('x', (3,1))

def mat_eq(m1, m2):
  """mat_eq(m1, m2): true iff m1 and m2 are element-wise equal.
    Raises IndexError if m1 and m2 have different shapes.
  """
  return z3matall(matmap2(lambda e1, e2: e1 == e2, m1, m2))

def mat_gt(m1, m2):
  """mat_eq(m1, m2): true iff m1 and m2 are element-wise equal.
    Raises IndexError if m1 and m2 have different shapes.
  """
  return z3matall(matmap2(lambda e1, e2: e1 > e2, m1, m2))

print 'Ready to prove (x.T * A.T).T == A*x'
#prove(mat_eq((x.T * A.T).T, A*x))

# show the equality fails if we forget to transpose A
#prove(mat_eq((x.T * A).T, A*x))



# to understand the counter-example, let's put it back
# into numpy form

def get_cex(p):
  """If p is a theorem, return 'proved'
    If we can refute p, return a model for Not(p)
    If Z3 fails, return 'unknown'
  """
  s = Solver()
  s.add(Not(p))
  ch = s.check()
  if(ch == unsat): return  'proved'
  elif(ch == sat): return s.model()
  else: return 'unknown'

"""
m = get_cex(mat_eq((x.T * A).T, A*x))
A_cex = z3matFromModel(A, m)
x_cex = z3matFromModel(x, m)
print 'A_cex = ' + str(A_cex)
print 'x_cex = ' + str(x_cex)
print '(x_cex.T * A_cex).T = ' + str((x_cex.T * A_cex).T)
print 'A_cex * x_cex = ' + str(A_cex * x_cex)
"""

# A freebie -- your reward for reading this far
def symmetric(A):
  """symmetric(A): return an expression that is satisfied iff A is a
    symmetric matrix.  symmetric(A) fails with IndexError if A is not a
    square matrix.
  """
  try:
    sh = A.shape
    if(sh[0] != sh[1]):
      raise IndexError('symmetric(A): A is not a square matrix')
    return And(*[A[i,j] == A[j,i] for i in range(sh[0]) for j in range(i)])
  except Exception:
    raise IndexError('symmetric(A): A is a matrix')

def element_wise_positive(A):
  """element_wise_positive(A): return an expression that is satisfied iff A is element_wise_positive.  symmetric(A) fails with IndexError if A is not a
    square matrix.
  """
  sh = A.shape
  return And(*[A[i,j] > 0 for i in range(sh[0]) for j in range(sh[0])])

def abs(x):
    return If(x >= 0,x,-x)

def diagonally_dominant(A):
  """diagonally_dominant(A): returns an expression which is satisfied iff A is diagonally_dominant and fails if A is not a square matrix
  """
  #sorry about this I was rushed.
  s00 = abs(A[0,0])
  s01 = abs(A[0,1])
  s02 = abs(A[0,2])
  s10 = abs(A[1,0])
  s11 = abs(A[1,1])
  s12 = abs(A[1,2])
  s20 = abs(A[2,0])
  s21 = abs(A[2,1])
  s22 = abs(A[2,2])
  return And((s00 > (s01 + s02)),(s11 > (s10 + s12)),(s22 > (s20 + s21)),
          A[0,0] == s00,
          A[0,1] == s01,
          A[0,2] == s02,
          A[1,0] == s10,
          A[1,1] == s11,
          A[1,2] == s12,
          A[2,0] == s20,
          A[2,1] == s21,
          A[2,2] == s22)

def not_zero_vector(x):
  """not_zero: return an expression that is satisfied iff no elements are equal to zero.
    square matrix.
  """
  sh = x.shape
  return Or(*[x[i,0] > 0 for i in range(sh[0])])

def positive_definite(A,x):
  """not_zero: return an expression that is satisfied iff no elements are equal to zero.
    square matrix.
  """
  sha = A.shape
  shx = x.shape
  if(sha[0] != sha[1]):
    raise IndexError('positive_definiete(A,x): A is not a square matrix')
  if(shx[1] != 1):
    raise IndexError('positive_definite(A,x): x is not a vector')
  if(shx[0] != sha[0]):
    raise IndexError('positive_definite(A,x): x and A have unequal lengths')
  zero = z3matrix('0', (1,1))
  zero[0,0] = 0
  return And(not_zero_vector(x), mat_gt((x.T * A * x),zero))


#stewarts work begins here
#semetric and element-wise positive
A = z3matrix('A', 3)
x = z3matrix('x', (3,1))
#solve(positive_definite(A,x))
solve(And(symmetric(A), element_wise_positive(A),Not(positive_definite(A,x))))
solve(And(symmetric(A), diagonally_dominant(A),Not(positive_definite(A,x))))
solve(And(diagonally_dominant(A), element_wise_positive(A),Not(positive_definite(A,x))))
