"""PEI 1: elegir la fisica, ejecutar los calculos y entregar datos a la GUI.

Ejecutar desde la raiz: python PEI1/PEI1.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from active.gui_reactive.gui import crear_interfaz
import time
from numpy import array, argmin, arange, errstate, interp, linspace, ceil, sqrt, log, abs, exp, prod, searchsorted, isfinite, eye
from numpy.linalg import norm, solve, LinAlgError
from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Cauchy_problem_adaptive, Integration_stopped
from active.numerical_engine.temporal_schemes import Euler, Crank_Nicolson, RK4
from active.space_physics.eje_intermedio import Rigid_body_problem, Initial_condition, Is_physical, Rotation_matrix
from active.space_physics.eje_intermedio import (Kinetic_energy_2T, Angular_momentum_L2, Energy_ellipsoid, Momentum_ellipsoid,
    Separatrix, Polhode_period, Linear_eigenvalues, Box_dimensions,
    Jacobian_eigenvalues, Kinematic_eigenvalues)
from active.numerical_engine.Estabilidad import stability_region, stability_function
from active.numerical_engine.Errores_Convergencia import curva_convergencia, tramo_recto, ordenes_locales

from inspect import signature
from active.numerical_engine.NewtonRaphson import Newton, Newton_failed


def iniciar_programa(animar=True):
    """El principal conecta las tres partes. Ninguna se importa desde la GUI."""
    resultados_actuales = {}

    def calcular_simulacion(parametros):
        # La GUI entrega números y el nombre del método, nunca un esquema.
        parametros = dict(parametros, metodo=metodos[parametros['nombre_metodo']])
        resultado = calcular_trayectoria(parametros)
        resultados_actuales.clear()
        resultados_actuales.update(parametros)
        resultados_actuales.update(resultado)
        # Devolver datos; la función del esquema se queda en el principal.
        datos = {clave: valor for clave, valor in resultados_actuales.items() if clave != 'metodo'}
        datos['orden'] = parametros['metodo'].order
        return datos

    def preparar_pagina(numero_pagina, tf_estudio):
        if numero_pagina in (1, 2):
            if 'comparacion_metodos' not in resultados_actuales:
                resultados_actuales['comparacion_metodos'] = comparar_metodos(resultados_actuales)
            if numero_pagina == 1:
                return dict(comparacion_metodos=resultados_actuales['comparacion_metodos'])
            return dict(estabilidad=preparar_datos_estabilidad(resultados_actuales, resultados_actuales['comparacion_metodos']))
        if numero_pagina == 3:
            return dict(estudio_error=calcular_estudio_error(resultados_actuales, tf_estudio))
        return {}

    interfaz = crear_interfaz(list(metodos), calcular_simulacion, preparar_pagina, animar=animar)
    # Aquí se inicia el primer cálculo, una vez construida la ventana.
    interfaz['solicitar_calculo']()
    return interfaz


class Esquema_temporal:
    """Guarda la funcion de un metodo y su orden para el paso adaptativo."""
    def __init__(self, funcion, orden):
        # El motor adaptativo necesita que el atributo se llame order.
        self.funcion, self.order = funcion, orden
        self.__name__ = funcion.__name__

    def __call__(self, U, dt, t, F):
        return self.funcion(U, dt, t, F)


def paso_crank_nicolson(U, dt, t, F):
    """Paso de Crank-Nicolson compatible con el Newton existente (F, U0).

    Mantiene la regla del trapecio y el Jacobiano exacto sin alterar el motor.
    Los fallos son ArithmeticError, como espera Cauchy_problem.
    """
    A = U + dt / 2 * F(U, t)
    X = Euler(U, dt, t, F)
    for _ in range(25):
        residuo = X - A - dt / 2 * F(X, t + dt)
        if not isfinite(residuo).all():
            raise Newton_failed("Residuo no finito")
        if norm(residuo) <= 1e-10:
            return X
        try:
            X = X - solve(eye(len(U)) - dt / 2 * F.jacobian(X, t + dt), residuo)
        except LinAlgError as exc:
            raise Newton_failed("Jacobiana singular") from exc
    raise Newton_failed("Limite de iteraciones de Newton")


paso_crank_nicolson.__name__ = "Crank_Nicolson"
metodo_CN = Crank_Nicolson if len(signature(Newton).parameters) >= 3 else paso_crank_nicolson
metodos = {"Euler": Esquema_temporal(Euler, 1), "Crank-Nicolson": Esquema_temporal(metodo_CN, 2), "RK4": Esquema_temporal(RK4, 4)}

metodos_implicitos = (metodos["Crank-Nicolson"],)
limite_pasos = {'rapido': 100000, 'lento': 30000}
max_muestras_animacion = 4000
max_puntos_curva = 2000


def instantes_cambio_signo(t, x):
    """ Instantes en que x cambia de signo (interpolacion lineal entre nodos) """
    i = ((x[1:] * x[:-1]) < 0).nonzero()[0]
    return t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])


def calcular_derivas(U, I):
    """ Derivas relativas |2T/2T0 - 1|, |L^2/L0^2 - 1| y ||q| - 1| a lo largo de una trayectoria U[n, :] """
    dT = abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(U[0], I) - 1)
    dL = abs(Angular_momentum_L2(U, I) / Angular_momentum_L2(U[0], I) - 1)
    dq = abs(sqrt((U[:, 3:7]**2).sum(axis=1)) - 1)
    return dT, dL, dq


def integrar_trayectoria(F, tf, U0, metodo, dt, adaptativo=False, tol=1e-8):
    """
    Cauchy_problem (o el adaptativo) protegido: si el esquema explota o Newton falla devuelve lo calculado
    y una nota. Paso fijo: conserva dt y acorta el horizonte si alcanza el limite de pasos.
    """
    aviso = ""
    try:
        with errstate(over="ignore", invalid="ignore"):
            if adaptativo:
                t, U = Cauchy_problem_adaptive(F, tf, U0, metodo, tol=tol, dt0=dt,
                                               max_steps=limite_pasos['lento' if metodo in metodos_implicitos else 'rapido'])
            else:
                N = max(1, int(ceil(tf / dt)))
                max_pasos = limite_pasos['lento' if metodo in metodos_implicitos else 'rapido']
                if N > max_pasos:
                    N = max_pasos
                    aviso = f"Límite de {max_pasos:,} pasos: t = {N*dt:g} s (Δt = {dt:g})"
                t = arange(N + 1, dtype=float) * dt
                t[-1] = min(t[-1], tf)
                U = Cauchy_problem(F, t, U0, metodo)
    except Integration_stopped as e:
        U, t = e.U_partial, e.t_partial
        aviso = (f"Limite de pasos en t = {t[-1]:.1f}" if "steps" in str(e) else f"Integracion detenida en t = {t[-1]:.1f}")
    with errstate(over="ignore", invalid="ignore"):
        acotada = norm(U, axis=1) < 1e6 * norm(U0)        # cortar donde |U| crece 1e6 veces
    if not acotada.all():
        indice_final = max(1, int(argmin(acotada)))
        U, t = U[:indice_final], t[:indice_final]
        aviso = f"Divergencia cerca de t = {t[-1]:.3g} s"
    return t, U, aviso


def calcular_trayectoria(parametros):
    """Integra el problema y prepara las muestras que necesitan las gráficas."""
    inicio_calculo = time.perf_counter()
    I = parametros["I"]
    if not I[0] < I[1] < I[2]:
        raise ValueError("Se requiere I₁ < I₂ < I₃ · se conserva el último resultado válido")
    # Preparar la fisica antes de llamar a los calculos.
    F = Rigid_body_problem(I)
    U0 = Initial_condition(parametros['eje'], parametros["Omega"], parametros["eps"])
    tn, Un, aviso = integrar_trayectoria(
        F, parametros["tf"], U0, parametros['metodo'], parametros["dt"],
        parametros['adaptativo'], parametros["tol"])
    if len(tn) < 2:
        raise ValueError("La solución diverge al empezar. Aumenta la precisión del paso.")
    if parametros['adaptativo']:
        t = linspace(tn[0], tn[-1], max_muestras_animacion)
        U = array([interp(t, tn, Un[:, j]) for j in range(Un.shape[1])]).T
    else:
        indices = linspace(0, len(tn)-1, min(len(tn), max_muestras_animacion), dtype=int)
        t, U = tn[indices], Un[indices]
    salto_dibujo = max(1, (len(t) + max_puntos_curva - 1) // max_puntos_curva)
    indices_dibujo = arange(0, len(t), salto_dibujo)
    if indices_dibujo[-1] != len(t) - 1:
        indices_dibujo = array([*indices_dibujo, len(t) - 1])
    # Preparar las puntas de los ejes para dibujar la estela durante la animación.
    puntas_eje = array([0.78 * Rotation_matrix(q)[:, parametros['eje']] for q in U[:, 3:7]])
    avisos = ([f"{parametros['nombre_metodo']}: {aviso}"] if aviso else [])
    if not Is_physical(I):
        avisos.append("I1 + I2 < I3: inercias no fisicas")
    movimiento = preparar_datos_movimiento(I, U, parametros['eje'])
    return dict(solucion_completa=(tn, Un), t=t, U=U, tiempo_calculo=time.perf_counter()-inicio_calculo, avisos=avisos, movimiento=movimiento,
                aviso=aviso, indice_actual=0, tiempo_actual=0.0, indices_dibujo=indices_dibujo, puntas_estela=puntas_eje,
                instantes_volteo=instantes_cambio_signo(tn, Un[:, parametros['eje']]), ventana_estela=min(15., .2*t[-1]),
                dt_utilizado=tn[1]-tn[0], derivas=[v.max() for v in calcular_derivas(Un, I)])


def preparar_datos_movimiento(I, U, eje):
    """Datos físicos que la página de movimiento solo tendrá que dibujar."""
    T2 = Kinetic_energy_2T(U[0], I)
    L2 = Angular_momentum_L2(U[0], I)
    rotaciones = array([Rotation_matrix(q) for q in U[:, 3:7]])
    momento_angular = rotaciones[0] @ (array(I) * U[0, :3])
    return dict(radio=sqrt(T2/I[0])*1.05,
                elipsoide_energia=Energy_ellipsoid(I, T2, 36),
                elipsoide_momento=Momentum_ellipsoid(I, L2, 36),
                separatriz=Separatrix(I, T2), dimensiones=Box_dimensions(I),
                rotaciones=rotaciones, vector_momento=.82*momento_angular/norm(momento_angular),
                autovalor=Linear_eigenvalues(I, eje, U[0, eje])[0],
                periodo=Polhode_period(I, T2, L2))


def comparar_metodos(parametros):
    comparacion_metodos = {}
    U0 = Initial_condition(parametros['eje'], parametros["Omega"], parametros["eps"])
    for nombre_metodo, metodo in metodos.items():
        if metodo is parametros['metodo']:
            t, U = parametros['solucion_completa']
            aviso = parametros['aviso']
        else:
            t, U, aviso = integrar_trayectoria(Rigid_body_problem(parametros["I"]), parametros["tf"], U0, metodo,
                                   parametros["dt"],
                                   parametros['adaptativo'], parametros["tol"])
        comparacion_metodos[nombre_metodo] = dict(t=t, U=U, aviso=aviso, derivas=calcular_derivas(U, parametros["I"]))
    return comparacion_metodos


def calcular_estudio_error(parametros, tf):
    inicio_calculo = time.perf_counter()
    curvas_convergencia = calcular_convergencia(parametros, tf)
    for curva in curvas_convergencia.values():
        with errstate(invalid="ignore", divide="ignore"):
            curva['ordenes'] = ordenes_locales(curva["D"])
    return dict(curvas_convergencia=curvas_convergencia, errores=estimar_error_richardson(parametros, tf), tf=tf,
                tiempo_calculo=time.perf_counter()-inicio_calculo)


def preparar_datos_estabilidad(datos, comparacion_metodos):
    """Regiones, autovalores y predicciones: la GUI recibe únicamente datos."""
    nombres_estabilidad = {"Euler": "Euler", "Crank-Nicolson": "Crank_Nicolson", "RK4": "RK4"}
    dt = datos['dt_utilizado']
    z_w = Linear_eigenvalues(datos["I"], datos['eje'], datos["Omega"]) * dt
    z_q = Kinematic_eigenvalues(datos["U"][0]) * dt
    radio = 1.6 * max(abs(z_w).max(), abs(z_q).max(), 1e-3)
    regiones_completas, regiones_ampliadas, curvas_eje_imaginario = {}, {}, {}
    y = linspace(0, 3.2, 400)
    for etiqueta, nombre_metodo in nombres_estabilidad.items():
        regiones_completas[etiqueta] = stability_region(nombre_metodo, linspace(-3.4, 1.4, 260), linspace(-3.2, 3.2, 300))
        regiones_ampliadas[etiqueta] = stability_region(nombre_metodo, linspace(-radio, radio, 241), linspace(-radio, radio, 241))
        curvas_eje_imaginario[etiqueta] = abs(stability_function(nombre_metodo, 1j*y))
    X, Y, A = regiones_ampliadas[datos['nombre_metodo']]
    with errstate(divide="ignore", invalid="ignore"):
        color_ampliacion = log(A) - X
    tn = datos['solucion_completa'][0]
    autovalores_por_instante = []
    for t, U in zip(datos["t"], datos["U"]):
        h = dt
        if datos['adaptativo']:
            i = min(max(int(searchsorted(tn, t)), 1), len(tn)-1)
            h = tn[i] - tn[i-1]
        autovalores_por_instante.append(Jacobian_eigenvalues(datos["I"], U) * h)
    nombres_cortos = {"Euler": "Euler", "Crank-Nicolson": "CN", "RK4": "RK4"}
    tipo_autovalor = "real: inestable" if abs(z_w[0].imag) < 1e-14 else "imaginario: centro"
    filas_tabla = ["1) ω mode at the equilibrium, ONE step", f"   z = {z_w[0]:.4g}   ({tipo_autovalor})",
            f"  {'':<6}{'|R(z)|':>13}{'exacto |e^z|':>13}"]
    for etiqueta, nombre_metodo in nombres_estabilidad.items():
        marca = "▶ " if etiqueta == datos['nombre_metodo'] else "  "
        filas_tabla.append(f"{marca}{nombres_cortos[etiqueta]:<6}{abs(stability_function(nombre_metodo, z_w[0])):13.8f}{abs(exp(z_w[0])):13.8f}")
    filas_tabla += ["", "2) Cuaternion: |q(t_f)| - 1   (exacto: 0)", "   z = ±i|ω|Δt/2 en cada paso",
             f"  {'':<6}{'prod |R(z_n)|':>13}{'simulado':>13}"]
    for etiqueta, nombre_metodo in nombres_estabilidad.items():
        t, U = comparacion_metodos[etiqueta]["t"], comparacion_metodos[etiqueta]["U"]
        if len(t) < 2:
            continue
        w = norm(U[:-1, :3], axis=1)
        factores = abs(stability_function(nombre_metodo, .5j*w*(t[1:]-t[:-1])))
        marca = "▶ " if etiqueta == datos['nombre_metodo'] else "  "
        filas_tabla.append(f"{marca}{nombres_cortos[etiqueta]:<6}{prod(factores)-1:13.3e}{norm(U[-1, 3:7])-1:13.3e}")
    return dict(autovalores_iniciales=(z_w, z_q), radio=radio, regiones_completas=regiones_completas,
                regiones_ampliadas=regiones_ampliadas, color_ampliacion=(X, Y, color_ampliacion),
                eje_imaginario=y, curvas_eje_imaginario=curvas_eje_imaginario,
                autovalores_por_instante=array(autovalores_por_instante), tabla="\n".join(filas_tabla))



def calcular_convergencia(parametros, tf):
    """ Curva de convergencia de los tres esquemas para el problema y la condicion inicial actuales """
    datos = parametros
    F = Rigid_body_problem(datos["I"])
    U0 = Initial_condition(datos['eje'], datos["Omega"], datos["eps"])
    resultado = {}
    for nombre_metodo, metodo in metodos.items():
        N, D = curva_convergencia(F, tf, U0, metodo, N0=40, niveles={"Euler": 11, "Crank-Nicolson": 8, "RK4": 8}[nombre_metodo])
        indices_ajuste, pendiente, b = tramo_recto(N, D)
        resultado[nombre_metodo] = dict(N=N, D=D, indices_ajuste=indices_ajuste, pendiente=pendiente, b=b)
    return resultado

def estimar_error_richardson(parametros, tf):
    """ Error de Richardson (con N y 2N) frente al error verdadero (RK4 con 8N pasos) en [0, t_f del estudio] """
    datos = parametros
    metodo, q = datos['metodo'], datos['metodo'].order
    N = int(min(max(round(tf / datos["dt"]), 20), 2000))
    F = Rigid_body_problem(datos["I"])
    U0 = Initial_condition(datos['eje'], datos["Omega"], datos["eps"])
    t = linspace(0, tf, N + 1)
    try:
        U1 = Cauchy_problem(F, t, U0, metodo)
        U2 = Cauchy_problem(F, linspace(0, tf, 2*N + 1), U0, metodo)
        Ur = Cauchy_problem(F, linspace(0, tf, 8*N + 1), U0, RK4)
    except ArithmeticError:
        return t, None, None, N
    error_estimado = norm(U1 - U2[::2], axis=1) / (1 - 2.**-q)
    error_referencia = norm(U1 - Ur[::8], axis=1)
    return t, error_estimado, error_referencia, N



if __name__ == "__main__":
    # 1. Crear los controles, calcular la trayectoria inicial y dibujarla.
    interfaz = iniciar_programa()
    try:                                                      # abrir maximizada (TkAgg / Qt)
        gestor_ventana = plt.get_current_fig_manager()
        if hasattr(gestor_ventana, "window") and hasattr(gestor_ventana.window, "state"):
            gestor_ventana.window.state("zoomed")
        elif hasattr(gestor_ventana, "window") and hasattr(gestor_ventana.window, "showMaximized"):
            gestor_ventana.window.showMaximized()
    except Exception:
        pass
    # 2. Entrar en el bucle de eventos de Matplotlib.
    # Desde aquí, los clics y el temporizador llaman a las funciones conectadas.
    plt.show()
