"""Estimación de error y orden de convergencia."""


def richardson_error(coarse_solution, fine_solution, order):
    """Estima el error mediante soluciones con pasos relacionados.

    TODO: documentar la razón entre pasos y alinear las mallas temporales.
    """
    raise NotImplementedError


def convergence_order(step_sizes, errors):
    """Estima el orden observado a partir de varios pasos y errores.

    TODO: ajustar la pendiente en escala logarítmica.
    """
    raise NotImplementedError
