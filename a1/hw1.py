"""Question 1"""
# Puzzel Solver
#http://www.logic-puzzles.org/game.php?u2=cf116e5b9aa6feb49395fe9d7ab9f3dd
from z3 import *
import puzzle_utils

Ships , (barnacle, crusty, dagger, doubloon, mermaid) = EnumSort('Ships' , ('barnacle', 'crusty', 'dagger', 'doubloon', 'mermaid'))
Pirates, (four, red, sparrow, stubborn, wicked) = EnumSort('Pirates', ('four', 'red', 'sparrow', 'stubborn', 'wicked'))
Countries, (denmark, england, ireland, spain, sweden) = EnumSort('Countries', ('denmark', 'england', 'ireland', 'spain', 'sweden'))
Years = ('Years', [1713,1731,1749,1767,1785])

s2p, p2s, one2oneA = puzzle_utils.one_to_one_fun(Ships, Pirates)
s2c, c2s, one2oneB = puzzle_utils.one_to_one_fun(Ships, Countries)
s2y, y2s, one2oneC = puzzle_utils.one_to_one_fun(Ships, Years)

p2c, c2p, one2oneD = puzzle_utils.one_to_one_fun(Pirates, Countries)
p2y, y2p, one2oneE = puzzle_utils.one_to_one_fun(Pirates, Years)
c2y, y2c, one2oneF = puzzle_utils.one_to_one_fun(Countries, Years)

s = Solver()

#The mermaid sank 18 years before the ship from england
v1 = (s2y(mermaid) + 18 == c2y(england))

#the one from spain was captianed by wicked weis
v2 = (c2p(spain) == wicked)

#of the ship that sank in 1749, and the vessle in 1767 one was captianed by sparrow strait, and the other was the doubloon
v3 = Xor(And(y2p(1749) == sparrow,y2s(1767) == doubloon),And(y2p(1767) == sparrow, y2s(1749) == doubloon))

#the ship sailed by stubborn sam sank 36 years before the crusty
v4 = (p2y(stubborn) + 36 == s2y(crusty))

#the ship from 1731 was captianed by foureyes
v5 = (y2p(1731) == four)

#the ship sailed by stubborn sam sank 36 years before the boat from sweden
v6 = (p2y(stubborn) + 36 == c2y(sweden))

#the ship sailed by stubborn sam sank 18 years before the ship from ireland
v7 = (p2y(stubborn) + 18 == c2y(ireland))

#The ship which sank in 1731 was either the dagger or the one from england
v8 = Xor(y2s(1731) == dagger, y2s(1731) == c2s(england))

#the ship sailed by stubborn sam sank 18 years before the dagger
v9 = (p2y(stubborn) + 18 == s2y(dagger))


v10 = And((one2oneA), (one2oneB),(one2oneC),(one2oneD), (one2oneE), (one2oneF)) 

s.add(v1,v2,v3,v4,v5,v6,v7,v8,v9,v10)
n_solution = 0
while( s.check() == sat and n_solution < 50):
    n_solution = n_solution + 1
    m = s.model()
    for year in Years[1]:
        ship = str(m.eval(y2s(year)))
        pirate = str(m.eval(y2p(year)))
        country = str(m.eval(y2c(year)))
        print "The " + ship + " from " + country + " sank in " + str(year) + " while sailed by " + pirate
    x = False
    for year in Years[1]:
        x = Or(x, s2y(m.eval(y2s(year))) != year, \
                p2y(m.eval(y2p(year))) != year, \
                c2y(m.eval(y2c(year))) != year)
    s.add(x)
    if(s.check() == sat):
        print "\n Here's another solution"

if(n_solution == 1 and s.check() == unsat):
  print "Yay -- there is exactly one solution!"
elif(s.check() == unsat):
  print "All " + str(n_solution) + " solutions reported"
elif(s.check() == unknown):
  print "Yikes, Z3 returned 'unknown' -- can this really be too complicated?"
elif(s.check() == sat):
  print "There are still more solutions"
else:
  print "Done -- but the status reporting code is botched"





""" Question 2 """
from z3 import *

def my_prove(s, claim):
  if(s.check() != sat):
    print "my_prove(" + str(claim) + "): WARNING -- assumptions are unsatisfiable"
  else:
    s.push()
    s.add(Not(claim))
    ch = s.check()
    if(ch == unsat):
      print "my_prove(" + str(claim) + "):  proven"
    elif(ch == sat):
      print "my_prove(" + str(claim) + "):  refuted, here's a counter-example"
      print "  " + str(s.model())
    elif(ch == unknown):
      print "my_prove(" + str(claim) + "):  solver failed"
    else:
      print "my_prove(" + str(claim) + "):  INTERNAL ERROR -- unrecognized return code"
    s.pop()

# the binary-search problem from "Satisfiabilty Modulo Theories: Introduction
# and Application"

# declare the variables
# I use low and high to represent the values at the beginning of executing
# the loop body, and low_new, and high_new to represent their values after
# executing the loop body
intbits = 32  # I'll assume 32 bit words
low, high, = BitVecs('low high', intbits)
mid, low_new, high_new, = BitVecs('mid low_new high_new', intbits)
key, val = BitVecs('key val', intbits)
arr = Function('arr', BitVecSort(intbits), BitVecSort(intbits))

s = Solver()
# a Solver has a set of constraints.  Here are the methods I'll use:
#    add(constraint) -- add a constraint to the solver.  The solver
#      looks for a solution that satisfies all constraints.
#    check() -- check to see if the current set of constraints is
#      satisfiable.  Returns 'sat' if satisfiable, 'unsat' if unsatisfiable,
#      and 'unkown' if the SMT solver failed.
#    model() -- if the current set of constraints is satisfiable, model()
#      returns a satifying assignment.   In particular, if
#        m = s.model(), 
#      then we can write
#        m.evaluate(expr)
#      to evaluate the expression expr with the assignment of values to
#      variables given by m.
#    push() -- create a new context that inherits all the existing constraints
#    pop()  -- restore the set of constraints to what it was just before the
#                corresponding push().

# Now, I'll translate the binary-search code to Z3
# assert( low > high || 0 <= low < high)
s.add(Or(low > high, And(0 <= low, low < high)))

# consider: while(low <= high)
#   There are two possible paths depending on the outcome of the
#   comparison.  We'll handle the low <= high case first.
s.push()  # we can s.pop() back to this state later
s.add(low <= high)  # the while-condition is satisfied
s.add(mid == (low/2 + high/2))
my_prove(s, And(0 <= mid, mid <= high))
s.add(val == arr(mid))
# consider: if(key == val)
#   As with the while-loop, we get two paths.
s.push() # we'll s.pop() later.
s.add(key == val) # the then-branch
my_prove(s, arr(mid) == key)  # make sure our return value is correct
s.pop()
s.add(key != val)  # now look at the else-branch
# I could write two more paths for the if(val > key).  But, I'll
# be a "good compiler", do some dataflow analysis, and notice that
# I can just use some conditional expressions instead.
s.add(low_new == If(val < key, mid+1, low))
s.add(high_new == If(val < key, high, mid-1))
# now check that our initial assertion holds here and that we've decreased high-low
my_prove(s, Or(high_new == low_new - 1, \
               And(low <= low_new, low_new <= high_new, high_new <= high, \
	          (high_new - low_new) < (high - low))))
s.pop()
# now we're to the exit of the while loop
# return -1  # what should we check?

""" C Code for question 2 

#include <stdio.h>
#include <assert.h>

int main () {
    int array[] = {1,2,5,7,9,10};
    int i = 0;
    for (i = 0; i < sizeof(array)/sizeof(int)-1; i++){
        int index = binary_search(array, 0, sizeof(array)/sizeof(int), array[i]);
        printf("index of %d is %d\n",array[i],index);
    }

}

int binary_search(
	int arr[], int low, int high, int key) {
		assert (low > high || 0 <= low < high);
		while ( low <= high ) {
            //Find middle value
            int mid = low/2 + high/2;
            printf("low %d, mid =  %d, high=%d key=%d\n",low,mid,high,key);
            assert(0 <= mid);
            assert(mid <= high);
            int val = arr[mid];
            printf("low %d, mid =  %d, high=%d key=%d val=%d\n",low,mid,high,key,val);
            //Refine range
            if (key == val) { 
                return mid;
            }
            if (val > key) {
                high = mid-1;
            }
            else {
                low = mid+1;
            }
        }
	    return -1;
}
"""




""" Question 3 """

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
  return And((s00 > (s01 + s02)),(s11 > (s10 + s12)),(s22 > (s20 + s21)))

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
solve(diagonally_dominant(A))
solve(And(symmetric(A), element_wise_positive(A),Not(positive_definite(A,x))))
solve(And(symmetric(A), diagonally_dominant(A),Not(positive_definite(A,x))))
solve(And(diagonally_dominant(A), element_wise_positive(A),Not(positive_definite(A,x))))
