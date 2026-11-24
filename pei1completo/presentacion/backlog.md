# Engineering backlog (separate from the presentation)

None of this has been changed in the code. Everything below was found by auditing the repository at commit f3eeb4b. Priorities: P1 before the defence if possible, P2 for PEI 2, P3 when convenient.

## A. Finite-difference Jacobian

**State: implemented, not validated in the repository.**

- `active/numerical_engine/NewtonRaphson.py`, `Jacobian(F, U)`: central differences, fixed h = 1e-3, same as `jahrWork/MUSE_orbits_S1/.../Newton.py`. `Newton` always uses it, and so does `Euler_implicit`.
- The GUI does not use it: its Crank-Nicolson (`paso_crank_nicolson` in `PEI1/PEI1.py`) uses the analytical `F.jacobian`.
- Measured on 2 Nov (7×7 system, 200 random states), max relative error against `F.jacobian`: 6e-15 (h = 0.1), 8e-13 (h = 1e-3), 6e-10 (h = 1e-6). Our F is bilinear, so the truncation term h²/6·F‴ vanishes and only rounding (≈ ε·|F|/h) remains.

Tasks:
1. (P1) Add `tests/test_jacobian.py`: compare `Jacobian` with `F.jacobian` at random states for the 3-state and 7-state systems; tolerance 1e-10.
2. (P2) Step size: h_i = ε^{1/3}·max(1, |U_i|) for general F (balances h² truncation against ε/h rounding); keep it as a parameter.
3. (P2) In Crank-Nicolson, fall back to the numerical Jacobian when F has no `jacobian` attribute instead of failing, so the engine stays problem-agnostic.
4. (P2) Kepler: no analytical Jacobian exists; use it as the test case for the fallback.

## B. Stability regions from the numerical scheme

**State: done for the presentation, outside the engine.**

- `presentacion/figuras/regiones_numericas.py` measures |U₁| after one real step of Euler, implicit Euler, Crank-Nicolson and RK4 (method of `Stability_Region`, jahrWork/MUSE_orbits_S1), using the real 2×2 form of λ because our Newton is real-valued. It agrees with `Estabilidad.stability_function` to ≤ 2e-12.

Tasks:
1. (P1) Move a `measured_stability_region(method, x, y)` function into `numerical_engine/Estabilidad.py` and let the GUI page Stability draw the measured boundary over the formula.
2. (P2) Make Newton accept complex states so the professor's scalar test (`F = lambda U, t: w*U`) runs unchanged.

## C. Known defects (from the audit)

| P | Defect | Where | Fix |
|---|---|---|---|
| P1 | `Crank_Nicolson` calls `Newton(G, U0, dG)` but `Newton` takes 2 arguments (TypeError). `PEI1.py` hides it with `signature(Newton)` and its own step. | `temporal_schemes.py`, `PEI1/PEI1.py` | Give `Newton` an optional Jacobian argument, and delete the shim and `paso_crank_nicolson`. |
| P1 | `Newton` raises `RuntimeError`; `Cauchy_problem` only catches `ArithmeticError`, so a failure is not turned into `Integration_stopped`. | `NewtonRaphson.py` | Raise `Newton_failed` (already defined). |
| P1 | `Gauss` calls `exit()` on a singular matrix: kills the GUI. | `NewtonRaphson.py` | Raise `Newton_failed` instead. |
| P2 | `Leap_Frog` keeps global state and has no `start()`, so a second integration reuses the previous one's memory. | `temporal_schemes.py` | Wrap it in a class with `start()`. |
| P2 | `tmp/visual_review.py` and `tmp/check_gui_controls.py` call functions that the last GUI rewrite removed. | `tmp/` | Rewrite them against the current API, or delete them. |
| P3 | Physics imports `partition` from the engine (breaks the layering its own docstring states). | `eje_intermedio.py` | Use `numpy.linspace`. |
| P3 | Root `README.md` and `hitos/README.md` are out of date (say GUI not started, Richardson not written). | `README.md`, `hitos/README.md` | Update the status tables. |
| P3 | `.env` contains an absolute path from one machine. | `.env` | Remove it from version control; `launch.json` already sets PYTHONPATH. |
| P3 | GUI labels mix Spanish and English. | `active/gui_reactive/` | Choose one language. |

## D. Automatic project knowledge map

**State: not started.** The preliminary deck had a NotebookLM placeholder. NotebookLM cannot read the repository by itself: it only sees uploaded documents, so anything it shows goes stale with the next commit.

Proposed design, all generated from the repository:
1. `tools/mapa_proyecto.py` parses every `.py` with `ast`: modules, public functions with their first docstring line, and imports between modules.
2. It writes `docs/mapa.mmd` (Mermaid graph: layers as subgraphs, imports as arrows, leaks in red) and `docs/mapa.md` (table: file → responsibility, read from the docstrings and README sections).
3. A pre-commit hook or a GitHub Action reruns it, so the map changes with the code. GitHub renders Mermaid directly.
4. Optional: upload `docs/mapa.md` plus the READMEs to NotebookLM for a conversational view. It is a snapshot, not a live sync.

Effort: about half a day. The import graph alone would have found the `partition` leak on day one.

## E. Workflow and documentation

1. (P1) Turn the one-off scripts into `pytest` tests: Jacobian check, orders of convergence on the oscillator (exact solution), regions measured against the formula, bit-for-bit regression of the three schemes.
2. (P2) An instructions file for the assistant in the repository (layers, interfaces, "never import across layers", "run the tests before proposing a change").
3. (P2) Run the tests on every push (GitHub Actions).
