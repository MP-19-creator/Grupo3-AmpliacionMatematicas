from numpy import array, zeros, max, dot

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

        # Calcular las incognitas desde la ultima fila hacia arriba
        for i in range(nv-1, -1, -1):
            U[i] = (b[i] - dot(A[i, i:nv], U[i:nv])) / A[i, i]

        return U

def intercambiar_filas(A, b, k, nv):
    maximos = zeros(nv)

    # Mayor valor absoluto de la parte restante de cada fila
    for i in range(k, nv):
        maximos[i] = max(abs(A[i, k:nv]))

        # Comparar el valor de la columna k con el maximo de su fila
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
