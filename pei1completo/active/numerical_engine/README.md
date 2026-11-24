# Motor numérico (`numerical_engine`)

Aquí van los métodos que avanzan la solución en el tiempo y los cálculos de error y estabilidad. No hay nada de física: todo recibe una función F(U, t) cualquiera, así que sirve igual para Kepler que para el sólido rígido.

Según el enunciado de la PEI 1, esta capa debe tener:

- Esquemas temporales de paso simple y adaptativo (Euler, Crank-Nicolson, RK4).
- Estimación del error por extrapolación de Richardson.
- Regiones de estabilidad numérica \|R(z)\| ≤ 1.

## Qué hay ahora

| Archivo | Qué contiene |
|---|---|
| [`temporal_schemes.py`](temporal_schemes.py) | Los esquemas de un paso y las funciones de error y estabilidad (estas últimas, sin escribir). |
| [`Cauchy_Problem.py`](Cauchy_Problem.py) | El integrador que aplica un esquema durante todo el intervalo. |

### Esquemas de un paso

Todos reciben `(U, dt, t, F)` y devuelven el estado en t + dt.

| Función | Qué hace |
|---|---|
| `Euler` | Euler explícito. |
| `Euler_implicit` | Euler implícito (inverso). |
| `RK4` | Runge-Kutta de orden 4. |
| `Crank_Nicolson` | Crank-Nicolson. |

### `Cauchy_problem(F, t, U0, method)`

Integra dU/dt = F(U, t) con U(t[0]) = U0.

- `F` es el campo, `t` el vector de instantes, `U0` la condición inicial y `method` uno de los esquemas de arriba.
- Devuelve la trayectoria `U[n, :]`, de tamaño `(N+1, nv)`, con N+1 = `len(t)`.
- El paso se calcula en cada tramo como `t[i+1] - t[i]`, así que la malla no tiene que ser uniforme.

```python
t = linspace(0, 6*pi, 10000)
U = Cauchy_problem(Kepler, t, array([1, 0, 0, 1]), RK4)
```

### Cómo se resuelven los esquemas implícitos

`Euler_implicit` y `Crank_Nicolson` tienen que despejar el estado nuevo Y de una ecuación no lineal. Ahora se hace con una iteración de punto fijo:

```text
Euler implícito:   Y ← U + dt·F(Y, t + dt)
Crank-Nicolson:    Y ← U + dt/2·[F(U, t) + F(Y, t + dt)]
```

- El valor inicial de Y es un paso de Euler explícito.
- Se itera mientras la norma del residuo sea mayor que 1e-6. La tolerancia es absoluta.
- No hay número máximo de iteraciones.

## Limitaciones conocidas de los esquemas implícitos

Comprobadas ejecutando el código. ρ(J) es el mayor módulo de los autovalores del Jacobiano de F.

| Caso | Qué ocurre |
|---|---|
| Paso grande | El punto fijo solo converge si dt·ρ(J) < 1 (dt·ρ(J)/2 < 1 en Crank-Nicolson). Fuera de ahí la función devuelve `nan` o no termina. Con dU/dt = −50·U, `Euler_implicit` no termina para dt = 0.02 y devuelve `nan` para dt entre 0.03 y 0.1. |
| Paso pequeño | Si el paso de Euler explícito inicial ya cumple la tolerancia, no se itera y la función devuelve ese paso. En Kepler circular ocurre aproximadamente para dt < 1.2e-3 en `Crank_Nicolson` y dt < 8.4e-4 en `Euler_implicit`. Con tf = 6π, `Crank_Nicolson` da exactamente lo mismo que `Euler` con N = 16000, y `Euler_implicit` con N = 32000. |
| Kepler con paso grande | Con `Euler_implicit` la órbita pierde energía y cae hacia r = 0, donde el punto fijo deja de converger. Con tf = 6π se queda atascado con N = 1000 y con N = 2000. |

Consecuencias:

- No se puede mostrar la estabilidad de Euler implícito y Crank-Nicolson con pasos grandes (hito 4).
- El orden de convergencia medido se estropea al reducir el paso (hito 3).
- `hitos/hito_2/Orbita_Kepler.py` funciona con N = 10000 porque ese paso queda entre los dos límites.

## Declarado pero sin escribir

Están en `temporal_schemes.py` y lanzan `NotImplementedError`:

| Función | Qué hará |
|---|---|
| `richardson_error` | Estimar el error comparando dos soluciones con pasos distintos. |
| `convergence_order` | Estimar el orden del método a partir de varios pasos y sus errores. |
| `stability_function` | Evaluar R(z) de cada método. |
| `is_absolutely_stable` | Decir si se cumple \|R(z)\| ≤ 1. |

## Qué falta

- Resolver los esquemas implícitos con el método de Newton, con una tolerancia más estricta y un número máximo de iteraciones.
- El paso adaptativo.
- Leap-Frog, que pide el hito 4. Es un método de dos pasos y no encaja en la firma `(U, dt, t, F)`.
- El hito 2 pide que el Euler implícito se llame `Inverse_Euler`. Ahora se llama `Euler_implicit`.
