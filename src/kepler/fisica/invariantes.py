"""Magnitudes conservadas y Jacobiano del campo de Kepler."""

from numpy import asarray, sqrt, zeros


def specific_energy(U):
    """Calcula E = |v|²/2 − 1/|r|.

    Admite un estado (4,) o una trayectoria (N+1, 4) guardada como U[n, :];
    devuelve un escalar o un vector (N+1,), respectivamente.
    """
    U = asarray(U, dtype=float)
    x, y, vx, vy = U[..., 0], U[..., 1], U[..., 2], U[..., 3]
    return (vx**2 + vy**2) / 2 - 1 / sqrt(x**2 + y**2)


def angular_momentum(U):
    """Calcula h = x·vy − y·vx (componente z de r × v).

    Admite un estado (4,) o una trayectoria (N+1, 4), igual que
    specific_energy. Conserva el signo: h > 0 es giro antihorario.
    """
    U = asarray(U, dtype=float)
    x, y, vx, vy = U[..., 0], U[..., 1], U[..., 2], U[..., 3]
    return x * vy - y * vx


def kepler_jacobian(U, t=0.0):
    """Devuelve el Jacobiano analítico ∂F/∂U (4x4) del campo de Kepler.

    Por bloques 2x2 es J = [[0, I], [G, 0]], con G = (3 r rᵀ − |r|² I)/|r|⁵.
    Solo depende de la posición; t no se usa, igual que en kepler_rhs.

    U es un único estado (4,). Como el campo, no está definido en r = 0.
    """
    U = asarray(U, dtype=float)
    x, y = U[0], U[1]
    r2 = x**2 + y**2
    r5 = r2**2.5

    J = zeros((4, 4))
    J[0, 2] = 1
    J[1, 3] = 1
    J[2, 0] = (3 * x**2 - r2) / r5
    J[2, 1] = 3 * x * y / r5
    J[3, 0] = 3 * x * y / r5
    J[3, 1] = (3 * y**2 - r2) / r5
    return J
