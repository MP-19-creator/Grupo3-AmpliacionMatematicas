"""
Pagina 3 · REGIONES DE ESTABILIDAD ABSOLUTA explicadas con los AUTOVALORES del problema  (enunciado 3, |R(z)| <= 1)

Idea en una linea: cerca de un estado, el error se comporta como  dE/dt = J E,  y cada modo propio de J
(autovalor lambda) es una ecuacion test  dU/dt = lambda U.  Un esquema multiplica ese modo por R(z), z = lambda dt,
en CADA paso.  Por eso basta con mirar donde caen los puntos z = lambda dt respecto de la region |R(z)| <= 1:
    |R| > 1 -> el modo crece un poco en cada paso       |R| = 1 -> se conserva       |R| < 1 -> se amortigua
Autovalores que se dibujan:
    x  dinamica en el equilibrio (ecs. 9, 10, 12):  +-i sigma dt (ejes 1 y 3)  o  +-lambda dt reales (eje 2)
    ◆  cinematica del cuaternion:  +-i |w| dt / 2  (explica la deriva de |q|)
    ●  J(w(t)) en el instante actual de la animacion (se mueven al reproducir)
"""
from numpy import abs
from matplotlib.widgets import Button

from active.gui_reactive.style import C, colores_metodos, preparar_grafica, poner_leyenda


class Pagina_estabilidad:

    titulo = "3  Stability regions"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.vista = 'Regiones'
        self.visible = False
        self.grafica_regiones    = preparar_grafica(figura.add_axes([0.065, 0.535, 0.390, 0.255]), "Regiones · |R(z)| ≤ 1",
                             "Re z", "Im z")
        self.grafica_ampliada = preparar_grafica(figura.add_axes([0.570, 0.535, 0.390, 0.255]),
                             "Detalle · log |R(z)| − Re z", "Re z", 'Im z')
        self.grafica_amplificacion    = preparar_grafica(figura.add_axes([0.060, 0.300, 0.390, 0.130]),
                             "Amplificación |R(iy)|", "y")
        self.titulo_tabla = figura.text(0.530, 0.450, "PREDICCIÓN / SIMULACIÓN", fontsize=10,
                                    color=C["accent"], fontweight="bold")
        self.tabla = figura.text(0.530, 0.425, "", fontsize=8, color=C["text"], va="top", family="monospace",
                              linespacing=1.2)
        self.texto_leyenda = figura.text(0.065, 0.842, "", fontsize=8, color=C["muted"], va="bottom")
        self.graficas_regiones = [self.grafica_regiones, self.grafica_ampliada, self.grafica_amplificacion]
        self.textos = [self.titulo_tabla, self.tabla, self.texto_leyenda]
        self.puntos_moviles = [ax.plot([], [], "o", color=C["point"], ms=8, mec="white", mew=0.8)[0]
                       for ax in (self.grafica_regiones, self.grafica_ampliada)]
        self.cursor_amplificacion = self.grafica_amplificacion.axvline(0, color=C["point"], lw=1.2)
        self.grafica_espiral = preparar_grafica(figura.add_axes([.065, .340, .410, .450]),
            'Modo oscilatorio · trayectorias', 'Re u', 'Im u')
        self.grafica_ganancia = preparar_grafica(figura.add_axes([.580, .630, .380, .160]),
            'Amplitud por paso · |R(iy)|', 'y = σΔt')
        self.grafica_desfase = preparar_grafica(figura.add_axes([.580, .350, .380, .150]),
            'Error de fase por paso', 'y = σΔt', 'arg R(iy) − y (rad)')
        self.graficas_modo = [self.grafica_espiral, self.grafica_ganancia, self.grafica_desfase]
        self.colores = {**colores_metodos, 'Euler implícito': '#3578A8', 'Exacta': C['ink']}
        self.curvas_modo = {}
        self.marcadores_modo = {}
        for nombre, color in self.colores.items():
            self.curvas_modo[nombre] = [ax.plot([], [], color=color,
                ls='--' if nombre == 'Exacta' else '-', lw=1.4, label=nombre)[0] for ax in self.graficas_modo]
            self.marcadores_modo[nombre], = self.grafica_espiral.plot([], [], 'o', ms=5, color=color, mec='white', mew=.6)
        self.grafica_ganancia.axhline(1, color=C['muted'], lw=.7, ls=':')
        self.grafica_desfase.axhline(0, color=C['muted'], lw=.7, ls=':')
        self.nota_modo = figura.text(.065, .278, '', fontsize=8, color=C['muted'], va='top', linespacing=1.35)
        self.control_vista = Button(figura.add_axes([.065, .885, .300, .035]), 'Ver amplitud y fase',
            color=C['soft'], hovercolor=C['line'])
        self.control_vista.label.set_fontsize(8)
        self.control_vista.label.set_color(C['accent'])
        self.control_vista.on_clicked(self.cambiar_vista)
        self.graficas = self.graficas_regiones + self.graficas_modo + [self.control_vista.ax]
        self.textos.append(self.nota_modo)
        self.artistas_moviles = [*self.puntos_moviles, self.cursor_amplificacion, *self.marcadores_modo.values()]

    def mostrar(self, visible):
        self.visible = visible
        for ax in self.graficas_regiones:
            ax.set_visible(visible and self.vista == 'Regiones')
        for ax in self.graficas_modo:
            ax.set_visible(visible and self.vista == 'Modo')
        for texto in (self.titulo_tabla, self.tabla):
            texto.set_visible(visible and self.vista == 'Regiones')
        self.texto_leyenda.set_visible(visible)
        self.nota_modo.set_visible(visible and self.vista == 'Modo')
        self.control_vista.ax.set_visible(visible)
        self.control_vista.set_active(visible)

    def cambiar_vista(self, _=None):
        self.vista = 'Modo' if self.vista == 'Regiones' else 'Regiones'
        self.control_vista.label.set_text('Ver regiones' if self.vista == 'Modo' else 'Ver amplitud y fase')
        if self.visible and 'estabilidad' in self.estado:
            self.estado['fondo'] = None
            self.dibujar()
            self.mostrar(True)
            self.dibujar_instante(self.estado['indice_actual'])
            self.figura.canvas.draw_idle()

    def dibujar_regiones(self, ax, regiones, seleccionado, rellenar=True):
        for etiqueta, (X, Y, A) in regiones.items():
            if etiqueta == seleccionado and rellenar:
                ax.contourf(X, Y, A, levels=[0, 1], colors=[colores_metodos[etiqueta]], alpha=0.16)
            ax.contour(X, Y, A, levels=[1], colors=[colores_metodos[etiqueta]],
                       linewidths=2.6 if etiqueta == seleccionado else 1.2, alpha=1 if etiqueta == seleccionado else 0.8)
        ax.axhline(0, color=C["muted"], lw=0.7)
        ax.axvline(0, color=C["muted"], lw=0.7)

    def dibujar(self):
        estado = self.estado
        if self.vista == 'Modo':
            self.dibujar_modo()
            return
        self.texto_leyenda.set_text('Rojo: amplifica · Azul: amortigua · Puntos: λΔt actual')
        datos_pagina = estado['estabilidad']
        axis, seleccionado = estado['eje'], estado['nombre_metodo']
        z_w, z_q = datos_pagina['autovalores_iniciales']
        for ax in (self.grafica_regiones, self.grafica_ampliada):
            for coll in list(ax.collections) + list(ax.images) + [l for l in ax.lines if l not in self.puntos_moviles]:
                coll.remove()
            for txt in list(ax.texts):
                txt.remove()
        # vista global: las tres regiones enteras
        self.dibujar_regiones(self.grafica_regiones, datos_pagina['regiones_completas'], seleccionado)
        self.grafica_regiones.set_xlim(-3.4, 1.4)
        self.grafica_regiones.set_ylim(-3.2, 3.2)
        self.grafica_regiones.set_aspect("auto")
        # zoom: ventana del tamano de los autovalores
        r = datos_pagina['radio']
        X, Y, G = datos_pagina['color_ampliacion']
        m = max(abs(G).max(), 1e-12)
        self.grafica_ampliada.pcolormesh(X, Y, G, cmap="RdBu_r", vmin=-m, vmax=m, shading="auto", alpha=0.85, zorder=0)
        self.dibujar_regiones(self.grafica_ampliada, datos_pagina['regiones_ampliadas'], seleccionado, rellenar=False)
        self.grafica_ampliada.set_xlim(-r, r)
        self.grafica_ampliada.set_ylim(-r, r)
        self.grafica_ampliada.set_aspect("auto")
        for ax in (self.grafica_regiones, self.grafica_ampliada):
            ax.plot(z_w.real, z_w.imag, "X", color=C["e"][axis], ms=13, mec="white", mew=1.0,
                    label="Equilibrio (ω)")
            ax.plot(z_q.real, z_q.imag, "D", color=C["gold"], ms=9, mec="white", mew=0.8,
                    label="Cuaternión")
        handles = [self.grafica_regiones.lines[-2], self.grafica_regiones.lines[-1], self.puntos_moviles[0]]
        self.puntos_moviles[0].set_label("Estado actual")
        self.grafica_ampliada.legend(handles=handles, loc="lower left", fontsize=7, facecolor=C["panel"],
                            edgecolor=C["line"], labelcolor=C["text"], framealpha=0.92)
        for etiqueta in datos_pagina['regiones_completas']:
            self.grafica_regiones.plot([], [], color=colores_metodos[etiqueta], lw=2.6 if etiqueta == seleccionado else 1.2, label=etiqueta)
        poner_leyenda(self.grafica_regiones, loc="lower left", fontsize=7)

        # |R(iy)| en el eje imaginario: Euler > 1, Crank-Nicolson = 1, RK4 < 1 hasta y = 2.83
        for line in [l for l in self.grafica_amplificacion.lines if l is not self.cursor_amplificacion]:
            line.remove()
        y = datos_pagina['eje_imaginario']
        for etiqueta, valores in datos_pagina['curvas_eje_imaginario'].items():
            self.grafica_amplificacion.plot(y, valores, color=colores_metodos[etiqueta],
                           lw=2.4 if etiqueta == seleccionado else 1.2, label=etiqueta)
        self.grafica_amplificacion.axhline(1, color=C["muted"], lw=0.8, ls=":")
        self.grafica_amplificacion.set_xlim(0, 3.2)
        self.grafica_amplificacion.set_ylim(0.6, 1.8)
        self.marcas_imaginarias = [abs(z_w[0].imag), abs(z_q[0].imag)]
        for ym, col in zip(self.marcas_imaginarias, (C["e"][axis], C["gold"])):
            if ym > 0:
                self.grafica_amplificacion.axvline(ym, color=col, lw=1.2, ls="--")
        self.tabla.set_text(datos_pagina['tabla'])

    def dibujar_modo(self):
        datos = self.estado['estabilidad']['demostracion']
        y = datos['barrido']
        for nombre, curva in datos['curvas'].items():
            orbita = curva['orbita']
            for linea, x, v in zip(self.curvas_modo[nombre],
                    (orbita.real, y, y), (orbita.imag, curva['ganancia'], curva['fase'])):
                linea.set_data(x, v)
        exacta = datos['exacta']
        for linea, x, v in zip(self.curvas_modo['Exacta'],
                (exacta.real, y, y), (exacta.imag, y*0+1, y*0)):
            linea.set_data(x, v)
        self.grafica_espiral.set_xlim(-3.3, 3.3)
        self.grafica_espiral.set_ylim(-3.3, 3.3)
        self.grafica_espiral.set_aspect('equal', adjustable='box')
        self.grafica_ganancia.set_xlim(0, y[-1])
        self.grafica_ganancia.set_ylim(0, 3.2)
        self.grafica_desfase.set_xlim(0, y[-1])
        self.grafica_desfase.set_ylim(-1.7, 1.7)
        poner_leyenda(self.grafica_espiral, fontsize=7, loc='upper left')
        self.texto_leyenda.set_text(f'Modo test u′ = iσu · σΔt = {datos["y"]:g} · comparación lineal, no trayectoria del satélite')
        self.nota_modo.set_text('Euler explícito: amplifica · Euler implícito: amortigua\n'
            'Crank–Nicolson conserva |u| en este modo lineal, pero introduce desfase.')

    # ------------------------------------------------------------ animacion
    def dibujar_instante(self, indice):
        estado = self.estado
        if self.vista == 'Modo':
            datos = estado['estabilidad']['demostracion']
            paso = estado['t'][indice]/estado['t'][-1]*(len(datos['n'])-1)
            n = min(len(datos['n'])-2, int(paso))
            fraccion = paso-n
            for nombre, marcador in self.marcadores_modo.items():
                orbita = datos['exacta'] if nombre == 'Exacta' else datos['curvas'][nombre]['orbita']
                # Interpolación exclusivamente visual entre los pasos calculados.
                u = (1-fraccion)*orbita[n] + fraccion*orbita[n+1]
                marcador.set_data([u.real], [u.imag])
            return
        z = estado['estabilidad']['autovalores_por_instante'][indice]
        for m in self.puntos_moviles:
            m.set_data(z.real, z.imag)
        self.cursor_amplificacion.set_xdata([abs(z.imag).max()] * 2)

    def tiempo_del_clic(self, evento):
        return None
