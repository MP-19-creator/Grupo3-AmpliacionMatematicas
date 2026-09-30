from numpy import array, zeros, arange
from numpy.linalg import norm
import matplotlib.pyplot as plt
from methods import Euler, RK4, Crank_Nicolson

I1 = 1; I2 = 2; I3 = 3
Omega = 1; eps = 1e-3; Nv = 3
N = 10000 ; Dt = 0.01
U = zeros((N+1, Nv))
U[0, :] = array([eps, Omega, eps])

def F(U):
    w1, w2, w3 = U
    return array([(I2 - I3)/I1 * w2*w3,
                  (I3 - I1)/I2 * w3*w1,
                  (I1 - I2)/I3 * w1*w2])

def energia(U):
    return I1*U[:, 0]**2 + I2*U[:, 1]**2 + I3*U[:, 2]**2

t = arange(N+1) * Dt

# Fila superior: w(t). Fila inferior: deriva relativa de 2T
fig, axs = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
for j, metodo in enumerate((Euler, RK4, Crank_Nicolson)):
    Us = metodo(U.copy(), F, Dt, N)
    T2 = energia(Us)

    axs[0, j].plot(t, Us[:, 0], label='w1')
    axs[0, j].plot(t, Us[:, 1], label='w2')
    axs[0, j].plot(t, Us[:, 2], label='w3')
    axs[0, j].set_title(metodo.__name__)
    axs[0, j].legend()

    axs[1, j].semilogy(t, abs(T2 - T2[0]) / T2[0])
    axs[1, j].set_xlabel('t')

axs[0, 0].set_ylabel('w')
axs[1, 0].set_ylabel('|2T - 2T0| / 2T0')
plt.tight_layout()
plt.show()