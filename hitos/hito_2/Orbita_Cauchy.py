from active.numerical_engine.temporal_schemes import Euler, RK4, Crank_Nicolson
from active.space_physics.kepler import Kepler
from active.numerical_engine.Cauchy_Problem import Cauchy_problem
import matplotlib.pyplot as plt
from numpy import array, cos, sin, pi  
from numpy import linspace

def PruebaCauchy(tf, N, U0): 
   t = linspace(0, tf, N)
   schemes = [Euler, RK4, Crank_Nicolson]

   for method in schemes:
      U =  Cauchy_problem(Kepler, t, U0, method) 

      plt.axes().set_aspect('equal')
      plt.plot( U[:,0] , U[:,1], ".")
      plt.plot( cos(t) , -sin(t), ".")
      plt.show()

if __name__ == "__main__":
  PruebaCauchy(tf = 24*pi, N = 40, U0 = array( [ 1., 0., 0., 1. ] ) )