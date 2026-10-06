# Física del problema de Kepler

Aquí van el campo F(U, t) = [ṙ, −r/|r|³], su Jacobiano y los cálculos de energía y momento angular. El problema es plano y adimensional (μ = 1), con estado U = (x, y, vx, vy). No se integra ni se dibujan gráficas aquí.

| Archivo | Qué contiene |
|---|---|
| `ecuaciones_kepler.py` | `kepler_rhs(U, t)`: la función F del problema de Cauchy. |
| `invariantes.py` | `specific_energy(U)`, `angular_momentum(U)` y `kepler_jacobian(U, t)`. |

La energía y el momento angular aceptan un estado `(4,)` o una trayectoria `(N+1, 4)` guardada como `U[n, :]`.
