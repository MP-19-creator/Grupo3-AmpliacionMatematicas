from numpy import array, zeros

# Campo de Euler F(ω, t) = [(I2−I3)/I1·ω2·ω3, (I3−I1)/I2·ω3·ω1, (I1−I2)/I3·ω1·ω2]
def euler_rhs(I):
    I1, I2, I3 = I

    def F(U, t):
        w1 = U[0]; w2 = U[1]; w3 = U[2]
        return array([(I2 - I3) / I1 * w2 * w3,
                      (I3 - I1) / I2 * w3 * w1,
                      (I1 - I2) / I3 * w1 * w2])
    return F

# Jacobiano ∂F/∂ω
def euler_jacobian(I):
    I1, I2, I3 = I

    def J(U, t):
        w1 = U[0]; w2 = U[1]; w3 = U[2]

        M = zeros((3, 3))
        M[0, 1] = (I2 - I3) / I1 * w3
        M[0, 2] = (I2 - I3) / I1 * w2
        M[1, 0] = (I3 - I1) / I2 * w3
        M[1, 2] = (I3 - I1) / I2 * w1
        M[2, 0] = (I1 - I2) / I3 * w2
        M[2, 1] = (I1 - I2) / I3 * w1
        return M
    return J


# --------- INVARIANTES ---------

# Doble de la energía cinética 2T = I1·ω1² + I2·ω2² + I3·ω3²
def twice_kinetic_energy(U, I):
    I1, I2, I3 = I
    w1 = U[..., 0]; w2 = U[..., 1]; w3 = U[..., 2]
    return I1 * w1**2 + I2 * w2**2 + I3 * w3**2

# Momento angular al cuadrado L² = I1²·ω1² + I2²·ω2² + I3²·ω3²
def angular_momentum_squared(U, I):
    I1, I2, I3 = I
    w1 = U[..., 0]; w2 = U[..., 1]; w3 = U[..., 2]
    return I1**2 * w1**2 + I2**2 * w2**2 + I3**2 * w3**2