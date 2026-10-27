from numpy import zeros, array, isfinite
from numpy.linalg import norm

# def Cauchy_problem(F, t, U0, method):
#     n = len(t) - 1
#     nv = len(U0)

#     U = zeros((n+1, nv))
#     U[0,:] = U0

#     for i in range(0, n):
#         dt = t[i+1] - t[i]
#         U[i+1,:] = method(U[i,:], dt, t[i], F)
        
#     return U

# class Integration_stopped(ArithmeticError):
#     """
#     The integration cannot go on at step n (non finite solution or Newton
#     did not converge). U_partial keeps the solution computed so far.
#     """
#     def __init__(self, n, U_partial, cause):
#         super().__init__(f"Integration stopped at step {n}: {cause}")
#         self.n = n
#         self.U_partial = U_partial

"""
Problema de Cauchy  dU/dt = F(U, t),  U(t0) = U0.  No sabe que problema integra: solo ve F(U, t).

  Cauchy_problem           paso FIJO en la malla t que se le da
  Cauchy_problem_adaptive  paso ADAPTATIVO: el propio algoritmo elige la malla con la estimacion de
                           error de Richardson (doblado de paso)
"""

class Integration_stopped(ArithmeticError):
    """
    La integracion no puede seguir en el paso n (solucion no finita, Newton no converge o demasiados pasos).
    U_partial y t_partial guardan lo calculado hasta ese momento.
    """
    def __init__(self, n, U_partial, cause, t_partial=None):
        super().__init__(f"Integration stopped at step {n}: {cause}")
        self.n = n
        self.U_partial = U_partial
        self.t_partial = t_partial


def Cauchy_problem(F, t, U0, method):
    """ Integra en la malla t (no tiene por que ser uniforme).  Devuelve U[n, :] de tamano (N+1, nv) """
    N = len(t) - 1
    U = zeros((N+1, len(U0)))
    U[0, :] = U0
    if hasattr(method, "start"):                     # esquemas multipaso (Leap-Frog): borrar la memoria
        method.start()

    for n in range(N):
        dt = t[n+1] - t[n]
        try:
            U[n+1, :] = method(U[n, :], dt, t[n], F)
        except ArithmeticError as e:                 # Newton_failed, ZeroDivisionError, ...
            raise Integration_stopped(n, U[:n+1].copy(), e, t[:n+1]) from e
        if not isfinite(U[n+1, :]).all():
            raise Integration_stopped(n, U[:n+1].copy(), "non finite solution", t[:n+1])
    return U

def Cauchy_problem_adaptive(F, tf, U0, method, tol=1e-8, dt0=1e-2, t0=0., max_steps=50000):
    """
    Paso ADAPTATIVO por doblado de paso = extrapolacion de Richardson aplicada a UN paso:
        U1 = un paso de tamano dt        U2 = dos pasos de tamano dt/2
        error local de U2  ~  |U2 - U1| / (2^q - 1)          (q = method.order)
    Se acepta si error <= tol (1 + |U2|).  El paso siguiente es  dt * 0.9 (tol/error)^(1/(q+1)),
    limitado entre 0.2 dt y 2 dt.   Devuelve (t, U) con la malla que ha elegido el algoritmo.
    """
    q = method.order
    t, U, dt = t0, array(U0, dtype=float), dt0
    t_list, U_list = [t], [U]

    for n in range(max_steps):
        if t >= tf - 1e-12 * max(1., abs(tf)):
            return array(t_list), array(U_list)
        dt = min(dt, tf - t)
        try:
            U1 = method(U, dt, t, F)
            U2 = method(method(U, dt/2, t, F), dt/2, t + dt/2, F)
        except ArithmeticError as e:
            raise Integration_stopped(n, array(U_list), e, array(t_list)) from e
        if not (isfinite(U1).all() and isfinite(U2).all()):
            raise Integration_stopped(n, array(U_list), "non finite solution", array(t_list))

        error = norm(U2 - U1) / (2**q - 1)
        scale = tol * (1 + norm(U2))
        if error <= scale:                           # paso aceptado: nos quedamos con U2 (el mejor)
            t, U = t + dt, U2
            t_list.append(t)
            U_list.append(U)
        factor = 2.0 if error == 0 else min(2.0, max(0.2, 0.9 * (scale / error)**(1/(q + 1))))
        dt = dt * factor

    raise Integration_stopped(max_steps, array(U_list), f"more than {max_steps} steps", array(t_list))