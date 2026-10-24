from numpy import array

def oscilador(U, t):
    x = U[0]
    vx = U[1]
    return array([vx, -x])