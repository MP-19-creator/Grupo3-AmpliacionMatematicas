import matplotlib.pyplot as plt
from numpy import linspace, meshgrid
from active.numerical_engine.Estabilidad import stability_function

schemes = ["Euler", "Inverse_Euler", "Crank_Nicolson", "RK4", "Leap_Frog"]
for method in schemes:
    X, Y = meshgrid(linspace(-4, 2, 400), linspace(-3.5, 3.5, 400))
    plt.contourf(X, Y, abs(stability_function(method, X + 1j*Y)), levels=[0, 1])
    plt.title(f"Region de estabilidad de {method}")
    plt.axis("equal")
    plt.xlabel("Re(z)")
    plt.ylabel("Im(z)")
    plt.colorbar(label="|R(z)|")
    plt.show()