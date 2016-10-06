"""z3mat: some functions for handling matrices of Z3 expressions.
The functions we define:
  z3matrix(name, dim): create a matrix of the given name and dimensions.
  matmap(fun, matrix): create a new_matrix by applying fun to each element of
      matrix.
  matmap2(fun, m1, m2): create a new matrix by applying fun to pairs of
      corresponding elements of m1 and m2.
  matred(fun, matrix, acc0, dir): combined the elements of matrix using
      fun.
    The reduction can be done per row, per column, or over all elements.
  z3matall(matrix): create the Z3 expression for the conjunction of all
    elements of matrix.
  z3matall(pred, matrix): create the Z3 expression for the conjunction of
    the result of pred applied to each element of matrix.
  z3matany(matrix): create the Z3 expression for the disjunction of all
    elements of matrix.
  z3matany(pred, matrix): create the Z3 expression for the disjunction of
    the result of pred applied to each element of matrix.
  z3matFromModel(A, model): A is a matrix of Z3 symbolic expressions.
    We evaluate each of these according to model to get a numerical
    matrix.  For example, model can be a counter-example from a failed
    theorem.
  doc(foo):  Print the docstring for foo, if it has one.
  z3RealToFloat(r): a helper for z3matFromModel.
"""

from z3 import *
import numpy

# I'd like to make z3mat a subclass of numpy.matrix, but numpy.matrix
#   defines its own version of __new__, and I don't want to work out
#   the inner workings of numpy.matrix so I can call it.  Because making
#   a subclass isn't practical, I'll just define some functions that
#   are handy when using Z3 expressions with matrices.

def z3matrix(name, dim):
  """z3matrix(name,dim) create a matrix with entries of class z3.Real.
    name: a string, we append [row_index,col_index] to this string to
      get the name for each element.
    dim: the dimensions.  Either a non-negative integer, in which case
      we make a square matrix of that size, or a list or tuple of two
      non-negative integers where the first specifies the number of
      rows and the second specifies the number of columns.
    Example:
      z3matrix('A', (2,3)) ->
      matrix([[A[0,0], A[0,1], A[0,2]],
              [A[1,0], A[1,1], A[1,2]]], dtype=object)
  """
  if(type(dim) == int):
    if(dim < 0): raise badDim()
    else: dim = (dim, dim)  # make a square matrix
  elif((type(dim) == list) or (type(dim) == tuple)):
    if(len(dim) != 2): badDim()
    elif((type(dim[0]) != int) or (dim[0] < 0)): badDim()
    elif((type(dim[1]) != int) or (dim[1] < 0)): badDim()
  return(numpy.matrix( \
    [ [ Real(name + "[" + str(i) + "," + str(j) + "]") \
        for j in range(dim[1]) \
      ] for i in range(dim[0]) \
    ] \
  ))

# numpy.matrix really should support map and reduce, but it doesn't.

import inspect

def matmap(fun, matrix):
  """matmap(fun, matrix): return the matrix obtained by applying fun to each
    element of matrix.
  fun can be called just with the element, or with the element and its
      indices:
    if fun takes one argument, we call fun(e) for each element e of matrix.
    if fun takes three arguments, we call fun(e, i, j) where i and j are
      the indices of e.
    if fun takes two arguments, we call fun(e, m) where m = ncols*i + j,
      and ncols is the number of columns of matrix.  This gives the position
      of e in matrix in row-major order.  In particular, if matrix is a vector
      (an n-by-1 or 1-by-n array), then m is the index you want.
    Example:
      matmap(lambda x: x*x, numpy.matrix(((1,2),(3,4)))) ->
      matrix([[ 1,  4],
              [ 9, 16]])
  """
  arity = len(inspect.getargspec(fun).args)
  if(arity == 1):
    data = [ [ fun(matrix[i,j]) for j in range(matrix.shape[1]) ] \
             for i in range(matrix.shape[0]) \
           ]
  elif(arity == 2):
    data = [ [ fun(matrix[i,j], i*matrix.shape[1] + j) \
               for j in range(matrix.shape[1])\
             ] \
             for i in range(matrix.shape[0])\
           ]
  elif(arity == 3):
    data = [ [ fun(matrix[i,j], i, j) for j in range(matrix.shape[1]) ] \
             for i in range(matrix.shape[0])\
           ]
  else:
    raise TypeError("z3mat.map: bad arity for fun -- " + str(arity))
  return numpy.matrix(data)

def matmap2(fun, m1, m2):
  """matmap(fun, m1, m2): return the matrix obtained by applying fun to each
    pair of corresponding elements from m1 and m2.  m1 and m2 must have the
    same shape.
  fun can be called just with the two elements, or with the elements and their
      indices:
    if fun takes two arguments, we call fun(e1, e2) for each element e1 of m1
      and the corresponding e2 of m2.
    if fun takes four arguments, we call fun(e1, e2, i, j) where i and j are
      the indices of e1 and e2.
    if fun takes tghree arguments, we call fun(e1, e2, m) where m = ncols*i + j,
      and ncols is the number of columns of m1 and m2.  This gives the position
      of e1 and e2 in m1 and m2 in row-major order.  In particular, if m1 and
      m2 are vectors (an n-by-1 or 1-by-n array), then m is the index you want.
  """
  if(m1.shape != m2.shape):
    raise IndexError('matmap2: m1 and m2 must have the same shape')
  else: shape = m1.shape
  arity = len(inspect.getargspec(fun).args)
  if(arity == 2):
    data = [ [ fun(m1[i,j], m2[i,j]) for j in range(shape[1]) ] \
             for i in range(shape[0]) \
           ]
  elif(arity == 3):
    data = [ [ fun(m1[i,j], m2[i,j], i*shape[1] + j) \
               for j in range(shape[1])\
             ] \
             for i in range(shape[0])\
           ]
  elif(arity == 4):
    data = [ [ fun(m1[i,j], m2[i,j], i, j) for j in range(shape[1]) ] \
             for i in range(shape[0])\
           ]
  else:
    raise TypeError("z3mat.map: bad arity for fun -- " + str(arity))
  return numpy.matrix(data)

def matred(fun, matrix, acc0=None, dir=None):
  """matred(fun, matrix, acc0, dir): reduce for matrices
   If dir is omitted, then we treat matrix as a list of elements in row-major
     order and perform the reduce.  
   If dir=0, we replace each row with the reduce of the elements of that row.
     Thus, if matrix.shape()=[nrows,ncols], matred with dir=0 returns rmat,
     with shape() = [nrows,1]
   If dir=1, we replace each column with the reduce of the elements of that
     column.  If matrix.shape()=[nrows,ncols], matred with dir=1 returns
     rmat with shap()=[1,nrows]
    Example:
      matred(lambda x,y: x+y, numpy.matrix(((1,2),(3,4))), 0, 0) ->
      matrix([[ 3],
              [ 7]])
  """
  arity = len(inspect.getargspec(fun).args)
  def red(stuff):
    if(acc0 is None):
      return reduce(fun, stuff)
    else:
      return reduce(fun, stuff, acc0)
  if(dir is None):
    return red([matrix[i,j] for i in range(matrix.shape[0]) \
                            for j in range(matrix.shape[1])])
  elif(dir == 0): # reduce each row
      r = [ [ red([matrix[i,j] for j in range(matrix.shape[1])]) ] \
	    for i in range(matrix.shape[0])]
  elif(dir == 1): # reduce each column
    r = [ [ red([matrix[i,j] for i in range(matrix.shape[0])]) \
	    for j in range(matrix.shape[1]) ] ]
  else:
    raise IndexError("z3mat.reduce: bad direction -- " + str(dir))
  return numpy.matrix(r)

def z3matall(pred, matrix=None):
  """z3matall(pred, matrix): true iff all elements of matrix satisfy pred.
    pred is a predicate (a function whose result is a boolean or z3 BoolSort())
    If pred takes one argument, we call pred(e) for each element e of matrix.
    If pred takes three arguments, we call pred(e, i, j) where i and j are
      the indices of e.
    If pred takes two arguments, we call pred(e, m) where m = ncols*i + j,
      and ncols is the number of columns of matrix.  This gives the position
      of e in matrix in row-major order.  In particular, if matrix is a vector
      (an n-by-1 or 1-by-n array), then m is the index you want.
    If z3matall is called with just one argument, it is assumed to be a matrix
      of booleans, and pred is the identity predicate.
  """
  if(matrix is None): return z3matall(lambda p: p, pred)
  else:
    pmat = matmap(pred, matrix)
    return And(*[pmat[i,j] for i in range(pmat.shape[0]) for j in range(pmat.shape[1])])

def z3matany(pred, matrix):
  """z3matany(pred, matrix): true iff any elements of matrix satisfy pred.
    pred is a predicate (a function whose result is a boolean or z3 BoolSort())
    If pred takes one argument, we call pred(e) for each element e of matrix.
    If pred takes three arguments, we call pred(e, i, j) where i and j are
      the indices of e.
    If pred takes two arguments, we call pred(e, m) where m = ncols*i + j,
      and ncols is the number of columns of matrix.  This gives the position
      of e in matrix in row-major order.  In particular, if matrix is a vector
      (an n-by-1 or 1-by-n array), then m is the index you want.
    If z3matany is called with just one argument, it is assumed to be a matrix
      of booleans, and pred is the identity predicate.
  """
  if(matrix is None): return z3matall(lambda p: p, pred)
  else:
    pmat = matmap(pred, matrix)
    return Or(*[pmat[i,j] for i in range(pmat.shape[0]) for j in range(pmat.shape[1])])

def z3RealToFloat(r):
  """z3RealToFloat(r): convert a z3 real to a python float
    This is a helper for z3matFromModel.  r is a Z3 real-valued constant.
    If r represents a real constant, we convert that constant to a python
    float.  Warning: we take no precautions about loss of precision,
    overflows, or underflows.  If r has not been bound to a particular
    value, we return 0.0.
  """
  dir(r)
  if(hasattr(r, 'as_decimal')):
    s = r.as_decimal(20)
    if(s[-1] == '?'): return float(s[:-1])
    else: return float(s)
  else: # r is unconstrained in the solution, we'll must make it 0.
    return 0.0

def z3matFromModel(A, model):
  """z3matFromModel(A, model):
    A is a matrix of Z3 Real's.  model is a model that provides valuations
    for the elements of A.  We return a matrix of floats that corresponds
    to this valuation.  If some element of A is missing in the valuation,
    we return 0.0 for that element.  Note that A can be n-by-1 or 1-by-n
    (i.e. a vector); so this function handles vectors as well a matrices.
  """
  return numpy.matrix( \
    [ [ z3RealToFloat(model.evaluate(A[i,j])) for j in range(A.shape[1]) ] \
      for i in range(A.shape[0]) \
    ] \
  )

def doc(foo):
  """There ought to be an easy way to print docstrings in python, but I
    haven't found it.  Please let me know if there's a better way to do
    this.  If foo has a docstring, we print it.  Otherwise, we print
    'No docstring for foo'
  """
  if(hasattr(foo, '__doc__')): print foo.__doc__
  else: print "doc(foo): no docstring for foo"
