# Hitos del curso

Cada carpeta corresponde a un hito de la hoja del curso ([`MUSE_weekly_milestones.pdf`](../ArchivosNecesarios/MUSE_weekly_milestones.pdf)). Estos ejercicios de órbitas de Kepler y problemas lineales son distintos del modelo de actitud de la PEI 1, que está en [`active/`](../active/).

## Qué hay en cada carpeta

| Archivo | Qué contiene |
|---|---|
| `README.md` | El enunciado del hito. |
| Scripts `.py` | Los programas del hito, directamente en la carpeta. |
| `resultados.md` | La explicación de los resultados obtenidos. |

## Estado

| Hito | Tema | Estado |
|---|---|---|
| [`hito_1/`](hito_1/) | Órbitas con Euler, Crank-Nicolson y RK4, sin funciones | Hecho. |
| [`hito_2/`](hito_2/) | Esquemas como funciones y problema de Kepler | Código hecho. `resultados.md` está vacío: falta explicar los resultados y variar el paso (puntos 7 y 8). |
| [`hito_3/`](hito_3/) | Error por Richardson y orden de convergencia | Sin empezar. |
| [`hito_4/`](hito_4/) | Problemas lineales y regiones de estabilidad | Sin empezar. |

## Cómo ejecutar

Los scripts del hito 1 no importan nada del repositorio y se lanzan directamente.

El del hito 2 importa de `active/` y hay que lanzarlo desde la raíz del repositorio:

```text
python -m hitos.hito_2.Orbita_Kepler
```

La explicación está en el [`README.md`](../README.md) de la raíz, apartado "Cómo ejecutar".
