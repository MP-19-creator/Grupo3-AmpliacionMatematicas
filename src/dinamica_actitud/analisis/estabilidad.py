"""Funciones y regiones de estabilidad absoluta."""


def stability_function(method, z):
    """Evalúa R(z) del método temporal indicado.

    TODO: definir las funciones de Euler, Euler inverso, Leap–Frog,
    Crank–Nicolson y RK4, incluyendo la representación de Leap–Frog.
    """
    raise NotImplementedError


def is_absolutely_stable(method, z):
    """Indica si el método satisface |R(z)| <= 1.

    TODO: contemplar con cuidado la estabilidad neutral en la frontera.
    """
    raise NotImplementedError
