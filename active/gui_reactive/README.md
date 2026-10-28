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

El rediseño conserva los módulos de `space_physics` y `numerical_engine`, las
condiciones iniciales, los rangos de parámetros, los métodos de paso fijo y
adaptativo y el cálculo cancelable en segundo plano.

Referencias consultadas para separar controles, movimiento y lectura de resultados:

- [PhET: principios de diseño de simulaciones](https://phet.colorado.edu/en/about).
- [myPhysicsLab: simuladores interactivos](https://myphysicslab.com/).

Atajos: **1–4** cambia de vista, **espacio** pausa, **← →** recorre el tiempo,
**+ −** cambia la velocidad, **V** restaura las cámaras, **R** restablece los
parámetros y **F** activa la pantalla completa. Las vistas 3D se giran arrastrando.
