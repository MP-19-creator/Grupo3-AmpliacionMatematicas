from numpy import array, zeros, max, dot
from numpy.linalg import norm

def Newton(F, U0):
    i = 0
    n = 1000
    # Trabajar con una copia decimal sin modificar el estado inicial
    U = array(U0, dtype=float)

    # Iterar mientras U no satisfaga el sistema F(U) = 0
    while norm(F(U)) > 1e-10 and i < n:
        i = i + 1
        J = Jacobian(F, U)
        b = -F(U)
        cambio = Gauss(J, b)
        U[:] = U[:] + cambio

    if not norm(F(U)) <= 1e-10:
        raise RuntimeError("Newton no ha encontrado una solucion con la tolerancia indicada")

    return U

def Jacobian(F, U):
    dt = 1e-3
    nv = len(U)
    cambio = zeros(nv)
    J = zeros((nv, nv))

    for i, _ in enumerate(U):
        cambio[:] = 0
        cambio[i] = dt
        J[:, i] = (F(U + cambio) - F(U - cambio)) / (2*dt)

    return J

def Gauss(A, b):
    nv = len(b)
    U = zeros(nv)

    # Convertir en ceros los elementos por debajo de la diagonal
    for k, _ in enumerate(A):
        intercambiar_filas(A, b, k, nv)

        # Restar un multiplo de la fila k a las filas inferiores
        for i in range(k+1, nv):
            factor = A[i, k] / A[k, k]
            A[i, k:nv] = A[i, k:nv] - factor * A[k, k:nv]
            b[i] = b[i] - factor * b[k]

    # Calcular las incognitas cuando la matriz ya es triangular
    for i in range(nv-1, -1, -1):
        U[i] = (b[i] - dot(A[i, i:nv], U[i:nv])) / A[i, i]

    return U

def intercambiar_filas(A, b, k, nv):
    maximos = zeros(nv)

    # Mayor valor absoluto de la parte restante de cada fila
    for i in range(k, nv):
        maximos[i] = max(abs(A[i, k:nv]))

    # Comparar cuando ya se han calculado todos los maximos
    mayor = abs(A[k, k] / maximos[k])
    fila = k
    for j in range(k, nv):
        if abs(A[j, k] / maximos[j]) > mayor:
            mayor = abs(A[j, k] / maximos[j])
            fila = j

    # Comprobar si se puede continuar resolviendo el sistema
    if mayor == 0.0:
        print("La matriz no permite obtener una solucion unica")
        exit()

    # Colocar la fila elegida en la posicion k
    if fila != k:
        A[[k, fila], k:nv] = A[[fila, k], k:nv]
        (b[k], b[fila]) = (b[fila], b[k])

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
