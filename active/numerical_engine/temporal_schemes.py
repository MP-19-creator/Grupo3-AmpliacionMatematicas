from active.numerical_engine.NewtonRaphson import Newton
from numpy import array_equal, isclose

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

# Crank-Nicolson
def Crank_Nicolson(U, dt, t, F):
    def G(X):
        return X - A - dt/2 * (F(X, t + dt))
    A = U + dt/2 * F(U, t)
    return Newton(G, U)

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