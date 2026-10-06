# PEI 1 — Resumen del enunciado

Resumen de [`ArchivosNecesarios/PEI1.pdf`](../ArchivosNecesarios/PEI1.pdf): *Dinámica de actitud satelital: teorema del eje intermedio, análisis espectral y entorno reactivo en Python*. Ante cualquier duda manda el PDF.

| | |
|---|---|
| Asignatura | Ampliación de Matemáticas 1 (MUSE, ETSIAE), curso 2026–2027 |
| Coordinador | Dr. Juan Antonio Hernández Ramos |
| Modalidad | Proyecto en grupo + defensa oral individual |
| Fecha | Semana 7 |
| Peso | 50 % de la calificación progresiva |
| Nota mínima | 3.0 / 10.0 individual para poder promediar |
| Tribunal | Mínimo 2 profesores, acto público |
| Duración | 20 min de exposición + 15 min de preguntas |

## Qué se pide

Formular, analizar y simular la rotación libre de un sólido rígido asimétrico, y mostrar la inestabilidad del giro en torno al eje de inercia intermedio (efecto Dzhanibekov o teorema de la raqueta de tenis). Todo ello en un programa en Python con interfaz gráfica interactiva.

## Problema físico

Satélite rígido, sin pares exteriores, en ejes principales de inercia con I₁ < I₂ < I₃. La velocidad angular en ejes cuerpo ω = (ω₁, ω₂, ω₃) cumple las ecuaciones de Euler:

```text
dω₁/dt = (I₂ − I₃)/I₁ · ω₂ω₃
dω₂/dt = (I₃ − I₁)/I₂ · ω₃ω₁
dω₃/dt = (I₁ − I₂)/I₃ · ω₁ω₂
```

(En la forma implícita de la ecuación (2) del PDF la tercera línea dice I₃ω̇₁; es una errata, debe ser I₃ω̇₃.)

El sistema conserva dos magnitudes:

```text
2T = I₁ω₁² + I₂ω₂² + I₃ω₃²          energía cinética de rotación
L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²       módulo del momento angular
```

Cada una define un elipsoide en el espacio (ω₁, ω₂, ω₃). La trayectoria es la intersección de ambos (polhodas de Poinsot), y solo existe movimiento si 2I₁T ≤ L² ≤ 2I₃T.

## Estabilidad de los tres giros puros

Jacobiano del campo:

```text
        |        0           (I₂−I₃)/I₁·ω₃   (I₂−I₃)/I₁·ω₂ |
J(ω) =  | (I₃−I₁)/I₂·ω₃           0          (I₃−I₁)/I₂·ω₁ |
        | (I₁−I₂)/I₃·ω₂   (I₁−I₂)/I₃·ω₁           0        |
```

Linealizando en torno a cada giro puro de velocidad Ω:

| Eje de giro | Equilibrio | Autovalores | Resultado |
|---|---|---|---|
| Mínimo (I₁) | (Ω, 0, 0) | ± iΩ·√[(I₃−I₁)(I₂−I₁) / (I₂I₃)] | Centro: estable en el sentido de Lyapunov, no asintóticamente |
| Intermedio (I₂) | (0, Ω, 0) | ± Ω·√[(I₃−I₂)(I₂−I₁) / (I₁I₃)] | Punto de silla: inestable |
| Máximo (I₃) | (0, 0, Ω) | ± iΩ·√[(I₃−I₂)(I₃−I₁) / (I₁I₂)] | Centro: estable en el sentido de Lyapunov |

El autovalor real positivo del eje intermedio es lo que produce el volteo periódico de 180°.

## Programa a entregar

Tres capas separadas, que en este repositorio están en [`active/`](../active/):

| Capa | Qué debe hacer |
|---|---|
| Física (`space.physics`) | Ecuaciones del problema, Jacobiano exacto y comprobación de 2T y L². |
| Matemática y algorítmica (`numerical.engine`) | Esquemas temporales de paso simple y adaptativo (Euler, Crank-Nicolson, RK4), estimación del error por extrapolación de Richardson y regiones de estabilidad \|R(z)\| ≤ 1. |
| Visualización (`gui.reactive`) | Cuadro de mando interactivo con varios paneles (p. ej. `matplotlib.widgets`). |

La interfaz debe permitir, en tiempo real:

1. Cambiar con deslizadores I₁, I₂, I₃, la velocidad angular inicial Ω y el paso temporal Δt.
2. Cambiar de integrador y comparar la deriva numérica de la energía ΔT(t) y del momento ΔL(t).
3. Ver a la vez el espacio de fases 3D con las superficies de Poinsot y la separatriz, y la animación 3D de la orientación del satélite durante el volteo.

## Defensa

- **Exposición del grupo (20 min):** fundamentos del teorema, derivación de los invariantes, arquitectura de clases del programa y demostración en directo con la interfaz.
- **Preguntas individuales (15 min):** a cada integrante, sobre la deducción matemática, los esquemas numéricos, el tratamiento de singularidades o el código.
- La nota es **individual**, aunque el trabajo sea de grupo.

## Rúbrica

| Bloque | Qué se valora | Peso |
|---|---|---|
| 1. Rigor dinámico y formulación analítica | Conservación de 2T y L², linealización de los tres equilibrios, demostración de la inestabilidad del eje intermedio y geometría de Poinsot. | 25 % |
| 2. Métodos numéricos y conservaciones físicas | Integradores de un paso (Euler, Crank-Nicolson, RK4), convergencia con Richardson, deriva de los invariantes y estabilidad numérica absoluta. | 25 % |
| 3. Ingeniería del software y GUI interactiva | Modularidad y desacoplo en tres capas, visualización sincronizada del espacio de fases 3D y estabilidad de la ejecución en vivo. | 25 % |
| 4. Defensa oral y dominio individual | Precisión en la exposición, razonamiento ante preguntas imprevistas y dominio del código del repositorio. | 25 % |
