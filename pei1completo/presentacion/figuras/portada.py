"""Polodias de la portada, integradas con el propio motor (RK4) sobre el elipsoide de energia de I = (1, 2, 3).

Ejecutar desde la raiz del repositorio:  python presentacion/figuras/portada.py
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from numpy import array, cos, sin, sqrt, linspace, pi
import matplotlib.pyplot as plt

from active.space_physics.eje_intermedio import Rigid_body_problem, Separatrix, Polhode_period
from active.space_physics.eje_intermedio import Kinetic_energy_2T, Angular_momentum_L2
from active.numerical_engine.Cauchy_Problem import Cauchy_problem
from active.numerical_engine.temporal_schemes import RK4

I = (1., 2., 3.)
T2 = 2.0
F = Rigid_body_problem(I, attitude=False)

# vista oblicua: rotacion en torno a z y luego en torno a x
a, b = 0.62, -0.42
R = array([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])
R = array([[1, 0, 0], [0, cos(b), -sin(b)], [0, sin(b), cos(b)]]) @ R


def proyectar(W):
    P = W @ R.T
    return P[:, 0], P[:, 2]


fig, ax = plt.subplots(figsize=(6, 6))
for eje, angulos in ((0, (0.25, 0.5, 0.8, 1.05)), (2, (0.2, 0.45, 0.7, 0.95))):
    for s in angulos:
        for signo in (1, -1):
            w0 = [0., 0., 0.]
            w0[eje] = signo * sqrt(T2 / I[eje]) * cos(s)
            otro = 1
            w0[otro] = sqrt(T2 / I[otro]) * sin(s)
            w0 = array(w0) * sqrt(T2 / Kinetic_energy_2T(array(w0), I))
            P = Polhode_period(I, Kinetic_energy_2T(w0, I), Angular_momentum_L2(w0, I))
            t = linspace(0, P, 1200)
            U = Cauchy_problem(F, t, w0, RK4)
            x, y = proyectar(U)
            ax.plot(x, y, color="#A78BFA", lw=1.4, alpha=0.85)
for curva in Separatrix(I, T2):
    x, y = proyectar(curva.T)
    ax.plot(x, y, color="#FFFFFF", lw=2.2)
ax.set_aspect("equal")
ax.axis("off")
fig.savefig(os.path.join(os.path.dirname(__file__), "recursos", "portada_polodias.png"), dpi=200,
            transparent=True, bbox_inches="tight")
print("ok")
