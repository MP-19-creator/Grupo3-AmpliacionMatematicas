"""
Esquemas temporales de UN paso con la firma del curso:   U_{n+1} = method(U_n, dt, t_n, F)

La PEI 1 usa solo los tres esquemas del enunciado: Euler, Crank_Nicolson y RK4.
Cada uno lleva su orden teorico en method.order (lo usan Richardson y el paso adaptativo).
Si F trae su Jacobiano exacto en F.jacobian (la capa fisica lo pone), Crank-Nicolson lo usa en Newton.
"""
from active.numerical_engine.NewtonRaphson import Newton
from numpy import array_equal, isclose, eye

# Euler explicit
def Euler(U, dt, t, F): 
    return U + dt * F(U, t) 

# Euler implicit
def Euler_implicit(U, dt, t, F):
    def G(X):
        return X - U - dt * F(X, t + dt)
    return Newton(G, U)

# Runge-Kutta 4th order
def RK4(U, dt, t, F):
    k1 = F( U, t)
    k2 = F( U + dt * k1/2, t + dt/2 )
    k3 = F( U + dt * k2/2, t + dt/2 )
    k4 = F( U + dt * k3,   t + dt   )
    return  U + dt * ( k1 + 2*k2 + 2*k3 + k4 )/6

# # Crank-Nicolson
# def Crank_Nicolson(U, dt, t, F):
#     def G(X):
#         return X - A - dt/2 * (F(X, t + dt))
#     A = U + dt/2 * F(U, t)
#     return Newton(G, U)

"ESTE LO HE PUESTO YO (NACHO), INVOLUCRA LA JACOBIANA PERO NO SE MUY BIEN PORQUE"
# Crank-Nicolson, regla del trapecio (orden 2, implicito):
#     U_{n+1} = U_n + dt/2 [ F(U_n, t_n) + F(U_{n+1}, t_{n+1}) ]
# La incognita U_{n+1} esta a los dos lados: se resuelve G(X) = X - A - dt/2 F(X, t_{n+1}) = 0 con Newton.
def Crank_Nicolson(U, dt, t, F):
    A = U + dt/2 * F(U, t)
    def G(X):
        return X - A - dt/2 * F(X, t + dt)
    def dG(X):                                       # dG/dX = Id - dt/2 dF/dX  (Jacobiano exacto)
        return eye(len(U)) - dt/2 * F.jacobian(X, t + dt)
    return Newton(G, Euler(U, dt, t, F), dG if hasattr(F, "jacobian") else None)   # predictor: Euler

# Leap-Frog
_leap_frog_state = None
def Leap_Frog(U, dt, t, F):
    global _leap_frog_state

    if _leap_frog_state is None:
        result = U + dt * F(U, t)
    else:
        result = _leap_frog_state + 2 * dt * F(U, t)

    _leap_frog_state = U.copy()
    return result