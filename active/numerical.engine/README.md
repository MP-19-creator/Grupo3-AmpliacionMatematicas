# Motor numérico (`numerical.engine`)

Aquí van los métodos que avanzan la solución en el tiempo y los cálculos de error y estabilidad. No hay nada de física: todo recibe una función F(U, t) cualquiera, así que sirve igual para Kepler que para el sólido rígido.

Según el enunciado de la PEI 1, esta capa debe tener:

- Esquemas temporales de paso simple y adaptativo (Euler, Crank-Nicolson, RK4).
- Estimación del error por extrapolación de Richardson.
- Regiones de estabilidad numérica \|R(z)\| ≤ 1.

## Qué hay ahora

Todo está en el archivo `numerical_engine`.

Los esquemas dan un paso: reciben `(U, dt, t, F)` y devuelven el estado en t + dt.

| Función | Qué hace |
|---|---|
| `Euler` | Euler explícito. |
| `RK4` | Runge-Kutta de orden 4. |
| `CN2` | Crank-Nicolson con F(Uⁿ⁺¹) aproximado por un paso de Euler explícito, en vez de resolver la ecuación implícita. |

El resto está declarado pero sin escribir (lanza `NotImplementedError`):

| Función | Qué hará |
|---|---|
| `richardson_error` | Estimar el error comparando dos soluciones con pasos distintos. |
| `convergence_order` | Estimar el orden del método a partir de varios pasos y sus errores. |
| `stability_function` | Evaluar R(z) de cada método. |
| `is_absolutely_stable` | Decir si se cumple \|R(z)\| ≤ 1. |

## Qué falta

- La función que integra todo el intervalo aplicando un esquema paso a paso.
- El paso adaptativo.
- Euler inverso y Leap-Frog, que piden los hitos.
