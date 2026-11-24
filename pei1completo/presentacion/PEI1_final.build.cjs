/*
 * PEI1_final.build.cjs - final PEI 1 deck, composed as code under .slides/tokens.cjs.
 *
 * Deck decisions (from the spec's structure and motif):
 *   Ground   ink for the cover panel, the three speaker dividers, the backup divider and the close;
 *            white paper for every evidence slide, framed by the MUSE header (eyebrow left,
 *            UPM / ETSIAE / IDR logos right, hairline) and footer.
 *   Motif    a three-pill tracker in the footer (Physics, Engine, Software), the current part filled
 *            in accent; every content slide carries a one-line source caption pointing at the repo.
 *   Accent   spent on one element per slide: the leading card, panel, table row or turning point.
 *   Shape    rounded corners everywhere (brand shape token).
 *   Links    slide 18 is a clickable phase map; the eyebrow of slides 19-25 links back to it.
 *
 * Content lives in the C block below, injected from PEI1_final.deck.md by inyectar_contenido.py.
 * Run: node --permission ... PEI1_final.build.cjs --tokens .slides/tokens.cjs --out PEI1_final.pptx
 */

const argv = process.argv.slice(2);
function arg(name) {
  const i = argv.indexOf(name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : null;
}
const tokensPath = arg("--tokens");
const outPath = arg("--out");
if (!tokensPath || !outPath) {
  console.error("usage: node PEI1_final.build.cjs --tokens <tokens.cjs> --out <deck.pptx>");
  process.exit(2);
}

const T = require(require("path").resolve(tokensPath));
const path = require("path");
const pptxgen = T.loadPptxgen();

const C = JSON.parse('{"s1": {"layout": "title", "brief": "The one thing is the question the deck answers; a dark ground with the MUSE logo and a phase-space polhode drawn as a mark, so the opening already shows the object we study (reference: the preliminary deck\'s dark cover, kept).", "title": "The Intermediate Axis Theorem", "subtitle": "Rigid-body dynamics, spectral analysis and a reactive Python tool", "notes": "[Rubén · 0:00–0:20] Good morning. We are Rubén Núñez, Mario Penin and Ignacio Pérez. In the next twenty minutes we will show you why a spinning body flips when it turns about its intermediate axis, how our numerical engine reproduces that flip, and how we built and corrected the software around it. I will start with the physics, Mario will take the numerical engine, and Ignacio will close with the software and the way we worked."}, "s2": {"layout": "composed", "brief": "One thing: the flip is real and it needs no torque; a resolved comparison, Dzhanibekov (the effect we model) against Explorer 1 (a look-alike our model cannot explain), because the contrast defines the scope of a torque-free rigid model before any equation (reference: a two-panel case comparison in an engineering failure report).", "title": "A wing nut flips in orbit with no torque acting on it", "visual": "A still frame of the Dzhanibekov wing nut in orbit, and a photograph of Explorer 1 (both real images, to be placed by the team).", "blockType": "comparison", "block": ["! Dzhanibekov, Salyut 7, 1985 | A wing nut spinning about its intermediate axis reverses every few seconds. Rigid, torque-free: our model.", "Explorer 1, 1958 | Spin about the minimum axis decays to the maximum axis. Cause: internal energy dissipation, outside a rigid model."], "notes": "[Rubén · 0:20–1:10] In 1985 the cosmonaut Vladimir Dzhanibekov unscrewed a wing nut on Salyut 7 and watched it fly off spinning. Every few seconds it turned over by half a turn and kept spinning the other way. No torque acts on it. That is the effect we model. The preliminary version of this talk opened with Explorer 1, and we want to be precise about why it is different. Explorer 1 started spinning about its axis of minimum inertia and ended up tumbling about the maximum axis, because its flexible antennas dissipated energy. A rigid, torque-free model conserves energy, so it cannot reproduce Explorer 1. It can reproduce the wing nut, and that is the scope of everything that follows."}, "s3": {"layout": "section", "brief": "One thing: the first part starts; ink divider naming the part and the speaker, the footer tracker shows Physics filled (reference: chapter openers in a printed lecture-notes series).", "title": "1 · Physics · Rubén Núñez", "notes": "[Rubén · 1:10–1:15] First part: the physics and the analytical results the rest of the project is built on."}, "s4": {"layout": "composed", "brief": "One thing: three first-order equations hold the whole problem; the equations set large on the left with the GUI\'s box beside them, because the audience must tie each I_k to a real axis of a real body before any analysis (reference: a textbook figure pairing an equation block with its labelled body).", "title": "Three coupled equations describe a torque-free rigid body", "visual": "Crop of the GUI\'s rotating box (homogeneous box with the inertias I = (1, 2, 3)) from figuras/recursos/caja_eje2.png.", "blockType": "freeform", "block": ["text h1 ink at cols 1-7 rows 1-2 | Body frame, principal axes, I₁ < I₂ < I₃", "text body ink at cols 1-7 rows 3-6 | I₁ dω₁/dt = (I₂ − I₃) ω₂ ω₃ / I₂ dω₂/dt = (I₃ − I₁) ω₃ ω₁ / I₃ dω₃/dt = (I₁ − I₂) ω₁ ω₂", "text body muted at cols 1-7 rows 7-9 | State U = ω = (ω₁, ω₂, ω₃). Attitude added through a quaternion: dq/dt = ½ q ⊗ (0, ω)."], "notes": "[Rubén · 1:15–2:05] We work in the body frame, along the principal axes, ordered so that I one is smaller than I two, which is smaller than I three. Without external torques, Euler\'s equations reduce to these three lines. Each component of the angular velocity is driven by the product of the other two, with a coefficient that is a difference of inertias. That coupling is the whole story. The state is the angular velocity vector, and to animate the body we also integrate its attitude with a quaternion, so the full state in the program has seven components. The box on the right is the one the GUI draws: its sides are computed from the inertias, so I one is the long axis and I three the short one."}, "s5": {"layout": "composed", "brief": "One thing: two conserved quantities confine the motion to the intersection of two ellipsoids; the derivation in one line on the left and the real Poinsot plot on the right, because the geometry is the argument (reference: Landau and Lifshitz, Mechanics, section 37 figure).", "title": "Two invariants confine ω to the intersection of two ellipsoids", "visual": "GUI phase-space view for the intermediate axis (figuras/recursos/poinsot_eje2.png).", "blockType": "freeform", "block": ["text body ink at cols 1-6 rows 1-3 | 2T = I₁ω₁² + I₂ω₂² + I₃ω₃² / L² = I₁²ω₁² + I₂²ω₂² + I₃²ω₃²", "text body ink at cols 1-6 rows 4-6 | Multiply equation k by ω_k (or I_k ω_k) and add: the right-hand sides cancel because (I₂ − I₃) + (I₃ − I₁) + (I₁ − I₂) = 0.", "text body muted at cols 1-6 rows 7-9 | Motion exists only if 2T·I₁ ≤ L² ≤ 2T·I₃. The polhode is the curve where both surfaces meet."], "notes": "[Rubén · 2:05–3:00] Two quantities are conserved. Twice the kinetic energy and the square of the angular momentum. The proof is one line: multiply each equation by omega k, or by I k times omega k, and add them up. The right-hand side becomes omega one, omega two, omega three times a sum of inertia differences that is identically zero. Each invariant is an ellipsoid in omega space, so the angular velocity can only move along the curve where both ellipsoids intersect. That curve is the polhode. On the right is our GUI: the purple ellipsoid is the energy, the orange one the momentum, and the dashed red curves are the separatrix we will come back to in two slides."}, "s6": {"layout": "composed", "brief": "One thing: linearising at the three pure spins gives centre, saddle, centre; a table, because the audience reads exact eigenvalues and needs the three rows side by side with the intermediate row leading (reference: the stability table in the PEI 1 statement, equations 9, 10 and 12).", "title": "Linearised at each pure spin, only the intermediate axis is a saddle", "blockType": "table", "block": ["Spin axis | Equilibrium | Eigenvalues of J | I = (1, 2, 3), Ω = 1 | Type", "Minimum I₁ | (Ω, 0, 0) | ± iΩ √[(I₃−I₁)(I₂−I₁)/(I₂I₃)] | ± 0.577 i | centre", "! Intermediate I₂ | (0, Ω, 0) | ± Ω √[(I₃−I₂)(I₂−I₁)/(I₁I₃)] | ± 0.577 | saddle", "Maximum I₃ | (0, 0, Ω) | ± iΩ √[(I₃−I₂)(I₃−I₁)/(I₁I₂)] | ± 1.000 i | centre"], "notes": "[Rubén · 3:00–3:55] To study stability we linearise around each pure spin. The Jacobian of the Euler equations has a zero eigenvalue along the spin axis and a pair in the other two directions. For the minimum and maximum axes the product under the square root is negative, so the pair is purely imaginary: a centre, small oscillations. For the intermediate axis the two inertia differences have opposite signs, the product is positive, and we get one real positive eigenvalue: a saddle. With the inertias one, two, three and unit spin, the intermediate axis grows like e to the 0.577 t. These are exactly the numbers the GUI prints in its theory panel, computed by Linear_eigenvalues in the physics layer."}, "s7": {"layout": "composed", "brief": "One thing: a linear centre does not prove stability, a conserved Lyapunov function does; a three-card set with the intermediate card leading, because the same function V gives three different signs (reference: the energy-Casimir method as laid out in Marsden and Ratiu).", "title": "A linear centre proves nothing; a conserved Lyapunov function does", "blockType": "card-grid", "block": ["Minimum axis | V = L² − I₁·2T = I₂(I₂−I₁)ω₂² + I₃(I₃−I₁)ω₃² / positive definite: stable", "! Intermediate axis | V = L² − I₂·2T = I₁(I₁−I₂)ω₁² + I₃(I₃−I₂)ω₃² / indefinite: V = 0 are the separatrix planes", "Maximum axis | V = L² − I₃·2T = I₁(I₁−I₃)ω₁² + I₂(I₂−I₃)ω₂² / negative definite: stable"], "notes": "[Rubén · 3:55–4:45] Imaginary eigenvalues are not enough. A linear centre can be destroyed by the nonlinear terms, so linearisation alone cannot prove that the minimum and maximum axes are stable. What does prove it is a combination of the two invariants: V equals L squared minus I k times two T. It is conserved because both terms are. Around the minimum axis it is positive definite in the other two components, around the maximum axis negative definite, so it is a Lyapunov function and the perturbation stays bounded. Around the intermediate axis it changes sign, and its zero set is a pair of planes. That function is Energy_Casimir in our code."}, "s8": {"layout": "composed", "brief": "One thing: the flip is a trajectory hugging the separatrix, and its timing is predictable; the real ω(t) trace with three measured numbers beside it, because the audience should see theory and simulation agree to the digit (reference: an annotated oscilloscope trace).", "title": "The flip follows the separatrix, and its timing is predictable", "visual": "GUI ω(t) trace for the intermediate axis (figuras/recursos/omega_eje2.png).", "blockType": "freeform", "block": ["text body ink at cols 1-4 rows 1-3 | Separatrix: two planes ω₃ = ± c ω₁, c = √[I₁(I₂−I₁) / I₃(I₃−I₂)]", "text body ink at cols 1-4 rows 4-6 | Period P = 4K(k)/ν, infinite on the separatrix. Exact 55.062 s, measured 55.062 s.", "text body ink at cols 1-4 rows 7-9 | First flip ≈ (1/λ) ln(1/ε): 14.9 s, 34.9 s and 50.8 s for ε = 10⁻³, 10⁻⁸, 10⁻¹²; slope 1.732 s = 1/λ."], "notes": "[Rubén · 4:45–6:00] Here is what a flip looks like. Omega two, in green, sits at plus one, then swings to minus one in a few seconds while omega one and omega three make a short excursion, and then it waits. Near the intermediate axis the trajectory runs along the separatrix, which is the pair of planes from the previous slide. Two numbers confirm the analysis. The period from the elliptic integral, four K of k over nu, is 55.062 seconds, and the period measured between flips in the simulation is also 55.062. And the waiting time grows with the logarithm of the initial perturbation: we measured the first flip at 14.9, 34.9 and 50.8 seconds for epsilon ten to the minus three, minus eight and minus twelve, and the slope is 1.732 seconds, which is one over lambda. The instability sets the clock. Mario will now show you how we integrate this."}, "s9": {"layout": "section", "brief": "One thing: the second part starts; ink divider, tracker on Engine (reference: chapter openers in a printed lecture-notes series).", "title": "2 · Numerical engine · Mario Penin", "notes": "[Mario · 6:00–6:05] Second part: how the model becomes numbers, and how far we can trust them."}, "s10": {"layout": "composed", "brief": "One thing: the engine never knows which physics it integrates; a left-to-right process of the call chain with file names under each box, because the decoupling is a sequence of handoffs (reference: a call graph in a numerical-methods textbook).", "title": "One engine integrates any F(U, t) and never sees the physics", "blockType": "process", "block": ["F(U, t) | space_physics: Euler + quaternion, exact Jacobian attached as F.jacobian", "Scheme | Euler, Crank-Nicolson, RK4: U_{n+1} = method(U_n, Δt, t_n, F)", "Cauchy_problem | Fixed mesh, or adaptive by step doubling (Richardson on one step)", "Integration_stopped | Newton failure or non-finite state: returns the partial solution"], "notes": "[Mario · 6:05–6:55] The engine is built around the interface of the course milestones. The physics layer hands over a function F of U and t. A scheme takes one step with the signature method of U, delta t, t, F. Cauchy_problem repeats that step over a mesh, which does not have to be uniform. The adaptive version takes one step of size delta t and two of size delta t over two, estimates the local error from their difference divided by two to the q minus one, and grows or shrinks the step. When something goes wrong, Newton fails or the state stops being finite, the engine raises Integration_stopped carrying everything computed so far, so the GUI can still draw the valid part instead of crashing."}, "s11": {"layout": "composed", "brief": "One thing: an implicit scheme is a nonlinear solve per step, and the solver choice decides whether it works; a comparison that resolves for Newton, because the first version silently failed (reference: a before and after panel in an engineering change note).", "title": "An implicit step is a Newton solve, not a fixed-point loop", "blockType": "comparison", "block": ["First version: fixed point | Y ← U + Δt/2 [F(U) + F(Y)], tolerance 1e-6, no iteration cap. Converges only if Δt·ρ(J)/2 < 1; for small Δt it returned the Euler predictor (CN identical to Euler at N = 16 000).", "! Current: Newton, exact Jacobian | Solve G(X) = X − U − Δt/2 [F(U) + F(X)] = 0 with G′ = I − Δt/2 J(X). Euler predictor, tolerance 1e-10, 25 iterations, failure raised as an exception."], "notes": "[Mario · 6:55–7:45] Crank-Nicolson is implicit, so each step means solving a nonlinear equation for the new state. Our first version used a fixed-point iteration. We documented two failures in the engine README. For large steps it only converges when delta t times the spectral radius over two is below one. For small steps the Euler predictor already satisfied the absolute tolerance, so the loop never iterated, and Crank-Nicolson gave exactly the same numbers as explicit Euler. The current version solves G of X equal to zero with Newton, using the exact Jacobian the physics layer provides: the identity minus delta t over two times J. It stops at ten to the minus ten or after twenty-five iterations, and a failure becomes an exception."}, "s12": {"layout": "composed", "brief": "One thing: we measure each scheme\'s order on the rigid body itself, without an exact solution; the real convergence plot with the three slopes direct-labelled, because the slope is the claim (reference: a log-log convergence figure in Hairer, Nørsett and Wanner).", "title": "Richardson measures the order on the rigid body itself", "visual": "GUI convergence plot and Richardson-versus-reference error (figuras/recursos/convergencia.png, richardson.png).", "blockType": "freeform", "block": ["text body ink at cols 1-4 rows 1-3 | D = |U_N(t_f) − U_2N(t_f)| ≈ E_N (1 − 2^−q): no exact solution needed.", "text body ink at cols 1-4 rows 4-6 | Measured order, intermediate axis, t_f = 20: Euler 1.02, Crank-Nicolson 2.00, RK4 4.02.", "text body muted at cols 1-4 rows 7-9 | The fitted range is chosen automatically: the longest run where the local order log₂(D_k / D_k+1) stays within 15 %."], "notes": "[Mario · 7:45–8:40] There is no closed-form solution to compare against, so we use Richardson extrapolation. We integrate with N and with 2N steps. For a scheme of order q, their difference D equals the error times one minus two to the minus q, so the logarithm of D against the logarithm of N is a straight line of slope minus q. On the rigid body, around the intermediate axis, we measure 1.02 for Euler, 2.00 for Crank-Nicolson and 4.02 for RK4. The fitting window is not hand-picked: the code keeps the longest run of meshes where the local order changes by less than fifteen percent. On the right, the error Richardson predicts for RK4 lies on top of the error against a reference eight times finer."}, "s13": {"layout": "composed", "brief": "One thing: these regions come from running our schemes, not from the textbook formula; the four measured regions with the formula dashed on top, because coincidence of the two is the evidence (reference: the Stability_Region routine in jahrWork/MUSE_orbits_S1, applied to our own code).", "title": "We measured the stability regions by running our own schemes", "visual": "figuras/regiones_numericas.png (generated by figuras/regiones_numericas.py).", "blockType": "freeform", "block": ["text body ink at cols 1-12 rows 1-2 | One step of size 1 on dU/dt = λU from U₀ = 1, for every z = λ on a 133 × 145 grid. |U₁| is the amplification. Our Newton is real-valued, so λ = a + ib runs as the real system A = [a −b; b a].", "text caption muted at cols 1-12 rows 11-12 | Largest gap between measured |U₁| and the formula |R(z)|: Euler 3·10⁻¹⁶, implicit Euler 2·10⁻¹² (finite-difference Jacobian), Crank-Nicolson 2·10⁻¹⁴, RK4 1·10⁻¹⁴. One failed step: implicit Euler at z = 1, where the system is singular."], "notes": "[Mario · 8:40–9:35] The statement asks for the regions where the absolute value of R of z is at most one. We did not want to plot four formulas from a book, so we measured them. Following the professor\'s Stability_Region routine, we take one step of size one on the test equation and read the amplification. Our Newton works with real numbers, so a complex lambda is written as the equivalent two by two real system, which gives exactly the same modulus. The shaded areas are measured, the dashed lines are the formulas, and they agree to ten to the minus twelve or better. The implicit Euler panel goes through our finite-difference Jacobian, and its one failed point is z equal to one, where the linear system is singular."}, "s14": {"layout": "composed", "brief": "One thing: the rigid body\'s modes sit almost on the imaginary axis, where the three schemes behave in three different ways; the |R(iy)| curve with the RK4 limit marked, because that axis is where the physics lives (reference: the imaginary-axis panel already in our GUI\'s stability page).", "title": "Rotation modes live on the imaginary axis, where the schemes part ways", "visual": "figuras/eje_imaginario.png.", "blockType": "freeform", "block": ["text body ink at cols 1-4 rows 1-3 | z = λΔt with Δt = 0.02: ± 0.0115 (axis 2, real), ± 0.0115 i and ± 0.02 i (axes 1, 3), ± 0.01 i (quaternion).", "text body ink at cols 1-4 rows 4-6 | Euler |R(iy)| = √(1 + y²) > 1: every rotation mode grows. Crank-Nicolson: exactly 1. RK4: below 1 up to y = 2√2.", "text body muted at cols 1-4 rows 7-9 | RK4 stays stable on axis 3 for Δt < 2√2/σ = 2.83 s; Euler is never stable there."], "notes": "[Mario · 9:35–10:30] Now we place the rigid body inside those regions. Each eigenvalue of the Jacobian times the step gives a point z. Around the minimum and maximum axes, and for the quaternion kinematics, those points are purely imaginary. Around the intermediate axis they are real, and that real growth is physical, every scheme must reproduce it. On the imaginary axis the three schemes differ completely. Euler multiplies each rotation mode by the square root of one plus y squared at every step, so it always gains energy. Crank-Nicolson has modulus exactly one. RK4 damps very slightly and stays stable up to y equal to two root two, which for the maximum axis means a step of 2.83 seconds."}, "s15": {"layout": "composed", "brief": "One thing: R(z) predicts the drift we observe, to the digit; a table of the three schemes with the Euler row leading, because the prediction and the measurement sit side by side (reference: the prediction-versus-simulation table on our GUI\'s stability page).", "title": "R(z) predicts the drift the simulation shows", "blockType": "table", "block": ["Scheme | max drift of 2T and L² | ‖q(t_f)‖ − 1 predicted by ∏ R(z_n) | ‖q(t_f)‖ − 1 simulated", "! Euler | 7.3·10⁻² | 2.405·10⁻¹ | 2.405·10⁻¹", "Crank-Nicolson | 3.3·10⁻⁵ | −1.3·10⁻¹⁴ | −1.5·10⁻¹⁰", "RK4 | 1.1·10⁻¹⁰ | −3.2·10⁻¹¹ | −3.9·10⁻¹¹"], "notes": "[Mario · 10:30–11:25] This is the test of the whole argument. Intermediate axis, delta t of 0.02, eighty seconds. For Euler, multiplying the amplification factor of the quaternion mode over every step predicts a norm error of 0.2405 at the end, and the simulation gives 0.2405. Energy and momentum drift by seven percent. RK4 is predicted and measured at a few times ten to the minus eleven. Crank-Nicolson is predicted at ten to the minus fourteen and measured at ten to the minus ten: the gap is our Newton tolerance. And during each flip its quaternion norm error rises to four times ten to the minus six and comes back, because the trapezoidal rule only preserves the norm when the matrix Omega of omega is the same at both ends of the step. During a flip omega changes fast, so it is not."}, "s16": {"layout": "composed", "brief": "One thing: the numerics have three hard limits we can name and measure; a three-card set with the saddle card leading, because each limit has a distinct cause (reference: the limitations table in our numerical_engine README).", "title": "Three limits we can name, and measure", "blockType": "card-grid", "block": ["! The saddle amplifies errors too | Any error along the unstable direction grows like e^{λt}, just as ε does. Euler\'s growth rate ln(1 + λΔt)/Δt is lower than λ: with ε = 10⁻¹² and Δt = 0.1 its first flip comes 1.4 s late.", "Singular implicit steps | Crank-Nicolson\'s R(z) has a pole at z = 2; implicit Euler at z = 1. There, I − Δt J cannot be inverted and the step fails.", "Floating point | Richardson differences stop falling near 10⁻¹² (RK4, N = 5120): below that, rounding dominates truncation."], "notes": "[Mario · 11:25–12:15] We close the engine with its limits. First, the intermediate axis is a saddle for errors as well as for perturbations. With a step of 0.02 all three schemes agree on the flip time to three tenths of a second, even with epsilon at ten to the minus twelve. But Euler grows at the rate log of one plus lambda delta t over delta t, which is below lambda, so with a step of 0.1 and that epsilon its flip arrives 1.4 seconds late, exactly what that rate predicts. Second, the implicit schemes have singular points: z equal to two for Crank-Nicolson and z equal to one for implicit Euler. Third, below about ten to the minus twelve the Richardson differences hit rounding error, so the convergence fit has to stop there. Ignacio will now show you the software that ties this together."}, "s17": {"layout": "section", "brief": "One thing: the third part starts; ink divider, tracker on Software (reference: chapter openers in a printed lecture-notes series).", "title": "3 · Software, GUI and AI · Ignacio Pérez", "notes": "[Ignacio · 12:15–12:20] Third part: how the application is built, what it shows, and how we built it with an AI assistant."}, "s18": {"layout": "composed", "brief": "One thing: the project went through ten phases and each one maps to a part of this talk; an interactive map of ten nodes anchored to real dates, each node a hyperlink to its slide and every software slide linking back, because the examiners can jump to any phase during questions (reference: a clickable table of contents in a technical report PDF).", "title": "Ten phases, one map: click any phase to jump to its evidence", "blockType": "process", "block": ["Physical problem | 24 Sep | 2", "Analytical model | 6 Oct | 4", "Numerical formulation | 28 Sep – 8 Oct | 10", "Software architecture | 6 Oct | 19", "Numerical implementation | 24 – 25 Oct | 13", "GUI development | 25 Oct – 2 Nov | 21", "Integration | 27 Oct | 20", "Testing and validation | 28 Oct | 15", "Debugging and iteration | 24 Oct – 2 Nov | 25", "Final application | 2 Nov | 22"], "notes": "[Ignacio · 12:20–13:00] This map is the backbone of my part, and it is interactive: each phase is a link to the slide that holds its evidence, and every slide in this section has a link back here. The phases are the ones any engineering project goes through, from defining the problem to the final application, but the dates come from our own history. We defined the problem and the model at the end of September, formulated the numerics through the milestones, reorganised everything into three layers on the sixth of October, and spent the last two weeks implementing, testing and rewriting the interface. If you want to see the evidence behind any phase during the questions, click it."}, "s19": {"layout": "composed", "brief": "One thing: three layers, one orchestrator, and dependencies that point one way; a drawn architecture with arrows, because the direction of the arrows is the design decision (reference: a C4-style container diagram).", "title": "Three layers, one orchestrator: the GUI imports neither physics nor engine", "blockType": "tree", "block": ["PEI1.py (orchestrator)", "space_physics: F(U, t), F.jacobian, invariants, Poinsot geometry", "numerical_engine: schemes, Cauchy_problem, Richardson, R(z)", "! gui_reactive: four pages, receives data and two callbacks"], "notes": "[Ignacio · 13:00–13:50] The statement asks for three decoupled layers. Physics only knows the problem: give it a state and it returns the derivative, the Jacobian and the invariants. The engine only knows how to integrate a function it is handed. The GUI is the one we were most careful with: it does not import the physics or the engine at all. It receives plain data and two callbacks, compute and prepare page, from the main program PEI1.py, which is the only file that knows all three. There is one leak we found while preparing this talk: the physics layer imports the partition helper from the engine. It is harmless, but it breaks the rule, and it is on our backlog."}, "s20": {"layout": "composed", "brief": "One thing: one click travels a fixed path through named functions; a numbered process of the real call chain, because an examiner can ask which function runs at each step (reference: a sequence diagram in a software design document).", "title": "One click on Calcular follows one path through named functions", "blockType": "process", "block": ["leer_parametros | GUI reads sliders and selectors: numbers and a method name, never a function", "al_calcular | callback into PEI1.py: picks the scheme, builds F and U₀", "integrar_trayectoria | Cauchy_problem with protection: partial result and a warning if it stops", "preparar_pagina | invariants, regions, Richardson computed only when a page needs them", "dibujar | each page draws data; the timer only moves the current instant"], "notes": "[Ignacio · 13:50–14:30] This is what happens when you press Calcular. The GUI reads the sliders and passes numbers and the name of the method, never a function. The callback in PEI1.py chooses the scheme, builds F and the initial condition, and integrates through a protected wrapper that returns whatever was computed if the integration stops. The expensive analyses, comparing three schemes or the Richardson study, are computed only when you open the page that needs them. Finally each page draws, and the animation timer only moves a marker through results that already exist. It never integrates again."}, "s21": {"layout": "composed", "brief": "One thing: each of the four pages answers one question of the statement; four real screenshots in a row, each captioned with its question, because the GUI is evidence, not decoration (reference: a product tour strip in a software release note).", "title": "Four pages, each answering one question of the statement", "visual": "The four real GUI pages (figuras/recursos/gui_p1.png to gui_p4.png).", "blockType": "card-grid", "block": ["Motion | What does the body do? Box, Poinsot surfaces, separatrix, ω(t)", "Conservation | How much do 2T, L² and |q| drift with each scheme?", "! Stability | Where do the modes z = λΔt fall relative to |R(z)| ≤ 1?", "Precision | What order does each scheme reach, measured by Richardson?"], "notes": "[Ignacio · 14:30–15:15] The interface has four pages and each one answers one requirement of the statement. Motion shows the body turning in the inertial frame, the Poinsot ellipsoids with the separatrix and the angular velocity in time. Conservation compares the drift of energy, momentum and quaternion norm for the three schemes on exactly the same problem. Stability, the one I would highlight, places the eigenvalues of the actual state on top of the stability regions while the animation runs, and prints the prediction you saw in Mario\'s table. Precision runs the Richardson study. All the screenshots in this talk are captured from the real program by a script in the repository."}, "s22": {"layout": "composed", "brief": "One thing: the live demo follows a fixed script of configurations, with the unusual cases still to be chosen marked as pending; a table of runs, because the demo must be reproducible under pressure (reference: a test-plan table).", "title": "Live demo: three axes, then the cases that break things", "blockType": "table", "block": ["Run | Settings | What to show", "! Intermediate axis, RK4 | I = (1, 2, 3), Ω = 1, ε = 10⁻³, Δt = 0.02 | flips every 27.5 s, λ = 0.577", "Minimum and maximum axes | same, axis I₁ then I₃ | closed polhodes, no flip", "Euler on axis 2 | Conservation page | 2T grows 7 % in 80 s", "PENDING: unusual cases | I₁ ≈ I₂; I₁ + I₂ < I₃; Δt beyond 2.83 s; adaptive step | to choose and rehearse"], "notes": "[Ignacio · 15:15–17:15] Live demo, about two minutes. First, the default case, intermediate axis with RK4: you will see the box flip every 27.5 seconds and the saddle eigenvalue 0.577 in the theory panel. Then the minimum and the maximum axes, where the polhode closes around the spin axis and nothing flips. Then Euler on the intermediate axis, on the conservation page, where energy grows seven percent. PENDING, to be decided by the team before the defence: the unusual cases. Candidates are nearly equal inertias, non-physical inertias where I one plus I two is less than I three, which the GUI flags, a step beyond the RK4 limit, and the adaptive step."}, "s23": {"layout": "composed", "brief": "One thing: the code changed shape twice, and the turning point was splitting the GUI into pages; a dated timeline with the turn marked, because the evolution is the evidence that we iterated (reference: a release history in a changelog).", "title": "Fifty-one commits, three authors, and two rewrites of the interface", "blockType": "timeline", "block": ["24 Sep | Repository, README and folder plan", "6 Oct | Three-layer reorganisation, milestone 2 engine", "24 Oct | Gauss pivoting fixed, milestones 3 and 4, stability regions", "! 27 Oct | GUI split into four page modules (+1189 lines)", "2 Nov | Flow rewritten for readability (−1443 lines)"], "notes": "[Ignacio · 17:15–17:50] Our history has fifty-one commits from three authors. The repository started on the twenty-fourth of September with a plan of folders and READMEs. On the sixth of October we reorganised it into the three layers. On the twenty-fourth we fixed the pivoting in Gauss and finished the error and stability milestones. The turning point was the twenty-seventh, when the interface was split from one large file into four page modules. The last rewrite, on the second of November, removed fourteen hundred lines so that each of us can read the flow from the button to the plot."}, "s24": {"layout": "composed", "brief": "One thing: the AI worked inside constraints we wrote first; a two-column split of what we did against what we propose, because the honest boundary between the two is the point (reference: a lessons-learned register).", "title": "The AI worked inside rules we wrote before the code", "blockType": "comparison", "block": ["! In place | README per layer written as a contract before the engine and GUI code (6–8 Oct). Fixed interfaces F(U, t) and method(U, Δt, t, F). A regression script that compared every scheme bit for bit before and after the GUI refactor (28 Oct). Screenshots of every page saved for review by a person.", "Proposed | Tests that run on every commit instead of one-off scripts. An instructions file for the assistant inside the repository. Automatic architecture map generated from the imports."], "notes": "[Ignacio · 17:50–18:35] We used an AI assistant to write much of the code, and the way we kept control of it is what we call the harness. Before writing the engine and the interface, we wrote a README for each layer saying what it must and must not do, and the interfaces were fixed by the course: F of U and t, and the scheme signature. When the assistant refactored the GUI, a script compared every scheme, with fixed and adaptive step, bit for bit against the previous version. And the same script saved a screenshot of every page for one of us to check. What we did not have, and propose, is tests running on every commit, an instructions file for the assistant inside the repository, and an architecture map generated automatically."}, "s25": {"layout": "composed", "brief": "One thing: we found and corrected real AI mistakes, and some are still visible; a three-card set of documented episodes with a pending card for the team\'s own, because concrete failures earn more trust than claims (reference: a post-incident review).", "title": "Where the AI got it wrong, and how we noticed", "blockType": "card-grid", "block": ["! A patch that hid a bug | temporal_schemes.Crank_Nicolson calls Newton with three arguments; Newton takes two. Instead of fixing it, PEI1.py checks Newton\'s signature and swaps in its own step.", "A silent wrong answer | The fixed-point implicit step returned the Euler predictor for small Δt. Caught by comparing outputs: Crank-Nicolson equal to Euler, digit for digit.", "Stale scaffolding | Both GUI test scripts in tmp/ still call functions the last rewrite removed; a physics docstring claims no imports from the engine.", "PENDING: our episodes | Team to add two or three real prompt exchanges and the correction each needed."], "notes": "[Ignacio · 18:35–19:20] The AI made mistakes, and showing them is more honest than saying it did not. One: the Crank-Nicolson in the engine calls Newton with three arguments while Newton accepts two. The fix that reached our main program does not repair that call. It inspects Newton\'s signature and substitutes a separate step. It works, but it hides the bug. Two: the first implicit step returned the Euler predictor for small steps, and we found it only by noticing that two different schemes gave identical numbers. Three: the test scripts were written for an earlier version of the GUI and no longer run. PENDING: the team will add our own prompt exchanges here."}, "s26": {"layout": "statement", "brief": "One thing: the line the board takes out of the room, bookending the wing nut; an ink close with one sentence and the turn to the individual questions (reference: the preliminary deck\'s dark conclusion slide, kept).", "statement": "The wing nut flips because its intermediate axis is a saddle. We can show it on the screen, measure where each scheme stops telling the truth, and point to the line of code that does it.", "notes": "[Ignacio · 19:20–20:00] To close where Rubén started: the wing nut flips because its intermediate axis is a saddle point in the space of angular velocities. Our program shows it, measures how far each scheme can be trusted, and every number in this talk comes from a line of code in our repository that each of us can explain. Thank you. We are ready for your questions."}, "s27": {"layout": "section", "brief": "One thing: what follows is backup for questions, not presented; ink divider (reference: appendix divider in a technical report).", "title": "Backup for questions", "notes": "Not presented. Slides for the individual questions."}, "s28": {"layout": "composed", "brief": "One thing: the finite-difference Jacobian already exists and is exact for our F; a short derivation with the measured error against h, because the examiner will ask why central differences and which h (reference: a numerical-analysis worked example).", "title": "The finite-difference Jacobian is exact for our F, up to rounding", "blockType": "table", "block": ["Step h | max relative error vs analytic J (7 × 7, 200 random states)", "0.1 | 6·10⁻¹⁵", "! 10⁻³ (current) | 8·10⁻¹³", "10⁻⁶ | 6·10⁻¹⁰"], "notes": "Backup. NewtonRaphson.Jacobian uses central differences with a fixed h of ten to the minus three, the same routine as the course repository. The error of a central difference is h squared over six times the third derivative plus about machine epsilon times F over h. Our F, Euler equations plus quaternion kinematics, is bilinear, so the third derivative is zero and only rounding is left. That is why a larger h is more accurate here. For a general F the optimum h is about the cube root of machine epsilon, scaled by the size of U. Pending: a test comparing both Jacobians in the repository, and using the numerical one as a fallback when F has no jacobian attribute."}, "s29": {"layout": "composed", "brief": "One thing: the adaptive step is Richardson applied to one step; a numbered process, because the examiner may ask how dt is chosen (reference: an algorithm box in a numerical-methods textbook).", "title": "Adaptive step: Richardson on a single step", "blockType": "process", "block": ["Two estimates | U₁ = one step of Δt; U₂ = two steps of Δt/2", "Error | e = |U₂ − U₁| / (2^q − 1)", "Accept | if e ≤ tol (1 + |U₂|), keep U₂", "Next step | Δt ← Δt · 0.9 (tol/e)^{1/(q+1)}, limited to [0.2, 2] Δt"], "notes": "Backup. Cauchy_problem_adaptive. Each attempt costs three steps of the scheme. The accepted value is the more accurate U2. The order q comes from the Esquema_temporal wrapper in PEI1.py, which attaches order 1, 2 and 4. Limit: fifty thousand steps for explicit schemes, thirty thousand for Crank-Nicolson, after which Integration_stopped returns the partial solution."}, "s30": {"layout": "composed", "brief": "One thing: the known defects from our own audit, honestly listed and prioritised; a table, because the board may ask what is wrong with the code (reference: a defect register).", "title": "Known defects from our own audit", "blockType": "table", "block": ["Defect | Where | Priority", "! Crank_Nicolson calls Newton with 3 arguments | temporal_schemes.py | high", "Newton raises RuntimeError, not caught by Cauchy_problem | NewtonRaphson.py | high", "Gauss calls exit() on a singular matrix | NewtonRaphson.py | high", "Leap_Frog keeps global state without start() | temporal_schemes.py | medium", "Physics imports partition from the engine; root README out of date | eje_intermedio.py, README.md | low"], "notes": "Backup. All found while preparing this presentation, none affects the GUI path, because the GUI uses its own Crank-Nicolson step and only Euler, Crank-Nicolson and RK4. Full plan in presentacion/backlog.md."}, "s31": {"layout": "composed", "brief": "One thing: the project knowledge map is pending, and how it will be generated; a placeholder that names the source and the method, because the preliminary deck promised it (reference: the professor\'s Mind Map in jahrWork/MUSE_orbits_S1/docs).", "title": "PENDING: project knowledge map", "visual": "Knowledge map of the project (pending; the preliminary deck left a NotebookLM placeholder here).", "blockType": "freeform", "block": ["text body ink at cols 1-12 rows 1-3 | To be generated from the repository: module imports, public functions and README sections, rendered as a graph. Proposal and steps in presentacion/backlog.md, task D."], "notes": "Backup, pending. Do not present until the map exists."}, "x": {"footer": "MUSE · UPM · Ampliación de Matemáticas 1 · PEI 1", "parts": ["Physics", "Engine", "Software"], "mapBack": "   ↩ phase map", "pending": "PENDING", "map": {"goTo": "Go to slide", "back": "Back to the phase map", "slideWord": "slide"}, "cover": {"master": "Máster Universitario en Sistemas Espaciales", "eyebrow": "AMPLIACIÓN DE MATEMÁTICAS 1 · PEI 1", "course": "Ampliación de Matemáticas 1 · Course 2026–2027", "authors": "Rubén Núñez Cuenca, Mario Penin Fernández and Ignacio Pérez González"}, "sections": {"s3": {"num": "1", "lines": "Model · invariants · linearisation · Lyapunov · the flip"}, "s9": {"num": "2", "lines": "Cauchy problem · Newton · Richardson · measured stability regions"}, "s17": {"num": "3", "lines": "Phase map · architecture · GUI · demo · how we worked with AI"}, "s27": {"num": "+", "lines": "Finite-difference Jacobian · adaptive step · defects · knowledge map"}}, "close": "Individual defence · questions", "eyebrows": {"s2": "PHYSICS · WHY THIS PROBLEM", "s4": "PHYSICS · MODEL", "s5": "PHYSICS · INVARIANTS", "s6": "PHYSICS · LINEAR STABILITY", "s7": "PHYSICS · NONLINEAR STABILITY", "s8": "PHYSICS · THE FLIP", "s10": "ENGINE · ARCHITECTURE", "s11": "ENGINE · IMPLICIT SCHEMES", "s12": "ENGINE · CONVERGENCE", "s13": "ENGINE · STABILITY REGIONS", "s14": "ENGINE · THE RIGID BODY IN THE REGIONS", "s15": "ENGINE · VALIDATION", "s16": "ENGINE · LIMITS", "s18": "SOFTWARE · DEVELOPMENT MAP", "s19": "SOFTWARE · ARCHITECTURE", "s20": "SOFTWARE · DATA FLOW", "s21": "SOFTWARE · GUI", "s22": "SOFTWARE · LIVE DEMO", "s23": "SOFTWARE · HISTORY", "s24": "SOFTWARE · AI HARNESS", "s25": "SOFTWARE · AI MISALIGNMENT", "s28": "BACKUP · NEWTON", "s29": "BACKUP · ADAPTIVE STEP", "s30": "BACKUP · CODE AUDIT", "s31": "BACKUP · KNOWLEDGE MAP"}, "sources": {"s4": "Source: active/space_physics/eje_intermedio.py · PEI1(), Attitude_equations()", "s5": "Source: Kinetic_energy_2T(), Angular_momentum_L2(), Energy_ellipsoid(), Momentum_ellipsoid() · GUI page Motion", "s6": "Source: euler_jacobian(), Linear_eigenvalues() · PEI 1 statement, eqs. (9), (10), (12)", "s7": "Source: Energy_Casimir() in eje_intermedio.py", "s8": "Source: Separatrix(), Polhode_period(), Elliptic_K() · flip times measured with RK4, Δt = 0.02, I = (1, 2, 3)", "s10": "Source: active/numerical_engine/Cauchy_Problem.py · temporal_schemes.py", "s11": "Source: paso_crank_nicolson() in PEI1/PEI1.py · limitations table in numerical_engine/README.md (8 Oct)", "s12": "Source: curva_convergencia(), tramo_recto(), ordenes_locales() · GUI page Precision", "s13": "Source: presentacion/figuras/regiones_numericas.py · method of Stability_Region, jahrWork/MUSE_orbits_S1", "s14": "Source: stability_function() in Estabilidad.py · I = (1, 2, 3), Ω = 1, Δt = 0.02", "s15": "Source: GUI pages Conservation and Stability · intermediate axis, Δt = 0.02, t_f = 80", "s16": "Source: flip-time runs (ε = 10⁻¹², Δt = 0.1) · Estabilidad.py · convergence table, page Precision", "s19": "Source: imports of active/ and PEI1/PEI1.py", "s20": "Source: active/gui_reactive/README.md · PEI1/PEI1.py", "s21": "Screenshots captured by presentacion/figuras/capturar_gui.py from the real program", "s23": "Source: git log, 51 commits (MP-19-creator 20, Rubennezc 17, Ignacio Pérez 14)", "s24": "Source: active/*/README.md · tmp/visual_review.py · tmp/visual-review/", "s25": "Source: temporal_schemes.py · PEI1/PEI1.py (signature check) · numerical_engine/README.md · tmp/", "s28": "Source: NewtonRaphson.Jacobian(), central differences · check over 200 random states", "s29": "Source: Cauchy_problem_adaptive() in Cauchy_Problem.py", "s30": "Source: audit of the repository at commit f3eeb4b"}, "labels": {"s2": {"photo": "PENDING · real photo"}, "s8": {"trace": "ω(t) in body axes, intermediate axis, ε = 10⁻³"}, "s12": {"rich": "RK4: Richardson estimate (solid) on the reference error (dashed)"}, "s14": {"curve": "Amplification per step on the imaginary axis"}, "s15": {"two": "2T drift in time: Euler (red), CN (green), RK4 (purple)", "q": "|q| drift in time"}, "s18": {"hint": "Click a phase to jump to its slide; the eyebrow of every software slide links back here."}, "s19": {"leak": "one leak: physics imports partition()", "note": "The GUI imports neither layer: it receives data and two callbacks."}, "s21": {}, "s22": {"thumbs": ["Axis I₁: closed polhode", "Axis I₂: separatrix", "Axis I₃: closed polhode"]}, "s23": {"scale": "24 Sep → 2 Nov 2026 · dots placed to scale in days"}, "s28": {"law": "E(h) ≈ h²/6 · |F‴| + ε_mach · |F| / h.  F is bilinear, so F‴ = 0: only rounding is left, and a larger h is more accurate."}}}}');

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "The Intermediate Axis Theorem";

const W = T.slide.w;
const H = T.slide.h;
const MX = T.margins.x;
const CW = W - 2 * MX;
const K = T.colours;
const S = T.scale;
const FH = T.fonts.heading;
const FB = T.fonts.body;
const X = C.x;
const ASSET = (name) => path.join(__dirname, "figuras", name);

const TOP = 1.75;          // first line of the content band
const SOURCE_Y = 6.6;      // source caption (the motif line)
const FOOT_Y = 7.0;        // footer row

// ------------------------------------------------------------------ primitives
function text(s, body, opts) {
  s.addText(body, Object.assign({ margin: 0, fontFace: FB, fontSize: S.body, color: K.ink, valign: "top" }, opts));
}
function line(s, opts) {
  s.addShape(pres.shapes.LINE, Object.assign({}, opts));
}
function panel(s, opts) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ rectRadius: 0.1 }, opts));
}
function tint(colour, transparency) {
  return { color: colour, transparency: transparency };
}
function boxText(s, runs, opts) {
  // text drawn inside its own rounded shape: one element, fill judged by the lint
  s.addText(runs, Object.assign({
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, margin: [10, 12, 10, 12],
    fontFace: FB, fontSize: S.body, color: K.ink, valign: "top",
  }, opts));
}
function cells(raw) {
  const lead = raw.startsWith("!");
  return { lead: lead, parts: raw.replace(/^!\s*/, "").split(" | ") };
}
function lines(str) {
  return str.split(" / ");
}
function runsFrom(label, body, colourLabel, colourBody, sizeBody) {
  const out = [{ text: label, options: { bold: true, color: colourLabel, breakLine: true, paraSpaceAfter: 6 } }];
  const parts = body ? lines(body) : [];
  parts.forEach((p, i) => out.push({ text: p, options: { color: colourBody, fontSize: sizeBody || S.body, breakLine: i < parts.length - 1, paraSpaceAfter: 4 } }));
  return out;
}
function freeformTexts(block) {
  return block.map((l) => l.split(" | ").slice(1).join(" | "));
}
function pad2(n) {
  return (n < 10 ? "0" : "") + n;
}
function partOf(n) {
  if (n <= 8) return 0;
  if (n <= 16) return 1;
  if (n <= 26) return 2;
  return -1;
}

// ------------------------------------------------------------------ chrome
function footer(s, n, dark) {
  text(s, X.footer, {
    x: MX, y: FOOT_Y, w: 5.6, h: 0.28, fontSize: S.caption, color: dark ? K.paper : K.muted,
    valign: "middle", objectName: "deco-footer",
  });
  const active = partOf(n);
  const pw = 1.3, gap = 0.14;
  const x0 = W - MX - 0.9 - (3 * pw + 2 * gap);
  X.parts.forEach((label, i) => {
    const on = i === active;
    s.addText(label, {
      shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.14, x: x0 + i * (pw + gap), y: FOOT_Y, w: pw, h: 0.28,
      fill: on ? { color: K.accent } : tint(dark ? K.ink : K.paper, 0),
      line: { color: on ? K.accent : (dark ? K.paper : K.muted), width: 0.75 },
      margin: 0, fontFace: FB, fontSize: S.caption, bold: on, align: "center", valign: "middle",
      color: on ? K.paper : (dark ? K.paper : K.muted), objectName: "deco-tracker-" + (i + 1),
    });
  });
  text(s, pad2(n), {
    x: W - MX - 0.7, y: FOOT_Y, w: 0.7, h: 0.28, fontSize: S.caption, bold: true, align: "right",
    valign: "middle", color: dark ? K.paper : K.accent, objectName: "deco-slide-number",
  });
}

function header(s, key, backToMap) {
  const runs = [{ text: X.eyebrows[key], options: {} }];
  // the click action (whole box -> slide 18) is attached afterwards by enlazar.py: no underlined run
  if (backToMap) runs.push({ text: X.mapBack, options: {} });
  text(s, runs, {
    x: MX, y: 0.27, w: 8.4, h: 0.34, fontSize: S.caption, bold: true, color: K.accent, charSpacing: 1,
    valign: "middle", objectName: "deco-eyebrow",
  });
  s.addImage({ path: ASSET("recursos/logos_upm_etsiae_idr.png"), x: W - MX - 2.33, y: 0.24, w: 2.33, h: 0.384, objectName: "deco-logos" });
  line(s, { x: MX, y: 0.76, w: CW, h: 0, line: { color: K.muted, width: 0.75, transparency: 55 }, objectName: "deco-header-rule" });
}

function paperSlide(n, key, backToMap) {
  const s = pres.addSlide();
  s.background = { color: K.paper };
  header(s, key, backToMap);
  footer(s, n, false);
  return s;
}

function title(s, str) {
  text(s, str, {
    x: MX, y: 0.92, w: CW, h: 0.6, fontFace: FH, fontSize: S.h1, bold: true, color: K.ink,
    valign: "middle", objectName: "slides-lead:Title",
  });
}

function source(s, key) {
  if (!X.sources[key]) return;
  text(s, X.sources[key], {
    x: MX, y: SOURCE_Y, w: CW, h: 0.28, fontSize: S.caption, color: K.muted, valign: "middle",
    objectName: "deco-source",
  });
}

function notes(s, d) {
  s.addNotes(d.visual && /PENDING|real images|pending/.test(d.visual) ? d.notes + "\n\nVISUAL TO ADD: " + d.visual : d.notes);
}

// ------------------------------------------------------------------ reusable compositions
function cardRow(s, items, y, h, opts) {
  const o = opts || {};
  const n = items.length;
  const gap = 0.25;
  const w = (CW - (n - 1) * gap) / n;
  items.forEach((raw, i) => {
    const c = cells(raw);
    const x = MX + i * (w + gap);
    const pending = c.parts[0].startsWith(X.pending);
    boxText(s, runsFrom(c.parts[0], c.parts[1], c.lead ? K.paper : (pending ? K.muted : K.accent), c.lead ? K.paper : K.ink, o.size), {
      x: x, y: y, w: w, h: h,
      fill: c.lead ? { color: K.accent } : (pending ? tint(K.paper, 0) : tint(K.ink, 94)),
      line: pending ? { color: K.muted, width: 1, dashType: "dash" } : (c.lead ? { color: K.accent, width: 0 } : tint(K.ink, 100)),
      objectName: "slides-field:Block",
    });
  });
}

function comparison(s, items, y, h, extra) {
  const gap = 0.25;
  const w = (CW - gap) / 2;
  items.forEach((raw, i) => {
    const c = cells(raw);
    const x = MX + i * (w + gap);
    // panel first, then its text on top: a slot drawn by `extra` can share the panel without overlapping text
    panel(s, {
      x: x, y: y, w: w, h: h,
      fill: c.lead ? { color: K.accent } : tint(K.ink, 94),
      line: c.lead ? { color: K.accent, width: 0 } : tint(K.ink, 100),
      objectName: "deco-panel-" + i,
    });
    text(s, runsFrom(c.parts[0], c.parts[1], c.lead ? K.paper : K.accent, c.lead ? K.paper : K.ink), {
      x: x + 0.3, y: y + 0.25, w: w - 0.6, h: (extra ? h - 2.45 : h) - 0.45,
      objectName: "slides-field:Block",
    });
    if (extra) extra(x, y, w, h, c.lead);
  });
}

function table(s, block, opts) {
  const rows = block.map(cells);
  const data = rows.map((r, i) => r.parts.map((p) => {
    const header = i === 0;
    const pending = !header && r.parts[0].startsWith(X.pending);
    return {
      text: p,
      options: {
        fontFace: FB, fontSize: opts.size || S.body, bold: header || r.lead,
        color: header || r.lead ? K.paper : (pending ? K.muted : K.ink),
        italic: pending,
        fill: { color: header ? K.ink : (r.lead ? K.accent : K.paper) },
        valign: "middle",
        border: [{ type: "none" }, { type: "none" }, { type: "solid", pt: 0.75, color: K.muted }, { type: "none" }],
      },
    };
  }));
  s.addTable(data, {
    x: opts.x, y: opts.y, w: opts.w, colW: opts.colW, rowH: opts.rowH, margin: [4, 8, 4, 8],
    objectName: "slides-field:Block",
  });
}

function sectionSlide(n, d, key) {
  const s = pres.addSlide();
  s.background = { color: K.ink };
  const sec = X.sections[key];
  s.addText(sec.num, {
    shape: pres.shapes.OVAL, x: 8.4, y: 1.3, w: 4.2, h: 4.2, fill: { color: K.accent }, line: { color: K.accent, width: 0 },
    fontFace: FH, fontSize: S.display, bold: true, color: K.paper, align: "center", valign: "middle", margin: 0,
    objectName: "slides-ghost",
  });
  text(s, d.title, {
    x: MX, y: 2.55, w: 7.5, h: 1.3, fontFace: FH, fontSize: S.title, bold: true, color: K.paper,
    valign: "bottom", objectName: "slides-lead:Title",
  });
  text(s, sec.lines, {
    x: MX, y: 4.05, w: 7.5, h: 0.8, fontSize: S.body, color: K.paper, objectName: "deco-section-lines",
  });
  footer(s, n, true);
  notes(s, d);
}

// ------------------------------------------------------------------ 1. title
{
  const d = C.s1;
  const s = pres.addSlide();
  s.background = { color: K.paper };
  const px = 4.75;
  s.addShape(pres.shapes.RECTANGLE, {
    x: px, y: 0, w: W - px, h: H, fill: { color: K.ink }, line: { color: K.ink, width: 0 }, objectName: "deco-cover-panel",
  });
  s.addImage({ path: ASSET("recursos/logo_muse.png"), x: MX, y: 0.55, w: 2.4, h: 0.95, objectName: "deco-muse-logo" });
  text(s, X.cover.master, { x: MX, y: 1.62, w: 3.7, h: 0.6, fontSize: S.caption, color: K.muted, objectName: "deco-master" });
  text(s, X.cover.course, { x: MX, y: 5.55, w: 3.7, h: 0.4, fontSize: S.caption, bold: true, color: K.ink, objectName: "deco-course" });
  text(s, X.cover.authors, { x: MX, y: 6.0, w: 3.7, h: 0.9, fontSize: S.caption, color: K.ink, objectName: "deco-authors" });
  text(s, X.cover.eyebrow, {
    x: px + 0.6, y: 0.95, w: 7.3, h: 0.35, fontSize: S.caption, bold: true, color: K.paper, charSpacing: 1, objectName: "deco-cover-eyebrow",
  });
  text(s, d.title, {
    x: px + 0.6, y: 1.4, w: 7.3, h: 1.95, fontFace: FH, fontSize: S.display, bold: true, color: K.paper,
    valign: "bottom", objectName: "slides-lead:Title",
  });
  text(s, d.subtitle, {
    x: px + 0.6, y: 3.45, w: 7.0, h: 0.75, fontSize: S.body, color: K.paper, objectName: "slides-field:Subtitle",
  });
  s.addImage({ path: ASSET("recursos/portada_polodias.png"), x: 8.15, y: 4.35, w: 4.25, h: 2.95, objectName: "deco-cover-polhodes" });
  notes(s, d);
}

// ------------------------------------------------------------------ 2. hook: comparison with photo slots
{
  const d = C.s2;
  const s = paperSlide(2, "s2");
  title(s, d.title);
  comparison(s, d.block, TOP + 0.05, 4.75, (x, y, w, h, lead) => {
    s.addText(X.labels.s2.photo, {
      shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.08, x: x + 0.3, y: y + h - 2.2, w: w - 0.6, h: 1.9,
      fill: tint(lead ? K.accent : K.paper, lead ? 0 : 100),
      line: { color: lead ? K.paper : K.muted, width: 1, dashType: "dash" },
      fontFace: FB, fontSize: S.caption, bold: true, color: lead ? K.paper : K.ink, align: "center", valign: "middle", margin: 0,
      objectName: "deco-photo-slot",
    });
  });
  notes(s, d);
}

sectionSlide(3, C.s3, "s3");

// ------------------------------------------------------------------ 4. model
{
  const d = C.s4;
  const s = paperSlide(4, "s4");
  title(s, d.title);
  const t = freeformTexts(d.block);
  text(s, t[0], { x: MX, y: TOP + 0.1, w: 6.9, h: 0.45, bold: true, color: K.accent, objectName: "slides-field:Block" });
  boxText(s, lines(t[1]).map((l, i, a) => ({ text: l, options: { breakLine: i < a.length - 1, paraSpaceAfter: 10 } })), {
    x: MX, y: TOP + 0.7, w: 6.9, h: 2.0, fill: tint(K.accent, 92), line: tint(K.accent, 100),
    margin: [18, 22, 18, 22], valign: "middle", objectName: "slides-field:Block",
  });
  text(s, t[2], { x: MX, y: TOP + 2.95, w: 6.9, h: 0.9, color: K.ink, objectName: "slides-field:Block" });
  s.addImage({ path: ASSET("recursos/caja_eje2.png"), x: 8.05, y: TOP, w: 4.4, h: 3.79, objectName: "deco-gui-box" });
  source(s, "s4");
  notes(s, d);
}

// ------------------------------------------------------------------ 5. invariants
{
  const d = C.s5;
  const s = paperSlide(5, "s5");
  title(s, d.title);
  const t = freeformTexts(d.block);
  boxText(s, lines(t[0]).map((l, i, a) => ({ text: l, options: { breakLine: i < a.length - 1, paraSpaceAfter: 10 } })), {
    x: MX, y: TOP + 0.1, w: 5.9, h: 1.3, fill: tint(K.accent, 92), line: tint(K.accent, 100),
    margin: [14, 20, 14, 20], valign: "middle", objectName: "slides-field:Block",
  });
  text(s, t[1], { x: MX, y: TOP + 1.65, w: 5.9, h: 1.4, objectName: "slides-field:Block" });
  text(s, t[2], { x: MX, y: TOP + 3.2, w: 5.9, h: 1.2, objectName: "slides-field:Block" });
  s.addImage({ path: ASSET("recursos/poinsot_eje2.png"), x: 6.95, y: TOP - 0.05, w: 5.6, h: 4.64, objectName: "deco-gui-poinsot" });
  source(s, "s5");
  notes(s, d);
}

// ------------------------------------------------------------------ 6. linearisation table
{
  const d = C.s6;
  const s = paperSlide(6, "s6");
  title(s, d.title);
  table(s, d.block, { x: MX, y: TOP + 0.25, w: CW, colW: [2.0, 1.55, 4.35, 2.4, CW - 10.3], rowH: 0.66 });
  source(s, "s6");
  notes(s, d);
}

// ------------------------------------------------------------------ 7. Lyapunov cards
{
  const d = C.s7;
  const s = paperSlide(7, "s7");
  title(s, d.title);
  cardRow(s, d.block, TOP + 0.25, 3.9);
  source(s, "s7");
  notes(s, d);
}

// ------------------------------------------------------------------ 8. the flip
{
  const d = C.s8;
  const s = paperSlide(8, "s8");
  title(s, d.title);
  const t = freeformTexts(d.block);
  const gap = 0.25, w = (CW - 2 * gap) / 3;
  t.forEach((str, i) => {
    boxText(s, str, {
      x: MX + i * (w + gap), y: TOP, w: w, h: 1.85, fontSize: S.body,
      fill: i === 2 ? { color: K.accent } : tint(K.ink, 94), color: i === 2 ? K.paper : K.ink,
      line: i === 2 ? { color: K.accent, width: 0 } : tint(K.ink, 100), objectName: "slides-field:Block",
    });
  });
  s.addImage({ path: ASSET("recursos/omega_eje2.png"), x: MX, y: TOP + 2.05, w: CW, h: 2.22, objectName: "deco-gui-omega" });
  text(s, X.labels.s8.trace, { x: MX, y: TOP + 4.35, w: CW, h: 0.3, fontSize: S.caption, color: K.muted, objectName: "deco-trace-label" });
  source(s, "s8");
  notes(s, d);
}

sectionSlide(9, C.s9, "s9");

// ------------------------------------------------------------------ 10. engine process
{
  const d = C.s10;
  const s = paperSlide(10, "s10");
  title(s, d.title);
  const n = d.block.length, gap = 0.45, w = (CW - (n - 1) * gap) / n, y = TOP + 0.45, h = 3.4;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const x = MX + i * (w + gap);
    boxText(s, runsFrom(c.parts[0], c.parts[1], i === 2 ? K.paper : K.accent, i === 2 ? K.paper : K.ink), {
      x: x, y: y, w: w, h: h, fill: i === 2 ? { color: K.accent } : tint(K.ink, 94),
      line: i === 2 ? { color: K.accent, width: 0 } : tint(K.ink, 100), objectName: "slides-field:Block",
    });
    if (i < n - 1) {
      line(s, { x: x + w + 0.07, y: y + h / 2, w: gap - 0.14, h: 0, line: { color: K.ink, width: 1.5, endArrowType: "triangle" }, objectName: "deco-arrow-" + i });
    }
  });
  source(s, "s10");
  notes(s, d);
}

// ------------------------------------------------------------------ 11. fixed point vs Newton
{
  const d = C.s11;
  const s = paperSlide(11, "s11");
  title(s, d.title);
  comparison(s, d.block, TOP + 0.15, 4.3);
  source(s, "s11");
  notes(s, d);
}

// ------------------------------------------------------------------ 12. convergence
{
  const d = C.s12;
  const s = paperSlide(12, "s12");
  title(s, d.title);
  const t = freeformTexts(d.block);
  text(s, t[0], { x: MX, y: TOP + 0.1, w: 4.3, h: 1.2, objectName: "slides-field:Block" });
  boxText(s, t[1], {
    x: MX, y: TOP + 1.45, w: 4.3, h: 1.45, fill: { color: K.accent }, line: { color: K.accent, width: 0 },
    color: K.paper, bold: true, objectName: "slides-field:Block",
  });
  text(s, t[2], { x: MX, y: TOP + 3.1, w: 4.3, h: 1.5, objectName: "slides-field:Block" });
  s.addImage({ path: ASSET("recursos/convergencia.png"), x: 5.15, y: TOP - 0.05, w: 4.05, h: 4.5, objectName: "deco-gui-convergence" });
  s.addImage({ path: ASSET("recursos/richardson.png"), x: 9.4, y: TOP + 0.1, w: 3.33, h: 1.71, objectName: "deco-gui-richardson" });
  text(s, X.labels.s12.rich, { x: 9.4, y: TOP + 1.9, w: 3.33, h: 0.6, fontSize: S.caption, color: K.muted, objectName: "deco-richardson-label" });
  source(s, "s12");
  notes(s, d);
}

// ------------------------------------------------------------------ 13. measured stability regions
{
  const d = C.s13;
  const s = paperSlide(13, "s13");
  title(s, d.title);
  const t = freeformTexts(d.block);
  text(s, t[0], { x: MX, y: TOP, w: CW, h: 0.62, objectName: "slides-field:Block" });
  s.addImage({ path: ASSET("regiones_numericas.png"), x: (W - 10.6) / 2, y: TOP + 0.72, w: 10.6, h: 3.59, objectName: "deco-measured-regions" });
  text(s, t[1], { x: MX, y: TOP + 4.38, w: CW, h: 0.42, fontSize: S.caption, color: K.ink, objectName: "slides-field:Block" });
  source(s, "s13");
  notes(s, d);
}

// ------------------------------------------------------------------ 14. imaginary axis
{
  const d = C.s14;
  const s = paperSlide(14, "s14");
  title(s, d.title);
  const t = freeformTexts(d.block);
  text(s, t[0], { x: MX, y: TOP + 0.1, w: 5.0, h: 1.25, objectName: "slides-field:Block" });
  boxText(s, t[1], {
    x: MX, y: TOP + 1.5, w: 5.0, h: 1.75, fill: { color: K.accent }, line: { color: K.accent, width: 0 },
    color: K.paper, objectName: "slides-field:Block",
  });
  text(s, t[2], { x: MX, y: TOP + 3.45, w: 5.0, h: 0.9, objectName: "slides-field:Block" });
  s.addImage({ path: ASSET("eje_imaginario.png"), x: 5.95, y: TOP, w: 6.75, h: 3.93, objectName: "deco-imaginary-axis" });
  text(s, X.labels.s14.curve, { x: 5.95, y: TOP + 4.0, w: 6.75, h: 0.3, fontSize: S.caption, color: K.muted, objectName: "deco-curve-label" });
  source(s, "s14");
  notes(s, d);
}

// ------------------------------------------------------------------ 15. prediction vs simulation
{
  const d = C.s15;
  const s = paperSlide(15, "s15");
  title(s, d.title);
  table(s, d.block, { x: MX, y: TOP, w: CW, colW: [2.2, 2.9, 3.6, CW - 8.7], rowH: 0.5 });
  s.addImage({ path: ASSET("recursos/deriva_2T.png"), x: MX, y: TOP + 2.25, w: 4.33, h: 2.45, objectName: "deco-gui-drift-2T" });
  s.addImage({ path: ASSET("recursos/deriva_q.png"), x: MX + 4.55, y: TOP + 2.25, w: 3.57, h: 2.45, objectName: "deco-gui-drift-q" });
  text(s, [
    { text: X.labels.s15.two, options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: X.labels.s15.q, options: {} },
  ], { x: MX + 8.4, y: TOP + 2.35, w: CW - 8.4, h: 1.3, fontSize: S.caption, color: K.muted, objectName: "deco-drift-labels" });
  source(s, "s15");
  notes(s, d);
}

// ------------------------------------------------------------------ 16. limits
{
  const d = C.s16;
  const s = paperSlide(16, "s16");
  title(s, d.title);
  cardRow(s, d.block, TOP + 0.2, 4.3);
  source(s, "s16");
  notes(s, d);
}

sectionSlide(17, C.s17, "s17");

// ------------------------------------------------------------------ 18. interactive phase map
{
  const d = C.s18;
  const s = paperSlide(18, "s18");
  title(s, d.title);
  const cols = 5, gap = 0.3, w = (CW - (cols - 1) * gap) / cols, h = 1.7;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const target = parseInt(c.parts[2], 10);
    const link = {};   // whole-node click action to `target` is attached by enlazar.py
    const row = Math.floor(i / cols), col = i % cols;
    const lead = i === 8;
    boxText(s, [
      { text: pad2(i + 1), options: Object.assign({ bold: true, color: lead ? K.paper : K.accent, breakLine: true, paraSpaceAfter: 2 }, link) },
      { text: c.parts[0], options: Object.assign({ bold: true, color: lead ? K.paper : K.ink, breakLine: true, paraSpaceAfter: 4 }, link) },
      { text: c.parts[1] + "  ·  " + X.map.slideWord + " " + target, options: Object.assign({ fontSize: S.caption, color: lead ? K.paper : K.ink }, link) },
    ], {
      x: MX + col * (w + gap), y: TOP + 0.15 + row * (h + 0.35), w: w, h: h,
      fill: lead ? { color: K.accent } : tint(K.ink, 94), line: lead ? { color: K.accent, width: 0 } : tint(K.ink, 100),
      objectName: "slides-field:Block",
    });
  });
  text(s, X.labels.s18.hint, { x: MX, y: TOP + 4.35, w: CW, h: 0.35, fontSize: S.caption, color: K.muted, objectName: "deco-map-hint" });
  notes(s, d);
}

// ------------------------------------------------------------------ 19. architecture
{
  const d = C.s19;
  const s = paperSlide(19, "s19", true);
  title(s, d.title);
  const items = d.block.map((l) => cells(l.trim()));
  const top = items[0];
  const tw = 4.4, tx = (W - tw) / 2, ty = TOP + 0.05, th = 0.95;
  boxText(s, runsFrom(top.parts[0].split(":")[0], null, K.paper, K.paper), {
    x: tx, y: ty, w: tw, h: th, fill: { color: K.ink }, line: { color: K.ink, width: 0 }, align: "center", valign: "middle",
    objectName: "slides-field:Block",
  });
  const bw = 3.75, g = (CW - 3 * bw) / 2, by = TOP + 1.95, bh = 2.05;
  items.slice(1).forEach((c, i) => {
    const [name, role] = c.parts[0].split(": ");
    const x = MX + i * (bw + g);
    boxText(s, runsFrom(name, role, c.lead ? K.paper : K.accent, c.lead ? K.paper : K.ink), {
      x: x, y: by, w: bw, h: bh, fill: c.lead ? { color: K.accent } : tint(K.ink, 94),
      line: c.lead ? { color: K.accent, width: 0 } : tint(K.ink, 100), objectName: "slides-field:Block",
    });
    const cx = x + bw / 2, fromX = W / 2, y0 = ty + th + 0.05, hh = by - y0 - 0.05;
    const o = { y: y0, h: hh, line: { color: K.ink, width: 1.5, endArrowType: "triangle" }, objectName: "deco-dep-" + i };
    if (cx < fromX - 0.01) Object.assign(o, { x: cx, w: fromX - cx, flipH: true });
    else if (cx > fromX + 0.01) Object.assign(o, { x: fromX, w: cx - fromX });
    else Object.assign(o, { x: fromX, w: 0 });
    line(s, o);
  });
  line(s, { x: MX + bw + 0.04, y: by + bh / 2, w: g - 0.08, h: 0, line: { color: K.muted, width: 1.5, dashType: "dash", endArrowType: "triangle" }, objectName: "deco-leak-arrow" });
  text(s, X.labels.s19.leak, { x: MX, y: by + bh + 0.12, w: 7.0, h: 0.3, fontSize: S.caption, color: K.muted, objectName: "deco-leak-label" });
  text(s, X.labels.s19.note, { x: MX, y: by + bh + 0.5, w: CW, h: 0.35, bold: true, color: K.ink, objectName: "deco-gui-note" });
  source(s, "s19");
  notes(s, d);
}

// ------------------------------------------------------------------ 20. data flow
{
  const d = C.s20;
  const s = paperSlide(20, "s20", true);
  title(s, d.title);
  const rh = 0.78, gap = 0.12;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const y = TOP + 0.05 + i * (rh + gap);
    boxText(s, pad2(i + 1) + "  " + c.parts[0], {
      x: MX, y: y, w: 3.6, h: rh, fill: i === 1 ? { color: K.accent } : tint(K.ink, 94),
      line: i === 1 ? { color: K.accent, width: 0 } : tint(K.ink, 100), bold: true,
      color: i === 1 ? K.paper : K.ink, valign: "middle", objectName: "slides-field:Block",
    });
    text(s, c.parts[1], { x: MX + 3.9, y: y, w: CW - 3.9, h: rh, valign: "middle", objectName: "slides-field:Block" });
  });
  source(s, "s20");
  notes(s, d);
}

// ------------------------------------------------------------------ 21. GUI tour
{
  const d = C.s21;
  const s = paperSlide(21, "s21", true);
  title(s, d.title);
  const n = 4, gap = 0.22, w = (CW - (n - 1) * gap) / n, h = w / 1.714;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const x = MX + i * (w + gap);
    s.addImage({ path: ASSET("recursos/gui_p" + (i + 1) + ".png"), x: x, y: TOP + 0.15, w: w, h: h, objectName: "deco-gui-page-" + (i + 1) });
    boxText(s, runsFrom(c.parts[0], c.parts[1], c.lead ? K.paper : K.accent, c.lead ? K.paper : K.ink), {
      x: x, y: TOP + h + 0.4, w: w, h: 2.15, fill: c.lead ? { color: K.accent } : tint(K.ink, 94),
      line: c.lead ? { color: K.accent, width: 0 } : tint(K.ink, 100), objectName: "slides-field:Block",
    });
  });
  source(s, "s21");
  notes(s, d);
}

// ------------------------------------------------------------------ 22. demo plan
{
  const d = C.s22;
  const s = paperSlide(22, "s22", true);
  title(s, d.title);
  table(s, d.block, { x: MX, y: TOP, w: CW, colW: [3.1, 4.6, CW - 7.7], rowH: 0.52, size: S.body });
  ["poinsot_eje1.png", "poinsot_eje2.png", "poinsot_eje3.png"].forEach((f, i) => {
    const x = MX + i * 4.1;
    s.addImage({ path: ASSET("recursos/" + f), x: x, y: TOP + 3.0, w: 2.15, h: 1.78, objectName: "deco-demo-thumb-" + i });
    text(s, X.labels.s22.thumbs[i], { x: x + 2.25, y: TOP + 3.6, w: 1.6, h: 0.6, fontSize: S.caption, color: K.ink, objectName: "deco-demo-label-" + i });
  });
  notes(s, d);
}

// ------------------------------------------------------------------ 23. timeline (spacing proportional to dates)
{
  const d = C.s23;
  const s = paperSlide(23, "s23", true);
  title(s, d.title);
  const days = [0, 12, 30, 33, 39];
  const x0 = MX + 0.9, x1 = W - MX - 1.1, ry = TOP + 2.3;
  line(s, { x: x0 - 0.3, y: ry, w: x1 - x0 + 0.6, h: 0, line: { color: K.muted, width: 2 }, objectName: "deco-rail" });
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const cx = x0 + (x1 - x0) * days[i] / 39;
    const r = c.lead ? 0.17 : 0.11;
    s.addShape(pres.shapes.OVAL, {
      x: cx - r, y: ry - r, w: 2 * r, h: 2 * r, fill: { color: c.lead ? K.accent : K.ink },
      line: { color: c.lead ? K.accent : K.ink, width: 0 }, objectName: "deco-dot-" + i,
    });
    // three dates fall in the last nine days: alternate sides and anchor the end labels to their dot
    const above = i % 2 === 1;
    const align = ["left", "center", "right", "center", "right"][i];
    const lw = i === 4 ? 2.15 : 2.4;
    const reach = i === 2 ? 0.05 : 0.2;
    const lx = align === "center" ? cx - lw / 2 : (align === "left" ? Math.max(cx - 0.2, MX) : Math.min(cx + reach, W - MX) - lw);
    text(s, [
      { text: c.parts[0], options: { bold: true, color: c.lead ? K.accent : K.ink, breakLine: true } },
      { text: c.parts[1], options: { color: K.ink } },
    ], {
      x: lx, y: above ? ry - 1.55 : ry + 0.35, w: lw, h: 1.2, align: align,
      valign: above ? "bottom" : "top", objectName: "slides-field:Block",
    });
  });
  text(s, X.labels.s23.scale, { x: MX, y: TOP + 4.3, w: CW, h: 0.3, fontSize: S.caption, color: K.muted, objectName: "deco-rail-scale" });
  source(s, "s23");
  notes(s, d);
}

// ------------------------------------------------------------------ 24. harness
{
  const d = C.s24;
  const s = paperSlide(24, "s24", true);
  title(s, d.title);
  comparison(s, d.block.map((l) => l.replace(/\. /g, ". / ")), TOP + 0.1, 4.55);
  source(s, "s24");
  notes(s, d);
}

// ------------------------------------------------------------------ 25. AI mistakes (2 x 2)
{
  const d = C.s25;
  const s = paperSlide(25, "s25", true);
  title(s, d.title);
  const gap = 0.25, w = (CW - gap) / 2, h = 2.18;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const pending = c.parts[0].startsWith(X.pending);
    boxText(s, runsFrom(c.parts[0], c.parts[1], c.lead ? K.paper : (pending ? K.muted : K.accent), c.lead ? K.paper : K.ink), {
      x: MX + (i % 2) * (w + gap), y: TOP + Math.floor(i / 2) * (h + 0.2), w: w, h: h,
      fill: c.lead ? { color: K.accent } : (pending ? tint(K.paper, 0) : tint(K.ink, 94)),
      line: pending ? { color: K.muted, width: 1, dashType: "dash" } : (c.lead ? { color: K.accent, width: 0 } : tint(K.ink, 100)),
      objectName: "slides-field:Block",
    });
  });
  source(s, "s25");
  notes(s, d);
}

// ------------------------------------------------------------------ 26. close
{
  const d = C.s26;
  const s = pres.addSlide();
  s.background = { color: K.ink };
  text(s, d.statement, {
    x: MX, y: 1.3, w: 10.6, h: 3.6, fontFace: FH, fontSize: S.title, bold: true, color: K.paper,
    valign: "bottom", objectName: "slides-lead:Statement",
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: MX, y: 5.35, w: 0.9, h: 0.12, rectRadius: 0.06, fill: { color: K.accent }, line: { color: K.accent, width: 0 }, objectName: "slides-ghost",
  });
  text(s, X.close, { x: MX, y: 5.65, w: 8, h: 0.45, fontSize: S.body, color: K.paper, objectName: "deco-close-line" });
  footer(s, 26, true);
  notes(s, d);
}

sectionSlide(27, C.s27, "s27");

// ------------------------------------------------------------------ 28. FD Jacobian
{
  const d = C.s28;
  const s = paperSlide(28, "s28");
  title(s, d.title);
  table(s, d.block, { x: MX, y: TOP + 0.1, w: 7.4, colW: [2.6, 4.8], rowH: 0.55 });
  boxText(s, X.labels.s28.law, {
    x: 8.3, y: TOP + 0.1, w: W - MX - 8.3, h: 2.2, fill: tint(K.accent, 92), line: tint(K.accent, 100), objectName: "deco-fd-law",
  });
  source(s, "s28");
  notes(s, d);
}

// ------------------------------------------------------------------ 29. adaptive step
{
  const d = C.s29;
  const s = paperSlide(29, "s29");
  title(s, d.title);
  const n = d.block.length, gap = 0.45, w = (CW - (n - 1) * gap) / n, y = TOP + 0.4, h = 2.6;
  d.block.forEach((raw, i) => {
    const c = cells(raw);
    const x = MX + i * (w + gap);
    boxText(s, runsFrom(pad2(i + 1) + "  " + c.parts[0], c.parts[1], K.accent, K.ink), {
      x: x, y: y, w: w, h: h, fill: tint(K.ink, 94), line: tint(K.ink, 100), objectName: "slides-field:Block",
    });
    if (i < n - 1) line(s, { x: x + w + 0.07, y: y + h / 2, w: gap - 0.14, h: 0, line: { color: K.ink, width: 1.5, endArrowType: "triangle" }, objectName: "deco-arrow-" + i });
  });
  source(s, "s29");
  notes(s, d);
}

// ------------------------------------------------------------------ 30. known defects
{
  const d = C.s30;
  const s = paperSlide(30, "s30");
  title(s, d.title);
  table(s, d.block, { x: MX, y: TOP, w: CW, colW: [6.6, 3.9, CW - 10.5], rowH: 0.62 });
  source(s, "s30");
  notes(s, d);
}

// ------------------------------------------------------------------ 31. knowledge map (pending)
{
  const d = C.s31;
  const s = paperSlide(31, "s31");
  title(s, d.title);
  const t = freeformTexts(d.block);
  s.addText(t[0], {
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: TOP + 0.1, w: CW, h: 4.5,
    fill: tint(K.paper, 0), line: { color: K.muted, width: 1.25, dashType: "dash" },
    fontFace: FB, fontSize: S.body, color: K.ink, align: "center", valign: "middle", margin: [20, 60, 20, 60],
    objectName: "slides-field:Block",
  });
  notes(s, d);
}

pres
  .writeFile({ fileName: outPath })
  .then(() => console.log("wrote " + outPath))
  .catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
