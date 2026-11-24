# Proyecto PEI 1 — Dinámica de actitud satelital

Proyecto de Ampliación de Matemáticas 1 (MUSE - ETSIAE).

Este repositorio está preparado como guía: cada carpeta indica qué trabajo va en ella.

## ¿Dónde va cada cosa?

```text
ArchivosNecesarios/       Enunciado de la PEI 1 y hoja de hitos del curso
PEI1/                     Resumen del enunciado de la PEI 1
active/                   Código de la PEI 1, en tres capas
  space_physics/          Ecuaciones del problema, Jacobiano e invariantes
  numerical_engine/       Esquemas temporales e integrador del problema de Cauchy
  gui_reactive/           Interfaz gráfica (todavía vacía)
hitos/
  hito_1/                 Primeros programas y comparación de órbitas
  hito_2/                 Métodos reutilizables y problema de Kepler
  hito_3/                 Estimación del error y convergencia
  hito_4/                 Problemas lineales y estabilidad
pruebas/                  Prototipos de la interfaz con sliders
```

Cada carpeta principal y cada hito tiene su propio `README.md` con una explicación más concreta.

## Archivos principales

| Archivo | Qué contiene |
|---|---|
| `active/space_physics/eje_intermedio.py` | Ecuaciones de Euler del sólido rígido (`euler_rhs`), su Jacobiano (`euler_jacobian`) y los invariantes 2T y L² (`twice_kinetic_energy`, `angular_momentum_squared`). |
| `active/space_physics/kepler.py` | Campo del problema de Kepler (`Kepler`). |
| `active/numerical_engine/temporal_schemes.py` | Esquemas de un paso: `Euler`, `Euler_implicit`, `RK4` y `Crank_Nicolson`. |
| `active/numerical_engine/Cauchy_Problem.py` | `Cauchy_problem`: aplica un esquema durante todo el intervalo de integración. |
| `hitos/hito_1/OrbitaEuler.py`, `OrbitaCN.py`, `OrbitaRK4.py` | Órbita de Kepler con cada método, sin funciones. |
| `hitos/hito_2/Orbita_Kepler.py` | Órbita de Kepler con los esquemas y el integrador de `active/`. |

## Cómo ejecutar

Los programas que importan de `active/` se lanzan **desde la raíz del repositorio** con `-m`:

```text
python -m hitos.hito_2.Orbita_Kepler
```

En VSCode también se puede usar F5 con la configuración "Ejecutar archivo Python" de `.vscode/launch.json`, que fija `PYTHONPATH` a la raíz del repositorio.

Lanzar el fichero directamente no funciona:

```text
python hitos/hito_2/Orbita_Kepler.py
ModuleNotFoundError: No module named 'active'
```

Al lanzar un fichero, Python busca los módulos en la carpeta de ese fichero (`hitos/hito_2/`) y no en la raíz, así que no encuentra `active`. Con `-m` los busca en la carpeta desde la que se ejecuta.

Los scripts del hito 1 no importan nada del repositorio y se pueden lanzar de cualquier forma.

El fichero `.env` versionado fija `PYTHONPATH` a una ruta absoluta de un ordenador concreto. En los demás esa ruta no existe y no sirve.

## Estado

| Parte | Estado |
|---|---|
| Física del sólido rígido (campo, Jacobiano, 2T y L²) | Hecha. |
| Física de Kepler | Hecho el campo. Sin Jacobiano ni invariantes. |
| Esquemas de un paso (Euler, Euler implícito, Crank-Nicolson, RK4) | Hechos. Los implícitos tienen limitaciones: ver [`active/numerical_engine/README.md`](active/numerical_engine/README.md). |
| Integrador del problema de Cauchy | Hecho. |
| Error por Richardson y orden de convergencia | Declarado, sin escribir. |
| Regiones de estabilidad | Declarado, sin escribir. |
| Paso adaptativo y Leap-Frog | Sin empezar. |
| Interfaz gráfica | Sin empezar. Hay dos prototipos antiguos en [`pruebas/`](pruebas/). |

## Diferencia entre los hitos y la PEI 1

La hoja `ArchivosNecesarios/MUSE_weekly_milestones.pdf` propone ejercicios semanales con órbitas de Kepler y problemas lineales. Están ordenados en `hitos/`. El enunciado `ArchivosNecesarios/PEI1.pdf` pide estudiar la rotación de un sólido rígido, sus ejes estables e inestable, sus magnitudes conservadas y una interfaz gráfica. Ese código va en `active/`.

Los hitos usan el motor numérico de `active/numerical_engine/`, que es el mismo que usará la PEI 1.

## Capas del programa

1. **Física:** define las ecuaciones y magnitudes del satélite.
2. **Métodos y análisis:** calcula la evolución y estudia su precisión y estabilidad.
3. **Gráficas e interfaz:** presenta los resultados y permite cambiar los parámetros.

La interfaz conectará las otras capas; las ecuaciones y métodos podrán usarse por separado.
