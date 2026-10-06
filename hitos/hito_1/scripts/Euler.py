from numpy import array, zeros
import matplotlib.pyplot as plt

def Euler(U, dt, t, F): 

    return U + dt * F(U, t)


plt.plot(U[:, 0], U[:, 1])
plt.axis('equal')
plt.show()