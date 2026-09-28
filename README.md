# Proyecto PEI 1 — Dinámica de actitud satelital

Proyecto de Ampliación de Matemáticas 1 (MUSE - ETSIAE).

Este repositorio está preparado como guía: cada carpeta indica qué trabajo irá en ella. 

## ¿Dónde va cada cosa?

```text
ArchivosNecesarios/       Enunciado de la PEI 1 y hoja de hitos del curso
documentacion/            Apuntes, explicaciones y material para la defensa
hitos/
  hito_1/                 Primeros programas y comparación de órbitas
  hito_2/                 Métodos reutilizables y problema de Kepler
  hito_3/                 Estimación del error y convergencia
  hito_4/                 Problemas lineales y estabilidad
pruebas/                  Comprobaciones del código
src/dinamica_actitud/     Código de la simulación de la PEI 1
  fisica/                 Ecuaciones del sólido, Jacobiano e invariantes
  metodos_numericos/      Métodos que avanzan la simulación en el tiempo
  analisis/               Error, convergencia y estabilidad
  graficas/               Espacio de fases, superficies y animaciones
  interfaz/               Ventana, controles y paneles de resultados
  ejemplos/               Casos de simulación que se puedan repetir
```

Cada carpeta principal y cada hito tiene su propio `README.md` con una explicación más concreta. En las carpetas de cada hito, `scripts/` es para los programas y `resultados/` para gráficas o datos.

## Archivos principales

| Archivo | Para qué servirá |
|---|---|
| `fisica/ecuaciones_euler.py` | Describir cómo cambia la velocidad angular del sólido. |
| `fisica/invariantes.py` | Calcular el Jacobiano, la energía y el momento angular. |
| `metodos_numericos/euler_explicito.py`, `euler_inverso.py`, `crank_nicolson.py`, `runge_kutta.py`, `salto_rana.py` | Implementar cada método de integración por separado. |
| `metodos_numericos/integrar.py` | Aplicar el método elegido durante todo el intervalo de simulación. |
| `analisis/convergencia.py` | Estimar errores y orden de convergencia con Richardson. |
| `analisis/estabilidad.py` | Estudiar cuándo cada método es numéricamente estable. |
| `graficas/espacio_fases.py` | Dibujar la trayectoria y las superficies de Poinsot. |
| `graficas/animacion_actitud.py` | Mostrar cómo cambia la orientación del satélite. |
| `interfaz/aplicacion.py` | Reunir los controles y las gráficas en la ventana del programa. |

## Diferencia entre los hitos y la PEI 1

La hoja `ArchivosNecesarios/MUSE_weekly_milestones.pdf` propone ejercicios semanales con órbitas de Kepler y problemas lineales. Están ordenados en `hitos/`. El enunciado `ArchivosNecesarios/PEI1.pdf` pide estudiar la rotación de un sólido rígido, sus ejes estables e inestable, sus magnitudes conservadas y una interfaz gráfica. Ese código va en `src/dinamica_actitud/`.

## Capas del programa

1. **Física:** define las ecuaciones y magnitudes del satélite.
2. **Métodos y análisis:** calcula la evolución y estudia su precisión y estabilidad.
3. **Gráficas e interfaz:** presenta los resultados y permite cambiar los parámetros.

La interfaz conectará las otras capas; las ecuaciones y métodos podrán usarse por separado.

