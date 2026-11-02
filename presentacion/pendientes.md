# Outstanding items before the defence

Inputs the deck needs from the team. Each one is marked PENDING in the deck.

| # | Item | Slide | Owner | What is needed |
|---|---|---|---|---|
| 1 | Real photos | 2 | Rubén | A still of the Dzhanibekov wing nut (Salyut 7 / ISS videos) and a photo of Explorer 1, with source. |
| 2 | Unusual GUI cases | 22 | Ignacio | Choose 1–2 of: I₁ ≈ I₂ (near-symmetric body), I₁ + I₂ < I₃ (GUI warns: non-physical), Δt beyond RK4's limit 2.83 s on axis 3, adaptive step. Note the parameters, check them in the GUI, save screenshots. |
| 3 | Our own AI episodes | 25 | All | Two or three real exchanges with the assistant: the request, what it produced, how we noticed it was wrong, the correction. Screenshots or copied prompts. |
| 4 | Knowledge map | 31 | All | Not built yet: see backlog task D. Remove slide 31 if it is not ready. |
| 5 | Demo rehearsal | 22 | Ignacio | Time the demo (target 2 min) and decide whether to show the GUI from the start or switch windows. Run `python PEI1/PEI1.py` from the repository root. |
| 6 | Timing rehearsal | all | All | The notes add up to about 20 minutes. Rehearse with a timer and cut notes, not slides. |
| 7 | Mixed-language GUI | 8, 21, 22 | Ignacio | The screenshots show Spanish labels (Movimiento, VELOCIDAD ANGULAR) next to English ones. Accept it, or unify the GUI language and re-run `figuras/capturar_gui.py`. |
| 8 | Spelling of names | 1, 9 | Mario | The preliminary deck wrote "Mario Penin Fernández"; confirm the accent on Penín. |

## Checked and closed during the preparation

- Juan Antonio's repository (jahrWork/MUSE_orbits_S1) reviewed: `ODES/Stability_regions.py` measures regions by running the scheme, and our slide 13 uses that method on our own code. `Newton.py` has the same central-difference Jacobian we use.
- Every number in the deck was regenerated from the code on 2 Nov 2026 (commit f3eeb4b).
