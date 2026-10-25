import matplotlib.pyplot as plt
from numpy import linspace, meshgrid
from active.numerical_engine.Estabilidad import stability_function

schemes = ["Euler", "Inverse_Euler", "Leap_Frog", "Crank_Nicolson", "RK4"]
for method in schemes:
    X, Y = meshgrid(linspace(-5, 3.5, 400), linspace(-3.5, 3.5, 400))
    # Revisable pero no sé cómo dibujarlo si no
    if method == "Leap_Frog":
        plt.plot([-6, 4], [0,0], 'k--', linewidth=0.5)
        plt.plot([0,0], [-3.5, 3.5], 'k--', linewidth=0.5)
        plt.plot([0,0], [-1,1], 'b',linewidth=4)
        plt.title(f"Region de estabilidad de {method}")
        plt.axis("equal")
        plt.xlim(-4, 3); plt.ylim(-3.5, 3.5)
        plt.xlabel("Re(z)")
        plt.ylabel("Im(z)")
        plt.grid(True, alpha=0.2)
        plt.show()
    else:
        plt.plot([-6, 4], [0,0], 'k--', linewidth=0.5)
        plt.plot([0,0], [-3.5, 3.5], 'k--', linewidth=0.5)
        plt.contourf(X, Y, abs(stability_function(method, X + 1j*Y)), levels=[0, 0.2, 0.4, 0.6, 0.8, 1])
        plt.title(f"Region de estabilidad de {method}")
        plt.axis("equal")
        plt.xlim(-4, 3); plt.ylim(-3.5, 3.5)
        plt.xlabel("Re(z)")
        plt.ylabel("Im(z)")
        plt.colorbar(label="|R(z)|")
        plt.grid(True, alpha=0.2)
        plt.show()