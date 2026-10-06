from numpy import zeros

def Cauchy_problem(F, t, U0, method):

    n = len(t) - 1
    nv = len(U0)

    U = zeros((n+1, nv))
    U[0,:] = U0

    for i in range(0, n):
        
        dt = t[i+1] - t[i]
        U[i+1,:] = method(U[i,:], dt, t[i], F)

    return U