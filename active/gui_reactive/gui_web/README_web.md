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
- la orientación de los tres integradores a la vez.

`gui_web.py` solo reduce lo que envía, sin cambiar ningún valor: submuestrea las series largas a 2000 puntos, como hacen las páginas de la v1 al dibujar, y de las mallas de estabilidad envía solo sus ejes, porque las filas de `meshgrid` se repiten.

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
| `gui_web/page_invariants_web.js` | `page_invariants.py` | Página 2: derivas de 2T, L² y \|q\| y trayectorias transversales |
| `gui_web/page_stability_web.js` | `page_stability.py` | Página 3: regiones \|R(z)\| ≤ 1, autovalores y modo test |
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
| C | Los tres integradores |
| P | Modo presentación |
| T | Tema claro para el proyector |
| F | Pantalla completa |
| G | Grabar la vista 3D en vídeo (.webm, a Descargas) |

## Ajustes rápidos

- **Brillo de estelas, flechas y halos:** constante `intensidadBrillo` al principio de `escena_web.js` (0 = sin brillo, 1 = máximo).
- **Duración de una reproducción completa:** `duracion_reproduccion` en `gui_web.py` (20 s, como en la v1).
