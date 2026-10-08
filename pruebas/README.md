# Pruebas

Aquí hay dos prototipos de la interfaz gráfica, hechos antes de reorganizar el código en `active/`. Integran las ecuaciones de Euler del sólido rígido con tres métodos y dibujan ω(t) y la deriva de la energía, con sliders para I₁, I₂, I₃ y Ω.

| Archivo | Qué es |
|---|---|
| `Prueba sliders` | Primera versión: las gráficas se recalculan al mover un slider. |
| `Prueba sliders v2` | Segunda versión: se recalculan al pulsar el botón "Actualizar". |

Los dos son código Python, aunque no tienen extensión `.py`.

## Estado

Ninguno de los dos arranca con el código actual:

- Importan `methods`, un módulo que ya no existe. Los esquemas están ahora en `active/numerical_engine/temporal_schemes.py`.
- Llaman a los métodos como `metodo(U, campo, DT, N)`, que integraba todo el intervalo. Los esquemas actuales dan un solo paso y reciben `(U, dt, t, F)`; el intervalo completo lo integra `Cauchy_problem`.
- `Prueba sliders` usa además la variable `deriva` sin definir, porque las líneas que la calculan están comentadas.

## Qué se puede reutilizar

La disposición de sliders, botones y paneles sirve de punto de partida para la interfaz definitiva, que irá en `active/gui_reactive/`.
