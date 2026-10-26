from active.gui_reactive.gui import build_gui
from active.numerical_engine.Temporal_Schemes import Euler, RK4, Crank_Nicolson, Euler_implicit
from active.space_physics.eje_intermedio import PEI1
from active.numerical_engine.Cauchy_Problem import Cauchy_problem
from active.numerical_engine.Errores_Convergencia import partition
import matplotlib.pyplot as plt

if __name__ == "__main__":
    gui = build_gui()
    plt.show()