from numpy import array, zeros
from numpy.linalg import norm
from active.numerical_engine.SistemaEq.EqLineal import Gauss

def Newton(F, U0):
    i = 0
    n = 1000
    # Trabajar con una copia decimal sin modificar el estado inicial
    U = array(U0, dtype=float)

    # Iterar mientras U no satisfaga el sistema F(U) = 0
    while norm(F(U)) > 1e-10 and i < n:
        i = i + 1
        J = Jacobian(F, U)
        b = -F(U)
        cambio = Gauss(J, b)
        U[:] = U[:] + cambio

    if not norm(F(U)) <= 1e-10:
        raise RuntimeError("Newton no ha encontrado una solucion con la tolerancia indicada")

    return U

def Jacobian(F, U):
    dt = 1e-3
    nv = len(U)
    cambio = zeros(nv)
    J = zeros((nv, nv))

    for i, _ in enumerate(U):
        cambio[:] = 0
        cambio[i] = dt
        J[:, i] = (F(U + cambio) - F(U - cambio)) / (2*dt)

    return J

# def f(U):
#     # return array([U**2 - 1])
#     return U**2 - 1

# U0 = array([0.1])
# print("solution =", Newton(f, U0))
