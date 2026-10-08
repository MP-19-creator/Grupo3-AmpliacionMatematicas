# Código de la PEI 1

El enunciado ([`PEI1.pdf`](../ArchivosNecesarios/PEI1.pdf), apartado 3; resumido en [`PEI1/README.md`](../PEI1/README.md)) pide que el programa esté dividido en tres capas separadas. Aquí hay una carpeta por capa:

| Carpeta | Capa | Qué debe hacer | Estado |
|---|---|---|---|
| [`space_physics/`](space_physics/) | Física | Define las ecuaciones del problema, su Jacobiano exacto y las magnitudes que se conservan (2T y L²). | Hecho para el sólido rígido. |
| [`numerical_engine/`](numerical_engine/) | Matemática y algorítmica | Avanza la solución en el tiempo (Euler, Crank-Nicolson, RK4, paso simple y adaptativo), estima el error con la extrapolación de Richardson y calcula las regiones de estabilidad \|R(z)\| ≤ 1. | Hay esquemas de un paso (Euler, Euler implícito, Crank-Nicolson, RK4) y el integrador. Faltan el paso adaptativo, Richardson y las regiones de estabilidad. |
| [`gui_reactive/`](gui_reactive/) | Visualización | Cuadro de mando interactivo con varios paneles (p. ej. `matplotlib.widgets`). | Vacía. |

## Cómo se relacionan

- La **física** solo sabe del problema: dado un estado U y un tiempo t, devuelve F(U, t). No integra ni dibuja.
- El **motor numérico** solo sabe integrar: recibe una F cualquiera y no conoce de qué problema viene. Por eso sirve igual para Kepler que para el sólido rígido.
- La **interfaz** es la única que usa las otras dos: toma la F de la física, la integra con el motor y muestra el resultado.

## Qué debe permitir la interfaz

En tiempo real:

1. Cambiar con deslizadores I₁, I₂, I₃, la velocidad angular inicial Ω y el paso temporal Δt.
2. Cambiar de integrador y comparar la deriva numérica de la energía ΔT(t) y del momento ΔL(t).
3. Ver a la vez el espacio de fases 3D (ω₁, ω₂, ω₃) con las superficies de Poinsot y la separatriz, y la animación 3D de la orientación del satélite durante el volteo.

La separación en tres capas es el bloque 3 de la rúbrica (25 %).
