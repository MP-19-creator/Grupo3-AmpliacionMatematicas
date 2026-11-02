# Apoyos visuales para la defensa de PEI1

Se conservan las cuatro paginas, Matplotlib, las carpetas y responsabilidades.
No se cambian ecuaciones, esquemas, tolerancias ni resultados originales.
No se han añadido capas, hilos, procesos de calculo ni ejecucion asincrona.

## Probar en la aplicacion

```powershell
python PEI1/PEI1.py
```

1. Elegir el eje **Mayor I3**, epsilon **0.03**, dt **0.15 s**, tf **40 s**,
   paso fijo, y pulsar **Calcular**. Las inercias pueden quedarse en (1,2,3).
2. En **Conservacion**, pulsar **Ver trayectorias**. Euler se abre respecto de
   la referencia; los otros dos metodos permiten comparar la fase sin una
   gran variacion de amplitud. Los puntos senalan el mismo instante.
3. Avanzar el tiempo y pulsar **Ampliar tiempo** para observar hasta dos ciclos
   cerca de ese instante. **Tiempo completo** recupera el intervalo global.
4. Volver a **Ver derivas** y alternar **Ver con signo / Ver magnitud**.
   El signo identifica aumento o disminucion; la tabla conserva los maximos
   absolutos. La escala con signo es simetrica logaritmica, no lineal.
5. En **Estabilidad**, pulsar **Ver amplitud y fase**. El ejemplo test lineal
   muestra Euler explicito hacia fuera, Euler implicito hacia dentro y la
   diferencia entre conservar amplitud y conservar fase. Usa y=sigma*dt=0.3
   fijo: no es otra integracion del satelite ni usa el dt global como su y.
6. Elegir el eje **Intermedio I2**, epsilon **0.001**, tf **80 s** y recalcular.
   En Trayectorias aparece una guia proporcional a exp(lambda*t), limitada
   a perturbaciones pequenas. La curva no se presenta como una prediccion
   global del volteo. Con epsilon=0 no se inventa crecimiento ni periodo medido.

La vista Movimiento conserva simultaneamente orientacion y Poinsot; ahora
incluye el lado de la separatriz y C=L2-2T I2. El campo de dt y el nuevo
deslizador logaritmico estan vinculados y se restablecen juntos.

## Que significan las referencias

- La referencia de Trayectorias se calcula con el RK4 existente y dt/4,
  con los mismos limites de pasos. Es aproximada. Su solucion completa se
  conserva para analisis y solo se reducen puntos para representar.
- Los marcadores no se extrapolan mas alla del final de una trayectoria
  truncada. El encuadre de fases y de la componente temporal usa la referencia:
  una curva divergente puede salir de el.
- El periodo medido es la media de intervalos entre cruces ascendentes de la
  componente transversal. Se necesitan al menos dos cruces. Un guion indica
  que no se dispone de ciclos suficientes; no se sustituye por un cero.
- La curva "Exacta" de Estabilidad es la del modo test lineal u'=i*sigma*u.
  No afirma que exista una solucion exacta del satelite en esa pagina.
- La fase de R(iy) se desenvuelve antes de restar y para evitar saltos
  artificiales de 2*pi en RK4.

## Capturas finales

| Vista | 1200 x 800 | 1600 x 950 |
|---|---|---|
| Orientacion y separatriz | [Ver](1200-movimiento.png) | [Ver](1600-movimiento.png) |
| Derivas | [Ver](1200-derivas.png) | [Ver](1600-derivas.png) |
| Derivas con signo | [Ver](1200-signo.png) | [Ver](1600-signo.png) |
| Trayectorias y periodos | [Ver](1200-trayectorias.png) | [Ver](1600-trayectorias.png) |
| Detalle temporal | [Ver](1200-detalle.png) | [Ver](1600-detalle.png) |
| Regiones de estabilidad | [Ver](1200-regiones.png) | [Ver](1600-regiones.png) |
| Espirales, amplitud y fase | [Ver](1200-modo.png) | [Ver](1600-modo.png) |
| Richardson | [Ver](1200-precision.png) | [Ver](1600-precision.png) |

[Guia de crecimiento del eje intermedio](1200-crecimiento-intermedio.png).

## Verificacion y rendimiento

[Comprobaciones y costes de fotograma](verificacion.json).
[Cadencia real del bucle de Tk](cadencia.json).

Se comprobaron los botones de las vistas mediante eventos de Matplotlib sobre
TkAgg, las cuatro paginas en ambos tamanos, el reinicio del campo y deslizador,
las medidas de periodo y derivas, y la ausencia de extrapolacion tras truncar
una trayectoria. La animacion y los cambios de representacion no integran
de nuevo ni acumulan objetos graficos. El buffer tras repintar parcialmente
coincide exactamente con el obtenido al reconstruir el fondo.

En 1600 x 950, las medianas de actualizacion y dibujo de las vistas nuevas
estan alrededor de 12-13 ms por fotograma; en 1200 x 800, alrededor de 8-10 ms.
En pruebas de tres segundos del bucle real de TkAgg se midieron 23.3 fps en
Trayectorias y 22.3 fps en el modo lineal. El intervalo mediano fue de unos
46 ms y el percentil 95 fue inferior a 49 ms en ambas pruebas. Son muestras
breves en este equipo, no una garantia universal de cadencia.

El primer acceso a Conservacion añade el calculo de la referencia RK4 de
paso mas fino. Se reutiliza hasta cambiar parametros. Los estudios siguen
siendo sincronos; no se modifica el modelo de ejecucion para ocultar su coste.

Para repetir desde la raiz del repositorio:

```powershell
python tmp/pei1-review/verificar_apoyos.py
python tmp/pei1-review/medir_apoyos.py
python tmp/pei1-review/verificar.py
```

## Distribucion del codigo

- `PEI1/PEI1.py`: prepara los datos auxiliares usando el modelo y el motor
  existentes, y los entrega mediante las mismas acciones del coordinador.
- `active/gui_reactive/page_invariants.py`: presenta derivas o trayectorias.
- `active/gui_reactive/page_stability.py`: presenta regiones o el modo test.
- `active/gui_reactive/page_attitude.py`: presenta el indicador de separatriz.
- `active/gui_reactive/gui.py`: enlaza los controles y el repintado existente.
- `active/space_physics/` y `active/numerical_engine/`: sin modificaciones.
