"""
Pagina 4 · RICHARDSON Y ORDEN DE CONVERGENCIA  (enunciado 3: estimacion de error por extrapolacion de Richardson)

No conocemos la solucion exacta del solido rigido, pero si sabemos COMO encoge el error de un esquema de orden q
al partir el paso por dos:  E_N ~ C dt^q.  Integrando con N y con 2N pasos:
        U_N - U_2N  =  E_N - E_2N  =  E_N (1 - 2^-q)     ->     E_N  ~  (U_N - U_2N) / (1 - 2^-q)
  - izquierda: log D frente a log N con D = |U_N(tf) - U_2N(tf)|.  Recta de pendiente -q: el orden se LEE en la grafica
  - derecha arriba: error estimado por Richardson frente al error verdadero (referencia muy fina) a lo largo del tiempo
  - derecha abajo: la tabla de la que sale todo: al duplicar N, D se divide por 2^q (2, 4, 16)
"""
import time
from numpy import array, log10, linspace, isfinite
from numpy.linalg import norm
from matplotlib.widgets import Slider

from active.gui_reactive.style import C, scheme_colors, Panel, Legend
from active.numerical_engine.Cauchy_Problem import Cauchy_problem
from active.numerical_engine.Errores_Convergencia import curva_convergencia, tramo_recto, ordenes_locales
from active.numerical_engine.temporal_schemes import RK4
from active.space_physics.eje_intermedio import Rigid_body_problem, Initial_condition

levels = { "Euler": 11, "Crank-Nicolson": 8, "RK4": 8 }      # Euler es barato y llega tarde a la zona asintotica
N0 = 40


class Richardson_page:

    title = "4  Richardson & order"

    def __init__(self, fig, S, schemes, on_change):
        self.fig, self.S, self.schemes = fig, S, schemes
        self.ax_conv = Panel(fig.add_axes([0.055, 0.345, 0.395, 0.505]),
                             "CONVERGENCE  ·  log D  vs  log N     (slope = −order)",
                             r"$\log_{10} N$", r"$\log_{10} D$,    $D = |U_N(t_f) - U_{2N}(t_f)|$")
        self.ax_rich = Panel(fig.add_axes([0.530, 0.610, 0.455, 0.240]),
                             "RICHARDSON ESTIMATE  vs  TRUE ERROR  (selected scheme, current Δt)", "t", "|error|")
        self.ax_rich.set_yscale("log")
        self.table_title = fig.text(0.515, 0.512, "", fontsize=10, color=C["accent"], fontweight="bold")
        self.table = fig.text(0.515, 0.487, "", fontsize=9.5, color=C["text"], va="top", family="monospace",
                              linespacing=1.45)
        self.side = fig.text(0.815, 0.480, "", fontsize=9.2, color=C["muted"], va="top", linespacing=1.55)
        self.status = fig.text(0.055, 0.893, "", fontsize=10, color=C["warn"])
        self.slider_ax = fig.add_axes([0.120, 0.262, 0.200, 0.018])
        self.tf_study = Slider(self.slider_ax, r"study $t_f$", 5., 40., valinit=20., valfmt="%.0f",
                               color=C["accent"], track_color=C["line"], initcolor="none",
                               handle_style={"facecolor": C["text"], "edgecolor": C["accent"], "size": 10})
        self.slider_ax.set_facecolor(C["panel"])
        self.tf_study.label.set_color(C["text"]); self.tf_study.valtext.set_color(C["muted"])
        self.tf_study.on_changed(lambda _: on_change())
        self.axes = [self.ax_conv, self.ax_rich, self.slider_ax]
        self.texts = [self.table_title, self.table, self.side, self.status]
        self.cache = {}

    def set_visible(self, flag):
        for a in self.axes + self.texts:
            a.set_visible(flag)

    # ------------------------------------------------------------ calculos (con cache: tardan unos segundos)
    def study(self):
        """ Curva de convergencia de los tres esquemas para el problema y la condicion inicial actuales """
        S = self.S
        tf = float(self.tf_study.val)
        key = (S["I"], S["Omega"], S["eps"], S["axis"], tf)
        if key not in self.cache:
            F = Rigid_body_problem(S["I"])
            U0 = Initial_condition(S["axis"], S["Omega"], S["eps"])
            result = {}
            for name, scheme in self.schemes.items():
                N, D = curva_convergencia(F, tf, U0, scheme, N0=N0, niveles=levels[name])
                idx, slope, b = tramo_recto(N, D)
                result[name] = dict(N=N, D=D, idx=idx, slope=slope, b=b)
            self.cache = {key: result}
        return self.cache[key]

    def richardson_vs_true(self):
        """ Error de Richardson (con N y 2N) frente al error verdadero (RK4 con 8N pasos) en [0, t_f del estudio] """
        S = self.S
        tf = float(self.tf_study.val)
        scheme, q = S["scheme"], S["scheme"].order
        N = int(min(max(round(tf / S["dt"]), 20), 2000))
        F = Rigid_body_problem(S["I"])
        U0 = Initial_condition(S["axis"], S["Omega"], S["eps"])
        t = linspace(0, tf, N + 1)
        try:
            U1 = Cauchy_problem(F, t, U0, scheme)
            U2 = Cauchy_problem(F, linspace(0, tf, 2*N + 1), U0, scheme)
            Ur = Cauchy_problem(F, linspace(0, tf, 8*N + 1), U0, RK4)
        except ArithmeticError:
            return t, None, None, N
        E_rich = norm(U1 - U2[::2], axis=1) / (1 - 2.**-q)
        E_true = norm(U1 - Ur[::8], axis=1)
        return t, E_rich, E_true, N

    # ------------------------------------------------------------ dibujo
    def refresh(self):
        S = self.S
        self.status.set_text("Computing the convergence study for the three schemes  ...")
        self.status.set_color(C["warn"])
        self.fig.canvas.draw()
        try:
            self.fig.canvas.flush_events()
        except NotImplementedError:
            pass
        clock = time.perf_counter()
        res = self.study()
        t, E_rich, E_true, N = self.richardson_vs_true()
        cpu = time.perf_counter() - clock

        ax = self.ax_conv
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        for name, r in res.items():
            col, sel = scheme_colors[name], name == S["name"]
            ok = isfinite(r["D"]) & (r["D"] > 0)
            x, y = log10(r["N"][ok]), log10(r["D"][ok])
            ax.plot(x, y, "o-", color=col, lw=2.2 if sel else 1.1, ms=6 if sel else 4, alpha=1 if sel else 0.8,
                    label=f"{name}:  slope {r['slope']:.2f}  ->  order {-r['slope']:.2f}")
            xi = log10(r["N"][r["idx"]])
            xx = array([xi[0] - 0.25, xi[-1] + 0.25])
            ax.plot(xx, r["slope"] * xx + r["b"], "--", color=col, lw=1.4, alpha=0.9)
            ax.plot(xi, log10(r["D"][r["idx"]]), "o", ms=10 if sel else 8, mfc="none", mec=col, mew=1.4)
            ax.text(xx[-1] + 0.05, r["slope"] * xx[-1] + r["b"], f"{-r['slope']:.2f}", color=col, fontsize=12,
                    fontweight="bold", va="center")
        ax.relim(); ax.autoscale_view()
        Legend(ax, loc="lower left", fontsize=9.5)

        ax = self.ax_rich
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        col = scheme_colors[S["name"]]
        if E_rich is not None:
            stride = max(1, N // 800)
            ax.plot(t[1::stride], E_rich[1::stride], color=col, lw=2.2, label="Richardson  |U_N − U_2N| / (1 − 2^−q)")
            ax.plot(t[1::stride], E_true[1::stride], color=C["point"], lw=1.3, ls=(0, (4, 3)),
                    label="true error  (reference: RK4, 8N steps)")
            ax.set_xlim(0, t[-1])
            Legend(ax, loc="lower right", fontsize=8.5)
        ax.relim(); ax.autoscale_view()

        r = res[S["name"]]
        p = ordenes_locales(r["D"])
        rows = [f"{'N':>7}{'dt':>9}{'D = |U_N - U_2N|':>18}{'D_k/D_k+1':>11}{'p_k':>7}"]
        for k in range(len(r["N"])):
            ratio = f"{r['D'][k]/r['D'][k+1]:11.2f}" if k + 1 < len(r["D"]) else " " * 11
            pk = f"{p[k]:7.2f}" if k < len(p) else " " * 7
            used = " ◀" if k in r["idx"] else ""
            rows.append(f"{r['N'][k]:7d}{float(self.tf_study.val)/r['N'][k]:9.4f}{r['D'][k]:18.3e}{ratio}{pk}{used}")
        self.table_title.set_text(f"{S['name'].upper()}  ·  the table behind the plot   (theory: ratio 2^q = "
                                  f"{2**S['scheme'].order}, p = {S['scheme'].order})")
        self.table.set_text("\n".join(rows))
        if E_rich is not None:
            ratio = E_rich[1:] / E_true[1:]
            self.ax_rich.text(0.01, 0.95, f"Richardson / true error  =  {ratio.min():.3f} ... {ratio.max():.3f}"
                              f"      (N = {N}, t_f = {self.tf_study.val:.0f})", transform=self.ax_rich.transAxes,
                              fontsize=10, color=C["text"], fontweight="bold", va="top")
        self.side.set_text(
            "THE RECIPE\n"
            "1  integrate with N and 2N\n"
            "2  D = |U_N − U_2N| at t_f\n"
            "    (no exact solution needed)\n"
            "3  halving Δt divides D by 2^q:\n"
            "    p_k = log2(D_k / D_k+1) → q\n"
            "4  error of U_N ≈ D / (1 − 2^−q)\n"
            "◀  points used for the fit")
        self.cpu_text = f"full state (ω and q)  ·  study t_f = {self.tf_study.val:.0f}  ·  CPU {cpu:.1f} s"
        self.status.set_text(self.cpu_text)
        self.status.set_color(C["muted"])

    def animated(self):
        return []

    def update_frame(self, k):
        pass

    def click_time(self, event):
        return None