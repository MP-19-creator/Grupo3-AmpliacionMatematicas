"""
Pagina 2 · INVARIANTES  (enunciado 3.2: conmutar integradores y contrastar la deriva de energia y momento)
Los tres esquemas integran EXACTAMENTE el mismo problema con el mismo dt (o la misma tolerancia si el paso
es adaptativo).  La fisica dice que 2T, L^2 y |q| no cambian: todo lo que se ve aqui es error numerico.
"""
from numpy import abs, maximum, sqrt, diff

from active.gui_reactive.style import C, scheme_colors, Panel, Legend
from active.space_physics.eje_intermedio import Kinetic_energy_2T, Angular_momentum_L2

floor = 1e-17                                    # suelo para el log de derivas nulas


def Drifts(U, I):
    """ Derivas relativas |2T/2T0 - 1|, |L^2/L0^2 - 1| y ||q| - 1| a lo largo de una trayectoria U[n, :] """
    dT = abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(U[0], I) - 1)
    dL = abs(Angular_momentum_L2(U, I) / Angular_momentum_L2(U[0], I) - 1)
    dq = abs(sqrt((U[:, 3:7]**2).sum(axis=1)) - 1)
    return dT, dL, dq


class Invariants_page:

    title = "2  Invariants"

    def __init__(self, fig, S):
        self.fig, self.S = fig, S
        self.ax_T  = Panel(fig.add_axes([0.050, 0.600, 0.430, 0.270]),
                           r"KINETIC ENERGY   $|2T/2T_0 - 1|$", ylabel="relative drift")
        self.ax_L  = Panel(fig.add_axes([0.550, 0.600, 0.430, 0.270]),
                           r"ANGULAR MOMENTUM   $|L^2/L_0^2 - 1|$", ylabel="relative drift")
        self.ax_q  = Panel(fig.add_axes([0.050, 0.305, 0.300, 0.215]),
                           r"QUATERNION NORM   $||q| - 1|$", xlabel="t")
        self.ax_dt = Panel(fig.add_axes([0.400, 0.305, 0.300, 0.215]),
                           r"TIME STEP USED   $\Delta t(t)$", xlabel="t")
        for ax in (self.ax_T, self.ax_L, self.ax_q):
            ax.set_yscale("log")
        self.table_title = fig.text(0.735, 0.505, "MAX RELATIVE DRIFT IN [0, tf]", fontsize=10, color=C["accent"],
                                    fontweight="bold")
        self.table = fig.text(0.735, 0.478, "", fontsize=10, color=C["text"], va="top", family="monospace",
                              linespacing=1.6)
        self.message = fig.text(0.735, 0.262, "", fontsize=9.5, color=C["muted"], va="bottom", linespacing=1.5)
        self.cursors = [ax.axvline(0, color=C["text"], lw=0.9, alpha=0.8, animated=True)
                        for ax in (self.ax_T, self.ax_L, self.ax_q, self.ax_dt)]
        self.axes = [self.ax_T, self.ax_L, self.ax_q, self.ax_dt]
        self.texts = [self.table_title, self.table, self.message]
        self.lines = []

    def set_visible(self, flag):
        for a in self.axes + self.texts:
            a.set_visible(flag)

    def refresh(self):
        S = self.S
        runs, I, selected = S["runs"], S["I"], S["name"]
        for line in self.lines:
            line.remove()
        self.lines = []
        short = { "Euler": "Euler", "Crank-Nicolson": "CN", "RK4": "RK4" }
        rows = [f"  {'':<6}{'2T':>9}{'L²':>9}{'|q|':>9}{'N':>7}"]
        steps, lo, hi = [], 1e300, 0.
        for name, run in runs.items():
            t, U = run["t"], run["U"]
            dT, dL, dq = Drifts(U, I)
            stride = max(1, (len(t) - 1) // 2000)
            lw, alpha, z = (2.4, 1.0, 3) if name == selected else (1.2, 0.75, 2)
            style = dict(color=scheme_colors[name], lw=lw, alpha=alpha, zorder=z, label=name)
            for ax, d in ((self.ax_T, dT), (self.ax_L, dL), (self.ax_q, dq)):
                self.lines += ax.plot(t[::stride], maximum(d[::stride], floor), **style)
            if len(t) > 1:
                h = diff(t)
                self.lines += self.ax_dt.plot(t[1:][::stride], h[::stride], **style)
                lo, hi = min(lo, h.min()), max(hi, h.max())
            mark = "▶ " if name == selected else "  "
            cut = f": {run['note']}" if run["note"] else ""
            rows.append(f"{mark}{short[name]:<6}{dT.max():9.1e}{dL.max():9.1e}{dq.max():9.1e}{len(t)-1:7d}")
            if cut:
                steps.append(f"{short[name]}{cut}")
        tf = S["t"][-1]
        for ax in self.axes:
            ax.set_xlim(0, tf)
        for ax in (self.ax_T, self.ax_L, self.ax_q):
            ax.set_ylim(floor, 10)
        self.ax_dt.set_yscale("log")
        if hi > 0:
            self.ax_dt.set_ylim(lo / 3, hi * 3)                       # el ruido de redondeo de un dt fijo no se ve
        Legend(self.ax_T, ncol=3, loc="lower right")
        self.table.set_text("\n".join(rows + steps))
        mode = (f"adaptive step, tol = {S['tol']:.0e}" if S["adaptive"] else f"fixed step, dt = {S['dt_used']:.3g}")
        self.message.set_text(f"Same problem for the three schemes  ·  {mode}\n"
                              "The physics keeps 2T, L² and |q| constant: every\n"
                              "curve on this page is pure numerical error.")

    def animated(self):
        return self.cursors

    def update_frame(self, k):
        tp = self.S["t"][k]
        for c in self.cursors:
            c.set_xdata([tp, tp])

    def click_time(self, event):
        return event.xdata if event.inaxes in self.axes else None