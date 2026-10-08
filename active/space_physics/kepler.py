from numpy import array

def Kepler(U, t):

    x = U[0]
    y = U[1]
    vx = U[2]
    vy = U[3]

    r = (x**2 + y**2)**1.5

    return array([
        vx,
        vy,
        -x/r,
        -y/r
    ])
