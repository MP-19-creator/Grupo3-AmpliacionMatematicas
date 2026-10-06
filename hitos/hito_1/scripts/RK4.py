from numpy import array, zeros
import matplotlib.pyplot as plt

def RK4(U, dt, t, F ): 

     k1 = F( U, t)
     k2 = F( U + dt * k1/2, t + dt/2 )
     k3 = F( U + dt * k2/2, t + dt/2 )
     k4 = F( U + dt * k3,   t + dt   )
 
     return  U + dt * ( k1 + 2*k2 + 2*k3 + k4 )/6

plt.plot(U[:, 0], U[:, 1])
plt.axis('equal')
plt.show()