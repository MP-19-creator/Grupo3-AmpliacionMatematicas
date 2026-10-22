from numpy import array, zeros
from numpy.linalg import norm
from active.numerical_engine.SistemaEq.EqLineal import Gauss

def Newton(F, U0):
    i = 0
    n = 1000
    U = U0
    cambio = U0
    print("U0 =", U0)

    while norm(cambio) > 1e-8 and i <= n:
        i = i + 1
        J = Jacobian(F, U0)
        b = -F(U0)
        cambio = Gauss(J, b)
        U[:] = U[:] + cambio
        print("U =", U, "i =", i, "norma del cambio =", norm(cambio))

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
