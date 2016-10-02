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
 

