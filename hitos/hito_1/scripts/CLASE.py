from numpy import array, zeros
from numpy.linalg import norm
import matplotlib.pyplot as plt
from methods import Euler, RK4, Crank_Nicolson

N = 10000 ; Dt = 0.001 ; Nv = 2
U = zeros((N+1, Nv))
U[0, :] = array([1, 0])

def F(U):
    return array([U[1], -U[0]])

fig, axs = plt.subplots(1, 3, figsize=(15, 5))
for ax, metodo in zip(axs, (Euler, RK4, Crank_Nicolson)):
    Us = metodo(U.copy(), F, Dt, N)
    ax.plot(Us[:, 0], Us[:, 1])
    ax.axis('equal')
    ax.set_title(metodo.__name__)
plt.show()