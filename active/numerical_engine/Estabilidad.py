"""
Estabilidad absoluta.  Aplicando un esquema al problema test  dU/dt = lambda U  se obtiene
        U_{n+1} = R(z) U_n,        z = lambda dt
R(z) es la FUNCION DE ESTABILIDAD: el numero por el que el esquema multiplica la solucion en cada paso.
Region de estabilidad absoluta:  { z : |R(z)| <= 1 }.
Se acepta el esquema como funcion (Euler) o como texto ("Euler").
"""
from numpy import sqrt, where, abs, exp, meshgrid


def stability_function(method, z):
    name = method if isinstance(method, str) else method.__name__
    if name == "Euler":                              # U + dt lambda U
        return 1 + z
    if name == "Crank_Nicolson":                     # (1 - z/2) U_{n+1} = (1 + z/2) U_n
        return (1 + z/2) / (1 - z/2)
    if name == "RK4":                                # Taylor de e^z hasta z^4
        return 1 + z + z**2/2 + z**3/6 + z**4/24
    # Solo para el hito 4 (la PEI no los usa)
    if name in ("Inverse_Euler", "Euler_implicit"):
        return 1 / (1 - z)
    if name == "Leap_Frog":                          # dos pasos: r^2 - 2 z r - 1 = 0, raiz de mayor modulo
        s = sqrt(z**2 + 1 + 0j)
        r1, r2 = z + s, z - s
        return where(abs(r1) >= abs(r2), r1, r2)
    raise ValueError(f"Esquema desconocido: {name}")


def is_absolutely_stable(method, z, tol=1e-12):
    return abs(stability_function(method, z)) <= 1 + tol


def stability_region(method, x, y):
    """ |R(z)| en la malla z = x + i y  (para contourf / contour) """
    X, Y = meshgrid(x, y)
    return X, Y, abs(stability_function(method, X + 1j*Y))


def amplification_error(method, z):
    """ |R(z)| / |e^z|: lo que el esquema amplifica (o amortigua) DE MAS respecto a la solucion exacta en un paso.
        Para z imaginario puro |e^z| = 1, asi que es directamente |R(z)| """
    return abs(stability_function(method, z)) / abs(exp(z))