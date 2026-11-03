"""PEI 1 · versión web: el mismo flujo que PEI1.py, con la GUI en el navegador.

Ejecutar desde la raiz: python PEI1/PEI1_web.py

Los cálculos se importan de PEI1.py, no se copian: si se corrige algo allí, esta
versión lo hereda. Aquí solo se añade lo que dibuja la GUI web y no la de
matplotlib (construcción de Poinsot, familia de polhodas, los tres integradores
a la vez). Borrar este fichero, gui_web.py y la carpeta gui_web/ deja la v1 intacta.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from numpy import array, arcsin, clip, cos, diff, einsum, isfinite, linspace, nan, pi, searchsorted, sin, sqrt
from numpy.linalg import norm
from PEI1 import (metodos, metodos_implicitos, limite_pasos,calcular_trayectoria, comparar_metodos, preparar_apoyo_comparacion,
    preparar_datos_estabilidad, calcular_estudio_error, integrar_trayectoria, instantes_cambio_signo)
from active.gui_reactive.gui_web import crear_interfaz_web
from active.space_physics.eje_intermedio import (Rigid_body_problem, Rotation_matrix, Kinetic_energy_2T,
    Angular_momentum_L2, Inertial_angular_momentum, Energy_ellipsoid, Momentum_ellipsoid, Separatrix,
    Polhode_period)


def iniciar_programa_web():
    """Misma estructura que iniciar_programa() de PEI1.py; cambia solo la GUI que se crea."""
    resultados_actuales = {}
    parametros_actuales = None
    estudios_error = {}

    def calcular_simulacion(parametros):
        nonlocal parametros_actuales
        if parametros != parametros_actuales:
            resultado = calcular_trayectoria(dict(parametros, metodo=metodos[parametros['nombre_metodo']]))
            resultados_actuales.clear()
            resultados_actuales.update(parametros, metodo=metodos[parametros['nombre_metodo']])
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
                resultados_actuales['comparacion_metodos'] = comparar_metodos(resultados_actuales)
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
                    # Volteos de cada esquema (solo web): instantes en que ω del eje inicial cambia de signo.
                    resultados_actuales['volteos_metodos'] = {
                        nombre: instantes_cambio_signo(r['t'], r['U'][:, resultados_actuales['eje']])
                        for nombre, r in resultados_actuales['comparacion_metodos'].items()}
                return dict(comparacion_metodos=resultados_actuales['comparacion_metodos'],
                            apoyo_comparacion=resultados_actuales['apoyo_comparacion'],
                            volteos_metodos=resultados_actuales['volteos_metodos'])
            if 'estabilidad' not in resultados_actuales:
                resultados_actuales['estabilidad'] = preparar_datos_estabilidad(resultados_actuales, resultados_actuales['comparacion_metodos'])
            return dict(estabilidad=resultados_actuales['estabilidad'])
        if numero_pagina == 3:
            if tf_estudio not in estudios_error:
                estudios_error[tf_estudio] = calcular_estudio_error(resultados_actuales, tf_estudio)
            return dict(estudio_error=estudios_error[tf_estudio])
        return {}

    interfaz = crear_interfaz_web(list(metodos), calcular_simulacion, preparar_pagina)
    # La GUI avisa antes de calcular si el paso fijo superaría el límite de pasos de PEI1.py.
    interfaz['configuracion']['limite_pasos'] = {
        nombre: limite_pasos['lento' if metodo in metodos_implicitos else 'rapido'] for nombre, metodo in metodos.items()}
    # Aquí se inicia el primer cálculo, una vez construida la interfaz.
    interfaz['solicitar_calculo']()
    return interfaz


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
            _, W, _ = integrar_trayectoria(F, periodo, w0, metodos['RK4'], periodo/240)
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
