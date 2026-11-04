import sys
import os
import time
from inspect import signature
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from numpy import (array, arcsin, clip, cos, diff, einsum, errstate, exp, eye, isfinite, linspace, log, nan, pi, prod,
    searchsorted, sin, sqrt, ceil, arange, argmin, interp, unwrap, angle)
from numpy.linalg import norm, solve, LinAlgError
from active.gui_reactive.gui_web import crear_interfaz_web
from active.numerical_engine.temporal_schemes import Euler, Euler_implicit, RK4, Crank_Nicolson
from active.numerical_engine.NewtonRaphson import Newton, Newton_failed
from active.numerical_engine.Estabilidad import stability_region, stability_function
from active.numerical_engine.Errores_Convergencia import curva_convergencia, tramo_recto, ordenes_locales
from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Cauchy_problem_adaptive, Integration_stopped
from active.space_physics.eje_intermedio import (Rigid_body_problem, Rotation_matrix, Kinetic_energy_2T, Jacobian_eigenvalues,
    Angular_momentum_L2, Inertial_angular_momentum, Energy_ellipsoid, Momentum_ellipsoid, Separatrix,
    Polhode_period, Initial_condition, Is_physical, Box_dimensions, Side_of_separatrix, Linear_eigenvalues, Kinematic_eigenvalues)

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

max_muestras_animacion = 4000
max_puntos_curva = 2000

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
    fin_integracion = time.perf_counter()
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
    avisos = ([f"{parametros['nombre_metodo']}: {aviso}"] if aviso else [])
    if not Is_physical(I):
        avisos.append("I1 + I2 < I3: inercias no fisicas")
    movimiento = preparar_datos_movimiento(I, U, parametros['eje'])
    puntas_eje = .78 * movimiento['rotaciones'][:, :, parametros['eje']]
    volteos = instantes_cambio_signo(tn, Un[:, parametros['eje']])
    derivas = [v.max() for v in calcular_derivas(Un, I)]
    return dict(solucion_completa=(tn, Un), t=t, U=U, tiempo_calculo=time.perf_counter()-inicio_calculo,
                tiempo_integracion=fin_integracion-inicio_calculo, tiempo_preparacion=time.perf_counter()-fin_integracion,
                avisos=avisos, movimiento=movimiento,
                aviso=aviso, indice_actual=0, tiempo_actual=0.0, indices_dibujo=indices_dibujo, puntas_estela=puntas_eje,
                instantes_volteo=volteos, ventana_estela=min(15., .2*t[-1]),
                dt_utilizado=tn[1]-tn[0], derivas=derivas)

def instantes_cambio_signo(t, x):
    """ Instantes en que x cambia de signo (interpolacion lineal entre nodos) """
    i = ((x[1:] * x[:-1]) < 0).nonzero()[0]
    return t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])

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
                lado_separatriz=Side_of_separatrix(I, T2, L2), casimir=L2-I[1]*T2,
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

def preparar_apoyo_comparacion(datos, comparacion):
    """Medidas y muestras para la defensa; no modifica las soluciones comparadas."""
    I, eje = datos['I'], datos['eje']
    transversales = [j for j in range(3) if j != eje]
    # Referencia auxiliar con el RK4 y los límites de pasos existentes.
    # Si se trunca, la GUI no extrapola sus muestras al resto del intervalo.
    tr, Ur, aviso = integrar_trayectoria(Rigid_body_problem(I), datos['tf'],
        Initial_condition(eje, datos['Omega'], datos['eps']), metodos['RK4'], datos['dt']/4)
    series = dict(comparacion)
    series['Referencia RK4'] = dict(t=tr, U=Ur, aviso=aviso)
    curvas = {}
    for nombre, resultado in series.items():
        t, U = resultado['t'], resultado['U']
        energia = Kinetic_energy_2T(U, I)
        momento = Angular_momentum_L2(U, I)
        derivas_signo = (energia/energia[0]-1, momento/momento[0]-1,
                         norm(U[:, 3:7], axis=1)-1)
        j, k = transversales
        x = U[:, j]
        cruces = ((x[:-1] < 0) & (x[1:] >= 0)).nonzero()[0]
        tc = t[cruces] - x[cruces]*(t[cruces+1]-t[cruces])/(x[cruces+1]-x[cruces])
        periodo = float((tc[-1]-tc[0])/(len(tc)-1)) if len(tc) >= 2 else float('nan')
        indices = linspace(0, len(t)-1, min(len(t), max_puntos_curva), dtype=int)
        curvas[nombre] = dict(t=t[indices], transversal=U[indices][:, transversales],
            amplitud=norm(U[indices][:, transversales], axis=1),
            derivas_signo=tuple(d[indices] for d in derivas_signo),
            periodo=periodo, aviso=resultado['aviso'],
            # Marcadores sincronizados con el reloj de la trayectoria principal.
            marcadores=array([interp(datos['t'], t, U[:, c]) for c in transversales]).T,
            fin=t[-1])
    lam = datos['movimiento']['autovalor']
    t = datos['t']
    inicial = norm(datos['solucion_completa'][1][0, transversales])
    guia_t, guia = array([]), array([])
    if lam.real > 0 and inicial > 0:
        # Guía proporcional, no solución exacta. Mostrar solo cerca del giro puro.
        limite = log(.1*datos['Omega']/inicial)/lam.real
        guia_t = t[t <= max(0., limite)]
        guia = inicial*exp(lam.real*guia_t)
    return dict(curvas=curvas, transversales=transversales,
        periodo_teorico=datos['movimiento']['periodo'], guia_crecimiento=(guia_t, guia),
        referencia='RK4 · Δt/4 · aproximada', referencia_aviso=aviso,
        referencia_completa=(tr, Ur))

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
    filas_tabla = [f"Equilibrio · z = {z_w[0]:.3g}",
            f"  {'':<6}{'|R(z)|':>11}{'|exp(z)|':>11}"]
    for etiqueta, nombre_metodo in nombres_estabilidad.items():
        marca = "▶ " if etiqueta == datos['nombre_metodo'] else "  "
        filas_tabla.append(f"{marca}{nombres_cortos[etiqueta]:<6}{abs(stability_function(nombre_metodo, z_w[0])):11.6f}{abs(exp(z_w[0])):11.6f}")
    filas_tabla += ["", "Cuaternión · |q(tf)| − 1",
             f"  {'':<6}{'Predicción':>11}{'Simulación':>11}"]
    for etiqueta, nombre_metodo in nombres_estabilidad.items():
        t, U = comparacion_metodos[etiqueta]["t"], comparacion_metodos[etiqueta]["U"]
        if len(t) < 2:
            continue
        w = norm(U[:-1, :3], axis=1)
        factores = abs(stability_function(nombre_metodo, .5j*w*(t[1:]-t[:-1])))
        marca = "▶ " if etiqueta == datos['nombre_metodo'] else "  "
        filas_tabla.append(f"{marca}{nombres_cortos[etiqueta]:<6}{prod(factores)-1:11.3e}{norm(U[-1, 3:7])-1:11.3e}")
    # Modo oscilatorio test: ilustra disipación y dispersión sin integrar de nuevo
    # el satélite, ni incorporar un integrador distinto a su simulación.
    n = arange(25)
    ys = linspace(0, 2.8, 240)
    demostracion = {}
    for etiqueta, nombre in {**nombres_estabilidad, 'Euler implícito': 'Euler_implicit'}.items():
        r = stability_function(nombre, .3j)
        demostracion[etiqueta] = dict(orbita=r**n,
            ganancia=abs(stability_function(nombre, 1j*ys)),
            fase=unwrap(angle(stability_function(nombre, 1j*ys)))-ys)
    return dict(autovalores_iniciales=(z_w, z_q), radio=radio, regiones_completas=regiones_completas,
                regiones_ampliadas=regiones_ampliadas, color_ampliacion=(X, Y, color_ampliacion),
                eje_imaginario=y, curvas_eje_imaginario=curvas_eje_imaginario,
                autovalores_por_instante=array(autovalores_por_instante), tabla="\n".join(filas_tabla),
                demostracion=dict(n=n, y=.3, barrido=ys, curvas=demostracion, exacta=exp(.3j*n)))

def calcular_estudio_error(parametros, tf):
    inicio_calculo = time.perf_counter()
    curvas_convergencia = calcular_convergencia(parametros, tf)
    for curva in curvas_convergencia.values():
        with errstate(invalid="ignore", divide="ignore"):
            curva['ordenes'] = ordenes_locales(curva["D"])
    return dict(curvas_convergencia=curvas_convergencia, errores=estimar_error_richardson(parametros, tf), tf=tf,
                tiempo_calculo=time.perf_counter()-inicio_calculo)

def estimar_error_richardson(parametros, tf):
    """Error de Richardson frente a una referencia aproximada RK4 de 8N pasos."""
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

def paso_euler_implicito(U, dt, t, F):
    """Paso de Euler implícito con el Jacobiano exacto, igual que paso_crank_nicolson de PEI1.py.

    Resuelve G(X) = X − U − Δt F(X, t + Δt) = 0 con Newton desde el predictor de Euler explícito.
    Euler_implicit de temporal_schemes pasa el Jacobiano a Newton, que aún solo admite (F, U0):
    cuando NewtonRaphson.py lo acepte, metodo_EI pasa a ser Euler_implicit sin tocar nada aquí.
    """
    X = Euler(U, dt, t, F)
    for _ in range(25):
        residuo = X - U - dt * F(X, t + dt)
        if not isfinite(residuo).all():
            raise Newton_failed("Residuo no finito")
        if norm(residuo) <= 1e-10:
            return X
        try:
            X = X - solve(eye(len(U)) - dt * F.jacobian(X, t + dt), residuo)
        except LinAlgError as exc:
            raise Newton_failed("Jacobiana singular") from exc
    raise Newton_failed("Limite de iteraciones de Newton")


paso_euler_implicito.__name__ = "Euler_implicit"
metodo_EI = Euler_implicit if len(signature(Newton).parameters) >= 3 else paso_euler_implicito
# Los tres esquemas de PEI1.py más el Euler implícito, en el orden de los botones (RK4 al final: es el inicial).
metodos_web = {"Euler": metodos["Euler"], "Euler implícito": Esquema_temporal(metodo_EI, 1),
               "Crank-Nicolson": metodos["Crank-Nicolson"], "RK4": metodos["RK4"]}
metodos_extra = {nombre: metodo for nombre, metodo in metodos_web.items() if nombre not in metodos}
nombres_estabilidad_web = {"Euler": "Euler", "Euler implícito": "Euler_implicit", "Crank-Nicolson": "Crank_Nicolson", "RK4": "RK4"}
niveles_convergencia_web = {"Euler implícito": 8}             # como Crank-Nicolson: cada paso resuelve Newton
# Es implícito: el mismo límite de pasos que Crank-Nicolson. Solo cambia en este proceso; PEI1.py no se toca.
metodos_implicitos = (*metodos_implicitos, metodos_web["Euler implícito"])


def iniciar_programa_web():
    """Misma estructura que iniciar_programa() de PEI1.py; cambia solo la GUI que se crea."""
    resultados_actuales = {}
    parametros_actuales = None
    estudios_error = {}

    def calcular_simulacion(parametros):
        nonlocal parametros_actuales
        if parametros != parametros_actuales:
            resultado = calcular_trayectoria(dict(parametros, metodo=metodos_web[parametros['nombre_metodo']]))
            resultados_actuales.clear()
            resultados_actuales.update(parametros, metodo=metodos_web[parametros['nombre_metodo']])
            resultados_actuales.update(resultado)
            # Periodo de la polhoda sin cancelaciones: cerca de la separatriz la v1 lo da como infinito.
            resultados_actuales['movimiento'].update(periodo_polhoda_web(parametros['I'], resultado['U'][0, :3]))
            # Lo que solo dibuja la versión web, preparado con la física existente.
            resultados_actuales['web'] = preparar_datos_web(resultados_actuales)
            parametros_actuales = dict(parametros)
            estudios_error.clear()
        # La GUI entrega números y el nombre del método, nunca un esquema.
        datos = {clave: valor for clave, valor in resultados_actuales.items() if clave != 'metodo'}
        datos['orden'] = resultados_actuales['metodo'].order
        return datos

    def preparar_pagina(numero_pagina, tf_estudio):
        if numero_pagina in (0, 1, 2):
            if 'comparacion_metodos' not in resultados_actuales:
                resultados_actuales['comparacion_metodos'] = comparar_metodos_web(resultados_actuales)
            if numero_pagina == 0:
                # Página de movimiento: los tres integradores a la vez (solo web).
                if 'fantasmas' not in resultados_actuales:
                    resultados_actuales['fantasmas'] = preparar_fantasmas(
                        resultados_actuales, resultados_actuales['comparacion_metodos'])
                return dict(fantasmas=resultados_actuales['fantasmas'])
            if numero_pagina == 1:
                if 'apoyo_comparacion' not in resultados_actuales:
                    resultados_actuales['apoyo_comparacion'] = preparar_apoyo_comparacion(
                        resultados_actuales, resultados_actuales['comparacion_metodos'])
                return dict(comparacion_metodos=resultados_actuales['comparacion_metodos'],
                            apoyo_comparacion=resultados_actuales['apoyo_comparacion'])
            if 'estabilidad' not in resultados_actuales:
                resultados_actuales['estabilidad'] = preparar_datos_estabilidad_web(resultados_actuales, resultados_actuales['comparacion_metodos'])
            return dict(estabilidad=resultados_actuales['estabilidad'])
        if numero_pagina == 3:
            if tf_estudio not in estudios_error:
                estudios_error[tf_estudio] = calcular_estudio_error_web(resultados_actuales, tf_estudio)
            return dict(estudio_error=estudios_error[tf_estudio])
        return {}

    interfaz = crear_interfaz_web(list(metodos_web), calcular_simulacion, preparar_pagina)
    # La GUI avisa antes de calcular si el paso fijo superaría el límite de pasos de PEI1.py.
    interfaz['configuracion']['limite_pasos'] = {
        nombre: limite_pasos['lento' if metodo in metodos_implicitos else 'rapido'] for nombre, metodo in metodos_web.items()}
    # Orden teórico de cada esquema: la explicación de Richardson lo compara con el medido.
    interfaz['configuracion']['ordenes'] = {nombre: metodo.order for nombre, metodo in metodos_web.items()}
    # Aquí se inicia el primer cálculo, una vez construida la interfaz.
    interfaz['solicitar_calculo']()
    return interfaz


def comparar_metodos_web(datos):
    """comparar_metodos de PEI1.py (sus tres esquemas) más los de la web, con el mismo Δt o la misma tolerancia."""
    comparacion = comparar_metodos(datos)
    for nombre, metodo in metodos_extra.items():
        if metodo is datos['metodo']:
            (t, U), aviso = datos['solucion_completa'], datos['aviso']
        else:
            t, U, aviso = integrar_trayectoria(Rigid_body_problem(datos['I']), datos['tf'],
                Initial_condition(datos['eje'], datos['Omega'], datos['eps']), metodo, datos['dt'],
                datos['adaptativo'], datos['tol'])
        comparacion[nombre] = dict(t=t, U=U, aviso=aviso, derivas=calcular_derivas(U, datos['I']))
    return {nombre: comparacion[nombre] for nombre in metodos_web}


def preparar_datos_estabilidad_web(datos, comparacion):
    """preparar_datos_estabilidad de PEI1.py completado con los esquemas de la web.

    PEI1.py prepara los tres esquemas del enunciado y colorea la ampliación del elegido; si el elegido es
    uno de la web, se le pasa Euler y después se rehace ese mapa. La región completa de los esquemas de la
    web llega hasta Re z = 2.4: la del Euler implícito es el exterior del círculo |z − 1| = 1.
    """
    elegido = datos['nombre_metodo']
    estabilidad = preparar_datos_estabilidad(dict(datos, nombre_metodo=elegido if elegido in metodos else "Euler"), comparacion)
    radio = estabilidad['radio']
    for nombre in metodos_extra:
        esquema = nombres_estabilidad_web[nombre]
        estabilidad['regiones_completas'][nombre] = stability_region(esquema, linspace(-3.4, 2.4, 320), linspace(-3.2, 3.2, 300))
        estabilidad['regiones_ampliadas'][nombre] = stability_region(esquema, linspace(-radio, radio, 241), linspace(-radio, radio, 241))
    if elegido in metodos_extra:
        X, Y, A = estabilidad['regiones_ampliadas'][elegido]
        with errstate(divide="ignore", invalid="ignore"):
            estabilidad['color_ampliacion'] = (X, Y, log(A) - X)
    # La web ya no dibuja |R(iy)| y presenta la tabla de predicción como tabla, con los cuatro esquemas.
    for clave in ('tabla', 'eje_imaginario', 'curvas_eje_imaginario'):
        estabilidad.pop(clave, None)
    estabilidad['prediccion'] = preparar_tabla_prediccion(estabilidad['autovalores_iniciales'][0][0], comparacion)
    return estabilidad


def preparar_tabla_prediccion(z, comparacion):
    """Las cifras de la tabla de texto de preparar_datos_estabilidad, en filas y para los cuatro esquemas.

    En el equilibrio, |R(z)| frente a |e^z|. En el cuaternión, |q(tf)| − 1 predicho por la cinemática
    (cada paso multiplica |q| por |R(i|ω|Δt/2)|) frente al de la simulación.
    """
    filas = []
    for nombre, esquema in nombres_estabilidad_web.items():
        t, U = comparacion[nombre]['t'], comparacion[nombre]['U']
        fila = dict(nombre=nombre, R=abs(stability_function(esquema, z)), exacta=abs(exp(z)), prediccion=None, simulacion=None)
        if len(t) >= 2:
            w = norm(U[:-1, :3], axis=1)
            fila.update(prediccion=prod(abs(stability_function(esquema, .5j*w*(t[1:] - t[:-1])))) - 1,
                        simulacion=norm(U[-1, 3:7]) - 1)
        filas.append(fila)
    return dict(z=z, filas=filas)


def calcular_estudio_error_web(datos, tf):
    """calcular_estudio_error de PEI1.py más la curva de convergencia de los esquemas de la web."""
    inicio = time.perf_counter()
    estudio = calcular_estudio_error(datos, tf)
    F = Rigid_body_problem(datos['I'])
    U0 = Initial_condition(datos['eje'], datos['Omega'], datos['eps'])
    curvas = estudio['curvas_convergencia']
    for nombre, metodo in metodos_extra.items():
        N, D = curva_convergencia(F, tf, U0, metodo, N0=40, niveles=niveles_convergencia_web[nombre])
        indices_ajuste, pendiente, b = tramo_recto(N, D)
        with errstate(invalid="ignore", divide="ignore"):
            ordenes = ordenes_locales(D)
        curvas[nombre] = dict(N=N, D=D, indices_ajuste=indices_ajuste, pendiente=pendiente, b=b, ordenes=ordenes)
    estudio['curvas_convergencia'] = {nombre: curvas[nombre] for nombre in metodos_web}
    estudio['tiempo_calculo'] = time.perf_counter() - inicio
    return estudio


def preparar_datos_web(datos):
    """Construcción de Poinsot y familia de polhodas: la GUI web solo tendrá que dibujarlas."""
    I, U, movimiento = datos['I'], datos['U'], datos['movimiento']
    T2 = Kinetic_energy_2T(U[0], I)
    L2 = Angular_momentum_L2(U[0], I)
    # ω en ejes inerciales: el punto de contacto del elipsoide con el plano invariable.
    herpolhoda = einsum('nij,nj->ni', movimiento['rotaciones'], U[:, :3])
    momento_angular = Inertial_angular_momentum(U[0], I)
    volteos = datos['instantes_volteo']
    return dict(herpolhoda=herpolhoda,
                normal_plano=momento_angular/norm(momento_angular),
                distancia_plano=T2/sqrt(L2),                         # ω·L/|L| = 2T/|L|
                elipsoide_energia=Energy_ellipsoid(I, T2, 96),
                elipsoide_momento=Momentum_ellipsoid(I, L2, 96),
                familia_polhodas=calcular_familia_polhodas(I, L2),
                separatriz_momento=Separatrix(I, L2/I[1]),
                intervalo_volteos=dict(teorico=movimiento['periodo']/2,
                                       medido=float(diff(volteos).mean()) if len(volteos) >= 2 else nan))


def periodo_polhoda_web(I, w):
    """Periodo exacto de ω(t), P = 4 K(k)/ν, sin cancelaciones cerca de la separatriz.

    Polhode_period redondea C = L² − 2T·I2 a 12 cifras y con ε ≲ 10⁻⁶ lo toma por la separatriz.
    Aquí cada diferencia se escribe como suma de términos del mismo signo,
        C = Σ Ii (Ii − I2) ωi²,   2T·I3 − L² = Σ Ii (I3 − Ii) ωi²,   L² − 2T·I1 = Σ Ii (Ii − I1) ωi²,
    y K se evalúa con el módulo complementario m1 = 1 − k² = (I3 − I1)|C| / (...), que es el pequeño:
        K = π / (2 AGM(1, √m1)).
    Solo C = 0 exacto (ε = 0) es la separatriz.
    """
    I1, I2, I3 = I
    w1, w2, w3 = (float(v)**2 for v in w)
    C = I1*(I1 - I2)*w1 + I3*(I3 - I2)*w3
    if C == 0:
        return dict(periodo=float('inf'), lado_separatriz=0, casimir=0.)
    hasta_I3 = I1*(I3 - I1)*w1 + I2*(I3 - I2)*w2           # 2T·I3 − L²
    desde_I1 = I2*(I2 - I1)*w2 + I3*(I3 - I1)*w3           # L² − 2T·I1
    if C > 0:                                              # la polhoda rodea I3
        m1 = (I3 - I1)*C / ((I3 - I2)*desde_I1)
        nu = sqrt((I3 - I2)*desde_I1 / (I1*I2*I3))
    else:                                                  # la polhoda rodea I1
        m1 = (I3 - I1)*(-C) / ((I2 - I1)*hasta_I3)
        nu = sqrt((I2 - I1)*hasta_I3 / (I1*I2*I3))
    a, g = 1., sqrt(m1)
    while abs(a - g) > 1e-15*a:
        a, g = (a + g)/2, sqrt(a*g)
    return dict(periodo=float(4*(pi/(2*a))/nu), lado_separatriz=1 if C > 0 else -1, casimir=C)


def calcular_familia_polhodas(I, L2, niveles=4):
    """Polhodas del mismo |L| con energías distintas, integradas con el motor (RK4, una vuelta)."""
    F = Rigid_body_problem(I, attitude=False)
    curvas = []
    # 2T = L²·s, con s entre 1/I3 y 1/I1; la separatriz está en s = 1/I2.
    for s0, s1 in ((1/I[2], 1/I[1]), (1/I[1], 1/I[0])):
        for s in linspace(s0, s1, niveles + 2)[1:-1]:
            # Punto de partida en el meridiano ω2 = 0 del elipsoide de momento.
            theta = arcsin(sqrt(clip((s - 1/I[2]) / (1/I[0] - 1/I[2]), 0, 1)))
            w0 = sqrt(L2) * array([sin(theta)/I[0], 0., cos(theta)/I[2]])
            periodo = Polhode_period(I, Kinetic_energy_2T(w0, I), L2)
            if not isfinite(periodo):
                continue
            _, W, _ = integrar_trayectoria(F, periodo, w0, metodos_web['RK4'], periodo/240)
            curvas += [W, -W]
    return curvas


def preparar_fantasmas(datos, comparacion):
    """Orientación y ω de cada integrador en los instantes de la animación principal."""
    fantasmas = {}
    for nombre_metodo, resultado in comparacion.items():
        t, U = resultado['t'], resultado['U']
        indices = searchsorted(t, datos['t']).clip(0, len(t) - 1)
        fantasmas[nombre_metodo] = dict(rotaciones=array([Rotation_matrix(q) for q in U[indices, 3:7]]),
                                        omega=U[indices, :3], fin=t[-1])
    return fantasmas


if __name__ == "__main__":
    # 1. Crear la interfaz y calcular la trayectoria inicial.
    interfaz = iniciar_programa_web()
    # 2. Abrir el navegador y atender sus peticiones (equivale a plt.show()).
    interfaz['servir']()
