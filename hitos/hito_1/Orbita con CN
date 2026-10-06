from numpy import array, zeros
from numpy.linalg import norm
import matplotlib.pyplot as plt

U0 = array([1.0, 0.0, 0.0, 1.0])

dt = 0.1
n = 200
nv = 4

U = zeros((n+1, nv))
U[0,:] = U0

for i in range(0, n):

    F = array([
        U[i,2],
        U[i,3],
        -U[i,0]/(U[i,0]**2 + U[i,1]**2)**1.5,
        -U[i,1]/(U[i,0]**2 + U[i,1]**2)**1.5
    ])

    Y = U[i,:]

    R = array([1.0, 1.0, 1.0, 1.0])

    while norm(R) > 1e-10:

        FY = array([
            Y[2],
            Y[3],
            -Y[0]/(Y[0]**2 + Y[1]**2)**1.5,
            -Y[1]/(Y[0]**2 + Y[1]**2)**1.5
        ])

        R = Y - U[i,:] - dt/2*(F + FY)

        Y = Y - R

    U[i+1,:] = Y

plt.plot(U[:,0], U[:,1])
plt.axis("equal")
plt.grid()
plt.title("Orbita de Kepler- Crank-Nicolson")
plt.xlabel("x") 
plt.ylabel("y") 
plt.show()