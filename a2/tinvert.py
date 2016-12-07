from z3 import *

s = Solver()
x_1, y_1, z_1, x_2, y_2, z_2 = Bools('x_1 y_1 z_1 x_2 y_2 z_2')
u_1, u_2 = Bools('u_1 u_2')
f = Function('f', BoolSort(),BoolSort(),BoolSort(),BoolSort())
g = Function('g', BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort())
h_x = Function('h_x', BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort())
h_y = Function('h_y', BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort())
h_z = Function('h_z', BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort(),BoolSort())

#solve(And(f(True,True,True) == False ,g == Not(f)))

#s.add(Implies(x_1,x_2))
#s.add(Implies(y_1,y_2))
#s.add(Implies(z_1,z_2))

#s.add(u_1 == Not(f(x_1,y_1,z_1)))
#s.add(u_2 == Not(g(x_1,y_1,z_1,Not(f(x_1,y_1,z_1)))))
Not(g(x_1,y_1,z_1,Not(f(x_1,y_1,z_1))))

for x_1 in [True, False]:
    for y_1 in [True, False]:
        for z_1 in [True, False]:
            s.add(Implies(x_1,x_2))
            s.add(Implies(y_1,y_2))
            s.add(Implies(z_1,z_2))
            s.add(Implies(f(x_1,y_1,z_1),f(x_2,y_2,z_2)))
            s.add(Implies(g(x_1,y_1,z_1,f(x_1,y_1,z_1)),g(x_2,y_2,z_2,f(x_2,y_2,z_2))))
            s.add(h_x(x_1,y_1,z_1,Not(f(x_1,y_1,z_1)),Not(g(x_1,y_1,z_1,Not(f(x_1,y_1,z_1))))) == Not(x_1))
            s.add(h_y(x_1,y_1,z_1,Not(f(x_1,y_1,z_1)),Not(g(x_1,y_1,z_1,Not(f(x_1,y_1,z_1))))) == Not(y_1))
            s.add(h_z(x_1,y_1,z_1,Not(f(x_1,y_1,z_1)),Not(g(x_1,y_1,z_1,Not(f(x_1,y_1,z_1))))) == Not(z_1))
            #s.add(Implies(f(x,y,z),f(x,y,z)))

#s.add(h_x(False,y_1,z_1,u_1,u_2) == True)
#s.add(h_x(True,y_1,z_1,u_1,u_2) == False)
#s.add(h_y(x_1,False,z_1,u_1,u_2) == True)
#s.add(h_y(x_1,True,z_1,u_1,u_2) == False)
#s.add(h_z(x_1,y_1,False,u_1,u_2) == True)
#s.add(h_z(x_1,y_1,True,u_1,u_2) == False)

#s.add(Implies(h_y(x_1,y_1,z_1,u_1,u_2),Not(y_1)))
#s.add(Implies(h_z(x_1,y_1,z_1,u_1,u_2),Not(z_1)))

print s.check()
m = s.model()
print m


