"""Regiones de estabilidad obtenidas EJECUTANDO los esquemas del motor, no con la formula de R(z).

Metodo (el de Stability_Region en jahrWork/MUSE_orbits_S1): un paso de tamano dt = 1 sobre el problema test
dU/dt = lambda U desde U0 = 1; el modulo del resultado es |R(z)| con z = lambda.

Nuestro Newton trabaja en reales, asi que lambda = a + i b se escribe como el sistema real equivalente
        dU/dt = A U,   A = [[a, -b], [b, a]],   U0 = (1, 0)
Toda funcion racional de A tiene la misma forma, de modo que |U1| = |R(z)| exactamente.

Esquemas que se ejecutan:
  Euler, RK4            -> active/numerical_engine/temporal_schemes.py
  Crank-Nicolson        -> el paso que usa la GUI (PEI1/PEI1.py, Newton con el Jacobiano exacto F.jacobian)
  Euler implicito       -> temporal_schemes.Euler_implicit (Newton con Jacobiano por DIFERENCIAS FINITAS)

Ejecutar desde la raiz del repositorio:  python presentacion/figuras/regiones_numericas.py
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, raiz)

import json
import warnings
from numpy import array, linspace, zeros, full, nan, isfinite, abs, nanmax, sqrt
from numpy.linalg import norm
import matplotlib.pyplot as plt

from active.numerical_engine.temporal_schemes import Euler, RK4, Euler_implicit
from active.numerical_engine.Estabilidad import stability_function
from active.space_physics.eje_intermedio import Linear_eigenvalues
from PEI1.PEI1 import metodos

import estilo

salida = os.path.dirname(__file__)
esquemas = [("Euler", Euler, "Euler"),
            ("Implicit Euler", Euler_implicit, "Euler_implicit"),
            ("Crank-Nicolson", metodos["Crank-Nicolson"], "Crank_Nicolson"),
            ("RK4", RK4, "RK4")]


def problema_test(a, b):
    A = array([[a, -b], [b, a]])
    def F(U, t):
        return A @ U
    F.jacobian = lambda U, t: A
    return F


def amplificacion_numerica(esquema, x, y):
    """|U1| tras UN paso real del esquema; nan donde el paso no se puede dar (Newton falla, sistema singular)."""
    rho = full((len(y), len(x)), nan)
    for j, b in enumerate(y):
        for i, a in enumerate(x):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    U1 = esquema(array([1., 0.]), 1., 0., problema_test(a, b))
            except (ArithmeticError, RuntimeError, SystemExit, ValueError):
                continue
            if isfinite(U1).all():
                rho[j, i] = norm(U1)
    return rho


x = linspace(-4.0, 2.6, 133)
y = linspace(-3.6, 3.6, 145)
X, Y = x[None, :], y[:, None]

resultados = {}
fig, ejes = plt.subplots(1, 4, figsize=(13.4, 3.9), sharey=True)
for ax, (titulo, esquema, nombre) in zip(ejes, esquemas):
    rho = amplificacion_numerica(esquema, x, y)
    exacta = abs(stability_function(nombre, X + 1j*Y))
    dentro = isfinite(rho) & (rho < 50)
    diferencia = nanmax(abs(rho[dentro] - exacta[dentro]) / exacta[dentro])
    fallos = int((~isfinite(rho)).sum())
    resultados[titulo] = dict(max_rel_diff=float(diferencia), failed_points=fallos, points=int(rho.size))

    estilo.region(ax, x, y, rho, exacta)
    ax.set_title(titulo, loc="left")
    ax.set_xlabel(r"Re $z$")
    print(f"{titulo:15s} max |rho_num - |R|| / |R| = {diferencia:.2e}   failed steps: {fallos}/{rho.size}")
ejes[0].set_ylabel(r"Im $z$")
estilo.leyenda_regiones(fig)
fig.savefig(os.path.join(salida, "regiones_numericas.png"), dpi=220)
fig.savefig(os.path.join(salida, "regiones_numericas.pdf"))

# ---------------------------------------------------------------- el problema dentro de las regiones
# Autovalores z = lambda dt del solido rigido para el caso por defecto de la GUI
I, Omega, dt = (1., 2., 3.), 1., 0.02
z = {eje: Linear_eigenvalues(I, eje, Omega) * dt for eje in range(3)}
z_q = 0.5 * Omega * dt
resultados["rigid_body_default"] = dict(
    I=I, Omega=Omega, dt=dt,
    z_axis={str(eje): [str(v) for v in z[eje]] for eje in z},
    z_quaternion=f"±{z_q:.4g}i",
    rk4_dt_max_axis1=float(2*sqrt(2) / abs(z[0][0]) * dt),
    rk4_dt_max_axis3=float(2*sqrt(2) / abs(z[2][0]) * dt))

y_im = linspace(0, 3.2, 400)
fig2, ax2 = plt.subplots(figsize=(6.2, 3.6))
estilo.eje_imaginario(ax2, y_im, {t: abs(stability_function(n, 1j*y_im)) for t, _, n in esquemas})
fig2.savefig(os.path.join(salida, "eje_imaginario.png"), dpi=220)
fig2.savefig(os.path.join(salida, "eje_imaginario.pdf"))

with open(os.path.join(salida, "regiones_numericas.json"), "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2)
print(json.dumps(resultados["rigid_body_default"], indent=2))
