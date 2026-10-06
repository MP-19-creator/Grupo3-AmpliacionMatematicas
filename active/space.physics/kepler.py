from numpy import asarray, concatenate, sqrt, zeros
from numpy.linalg import norm

# Campo de Kepler F(U, t) = [v, −r/|r|³]
def kepler_rhs(U, t=0.0):
    U = asarray(U, dtype=float)
    r, v = U[0:2], U[2:4]
    return concatenate((v, -r / norm(r)**3))

# Jacobiano ∂F/∂U
def kepler_jacobian(U, t=0.0):
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


# --------- INVARIANTES ---------

# Energía específica E = |v|²/2 − 1/|r|
def specific_energy(U):
    U = asarray(U, dtype=float)
    x, y, vx, vy = U[..., 0], U[..., 1], U[..., 2], U[..., 3]
    return (vx**2 + vy**2) / 2 - 1 / sqrt(x**2 + y**2)

# Momento angular h = x·vy − y·vx
def angular_momentum(U):
    U = asarray(U, dtype=float)
    x, y, vx, vy = U[..., 0], U[..., 1], U[..., 2], U[..., 3]
    return x * vy - y * vx