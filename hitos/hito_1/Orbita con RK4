from numpy import array, zeros
import matplotlib.pyplot as plt

U0 = array([1.0, 0.0, 0.0, 1.0])

dt = 0.1
n = 200
nv = 4

U = zeros((n+1, nv))
U[0, :] = U0

for i in range(0, n):

    X = U[i, :]

    k1 = array([
        X[2],
        X[3],
        -X[0]/(X[0]**2 + X[1]**2)**1.5,
        -X[1]/(X[0]**2 + X[1]**2)**1.5
    ])

    X = U[i, :] + dt*k1/2

    k2 = array([
        X[2],
        X[3],
        -X[0]/(X[0]**2 + X[1]**2)**1.5,
        -X[1]/(X[0]**2 + X[1]**2)**1.5
    ])

    X = U[i, :] + dt*k2/2

    k3 = array([
        X[2],
        X[3],
        -X[0]/(X[0]**2 + X[1]**2)**1.5,
        -X[1]/(X[0]**2 + X[1]**2)**1.5
    ])

    X = U[i, :] + dt*k3

    k4 = array([
        X[2],
        X[3],
        -X[0]/(X[0]**2 + X[1]**2)**1.5,
        -X[1]/(X[0]**2 + X[1]**2)**1.5
    ])

    U[i+1, :] = U[i, :] + dt*(k1 + 2*k2 + 2*k3 + k4)/6


plt.plot(U[:, 0], U[:, 1])
plt.axis("equal")
plt.grid()
plt.title("Orbita de Kepler- RK4")
plt.xlabel("x")
plt.ylabel("y")
plt.show()