"""
Pagina 1 · ACTITUD Y ESPACIO DE FASES  (enunciado 3.3)
  - izquierda: la caja con las proporciones reales de las inercias, girando en ejes inerciales (cuaterniones)
  - centro:    espacio de fases (w1, w2, w3) con los elipsoides de 2T y L^2, la separatriz y la polhoda
  - derecha:   teoria frente a simulacion (autovalor, lado de la separatriz, periodo exacto y medido, volteos)
  - abajo:     w(t) en ejes cuerpo, que se dibuja hasta el instante actual
"""
from numpy import array, cross, linspace, searchsorted, clip, sqrt
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

from active.gui_reactive.style import C, Panel, Legend
from active.space_physics.eje_intermedio import (Kinetic_energy_2T, Angular_momentum_L2, Rotation_matrix,
    Energy_ellipsoid, Momentum_ellipsoid, Separatrix, Side_of_separatrix, Polhode_period, Linear_eigenvalues,
    Box_dimensions)

light = array([0.35, -0.55, 0.76]) / norm([0.35, -0.55, 0.76])      # direccion de la luz que ilumina la caja


def Zero_crossings(t, x):
    """ Instantes en que x cambia de signo (interpolacion lineal entre nodos) """
    i = ((x[1:] * x[:-1]) < 0).nonzero()[0]
    return t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])


class Attitude_page:

    title = "1  Attitude & phase space"

    def __init__(self, fig, S):
        self.fig, self.S = fig, S
        self.ax_body  = fig.add_axes([0.000, 0.385, 0.360, 0.515], projection="3d")
        self.ax_phase = fig.add_axes([0.330, 0.385, 0.385, 0.515], projection="3d")
        self.ax_w     = Panel(fig.add_axes([0.045, 0.275, 0.655, 0.105]))
        for ax in (self.ax_body, self.ax_phase):
            ax.set_facecolor(C["bg"]); ax.set_axis_off()
        T = []
        T.append(fig.text(0.022, 0.885, "ATTITUDE  ·  inertial frame", fontsize=10, color=C["muted"], fontweight="bold"))
        T.append(fig.text(0.355, 0.885, "PHASE SPACE  ·  body frame  (Poinsot)", fontsize=10, color=C["muted"],
                          fontweight="bold"))
        self.badge = fig.text(0.735, 0.872, "", fontsize=15, fontweight="bold", va="center", color=C["bg"],
                              bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.8", fc=C["ok"], ec="none"))
        T.append(fig.text(0.735, 0.815, "THEORY  vs  SIMULATION", fontsize=10, color=C["accent"], fontweight="bold"))
        self.info_labels = fig.text(0.735, 0.790, "", fontsize=11, color=C["muted"], va="top", linespacing=1.6)
        self.info = fig.text(0.985, 0.790, "", fontsize=11, color=C["text"], va="top", ha="right",
                             linespacing=1.6, fontweight="bold")
        self.flips_label = fig.text(0.735, 0.392, "FLIPS OF THE SPIN AXIS", fontsize=10, fontweight="bold")
        self.flips = fig.text(0.735, 0.285, "0", fontsize=52, fontweight="bold", animated=True)
        self.clock = fig.text(0.835, 0.325, "", fontsize=20, color=C["text"], animated=True)
        self.speed = fig.text(0.835, 0.290, "", fontsize=10, color=C["muted"], animated=True)
        T += [self.badge, self.info_labels, self.info, self.flips_label, self.flips, self.clock, self.speed]
        self.texts = T

        self.lines_bg = [self.ax_w.plot([], [], color=C["e"][i], lw=1.0, alpha=0.22)[0] for i in range(3)]
        self.lines = [self.ax_w.plot([], [], color=C["e"][i], lw=1.8, label=fr"$\omega_{i+1}$", animated=True)[0]
                      for i in range(3)]
        self.cursor = self.ax_w.axvline(0, color=C["text"], lw=0.9, alpha=0.8, animated=True)
        Legend(self.ax_w, ncol=3, loc="upper right", fontsize=8)
        self.ax_w.set_title("ANGULAR VELOCITY  ·  body frame", loc="left", fontsize=9, color=C["muted"])
        self.axes = [self.ax_body, self.ax_phase, self.ax_w]

    def set_visible(self, flag):
        for a in self.axes + self.texts:
            a.set_visible(flag)

    # ------------------------------------------------------------ dibujo estatico (una vez por calculo)
    def refresh(self):
        self.draw_phase_space()
        self.draw_body()
        t, U, d = self.S["t"], self.S["U"], self.S["d"]
        for i in range(3):
            self.lines_bg[i].set_data(t[d], U[d, i])
        self.ax_w.set_xlim(0, t[-1])
        m = abs(U[:, 0:3]).max() * 1.15
        self.ax_w.set_ylim(-m, m)
        self.write_info()

    def draw_phase_space(self):
        S, ax = self.S, self.ax_phase
        I, U, d = S["I"], S["U"], S["d"]
        T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
        ax.clear(); ax.set_axis_off()
        R = sqrt(T2 / I[0]) * 1.05
        for i, name in enumerate((r"$\omega_1$", r"$\omega_2$", r"$\omega_3$")):
            e = [0, 0, 0]; e[i] = R
            ax.plot([-e[0], e[0]], [-e[1], e[1]], [-e[2], e[2]], color=C["e"][i], lw=0.9, alpha=0.55)
            ax.text(*(1.1 * array(e)), name, color=C["e"][i], fontsize=14, ha="center", va="center")
        ax.plot_wireframe(*Energy_ellipsoid(I, T2, 36), color=C["energy"], lw=0.35, alpha=0.35, rcount=14, ccount=14)
        ax.plot_wireframe(*Momentum_ellipsoid(I, L2, 36), color=C["momentum"], lw=0.35, alpha=0.25, rcount=14, ccount=14)
        for curve in Separatrix(I, T2):
            ax.plot(*curve, color=C["separatrix"], lw=1.6, ls=(0, (5, 4)))
        ax.plot(U[d, 0], U[d, 1], U[d, 2], color=C["polhode"], lw=0.8, alpha=0.35)
        self.recent, = ax.plot([], [], [], color=C["polhode"], lw=2.4, solid_capstyle="round", animated=True)
        self.glow, = ax.plot([], [], [], "o", color=C["point"], ms=17, alpha=0.25, mew=0, animated=True)
        self.point, = ax.plot([], [], [], "o", color=C["point"], ms=7, mec="white", mew=0.8, animated=True)
        ax.set_xlim(-R, R); ax.set_ylim(-R, R); ax.set_zlim(-R, R)
        ax.set_box_aspect((1, 1, 1), zoom=1.2)
        handles = [plt.Line2D([], [], color=C["energy"], lw=2, label="2T ellipsoid"),
                   plt.Line2D([], [], color=C["momentum"], lw=2, label=r"$L^2$ ellipsoid"),
                   plt.Line2D([], [], color=C["separatrix"], lw=2, ls=(0, (5, 4)), label="separatrix"),
                   plt.Line2D([], [], color=C["polhode"], lw=2, label="polhode (numerical)")]
        ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=False, labelcolor=C["muted"],
                  bbox_to_anchor=(0.0, 0.0))

    def draw_body(self):
        S, ax = self.S, self.ax_body
        I, U = S["I"], S["U"]
        a, b, c = Box_dimensions(I)
        side = max(a, b, c)
        a, b, c = [max(s/side, 0.04) for s in (a, b, c)]            # placa plana: grosor minimo
        V = array([[sx*a/2, sy*b/2, sz*c/2] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        self.faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
        normals = []
        for f in self.faces:                                         # normal exterior de cada cara
            n = cross(V[f[1]] - V[f[0]], V[f[2]] - V[f[0]])
            n = n / norm(n)
            normals.append(n if n @ V[f].mean(axis=0) > 0 else -n)
        self.vertices, self.normals = V, array(normals)

        ax.clear(); ax.set_axis_off(); ax.set_facecolor(C["bg"])
        self.trail = Line3DCollection([[(0, 0, 0), (0, 0, 0)]], linewidths=2.2, capstyle="round")
        ax.add_collection3d(self.trail)
        self.box = Poly3DCollection([], edgecolor="#3A2A0C", linewidths=0.6)
        ax.add_collection3d(self.box)
        self.arrows = [ax.plot([], [], [], color=C["e"][i], lw=3, solid_capstyle="round")[0] for i in range(3)]
        self.tips = [ax.plot([], [], [], "o", color=C["e"][i], ms=6)[0] for i in range(3)]
        L = Rotation_matrix(U[0, 3:7]) @ (array(I) * U[0, 0:3])
        L = 0.82 * L / norm(L)
        ax.plot([0, L[0]], [0, L[1]], [0, L[2]], color=C["text"], lw=1.4, ls=(0, (4, 3)))
        ax.text(*(1.1 * L), "L", color=C["text"], fontsize=14, fontweight="bold", ha="center", va="center")
        for lim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
            lim(-0.75, 0.75)
        ax.set_box_aspect((1, 1, 1), zoom=1.15)
        ax.view_init(elev=18, azim=-55)
        for a in (self.trail, self.box, *self.arrows, *self.tips):
            a.set_animated(True)

    def write_info(self):
        S = self.S
        I, t, U, axis = S["I"], S["t"], S["U"], S["axis"]
        T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
        lam = Linear_eigenvalues(I, axis, U[0, axis])[0]
        real = abs(lam.imag) < 1e-14
        side = {1: "around I3", -1: "around I1", 0: "separatrix"}[Side_of_separatrix(I, T2, L2)]
        c = Zero_crossings(t, U[:, 1])
        measured = f"{c[2] - c[0]:.3f}" if len(c) >= 3 else "not reached"
        tn = S["nodes"][0]
        rows = [ ("Linearised eigenvalue  λ", f"±{abs(lam):.4f}{'' if real else ' i'}"),
                 ("Polhode  (L²/2T vs I₂)", f"{side}  ({L2/T2:.4f})"),
                 ("Period  exact  4K(k)/ν", f"{Polhode_period(I, T2, L2):.3f}"),
                 ("Period  measured", measured),
                 ("Max drift  2T  ·  L²", f"{S['drifts'][0]:.1e}  ·  {S['drifts'][1]:.1e}"),
                 ("Max drift  |q|", f"{S['drifts'][2]:.1e}"),
                 ("Scheme", S["name"] + ("  (adaptive)" if S["adaptive"] else "")),
                 ("Steps N  ·  CPU", f"{len(tn) - 1}  ·  {S['cpu']:.2f} s") ]
        self.info_labels.set_text("\n".join(r[0] for r in rows))
        self.info.set_text("\n".join(r[1] for r in rows))
        self.badge.set_text(f"{'UNSTABLE  ·  saddle' if real else 'STABLE  ·  centre'}    "
                            f"λ = ±{abs(lam):.3f}{'' if real else ' i'}")
        self.badge.get_bbox_patch().set_facecolor(C["bad"] if real else C["ok"])
        self.flips_label.set_color(C["e"][axis]); self.flips.set_color(C["e"][axis])

    # ------------------------------------------------------------ animacion (cada fotograma)
    def animated(self):
        if not hasattr(self, "box"):
            return []
        return [self.trail, self.box, *self.arrows, *self.tips, self.recent, self.glow, self.point,
                *self.lines, self.cursor, self.flips, self.clock, self.speed]

    def update_frame(self, k):
        S = self.S
        t, U, d, w = S["t"], S["U"], S["d"], S["window"]
        tp = t[k]
        self.point.set_data_3d(U[k:k+1, 0], U[k:k+1, 1], U[k:k+1, 2])
        self.glow.set_data_3d(U[k:k+1, 0], U[k:k+1, 1], U[k:k+1, 2])
        j0 = searchsorted(t, tp - 0.35 * w)
        seg = U[j0:k+1:max(1, (k - j0) // 120 or 1)]
        self.recent.set_data_3d(seg[:, 0], seg[:, 1], seg[:, 2])
        self.move_body(k)
        kd = searchsorted(d, k, side="right")
        for i in range(3):
            self.lines[i].set_data(t[d[:kd]], U[d[:kd], i])
        self.cursor.set_xdata([tp, tp])
        self.clock.set_text(f"t = {tp:.1f}")
        self.flips.set_text(f"{searchsorted(S['flips'], tp)}")
        self.speed.set_text(f"speed ×{S['speed']:g}" + ("" if S["playing"] else "   paused"))

    def move_body(self, k):
        S = self.S
        U, axis, t = S["U"], S["axis"], S["t"]
        R = Rotation_matrix(U[k, 3:7])
        v = self.vertices @ R.T
        self.box.set_verts([[v[i] for i in face] for face in self.faces])
        shade = 0.28 + 0.72 * clip((self.normals @ R.T) @ light, 0, 1)
        gold = array(to_rgb(C["gold"]))
        self.box.set_facecolor([(*(gold * s), 1.0) for s in shade])
        for i in range(3):
            e = 0.78 * R[:, i]
            self.arrows[i].set_data_3d([0, e[0]], [0, e[1]], [0, e[2]])
            self.tips[i].set_data_3d([e[0]], [e[1]], [e[2]])
        # estela de la punta del eje de giro inicial durante la ultima ventana de tiempo
        idx = searchsorted(t, linspace(max(0., t[k] - S["window"]), t[k], 60)).clip(0, len(t) - 1)
        tips = array([0.78 * Rotation_matrix(U[j, 3:7])[:, axis] for j in idx])
        self.trail.set_segments([tips[i:i+2] for i in range(len(tips) - 1)])
        col = array(to_rgb(C["e"][axis]))
        self.trail.set_color([(*col, 0.9 * (i + 1) / len(tips)) for i in range(len(tips) - 1)])

    def reset_views(self):
        self.ax_body.view_init(elev=18, azim=-55)
        self.ax_phase.view_init(elev=30, azim=-60)

    def click_time(self, event):
        return event.xdata if event.inaxes is self.ax_w else None