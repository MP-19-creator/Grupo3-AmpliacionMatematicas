# Revisión de interfaz y rendimiento de PEI1

Se mantienen Matplotlib, las carpetas y las responsabilidades originales.
No se han modificado `active/space_physics/` ni `active/numerical_engine/`,
las ecuaciones, esquemas, tolerancias ni la solución numérica completa.

## Diagnóstico previo

Se ejecutaron las cuatro páginas con TkAgg y se redimensionó la ventana.
Las tablas de Conservación y Estabilidad desbordaban el margen derecho;
los títulos de Precisión se solapaban y su explicación tapaba la tabla.
Las instrucciones del lateral se cortaban en la ventana pequeña. Los gráficos
competían con explicaciones extensas y paneles de resultados demasiado estrechos.

La animación ya actualizaba los objetos 3D existentes: el problema principal
era el repintado completo del lienzo, incluidos controles, textos, leyendas
y mallas estáticas. Un perfil previo de `canvas.draw` atribuyó aproximadamente
0,37 de 0,51 s al dibujo de texto en esta instalación de Matplotlib.

La trayectoria no se reintegraba durante la animación. Las pestañas ya
reutilizaban una página dibujada mientras no se pulsara Calcular. Sin embargo,
Calcular invalidaba todos los resultados aun con parámetros idénticos; cambiar
solo el intervalo de Precisión también reintegraba la trayectoria y hacía perder
la comparación entre métodos. La preparación calculaba dos veces las matrices
de rotación de las muestras visuales.

## Cambios

- Títulos breves, controles agrupados, tablas compactas y tipografía adaptada
  al tamaño del lienzo. Se retiran instrucciones redundantes y explicaciones
  que tapaban los resultados. Los gráficos conservan unidades y leyendas.
- Conservación dedica todo el ancho a sus cuatro gráficos y coloca las derivas
  en una tabla inferior. Paso fijo muestra una única marca representativa de Δt.
- Estabilidad separa regiones, detalle, amplificación y tabla; Precisión elimina
  el texto superpuesto a los valores de convergencia.
- `PEI1/PEI1.py` conserva la coordinación y reutiliza la trayectoria y los
  estudios válidos. La caché se invalida al cambiar parámetros; los estudios
  de precisión se distinguen por su intervalo.
- La GUI mantiene un fondo estático en TkAgg. Poinsot actualiza tres líneas;
  Conservación, cuatro cursores; Estabilidad, sus puntos y cursor. El cuerpo
  reutiliza todas sus colecciones, pero se dibuja como eje 3D completo para
  recalcular proyección y ordenación de profundidad.
- El repintado parcial se habilita únicamente en TkAgg, con `supports_blit`.
  Se verifica contra el dibujo completo. Otros backends usan `draw_idle`.
  Cámara, tamaño, controles y datos invalidan el fondo; las exportaciones incluyen
  también el cuerpo 3D.
- El temporizador intenta 30 fps y descuenta el coste del fotograma de su espera.
  No crea una cola de imágenes; el avance sigue el reloj real. Pausado reduce
  la frecuencia de los callbacks. No se introducen hilos, procesos ni asincronía.
- Reiniciar vuelve al instante cero incluso si los parámetros ya eran los
  iniciales. Los cambios del estudio se indican por separado de los físicos.

## Comparación reproducible

Mismo equipo, Python 3.14, Matplotlib 3.11.2 y TkAgg. Parámetros en ambos casos:
I=(1,2,3), eje intermedio, Ω=1, ε=0,001, RK4, paso fijo Δt=0,02 s,
tf=80 s, tolerancia del control 1e-6; estudio de precisión de 20 s.
La solución completa contiene 4001 nodos y permanece disponible para análisis.

Se midieron 33 fotogramas por página/tamaño y se descartaron los tres primeros.
La actualización de artistas y el dibujo se registran por separado. La referencia
se carga desde Git HEAD en memoria, sin modificar los archivos de trabajo.
Las ejecuciones son secuenciales: hay variación de carga del equipo y estas cifras
no representan una aceleración del algoritmo de integración.

Tiempo mediano de actualización y dibujo por fotograma, en milisegundos:

| Ventana | Página | Antes: actualizar | Antes: dibujar | Después: actualizar | Después: dibujar | Total antes → después |
|---|---|---:|---:|---:|---:|---:|
| 1600×950 | Movimiento | 0,84 | 321,18 | 1,06 | 35,11 | 322,17 → 36,19 |
| 1600×950 | Conservación | 0,13 | 458,89 | 0,08 | 7,98 | 459,03 → 8,08 |
| 1600×950 | Estabilidad | 0,17 | 493,58 | 0,16 | 15,62 | 493,73 → 15,78 |
| 1200×800 | Movimiento | 0,91 | 399,75 | 0,87 | 26,52 | 400,32 → 27,54 |
| 1200×800 | Conservación | 0,12 | 451,11 | 0,12 | 10,77 | 451,25 → 10,88 |
| 1200×800 | Estabilidad | 0,17 | 572,46 | 0,18 | 12,34 | 572,69 → 12,54 |

Precisión es estática y ya evitaba dibujar en cada tic: sigue sin redibujarse
durante la reproducción. El escalado de Windows es 125 %: Tk devuelve tamaños
lógicos de lienzo de 1280×760 y 960×640, respectivamente; los buffers de las
capturas conservan los píxeles físicos.

Una prueba adicional del bucle real de Tk de cuatro segundos en Movimiento,
ventana grande, registró **21,4 fps**, intervalo mediano **45,5 ms** y percentil
95 **62,3 ms**. Es una muestra breve, no una garantía de 30 fps. Los percentiles
95 de coste de dibujo más actualización son 42,8 ms en Movimiento grande y
38,8 ms en la ventana pequeña. El objetivo de 30 fps evita actualizaciones
excesivas cuando los gráficos son más baratos.

Tiempos de cálculo y preparación, separados del dibujo:

| Operación | Antes (s) | Después (s) | Interpretación |
|---|---:|---:|---|
| Integración principal inicial | 0,204 | 0,163 | Mismo cálculo; variación de ejecución |
| Preparación principal, sin integración | 0,072 | 0,025 | Reutilización de las rotaciones |
| Comparación de los otros métodos | 0,457 | 0,873 | Mismos cálculos; variación de ejecución |
| Preparación de estabilidad | 0,097 | 0,157 | Mismos datos; variación de ejecución |
| Estudio de precisión, primera apertura | 7,613 | 8,170 | Mismos cálculos; no se acelera el estudio |
| Calcular otra vez desde Precisión, incluyendo dibujo | 9,492 | 0,591 | Ya no integra ni repite el estudio |

Tras ese segundo Calcular, recorrer las pestañas provocaba antes dos
integraciones adicionales y otra preparación de comparación/estabilidad;
ahora provoca **cero** llamadas a esos cálculos. Cambiar únicamente el intervalo
de Precisión tampoco reintegra la trayectoria. Volver a un intervalo previamente
calculado reutiliza el estudio.

Los JSON contienen las muestras resumidas, tiempos de funciones y contadores:
[referencia](baseline-timings.json), [versión final](final-timings.json).

## Verificación

[Resultados de las comprobaciones](verificacion.json).

- Igualdad exacta de todos los nodos y estados de la solución inicial antes/después.
- Igualdad exacta para Euler, Crank–Nicolson y RK4, en paso fijo y adaptativo:
  solución completa, muestras visuales, derivas, rotaciones, estela y volteos.
- Clic y teclado en las cuatro pestañas, navegación temporal, pausa/reproducción,
  velocidad, selección de eje/método/paso, cámara y reinicio.
- Inercias inválidas conservan el último resultado válido.
- Estudio de precisión independiente de la integración principal.
- Las cuatro páginas en ambos tamaños, sin crecimiento del número de artistas
  durante la reproducción. Igualdad exacta del buffer tras actualizar parcialmente
  y tras reconstruir el fondo completo.
- Captura, exportación PNG y cierre que detiene el temporizador.

Las capturas finales se revisaron visualmente. También se ejecutó la aplicación
normal para inspeccionar su vista de movimiento animada. El resto de los controles
y el redimensionado se verificaron sobre un canvas Tk real mediante los mismos
eventos de Matplotlib que reciben los widgets.

## Capturas

| Página | Antes, 1200×800 | Después, 1200×800 | Después, 1600×950 |
|---|---|---|---|
| Movimiento | [Ver](baseline-1200-page-1.png) | [Ver](final-1200-page-1.png) | [Ver](final-1600-page-1.png) |
| Conservación | [Ver](baseline-1200-page-2.png) | [Ver](final-1200-page-2.png) | [Ver](final-1600-page-2.png) |
| Estabilidad | [Ver](baseline-1200-page-3.png) | [Ver](final-1200-page-3.png) | [Ver](final-1600-page-3.png) |
| Precisión | [Ver](baseline-1200-page-4.png) | [Ver](final-1200-page-4.png) | [Ver](final-1600-page-4.png) |

## Repetir las pruebas

Desde la raíz, con Python y Tk correctamente instalados:

```powershell
python tmp/pei1-review/comparacion.py baseline --baseline
python tmp/pei1-review/comparacion.py final
python tmp/pei1-review/verificar.py
```

`--baseline` utiliza el HEAD actual del repositorio: para conservar la referencia
original después de un futuro commit, hay que usar su revisión de Git original.
Los ficheros `before-*` y `after-*` corresponden al diagnóstico y a una iteración
intermedia; la comparación definitiva es `baseline-*` frente a `final-*`.

## Limitación y propuesta pendiente

El primer estudio costoso continúa bloqueando el bucle de eventos mientras
se calcula. Se pinta el estado de espera antes de iniciarlo y se evita repetirlo.
Mantener la interfaz interactiva durante ese primer cálculo exigiría ceder
el control del bucle o ejecutar el cálculo fuera de él. Es una propuesta
pendiente que cambiaría el modelo de ejecución; no se ha implementado.
