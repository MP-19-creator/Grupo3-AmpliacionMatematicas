# ÓRBITA · Cuaderno de dinámica

Interfaz del teorema del eje intermedio en Matplotlib. Ejecutar desde la raíz:

```powershell
python PEI1/PEI1.py
```

El diseño utiliza papel marfil, tinta violeta, cobre y verde petróleo. Los controles
se agrupan en un banco lateral permanente; las cuatro pestañas presentan movimiento,
conservación, estabilidad y precisión. El panel derecho de movimiento mantiene la
comparación entre teoría y simulación y permite recorrer el tiempo haciendo clic.

Los colores de cada integrador y de los tres ejes se conservan entre vistas. La
retícula de presentación y el área de repintado de la animación están definidos en
`gui.py`; la paleta compartida está en `style.py`.

ε y Δt se introducen directamente en campos numéricos: escribe el valor y pulsa
Intro. Se admite coma decimal y notación científica. ε admite de 0 a 1; Δt,
de 0,000001 a 2 segundos. El tiempo final puede reducirse hasta 1 segundo.
La tolerancia aparece al seleccionar el modo adaptativo y también se introduce
como valor directo.

El paso fijo respeta el Δt solicitado, con un último paso más corto si hace falta
para alcanzar el tiempo final. Si se alcanza el presupuesto de 100 000 pasos
(30 000 para Crank–Nicolson), se muestra una trayectoria parcial y un aviso con
el tiempo alcanzado; reduce el tiempo final para estudiar pasos aún más pequeños.
La animación utiliza como máximo 4000 muestras, conservando los nodos completos
para el análisis. Los módulos de `space_physics` y `numerical_engine` se mantienen.

Referencias consultadas para separar controles, movimiento y lectura de resultados:

- [PhET: principios de diseño de simulaciones](https://phet.colorado.edu/en/about).
- [myPhysicsLab: simuladores interactivos](https://myphysicslab.com/).

Atajos: **1–4** cambia de vista, **espacio** pausa, **← →** recorre el tiempo,
**+ −** cambia la velocidad, **V** restaura las cámaras, **R** restablece los
parámetros y **F** activa la pantalla completa. Las vistas 3D se giran arrastrando.
