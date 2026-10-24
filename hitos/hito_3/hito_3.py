from active.numerical_engine.Errores_Convergencia import partition, error_richardson, orden_convergencia
from active.numerical_engine.Temporal_Schemes import Euler, Euler_implicit, Crank_Nicolson, RK4
from active.space_physics.oscilador import oscilador
from numpy import array, zeros, pi, log10, polyfit
from numpy.linalg import norm
import matplotlib.pyplot as plt

def PruebaError(tf, N, U0, F):
    t = partition(0, tf, N)
    schemes = [(Euler, 1), (Euler_implicit, 1), (Crank_Nicolson, 2), (RK4, 4)]
    plt.figure()

    for method, orden in schemes:
        U, error = error_richardson(F, t, U0, method, orden)
        errores = zeros(len(t))

        for i in range(0, len(t)):
            errores[i] = norm(error[i, :])

        # El error inicial es cero y no se representa en escala logaritmica
        plt.semilogy(t[1:], errores[1:], label=method.__name__)

    plt.xlabel('t')
    plt.ylabel('Norma del error estimado')
    plt.title('Error por Richardson')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.show()

def PruebaConvergencia(tf, N, U0, F, refinamientos=10, inicio=4, fin=8):
    t = partition(0, tf, N)
    schemes = [(Euler, 1), (Euler_implicit, 1), (Crank_Nicolson, 2), (RK4, 4)]
    plt.figure(figsize=(11, 8))

    for i, (method, orden) in enumerate(schemes):
        intervalos, errores, orden_observado = orden_convergencia(F, t, U0, method, refinamientos, inicio, fin)
        print(method.__name__, ': pendiente =', -orden_observado, ', orden observado =', orden_observado,
              ', orden teorico =', orden, ', tramo N =', intervalos[inicio:fin])
        plt.subplot(2, 2, i+1)
        validos = errores > 0
        plt.plot(log10(intervalos[validos]), log10(errores[validos]), 'o-', label='Todas las mallas')
        x = log10(intervalos[inicio:fin])
        y = log10(errores[inicio:fin])
        # Dibujar la recta sobre los mismos puntos usados para medir el orden
        pendiente, b = polyfit(x, y, 1)
        plt.plot(x, y, 'ro', label='Tramo elegido')
        plt.plot(x, pendiente*x + b, 'r--', label=f'Pendiente {pendiente:.3f}')

        plt.xlabel('log10(N)')
        plt.ylabel('log10(error estimado en tf)')
        plt.title(f'{method.__name__}: orden {orden_observado:.3f}')
        plt.legend()
        plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    PruebaError(tf=2*pi, N=200, U0=array([1., 0.]), F=oscilador)
    PruebaConvergencia(tf=2*pi, N=10, U0=array([1., 0.]), F=oscilador)