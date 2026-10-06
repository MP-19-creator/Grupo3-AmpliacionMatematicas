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

Todo está en el archivo `eje_intermedio.py`.

| Función | Qué hace |
|---|---|
| `euler_rhs(I)` | Devuelve el campo F(U, t) de las ecuaciones de Euler. |
| `euler_jacobian(I)` | Devuelve el Jacobiano analítico J(U, t) = ∂F/∂U. |
| `twice_kinetic_energy(U, I)` | El doble de la energía cinética de rotación, 2T. |
| `angular_momentum_squared(U, I)` | El cuadrado del módulo del momento angular, L². |

### `euler_rhs(I)`

Recibe las inercias I = (I₁, I₂, I₃) y devuelve una función F(U, t) con el segundo miembro de dU/dt = F(U, t), es decir, las ecuaciones de Euler (ec. (2) del enunciado):

```text
dω₁/dt = (I₂ − I₃)/I₁ · ω₂ω₃
dω₂/dt = (I₃ − I₁)/I₂ · ω₃ω₁
dω₃/dt = (I₁ − I₂)/I₃ · ω₁ω₂
```

```python
F = euler_rhs((1.0, 2.0, 3.0))
dU = F(U, t)
```

- Las inercias entran por fábrica y no como argumento de F. Así F respeta la interfaz F(U, t) del motor numérico y los esquemas temporales no se tocan.
- Si cambian las inercias (por ejemplo, con los sliders de la GUI), se crea un F nuevo llamando otra vez a `euler_rhs`.
- El campo es autónomo: `t` no se usa y solo está en la firma para respetar la interfaz F(U, t). En el código tiene valor por defecto 0.0.
- `U` es un único estado `(3,)`, no una trayectoria.
- No se comprueba que I₁ < I₂ < I₃: es responsabilidad de quien llama.

### `euler_jacobian(I)`

Recibe las mismas inercias y devuelve una función J(U, t) con el Jacobiano analítico ∂F/∂ω, de tamaño 3x3 (ec. (7) del enunciado):

```text
J = [ 0                   (I₂ − I₃)/I₁ · ω₃   (I₂ − I₃)/I₁ · ω₂ ]
    [ (I₃ − I₁)/I₂ · ω₃   0                   (I₃ − I₁)/I₂ · ω₁ ]
    [ (I₁ − I₂)/I₃ · ω₂   (I₁ − I₂)/I₃ · ω₁   0                 ]
```

- Se usa igual que `euler_rhs`: `J = euler_jacobian(I)` y luego `J(U, t)`.
- Solo depende de ω; `t` no se usa, igual que en el campo.
- `U` es un único estado `(3,)`.
- Tampoco comprueba el orden de las inercias.

### `twice_kinetic_energy(U, I)` y `angular_momentum_squared(U, I)`

Son las dos magnitudes que se conservan (ecs. (3) y (4) del enunciado):

```text
2T = I₁ω₁² + I₂ω₂² + I₃ω₃²          doble de la energía cinética de rotación
L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²       cuadrado del módulo del momento angular
```

- Devuelven 2T y L², que son las integrales primeras tal como las escribe el enunciado, y no T ni |L|.
- Las dos aceptan un estado `(3,)` o una trayectoria `(N+1, 3)` guardada como `U[n, :]`, y devuelven un escalar o un vector `(N+1,)`, respectivamente.
- Aquí las inercias van como argumento `I`, porque no son un campo que se pase a un esquema temporal.
- No se comprueba el orden I₁ < I₂ < I₃.

La estabilidad de los tres giros puros, a partir de este Jacobiano, está en [`PEI1/README.md`](../../PEI1/README.md).