# Technical defence checklist

Likely questions in the 15-minute individual round, with short answers grounded in our code. Numbers are for I = (1, 2, 3), Ω = 1 unless stated.

## Physics and intermediate-axis dynamics

**Why is 2T conserved? And L²?** Multiply equation k by ω_k (by I_k·ω_k for L²) and add. The right-hand side is ω₁ω₂ω₃ times (I₂−I₃)+(I₃−I₁)+(I₁−I₂) = 0, or I₁(I₂−I₃)+I₂(I₃−I₁)+I₃(I₁−I₂) = 0.

**Is L conserved as a vector?** In the inertial frame, yes (no torque). In body axes only its modulus is constant. The code checks it: `Inertial_angular_momentum()` returns R(q)·I·ω, a constant vector.

**Why does a centre not prove stability?** The linearisation only describes the linear terms; a nonlinear term can make a centre spiral in or out. Stability of axes 1 and 3 comes from V = L² − I_k·2T: conserved, and definite in the other two components, so it is a Lyapunov function.

**What are the eigenvalues at the intermediate axis?** ±Ω·√[(I₃−I₂)(I₂−I₁)/(I₁I₃)] = ±0.577, plus 0 along the spin axis.

**Why does the flip time depend on ε?** The perturbation grows like ε·e^{λt} until it is O(1): t ≈ (1/λ)·ln(1/ε) + const. Measured slope 1.732 s = 1/λ (flips at 14.9, 34.9 and 50.8 s for ε = 10⁻³, 10⁻⁸ and 10⁻¹²).

**What is the period?** P = 4K(k)/ν (Landau and Lifshitz §37), with K computed by the AGM (`Elliptic_K`). Exact 55.062 s, measured 55.062 s. It is infinite on the separatrix.

**Is Explorer 1 the intermediate-axis effect?** No. It is the major-axis rule: energy dissipation at constant |L| drives the body to minimum energy T = L²/(2I_max). A rigid model cannot show it.

**What happens if I₁ = I₂?** The body is axisymmetric: the intermediate axis is no longer unique and there is no saddle. With I₁ ≈ I₂, λ → 0 and the flip takes longer and longer.

**Why I₁ + I₂ ≥ I₃?** The triangle inequality for real mass distributions (I₁ + I₂ − I₃ = 2∫z²dm ≥ 0). The GUI warns when it fails (`Is_physical`).

## Numerical methods

**Order of each scheme, and how you measured it.** Euler 1, CN 2, RK4 4 in theory. Richardson with N and 2N on the rigid body: 1.02, 2.00, 4.02. The slope of log D against log N is −q; the fitting range is chosen automatically where local orders vary by less than 15 %.

**Why Richardson works without an exact solution.** U_N − U_2N = E_N − E_2N = E_N(1 − 2^−q) when E ∝ Δt^q, so the difference measures the error.

**Why did the convergence curve stop going down?** Below about 10⁻¹² the difference is rounding, not truncation (RK4 at N = 5120: D = 2.1·10⁻¹²).

**How is Crank-Nicolson solved?** Newton on G(X) = X − U − Δt/2·[F(U) + F(X)] with G′ = I − Δt/2·J(X), using the exact Jacobian, an Euler predictor, tolerance 1e-10 and 25 iterations.

**Why not fixed-point iteration?** It converges only when Δt·ρ(J)/2 < 1, and with an absolute tolerance of 1e-6 it returned the Euler predictor for small Δt (CN identical to Euler at N = 16 000).

**How does the adaptive step choose Δt?** Step doubling: e = |U₂ − U₁|/(2^q − 1), accept if e ≤ tol·(1 + |U₂|), next Δt = 0.9·Δt·(tol/e)^{1/(q+1)}, limited to [0.2, 2]·Δt.

**Finite-difference Jacobian: which h, and what error?** Central differences, h = 1e-3. The error is h²/6·F‴ + ε·|F|/h. Our F is bilinear, so F‴ = 0 and only rounding remains: 8·10⁻¹³ against the exact one. For a general F the optimum is h ≈ ε^{1/3}·|U|.

## Stability regions and plots

**How did you obtain the regions?** By running our schemes: one step of size 1 on dU/dt = λU, λ = a + ib as the real system [a −b; b a], and |U₁| on a 133 × 145 grid. The result matches the formula to ≤ 2·10⁻¹². This is the method of the professor's `Stability_Region`.

**Why the 2×2 real system?** Our Newton converts the state to float, so it would drop the imaginary part. Every rational function of A = [a −b; b a] has the same form, so |U₁| = |R(z)| exactly.

**Where are the rigid body's z = λΔt?** Axis 2: ±0.0115 (real, physical growth). Axes 1 and 3: ±0.0115i and ±0.02i. Quaternion: ±0.01i. All very close to 0.

**Why does Euler gain energy?** On the imaginary axis |1 + iy| = √(1 + y²) > 1, so every rotation mode grows at each step: 2T drifts 7 % in 80 s at Δt = 0.02.

**RK4 stability limit on the imaginary axis?** |R(iy)|² = 1 − y⁶/72 + y⁸/576 ≤ 1 up to y = 2√2, so Δt < 2√2/σ: 2.83 s for axis 3 and 4.90 s for axis 1.

**CN should conserve |q| exactly; why 4·10⁻⁶ during flips?** The trapezoidal rule is norm-preserving for dq/dt = ½Ω q only if Ω is constant over the step. At a flip ω changes fast, so Ω(ω_n) ≠ Ω(ω_{n+1}). The final error, 1.5·10⁻¹⁰ against a predicted 1.3·10⁻¹⁴, is the Newton tolerance.

**Does the numerical error trigger the flip?** No. With Δt = 0.02 all three schemes agree on the flip time to 0.3 s even with ε = 10⁻¹². What changes is the growth rate: Euler's is ln(1 + λΔt)/Δt < λ, which makes it 1.4 s late at Δt = 0.1, as predicted.

**Singularities.** CN's R(z) has a pole at z = 2 and implicit Euler's at z = 1, where I − Δt·J is singular. On the rigid body this needs Δt·λ = 2 on axis 2 (Δt = 3.46 s), beyond the GUI's range. At r = 0, Kepler is singular (not used in the PEI).

## Software architecture and GUI

**How are the layers decoupled?** Physics returns F(U, t) and F.jacobian; the engine integrates any F; the GUI imports neither and receives data and two callbacks from `PEI1.py`. Known leak: physics imports `partition`.

**What happens if the integration fails?** `Cauchy_problem` raises `Integration_stopped` with the partial solution; `integrar_trayectoria` catches it and the GUI draws what exists, with a warning. Known gap: `Newton` raises `RuntimeError`, which is not caught (backlog C).

**Why is the GUI responsive?** Heavy analyses run only when their page opens (`preparar_pagina`); the animation timer moves through precomputed results; there are step caps (100 000 explicit, 30 000 implicit) and at most 4 000 animation samples.

**Why does Crank_Nicolson exist twice?** Honest answer: the engine's version calls `Newton` with three arguments, which `Newton` does not accept. `PEI1.py` detects that and uses its own Newton step. It is the first item of our backlog.

## AI-assisted development and harness

**Did the AI write the project?** It wrote much of the code inside constraints we set: per-layer READMEs written before the engine and GUI code, interfaces fixed by the course, a bit-for-bit regression script before and after the GUI refactor, and screenshots for human review. We found and fixed its mistakes (slide 25).

**Give an example where it was wrong.** The fixed-point implicit step that silently returned Euler, found because CN and Euler gave identical numbers. Or the signature shim that hides a TypeError instead of fixing it.

**What would you do differently?** Tests on every commit instead of one-off scripts, an instructions file for the assistant in the repository, and an import graph generated automatically (backlog D and E).

**Can each of you explain any file?** Prepare: Rubén `eje_intermedio.py`; Mario `Cauchy_Problem.py`, `temporal_schemes.py`, `Errores_Convergencia.py`, `Estabilidad.py`, `NewtonRaphson.py`; Ignacio `PEI1/PEI1.py`, `gui.py` and the four page modules. Each of us should also be able to walk through `Cauchy_problem` line by line.
