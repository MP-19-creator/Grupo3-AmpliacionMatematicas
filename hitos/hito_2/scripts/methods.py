from numpy.linalg import norm

def Euler(U, F, Dt, N):
    for n in range(0, N):
        U[n+1, :] = U[n, :] + Dt * F(U[n, :])
    return U

def RK4(U, F, Dt, N):
    for n in range(0, N):
        k1 = F(U[n, :])
        k2 = F(U[n, :] + (Dt * k1)/2)
        k3 = F(U[n, :] + (Dt * k2)/2)
        k4 = F(U[n, :] + Dt * k3)
        U[n+1, :] = U[n, :] + Dt * (k1 + 2*k2 + 2*k3 + k4)/6
    return U

def Crank_Nicolson(U, F, Dt, N):
    for n in range(0, N):
        Fn = F(U[n, :])
        Y = U[n, :] + Dt * Fn
        R = Y - U[n, :] - Dt/2 * (Fn + F(Y))
        while norm(R) > 1e-6:
            Y = Y - R
            R = Y - U[n, :] - Dt/2 * (Fn + F(Y))
        U[n+1, :] = Y
    return U