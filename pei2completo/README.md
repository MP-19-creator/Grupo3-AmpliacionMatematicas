# Proyecto PEI 2 — Dinámica Orbital 3D en el CR3BP: Soluciones Periódicas, Variedades y Conexión GMAT vía MCP

**Asignatura:** Ampliación de Matemáticas 1  
**Máster:** Máster Universitario en Sistemas Espaciales (MUSE) — ETSIAE, UPM  
**Curso:** 2026–2027  
**Coordinador:** Dr. Juan Antonio Hernández Ramos  

---

## 1. Estructura del Proyecto

El desarrollo sigue una arquitectura estricta en tres pilares desacoplados, complementada con los hitos semanales del curso:

```text
pei2completo/
├── ArchivosNecesarios/
│   ├── PEI2.pdf                       # Enunciado oficial de la PEI 2
│   └── MUSE_weekly_milestones.pdf     # Guía oficial de hitos semanales
├── active/                            # Código de producción (3 capas)
│   ├── space_physics/                 # Pilar 1: Formulación analítica y física del CR3BP 3D
│   ├── numerical_engine/              # Pilar 2: Solucionadores, disparo simétrico, continuación y variedades
│   └── gui_orchestrator/              # Pilar 3: Interfaz gráfica 3D y cliente MCP / NASA GMAT
├── hitos/                             # Hitos semanales del primer semestre (desde el 5 en adelante)
│   ├── hito_5/                        # Formulación e integración del CR3BP
│   ├── hito_6/                        # Puntos de Lagrange, estabilidad y Runge-Kutta embebido
│   └── hito_7/                        # Órbitas periódicas (Arenstorf), familias, esfuerzo y MCP/GMAT
├── presentacion/                      # Material para la defensa oral colegiada (20 min)
└── README.md                          # Este documento
```

---

## 2. Marco Físico y Matemático (CR3BP 3D)

### 2.1 Ecuaciones de Movimiento
En el sistema sinódico con velocidad angular normalizada $\boldsymbol{\omega} = [0, 0, 1]^T$, baricentro en el origen y masas primarias en $\mathbf{r}_{m_1} = [-\mu, 0, 0]^T$, $\mathbf{r}_{m_2} = [1-\mu, 0, 0]^T$:

$$\begin{cases}
\ddot{x} - 2\dot{y} = \dfrac{\partial\Omega}{\partial x} \\
\ddot{y} + 2\dot{x} = \dfrac{\partial\Omega}{\partial y} \\
\ddot{z} = \dfrac{\partial\Omega}{\partial z}
\end{cases}$$

con el pseudopotencial efectivo:
$$\Omega(x, y, z) = \frac{1}{2}(x^2 + y^2) + \frac{1-\mu}{r_1} + \frac{\mu}{r_2}$$
y distancias:
$$r_1 = \sqrt{(x+\mu)^2 + y^2 + z^2}, \quad r_2 = \sqrt{(x - 1 + \mu)^2 + y^2 + z^2}$$

### 2.2 Constante de Jacobi y ZVS
$$C_J = 2\Omega(x, y, z) - v^2 = \text{cte}, \quad v^2 = \dot{x}^2 + \dot{y}^2 + \dot{z}^2 \ge 0$$
Las Superficies de Velocidad Cero ($2\Omega(x,y,z) = C_J$) definen los límites de las zonas accesibles al vehículo espacial.

### 2.3 Puntos de Lagrange ($L_1 \dots L_5$)
- Colineales ($L_1, L_2, L_3$ sobre el eje $x$): puntos centro-silla inestables.
- Triangulares ($L_4, L_5$ en triángulo equilátero): espectralmente estables según el criterio de Routh ($\mu < \mu_R \approx 0.03852$).

### 2.4 Frecuencias y Familias Orbitales
- Frecuencia vertical: $\nu = \sqrt{\dfrac{1-\mu}{r_1^3} + \dfrac{\mu}{r_2^3}}$
- Frecuencia planar: $\omega_p$
- **Órbitas de Lyapunov**: periódicas en el plano ($z=0$).
- **Lissajous**: cuasiperiódicas tridimensionales (toros $T^2$).
- **Órbitas Halo 3D**: bifurcación 1:1 resonante ($\omega_p \approx \nu$) que genera ramas simétricas Norte ($z>0$) y Sur ($z<0$).
- **Órbitas NRHO**: miembros de la familia Halo con gran amplitud vertical en Tierra-Luna (base de la estación *Lunar Gateway* del programa Artemis).

### 2.5 Variedades Invariantes ($W^s, W^u$)
Tubos de transporte gravitatorio asintóticos para diseño de trayectorias de bajo coste propulsivo ($\Delta V \approx 0$).

---

## 3. Plan de Hitos Semanales

- **Hito 5 (CR3BP Básico):**
  - Implementación del campo de velocidades/aceleraciones del CR3BP.
  - Integración numérica de prueba y cálculo de la constante de Jacobi.
- **Hito 6 (Puntos de Lagrange y Estabilidad):**
  - Implementación de Runge-Kutta embebido de alto orden (Dormand-Prince / RK45).
  - Cálculo de las posiciones exactas de $L_1 \dots L_5$ ($\nabla \Omega = \mathbf{0}$).
  - Análisis espectral de estabilidad y linealización.
  - Órbitas preliminares en torno a los puntos de equilibrio.
- **Hito 7 (Familias Periódicas, Arenstorf y Conexión MCP / GMAT):**
  - Algoritmo de disparo diferencial simétrico en $\mathbb{R}^6$.
  - Órbita de Arenstorf y comparación entre familias de integradores.
  - Generación de scripts de misión de NASA GMAT (`.script`).
  - Conexión vía protocolo abierto MCP (Model Context Protocol).
  - Comparación de residuos $\| \mathbf{r}_{CR3BP} - \mathbf{r}_{GMAT} \|$ y deriva de $C_J$.

---

## 4. Rúbrica Oficial de Evaluación (50% Calificación Progresiva)
- **Bloque 1 (25%):** Rigor Dinámico y Formulación Analítica.
- **Bloque 2 (25%):** Algoritmos Numéricos y Corrección Diferencial.
- **Bloque 3 (25%):** Orquestación Software, GUI e Interoperabilidad (MCP / NASA GMAT).
- **Bloque 4 (25%):** Defensa Oral Colegiada (20 min) y Dominio Individual (15 min).
