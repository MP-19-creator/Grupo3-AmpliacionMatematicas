# Error y convergencia

Se integra el oscilador U' = (U[1], -U[0]) con U0 = (1, 0) hasta tf = 2*pi.
Su solucion exacta es U(t) = (cos(t), -sin(t)).

## Estimacion del error

Para cada metodo se integra con N y 2*N intervalos usando `Cauchy_problem`.
Se comparan las soluciones en los mismos instantes: U[i, :] y U2[2*i, :].
El error estimado de la solucion con N intervalos es
(U - U2) / (1 - 1/2**orden), tomando error = solucion numerica - solucion exacta.
La primera grafica representa su norma frente al tiempo con N = 200.

Richardson es una estimacion asintotica: necesita un paso suficientemente pequeno.
Los dos Euler son de primer orden; Crank-Nicolson es de segundo y RK4 de cuarto.
Para este ejemplo y este paso, RK4 presenta el menor error de los cuatro.

## Convergencia

Se usan diez mallas con 10, 20, 40... hasta 5120 intervalos. Para cada malla
se toma la norma de la diferencia entre soluciones con N y 2*N intervalos en tf.
Primero se mide el orden sin introducir el orden teorico en este calculo.

La pendiente de log(diferencia) frente a log(N) es aproximadamente -p en la
zona asintotica. Se selecciona manualmente el tramo [inicio:fin], con indices
desde cero y fin excluido. En este ejemplo inicio = 4 y fin = 8 seleccionan
N = 160, 320, 640 y 1280. No se ajustan todos los puntos de la curva.
El tramo se debe revisar al cambiar el problema o sus parametros.

Una vez obtenido p = -pendiente, se aplica el factor 1/(1 - 1/2**p) para
estimar el error de Richardson. Esta correccion desplaza la curva verticalmente
en escala logaritmica y no cambia la pendiente. Las graficas muestran estos
errores corregidos, todas las mallas y el tramo ajustado en rojo.

| Metodo | Orden teorico | Orden observado |
|---|---:|---:|
| Euler | 1 | 1.038 |
| Euler implicito | 1 | 0.961 |
| Crank-Nicolson | 2 | 2.000 |
| RK4 | 4 | 4.000 |

Al dividir el paso por dos, el error disminuye aproximadamente por un factor
2 en los Euler, 4 en Crank-Nicolson y 16 en RK4. Las pequenas desviaciones
de los ordenes teoricos se deben a que los pasos son finitos.

Con pocos intervalos puede no observarse todavia una pendiente constante.
Con demasiados, el redondeo o la tolerancia de Newton pueden dominar el error.
Por eso se elige un tramo intermedio donde la curva sea aproximadamente recta.
La funcion avisa si el tramo seleccionado contiene diferencias menores o iguales
a 1e-12. Este umbral no elige automaticamente el tramo ni garantiza que las
tolerancias sean despreciables: hay que comprobar la grafica.
