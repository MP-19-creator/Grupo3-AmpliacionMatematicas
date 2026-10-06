# Capa física (`space.physics`)

Aquí se define el problema: el campo F(U, t), su Jacobiano y las magnitudes que se conservan. No se integra ni se dibujan gráficas aquí.

Hay dos problemas, y se hacen en este orden:

| Dónde | Problema | Para qué |
|---|---|---|
| [`kepler.py`](kepler.py) | Órbita de Kepler | Es el primero. Lo piden los hitos del curso y sirve para probar el motor numérico con un problema conocido. |
| [`eje_intermedio.py`](eje_intermedio.py) | Rotación libre del sólido rígido | Es la física de la PEI 1. |

Los dos se escriben igual, como una función F(U, t), para que el mismo motor numérico integre cualquiera de ellos.

## Kepler

El problema es plano y adimensional (μ = 1). El estado es U = (x, y, vx, vy), con r = (x, y) y v = (vx, vy).

Todo está en el archivo `kepler.py`.

| Función | Qué hace |
|---|---|
| `kepler_rhs(U, t)` | El campo F(U, t) del problema de Cauchy. |
| `kepler_jacobian(U, t)` | El Jacobiano analítico ∂F/∂U. |
| `specific_energy(U)` | La energía específica E. |
| `angular_momentum(U)` | El momento angular h. |

### `kepler_rhs(U, t)`

Devuelve el segundo miembro del problema de Cauchy dU/dt = F(U, t):

```text
F(U, t) = [ṙ, −r/|r|³] = (vx, vy, −x/|r|³, −y/|r|³)
```

- Se pasa tal cual a un esquema temporal.
- El campo es autónomo: `t` no se usa y solo está en la firma para respetar la interfaz F(U, t).
- `U` es un único estado `(4,)`, no una trayectoria.
- El campo no está definido en r = 0: ahí numpy devuelve inf/nan con un aviso.

### `kepler_jacobian(U, t)`

Devuelve el Jacobiano analítico ∂F/∂U, de tamaño 4x4. Por bloques 2x2:

```text
J = [ 0  I ]        G = (3 r rᵀ − |r|² I) / |r|⁵
    [ G  0 ]
```

- Solo depende de la posición; `t` no se usa, igual que en `kepler_rhs`.
- `U` es un único estado `(4,)`.
- Como el campo, no está definido en r = 0.

### `specific_energy(U)` y `angular_momentum(U)`

Son las dos magnitudes que se conservan:

```text
E = |v|²/2 − 1/|r|          energía específica
h = x·vy − y·vx             momento angular (componente z de r × v)
```

- Las dos aceptan un estado `(4,)` o una trayectoria `(N+1, 4)` guardada como `U[n, :]`, y devuelven un escalar o un vector `(N+1,)`, respectivamente.
- El momento angular conserva el signo: h > 0 es giro antihorario.

## Eje intermedio

Esta es la física de la PEI 1: la rotación libre de un satélite rígido, sin pares exteriores, en ejes principales de inercia con I₁ < I₂ < I₃. El estado es la velocidad angular en ejes cuerpo, U = ω = (ω₁, ω₂, ω₃).

El archivo `eje_intermedio.py` está vacío todavía. Ahí irán, igual que en `kepler.py`:

- El campo F(U, t), que son las ecuaciones de Euler:

  ```text
  dω₁/dt = (I₂ − I₃)/I₁ · ω₂ω₃
  dω₂/dt = (I₃ − I₁)/I₂ · ω₃ω₁
  dω₃/dt = (I₁ − I₂)/I₃ · ω₁ω₂
  ```

- El Jacobiano exacto J(ω).
- Las dos magnitudes que se conservan:

  ```text
  2T = I₁ω₁² + I₂ω₂² + I₃ω₃²          energía cinética de rotación
  L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²       módulo del momento angular
  ```

El Jacobiano completo y la estabilidad de los tres giros puros están en [`PEI1/README.md`](../../PEI1/README.md).
