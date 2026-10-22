from numpy import array, zeros

def partition(a, b, N):
    """Devuelve N+1 puntos equiespaciados entre a y b, con N segmentos."""
    return array([a + i*(b-a)/N for i in range(0, N+1)])

def Cauchy_problem(F, t, U0, method):
    n = len(t) - 1
    nv = len(U0)

    U = zeros((n+1, nv))
    U[0,:] = U0

    for i in range(0, n):
        dt = t[i+1] - t[i]
        U[i+1,:] = method(U[i,:], dt, t[i], F)
        
    return U
