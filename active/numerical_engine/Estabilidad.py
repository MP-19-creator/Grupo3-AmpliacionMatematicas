"""
Estabilidad absoluta.  Aplicando un esquema al problema test  dU/dt = lambda U  se obtiene
        U_{n+1} = R(z) U_n,        z = lambda dt
R(z) es la FUNCION DE ESTABILIDAD: el numero por el que el esquema multiplica la solucion en cada paso.
Region de estabilidad absoluta:  { z : |R(z)| <= 1 }.
Se acepta el esquema como funcion (Euler) o como texto ("Euler").
"""
from numpy import sqrt, where, abs, exp, meshgrid


def stability_function(method, z):
    from types import FunctionType
    from numpy import asarray, zeros_like, ones_like, errstate
    from active.numerical_engine import temporal_schemes

    name = method if isinstance(method, str) else getattr(method, "__name__", "")
    if name == "Leap_Frog":  # Dos pasos: no tiene un unico factor obtenido con un paso.
        s = sqrt(z**2 + 1 + 0j)
        r1, r2 = z + s, z - s
        return where(abs(r1) >= abs(r2), r1, r2)

    if isinstance(method, str):
        name = "Euler_implicit" if name == "Inverse_Euler" else name
        if name not in ("Euler", "Euler_implicit", "Crank_Nicolson", "RK4"):
            raise ValueError(f"Esquema desconocido: {name}")
        method = getattr(temporal_schemes, name)

    z = asarray(z, dtype=complex)

    # El problema test es lineal: su residuo implicito es afin. Se resuelve
    # con dos evaluaciones, sin formulas de R(z), para toda la malla a la vez.
    # Esta adaptacion local admite complejos y la llamada con tres argumentos
    # de Crank-Nicolson, sin cambiar Newton ni los esquemas del proyecto.
    def solve_test_residual(G, U0, *args):
        zero = zeros_like(U0, dtype=complex)
        g0 = G(zero)
        return -g0 / (G(ones_like(zero)) - g0)

    if method in (temporal_schemes.Euler_implicit, temporal_schemes.Crank_Nicolson):
        method = FunctionType(method.__code__,
                              dict(method.__globals__, Newton=solve_test_residual),
                              method.__name__, method.__defaults__, method.__closure__)

    # Como el profesor: u0 = 1, dt = 1, F(u,t) = z*u; el paso devuelve R(z).
    with errstate(divide="ignore", invalid="ignore"):
        result = method(U=ones_like(z), dt=1., t=0., F=lambda U, t: z * U)
    return result.item() if z.ndim == 0 else result


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
