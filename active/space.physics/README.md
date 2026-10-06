# Capa física (`space.physics`)

Aquí se define el problema: el campo F(U, t), su Jacobiano y las magnitudes que se conservan. No se integra ni se dibujan gráficas aquí.

Hay dos problemas, y se hacen en este orden:

| Carpeta | Problema | Para qué |
|---|---|---|
| [`kepler/`](kepler/) | Órbita de Kepler | Es el primero. Lo piden los hitos del curso y sirve para probar el motor numérico con un problema conocido. |
| [`eje_intermedio/`](eje_intermedio/) | Rotación libre del sólido rígido | Es la física de la PEI 1. |

Los dos se escriben igual, como una función F(U, t), para que el mismo motor numérico integre cualquiera de ellos.

## Kepler

Campo F(U, t) = [ṙ, −r/|r|³]. El problema es plano y adimensional (μ = 1), con estado U = (x, y, vx, vy).

| Archivo | Qué contiene |
|---|---|
| `kepler/ecuaciones_kepler.py` | `kepler_rhs(U, t)`: la función F del problema de Cauchy. |
| `kepler/invariantes.py` | `specific_energy(U)`, `angular_momentum(U)` y `kepler_jacobian(U, t)`. |

La energía y el momento angular aceptan un estado `(4,)` o una trayectoria `(N+1, 4)` guardada como `U[n, :]`.
