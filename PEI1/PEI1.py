"""
PEI 1 · Teorema del eje intermedio.  Lanza la GUI de cuatro paginas.
Ejecutar desde la raiz del repositorio:   python PEI1/PEI1.py      (o Ctrl+F5 en VS Code)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from active.gui_reactive.gui import build_gui

if __name__ == "__main__":
    gui = build_gui()
    try:                                                      # abrir maximizada (TkAgg / Qt)
        manager = plt.get_current_fig_manager()
        if hasattr(manager, "window") and hasattr(manager.window, "state"):
            manager.window.state("zoomed")
        elif hasattr(manager, "window") and hasattr(manager.window, "showMaximized"):
            manager.window.showMaximized()
    except Exception:
        pass
    plt.show()