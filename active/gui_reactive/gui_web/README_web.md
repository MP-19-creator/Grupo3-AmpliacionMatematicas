# GUI web de ÓRBITA (versión 2, en paralelo a la v1)

Ejecutar desde la raíz del repositorio:

```powershell
python PEI1/PEI1_web.py
```

Se abre una ventana de Chrome o Edge sin pestañas. Cerrarla termina el programa; también vale Ctrl+C en la terminal.

Las cuatro páginas de la v1 están completas: actitud y espacio de fases, invariantes, estabilidad y Richardson.

Si el puerto 8765 está ocupado (por ejemplo, con el programa abierto dos veces), se usa otro libre y la terminal indica cuál. Para fijar otro puerto: `$env:ORBITA_PUERTO = 8800` antes de ejecutar.

## Relación con la v1

La v1 (`PEI1/PEI1.py` + `gui.py` y `page_*.py`, con matplotlib) no se ha tocado y sigue funcionando igual.

El flujo es el mismo de la presentación. Solo cambia quién crea la GUI y dónde se dibuja:

| Paso | v1 | Web |
|---|---|---|
| Programa principal | `PEI1.py` → `iniciar_programa()` | `PEI1_web.py` → `iniciar_programa_web()` |
| Crear la GUI | `crear_interfaz()` (gui.py) | `crear_interfaz_web()` (gui_web.py) |
| Cálculos | `calcular_trayectoria`, `integrar_trayectoria`… | **las mismas funciones, importadas de PEI1.py** |
| Física y motor | `space_physics`, `numerical_engine` | igual, sin cambios |
| Dibujar y animar | matplotlib en la CPU | el navegador en la GPU (Three.js y Plotly) |
| Bucle de eventos | `plt.show()` | `interfaz['servir']()` |

Python calcula y envía los resultados en JSON. El navegador no calcula nada: dibuja lo que recibe e interpola entre muestras para que la animación sea fluida.

`PEI1_web.py` solo añade lo que dibuja la web y no la v1:

- la herpolhoda, R(q)·ω;
- el plano invariable, a distancia 2T/|L|;
- la familia de polhodas, integrada con RK4;
- la orientación de todos los integradores a la vez;
- el **Euler implícito** (orden 1), con el mismo flujo que los tres esquemas del enunciado: selector, comparación de derivas, fantasmas 3D, regiones de estabilidad, tabla de predicción y estudio de convergencia. Se importa `Euler_implicit` de `temporal_schemes`; como `Newton` (en `NewtonRaphson.py`) aún no admite el Jacobiano, mientras tanto se usa `paso_euler_implicito`, el mismo patrón que `paso_crank_nicolson` en `PEI1.py`. Tiene el límite de pasos de los implícitos (30 000). Las funciones de `PEI1.py` se envuelven (`comparar_metodos_web`, `preparar_datos_estabilidad_web`, `calcular_estudio_error_web`), no se copian;
- el periodo de la polhoda sin cancelaciones (`periodo_polhoda_web`). `Polhode_period` redondea C = L² − 2T·I₂ a 12 cifras y con ε ≲ 10⁻⁶ lo toma por la separatriz (P = ∞). Aquí cada diferencia es una suma de términos del mismo signo y K se evalúa con el módulo complementario. Con ε = 10⁻⁷ da P/2 = 59,4 s, frente a 59,6 s simulados. Donde la v1 es válida, coincide con ella.

`gui_web.py` solo reduce lo que envía, sin cambiar ningún valor: submuestrea las series largas a 2000 puntos, como hacen las páginas de la v1 al dibujar, y de las mallas de estabilidad envía solo sus ejes, porque las filas de `meshgrid` se repiten. También traduce al inglés los avisos que la v1 escribe en español (`traducciones`).

Diferencias de controles con la v1: el Δt mínimo es 10⁻³ s (en la v1, 10⁻⁶). Debajo de Time se indica en vivo el número de pasos N = t_f/Δt: en ámbar por encima de 20 000 y en rojo si supera el límite de pasos de `PEI1.py`.

Todo ello usa funciones de física que ya existían.

## Ficheros

| Fichero | Equivale a | Qué hace |
|---|---|---|
| `PEI1/PEI1_web.py` | `PEI1.py` | Principal: mismo flujo; importa los cálculos de la v1 |
| `gui_reactive/gui_web.py` | `gui.py` (parte Python) | Servidor local, controles, conversión a JSON |
| `gui_web/index_web.html` | — | Estructura de la página |
| `gui_web/style_web.css` | `style.py` | Paleta, tipografía, tema oscuro y claro |
| `gui_web/gui_web.js` | `gui.py` (parte navegador) | Controles, reloj común, pestañas, teclado |
| `gui_web/page_attitude_web.js` | `page_attitude.py` | Página 1: actitud, Poinsot, espacio de fases |
| `gui_web/page_invariants_web.js` | `page_invariants.py` | Página 2: derivas de 2T y L² y trayectorias transversales |
| `gui_web/page_stability_web.js` | `page_stability.py` | Página 3: regiones \|R(z)\| ≤ 1 (ejes a la misma escala), autovalores, tabla de predicción y modo test |
| `gui_web/page_richardson_web.js` | `page_richardson.py` | Página 4: convergencia y estimación de Richardson |
| `gui_web/graficas_web.js` | `preparar_grafica`, `poner_leyenda` | Estilo común de las gráficas Plotly y cursor del instante actual |
| `gui_web/escena_web.js` | ayudas de `style.py` | Piezas 3D comunes: visor, estelas, flechas, elipsoides |
| `gui_web/cuerpos_web.js` | `dibujar_cuerpo` | Caja exacta, T, raqueta y satélite |
| `gui_web/vendor/` | — | Three.js, Plotly y fuentes, con sus licencias (sin internet en el aula) |

Para quitar la versión web basta con borrar `PEI1_web.py`, `gui_web.py` y la carpeta `gui_web/`. Ningún fichero de la v1 importa nada de ellos.

## Teclado

`?` muestra todos los atajos. Los principales:

| Tecla | Acción |
|---|---|
| Espacio | Pausar |
| ← → | Tiempo |
| 1–4 | Páginas |
| ↵ | Calcular |
| O | Vista del cuerpo / Poinsot |
| B | Forma del cuerpo |
| C | Todos los integradores |
| P | Modo presentación |
| T | Tema claro para el proyector |
| F | Pantalla completa |
| G | Grabar la vista 3D en vídeo (.webm, a Descargas) |

## Ajustes rápidos

- **Brillo de estelas, flechas y halos:** constante `intensidadBrillo` al principio de `escena_web.js` (0 = sin brillo, 1 = máximo; ahora 0,32).
- **Longitud de las estelas:** `factorEstela` en `page_attitude_web.js` (fracción de la ventana de la v1; ahora 0,7).
- **Calidad automática:** al entrar se miden los fps de la página 1 durante 3 s; por debajo de `fpsMinimos` (40, en `page_attitude_web.js`) se quita el bloom. La consola del navegador indica el resultado (`[ORBITA] … fps`). La densidad de píxeles de los visores 3D está limitada a 1,25 (`maximaDensidad`, en `escena_web.js`).
- **Pantallas pequeñas:** `style_web.css` compacta la interfaz por debajo de 1440 y de 1100 px de ancho (comprobado a 1920×1080, 1280×720 y 1024×768).
- **Duración de una reproducción completa:** `duracion_reproduccion` en `gui_web.py` (20 s, como en la v1).
