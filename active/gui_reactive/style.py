"""
Estilo de presentacion comun a todas las paginas de la GUI: tema claro, paleta y pequenas ayudas de dibujo.
Los colores de los ejes del cuerpo (e1 cobre, e2 verde petróleo, e3 violeta) y de los esquemas son los mismos en todas las paginas.
"""
import sys
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ÓRBITA / cuaderno de dinámica: papel cálido, tinta violeta y cobre.
C = dict(bg="#F4F1E9", panel="#FFFDF7", line="#DCD6CB", text="#292538", muted="#736D7C",
         accent="#6544BC", gold="#D77C48", e=("#C85B37", "#298579", "#7252BC"),
         energy="#7252BC", momentum="#C98A30", polhode="#373044", separatrix="#C54F67", point="#16877C",
         ok="#398575", bad="#BD4F52", warn="#A96120", soft="#EBE4F8", ink="#302744")

# Colores consistentes y legibles sobre papel en las cuatro vistas.
scheme_colors = {"Euler": "#C85B37", "Crank-Nicolson": "#218579", "RK4": "#6544BC"}



def _font(candidates):
    available = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in candidates if c in available), "DejaVu Sans")


def Presentation_style():
    """ Tema claro y teclas libres para los atajos (se quitan los atajos de matplotlib que chocan) """
    plt.rcParams.update({
        "toolbar": "None",
        "font.family": _font(["Segoe UI", "Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]),
        "mathtext.fontset": "stixsans",
        "figure.facecolor": C["bg"], "axes.facecolor": C["panel"], "savefig.facecolor": C["bg"],
        "axes.edgecolor": C["line"], "axes.labelcolor": C["muted"], "text.color": C["text"],
        "xtick.color": C["muted"], "ytick.color": C["muted"], "axes.titlecolor": C["muted"],
        "grid.color": C["line"], "grid.alpha": 0.55, "grid.linewidth": 0.6, "grid.linestyle": ":",
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
