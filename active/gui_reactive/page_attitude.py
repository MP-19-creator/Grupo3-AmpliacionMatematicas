"""
Pagina 1 · ACTITUD Y ESPACIO DE FASES  (enunciado 3.3)
  - izquierda: la caja con las proporciones reales de las inercias, girando en ejes inerciales (cuaterniones)
  - centro:    espacio de fases (w1, w2, w3) con los elipsoides de 2T y L^2, la separatriz y la polhoda
  - derecha:   teoria frente a simulacion (autovalor, lado de la separatriz, periodo exacto y medido, volteos)
  - abajo:     w(t) en ejes cuerpo, que se dibuja hasta el instante actual
"""
from numpy import array, cross, linspace, searchsorted, clip
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

from active.gui_reactive.style import C, preparar_grafica, poner_leyenda
direccion_luz = array([0.35, -0.55, 0.76]) / norm([0.35, -0.55, 0.76])      # direccion de la luz que ilumina la caja


class Pagina_movimiento:

    titulo = "1  Attitude & phase space"

    def __init__(self, figura, estado):
        self.figura, self.estado = figura, estado
        self.grafica_cuerpo  = figura.add_axes([0.000, 0.385, 0.360, 0.515], projection="3d")
        self.grafica_fases = figura.add_axes([0.330, 0.385, 0.385, 0.515], projection="3d")
        self.grafica_velocidades     = preparar_grafica(figura.add_axes([0.045, 0.275, 0.655, 0.105]))
        for ax in (self.grafica_cuerpo, self.grafica_fases):
            ax.set_facecolor(C["bg"])
            ax.set_axis_off()
        textos_cabecera = []
        textos_cabecera.append(figura.text(0.022, 0.885, "ATTITUDE  ·  inertial frame", fontsize=10, color=C["muted"], fontweight="bold"))
        textos_cabecera.append(figura.text(0.355, 0.885, "PHASE SPACE  ·  body frame  (Poinsot)", fontsize=10, color=C["muted"],
                          fontweight="bold"))
        self.indicador_estabilidad = figura.text(0.735, 0.872, "", fontsize=15, fontweight="bold", va="center", color=C["bg"],
                              bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.8", fc=C["ok"], ec="none"))
        textos_cabecera.append(figura.text(0.735, 0.815, "THEORY  vs  SIMULATION", fontsize=10, color=C["accent"], fontweight="bold"))
        self.etiquetas_informacion = figura.text(0.735, 0.790, "", fontsize=11, color=C["muted"], va="top", linespacing=1.6)
        self.texto_informacion = figura.text(0.985, 0.790, "", fontsize=11, color=C["text"], va="top", ha="right",
                             linespacing=1.6, fontweight="bold")
        self.titulo_volteos = figura.text(0.735, 0.392, "FLIPS OF THE SPIN AXIS", fontsize=10, fontweight="bold")
        self.contador_volteos = figura.text(0.735, 0.285, "0", fontsize=52, fontweight="bold")
        self.reloj = figura.text(0.835, 0.325, "", fontsize=20, color=C["text"])
        self.velocidad = figura.text(0.835, 0.290, "", fontsize=10, color=C["muted"])
        textos_cabecera += [self.indicador_estabilidad, self.etiquetas_informacion, self.texto_informacion, self.titulo_volteos, self.contador_volteos, self.reloj, self.velocidad]
        self.textos = textos_cabecera

        self.lineas_completas = [self.grafica_velocidades.plot([], [], color=C["e"][i], lw=1.0, alpha=0.22)[0] for i in range(3)]
        self.lineas = [self.grafica_velocidades.plot([], [], color=C["e"][i], lw=1.8, label=fr"$\omega_{i+1}$")[0]
                      for i in range(3)]
        self.cursor_tiempo = self.grafica_velocidades.axvline(0, color=C["text"], lw=0.9, alpha=0.8)
        poner_leyenda(self.grafica_velocidades, ncol=3, loc="upper right", fontsize=8)
        self.grafica_velocidades.set_title("ANGULAR VELOCITY  ·  body frame", loc="left", fontsize=9, color=C["muted"])
        self.graficas = [self.grafica_cuerpo, self.grafica_fases, self.grafica_velocidades]

    def crear_linea_tiempo(self, posicion_horizontal, posicion_vertical):
        """Crea el recorrido temporal una vez colocados los paneles."""
        self.linea_tiempo = self.figura.add_axes([posicion_horizontal(.738), posicion_vertical(.530), .232*.735, .018])
        self.linea_tiempo.set_facecolor(C["panel"])
        self.linea_tiempo.set_ylim(-1, 1)
        self.linea_tiempo.set_yticks([])
        self.linea_tiempo.tick_params(axis="x", colors=C["muted"], labelsize=8, length=0, pad=6)
        for spine in self.linea_tiempo.spines.values():
            spine.set_visible(False)
        self.linea_tiempo.axhline(0, color=C["line"], lw=4, solid_capstyle="round")
        self.progreso, = self.linea_tiempo.plot([], [], color=C["accent"], lw=4, solid_capstyle="round")
        self.marcador_tiempo, = self.linea_tiempo.plot([], [], "o", color=C["accent"], ms=7, mec=C["panel"])
        titulo = self.figura.text(posicion_horizontal(.737), posicion_vertical(.570), "RECORRIDO TEMPORAL", fontsize=8.5,
                              fontweight="bold", color=C["accent"])
        hint = self.figura.text(posicion_horizontal(.737), posicion_vertical(.478), "Pulsa la línea para explorar el tiempo.",
                             fontsize=8, color=C["muted"])
        self.graficas.append(self.linea_tiempo)
        self.textos += [titulo, hint]

    def mostrar(self, visible):
        for a in self.graficas + self.textos:
            a.set_visible(visible)

    # ------------------------------------------------------------ dibujo estatico (una vez por calculo)
    def dibujar(self):
        self.dibujar_espacio_fases()
        self.dibujar_cuerpo()
        t, U, d = self.estado["t"], self.estado["U"], self.estado['indices_dibujo']
        for i in range(3):
            self.lineas_completas[i].set_data(t[d], U[d, i])
        self.grafica_velocidades.set_xlim(0, t[-1])
        m = abs(U[:, 0:3]).max() * 1.15
        self.grafica_velocidades.set_ylim(-m, m)
        self.escribir_informacion()
        self.linea_tiempo.set_xlim(0, t[-1])
        self.linea_tiempo.set_xticks([0, t[-1]])
        self.linea_tiempo.set_xticklabels(["0 s", f"{t[-1]:g} s"])
        for ax in (self.grafica_cuerpo, self.grafica_fases):
            ax.set_facecolor(C["panel"])

    def dibujar_espacio_fases(self):
        estado, ax = self.estado, self.grafica_fases
        U, d = estado["U"], estado['indices_dibujo']
        ax.clear()
        ax.set_axis_off()
        R = estado['movimiento']['radio']
        for i, nombre_metodo in enumerate((r"$\omega_1$", r"$\omega_2$", r"$\omega_3$")):
            e = [0, 0, 0]
            e[i] = R
            ax.plot([-e[0], e[0]], [-e[1], e[1]], [-e[2], e[2]], color=C["e"][i], lw=0.9, alpha=0.55)
            ax.text(*(1.1 * array(e)), nombre_metodo, color=C["e"][i], fontsize=14, ha="center", va="center")
        ax.plot_wireframe(*estado['movimiento']['elipsoide_energia'], color=C["energy"], lw=0.35, alpha=0.35, rcount=14, ccount=14)
        ax.plot_wireframe(*estado['movimiento']['elipsoide_momento'], color=C["momentum"], lw=0.35, alpha=0.25, rcount=14, ccount=14)
        for curve in estado['movimiento']['separatriz']:
            ax.plot(*curve, color=C["separatrix"], lw=1.6, ls=(0, (5, 4)))
        ax.plot(U[d, 0], U[d, 1], U[d, 2], color=C["polhode"], lw=0.8, alpha=0.35)
        self.trayectoria_reciente, = ax.plot([], [], [], color=C["polhode"], lw=2.4, solid_capstyle="round")
        self.halo, = ax.plot([], [], [], "o", color=C["point"], ms=17, alpha=0.25, mew=0)
        self.punto_actual, = ax.plot([], [], [], "o", color=C["point"], ms=7, mec="white", mew=0.8)
        ax.set_xlim(-R, R)
        ax.set_ylim(-R, R)
        ax.set_zlim(-R, R)
        ax.set_box_aspect((1, 1, 1), zoom=1.2)
        handles = [plt.Line2D([], [], color=C["energy"], lw=2, label="2T ellipsoid"),
                   plt.Line2D([], [], color=C["momentum"], lw=2, label=r"$L^2$ ellipsoid"),
                   plt.Line2D([], [], color=C["separatrix"], lw=2, ls=(0, (5, 4)), label='separatriz'),
                   plt.Line2D([], [], color=C["polhode"], lw=2, label="polhode (numerical)")]
        ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=False, labelcolor=C["muted"],
                  bbox_to_anchor=(0.0, 0.0))

    def dibujar_cuerpo(self):
        estado, ax = self.estado, self.grafica_cuerpo
        a, b, c = estado['movimiento']['dimensiones']
        explicacion = max(a, b, c)
        a, b, c = [max(s/explicacion, 0.04) for s in (a, b, c)]            # placa plana: grosor minimo
        V = array([[sx*a/2, sy*b/2, sz*c/2] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        self.caras = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
        normales = []
        for f in self.caras:                                         # normal exterior de cada cara
            n = cross(V[f[1]] - V[f[0]], V[f[2]] - V[f[0]])
            n = n / norm(n)
            normales.append(n if n @ V[f].mean(axis=0) > 0 else -n)
        self.vertices, self.normales = V, array(normales)

        ax.clear()
        ax.set_axis_off()
        ax.set_facecolor(C["bg"])
        self.estela = Line3DCollection([[(0, 0, 0), (0, 0, 0)]], linewidths=2.2, capstyle="round")
        ax.add_collection3d(self.estela)
        self.caja = Poly3DCollection([], edgecolor="#3A2A0C", linewidths=0.6)
        ax.add_collection3d(self.caja)
        self.flechas = [ax.plot([], [], [], color=C["e"][i], lw=3, solid_capstyle="round")[0] for i in range(3)]
        self.puntas_ejes = [ax.plot([], [], [], "o", color=C["e"][i], ms=6)[0] for i in range(3)]
        L = estado['movimiento']['vector_momento']
        ax.plot([0, L[0]], [0, L[1]], [0, L[2]], color=C["text"], lw=1.4, ls=(0, (4, 3)))
        ax.text(*(1.1 * L), "L", color=C["text"], fontsize=14, fontweight="bold", ha="center", va="center")
        for lim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
            lim(-0.75, 0.75)
        ax.set_box_aspect((1, 1, 1), zoom=1.15)
        ax.view_init(elev=18, azim=-55)

    def escribir_informacion(self):
        estado = self.estado
        axis = estado['eje']
        lam = estado['movimiento']['autovalor']
        real = abs(lam.imag) < 1e-14
        self.etiquetas_informacion.set_text("Autovalor λ\nPeriodo exacto\nDeriva 2T · L²\nDeriva |q|")
        self.texto_informacion.set_text(
            f"±{abs(lam):.4f}{'' if real else ' i'}\n"
            f"{estado['movimiento']['periodo']:.3f}\n"
            f"{estado['derivas'][0]:.1e}  ·  {estado['derivas'][1]:.1e}\n"
            f"{estado['derivas'][2]:.1e}")
        self.indicador_estabilidad.set_text(f"{'INESTABLE' if real else 'ESTABLE'}    "
                            f"λ = ±{abs(lam):.3f}{'' if real else ' i'}")
        self.indicador_estabilidad.get_bbox_patch().set_facecolor(C["bad"] if real else C["ok"])
        self.titulo_volteos.set_color(C["e"][axis])
        self.contador_volteos.set_color(C["e"][axis])

    # ------------------------------------------------------------ animacion (cada fotograma)
    def dibujar_instante(self, indice):
        estado = self.estado
        t, U, d, w = estado["t"], estado["U"], estado['indices_dibujo'], estado['ventana_estela']
        tiempo_elegido = t[indice]
        self.punto_actual.set_data_3d(U[indice:indice+1, 0], U[indice:indice+1, 1], U[indice:indice+1, 2])
        self.halo.set_data_3d(U[indice:indice+1, 0], U[indice:indice+1, 1], U[indice:indice+1, 2])
        j0 = searchsorted(t, tiempo_elegido - 0.35 * w)
        seg = U[j0:indice+1:max(1, (indice - j0) // 120 or 1)]
        self.trayectoria_reciente.set_data_3d(seg[:, 0], seg[:, 1], seg[:, 2])
        self.mover_cuerpo(indice)
        kd = searchsorted(d, indice, side="right")
        for i in range(3):
            self.lineas[i].set_data(t[d[:kd]], U[d[:kd], i])
        self.cursor_tiempo.set_xdata([tiempo_elegido, tiempo_elegido])
        self.reloj.set_text(f"t = {tiempo_elegido:.1f}")
        self.contador_volteos.set_text(f"{searchsorted(estado['instantes_volteo'], tiempo_elegido)}")
        self.velocidad.set_text(f"speed ×{estado['velocidad']:g}" + ("" if estado['reproduciendo'] else "   paused"))
        self.progreso.set_data([0, tiempo_elegido], [0, 0])
        self.marcador_tiempo.set_data([tiempo_elegido], [0])

    def mover_cuerpo(self, indice):
        estado = self.estado
        U, axis, t = estado["U"], estado['eje'], estado["t"]
        R = estado['movimiento']['rotaciones'][indice]
        v = self.vertices @ R.T
        self.caja.set_verts([[v[i] for i in face] for face in self.caras])
        shade = 0.28 + 0.72 * clip((self.normales @ R.T) @ direccion_luz, 0, 1)
        gold = array(to_rgb(C["gold"]))
        self.caja.set_facecolor([(*(gold * s), 1.0) for s in shade])
        for i in range(3):
            e = 0.78 * R[:, i]
            self.flechas[i].set_data_3d([0, e[0]], [0, e[1]], [0, e[2]])
            self.puntas_ejes[i].set_data_3d([e[0]], [e[1]], [e[2]])
        # estela de la punta del eje de giro inicial durante la ultima ventana de tiempo
        indices_ajuste = searchsorted(t, linspace(max(0., t[indice] - estado['ventana_estela']), t[indice], 60)).clip(0, len(t) - 1)
        puntas_ejes = estado['puntas_estela'][indices_ajuste]
        self.estela.set_segments([puntas_ejes[i:i+2] for i in range(len(puntas_ejes) - 1)])
        col = array(to_rgb(C["e"][axis]))
        self.estela.set_color([(*col, 0.9 * (i + 1) / len(puntas_ejes)) for i in range(len(puntas_ejes) - 1)])

    def restablecer_camaras(self):
        self.grafica_cuerpo.view_init(elev=18, azim=-55)
        self.grafica_fases.view_init(elev=30, azim=-60)

    def tiempo_del_clic(self, evento):
        return evento.xdata if evento.inaxes in (self.grafica_velocidades, self.linea_tiempo) else None
