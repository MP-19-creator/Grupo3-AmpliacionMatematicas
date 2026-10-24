from numpy import array, zeros, log10, polyfit, isfinite
from numpy.linalg import norm

def partition(a, b, N):
    """Devuelve N+1 puntos equiespaciados entre a y b, con N segmentos."""
    return array([a + i*(b-a)/N for i in range(0, N+1)])

def Cauchy_problem(F, t, U0, method):
    n = len(t) - 1
    nv = len(U0)

    U = zeros((n+1, nv))
    U[0,:] = U0

    for i in range(0, n):
        dt = t[i+1] - t[i]
        U[i+1,:] = method(U[i,:], dt, t[i], F)
        
    return U

def error_richardson(F, t, U0, method, orden=None):
    """Integra sobre una malla uniforme t y estima el error U - U_exacta.

    Con orden indicado devuelve U y el error estimado en los instantes de t.
    Sin orden devuelve U y la diferencia U - U2, para medir primero el orden.
    """
    N = len(t) - 1
    nv = len(U0)
    t2 = partition(t[0], t[N], 2*N)

    U = Cauchy_problem(F, t, U0, method)
    U2 = Cauchy_problem(F, t2, U0, method)
    error = zeros((N+1, nv))

    # Comparar las soluciones en los mismos instantes
    for i in range(0, N+1):
        error[i, :] = U[i, :] - U2[2*i, :]

    if orden is not None:
        error = error / (1 - 1/2**orden)

    return U, error

def orden_convergencia(F, t, U0, method, refinamientos=10, inicio=4, fin=8):
    """Ajusta log(diferencia) frente a log(N) en el tramo [inicio:fin].

    Devuelve intervalos, errores de Richardson y orden observado.
    El tramo se elige mirando la zona recta de la grafica; fin no se incluye.
    El orden se obtiene de las diferencias, antes de corregir los errores.
    """
    if not 0 <= inicio < fin <= refinamientos or fin - inicio < 2:
        raise ValueError("Elegir un tramo con al menos dos puntos dentro de las mallas calculadas")

    N = len(t) - 1
    intervalos = zeros(refinamientos)
    errores = zeros(refinamientos)

    for i in range(0, refinamientos):
        t2 = partition(t[0], t[-1], N)
        U, error = error_richardson(F, t2, U0, method)
        intervalos[i] = N
        errores[i] = norm(error[-1, :])
        N = 2*N

    if not all(isfinite(errores)):
        raise ValueError("Los errores deben ser finitos para calcular el orden")

    if any(errores[inicio:fin] <= 1e-12):
        raise ValueError("El tramo elegido contiene errores demasiado pequenos; elegir otro tramo")

    pendiente, b = polyfit(log10(intervalos[inicio:fin]), log10(errores[inicio:fin]), 1)
    orden_observado = -pendiente
    if orden_observado <= 0:
        raise ValueError("El error no disminuye en el tramo elegido; revisar la grafica")

    # Aplicar Richardson una vez medido el orden
    errores = errores / (1 - 1/2**orden_observado)
    return intervalos, errores, orden_observado
