"""
Pagina 4 · RICHARDSON Y ORDEN DE CONVERGENCIA  (enunciado 3: estimacion de error por extrapolacion de Richardson)

No conocemos la solucion exacta del solido rigido, pero si sabemos COMO encoge el error de un esquema de orden q
al partir el paso por dos:  E_N ~ C dt^q.  Integrando con N y con 2N pasos:
        U_N - U_2N  =  E_N - E_2N  =  E_N (1 - 2^-q)     ->     E_N  ~  (U_N - U_2N) / (1 - 2^-q)
  - izquierda: log D frente a log N con D = |U_N(tf) - U_2N(tf)|.  Recta de pendiente -q: el orden se LEE en la grafica
  - derecha arriba: error estimado por Richardson frente al error verdadero (referencia muy fina) a lo largo del tiempo
  - derecha abajo: la tabla de la que sale todo: al duplicar N, D se divide por 2^q (2, 4, 16)
"""
from numpy import log10, isfinite, maximum
from matplotlib.widgets import Slider

from active.gui_reactive.style import C, colores_metodos, preparar_grafica, poner_leyenda


class Pagina_precision:

    titulo = "4  Richardson & order"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.grafica_convergencia = preparar_grafica(figura.add_axes([0.055, 0.345, 0.395, 0.505]),
                             "CONVERGENCE  ·  log D  vs  log N     (slope = −order)",
                             r"$\log_{10} N$", r"$\log_{10} D$,    $D = |U_N(t_f) - U_{2N}(t_f)|$")
        self.grafica_error = preparar_grafica(figura.add_axes([0.530, 0.610, 0.455, 0.240]),
                             "RICHARDSON ESTIMATE  vs  TRUE ERROR  (selected scheme, current Δt)", "t", "|error|")
        self.grafica_error.set_yscale("log")
        self.titulo_tabla = figura.text(0.515, 0.512, "", fontsize=10, color=C["accent"], fontweight="bold")
        self.tabla = figura.text(0.515, 0.487, "", fontsize=9.5, color=C["text"], va="top", family="monospace",
                              linespacing=1.45)
        self.explicacion = figura.text(0.815, 0.480, "", fontsize=9.2, color=C["muted"], va="top", linespacing=1.55)
        self.texto_resumen_estudio = figura.text(0.055, 0.893, "", fontsize=10, color=C["warn"])
        self.grafica_control_estudio = figura.add_axes([0.120, 0.262, 0.200, 0.018])
        self.control_tf_estudio = Slider(self.grafica_control_estudio, r"study $t_f$", 5., 40., valinit=20., valfmt="%.0f",
                               color=C["accent"], track_color=C["line"], initcolor="none",
                               handle_style={"facecolor": C["text"], "edgecolor": C["accent"], "size": 10})
        self.grafica_control_estudio.set_facecolor(C["panel"])
        self.control_tf_estudio.label.set_color(C["text"])
        self.control_tf_estudio.valtext.set_color(C["muted"])
        self.graficas = [self.grafica_convergencia, self.grafica_error, self.grafica_control_estudio]
        self.textos = [self.titulo_tabla, self.tabla, self.explicacion, self.texto_resumen_estudio]

    def mostrar(self, visible):
        for a in self.graficas + self.textos:
            a.set_visible(visible)

    # ------------------------------------------------------------ dibujo
    def dibujar(self):
        datos_pagina = self.estado['estudio_error']
        curvas = datos_pagina['curvas_convergencia']
        t, error_estimado, error_referencia, N = datos_pagina['errores']
        tiempo_calculo, tf_estudio = datos_pagina['tiempo_calculo'], datos_pagina["tf"]
        estado, ax = self.estado, self.grafica_convergencia
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        for nombre_metodo, r in curvas.items():
            col = colores_metodos[nombre_metodo]
            validos = isfinite(r["D"]) & (r["D"] > 0)
            seleccionado = nombre_metodo == estado['nombre_metodo']
            ax.plot(log10(r["N"][validos]), log10(r["D"][validos]), "o-", color=col,
                    lw=2.4 if seleccionado else 1.1, ms=5, label=f"{nombre_metodo} · orden {-r['pendiente']:.2f}")
            indices_ajuste = r['indices_ajuste']
            if len(indices_ajuste) >= 2 and isfinite(r['pendiente']):
                x = log10(r["N"][indices_ajuste])
                ax.plot(x, r['pendiente']*x+r["b"], "--", color=col, alpha=.65)
        ax.relim()
        ax.autoscale_view()
        poner_leyenda(ax, loc="lower left", fontsize=9)
        ax = self.grafica_error
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        if error_estimado is not None:
            d = slice(1, None, max(1, N//800))
            ax.plot(t[d], maximum(error_estimado[d], 1e-17), color=colores_metodos[estado['nombre_metodo']], lw=2,
                    label="Estimación de Richardson")
            ax.plot(t[d], maximum(error_referencia[d], 1e-17), color=C["point"], ls="--", lw=1.2,
                    label="Referencia RK4 · 8N pasos")
            ax.set_xlim(0, t[-1])
            poner_leyenda(ax, fontsize=8, loc="lower right")
        else:
            ax.text(.05, .5, "El método diverge en este intervalo. Reduce Δt.", transform=ax.transAxes,
                    color=C["warn"], fontsize=10)
        ax.relim()
        ax.autoscale_view()
        r = curvas[estado['nombre_metodo']]
        ordenes = r['ordenes']
        filas_tabla = [f"{'N':>7} {'Δt':>9} {'Diferencia D':>14} {'Orden':>8}"]
        for indice, n in enumerate(r["N"]):
            orden = f"{ordenes[indice]:8.2f}" if indice < len(ordenes) and isfinite(ordenes[indice]) else "       —"
            filas_tabla.append(f"{n:7d} {tf_estudio/n:9.4f} {r['D'][indice]:14.3e} {orden}")
        self.titulo_tabla.set_text(f"{estado['nombre_metodo'].upper()}  /  ORDEN TEÓRICO {estado['orden']}")
        self.tabla.set_text("\n".join(filas_tabla))
        self.explicacion.set_text("CÓMO LEERLO\n\nDuplicar N reduce Δt\na la mitad.\n\nLa pendiente mide\nel orden observado.\n\nD compara las mallas\nN y 2N, sin solución\nexacta conocida.")
        self.texto_resumen_estudio.set_text(f"Estudio completo · t = {tf_estudio:.0f} · cálculo {tiempo_calculo:.2f} s")
        self.texto_resumen_estudio.set_color(C["muted"])


    def dibujar_instante(self, indice):
        pass

    def tiempo_del_clic(self, evento):
        return None
