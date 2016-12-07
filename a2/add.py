from z3 import *

def addCheck(a, b, c_in, s, c_out):
  return(And(s == Xor(Xor(a, b), c_in),
         c_out == Or(And(a, b), And(b, c_in), And(a, c_in))))

def proveAddCheck():
  a, b, c_in, c_out, s = Bools('a b c_in c_out s')
  aint, bint, c_inint, c_outint, sint = Ints('aint bint c_inint c_outint sint')
  aint = If(a == True, 1, 0)
  bint = If(b == True,  1, 0)
  c_inint = If(c_in == True, 1, 0)
  c_outint = If(c_out == True, 1, 0)
  sint = If(s == True, 1, 0)
  prove(And(addCheck(a,b,c_in,s,c_out),aint + bint + c_inint == sint + 2*c_outint))

def test1():
  a, b, c_in = Bools('a b c_in')
  x = Xor(a, b)
  s = Xor(x, c_in)
  y = Not(And(a, b))
  z = Not(And(c_in, x))
  c_out = Not(And(y, z))
  prove(addCheck(a, b, c_in, s, c_out))

def test2():
    a, b, c_in = Bools('a b c_in')
    e = Not(Xor(a, b))
    f = Not(And(a, b))
    g = Not(Xor(a, c_in))
    h = Not(And(c_in, e))
    i = Not(And(h, f))
    s = g
    c_out = i
    prove(addCheck(a, b, c_in, s, c_out))


def test3():
    a, b, c_in = Bools('a b c_in')
    e = Not(And(a, b))
    f = Not(And(b, c_in))
    g = Not(And(a, c_in))
    h = Not(Or(a, b, c_in))
    i = Not(And(a, b, c_in))
    j = Not(And(e, f, g))
    k = Not(Or(h, j))
    l = Not(And(i, k))
    s = l
    c_out = j
    prove(addCheck(a, b, c_in, s, c_out))

def test4():
    a, b, c_in = Bools('a b c_in')
    e = Not(And(a, b))
    f = Not(And(b, c_in))
    g = Not(And(a, c_in))
    h = Not(Or(a, b, c_in))
    i = Not(And(a, b, c_in))
    j = Not(And(e, f, g))
    k = Or(h, j)
    l = Not(And(i, k))
    s = l
    c_out = j
    prove(addCheck(a, b, c_in, s, c_out))

test1()
test2()
test3()
test4()
proveAddCheck()
