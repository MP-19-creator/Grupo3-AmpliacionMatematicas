"""
Pagina 2 · INVARIANTES  (enunciado 3.2: conmutar integradores y contrastar la deriva de energia y momento)
Los tres esquemas integran EXACTAMENTE el mismo problema con el mismo dt (o la misma tolerancia si el paso
es adaptativo).  La fisica dice que 2T, L^2 y |q| no cambian: todo lo que se ve aqui es error numerico.
"""
from numpy import maximum, diff, isfinite, abs
from matplotlib.ticker import LogLocator, LogFormatterSciNotation, NullLocator
from matplotlib.widgets import Button

from active.gui_reactive.style import C, colores_metodos, preparar_grafica, poner_leyenda

minimo_logaritmo = 1e-17                                    # suelo para el log de derivas nulas


class Pagina_conservacion:

    titulo = "2  Invariants"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.vista = 'Derivas'
        self.con_signo = False
        self.detalle = False
        self.visible = False
        self.grafica_energia  = preparar_grafica(figura.add_axes([0.065, 0.575, 0.415, 0.220]),
                           r"KINETIC ENERGY   $|2T/2T_0 - 1|$", ylabel="relative drift")
        self.grafica_momento  = preparar_grafica(figura.add_axes([0.570, 0.575, 0.400, 0.220]),
                           r"ANGULAR MOMENTUM   $|L^2/L_0^2 - 1|$", ylabel="relative drift")
        self.grafica_norma  = preparar_grafica(figura.add_axes([0.065, 0.365, 0.415, 0.135]),
                           r"QUATERNION NORM   $||q| - 1|$", xlabel="t")
        self.grafica_paso = preparar_grafica(figura.add_axes([0.570, 0.365, 0.400, 0.135]),
                           r"TIME STEP USED   $\Delta t(t)$", xlabel="t")
        for ax in (self.grafica_energia, self.grafica_momento, self.grafica_norma):
            ax.set_yscale("log")
        self.titulo_tabla = figura.text(0.065, 0.290, "DERIVAS MÁXIMAS", fontsize=10, color=C["accent"],
                                    fontweight="bold")
        self.tabla = figura.text(0.400, 0.303, "", fontsize=9, color=C["text"], va="top", family="monospace",
                              linespacing=1.25)
        self.mensaje = figura.text(0.065, 0.268, "", fontsize=8, color=C["muted"], va="top", linespacing=1.3)
        self.cursores = [ax.axvline(0, color=C["text"], lw=0.9, alpha=0.8)
                        for ax in (self.grafica_energia, self.grafica_momento, self.grafica_norma, self.grafica_paso)]
        self.graficas_derivas = [self.grafica_energia, self.grafica_momento, self.grafica_norma, self.grafica_paso]
        self.grafica_trayectorias = preparar_grafica(figura.add_axes([.065, .365, .415, .430]),
            'Proyección transversal')
        self.grafica_fase = preparar_grafica(figura.add_axes([.570, .620, .400, .175]),
            'Componente transversal · fase', 't (s)')
        self.grafica_perturbacion = preparar_grafica(figura.add_axes([.570, .365, .400, .135]),
            'Perturbación transversal', 't (s)', 'Norma (rad/s)')
        self.grafica_perturbacion.set_yscale('log')
        self.grafica_perturbacion.set_ylim(minimo_logaritmo, 1)
        self.graficas_trayectorias = [self.grafica_trayectorias, self.grafica_fase, self.grafica_perturbacion]
        self.contexto = figura.text(.065, .842, '', fontsize=8, color=C['muted'])
        self.textos = [self.titulo_tabla, self.tabla, self.mensaje, self.contexto]
        self.lineas = []
        for ax, titulo in zip(self.graficas_derivas, ('Energía 2T', 'Momento L²', 'Norma del cuaternión', 'Paso temporal')):
            ax.set_title(titulo, loc='left')
            ax.set_ylabel('Deriva relativa' if ax is not self.grafica_paso else 'Δt (s)')
            if ax in (self.grafica_norma, self.grafica_paso): ax.set_xlabel('t (s)')
        for ax in self.graficas_derivas[:3]:
            ax.set_ylim(minimo_logaritmo, 10)
        self.ceros = [ax.axhline(0, color=C['muted'], lw=.8) for ax in self.graficas_derivas[:3]]
        self.curvas_trayectorias, self.marcadores = {}, {}
        for nombre, color in {**colores_metodos, 'Referencia RK4': C['ink']}.items():
            estilo = dict(color=color, lw=1.4, ls='--' if nombre == 'Referencia RK4' else '-', label=nombre)
            self.curvas_trayectorias[nombre] = [ax.plot([], [], **estilo)[0] for ax in self.graficas_trayectorias]
            self.marcadores[nombre] = [ax.plot([], [], 'o', color=color, ms=5, mec='white', mew=.6)[0]
                                       for ax in (self.grafica_trayectorias, self.grafica_fase)]
        self.guia_crecimiento, = self.grafica_perturbacion.plot([], [], ':', color=C['bad'], lw=1.3,
            label=r'Guía local $\propto e^{\lambda t}$')
        self.cursores_trayectorias = [ax.axvline(0, color=C['muted'], lw=.8)
            for ax in (self.grafica_fase, self.grafica_perturbacion)]
        self.artistas_moviles = [*self.cursores, *self.cursores_trayectorias,
            *(m for grupo in self.marcadores.values() for m in grupo)]
        self.controles = []
        for x, ancho, texto, accion in ((.065, .230, 'Ver trayectorias', self.cambiar_vista),
                (.325, .220, 'Ver con signo', self.cambiar_signo),
                (.585, .220, 'Ampliar tiempo', self.cambiar_ventana)):
            b = Button(figura.add_axes([x, .885, ancho, .035]), texto, color=C['soft'], hovercolor=C['line'])
            b.label.set_fontsize(8)
            b.label.set_color(C['accent'])
            b.on_clicked(accion)
            self.controles.append(b)
        self.graficas = self.graficas_derivas + self.graficas_trayectorias + [b.ax for b in self.controles]

    def mostrar(self, visible):
        self.visible = visible
        for ax in self.graficas_derivas:
            ax.set_visible(visible and self.vista == 'Derivas')
        for ax in self.graficas_trayectorias:
            ax.set_visible(visible and self.vista == 'Trayectorias')
        for texto in self.textos:
            texto.set_visible(visible)
        for i, b in enumerate(self.controles):
            activo = visible and (i == 0 or (i == 1 and self.vista == 'Derivas') or (i == 2 and self.vista == 'Trayectorias'))
            b.ax.set_visible(activo)
            b.set_active(activo)

    def cambiar_vista(self, _=None):
        self.vista = 'Trayectorias' if self.vista == 'Derivas' else 'Derivas'
        self.controles[0].label.set_text('Ver derivas' if self.vista == 'Trayectorias' else 'Ver trayectorias')
        self.actualizar_presentacion()

    def cambiar_signo(self, _=None):
        self.con_signo = not self.con_signo
        self.controles[1].label.set_text('Ver magnitud' if self.con_signo else 'Ver con signo')
        self.actualizar_presentacion()

    def cambiar_ventana(self, _=None):
        self.detalle = not self.detalle
        self.controles[2].label.set_text('Tiempo completo' if self.detalle else 'Ampliar tiempo')
        self.actualizar_presentacion()

    def actualizar_presentacion(self):
        if self.visible and 'apoyo_comparacion' in self.estado:
            self.estado['fondo'] = None
            self.dibujar()
            self.mostrar(True)
            self.dibujar_instante(self.estado['indice_actual'])
            self.figura.canvas.draw_idle()

    def dibujar(self):
        estado = self.estado
        if self.vista == 'Trayectorias':
            self.dibujar_trayectorias()
            return
        comparacion_metodos, seleccionado = estado['comparacion_metodos'], estado['nombre_metodo']
        for line in self.lineas:
            line.remove()
        self.lineas = []
        nombres_cortos = { "Euler": "Euler", "Crank-Nicolson": "CN", "RK4": "RK4" }
        filas_tabla = [f"  {'':<6}{'2T':>9}{'L²':>9}{'|q|':>9}{'N':>7}"]
        avisos_metodos, lo, hi = [], 1e300, 0.
        for nombre_metodo, resultado_metodo in comparacion_metodos.items():
            t, U = resultado_metodo["t"], resultado_metodo["U"]
            dT, dL, dq = resultado_metodo['derivas']
            salto_dibujo = max(1, (len(t) - 1) // 2000)
            lw, alpha, z = (2.4, 1.0, 3) if nombre_metodo == seleccionado else (1.2, 0.75, 2)
            style = dict(color=colores_metodos[nombre_metodo], lw=lw, alpha=alpha, zorder=z, label=nombre_metodo)
            for j, (ax, d) in enumerate(((self.grafica_energia, dT), (self.grafica_momento, dL), (self.grafica_norma, dq))):
                if self.con_signo:
                    curva = estado['apoyo_comparacion']['curvas'][nombre_metodo]
                    self.lineas += ax.plot(curva['t'], curva['derivas_signo'][j], **style)
                else:
                    self.lineas += ax.plot(t[::salto_dibujo], maximum(d[::salto_dibujo], minimo_logaritmo), **style)
            if len(t) > 1:
                h = diff(t)
                self.lineas += self.grafica_paso.plot(t[1:][::salto_dibujo], h[::salto_dibujo], **style)
                lo, hi = min(lo, h.min()), max(hi, h.max())
            marca = "▶ " if nombre_metodo == seleccionado else "  "
            aviso = f": {resultado_metodo['aviso']}" if resultado_metodo['aviso'] else ""
            filas_tabla.append(f"{marca}{nombres_cortos[nombre_metodo]:<6}{dT.max():9.1e}{dL.max():9.1e}{dq.max():9.1e}{len(t)-1:7d}")
            if aviso:
                avisos_metodos.append(f"{nombres_cortos[nombre_metodo]}{aviso}")
        tf = estado["t"][-1]
        for ax in self.graficas_derivas:
            ax.set_xlim(0, tf)
        for j, ax in enumerate(self.graficas_derivas[:3]):
            self.ceros[j].set_visible(self.con_signo)
            ax.set_ylabel('Deriva con signo' if self.con_signo else 'Deriva relativa |·|')
            if self.con_signo:
                m = max(max(abs(r['derivas_signo'][j]).max() for r in estado['apoyo_comparacion']['curvas'].values()), 1e-12)
                ax.set_yscale('symlog', linthresh=1e-12)
                ax.set_ylim(-m*1.2, m*1.2)
                interior = min(m/100, 1e-6)
                ticks = [-m, -interior, 0, interior, m] if m > 1e-8 else [-m, 0, m]
                ax.set_yticks(ticks, labels=[f'{v:.0e}' if v else '0' for v in ticks])
            else:
                ax.set_yscale('log')
                ax.yaxis.set_major_locator(LogLocator(numticks=5))
                ax.yaxis.set_major_formatter(LogFormatterSciNotation())
                ax.set_ylim(minimo_logaritmo, 10)
        self.grafica_paso.set_yscale("log")
        if hi > 0:
            self.grafica_paso.set_ylim(lo / 3, hi * 3)                       # el ruido de redondeo de un dt fijo no se ve
            if hi / lo < 1 + 1e-8:
                self.grafica_paso.set_yticks([lo], labels=[f'{lo:.3g}'])
                self.grafica_paso.yaxis.set_minor_locator(NullLocator())
            else:
                self.grafica_paso.yaxis.set_major_locator(LogLocator(numticks=4))
                self.grafica_paso.yaxis.set_major_formatter(LogFormatterSciNotation())
                self.grafica_paso.yaxis.set_minor_locator(NullLocator())
        poner_leyenda(self.grafica_energia, ncol=3, loc="lower right", fontsize=7)
        self.tabla.set_text("\n".join(filas_tabla))
        self.titulo_tabla.set_text('DERIVAS MÁXIMAS |·|')
        self.contexto.set_text('Con signo: positivo aumenta; negativo disminuye · escala simétrica logarítmica' if self.con_signo
                               else 'Mismo problema y parámetros · comparar la magnitud del error numérico')
        tipo_paso = (f"Adaptativo · tol {estado['tol']:.0e}" if estado['adaptativo'] else f"Paso fijo · Δt {estado['dt_utilizado']:.3g} s")
        self.mensaje.set_text(tipo_paso + ('\nTrayectorias truncadas: ' + ', '.join(
            nombres_cortos[n] for n, r in comparacion_metodos.items() if r['aviso']) if avisos_metodos else ''))
        self.mensaje.set_color(C['warn'] if avisos_metodos else C['muted'])

    def dibujar_trayectorias(self):
        datos = self.estado['apoyo_comparacion']
        self.grafica_trayectorias.set_aspect('equal', adjustable='box')
        j, k = datos['transversales']
        self.grafica_trayectorias.set_xlabel(f'ω{j+1} (rad/s)')
        self.grafica_trayectorias.set_ylabel(f'ω{k+1} (rad/s)')
        self.grafica_fase.set_ylabel(f'ω{j+1} (rad/s)')
        for nombre, curva in datos['curvas'].items():
            t, xy = curva['t'], curva['transversal']
            for linea, x, y in zip(self.curvas_trayectorias[nombre],
                    (xy[:, 0], t, t), (xy[:, 1], xy[:, 0], maximum(curva['amplitud'], minimo_logaritmo))):
                linea.set_data(x, y)
        referencia = datos['curvas']['Referencia RK4']
        # El encuadre sigue la referencia: una divergencia no oculta las otras curvas.
        for c, limitar in enumerate((self.grafica_trayectorias.set_xlim, self.grafica_trayectorias.set_ylim)):
            m = max(abs(referencia['transversal'][:, c]).max()*1.35, 1e-9)
            limitar(-m, m)
        tf = self.estado['t'][-1]
        ancho = min(tf, 2*datos['periodo_teorico']) if self.detalle and isfinite(datos['periodo_teorico']) else (tf/4 if self.detalle else tf)
        ancho = max(ancho, min(tf, self.estado['dt_utilizado']))
        inicio = min(max(self.estado['tiempo_actual']-ancho/2, 0), tf-ancho) if self.detalle else 0
        self.guia_crecimiento.set_data(*datos['guia_crecimiento'])
        for ax in (self.grafica_fase, self.grafica_perturbacion):
            ax.set_autoscaley_on(True)
            ax.relim()
            ax.autoscale_view(scalex=False)
            ax.set_xlim(inicio, inicio+ancho)
        m = max(abs(referencia['transversal'][:, 0]).max()*1.35, 1e-9)
        self.grafica_fase.set_ylim(-m, m)
        self.grafica_perturbacion.yaxis.set_major_locator(LogLocator(numticks=4))
        self.grafica_perturbacion.yaxis.set_major_formatter(LogFormatterSciNotation())
        self.grafica_perturbacion.yaxis.set_minor_locator(NullLocator())
        self.guia_crecimiento.set_visible(len(datos['guia_crecimiento'][0]) > 1)
        poner_leyenda(self.grafica_trayectorias, loc='upper left', fontsize=7)
        if self.guia_crecimiento.get_visible():
            self.grafica_perturbacion.legend(handles=[self.guia_crecimiento], fontsize=7, loc='upper right')
        elif self.grafica_perturbacion.get_legend() is not None:
            self.grafica_perturbacion.get_legend().remove()
        estable = self.estado['eje'] != 1
        self.contexto.set_text(('Giro estable: comparar amplitud y fase' if estable else 'Eje intermedio: crecimiento físico y error numérico coexisten')
            + ' · ejes de la referencia')
        self.titulo_tabla.set_text('PERIODO MEDIO · cruces ↑')
        p = datos['periodo_teorico']
        self.mensaje.set_text(f'P teórico: {p:.4g} s\nReferencia RK4 · Δt/4\nAproximada' + (' · truncada' if datos['referencia_aviso'] else '')
                             + '\n—: faltan ciclos completos')
        self.mensaje.set_color(C['warn'] if datos['referencia_aviso'] else C['muted'])
        filas = [f"{'Método':<17}{'P (s)':>10}{'ΔP/P (%)':>12}"]
        for nombre, curva in datos['curvas'].items():
            pm = curva['periodo']
            error = 100*(pm/p-1) if isfinite(p) and p > 0 else float('nan')
            filas.append(f"{nombre:<17}" + (f'{pm:10.4g}' if isfinite(pm) else f"{'—':>10}")
                         + (f'{error:12.3g}' if isfinite(error) else f"{'—':>12}"))
        self.tabla.set_text('\n'.join(filas))

    def dibujar_instante(self, indice):
        tiempo_elegido = self.estado["t"][indice]
        for c in self.cursores:
            c.set_xdata([tiempo_elegido, tiempo_elegido])
        if self.vista == 'Trayectorias':
            for cursor in self.cursores_trayectorias:
                cursor.set_xdata([tiempo_elegido]*2)
            for nombre, curva in self.estado['apoyo_comparacion']['curvas'].items():
                x, y = curva['marcadores'][indice]
                valido = tiempo_elegido <= curva['fin']
                self.marcadores[nombre][0].set_data([x] if valido else [], [y] if valido else [])
                self.marcadores[nombre][1].set_data([tiempo_elegido] if valido else [], [x] if valido else [])

    def tiempo_del_clic(self, evento):
        return evento.xdata if evento.inaxes in self.graficas_derivas + [self.grafica_fase, self.grafica_perturbacion] else None
