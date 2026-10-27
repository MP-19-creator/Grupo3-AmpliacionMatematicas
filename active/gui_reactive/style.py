"""
Estilo de presentacion comun a todas las paginas de la GUI: tema oscuro, paleta y pequenas ayudas de dibujo.
Los colores de los ejes del cuerpo (e1 rojo, e2 verde, e3 azul) y de los esquemas son los mismos en todas las paginas.
"""
import sys
import matplotlib.pyplot as plt
from matplotlib import font_manager

C = dict(bg="#0B1220", panel="#121B2E", line="#24324D", text="#E8EEF7", muted="#8B9BB8",
         accent="#5AA9FF", gold="#D4A246", e=("#FF6B5A", "#3DDC84", "#5AA9FF"),
         energy="#5AA9FF", momentum="#FFB347", polhode="#F4F7FB", separatrix="#FF4D6D", point="#FF4FD8",
         ok="#3DDC84", bad="#FF4D6D", warn="#FFC145")

# Un color por esquema (el mismo en invariantes, estabilidad y Richardson)
scheme_colors = { "Euler": "#FF8A5B", "Crank-Nicolson": "#4FD1C5", "RK4": "#F4F7FB" }


def _font(candidates):
    available = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in candidates if c in available), "DejaVu Sans")


def Presentation_style():
    """ Tema oscuro y teclas libres para los atajos (se quitan los atajos de matplotlib que chocan) """
    plt.rcParams.update({
        "toolbar": "None",
        "font.family": _font(["Segoe UI", "Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]),
        "mathtext.fontset": "stixsans",
        "figure.facecolor": C["bg"], "axes.facecolor": C["panel"], "savefig.facecolor": C["bg"],
        "axes.edgecolor": C["line"], "axes.labelcolor": C["muted"], "text.color": C["text"],
        "xtick.color": C["muted"], "ytick.color": C["muted"], "axes.titlecolor": C["muted"],
        "grid.color": C["line"], "grid.alpha": 0.7, "grid.linewidth": 0.6,
        "keymap.back": [], "keymap.forward": [], "keymap.home": ["h", "home"], "keymap.pan": [],
        "keymap.zoom": [], "keymap.grid": [], "keymap.grid_minor": [], "keymap.xscale": [],
        "keymap.yscale": [], "keymap.quit": ["ctrl+w", "cmd+w"], "keymap.save": ["ctrl+s"] })


def Panel(ax, title=None, xlabel=None, ylabel=None):
    """ Ejes 2D con el aspecto de la presentacion """
    ax.set_facecolor(C["panel"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.grid(True, which="major")
    if title:
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=C["muted"], pad=8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    return ax


def Legend(ax, ncol=1, loc="lower right", fontsize=9):
    return ax.legend(loc=loc, fontsize=fontsize, ncol=ncol, facecolor=C["panel"], edgecolor=C["line"],
                     labelcolor=C["text"], framealpha=0.92)


def Debugger_attached():
    """ True si se ejecuta bajo un depurador (VS Code con F5 carga debugpy/pydevd): la animacion va mas lenta """
    return sys.gettrace() is not None or any(m in sys.modules for m in ("pydevd", "debugpy"))