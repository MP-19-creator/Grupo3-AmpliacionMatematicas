"""
Pagina 2 · INVARIANTES  (enunciado 3.2: conmutar integradores y contrastar la deriva de energia y momento)
Los tres esquemas integran EXACTAMENTE el mismo problema con el mismo dt (o la misma tolerancia si el paso
es adaptativo).  La fisica dice que 2T, L^2 y |q| no cambian: todo lo que se ve aqui es error numerico.
"""
from numpy import maximum, diff

from active.gui_reactive.style import C, colores_metodos, preparar_grafica, poner_leyenda

minimo_logaritmo = 1e-17                                    # suelo para el log de derivas nulas


class Pagina_conservacion:

    titulo = "2  Invariants"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.grafica_energia  = preparar_grafica(figura.add_axes([0.050, 0.600, 0.430, 0.270]),
                           r"KINETIC ENERGY   $|2T/2T_0 - 1|$", ylabel="relative drift")
        self.grafica_momento  = preparar_grafica(figura.add_axes([0.550, 0.600, 0.430, 0.270]),
                           r"ANGULAR MOMENTUM   $|L^2/L_0^2 - 1|$", ylabel="relative drift")
        self.grafica_norma  = preparar_grafica(figura.add_axes([0.050, 0.305, 0.300, 0.215]),
                           r"QUATERNION NORM   $||q| - 1|$", xlabel="t")
        self.grafica_paso = preparar_grafica(figura.add_axes([0.400, 0.305, 0.300, 0.215]),
                           r"TIME STEP USED   $\Delta t(t)$", xlabel="t")
        for ax in (self.grafica_energia, self.grafica_momento, self.grafica_norma):
            ax.set_yscale("log")
        self.titulo_tabla = figura.text(0.735, 0.505, "MAX RELATIVE DRIFT IN [0, tf]", fontsize=10, color=C["accent"],
                                    fontweight="bold")
        self.tabla = figura.text(0.735, 0.478, "", fontsize=10, color=C["text"], va="top", family="monospace",
                              linespacing=1.6)
        self.mensaje = figura.text(0.735, 0.262, "", fontsize=9.5, color=C["muted"], va="bottom", linespacing=1.5)
        self.cursores = [ax.axvline(0, color=C["text"], lw=0.9, alpha=0.8)
                        for ax in (self.grafica_energia, self.grafica_momento, self.grafica_norma, self.grafica_paso)]
        self.graficas = [self.grafica_energia, self.grafica_momento, self.grafica_norma, self.grafica_paso]
        self.textos = [self.titulo_tabla, self.tabla, self.mensaje]
        self.lineas = []

    def mostrar(self, visible):
        for a in self.graficas + self.textos:
            a.set_visible(visible)

    def dibujar(self):
        estado = self.estado
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
            for ax, d in ((self.grafica_energia, dT), (self.grafica_momento, dL), (self.grafica_norma, dq)):
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
        for ax in self.graficas:
            ax.set_xlim(0, tf)
        for ax in (self.grafica_energia, self.grafica_momento, self.grafica_norma):
            ax.set_ylim(minimo_logaritmo, 10)
        self.grafica_paso.set_yscale("log")
        if hi > 0:
            self.grafica_paso.set_ylim(lo / 3, hi * 3)                       # el ruido de redondeo de un dt fijo no se ve
        poner_leyenda(self.grafica_energia, ncol=3, loc="lower right")
        self.tabla.set_text("\n".join(filas_tabla + avisos_metodos))
        tipo_paso = (f"adaptive step, tol = {estado['tol']:.0e}" if estado['adaptativo'] else f"fixed step, dt = {estado['dt_utilizado']:.3g}")
        self.mensaje.set_text(f"Same problem for the three schemes  ·  {tipo_paso}\n"
                              "The physics keeps 2T, L² and |q| constant: every\n"
                              "curve on this page is pure numerical error.")

    def dibujar_instante(self, indice):
        tiempo_elegido = self.estado["t"][indice]
        for c in self.cursores:
            c.set_xdata([tiempo_elegido, tiempo_elegido])

    def tiempo_del_clic(self, evento):
        return evento.xdata if evento.inaxes in self.graficas else None