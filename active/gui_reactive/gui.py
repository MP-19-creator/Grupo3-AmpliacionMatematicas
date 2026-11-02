"""Interfaz del eje intermedio.

La GUI recibe nombres, datos y acciones proporcionadas por el programa principal.
Después, plt.show() atiende el ratón, el teclado y el temporizador de animación.
"""
import time
from numpy import array, clip, isfinite, searchsorted
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox

from active.gui_reactive.style import C, aplicar_estilo
from active.gui_reactive.page_attitude import Pagina_movimiento
from active.gui_reactive.page_invariants import Pagina_conservacion
from active.gui_reactive.page_stability import Pagina_estabilidad
from active.gui_reactive.page_richardson import Pagina_precision

nombres_ejes = {"Menor  I₁": 0, "Intermedio  I₂": 1, "Mayor  I₃": 2}
tipos_paso = ("Paso fijo", "Adaptativo")
duracion_reproduccion = 20


def crear_interfaz(nombres_metodos, al_calcular, al_preparar_pagina, animar=True):
    """Crea controles y dibujos; el programa principal proporciona las acciones."""
    aplicar_estilo()
    # Estado: resultados recibidos y situacion actual de la ventana.
    estado = dict(reproduciendo=True, velocidad=1., reloj=time.perf_counter(), tiempo_actual=0., indice_actual=0,
             pagina_actual=0, lista_para_dibujar=False, cerrada=False, cambios_pendientes=False)
    figura = plt.figure(figsize=(19.2, 11.2))
    figura.canvas.manager.set_window_title("ÓRBITA · Cuaderno de dinámica / PEI 1")

    # 1. ACCIONES. Definir estas funciones no las ejecuta.
    def leer_parametros():
        nombre_metodo = selector_metodo.value_selected
        return dict(I=(control_I1.val, control_I2.val, control_I3.val), Omega=control_omega.val,
                    dt=control_dt.val, eps=control_perturbacion.val, tf=control_tf.val, tol=control_tolerancia.val,
                    nombre_metodo=nombre_metodo,
                    adaptativo=selector_paso.value_selected == tipos_paso[1],
                    eje=nombres_ejes[selector_eje.value_selected])

    def mostrar_aviso(mensaje, error=False):
        texto_aviso.set_text(mensaje)
        texto_aviso.set_color(C["warn"] if error else C["muted"])
        figura.canvas.draw_idle()

    def marcar_cambios(_=None):
        estado['cambios_pendientes'] = True
        mostrar_aviso("Parámetros modificados · pulsa Calcular para aplicarlos")

    # Al pulsar Calcular: leer valores, avisar al principal y recibir resultados.
    def solicitar_calculo(_=None):
        parametros = leer_parametros()
        try:
            resultado = al_calcular(parametros)
        except (ArithmeticError, ValueError, RuntimeError) as exc:
            mostrar_aviso(f"No se pudo calcular la trayectoria: {exc}", True)
            return
        estado.update(resultado)
        estado['cambios_pendientes'] = False
        estado.pop("error", None)
        # Estos análisis dejan de corresponder a la nueva trayectoria.
        for pagina in paginas:
            pagina.necesita_dibujo = True
        texto_resumen.set_text(f"{estado['nombre_metodo']}  ·  {len(estado['solucion_completa'][0])-1:,} pasos  ·  {estado['tiempo_calculo']:.2f} s")
        mostrar_pagina(estado['pagina_actual'])
        estado['reloj'] = time.perf_counter()

    # Al cambiar de pagina: pedir los datos que faltan y dibujarlos.
    def mostrar_pagina(numero_pagina):
        estado['pagina_actual'] = numero_pagina
        pagina = paginas[numero_pagina]
        estado['lista_para_dibujar'] = False
        paginas[3].control_tf_estudio.set_active(numero_pagina == 3)
        for numero, otra_pagina in enumerate(paginas):
            otra_pagina.mostrar(False)
            pestanas[numero].color = C["accent"] if numero == numero_pagina else C["bg"]
            pestanas[numero].ax.set_facecolor(pestanas[numero].color)
            pestanas[numero].label.set_color(C["bg"] if numero == numero_pagina else C["text"])
        for fondo in fondos_movimiento:
            fondo.set_visible(numero_pagina == 0)
        texto_espera.set_visible(True)
        try:
            if pagina.necesita_dibujo:
                estado.update(al_preparar_pagina(numero_pagina, float(paginas[3].control_tf_estudio.val)))
                pagina.dibujar()
                pagina.necesita_dibujo = False
            pagina.mostrar(True)
            pagina.dibujar_instante(estado['indice_actual'])
            texto_espera.set_visible(False)
            estado['lista_para_dibujar'] = True
            if estado['cambios_pendientes']:
                mostrar_aviso("Parámetros modificados · pulsa Calcular para aplicarlos")
            else:
                mostrar_aviso(" · ".join(estado['avisos']) or "Listo")
        except (ArithmeticError, ValueError, RuntimeError) as exc:
            estado["error"] = str(exc)
            pagina.mostrar(False)
            texto_espera.set_text(f"No se pudo calcular esta vista\n{exc}")
            mostrar_aviso("Error en esta vista · ajusta los parámetros y pulsa Calcular", True)
        estado['reloj'] = time.perf_counter()
        figura.canvas.draw_idle()

    def cambiar_intervalo_estudio(_=None):
        paginas[3].necesita_dibujo = True
        estado['cambios_pendientes'] = True
        mostrar_aviso("Intervalo del estudio modificado · pulsa Calcular para actualizarlo")

    # Cada tic recorre la solucion ya calculada; no vuelve a integrar.
    def avanzar_animacion():
        if estado['cerrada'] or not estado['lista_para_dibujar'] or not estado['reproduciendo']:
            return
        tiempo_real = time.perf_counter()
        tiempo_transcurrido = min(tiempo_real - estado['reloj'], .25)
        estado['reloj'] = tiempo_real
        tiempo_final = estado["t"][-1]
        avance = tiempo_transcurrido * estado['velocidad'] * tiempo_final / duracion_reproduccion
        tiempo_siguiente = (estado['tiempo_actual'] + avance) % tiempo_final
        mostrar_instante(tiempo_siguiente)

    def mostrar_instante(tiempo_elegido):
        estado['tiempo_actual'] = float(clip(tiempo_elegido, 0, estado["t"][-1]))
        estado['indice_actual'] = min(int(searchsorted(estado["t"], estado['tiempo_actual'])), len(estado["t"]) - 1)
        if estado['lista_para_dibujar'] and estado['pagina_actual'] != 3:
            paginas[estado['pagina_actual']].dibujar_instante(estado['indice_actual'])
            figura.canvas.draw_idle()

    def pausar_reanudar(_=None):
        estado['reproduciendo'] = not estado['reproduciendo']
        estado['reloj'] = time.perf_counter()
        boton_pausa.label.set_text("Pausar" if estado['reproduciendo'] else "Reproducir")
        mostrar_instante(estado['tiempo_actual'])

    def restablecer_parametros(_=None):
        for control in controles_parametros:
            control.eventson = False
            if isinstance(control, TextBox):
                control.val = control.valor_inicial
                control.set_val(str(control.valor_inicial))
            else:
                control.reset()
            control.eventson = True
        for selector, seleccionado in ((selector_metodo, 2), (selector_paso, 0), (selector_eje, 1)):
            selector.eventson = False
            selector.set_active(seleccionado)
            selector.eventson = True
        control_tolerancia.ax.set_visible(False)
        estado.update(velocidad=1., reproduciendo=True)
        boton_pausa.label.set_text("Pausar")
        solicitar_calculo()

    def pulsar_tecla(evento):
        if any(control.capturekeystrokes for control in (control_perturbacion, control_dt, control_tolerancia)):
            return
        tecla = evento.key
        if tecla in ("1", "2", "3", "4"):
            mostrar_pagina(int(tecla) - 1)
        elif tecla == " ":
            pausar_reanudar()
        elif tecla in ("left", "right"):
            mostrar_instante(estado['tiempo_actual'] + (.04 if tecla == "right" else -.04) * estado["t"][-1])
        elif tecla == "a":
            selector_eje.set_active((nombres_ejes[selector_eje.value_selected] + 1) % 3)
        elif tecla in ("up", "down"):
            etiquetas = list(nombres_metodos)
            indice_seleccionado = etiquetas.index(selector_metodo.value_selected)
            selector_metodo.set_active((indice_seleccionado + (1 if tecla == "down" else -1)) % len(etiquetas))
        elif tecla == "m":
            selector_paso.set_active(1 - tipos_paso.index(selector_paso.value_selected))
        elif tecla in ("+", "=", "plus"):
            estado['velocidad'] = min(8., estado['velocidad'] * 2)
        elif tecla in ("-", "minus"):
            estado['velocidad'] = max(.125, estado['velocidad'] / 2)
        elif tecla == "v":
            paginas[0].restablecer_camaras()
            figura.canvas.draw_idle()
        elif tecla == "r":
            restablecer_parametros()
        elif tecla == "f":
            figura.canvas.manager.full_screen_toggle()

    def seleccionar_pestana(evento):
        for numero, boton in enumerate(pestanas):
            if evento.inaxes is boton.ax:
                mostrar_pagina(numero)
                return

    def cambiar_tipo_paso(etiqueta):
        control_tolerancia.ax.set_visible(etiqueta == tipos_paso[1])
        figura.canvas.draw_idle()

    def pulsar_grafica(evento):
        if estado['lista_para_dibujar'] and evento.button == 1 and evento.xdata is not None:
            tiempo_elegido = paginas[estado['pagina_actual']].tiempo_del_clic(evento)
            if tiempo_elegido is not None:
                mostrar_instante(tiempo_elegido)

    def cerrar_interfaz(_=None):
        estado['cerrada'] = True
        if estado['temporizador'] is not None:
            estado['temporizador'].stop()

    def capturar_imagen():
        figura.canvas.draw()
        return array(figura.canvas.buffer_rgba())


    # 2. DIBUJO. Crear y colocar las cuatro paginas y sus textos.
    def posicion_horizontal(x):
        return .255 + .735*x

    def posicion_vertical(y):
        return .105 + (y-.255)*1.10

    figura.patches.append(FancyBboxPatch((.012, .018), .227, .964,
        boxstyle="round,pad=0,rounding_size=0.018", transform=figura.transFigure,
        fc=C["panel"], ec=C["line"], lw=.8, zorder=-3))
    figura.text(.030, .950, "ÓRBITA", fontsize=29, fontweight="bold", color=C["accent"])
    figura.text(.031, .924, "DINÁMICA DEL SÓLIDO", fontsize=9, color=C["muted"])
    figura.text(.266, .952, "Teorema del eje intermedio", fontsize=27, fontweight="bold", color=C["ink"])
    figura.text(.267, .920, "Ajusta los parámetros y compara los métodos", fontsize=10, color=C["muted"])
    figura.text(.982, .950, "I₁ < I₂ < I₃", fontsize=17, ha="right", color=C["accent"], family="monospace")
    texto_resumen = figura.text(.982, .920, "Preparando simulación", fontsize=8.5, color=C["muted"], ha="right")
    texto_aviso = figura.text(.267, .032, "", fontsize=9, color=C["muted"], va="center")

    paginas = [
        Pagina_movimiento(figura, estado),
        Pagina_conservacion(figura, estado),
        Pagina_estabilidad(figura, estado),
        Pagina_precision(figura, estado),
    ]
    for pagina in paginas:
        for ax in pagina.graficas:
            x, y, w, h = ax.get_position().bounds
            ax.set_position([posicion_horizontal(x), posicion_vertical(y), w*.735, h*1.10])
            ax.title.set_fontsize(9)
        for texto in pagina.textos:
            x, y = texto.get_position()
            texto.set_position((posicion_horizontal(x), posicion_vertical(y)))
            texto.set_fontsize(min(texto.get_fontsize(), 9))

    paginas[2].texto_leyenda.set_position((posicion_horizontal(.355), .827))
    paginas[2].texto_leyenda.set_fontsize(9)
    paginas[2].texto_leyenda.set_text("Rojo: amplificación extra · Azul: amortiguamiento extra · Puntos: λΔt del estado actual")

    pagina_movimiento = paginas[0]
    pagina_movimiento.textos[0].set_text("ORIENTACIÓN / referencia inercial")
    pagina_movimiento.textos[1].set_text("POINSOT / espacio de fases")
    pagina_movimiento.textos[2].set_text("TEORÍA Y SIMULACIÓN")
    pagina_movimiento.titulo_volteos.set_text("VOLTEOS DEL EJE DE GIRO")
    pagina_movimiento.grafica_velocidades.set_title("VELOCIDAD ANGULAR / ejes del cuerpo", loc="left", fontsize=9, color=C["muted"])
    pagina_movimiento.etiquetas_informacion.set_fontsize(8)
    pagina_movimiento.texto_informacion.set_fontsize(8)
    pagina_movimiento.indicador_estabilidad.set_fontsize(10)
    pagina_movimiento.contador_volteos.set_fontsize(48)
    pagina_movimiento.reloj.set_fontsize(16)
    pagina_movimiento.etiquetas_informacion.set_x(posicion_horizontal(.737))
    pagina_movimiento.crear_linea_tiempo(posicion_horizontal, posicion_vertical)
    fondos_movimiento = []
    for x, w in ((.005, .698), (.720, .280)):
        fondo = FancyBboxPatch((posicion_horizontal(x), .099), w*.735, .720,
            boxstyle="round,pad=0,rounding_size=0.012", transform=figura.transFigure,
            fc=C["panel"], ec=C["line"], lw=.8, zorder=-2)
        figura.patches.append(fondo)
        fondos_movimiento.append(fondo)
    texto_espera = figura.text(.62, .48, "Preparando simulación…", ha="center", va="center", fontsize=13,
        color=C["muted"], linespacing=2, bbox=dict(boxstyle="round,pad=2", fc=C["panel"], ec=C["line"]))
    pestanas = []
    for i, etiqueta in enumerate(("Movimiento", "Conservación", "Estabilidad", "Precisión")):
        b = Button(figura.add_axes([.266 + .183*i, .861, .174, .037]), etiqueta,
                   color=C["bg"], hovercolor=C["soft"])
        b.label.set_fontsize(10)
        b.label.set_fontweight("bold")
        b.label.set_color(C["text"])
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        pestanas.append(b)

    # 3. CONTROLES. Crear deslizadores, campos, botones y selectores.
    def dibujar_seccion(y, numero, titulo):
        figura.text(.031, y, numero, fontsize=9, color=C["accent"], fontweight="bold", family="monospace")
        figura.text(.055, y, titulo, fontsize=9, color=C["text"], fontweight="bold")
        figura.add_artist(plt.Line2D([.031, .220], [y-.012, y-.012], transform=figura.transFigure, color=C["line"], lw=.8))
    dibujar_seccion(.846, "01", "PROPIEDADES DEL SÓLIDO")
    dibujar_seccion(.625, "02", "RESOLUCIÓN TEMPORAL")
    dibujar_seccion(.467, "03", "INTEGRACIÓN")
    dibujar_seccion(.285, "04", "EJE DE GIRO INICIAL")

    def crear_deslizador(x, y, ancho, etiqueta, minimo, maximo, valor_inicial, formato="%.2f"):
        deslizador = Slider(figura.add_axes([x, y, ancho, .016]), etiqueta, minimo, maximo, valinit=valor_inicial, valfmt=formato,
            color=C["accent"], track_color=C["line"], initcolor="none",
            handle_style={"facecolor": C["panel"], "edgecolor": C["accent"], "size": 9})
        deslizador.ax.set_facecolor(C["panel"])
        deslizador.label.set_color(C["text"])
        deslizador.label.set_fontsize(10)
        deslizador.valtext.set_color(C["accent"])
        deslizador.valtext.set_fontsize(9)
        return deslizador

    control_I1  = crear_deslizador(.080, .803, .122, r"$I_1$", .2, 5., 1.)
    control_I2  = crear_deslizador(.080, .767, .122, r"$I_2$", .2, 5., 2.)
    control_I3  = crear_deslizador(.080, .731, .122, r"$I_3$", .2, 5., 3.)
    control_omega   = crear_deslizador(.080, .695, .122, r"$\Omega$", .1, 3., 1.)
    def crear_campo_numerico(y, etiqueta, valor_inicial, minimo, maximo):
        campo = TextBox(figura.add_axes([.100, y-.004, .110, .028]), etiqueta + "  ",
                        initial=f"{valor_inicial:g}", color=C["bg"], hovercolor=C["soft"])
        campo.val = valor_inicial
        campo.valor_inicial = valor_inicial
        campo.label.set_fontsize(10)
        campo.text_disp.set_fontsize(10)
        for spine in campo.ax.spines.values():
            spine.set_edgecolor(C["line"])

        def aceptar_valor(texto):
            try:
                valor = float(texto.replace(",", "."))
                if not isfinite(valor) or not minimo <= valor <= maximo:
                    raise ValueError()
            except ValueError:
                mostrar_aviso(f"{etiqueta}: introduce un valor entre {minimo:g} y {maximo:g}", True)
                return
            campo.val = valor
            marcar_cambios()

        campo.on_submit(aceptar_valor)
        return campo

    control_perturbacion = crear_campo_numerico(.659, "ε", .001, 0., 1.)
    control_dt  = crear_campo_numerico(.582, "Δt (s)", .02, 1e-6, 2.)
    control_tf  = crear_deslizador(.080, .539, .122, r"$t_f$", 1., 150., 80., "%.0f")
    control_tolerancia = crear_campo_numerico(.499, "Tolerancia", 1e-6, 1e-12, .01)
    control_tolerancia.ax.set_visible(False)

    def crear_boton(x, y, etiqueta, ancho=.089, destacado=False):
        boton = Button(figura.add_axes([x, y, ancho, .035]), etiqueta,
                   color=C["accent"] if destacado else C["soft"], hovercolor=C["muted"] if destacado else C["line"])
        boton.label.set_color(C["panel"] if destacado else C["accent"])
        boton.label.set_fontsize(9)
        boton.label.set_fontweight("bold")
        for borde in boton.ax.spines.values():
            borde.set_visible(False)
        return boton

    boton_calcular = crear_boton(.031, .129, "Calcular", ancho=.189, destacado=True)
    boton_pausa = crear_boton(.031, .086, "Pausar")
    boton_restablecer = crear_boton(.131, .086, "Restablecer")

    def crear_selector(posicion, etiquetas, opcion_inicial):
        grafica_selector = figura.add_axes(posicion)
        grafica_selector.set_facecolor(C["panel"])
        for borde in grafica_selector.spines.values():
            borde.set_visible(False)
        selector = RadioButtons(grafica_selector, etiquetas, active=opcion_inicial, activecolor=C["accent"],
                         radio_props={"edgecolor": C["muted"], "s": 48})
        for texto in selector.labels:
            texto.set_color(C["text"])
            texto.set_fontsize(9.5)
        return selector

    selector_metodo = crear_selector([.030, .365, .192, .090], list(nombres_metodos), 2)
    selector_paso = crear_selector([.030, .300, .192, .060], list(tipos_paso), 0)
    selector_eje = crear_selector([.030, .181, .192, .090], list(nombres_ejes), 1)
    figura.text(.031, .065, "Espacio / pausa    ·    1–4 / vistas\n← → tiempo    ·    + − velocidad\nArrastra el 3D    ·    V / cámara    ·    F / ampliar",
             fontsize=7.5, color=C["muted"], va="top", linespacing=1.7)


    # 4. EVENTOS. Conectar cada control con la accion que debe ejecutar.
    controles_parametros = (control_I1, control_I2, control_I3, control_omega, control_dt, control_perturbacion, control_tf, control_tolerancia)
    for deslizador in (control_I1, control_I2, control_I3, control_omega, control_tf):
        deslizador.on_changed(marcar_cambios)
    for selector in (selector_metodo, selector_paso, selector_eje):
        selector.on_clicked(marcar_cambios)
    selector_paso.on_clicked(cambiar_tipo_paso)
    paginas[3].control_tf_estudio.on_changed(cambiar_intervalo_estudio)
    for boton in pestanas:
        boton.on_clicked(seleccionar_pestana)
    boton_calcular.on_clicked(solicitar_calculo)
    boton_pausa.on_clicked(pausar_reanudar)
    boton_restablecer.on_clicked(restablecer_parametros)
    figura.canvas.mpl_connect("key_press_event", pulsar_tecla)
    figura.canvas.mpl_connect("button_press_event", pulsar_grafica)
    figura.canvas.mpl_connect("close_event", cerrar_interfaz)

    # El programa principal iniciará el primer cálculo después de crear la GUI.
    for pagina in paginas:
        pagina.necesita_dibujo = True
        pagina.mostrar(False)

    # 5. ANIMACION. El temporizador llama a avanzar_animacion con la ventana abierta.
    estado['temporizador'] = None
    if animar:
        estado['temporizador'] = figura.canvas.new_timer(interval=40)
        estado['temporizador'].add_callback(avanzar_animacion)
        estado['temporizador'].start()

    # 6. Devolver al principal las acciones y el estado de la interfaz.
    estado.update(
        figura=figura,
        solicitar_calculo=solicitar_calculo,
        mostrar_pagina=mostrar_pagina,
        mostrar_instante=mostrar_instante,
        avanzar_animacion=avanzar_animacion,
        restablecer_parametros=restablecer_parametros,
        cerrar_interfaz=cerrar_interfaz,
        capturar_imagen=capturar_imagen,
        paginas=paginas,
        texto_aviso=texto_aviso,
        controles_parametros=controles_parametros,
        selector_metodo=selector_metodo,
        selector_paso=selector_paso,
        selector_eje=selector_eje,
        pestanas=pestanas,
        botones=(boton_pausa, boton_restablecer, boton_calcular),
    )
    return estado
