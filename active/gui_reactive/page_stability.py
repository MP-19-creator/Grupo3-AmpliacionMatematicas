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
from numpy import linspace, abs, exp, log, prod, sqrt, searchsorted

from active.gui_reactive.style import C, scheme_colors, Panel, Legend
from active.numerical_engine.Estabilidad import stability_region, stability_function
from active.space_physics.eje_intermedio import Linear_eigenvalues, Jacobian_eigenvalues, Kinematic_eigenvalues

names = { "Euler": "Euler", "Crank-Nicolson": "Crank_Nicolson", "RK4": "RK4" }     # etiqueta GUI -> funcion R(z)


class Stability_page:

    title = "3  Stability regions"

    def __init__(self, fig, S):
        self.fig, self.S = fig, S
        self.ax_z    = Panel(fig.add_axes([0.035, 0.300, 0.290, 0.545]), "REGIONS  |R(z)| ≤ 1   ·   z = λΔt",
                             "Re z", "Im z")
        self.ax_zoom = Panel(fig.add_axes([0.355, 0.300, 0.290, 0.545]),
                             "ZOOM  ·  colour = log( |R(z)| / |e^z| )  of the selected scheme", "Re z")
        self.ax_R    = Panel(fig.add_axes([0.715, 0.672, 0.270, 0.173]),
                             "|R(iy)|  ON THE IMAGINARY AXIS", "y   (z = i y)")
        self.table_title = fig.text(0.700, 0.590, "PREDICTION WITH R(z)  vs  SIMULATION", fontsize=10,
                                    color=C["accent"], fontweight="bold")
        self.table = fig.text(0.700, 0.567, "", fontsize=9.2, color=C["text"], va="top", family="monospace",
                              linespacing=1.42)
        self.legend_text = fig.text(0.355, 0.888, "", fontsize=10, color=C["muted"], va="bottom")
        self.axes = [self.ax_z, self.ax_zoom, self.ax_R]
        self.texts = [self.table_title, self.table, self.legend_text]
        self.moving = [ax.plot([], [], "o", color=C["point"], ms=8, mec="white", mew=0.8, animated=True)[0]
                       for ax in (self.ax_z, self.ax_zoom)]
        self.cursor_R = self.ax_R.axvline(0, color=C["point"], lw=1.2, animated=True)

    def set_visible(self, flag):
        for a in self.axes + self.texts:
            a.set_visible(flag)

    # ------------------------------------------------------------ paso local (fijo o adaptativo)
    def local_dt(self, tp):
        tn = self.S["nodes"][0]
        if not self.S["adaptive"] or len(tn) < 2:
            return self.S["dt_used"]
        i = min(max(int(searchsorted(tn, tp)), 1), len(tn) - 1)
        return tn[i] - tn[i-1]

    def draw_regions(self, ax, x, y, selected, fill=True):
        for label, fname in names.items():
            X, Y, A = stability_region(fname, x, y)
            if label == selected and fill:
                ax.contourf(X, Y, A, levels=[0, 1], colors=[scheme_colors[label]], alpha=0.16)
            ax.contour(X, Y, A, levels=[1], colors=[scheme_colors[label]],
                       linewidths=2.6 if label == selected else 1.2, alpha=1 if label == selected else 0.8)
        ax.axhline(0, color=C["muted"], lw=0.7); ax.axvline(0, color=C["muted"], lw=0.7)

    def refresh(self):
        S = self.S
        I, axis, Omega, selected = S["I"], S["axis"], S["Omega"], S["name"]
        dt = self.local_dt(0.)
        z_w = Linear_eigenvalues(I, axis, Omega) * dt                     # dinamica en el equilibrio
        z_q = Kinematic_eigenvalues(S["U"][0]) * dt                       # cinematica del cuaternion
        self.z_static = (z_w, z_q)

        for ax in (self.ax_z, self.ax_zoom):
            for coll in list(ax.collections) + list(ax.images) + [l for l in ax.lines if l not in self.moving]:
                coll.remove()
            for txt in list(ax.texts):
                txt.remove()
        # vista global: las tres regiones enteras
        self.draw_regions(self.ax_z, linspace(-3.4, 1.4, 260), linspace(-3.2, 3.2, 300), selected)
        self.ax_z.set_xlim(-3.4, 1.4); self.ax_z.set_ylim(-3.2, 3.2); self.ax_z.set_aspect("equal", "box")
        # zoom: ventana del tamano de los autovalores
        r = 1.6 * max(abs(z_w).max(), abs(z_q).max(), 1e-3)
        X, Y, A = stability_region(names[selected], linspace(-r, r, 241), linspace(-r, r, 241))
        G = log(A) - X                         # log(|R(z)| / |e^z|): lo que el esquema amplifica DE MAS (rojo) o DE MENOS
        m = max(abs(G).max(), 1e-12)
        self.ax_zoom.pcolormesh(X, Y, G, cmap="RdBu_r", vmin=-m, vmax=m, shading="auto", alpha=0.85, zorder=0)
        self.draw_regions(self.ax_zoom, linspace(-r, r, 241), linspace(-r, r, 241), selected, fill=False)
        self.ax_zoom.set_xlim(-r, r); self.ax_zoom.set_ylim(-r, r); self.ax_zoom.set_aspect("equal", "box")
        for ax in (self.ax_z, self.ax_zoom):
            ax.plot(z_w.real, z_w.imag, "X", color=C["e"][axis], ms=13, mec="white", mew=1.0,
                    label="λ dt  equilibrium (ω)")
            ax.plot(z_q.real, z_q.imag, "D", color=C["gold"], ms=9, mec="white", mew=0.8,
                    label="±i|ω|dt/2  quaternion")
        handles = [self.ax_z.lines[-2], self.ax_z.lines[-1], self.moving[0]]
        self.moving[0].set_label("eigenvalues of J(ω(t)) dt  ·  now")
        self.ax_zoom.legend(handles=handles, loc="lower left", fontsize=8.5, facecolor=C["panel"],
                            edgecolor=C["line"], labelcolor=C["text"], framealpha=0.92)
        for label in names:
            self.ax_z.plot([], [], color=scheme_colors[label], lw=2.6 if label == selected else 1.2, label=label)
        Legend(self.ax_z, loc="lower left", fontsize=8.5)

        # |R(iy)| en el eje imaginario: Euler > 1, Crank-Nicolson = 1, RK4 < 1 hasta y = 2.83
        for line in [l for l in self.ax_R.lines if l is not self.cursor_R]:
            line.remove()
        y = linspace(0, 3.2, 400)
        for label, fname in names.items():
            self.ax_R.plot(y, abs(stability_function(fname, 1j*y)), color=scheme_colors[label],
                           lw=2.4 if label == selected else 1.2, label=label)
        self.ax_R.axhline(1, color=C["muted"], lw=0.8, ls=":")
        self.ax_R.set_xlim(0, 3.2); self.ax_R.set_ylim(0.6, 1.8)
        self.y_marks = [abs(z_w[0].imag), abs(z_q[0].imag)]
        for ym, col in zip(self.y_marks, (C["e"][axis], C["gold"])):
            if ym > 0:
                self.ax_R.axvline(ym, color=col, lw=1.2, ls="--")
        self.write_table(z_w, z_q)

    def write_table(self, z_w, z_q):
        """ Prediccion con R(z) frente a lo que da la simulacion de cada esquema """
        S = self.S
        short = { "Euler": "Euler", "Crank-Nicolson": "CN", "RK4": "RK4" }
        kind = "real: unstable" if abs(z_w[0].imag) < 1e-14 else "imaginary: centre"
        rows = ["1) ω mode at the equilibrium, ONE step", f"   z = {z_w[0]:.4g}   ({kind})",
                f"  {'':<6}{'|R(z)|':>13}{'exact |e^z|':>13}"]
        for label, fname in names.items():
            mark = "▶ " if label == S["name"] else "  "
            rows.append(f"{mark}{short[label]:<6}{abs(stability_function(fname, z_w[0])):13.8f}{abs(exp(z_w[0])):13.8f}")
        rows += ["", "2) quaternion: |q(t_f)| - 1   (exact: 0)", "   z = ±i|ω|Δt/2 at every step",
                 f"  {'':<6}{'prod |R(z_n)|':>13}{'simulated':>13}"]
        for label, fname in names.items():
            run = S["runs"].get(label)
            if run is None or len(run["t"]) < 2:
                continue
            mark = "▶ " if label == S["name"] else "  "
            t, U = run["t"], run["U"]
            w = sqrt((U[:-1, 0:3]**2).sum(axis=1))                         # |w_n| en cada paso
            factors = abs(stability_function(fname, 0.5j * w * (t[1:] - t[:-1])))
            predicted, simulated = prod(factors) - 1, sqrt((U[-1, 3:7]**2).sum()) - 1
            rows.append(f"{mark}{short[label]:<6}{predicted:13.3e}{simulated:13.3e}")
        self.table.set_text("\n".join(rows))
        self.legend_text.set_text("Every step multiplies each mode by R(z), z = λΔt.  Zoom colour: red = the scheme "
                                  "amplifies MORE than the physics (e^z), blue = LESS, white = exact")

    # ------------------------------------------------------------ animacion
    def animated(self):
        return self.moving + [self.cursor_R]

    def update_frame(self, k):
        S = self.S
        tp = S["t"][k]
        z = Jacobian_eigenvalues(S["I"], S["U"][k]) * self.local_dt(tp)
        for m in self.moving:
            m.set_data(z.real, z.imag)
        self.cursor_R.set_xdata([abs(z.imag).max()] * 2)

    def click_time(self, event):
        return None