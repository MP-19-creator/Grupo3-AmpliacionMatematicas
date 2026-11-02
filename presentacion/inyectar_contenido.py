"""Vuelca el contenido del spec (PEI1_final.deck.md) y las etiquetas de los diagramas en la linea
`const C = JSON.parse(...)` de PEI1_final.build.cjs. Asi todo texto del deck vive en un solo sitio.

Ejecutar antes de construir:  python presentacion/inyectar_contenido.py
"""
import json
import os
import re

aqui = os.path.dirname(os.path.abspath(__file__))
spec = os.path.join(aqui, "PEI1_final.deck.md")
script = os.path.join(aqui, "PEI1_final.build.cjs")
CAMPOS = ("layout", "Brief", "Title", "Subtitle", "Statement", "Notes", "Visual", "Block")


def leer_spec(ruta):
    texto = open(ruta, encoding="utf-8").read()
    partes = re.split(r"^## Slide (\d+)\s*$", texto, flags=re.M)
    slides = {}
    for numero, cuerpo in zip(partes[1::2], partes[2::2]):
        datos, campo = {}, None
        for linea in cuerpo.strip("\n").split("\n"):
            m = re.match(r"^(%s):\s?(.*)$" % "|".join(CAMPOS), linea)
            if m:
                campo = m.group(1)
                if campo == "Block":
                    datos["blockType"] = m.group(2).strip()
                    datos["block"] = []
                else:
                    datos[campo] = m.group(2).strip()
            elif campo == "Block":
                if linea.strip():
                    datos["block"].append(linea.strip())
            elif campo:
                datos[campo] = (datos[campo] + "\n" + linea).strip("\n") if datos[campo] else linea
        slides["s" + numero] = {k[0].lower() + k[1:]: v.strip() if isinstance(v, str) else v
                                for k, v in datos.items()}
    return slides


extra = {
    "footer": "MUSE · UPM · Ampliación de Matemáticas 1 · PEI 1",
    "parts": ["Physics", "Engine", "Software"],
    "mapBack": "   ↩ phase map",
    "pending": "PENDING",
    "map": {"goTo": "Go to slide", "back": "Back to the phase map", "slideWord": "slide"},
    "cover": {
        "master": "Máster Universitario en Sistemas Espaciales",
        "eyebrow": "AMPLIACIÓN DE MATEMÁTICAS 1 · PEI 1",
        "course": "Ampliación de Matemáticas 1 · Course 2026–2027",
        "authors": "Rubén Núñez Cuenca, Mario Penin Fernández and Ignacio Pérez González",
    },
    "sections": {
        "s3": {"num": "1", "lines": "Model · invariants · linearisation · Lyapunov · the flip"},
        "s9": {"num": "2", "lines": "Cauchy problem · Newton · Richardson · measured stability regions"},
        "s17": {"num": "3", "lines": "Phase map · architecture · GUI · demo · how we worked with AI"},
        "s27": {"num": "+", "lines": "Finite-difference Jacobian · adaptive step · defects · knowledge map"},
    },
    "close": "Individual defence · questions",
    "eyebrows": {
        "s2": "PHYSICS · WHY THIS PROBLEM", "s4": "PHYSICS · MODEL", "s5": "PHYSICS · INVARIANTS",
        "s6": "PHYSICS · LINEAR STABILITY", "s7": "PHYSICS · NONLINEAR STABILITY", "s8": "PHYSICS · THE FLIP",
        "s10": "ENGINE · ARCHITECTURE", "s11": "ENGINE · IMPLICIT SCHEMES", "s12": "ENGINE · CONVERGENCE",
        "s13": "ENGINE · STABILITY REGIONS", "s14": "ENGINE · THE RIGID BODY IN THE REGIONS",
        "s15": "ENGINE · VALIDATION", "s16": "ENGINE · LIMITS",
        "s18": "SOFTWARE · DEVELOPMENT MAP", "s19": "SOFTWARE · ARCHITECTURE", "s20": "SOFTWARE · DATA FLOW",
        "s21": "SOFTWARE · GUI", "s22": "SOFTWARE · LIVE DEMO", "s23": "SOFTWARE · HISTORY",
        "s24": "SOFTWARE · AI HARNESS", "s25": "SOFTWARE · AI MISALIGNMENT",
        "s28": "BACKUP · NEWTON", "s29": "BACKUP · ADAPTIVE STEP", "s30": "BACKUP · CODE AUDIT",
        "s31": "BACKUP · KNOWLEDGE MAP",
    },
    "sources": {
        "s4": "Source: active/space_physics/eje_intermedio.py · PEI1(), Attitude_equations()",
        "s5": "Source: Kinetic_energy_2T(), Angular_momentum_L2(), Energy_ellipsoid(), Momentum_ellipsoid() · GUI page Motion",
        "s6": "Source: euler_jacobian(), Linear_eigenvalues() · PEI 1 statement, eqs. (9), (10), (12)",
        "s7": "Source: Energy_Casimir() in eje_intermedio.py",
        "s8": "Source: Separatrix(), Polhode_period(), Elliptic_K() · flip times measured with RK4, Δt = 0.02, I = (1, 2, 3)",
        "s10": "Source: active/numerical_engine/Cauchy_Problem.py · temporal_schemes.py",
        "s11": "Source: paso_crank_nicolson() in PEI1/PEI1.py · limitations table in numerical_engine/README.md (8 Oct)",
        "s12": "Source: curva_convergencia(), tramo_recto(), ordenes_locales() · GUI page Precision",
        "s13": "Source: presentacion/figuras/regiones_numericas.py · method of Stability_Region, jahrWork/MUSE_orbits_S1",
        "s14": "Source: stability_function() in Estabilidad.py · I = (1, 2, 3), Ω = 1, Δt = 0.02",
        "s15": "Source: GUI pages Conservation and Stability · intermediate axis, Δt = 0.02, t_f = 80",
        "s16": "Source: flip-time runs (ε = 10⁻¹², Δt = 0.1) · Estabilidad.py · convergence table, page Precision",
        "s19": "Source: imports of active/ and PEI1/PEI1.py",
        "s20": "Source: active/gui_reactive/README.md · PEI1/PEI1.py",
        "s21": "Screenshots captured by presentacion/figuras/capturar_gui.py from the real program",
        "s23": "Source: git log, 51 commits (MP-19-creator 20, Rubennezc 17, Ignacio Pérez 14)",
        "s24": "Source: active/*/README.md · tmp/visual_review.py · tmp/visual-review/",
        "s25": "Source: temporal_schemes.py · PEI1/PEI1.py (signature check) · numerical_engine/README.md · tmp/",
        "s28": "Source: NewtonRaphson.Jacobian(), central differences · check over 200 random states",
        "s29": "Source: Cauchy_problem_adaptive() in Cauchy_Problem.py",
        "s30": "Source: audit of the repository at commit f3eeb4b",
    },
    "labels": {
        "s2": {"photo": "PENDING · real photo"},
        "s8": {"trace": "ω(t) in body axes, intermediate axis, ε = 10⁻³"},
        "s12": {"rich": "RK4: Richardson estimate (solid) on the reference error (dashed)"},
        "s14": {"curve": "Amplification per step on the imaginary axis"},
        "s15": {"two": "2T drift in time: Euler (red), CN (green), RK4 (purple)",
                "q": "|q| drift in time"},
        "s18": {"hint": "Click a phase to jump to its slide; the eyebrow of every software slide links back here."},
        "s19": {"leak": "one leak: physics imports partition()",
                "note": "The GUI imports neither layer: it receives data and two callbacks."},
        "s21": {},
        "s22": {"thumbs": ["Axis I₁: closed polhode", "Axis I₂: separatrix", "Axis I₃: closed polhode"]},
        "s23": {"scale": "24 Sep → 2 Nov 2026 · dots placed to scale in days"},
        "s28": {"law": "E(h) ≈ h²/6 · |F‴| + ε_mach · |F| / h.  F is bilinear, so F‴ = 0: only rounding is left, and a larger h is more accurate."},
    },
}


def main():
    contenido = leer_spec(spec)
    contenido["x"] = extra
    linea_json = json.dumps(contenido, ensure_ascii=False)
    literal = linea_json.replace("\\", "\\\\").replace("'", "\\'")
    nueva = "const C = JSON.parse('" + literal + "');"
    lineas = open(script, encoding="utf-8").read().split("\n")
    indices = [i for i, l in enumerate(lineas) if l.startswith("const C = JSON.parse(")]
    if len(indices) != 1:
        raise SystemExit("PEI1_final.build.cjs debe tener exactamente una linea 'const C = JSON.parse('")
    lineas[indices[0]] = nueva
    open(script, "w", encoding="utf-8", newline="\n").write("\n".join(lineas))
    print(f"{len(contenido) - 1} slides inyectadas en {os.path.basename(script)}")


if __name__ == "__main__":
    main()
