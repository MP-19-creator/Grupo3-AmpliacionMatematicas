---
deck: The Intermediate Axis Theorem
audience: The PEI 1 examining board (at least two lecturers, among them the author of the course milestones). They know rigid-body dynamics and one-step schemes by heart and walk in wanting to know whether each of us understands the physics, the numerics and the code we are submitting, and whether the software is ours.
register: presented
structure: Ink for the opening, the three speaker dividers and the close; white paper for every evidence slide in between, framed by the MUSE header (section eyebrow left, UPM, ETSIAE and IDR logos right) and footer.
motif: A three-pill tracker in the footer (Physics, Engine, Software) with the current speaker's part filled in accent; every equation, number and figure on a slide is traced to a file in the repository in a caption line.
---

## Slide 1
layout: title
Brief: The one thing is the question the deck answers; a dark ground with the MUSE logo and a phase-space polhode drawn as a mark, so the opening already shows the object we study (reference: the preliminary deck's dark cover, kept).
Title: The Intermediate Axis Theorem
Subtitle: Rigid-body dynamics, spectral analysis and a reactive Python tool
Notes:
[Rubén · 0:00–0:20] Good morning. We are Rubén Núñez, Mario Penin and Ignacio Pérez. In the next twenty minutes we will show you why a spinning body flips when it turns about its intermediate axis, how our numerical engine reproduces that flip, and how we built and corrected the software around it. I will start with the physics, Mario will take the numerical engine, and Ignacio will close with the software and the way we worked.

## Slide 2
layout: composed
Brief: One thing: the flip is real and it needs no torque; a resolved comparison, Dzhanibekov (the effect we model) against Explorer 1 (a look-alike our model cannot explain), because the contrast defines the scope of a torque-free rigid model before any equation (reference: a two-panel case comparison in an engineering failure report).
Title: A wing nut flips in orbit with no torque acting on it
Visual: A still frame of the Dzhanibekov wing nut in orbit, and a photograph of Explorer 1 (both real images, to be placed by the team).
Block: comparison
! Dzhanibekov, Salyut 7, 1985 | A wing nut spinning about its intermediate axis reverses every few seconds. Rigid, torque-free: our model.
Explorer 1, 1958 | Spin about the minimum axis decays to the maximum axis. Cause: internal energy dissipation, outside a rigid model.
Notes:
[Rubén · 0:20–1:10] In 1985 the cosmonaut Vladimir Dzhanibekov unscrewed a wing nut on Salyut 7 and watched it fly off spinning. Every few seconds it turned over by half a turn and kept spinning the other way. No torque acts on it. That is the effect we model. The preliminary version of this talk opened with Explorer 1, and we want to be precise about why it is different. Explorer 1 started spinning about its axis of minimum inertia and ended up tumbling about the maximum axis, because its flexible antennas dissipated energy. A rigid, torque-free model conserves energy, so it cannot reproduce Explorer 1. It can reproduce the wing nut, and that is the scope of everything that follows.

## Slide 3
layout: section
Brief: One thing: the first part starts; ink divider naming the part and the speaker, the footer tracker shows Physics filled (reference: chapter openers in a printed lecture-notes series).
Title: 1 · Physics · Rubén Núñez
Notes:
[Rubén · 1:10–1:15] First part: the physics and the analytical results the rest of the project is built on.

## Slide 4
layout: composed
Brief: One thing: three first-order equations hold the whole problem; the equations set large on the left with the GUI's box beside them, because the audience must tie each I_k to a real axis of a real body before any analysis (reference: a textbook figure pairing an equation block with its labelled body).
Title: Three coupled equations describe a torque-free rigid body
Visual: Crop of the GUI's rotating box (homogeneous box with the inertias I = (1, 2, 3)) from figuras/recursos/caja_eje2.png.
Block: freeform
text h1 ink at cols 1-7 rows 1-2 | Body frame, principal axes, I₁ < I₂ < I₃
text body ink at cols 1-7 rows 3-6 | I₁ dω₁/dt = (I₂ − I₃) ω₂ ω₃ / I₂ dω₂/dt = (I₃ − I₁) ω₃ ω₁ / I₃ dω₃/dt = (I₁ − I₂) ω₁ ω₂
text body muted at cols 1-7 rows 7-9 | State U = ω = (ω₁, ω₂, ω₃). Attitude added through a quaternion: dq/dt = ½ q ⊗ (0, ω).
Notes:
[Rubén · 1:15–2:05] We work in the body frame, along the principal axes, ordered so that I one is smaller than I two, which is smaller than I three. Without external torques, Euler's equations reduce to these three lines. Each component of the angular velocity is driven by the product of the other two, with a coefficient that is a difference of inertias. That coupling is the whole story. The state is the angular velocity vector, and to animate the body we also integrate its attitude with a quaternion, so the full state in the program has seven components. The box on the right is the one the GUI draws: its sides are computed from the inertias, so I one is the long axis and I three the short one.

## Slide 5
layout: composed
Brief: One thing: two conserved quantities confine the motion to the intersection of two ellipsoids; the derivation in one line on the left and the real Poinsot plot on the right, because the geometry is the argument (reference: Landau and Lifshitz, Mechanics, section 37 figure).
Title: Two invariants confine ω to the intersection of two ellipsoids
Visual: GUI phase-space view for the intermediate axis (figuras/recursos/poinsot_eje2.png).
Block: freeform
text body ink at cols 1-6 rows 1-3 | 2T = I₁ω₁² + I₂ω₂² + I₃ω₃² / L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²
text body ink at cols 1-6 rows 4-6 | Multiply equation k by ω_k (or I_k ω_k) and add: the right-hand sides cancel because (I₂ − I₃) + (I₃ − I₁) + (I₁ − I₂) = 0.
text body muted at cols 1-6 rows 7-9 | Motion exists only if 2T·I₁ ≤ L² ≤ 2T·I₃. The polhode is the curve where both surfaces meet.
Notes:
[Rubén · 2:05–3:00] Two quantities are conserved. Twice the kinetic energy and the square of the angular momentum. The proof is one line: multiply each equation by omega k, or by I k times omega k, and add them up. The right-hand side becomes omega one, omega two, omega three times a sum of inertia differences that is identically zero. Each invariant is an ellipsoid in omega space, so the angular velocity can only move along the curve where both ellipsoids intersect. That curve is the polhode. On the right is our GUI: the purple ellipsoid is the energy, the orange one the momentum, and the dashed red curves are the separatrix we will come back to in two slides.

## Slide 6
layout: composed
Brief: One thing: linearising at the three pure spins gives centre, saddle, centre; a table, because the audience reads exact eigenvalues and needs the three rows side by side with the intermediate row leading (reference: the stability table in the PEI 1 statement, equations 9, 10 and 12).
Title: Linearised at each pure spin, only the intermediate axis is a saddle
Block: table
Spin axis | Equilibrium | Eigenvalues of J | I = (1, 2, 3), Ω = 1 | Type
Minimum I₁ | (Ω, 0, 0) | ± iΩ √[(I₃−I₁)(I₂−I₁)/(I₂I₃)] | ± 0.577 i | centre
! Intermediate I₂ | (0, Ω, 0) | ± Ω √[(I₃−I₂)(I₂−I₁)/(I₁I₃)] | ± 0.577 | saddle
Maximum I₃ | (0, 0, Ω) | ± iΩ √[(I₃−I₂)(I₃−I₁)/(I₁I₂)] | ± 1.000 i | centre
Notes:
[Rubén · 3:00–3:55] To study stability we linearise around each pure spin. The Jacobian of the Euler equations has a zero eigenvalue along the spin axis and a pair in the other two directions. For the minimum and maximum axes the product under the square root is negative, so the pair is purely imaginary: a centre, small oscillations. For the intermediate axis the two inertia differences have opposite signs, the product is positive, and we get one real positive eigenvalue: a saddle. With the inertias one, two, three and unit spin, the intermediate axis grows like e to the 0.577 t. These are exactly the numbers the GUI prints in its theory panel, computed by Linear_eigenvalues in the physics layer.

## Slide 7
layout: composed
Brief: One thing: a linear centre does not prove stability, a conserved Lyapunov function does; a three-card set with the intermediate card leading, because the same function V gives three different signs (reference: the energy-Casimir method as laid out in Marsden and Ratiu).
Title: A linear centre proves nothing; a conserved Lyapunov function does
Block: card-grid
Minimum axis | V = L² − I₁·2T = I₂(I₂−I₁)ω₂² + I₃(I₃−I₁)ω₃² / positive definite: stable
! Intermediate axis | V = L² − I₂·2T = I₁(I₁−I₂)ω₁² + I₃(I₃−I₂)ω₃² / indefinite: V = 0 are the separatrix planes
Maximum axis | V = L² − I₃·2T = I₁(I₁−I₃)ω₁² + I₂(I₂−I₃)ω₂² / negative definite: stable
Notes:
[Rubén · 3:55–4:45] Imaginary eigenvalues are not enough. A linear centre can be destroyed by the nonlinear terms, so linearisation alone cannot prove that the minimum and maximum axes are stable. What does prove it is a combination of the two invariants: V equals L squared minus I k times two T. It is conserved because both terms are. Around the minimum axis it is positive definite in the other two components, around the maximum axis negative definite, so it is a Lyapunov function and the perturbation stays bounded. Around the intermediate axis it changes sign, and its zero set is a pair of planes. That function is Energy_Casimir in our code.

## Slide 8
layout: composed
Brief: One thing: the flip is a trajectory hugging the separatrix, and its timing is predictable; the real ω(t) trace with three measured numbers beside it, because the audience should see theory and simulation agree to the digit (reference: an annotated oscilloscope trace).
Title: The flip follows the separatrix, and its timing is predictable
Visual: GUI ω(t) trace for the intermediate axis (figuras/recursos/omega_eje2.png).
Block: freeform
text body ink at cols 1-4 rows 1-3 | Separatrix: two planes ω₃ = ± c ω₁, c = √[I₁(I₂−I₁) / I₃(I₃−I₂)]
text body ink at cols 1-4 rows 4-6 | Period P = 4K(k)/ν, infinite on the separatrix. Exact 55.062 s, measured 55.062 s.
text body ink at cols 1-4 rows 7-9 | First flip ≈ (1/λ) ln(1/ε): 14.9 s, 34.9 s and 50.8 s for ε = 10⁻³, 10⁻⁸, 10⁻¹²; slope 1.732 s = 1/λ.
Notes:
[Rubén · 4:45–6:00] Here is what a flip looks like. Omega two, in green, sits at plus one, then swings to minus one in a few seconds while omega one and omega three make a short excursion, and then it waits. Near the intermediate axis the trajectory runs along the separatrix, which is the pair of planes from the previous slide. Two numbers confirm the analysis. The period from the elliptic integral, four K of k over nu, is 55.062 seconds, and the period measured between flips in the simulation is also 55.062. And the waiting time grows with the logarithm of the initial perturbation: we measured the first flip at 14.9, 34.9 and 50.8 seconds for epsilon ten to the minus three, minus eight and minus twelve, and the slope is 1.732 seconds, which is one over lambda. The instability sets the clock. Mario will now show you how we integrate this.

## Slide 9
layout: section
Brief: One thing: the second part starts; ink divider, tracker on Engine (reference: chapter openers in a printed lecture-notes series).
Title: 2 · Numerical engine · Mario Penin
Notes:
[Mario · 6:00–6:05] Second part: how the model becomes numbers, and how far we can trust them.

## Slide 10
layout: composed
Brief: One thing: the engine never knows which physics it integrates; a left-to-right process of the call chain with file names under each box, because the decoupling is a sequence of handoffs (reference: a call graph in a numerical-methods textbook).
Title: One engine integrates any F(U, t) and never sees the physics
Block: process
F(U, t) | space_physics: Euler + quaternion, exact Jacobian attached as F.jacobian
Scheme | Euler, Crank-Nicolson, RK4: U_{n+1} = method(U_n, Δt, t_n, F)
Cauchy_problem | Fixed mesh, or adaptive by step doubling (Richardson on one step)
Integration_stopped | Newton failure or non-finite state: returns the partial solution
Notes:
[Mario · 6:05–6:55] The engine is built around the interface of the course milestones. The physics layer hands over a function F of U and t. A scheme takes one step with the signature method of U, delta t, t, F. Cauchy_problem repeats that step over a mesh, which does not have to be uniform. The adaptive version takes one step of size delta t and two of size delta t over two, estimates the local error from their difference divided by two to the q minus one, and grows or shrinks the step. When something goes wrong, Newton fails or the state stops being finite, the engine raises Integration_stopped carrying everything computed so far, so the GUI can still draw the valid part instead of crashing.

## Slide 11
layout: composed
Brief: One thing: an implicit scheme is a nonlinear solve per step, and the solver choice decides whether it works; a comparison that resolves for Newton, because the first version silently failed (reference: a before and after panel in an engineering change note).
Title: An implicit step is a Newton solve, not a fixed-point loop
Block: comparison
First version: fixed point | Y ← U + Δt/2 [F(U) + F(Y)], tolerance 1e-6, no iteration cap. Converges only if Δt·ρ(J)/2 < 1; for small Δt it returned the Euler predictor (CN identical to Euler at N = 16 000).
! Current: Newton, exact Jacobian | Solve G(X) = X − U − Δt/2 [F(U) + F(X)] = 0 with G′ = I − Δt/2 J(X). Euler predictor, tolerance 1e-10, 25 iterations, failure raised as an exception.
Notes:
[Mario · 6:55–7:45] Crank-Nicolson is implicit, so each step means solving a nonlinear equation for the new state. Our first version used a fixed-point iteration. We documented two failures in the engine README. For large steps it only converges when delta t times the spectral radius over two is below one. For small steps the Euler predictor already satisfied the absolute tolerance, so the loop never iterated, and Crank-Nicolson gave exactly the same numbers as explicit Euler. The current version solves G of X equal to zero with Newton, using the exact Jacobian the physics layer provides: the identity minus delta t over two times J. It stops at ten to the minus ten or after twenty-five iterations, and a failure becomes an exception.

## Slide 12
layout: composed
Brief: One thing: we measure each scheme's order on the rigid body itself, without an exact solution; the real convergence plot with the three slopes direct-labelled, because the slope is the claim (reference: a log-log convergence figure in Hairer, Nørsett and Wanner).
Title: Richardson measures the order on the rigid body itself
Visual: GUI convergence plot and Richardson-versus-reference error (figuras/recursos/convergencia.png, richardson.png).
Block: freeform
text body ink at cols 1-4 rows 1-3 | D = |U_N(t_f) − U_2N(t_f)| ≈ E_N (1 − 2^−q): no exact solution needed.
text body ink at cols 1-4 rows 4-6 | Measured order, intermediate axis, t_f = 20: Euler 1.02, Crank-Nicolson 2.00, RK4 4.02.
text body muted at cols 1-4 rows 7-9 | The fitted range is chosen automatically: the longest run where the local order log₂(D_k / D_k+1) stays within 15 %.
Notes:
[Mario · 7:45–8:40] There is no closed-form solution to compare against, so we use Richardson extrapolation. We integrate with N and with 2N steps. For a scheme of order q, their difference D equals the error times one minus two to the minus q, so the logarithm of D against the logarithm of N is a straight line of slope minus q. On the rigid body, around the intermediate axis, we measure 1.02 for Euler, 2.00 for Crank-Nicolson and 4.02 for RK4. The fitting window is not hand-picked: the code keeps the longest run of meshes where the local order changes by less than fifteen percent. On the right, the error Richardson predicts for RK4 lies on top of the error against a reference eight times finer.

## Slide 13
layout: composed
Brief: One thing: these regions come from running our schemes, not from the textbook formula; the four measured regions with the formula dashed on top, because coincidence of the two is the evidence (reference: the Stability_Region routine in jahrWork/MUSE_orbits_S1, applied to our own code).
Title: We measured the stability regions by running our own schemes
Visual: figuras/regiones_numericas.png (generated by figuras/regiones_numericas.py).
Block: freeform
text body ink at cols 1-12 rows 1-2 | One step of size 1 on dU/dt = λU from U₀ = 1, for every z = λ on a 133 × 145 grid. |U₁| is the amplification. Our Newton is real-valued, so λ = a + ib runs as the real system A = [a −b; b a].
text caption muted at cols 1-12 rows 11-12 | Largest gap between measured |U₁| and the formula |R(z)|: Euler 3·10⁻¹⁶, implicit Euler 2·10⁻¹² (finite-difference Jacobian), Crank-Nicolson 2·10⁻¹⁴, RK4 1·10⁻¹⁴. One failed step: implicit Euler at z = 1, where the system is singular.
Notes:
[Mario · 8:40–9:35] The statement asks for the regions where the absolute value of R of z is at most one. We did not want to plot four formulas from a book, so we measured them. Following the professor's Stability_Region routine, we take one step of size one on the test equation and read the amplification. Our Newton works with real numbers, so a complex lambda is written as the equivalent two by two real system, which gives exactly the same modulus. The shaded areas are measured, the dashed lines are the formulas, and they agree to ten to the minus twelve or better. The implicit Euler panel goes through our finite-difference Jacobian, and its one failed point is z equal to one, where the linear system is singular.

## Slide 14
layout: composed
Brief: One thing: the rigid body's modes sit almost on the imaginary axis, where the three schemes behave in three different ways; the |R(iy)| curve with the RK4 limit marked, because that axis is where the physics lives (reference: the imaginary-axis panel already in our GUI's stability page).
Title: Rotation modes live on the imaginary axis, where the schemes part ways
Visual: figuras/eje_imaginario.png.
Block: freeform
text body ink at cols 1-4 rows 1-3 | z = λΔt with Δt = 0.02: ± 0.0115 (axis 2, real), ± 0.0115 i and ± 0.02 i (axes 1, 3), ± 0.01 i (quaternion).
text body ink at cols 1-4 rows 4-6 | Euler |R(iy)| = √(1 + y²) > 1: every rotation mode grows. Crank-Nicolson: exactly 1. RK4: below 1 up to y = 2√2.
text body muted at cols 1-4 rows 7-9 | RK4 stays stable on axis 3 for Δt < 2√2/σ = 2.83 s; Euler is never stable there.
Notes:
[Mario · 9:35–10:30] Now we place the rigid body inside those regions. Each eigenvalue of the Jacobian times the step gives a point z. Around the minimum and maximum axes, and for the quaternion kinematics, those points are purely imaginary. Around the intermediate axis they are real, and that real growth is physical, every scheme must reproduce it. On the imaginary axis the three schemes differ completely. Euler multiplies each rotation mode by the square root of one plus y squared at every step, so it always gains energy. Crank-Nicolson has modulus exactly one. RK4 damps very slightly and stays stable up to y equal to two root two, which for the maximum axis means a step of 2.83 seconds.

## Slide 15
layout: composed
Brief: One thing: R(z) predicts the drift we observe, to the digit; a table of the three schemes with the Euler row leading, because the prediction and the measurement sit side by side (reference: the prediction-versus-simulation table on our GUI's stability page).
Title: R(z) predicts the drift the simulation shows
Block: table
Scheme | max drift of 2T and L² | ‖q(t_f)‖ − 1 predicted by ∏ R(z_n) | ‖q(t_f)‖ − 1 simulated
! Euler | 7.3·10⁻² | 2.405·10⁻¹ | 2.405·10⁻¹
Crank-Nicolson | 3.3·10⁻⁵ | −1.3·10⁻¹⁴ | −1.5·10⁻¹⁰
RK4 | 1.1·10⁻¹⁰ | −3.2·10⁻¹¹ | −3.9·10⁻¹¹
Notes:
[Mario · 10:30–11:25] This is the test of the whole argument. Intermediate axis, delta t of 0.02, eighty seconds. For Euler, multiplying the amplification factor of the quaternion mode over every step predicts a norm error of 0.2405 at the end, and the simulation gives 0.2405. Energy and momentum drift by seven percent. RK4 is predicted and measured at a few times ten to the minus eleven. Crank-Nicolson is predicted at ten to the minus fourteen and measured at ten to the minus ten: the gap is our Newton tolerance. And during each flip its quaternion norm error rises to four times ten to the minus six and comes back, because the trapezoidal rule only preserves the norm when the matrix Omega of omega is the same at both ends of the step. During a flip omega changes fast, so it is not.

## Slide 16
layout: composed
Brief: One thing: the numerics have three hard limits we can name and measure; a three-card set with the saddle card leading, because each limit has a distinct cause (reference: the limitations table in our numerical_engine README).
Title: Three limits we can name, and measure
Block: card-grid
! The saddle amplifies errors too | Any error along the unstable direction grows like e^{λt}, just as ε does. Euler's growth rate ln(1 + λΔt)/Δt is lower than λ: with ε = 10⁻¹² and Δt = 0.1 its first flip comes 1.4 s late.
Singular implicit steps | Crank-Nicolson's R(z) has a pole at z = 2; implicit Euler at z = 1. There, I − Δt J cannot be inverted and the step fails.
Floating point | Richardson differences stop falling near 10⁻¹² (RK4, N = 5120): below that, rounding dominates truncation.
Notes:
[Mario · 11:25–12:15] We close the engine with its limits. First, the intermediate axis is a saddle for errors as well as for perturbations. With a step of 0.02 all three schemes agree on the flip time to three tenths of a second, even with epsilon at ten to the minus twelve. But Euler grows at the rate log of one plus lambda delta t over delta t, which is below lambda, so with a step of 0.1 and that epsilon its flip arrives 1.4 seconds late, exactly what that rate predicts. Second, the implicit schemes have singular points: z equal to two for Crank-Nicolson and z equal to one for implicit Euler. Third, below about ten to the minus twelve the Richardson differences hit rounding error, so the convergence fit has to stop there. Ignacio will now show you the software that ties this together.

## Slide 17
layout: section
Brief: One thing: the third part starts; ink divider, tracker on Software (reference: chapter openers in a printed lecture-notes series).
Title: 3 · Software, GUI and AI · Ignacio Pérez
Notes:
[Ignacio · 12:15–12:20] Third part: how the application is built, what it shows, and how we built it with an AI assistant.

## Slide 18
layout: composed
Brief: One thing: the project went through ten phases and each one maps to a part of this talk; an interactive map of ten nodes anchored to real dates, each node a hyperlink to its slide and every software slide linking back, because the examiners can jump to any phase during questions (reference: a clickable table of contents in a technical report PDF).
Title: Ten phases, one map: click any phase to jump to its evidence
Block: process
Physical problem | 24 Sep | 2
Analytical model | 6 Oct | 4
Numerical formulation | 28 Sep – 8 Oct | 10
Software architecture | 6 Oct | 19
Numerical implementation | 24 – 25 Oct | 13
GUI development | 25 Oct – 2 Nov | 21
Integration | 27 Oct | 20
Testing and validation | 28 Oct | 15
Debugging and iteration | 24 Oct – 2 Nov | 25
Final application | 2 Nov | 22
Notes:
[Ignacio · 12:20–13:00] This map is the backbone of my part, and it is interactive: each phase is a link to the slide that holds its evidence, and every slide in this section has a link back here. The phases are the ones any engineering project goes through, from defining the problem to the final application, but the dates come from our own history. We defined the problem and the model at the end of September, formulated the numerics through the milestones, reorganised everything into three layers on the sixth of October, and spent the last two weeks implementing, testing and rewriting the interface. If you want to see the evidence behind any phase during the questions, click it.

## Slide 19
layout: composed
Brief: One thing: three layers, one orchestrator, and dependencies that point one way; a drawn architecture with arrows, because the direction of the arrows is the design decision (reference: a C4-style container diagram).
Title: Three layers, one orchestrator: the GUI imports neither physics nor engine
Block: tree
PEI1.py (orchestrator)
  space_physics: F(U, t), F.jacobian, invariants, Poinsot geometry
  numerical_engine: schemes, Cauchy_problem, Richardson, R(z)
  ! gui_reactive: four pages, receives data and two callbacks
Notes:
[Ignacio · 13:00–13:50] The statement asks for three decoupled layers. Physics only knows the problem: give it a state and it returns the derivative, the Jacobian and the invariants. The engine only knows how to integrate a function it is handed. The GUI is the one we were most careful with: it does not import the physics or the engine at all. It receives plain data and two callbacks, compute and prepare page, from the main program PEI1.py, which is the only file that knows all three. There is one leak we found while preparing this talk: the physics layer imports the partition helper from the engine. It is harmless, but it breaks the rule, and it is on our backlog.

## Slide 20
layout: composed
Brief: One thing: one click travels a fixed path through named functions; a numbered process of the real call chain, because an examiner can ask which function runs at each step (reference: a sequence diagram in a software design document).
Title: One click on Calcular follows one path through named functions
Block: process
leer_parametros | GUI reads sliders and selectors: numbers and a method name, never a function
al_calcular | callback into PEI1.py: picks the scheme, builds F and U₀
integrar_trayectoria | Cauchy_problem with protection: partial result and a warning if it stops
preparar_pagina | invariants, regions, Richardson computed only when a page needs them
dibujar | each page draws data; the timer only moves the current instant
Notes:
[Ignacio · 13:50–14:30] This is what happens when you press Calcular. The GUI reads the sliders and passes numbers and the name of the method, never a function. The callback in PEI1.py chooses the scheme, builds F and the initial condition, and integrates through a protected wrapper that returns whatever was computed if the integration stops. The expensive analyses, comparing three schemes or the Richardson study, are computed only when you open the page that needs them. Finally each page draws, and the animation timer only moves a marker through results that already exist. It never integrates again.

## Slide 21
layout: composed
Brief: One thing: each of the four pages answers one question of the statement; four real screenshots in a row, each captioned with its question, because the GUI is evidence, not decoration (reference: a product tour strip in a software release note).
Title: Four pages, each answering one question of the statement
Visual: The four real GUI pages (figuras/recursos/gui_p1.png to gui_p4.png).
Block: card-grid
Motion | What does the body do? Box, Poinsot surfaces, separatrix, ω(t)
Conservation | How much do 2T, L² and |q| drift with each scheme?
! Stability | Where do the modes z = λΔt fall relative to |R(z)| ≤ 1?
Precision | What order does each scheme reach, measured by Richardson?
Notes:
[Ignacio · 14:30–15:15] The interface has four pages and each one answers one requirement of the statement. Motion shows the body turning in the inertial frame, the Poinsot ellipsoids with the separatrix and the angular velocity in time. Conservation compares the drift of energy, momentum and quaternion norm for the three schemes on exactly the same problem. Stability, the one I would highlight, places the eigenvalues of the actual state on top of the stability regions while the animation runs, and prints the prediction you saw in Mario's table. Precision runs the Richardson study. All the screenshots in this talk are captured from the real program by a script in the repository.

## Slide 22
layout: composed
Brief: One thing: the live demo follows a fixed script of configurations, with the unusual cases still to be chosen marked as pending; a table of runs, because the demo must be reproducible under pressure (reference: a test-plan table).
Title: Live demo: three axes, then the cases that break things
Block: table
Run | Settings | What to show
! Intermediate axis, RK4 | I = (1, 2, 3), Ω = 1, ε = 10⁻³, Δt = 0.02 | flips every 27.5 s, λ = 0.577
Minimum and maximum axes | same, axis I₁ then I₃ | closed polhodes, no flip
Euler on axis 2 | Conservation page | 2T grows 7 % in 80 s
PENDING: unusual cases | I₁ ≈ I₂; I₁ + I₂ < I₃; Δt beyond 2.83 s; adaptive step | to choose and rehearse
Notes:
[Ignacio · 15:15–17:15] Live demo, about two minutes. First, the default case, intermediate axis with RK4: you will see the box flip every 27.5 seconds and the saddle eigenvalue 0.577 in the theory panel. Then the minimum and the maximum axes, where the polhode closes around the spin axis and nothing flips. Then Euler on the intermediate axis, on the conservation page, where energy grows seven percent. PENDING, to be decided by the team before the defence: the unusual cases. Candidates are nearly equal inertias, non-physical inertias where I one plus I two is less than I three, which the GUI flags, a step beyond the RK4 limit, and the adaptive step.

## Slide 23
layout: composed
Brief: One thing: the code changed shape twice, and the turning point was splitting the GUI into pages; a dated timeline with the turn marked, because the evolution is the evidence that we iterated (reference: a release history in a changelog).
Title: Fifty-one commits, three authors, and two rewrites of the interface
Block: timeline
24 Sep | Repository, README and folder plan
6 Oct | Three-layer reorganisation, milestone 2 engine
24 Oct | Gauss pivoting fixed, milestones 3 and 4, stability regions
! 27 Oct | GUI split into four page modules (+1189 lines)
2 Nov | Flow rewritten for readability (−1443 lines)
Notes:
[Ignacio · 17:15–17:50] Our history has fifty-one commits from three authors. The repository started on the twenty-fourth of September with a plan of folders and READMEs. On the sixth of October we reorganised it into the three layers. On the twenty-fourth we fixed the pivoting in Gauss and finished the error and stability milestones. The turning point was the twenty-seventh, when the interface was split from one large file into four page modules. The last rewrite, on the second of November, removed fourteen hundred lines so that each of us can read the flow from the button to the plot.

## Slide 24
layout: composed
Brief: One thing: the AI worked inside constraints we wrote first; a two-column split of what we did against what we propose, because the honest boundary between the two is the point (reference: a lessons-learned register).
Title: The AI worked inside rules we wrote before the code
Block: comparison
! In place | README per layer written as a contract before the engine and GUI code (6–8 Oct). Fixed interfaces F(U, t) and method(U, Δt, t, F). A regression script that compared every scheme bit for bit before and after the GUI refactor (28 Oct). Screenshots of every page saved for review by a person.
Proposed | Tests that run on every commit instead of one-off scripts. An instructions file for the assistant inside the repository. Automatic architecture map generated from the imports.
Notes:
[Ignacio · 17:50–18:35] We used an AI assistant to write much of the code, and the way we kept control of it is what we call the harness. Before writing the engine and the interface, we wrote a README for each layer saying what it must and must not do, and the interfaces were fixed by the course: F of U and t, and the scheme signature. When the assistant refactored the GUI, a script compared every scheme, with fixed and adaptive step, bit for bit against the previous version. And the same script saved a screenshot of every page for one of us to check. What we did not have, and propose, is tests running on every commit, an instructions file for the assistant inside the repository, and an architecture map generated automatically.

## Slide 25
layout: composed
Brief: One thing: we found and corrected real AI mistakes, and some are still visible; a three-card set of documented episodes with a pending card for the team's own, because concrete failures earn more trust than claims (reference: a post-incident review).
Title: Where the AI got it wrong, and how we noticed
Block: card-grid
! A patch that hid a bug | temporal_schemes.Crank_Nicolson calls Newton with three arguments; Newton takes two. Instead of fixing it, PEI1.py checks Newton's signature and swaps in its own step.
A silent wrong answer | The fixed-point implicit step returned the Euler predictor for small Δt. Caught by comparing outputs: Crank-Nicolson equal to Euler, digit for digit.
Stale scaffolding | Both GUI test scripts in tmp/ still call functions the last rewrite removed; a physics docstring claims no imports from the engine.
PENDING: our episodes | Team to add two or three real prompt exchanges and the correction each needed.
Notes:
[Ignacio · 18:35–19:20] The AI made mistakes, and showing them is more honest than saying it did not. One: the Crank-Nicolson in the engine calls Newton with three arguments while Newton accepts two. The fix that reached our main program does not repair that call. It inspects Newton's signature and substitutes a separate step. It works, but it hides the bug. Two: the first implicit step returned the Euler predictor for small steps, and we found it only by noticing that two different schemes gave identical numbers. Three: the test scripts were written for an earlier version of the GUI and no longer run. PENDING: the team will add our own prompt exchanges here.

## Slide 26
layout: statement
Brief: One thing: the line the board takes out of the room, bookending the wing nut; an ink close with one sentence and the turn to the individual questions (reference: the preliminary deck's dark conclusion slide, kept).
Statement: The wing nut flips because its intermediate axis is a saddle. We can show it on the screen, measure where each scheme stops telling the truth, and point to the line of code that does it.
Notes:
[Ignacio · 19:20–20:00] To close where Rubén started: the wing nut flips because its intermediate axis is a saddle point in the space of angular velocities. Our program shows it, measures how far each scheme can be trusted, and every number in this talk comes from a line of code in our repository that each of us can explain. Thank you. We are ready for your questions.

## Slide 27
layout: section
Brief: One thing: what follows is backup for questions, not presented; ink divider (reference: appendix divider in a technical report).
Title: Backup for questions
Notes:
Not presented. Slides for the individual questions.

## Slide 28
layout: composed
Brief: One thing: the finite-difference Jacobian already exists and is exact for our F; a short derivation with the measured error against h, because the examiner will ask why central differences and which h (reference: a numerical-analysis worked example).
Title: The finite-difference Jacobian is exact for our F, up to rounding
Block: table
Step h | max relative error vs analytic J (7 × 7, 200 random states)
0.1 | 6·10⁻¹⁵
! 10⁻³ (current) | 8·10⁻¹³
10⁻⁶ | 6·10⁻¹⁰
Notes:
Backup. NewtonRaphson.Jacobian uses central differences with a fixed h of ten to the minus three, the same routine as the course repository. The error of a central difference is h squared over six times the third derivative plus about machine epsilon times F over h. Our F, Euler equations plus quaternion kinematics, is bilinear, so the third derivative is zero and only rounding is left. That is why a larger h is more accurate here. For a general F the optimum h is about the cube root of machine epsilon, scaled by the size of U. Pending: a test comparing both Jacobians in the repository, and using the numerical one as a fallback when F has no jacobian attribute.

## Slide 29
layout: composed
Brief: One thing: the adaptive step is Richardson applied to one step; a numbered process, because the examiner may ask how dt is chosen (reference: an algorithm box in a numerical-methods textbook).
Title: Adaptive step: Richardson on a single step
Block: process
Two estimates | U₁ = one step of Δt; U₂ = two steps of Δt/2
Error | e = |U₂ − U₁| / (2^q − 1)
Accept | if e ≤ tol (1 + |U₂|), keep U₂
Next step | Δt ← Δt · 0.9 (tol/e)^{1/(q+1)}, limited to [0.2, 2] Δt
Notes:
Backup. Cauchy_problem_adaptive. Each attempt costs three steps of the scheme. The accepted value is the more accurate U2. The order q comes from the Esquema_temporal wrapper in PEI1.py, which attaches order 1, 2 and 4. Limit: fifty thousand steps for explicit schemes, thirty thousand for Crank-Nicolson, after which Integration_stopped returns the partial solution.

## Slide 30
layout: composed
Brief: One thing: the known defects from our own audit, honestly listed and prioritised; a table, because the board may ask what is wrong with the code (reference: a defect register).
Title: Known defects from our own audit
Block: table
Defect | Where | Priority
! Crank_Nicolson calls Newton with 3 arguments | temporal_schemes.py | high
Newton raises RuntimeError, not caught by Cauchy_problem | NewtonRaphson.py | high
Gauss calls exit() on a singular matrix | NewtonRaphson.py | high
Leap_Frog keeps global state without start() | temporal_schemes.py | medium
Physics imports partition from the engine; root README out of date | eje_intermedio.py, README.md | low
Notes:
Backup. All found while preparing this presentation, none affects the GUI path, because the GUI uses its own Crank-Nicolson step and only Euler, Crank-Nicolson and RK4. Full plan in presentacion/backlog.md.

## Slide 31
layout: composed
Brief: One thing: the project knowledge map is pending, and how it will be generated; a placeholder that names the source and the method, because the preliminary deck promised it (reference: the professor's Mind Map in jahrWork/MUSE_orbits_S1/docs).
Title: PENDING: project knowledge map
Visual: Knowledge map of the project (pending; the preliminary deck left a NotebookLM placeholder here).
Block: freeform
text body ink at cols 1-12 rows 1-3 | To be generated from the repository: module imports, public functions and README sections, rendered as a graph. Proposal and steps in presentacion/backlog.md, task D.
Notes:
Backup, pending. Do not present until the map exists.
