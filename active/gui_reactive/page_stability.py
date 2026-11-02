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

from active.gui_reactive.style import C, colores_metodos, preparar_grafica, poner_leyenda


class Pagina_estabilidad:

    titulo = "3  Stability regions"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.grafica_regiones    = preparar_grafica(figura.add_axes([0.035, 0.300, 0.290, 0.545]), "REGIONS  |R(z)| ≤ 1   ·   z = λΔt",
                             "Re z", "Im z")
        self.grafica_ampliada = preparar_grafica(figura.add_axes([0.355, 0.300, 0.290, 0.545]),
                             "ZOOM  ·  colour = log( |R(z)| / |e^z| )  of the selected scheme", "Re z")
        self.grafica_amplificacion    = preparar_grafica(figura.add_axes([0.715, 0.672, 0.270, 0.173]),
                             "|R(iy)|  ON THE IMAGINARY AXIS", "y   (z = i y)")
        self.titulo_tabla = figura.text(0.700, 0.590, "PREDICTION WITH R(z)  vs  SIMULATION", fontsize=10,
                                    color=C["accent"], fontweight="bold")
        self.tabla = figura.text(0.700, 0.567, "", fontsize=9.2, color=C["text"], va="top", family="monospace",
                              linespacing=1.42)
        self.texto_leyenda = figura.text(0.355, 0.888, "", fontsize=10, color=C["muted"], va="bottom")
        self.graficas = [self.grafica_regiones, self.grafica_ampliada, self.grafica_amplificacion]
        self.textos = [self.titulo_tabla, self.tabla, self.texto_leyenda]
        self.puntos_moviles = [ax.plot([], [], "o", color=C["point"], ms=8, mec="white", mew=0.8)[0]
                       for ax in (self.grafica_regiones, self.grafica_ampliada)]
        self.cursor_amplificacion = self.grafica_amplificacion.axvline(0, color=C["point"], lw=1.2)

    def mostrar(self, visible):
        for a in self.graficas + self.textos:
            a.set_visible(visible)

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
        self.grafica_regiones.set_aspect("equal", "box")
        # zoom: ventana del tamano de los autovalores
        r = datos_pagina['radio']
        X, Y, G = datos_pagina['color_ampliacion']
        m = max(abs(G).max(), 1e-12)
        self.grafica_ampliada.pcolormesh(X, Y, G, cmap="RdBu_r", vmin=-m, vmax=m, shading="auto", alpha=0.85, zorder=0)
        self.dibujar_regiones(self.grafica_ampliada, datos_pagina['regiones_ampliadas'], seleccionado, rellenar=False)
        self.grafica_ampliada.set_xlim(-r, r)
        self.grafica_ampliada.set_ylim(-r, r)
        self.grafica_ampliada.set_aspect("equal", "box")
        for ax in (self.grafica_regiones, self.grafica_ampliada):
            ax.plot(z_w.real, z_w.imag, "X", color=C["e"][axis], ms=13, mec="white", mew=1.0,
                    label="λ dt  equilibrium (ω)")
            ax.plot(z_q.real, z_q.imag, "D", color=C["gold"], ms=9, mec="white", mew=0.8,
                    label="±i|ω|dt/2  quaternion")
        handles = [self.grafica_regiones.lines[-2], self.grafica_regiones.lines[-1], self.puntos_moviles[0]]
        self.puntos_moviles[0].set_label("eigenvalues of J(ω(t)) dt  ·  now")
        self.grafica_ampliada.legend(handles=handles, loc="lower left", fontsize=8.5, facecolor=C["panel"],
                            edgecolor=C["line"], labelcolor=C["text"], framealpha=0.92)
        for etiqueta in datos_pagina['regiones_completas']:
            self.grafica_regiones.plot([], [], color=colores_metodos[etiqueta], lw=2.6 if etiqueta == seleccionado else 1.2, label=etiqueta)
        poner_leyenda(self.grafica_regiones, loc="lower left", fontsize=8.5)

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

    # ------------------------------------------------------------ animacion
    def dibujar_instante(self, indice):
        estado = self.estado
        z = estado['estabilidad']['autovalores_por_instante'][indice]
        for m in self.puntos_moviles:
            m.set_data(z.real, z.imag)
        self.cursor_amplificacion.set_xdata([abs(z.imag).max()] * 2)

    def tiempo_del_clic(self, evento):
        return None