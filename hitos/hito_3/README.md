# Enunciado

**Milestone 3: Error estimation of numerical solutions.**

1. Write a function to evaluate errors of numerical integration by means of Richardson extrapolation. This function should be based on the Cauchy problem solution implemented in milestone 2.
2. Numerical error for different temporal schemes: Euler, Inverse Euler, Crank Nicolson and fourth order Runge Kutta method.
3. Write a function to evaluate the convergence rate of different temporal schemes.
4. Convergence rate of the different methods with the time step.

## Ejecucion

Desde la raiz del repositorio:

```text
python -m hitos.hito_3.Error_Convergencia
```

La primera ventana compara el error de Richardson frente al tiempo. Al cerrarla,
se muestran cuatro paneles de log10(error) frente a log10(N), con el tramo
ajustado en rojo, y se imprimen las pendientes y los ordenes observados.

Se usa el oscilador con U0 = (1, 0), tf = 2*pi y N = 200 intervalos.
Para convergencia se empieza en N = 10 y se comparan diez mallas hasta N = 5120.
En `PruebaConvergencia`, `inicio=4` y `fin=8` seleccionan los puntos con
N = 160, 320, 640 y 1280. Los indices empiezan en cero y fin no se incluye.
Se debe mirar la grafica y cambiar ese tramo si deja de ser aproximadamente recto.
Los calculos reutilizables estan en `active/numerical_engine/Cauchy_Problem.py`.
