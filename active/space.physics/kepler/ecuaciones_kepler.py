"""Ecuaciones del problema de Kepler plano y adimensional (μ = 1)."""

from numpy import asarray, concatenate
from numpy.linalg import norm


def kepler_rhs(U, t=0.0):
    """Devuelve F(U, t) = [ṙ, −r/|r|³] para el estado U = (x, y, vx, vy).

    Es el segundo miembro del problema de Cauchy dU/dt = F(U, t), así que se
    pasa tal cual a un esquema temporal. El campo es autónomo: t no se usa y
    solo está en la firma para respetar la interfaz F(U, t).

    U es un único estado (4,), no una trayectoria. El campo no está definido
    en r = 0: ahí numpy devuelve inf/nan con un aviso.
    """
    U = asarray(U, dtype=float)
    r, v = U[0:2], U[2:4]
    return concatenate((v, -r / norm(r)**3))
