from z3 import *

# es is a z3 EnumSort.  We return a list of all values in the set.
# There's got to be a better way to do this!
def get_values(es):
  maxhowmany = 1000000
  s = Solver()
  a,b = Consts(('a', 'b'), es)
  s.add(a==b)
  v = []

  # If es is IntSort() or RealSort() or some other unbounded type,
  # then we'll never run out of values to include in our set.  We'll
  # set an upper-bound of maxhowmany and give up if we hit that limit.
  howmany = 0
  while((s.check() == sat) and (howmany <= maxhowmany)):
    m = s.model()
    v.append(m.eval(m[0]()))
    s.add(a != v[-1])
  if(howmany > maxhowmany):
    raise Exception("too many values in " + es.str)
  return tuple(v)


class my_enum:
  def __init__(self, stuff):
    if(type(stuff) == tuple):
      self.values = tuple(set(stuff[1]))
      lo = None
      hi = None
      for v in self.values:
        if(isinstance(v, (int, long))): # how wonderfully non-Pythonic  :)
          if((lo == None) or (v < lo)): lo = v
	  else:
	    if((hi == None) or (hi < v)): hi = v
	else:
	  raise Exception("z3_utils.my_enum: stuff must be a z3 enumerated type or a list of integers")
      self.sort = IntSort()
      self.lo = lo
      self.hi = hi
      self.name = stuff[0]
    else: # assume stuff is a z3 enumeration
      self.values = get_values(stuff)
      self.sort = stuff
      self.name = str(stuff)

  def len(self):
    return len(self.values)

  def valid(self, v):
    if(self.sort == IntSort()):
      if(self.len() == self.hi + 1 - self.lo):
        return And(self.lo <= v, v <= self.hi)
      else:
        x = []
	for u in self.values:
	  x.append(v == u)
	return Or(*x)
    else:
      raise Exception("I don't want to bother with checking membership in z3 enumerated types")

    
# define an uninterpreted function from sort1 to sort2 called name12
#   and one from sort2 to sort1 called name12 + "_inv".
#   sort1 and sort2 can each be either a z3 EnumSort or a list of integers.
#   We require sort1 and sort2 to have the same cardinality
#   We return (f12, f12_inv, constraints) where f12 is the function corresponding
#   to name12, constraints is a z3 predicate asserting that f12_inv is the inverse
#   of f12 (which implies that f12 is one_to_one), and f12_inv is the inverse of
#   f12.
def one_to_one_fun(sort1, sort2):
  me1 = my_enum(sort1)
  me2 = my_enum(sort2)
  if(me1.len() != me2.len()):
    raise Exception("one_to_one_fun: sort1 and sort2 have different cardinalities")
  name12 = me1.name + "_to_" + me2.name
  name21 = me2.name + "_to_" + me1.name
  f12 = Function(name12, me1.sort, me2.sort)
  f21 = Function(name21, me2.sort, me1.sort)
  c = []
  v1 = me1.values
  for i in range(me1.len()):
    c.append(f21(f12(v1[i])) == v1[i])
  if(me2.sort == IntSort()):
    for i in range(me1.len()):
      c.append(me2.valid(f12(v1[i])))
  if(me1.sort == IntSort()):
    v2 = me2.values
    for i in range(me2.len()):
      c.append(me1.valid(f21(v2[i])))

  return (f12, f21, And(*c))
