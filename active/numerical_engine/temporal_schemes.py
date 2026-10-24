from active.numerical_engine.NewtonRaphson import Newton

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
def Leap_Frog(V, dt, t, F):  # V = (Uⁿ, Uⁿ⁻¹), longitud 2N
    N = len(V) // 2
    Un, Unm1 = V[:N], V[N:]
    return concatenate((Unm1 + 2*dt*F(Un, t), Un))  # (Uⁿ⁺¹, Uⁿ)

# arranque: el primer paso se da con Euler para tener U¹
U1 = U0 + dt*F(U0, t[0])
V  = Cauchy_problem(F, t[1:], concatenate((U1, U0)), Leap_Frog)
U  = V[:, :N]     