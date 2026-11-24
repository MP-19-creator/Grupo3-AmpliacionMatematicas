"""Estilo comun de las figuras de la presentacion: Calibri y la paleta del deck (tinta, morado, gris)."""
from numpy import isfinite, linspace
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

INK, ACCENT, MUTED, LINE, PAPER, WARN = "#171717", "#6D28D9", "#6B7280", "#D1D5DB", "#FFFFFF", "#B91C1C"
SOFT = "#EDE9FE"

plt.rcParams.update({
    "font.family": "Calibri", "mathtext.fontset": "custom", "mathtext.it": "Calibri:italic",
    "mathtext.rm": "Calibri", "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "axes.spines.top": False, "axes.spines.right": False,
    "savefig.bbox": "tight", "savefig.facecolor": PAPER, "figure.facecolor": PAPER,
})


def region(ax, x, y, rho, exacta):
    """Relleno: region medida |U1| <= 1.  Linea: frontera |R(z)| = 1 de la formula.  Gris: el paso fallo."""
    estable = (rho <= 1).astype(float)
    estable[~isfinite(rho)] = float("nan")
    ax.contourf(x, y, estable, levels=[-.5, .5, 1.5], colors=[PAPER, SOFT])
    fallo = (~isfinite(rho)).astype(float)
    if fallo.any():
        ax.contourf(x, y, fallo, levels=[.5, 1.5], colors=[LINE])
    ax.contour(x, y, rho, levels=[1.], colors=[ACCENT], linewidths=2.2)
    ax.contour(x, y, exacta, levels=[1.], colors=[INK], linewidths=.9, linestyles="--")
    ax.axhline(0, color=MUTED, lw=.6)
    ax.axvline(0, color=MUTED, lw=.6)
    ax.set_aspect("equal")


def leyenda_regiones(fig):
    fig.legend(handles=[Patch(fc=SOFT, ec="none", label="measured: one real step gives |U₁| ≤ 1"),
                        Line2D([], [], color=ACCENT, lw=2.2, label="measured boundary"),
                        Line2D([], [], color=INK, lw=.9, ls="--", label="formula |R(z)| = 1"),
                        Patch(fc=LINE, ec="none", label="step failed (Newton)")],
               loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, -.06))


def eje_imaginario(ax, y, curvas):
    colores = {"Euler": WARN, "Implicit Euler": MUTED, "Crank-Nicolson": INK, "RK4": ACCENT}
    for nombre, valores in curvas.items():
        ax.plot(y, valores, color=colores[nombre], lw=2 if nombre in ("RK4", "Euler") else 1.4, label=nombre)
    ax.axhline(1, color=MUTED, lw=.6)
    ax.axvline(2*2**.5, color=ACCENT, lw=.8, ls=":")
    ax.text(2*2**.5, 1.55, "  y = 2√2", color=ACCENT, va="center")
    ax.set_ylim(.4, 1.8)
    ax.set_xlabel(r"$y$   (pure rotation mode, $z = i\,y = i\,\sigma\Delta t$)")
    ax.set_ylabel(r"$|R(iy)|$ per step")
    ax.legend(frameon=False, loc="upper left")
