# Puzzel Solver
#http://www.logic-puzzles.org/game.php?u2=b78d0b29dc3707b02090e39b263e1ed9
from z3 import *
import puzzle_utils

Player, (gretchen, johnathan, maggie, rena, vincent) = EnumSort('Player', ('gretchen','johnathan','maggie','rena','vincent'))
Towns, (bristol, cutler, junction, ontario, pacific) = EnumSort('Towns', ('bristol','cutler','junction','ontario', 'pacific'))
Lanes, (one, two, four, five, six) = EnumSort('Lanes',('one','two','four','five','six'))

Scores = ('scores', [300, 380, 460, 540, 620])

p2t, t2p, one2oneA = puzzle_utils.one_to_one_fun(Player, Towns)
p2l, l2p, one2oneB = puzzle_utils.one_to_one_fun(Player, Lanes)
p2s, s2p, one2oneC = puzzle_utils.one_to_one_fun(Player, Scores)

l2s, s2l, one2oneD = puzzle_utils.one_to_one_fun(Lanes, Scores)
l2t, t2l, one2oneE = puzzle_utils.one_to_one_fun(Lanes, Towns)
t2s, s2t, one2oneF = puzzle_utils.one_to_one_fun(Towns, Scores)

s = Solver()


#1 Of gretchen and the person in lane 1, one scored 380 and the other was from Pacific Grove
v1 = (Or(
    And(p2s(gretchen) == 380, l2t(one) == pacific),
    And(p2t(gretchen) == pacific, l2s(one) == 380)
    ))

#2
v2 = (p2l(gretchen) != two)

#3 person in lane 6 scored 240 points more points than Gretchen
v3 = (l2s(six) == p2s(gretchen) + 240)

#4 The person in lane 5 scored more points than the contestant from Ontario
v4 = (l2s(five) > t2s(ontario))

#5 The contestant who scored 620 points is either the player from Bristol or the person in lane six
v5 = (Or(
    And(s2p(620) == l2p(six), s2p(620) != t2p(bristol)),
    And(s2p(620) != l2p(six), s2p(620) == t2p(bristol))
        ))

#6 Vincent wasn't from Junction City
v6 = (p2t(vincent) != junction)

#7 the player from junction City, maggie, Rena and the person who scored 460 are different
v7 = And((t2p(junction) != maggie ),
        (t2p(junction) != rena ),
        (t2p(junction) != s2p(460)),
        (maggie != rena),
        (maggie != s2p(460)),
        (rena != s2p(460)))

#8 the person who scored 460 was from Culter
v8 = (s2t(460) == cutler)

#9 Rena, the person who scored 540 and the contestant from cutler are three different people
v9 = And((rena != s2p(540) ),
        (rena != t2p(cutler)),
        (s2p(540) != t2p(cutler)))

#10 the player in lane 4 scored 80 points fewer points then gretchen
v10 = (l2s(four) == p2s(gretchen)- 80)

v11 = And((one2oneA),
    (one2oneB),
    (one2oneC),
    (one2oneD),
    (one2oneE),
    (one2oneF))

s.add(v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11)
print s.check()
s.check()
m = s.model()

print "traversing model..."
for d in m.decls():
    print "%s = %s" % (d.name(), m[d])


