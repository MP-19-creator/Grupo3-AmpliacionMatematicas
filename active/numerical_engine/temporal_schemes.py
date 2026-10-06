from numpy.linalg import norm 

# Euler explicit
def Euler(U, dt, t, F): 
    return U + dt * F(U, t)

# Euler implicit
def Euler_implicit(U, dt, t, F):
    Y = U + dt * F(U, t)
    R = Y - U - dt * F(Y, t + dt)
    while norm(R) > 1e-6:
        Y = U + dt * F(Y, t + dt)
        R = Y - U - dt * F(Y, t + dt)
    return Y    

# Runge-Kutta 4th order
def RK4(U, dt, t, F):
    k1 = F( U, t)
    k2 = F( U + dt * k1/2, t + dt/2 )
    k3 = F( U + dt * k2/2, t + dt/2 )
    k4 = F( U + dt * k3,   t + dt   )
    return  U + dt * ( k1 + 2*k2 + 2*k3 + k4 )/6

# Crank-Nicolson
def Crank_Nicolson(U, dt, t, F):
    Y = U + dt * F(U, t)
    R = Y - U - dt/2 * (F(U, t) + F(Y, t + dt))
    while norm(R) > 1e-6:
        Y = Y - R
        R = Y - U - dt/2 * (F(U, t) + F(Y, t + dt))
    return Y

# --------- CONVERGENCIA ---------
def richardson_error(coarse_solution, fine_solution, order):
    """Estima el error mediante soluciones con pasos relacionados.

    TODO: documentar la razón entre pasos y alinear las mallas temporales.
    """
    raise NotImplementedError


def convergence_order(step_sizes, errors):
    """Estima el orden observado a partir de varios pasos y errores.

    TODO: ajustar la pendiente en escala logarítmica.
    """
    raise NotImplementedError

# --------- ESTABILIDAD ---------
def stability_function(method, z):
    """Evalúa R(z) del método temporal indicado.

    TODO: definir las funciones de Euler, Euler inverso, Leap–Frog,
    Crank–Nicolson y RK4, incluyendo la representación de Leap–Frog.
    """
    raise NotImplementedError

def is_absolutely_stable(method, z):
    """Indica si el método satisface |R(z)| <= 1.

    TODO: contemplar con cuidado la estabilidad neutral en la frontera.
    """
    raise NotImplementedError