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
s.add(Or(low >= high, And(0 <= low, low < high)))

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
