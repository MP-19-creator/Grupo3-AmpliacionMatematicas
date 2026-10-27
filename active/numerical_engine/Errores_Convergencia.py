from numpy import array, zeros, log10, polyfit, isfinite
from numpy.linalg import norm
from active.numerical_engine.Cauchy_Problem import Cauchy_problem

def partition(a, b, N):
    # Devuelve N+1 puntos equiespaciados entre a y b, con N segmentos.
    return array([a + i*(b-a)/N for i in range(0, N+1)])

def error_richardson(F, t, U0, method, orden=None):
    # Integra sobre una malla uniforme t y estima el error U - U_exacta. 
    # Con orden indicado devuelve U y el error estimado en los instantes de t. 
    # Sin orden devuelve U y la diferencia U - U2, para medir primero el orden.
    N = len(t) - 1
    nv = len(U0)
    t2 = partition(t[0], t[N], 2*N)

    U = Cauchy_problem(F, t, U0, method)
    U2 = Cauchy_problem(F, t2, U0, method)
    error = zeros((N+1, nv))

    # Comparar las soluciones en los mismos instantes
    for i in range(0, N+1):
        error[i, :] = (U[i, :] - U2[2*i, :])

    if orden is not None:
        error = error / (1 - 1/2**orden)

    return U, error

def orden_convergencia(F, t, U0, method, refinamientos=10, inicio=4, fin=8):
    # Ajusta log(diferencia) frente a log(N) en el tramo [inicio:fin].
    # Devuelve intervalos, errores de Richardson y orden observado.
    # El tramo se elige mirando la zona recta de la grafica; fin no se incluye.
    # El orden se obtiene de las diferencias, antes de corregir los errores.
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

# ---------------------------------------------------------------------------------------------
# Estudio de convergencia para la GUI (cualquier problema, en particular el solido rigido)
# ---------------------------------------------------------------------------------------------
def curva_convergencia(F, tf, U0, method, N0=40, niveles=8, t0=0.):
    """
    Richardson sin solucion exacta.  Para N_k = N0 2^k (k = 0..niveles-1):
        D_k = |U_{N_k}(tf) - U_{2 N_k}(tf)|          (diferencia entre la malla N y la malla 2N)
    Si el esquema es de orden q, el error de U_N es E_N ~ C dt^q y  D_k ~ C dt^q (1 - 2^-q),
    asi que  log D = -q log N + cte  (recta de pendiente -q)  y  E_N ~ D_k / (1 - 2^-q).
    Cada solucion se reutiliza: la malla 2N del nivel k es la malla N del nivel k+1 (niveles+1 integraciones).
    Devuelve N (niveles,) y D (niveles,).  Si una integracion falla, D vale nan desde ese nivel.
    """
    finales = []
    for k in range(niveles + 1):
        N = N0 * 2**k
        try:
            finales.append(Cauchy_problem(F, partition(t0, tf, N), U0, method)[-1])
        except ArithmeticError:
            finales.append(None)
    N = array([N0 * 2**k for k in range(niveles)])
    D = array([norm(finales[k] - finales[k+1]) if finales[k] is not None and finales[k+1] is not None
               else float("nan") for k in range(niveles)])
    return N, D


def ordenes_locales(D):
    """ p_k = log2(D_k / D_{k+1}):  al duplicar N el error se divide por 2^p.  Tiende al orden q """
    return log10(D[:-1] / D[1:]) / log10(2.)


def tramo_recto(N, D, suelo=1e-13, tolerancia=0.15):
    """
    Elige el tramo ASINTOTICO (recto) de log D frente a log N sin usar el orden teorico:
      - fuera los puntos no finitos o por debajo del suelo de redondeo (ahi D ya no puede bajar)
      - candidatos: tramos contiguos de 3 o mas puntos cuyos ordenes locales p_k casi no cambian
        (max p - min p <= 15 % de la mediana)
      - se queda con el que llega a las mallas mas finas (es el mas asintotico); si empatan, el mas largo
    Devuelve (indices, pendiente, ordenada) del ajuste por minimos cuadrados en ese tramo.
    """
    validos = [k for k in range(len(D)) if isfinite(D[k]) and D[k] > suelo]
    mejor = []
    for a in range(len(validos)):
        for b in range(a + 2, len(validos)):
            idx = validos[a:b+1]
            if idx[-1] - idx[0] != len(idx) - 1:                  # tiene que ser contiguo
                break
            p = sorted(ordenes_locales(D[idx]))
            mediana = p[len(p)//2]
            if mediana > 0 and p[-1] - p[0] <= tolerancia * mediana:
                if not mejor or idx[-1] > mejor[-1] or (idx[-1] == mejor[-1] and len(idx) > len(mejor)):
                    mejor = idx
    if len(mejor) < 2:                                            # nada recto: los ultimos puntos validos
        mejor = validos[-3:] if len(validos) >= 2 else list(range(len(D)))
    pendiente, ordenada = polyfit(log10(N[mejor]), log10(D[mejor]), 1)
    return array(mejor), pendiente, ordenada