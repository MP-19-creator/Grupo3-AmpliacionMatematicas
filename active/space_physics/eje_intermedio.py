from numpy import array, cos, pi, sign, sin, sqrt, zeros
from numpy import concatenate, outer, ones
from active.numerical_engine.Errores_Convergencia import partition

# Campo de Euler F(ω, t) = [(I2−I3)/I1·ω2·ω3, (I3−I1)/I2·ω3·ω1, (I1−I2)/I3·ω1·ω2]
def PEI1(I, U, t):
    I1, I2, I3 = I
    
    w1 = U[0]
    w2 = U[1]
    w3 = U[2]

    return array([(I2 - I3) / I1 * w2 * w3,
                  (I3 - I1) / I2 * w3 * w1,
                  (I1 - I2) / I3 * w1 * w2])

# Jacobiano ∂F/∂ω
def euler_jacobian(I,U,t):
    I1, I2, I3 = I
    w1 = U[0]; w2 = U[1]; w3 = U[2]
    J = zeros((3, 3))   
    J[0, 1] = (I2 - I3)/I1 * w3;   J[0, 2] = (I2 - I3)/I1 * w2
    J[1, 0] = (I3 - I1)/I2 * w3;   J[1, 2] = (I3 - I1)/I2 * w1
    J[2, 0] = (I1 - I2)/I3 * w2;   J[2, 1] = (I1 - I2)/I3 * w1
    return J

# --------- INVARIANTES ---------
# Doble de la energía cinética 2T = I1·ω1² + I2·ω2² + I3·ω3²
def Kinetic_energy_2T(U, I):
    I1, I2, I3 = I
    w1 = U[..., 0]; w2 = U[..., 1]; w3 = U[..., 2]
    return I1 * w1**2 + I2 * w2**2 + I3 * w3**2

# Momento angular al cuadrado L² = I1²·ω1² + I2²·ω2² + I3²·ω3²
def Angular_momentum_L2(U, I):
    I1, I2, I3 = I
    w1 = U[..., 0]; w2 = U[..., 1]; w3 = U[..., 2]
    return I1**2 * w1**2 + I2**2 * w2**2 + I3**2 * w3**2

# ---------- INVARIANTES ---------
def Quaternion_product(p, q):

    p0, p1, p2, p3 = p
    q0, q1, q2, q3 = q
    return array( [ p0*q0 - p1*q1 - p2*q2 - p3*q3,
                    p0*q1 + p1*q0 + p2*q3 - p3*q2,
                    p0*q2 - p1*q3 + p2*q0 + p3*q1,
                    p0*q3 + p1*q2 - p2*q1 + p3*q0 ] )


def Attitude_equations(U, t, I):
    """ dw/dt = Euler equations,  dq/dt = 1/2 q (x) (0, w)   (q: body -> inertial) """
    w = U[0:3]; q = U[3:7]
    return concatenate( ( PEI1(I, w, t), 0.5 * Quaternion_product(q, (0., *w)) ) )


def Attitude_jacobian(U, t, I):

    w1, w2, w3 = U[0:3]
    q0, q1, q2, q3 = U[3:7]
    J = zeros((7, 7))
    J[0:3, 0:3] = euler_jacobian(I, U, t)
    J[3:7, 0:3] = 0.5 * array( [ [-q1, -q2, -q3],
                                 [ q0, -q3,  q2],
                                 [ q3,  q0, -q1],
                                 [-q2,  q1,  q0] ] )
    J[3:7, 3:7] = 0.5 * array( [ [0., -w1, -w2, -w3],
                                 [w1,  0.,  w3, -w2],
                                 [w2, -w3,  0.,  w1],
                                 [w3,  w2, -w1,  0.] ] )
    return J


def Rotation_matrix(q):
    """ R(q): body -> inertial (q is normalized only to use it) """
    q0, q1, q2, q3 = array(q) / sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
    return array( [ [1 - 2*(q2*q2 + q3*q3), 2*(q1*q2 - q0*q3),     2*(q1*q3 + q0*q2)],
                    [2*(q1*q2 + q0*q3),     1 - 2*(q1*q1 + q3*q3), 2*(q2*q3 - q0*q1)],
                    [2*(q1*q3 - q0*q2),     2*(q2*q3 + q0*q1),     1 - 2*(q1*q1 + q2*q2)] ] )


def Inertial_angular_momentum(U, I):
    """ L = R(q) I w : a CONSTANT vector (not only its modulus) """
    return Rotation_matrix(U[3:7]) @ ( array(I) * U[0:3] )


def Rigid_body_problem(I, attitude=True):
    """ Closure F(U, t) with its exact Jacobian as attribute F.jacobian """
    if attitude:
        def F(U, t): return Attitude_equations(U, t, I)
        F.jacobian = lambda U, t: Attitude_jacobian(U, t, I)
    else:
        def F(U, t): return PEI1(I, U, t)
        F.jacobian = lambda U, t: euler_jacobian(I, U, t)
    return F


# ------------------------------------------------------------ equilibria and linear stability
def Initial_condition(axis, Omega, eps, attitude=True):
    """ w0 = Omega e_axis + eps*Omega in the other two components; q0 = identity """
    w0 = eps * Omega * ones(3)
    w0[axis] = Omega
    return concatenate( (w0, [1., 0., 0., 0.]) ) if attitude else w0


def Linear_eigenvalues(I, axis, Omega):
    """ Non zero eigenvalues of J at w* = Omega e_axis, equations (9), (10), (12) """
    I1, I2, I3 = I
    lambda2 = { 0: (I3 - I1)*(I1 - I2)/(I2*I3),
                1: (I2 - I3)*(I1 - I2)/(I1*I3),
                2: (I2 - I3)*(I3 - I1)/(I1*I2) }[axis] * Omega**2
    lam = sqrt(complex(lambda2))
    return array([lam, -lam])


# ------------------------------------------------------------ Poinsot geometry
def Ellipsoid(semiaxes, n=30):
    u = partition(0, 2*pi, n); v = partition(0, pi, n//2)
    return ( semiaxes[0]*outer(cos(u), sin(v)),
             semiaxes[1]*outer(sin(u), sin(v)),
             semiaxes[2]*outer(ones(n+1), cos(v)) )


def Energy_ellipsoid(I, T2, n=30):
    return Ellipsoid( sqrt(T2 / array(I)), n )


def Momentum_ellipsoid(I, L2, n=30):
    return Ellipsoid( sqrt(L2) / array(I), n )


def Separatrix(I, T2, n=200):
    """
    Polhodes with L^2 = 2 T I2. Subtracting I2*2T from L^2:
        I1 (I1 - I2) w1^2 + I3 (I3 - I2) w3^2 = 0   ->   w3 = +- c w1
    Two planes; each one cuts the energy ellipsoid along an ellipse.
    """
    I1, I2, I3 = I
    c = sqrt( I1*(I2 - I1) / (I3*(I3 - I2)) )
    s = partition(0, 2*pi, n)
    w1 = sqrt( T2/(I1 + I3*c**2) ) * cos(s)
    w2 = sqrt( T2/I2 ) * sin(s)
    return [ array([w1, w2, c*w1]), array([w1, w2, -c*w1]) ]


def Side_of_separatrix(I, T2, L2):
    """ +1: the polhode goes around I3,  -1: around I1,  0: separatrix """
    return int( sign( round( (L2 - I[1]*T2) / (I[1]*T2), 12 ) ) )


def Polhode_period(I, T2, L2):
    """
    Exact period of w(t) (Landau-Lifshitz, section 37):  P = 4 K(k) / nu
    L^2 > 2T I2:  k^2 = (I2-I1)(2T I3 - L^2) / ((I3-I2)(L^2 - 2T I1)),
                  nu  = sqrt( (I3-I2)(L^2 - 2T I1) / (I1 I2 I3) )
    L^2 < 2T I2:  I1 and I3 swap roles.   On the separatrix P = infinity.
    """
    I1, I2, I3 = I
    side = Side_of_separatrix(I, T2, L2)
    if side == 0:
        return float("inf")
    if side > 0:
        k2 = (I2 - I1)*(I3*T2 - L2) / ((I3 - I2)*(L2 - I1*T2))
        nu = sqrt( (I3 - I2)*(L2 - I1*T2) / (I1*I2*I3) )
    else:
        k2 = (I3 - I2)*(L2 - I1*T2) / ((I2 - I1)*(I3*T2 - L2))
        nu = sqrt( (I2 - I1)*(I3*T2 - L2) / (I1*I2*I3) )
    return 4 * Elliptic_K(k2) / nu


def Elliptic_K(m):
    """ K(m) = pi / (2 AGM(1, sqrt(1 - m))),  0 <= m < 1 """
    a, g = 1.0, sqrt(1 - m)
    while abs(a - g) > 1e-15 * a:
        a, g = (a + g)/2, sqrt(a*g)
    return pi / (2*a)


# ------------------------------------------------------------ physical body
def Is_physical(I):
    """ A real body satisfies I1 + I2 >= I3 """
    return I[0] + I[1] >= I[2] * (1 - 1e-12)


def Box_dimensions(I, m=1.):
    """ Sides of the homogeneous box with inertias I: a^2 = 6 (I2 + I3 - I1)/m ... """
    I1, I2, I3 = I
    return sqrt( (6/m * array([I2 + I3 - I1, I1 + I3 - I2, I1 + I2 - I3])).clip(min=0) )