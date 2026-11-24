# Slide-by-slide guide — PEI 1 final presentation

20 minutes, three speakers, 26 presented slides plus 5 backup slides (27–31). The full spoken script, with timings, is in the speaker notes of `PEI1_final.pptx` (and in `PEI1_final.deck.md`). This guide says what each slide is for, where its evidence lives and what the speaker must master.

| Speaker | Slides | Time |
|---|---|---|
| Rubén Núñez — Physics | 1–8 | 0:00–6:00 |
| Mario Penin — Numerical engine | 9–16 | 6:00–12:15 |
| Ignacio Pérez — Software, GUI, AI, close | 17–26 | 12:15–20:00 (live demo 15:15–17:15) |

## Rubén — Physics

**1 · Title.** Opens the talk and announces the three parts. Evidence: the polhodes on the cover were integrated with our own RK4 (`figuras/portada.py`).

**2 · A wing nut flips in orbit with no torque acting on it.** Sets the scope. Dzhanibekov (rigid, torque-free) is what we model; Explorer 1 (energy dissipation) is outside a rigid model. Master: why dissipation drives a body to its maximum axis (energy falls at fixed |L|, and T = L²/2I is minimum for the largest I). PENDING: two real photos.

**3 · Section divider.**

**4 · Three coupled equations.** Euler equations in principal axes; the state is ω, and the program adds the quaternion (7 states). Evidence: `eje_intermedio.py`, `PEI1()` and `Attitude_equations()`. Master: where the equations come from (dL/dt = 0 in the inertial frame, written in the rotating body frame); why a quaternion and not Euler angles (no gimbal lock).

**5 · Two invariants, two ellipsoids.** One-line proof of conservation of 2T and L²; the polhode is the intersection; condition 2T·I₁ ≤ L² ≤ 2T·I₃. Evidence: GUI page Motion. Master: semi-axes √(2T/I_k) and |L|/I_k.

**6 · Linearisation table.** Eigenvalues at the three pure spins: ±0.577i, ±0.577, ±1i for I = (1, 2, 3), Ω = 1. Evidence: `Linear_eigenvalues()`. Master: the third eigenvalue is 0 (along the spin axis), and why.

**7 · A linear centre proves nothing.** V = L² − I_k·2T is conserved and definite for axes 1 and 3, so it is a Lyapunov function: nonlinear stability. Indefinite for axis 2; V = 0 are the separatrix planes. Evidence: `Energy_Casimir()`. This is the slide most likely to be probed.

**8 · The flip follows the separatrix.** Separatrix planes ω₃ = ±c·ω₁; exact period 4K(k)/ν = 55.062 s equals the measured one; first flip at 14.9, 34.9 and 50.8 s for ε = 10⁻³, 10⁻⁸ and 10⁻¹²; slope 1.732 s = 1/λ. Evidence: `Polhode_period()`, `Elliptic_K()`, the flip-time runs. Master: why t ≈ (1/λ)·ln(1/ε) (linear growth ε·e^{λt} reaches O(1)).

## Mario — Numerical engine

**9 · Section divider.**

**10 · One engine integrates any F(U, t).** Process: F → scheme → `Cauchy_problem` → `Integration_stopped`. Master: the adaptive step (backup 29) and why the engine is problem-agnostic.

**11 · Fixed point vs Newton.** The first implicit solver failed in two documented ways; the current one is Newton with G′ = I − Δt/2·J. Evidence: `paso_crank_nicolson()` in `PEI1/PEI1.py`, limitations table in `numerical_engine/README.md`. Master: why the fixed point needs Δt·ρ(J)/2 < 1 (contraction mapping).

**12 · Richardson measures the order.** D = |U_N − U_2N| ≈ E_N(1 − 2^−q); orders 1.02, 2.00, 4.02 on the rigid body; automatic choice of the straight range. Evidence: GUI page Precision. Master: why the slope is −q, and why the range has to stop near 10⁻¹².

**13 · Stability regions measured by running our schemes.** One real step of size 1 on dU/dt = λU, λ = a + ib as the real 2×2 system. Agreement with the formula to ≤ 2·10⁻¹². Evidence: `figuras/regiones_numericas.py` (method of `Stability_Region`, jahrWork/MUSE_orbits_S1). Master: why |U₁| = |R(z)| for that matrix (every rational function of A has the form [α −β; β α]).

**14 · The rigid body in the regions.** z = λΔt values; |R(iy)| = √(1 + y²) for Euler, 1 for CN, ≤ 1 for RK4 up to y = 2√2. Evidence: `eje_imaginario.png`. Master: |R_RK4(iy)|² = 1 − y⁶/72 + y⁸/576.

**15 · R(z) predicts the drift.** Euler ‖q‖ − 1: 0.2405 predicted, 0.2405 simulated. CN gap explained by the Newton tolerance; CN peaks at flips because Ω(ω) changes within the step. Evidence: GUI pages Conservation and Stability.

**16 · Three limits.** The saddle amplifies errors; Euler's growth rate ln(1 + λΔt)/Δt < λ makes its flip 1.4 s late (ε = 10⁻¹², Δt = 0.1); singular points z = 2 (CN) and z = 1 (implicit Euler); rounding floor near 10⁻¹².

## Ignacio — Software, GUI, AI, close

**17 · Section divider.**

**18 · Phase map (interactive).** Ten phases with real dates; each node is clickable (whole box) and jumps to its slide; the eyebrow of slides 19–25 jumps back. Works in slideshow mode only.

**19 · Architecture.** Three layers plus `PEI1.py`; the GUI imports neither layer and receives data and two callbacks. Admit the leak: physics imports `partition()` from the engine.

**20 · One click on Calcular.** Real call chain: `leer_parametros` → `al_calcular` → `integrar_trayectoria` → `preparar_pagina` → `dibujar`. Master: lazy computation per page; the timer never re-integrates.

**21 · GUI tour.** Four pages, each answering one question of the statement. Screenshots captured by `figuras/capturar_gui.py`.

**22 · Live demo.** Script: intermediate axis with RK4 → axes 1 and 3 → Euler on the conservation page. PENDING: choose and rehearse the unusual cases.

**23 · Timeline.** 51 commits, 3 authors; 27 Oct page split (+1189 lines), 2 Nov rewrite (−1443 lines). Dots placed to scale.

**24 · The harness.** In place versus proposed. Do not claim more than the left column.

**25 · Where the AI got it wrong.** Three documented episodes. PENDING: the team's own prompt exchanges.

**26 · Close.** Bookends the wing nut.

## Backup (not presented)

**27** divider · **28** finite-difference Jacobian (exact for our bilinear F) · **29** adaptive step · **30** known defects · **31** knowledge map (PENDING).

## How to rebuild the deck

From the repository root, in the `muse` environment:

```text
python presentacion/figuras/capturar_gui.py        # real GUI screenshots
python presentacion/figuras/regiones_numericas.py  # measured stability regions
python presentacion/figuras/preparar_recursos.py   # logos and crops
python presentacion/figuras/portada.py             # cover polhodes
python presentacion/inyectar_contenido.py          # spec -> build script
```

Then build with `/ppt construir presentacion/PEI1_final.deck.md`, and run `python presentacion/enlazar.py presentacion/PEI1_final.pptx` before the lint.
