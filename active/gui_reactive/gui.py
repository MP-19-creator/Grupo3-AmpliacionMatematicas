"""
Capa de VISUALIZACION (gui_reactive).  Es la unica capa que conoce a las otras dos:
toma F de space_physics, la integra con numerical_engine y dibuja.

Cuadro de mando en CUATRO PAGINAS (pestanas arriba, controles comunes abajo):
    1  Attitude & phase space   la caja girando, Poinsot, separatriz, polhoda, w(t)          (enunciado 3.3)
    2  Invariants               deriva de 2T, L^2 y |q| con los tres esquemas y el mismo dt   (enunciado 3.2)
    3  Stability regions        |R(z)| <= 1 con los autovalores z = lambda dt del problema   (enunciado 3)
    4  Richardson & order       log D frente a log N con su pendiente y el error estimado     (enunciado 3)
Los sliders (I1, I2, I3, Omega, dt, ...) son comunes: al moverlos se recalcula y todas las paginas se actualizan.
Esquemas: solo los del enunciado (Euler, Crank-Nicolson, RK4), con paso fijo o adaptativo (Richardson).

Fluidez (blitting): lo estatico se dibuja una vez y se guarda como imagen de fondo; en cada fotograma solo se
restaura ese fondo y se pintan encima las piezas animadas de la pagina visible.
Ejecutar con el depurador de VS Code (F5) es mucho mas lento: usar Ctrl+F5 o 'python PEI1/PEI1.py'.

Atajos:  1 2 3 4  paginas            espacio  play/pausa          <- ->  mover el tiempo
         a  eje de giro inicial      arriba/abajo  esquema         m  paso fijo / adaptativo
         + -  velocidad              v  recolocar camaras 3D       r  reset      f  pantalla completa
         p  medidor de rendimiento   clic en una grafica temporal: saltar a ese instante
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
from numpy import array, argmin, arange, clip, errstate, interp, linspace, searchsorted
from numpy.linalg import norm
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
from matplotlib.widgets import Slider, Button, RadioButtons

from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Cauchy_problem_adaptive, Integration_stopped
from active.numerical_engine.temporal_schemes import Euler, Crank_Nicolson, RK4
from active.space_physics.eje_intermedio import Rigid_body_problem, Initial_condition, Is_physical
from active.gui_reactive.style import C, Presentation_style, Debugger_attached
from active.gui_reactive.page_attitude import Attitude_page, Zero_crossings
from active.gui_reactive.page_invariants import Invariants_page, Drifts
from active.gui_reactive.page_stability import Stability_page
from active.gui_reactive.page_richardson import Richardson_page

schemes = { "Euler": Euler, "Crank-Nicolson": Crank_Nicolson, "RK4": RK4 }     # SOLO los del enunciado
slow = (Crank_Nicolson,)                                  # TUPLA (con coma): implicito con Newton, mas lento
N_max = { "fast": 20000, "slow": 6000 }                   # la GUI no debe congelarse
axes_names = { "Minor axis  I1": 0, "Intermediate  I2": 1, "Major axis  I3": 2 }
modes = ("Fixed Δt", "Adaptive (Richardson)")
N_display = 4000                                          # puntos para animar una solucion adaptativa
N_draw = 2000                                             # puntos dibujados por curva (se integra con todos)
play_seconds = 20                                         # segundos reales que dura t in [0, tf] a velocidad x1


def Integrate(F, tf, U0, scheme, dt, adaptive=False, tol=1e-8):
    """
    Cauchy_problem (o el adaptativo) protegido: si el esquema explota o Newton falla devuelve lo calculado
    y una nota.  Paso fijo: N = tf/dt limitado por N_max.  Devuelve (t, U, nota).
    """
    note = ""
    try:
        with errstate(over="ignore", invalid="ignore"):
            if adaptive:
                t, U = Cauchy_problem_adaptive(F, tf, U0, scheme, tol=tol, dt0=dt,
                                               max_steps=N_max["slow" if scheme in slow else "fast"])
            else:
                N = max(2, int(round(tf / dt)))
                Nm = N_max["slow" if scheme in slow else "fast"]
                if N > Nm:
                    N, note = Nm, f"N capped at {Nm}"
                t = linspace(0, tf, N + 1)
                U = Cauchy_problem(F, t, U0, scheme)
    except Integration_stopped as e:
        U, t = e.U_partial, e.t_partial
        note = (f"step limit reached at t = {t[-1]:.1f}" if "steps" in str(e) else f"stopped at t = {t[-1]:.1f}")
    with errstate(over="ignore", invalid="ignore"):
        bounded = norm(U, axis=1) < 1e6 * norm(U0)        # cortar donde |U| crece 1e6 veces
    if not bounded.all():
        U, t = U[:argmin(bounded)], t[:argmin(bounded)]
        note = f"blows up near t = {t[-1]:.1f}"
    return t, U, note


def build_gui(animate=True):

    Presentation_style()
    S = {"playing": True, "speed": 1.0, "clock": time.perf_counter(), "tp": 0.0, "k": 0, "background": None,
         "closed": False, "show_perf": False, "cost": 0.01, "fps": 30.0, "interval": 16, "version": 0,
         "runs_version": -1, "page": 0}

    fig = plt.figure(figsize=(16, 9))
    try:
        fig.canvas.manager.set_window_title("Intermediate axis theorem  ·  PEI 1")
    except AttributeError:
        pass

    # ------------------------------------------------------------ calculo
    def read_controls():
        S.update(I=(S_I1.val, S_I2.val, S_I3.val), Omega=S_W.val, dt=10**S_dt.val, eps=10**S_eps.val,
                 tf=S_tf.val, tol=10**S_tol.val, name=R_scheme.value_selected,
                 adaptive=R_mode.value_selected == modes[1], axis=axes_names[R_axis.value_selected])
        S["scheme"] = schemes[S["name"]]

    def compute():
        """ Integra el esquema elegido (modelo completo: w y q) y actualiza la pagina visible """
        read_controls()
        warning.set_text("")
        I = S["I"]
        if not I[0] < I[1] < I[2]:
            warning.set_text("I1 < I2 < I3 required  ·  showing the last valid result")
            fig.canvas.draw_idle()
            return
        clock = time.perf_counter()
        tn, Un, note = Integrate(Rigid_body_problem(I), S["tf"], Initial_condition(S["axis"], S["Omega"], S["eps"]),
                                 S["scheme"], S["dt"], S["adaptive"], S["tol"])
        cpu = time.perf_counter() - clock
        if len(Un) < 2:
            warning.set_text("The solution blows up at the first step  ·  reduce Δt")
            fig.canvas.draw_idle()
            return
        notes = [f"{S['name']}: {note}"] if note else []
        if not Is_physical(I):
            notes.append("I1 + I2 < I3: no real body")

        # para animar: la malla de calculo si es fija; si es adaptativa (pasos irregulares) se interpola
        if S["adaptive"]:
            t = linspace(tn[0], tn[-1], max(N_display, len(tn)))
            U = array([interp(t, tn, Un[:, j]) for j in range(Un.shape[1])]).T
        else:
            t, U = tn, Un
        stride = max(1, (len(t) - 1) // N_draw)
        S.update(nodes=(tn, Un), t=t, U=U, cpu=cpu, notes=notes, note=note, k=0, tp=0.0, d=arange(0, len(t), stride),
                 flips=Zero_crossings(t, U[:, S["axis"]]), window=min(15.0, 0.2 * t[-1]),
                 dt_used=(tn[-1] - tn[0]) / (len(tn) - 1), drifts=[d.max() for d in Drifts(Un, I)])
        S["version"] += 1
        notes_text.set_text("\n".join(notes))
        show_page(S["page"], force=True)

    def ensure_runs():
        """ Los tres esquemas con el mismo dt (o la misma tolerancia).  Se calcula solo si una pagina lo pide """
        if S["runs_version"] == S["version"]:
            return
        runs = {}
        U0 = Initial_condition(S["axis"], S["Omega"], S["eps"])
        dt = S["dt_used"] if not S["adaptive"] else S["dt"]
        for name, scheme in schemes.items():
            if scheme is S["scheme"]:
                tn, Un = S["nodes"]
                note = S["note"]
            else:
                tn, Un, note = Integrate(Rigid_body_problem(S["I"]), S["tf"], U0, scheme, dt, S["adaptive"], S["tol"])
            runs[name] = dict(t=tn, U=Un, note=note)
        S["runs"], S["runs_version"] = runs, S["version"]

    def schedule(_=None):
        """ Recalcula 350 ms despues del ultimo cambio (no en cada movimiento del raton) """
        timer.stop(); timer.start()

    # ------------------------------------------------------------ paginas
    def show_page(i, force=False):
        S["page"] = i
        for j, page in enumerate(pages):
            page.set_visible(j == i)
            tabs[j].ax.set_facecolor(C["accent"] if j == i else C["line"])
            tabs[j].color = C["accent"] if j == i else C["line"]
            tabs[j].label.set_color(C["bg"] if j == i else C["text"])
        page = pages[i]
        if "U" in S and (force or getattr(page, "version", -1) != S["version"]):
            if isinstance(page, (Invariants_page, Stability_page)):
                ensure_runs()
            page.refresh()
            page.version = S["version"]
        if "U" in S:
            page.update_frame(S["k"])
        fig.canvas.draw_idle()

    def richardson_changed():
        pages[3].version = -1
        if S["page"] == 3:
            richardson_timer.stop(); richardson_timer.start()

    # ------------------------------------------------------------ animacion
    def frame(_=None):
        if "U" not in S or S["closed"]:
            return
        now = time.perf_counter()
        real_dt = min(now - S["clock"], 0.25)       # tiempo real, no fotogramas (tope: sin saltos tras una pausa)
        S["clock"] = now
        t = S["t"]
        if S["playing"]:
            S["tp"] = (S["tp"] + real_dt * S["speed"] * t[-1] / play_seconds) % t[-1]
        S["k"] = min(int(searchsorted(t, S["tp"])), len(t) - 1)
        pages[S["page"]].update_frame(S["k"])
        if S["show_perf"]:
            perf_text.set_text(f"{S['fps']:4.0f} fps  ·  {1000*S['cost']:4.1f} ms/frame  ·  timer {S['interval']} ms  ·  "
                               f"{matplotlib.get_backend()}  ·  debugger {'ON' if Debugger_attached() else 'off'}")
        try:
            blit()
        except (AttributeError, RuntimeError):      # la ventana se ha cerrado entre dos fotogramas
            on_close()
            return
        cost = time.perf_counter() - now
        S["cost"] = 0.9 * S["cost"] + 0.1 * cost
        S["fps"] = 0.9 * S["fps"] + 0.1 / max(real_dt, 1e-3)
        if S.get("animation") is not None:
            target = int(clip(1250 * S["cost"], 16, 100))      # dejar ~20 % del tiempo libre para eventos
            if abs(target - S["interval"]) > 3:
                S["interval"] = target
                S["animation"].interval = target

    def on_close(_=None):
        S["closed"] = True
        for tm in (S.get("animation"), timer, richardson_timer):
            if tm is not None:
                tm.stop()

    def animated():
        return pages[S["page"]].animated() + [perf_text]

    def paint_animated():
        for a in animated():
            if hasattr(a, "do_3d_projection"):              # colecciones 3D: proyectar con la camara actual
                a.do_3d_projection()
            fig.draw_artist(a)

    band = Bbox([[0.0, 0.255], [1.0, 0.905]])               # franja que cambia en cada fotograma (la pagina)

    def on_draw(_):
        """ Tras cada redibujado completo: guardar el fondo y pintar encima lo animado """
        S["region"] = band.transformed(fig.transFigure)
        S["background"] = fig.canvas.copy_from_bbox(S["region"])
        paint_animated()

    def blit():
        if S["background"] is None:
            return
        fig.canvas.restore_region(S["background"])
        paint_animated()
        fig.canvas.blit(S["region"])

    def render():
        """ Imagen RGBA del estado actual (capturas sin pantalla y pruebas) """
        fig.canvas.draw()
        blit()
        return array(fig.canvas.buffer_rgba())

    def goto(tp):
        if "U" not in S:
            return
        S["tp"] = float(clip(tp, 0, S["t"][-1]))
        S["k"] = min(int(searchsorted(S["t"], S["tp"])), len(S["t"]) - 1)
        pages[S["page"]].update_frame(S["k"])
        blit()

    # ------------------------------------------------------------ teclado y raton
    def play_pause(_=None):
        S["playing"] = not S["playing"]

    def reset(_=None):
        for s in (S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf, S_tol):
            s.reset()
        compute()

    def on_key(event):
        key, labels = event.key, list(schemes)
        if key in ("1", "2", "3", "4"):
            show_page(int(key) - 1)
        elif key == " ":
            play_pause()
        elif key in ("left", "right") and "t" in S:
            goto(S["tp"] + (0.04 if key == "right" else -0.04) * S["t"][-1])
        elif key == "a":
            R_axis.set_active((axes_names[R_axis.value_selected] + 1) % 3)
        elif key in ("up", "down"):
            i = labels.index(R_scheme.value_selected)
            R_scheme.set_active((i + (1 if key == "down" else -1)) % len(labels))
        elif key == "m":
            R_mode.set_active(1 - modes.index(R_mode.value_selected))
        elif key == "v":
            pages[0].reset_views(); fig.canvas.draw_idle()
        elif key in ("+", "=", "plus"):
            S["speed"] = min(8.0, S["speed"] * 2)
        elif key in ("-", "minus"):
            S["speed"] = max(0.125, S["speed"] / 2)
        elif key == "r":
            reset()
        elif key == "p":
            S["show_perf"] = not S["show_perf"]
            if not S["show_perf"]:
                perf_text.set_text("")

    def on_click(event):
        if event.button == 1 and event.xdata is not None:
            tp = pages[S["page"]].click_time(event)
            if tp is not None:
                goto(tp)

    # ------------------------------------------------------------ cabecera y pestanas
    fig.text(0.018, 0.962, "The intermediate axis theorem", fontsize=21, fontweight="bold", va="center")
    fig.text(0.018, 0.926, r"Torque-free rigid body   $I\,\dot{\omega} + \omega \times I\omega = 0$"
             r"   ·   $I_1 < I_2 < I_3$   ·   Euler · Crank-Nicolson · RK4", fontsize=10.5, color=C["muted"],
             va="center")
    warning = fig.text(0.40, 0.905, "", fontsize=11, color=C["warn"], va="center", fontweight="bold")
    perf_text = fig.text(0.985, 0.903, "", fontsize=8.5, color=C["warn"], ha="right", animated=True)
    if Debugger_attached():
        fig.text(0.985, 0.903, "Debugger attached: animation is slower  ·  run with Ctrl+F5 or 'python PEI1/PEI1.py'",
                 fontsize=9, color=C["warn"], ha="right")

    pages = [Attitude_page(fig, S), Invariants_page(fig, S), Stability_page(fig, S),
             Richardson_page(fig, S, schemes, lambda: richardson_changed())]
    tabs = []
    for i, page in enumerate(pages):
        b = Button(fig.add_axes([0.418 + 0.143*i, 0.935, 0.137, 0.046]), page.title, color=C["line"],
                   hovercolor="#30456E")
        b.label.set_fontsize(11.5); b.label.set_fontweight("bold"); b.label.set_color(C["text"])
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        b.on_clicked(lambda _, i=i: show_page(i))
        tabs.append(b)

    # ------------------------------------------------------------ banda de controles (comun a todas las paginas)
    fig.patches.append(FancyBboxPatch((0.012, 0.012), 0.976, 0.232, boxstyle="round,pad=0,rounding_size=0.006",
                                      transform=fig.transFigure, fc=C["panel"], ec=C["line"], lw=0.8, zorder=-1))
    for x, title in ((0.028, "BODY"), (0.300, "NUMERICS"), (0.535, "SCHEME"), (0.665, "INITIAL SPIN"),
                     (0.815, "KEYS")):
        fig.text(x, 0.220, title, fontsize=9.5, fontweight="bold", color=C["accent"])

    def slider(x, y, w, label, a, b, v, fmt="%.2f"):
        s = Slider(fig.add_axes([x, y, w, 0.018]), label, a, b, valinit=v, valfmt=fmt, color=C["accent"],
                   track_color=C["line"], initcolor="none",
                   handle_style={"facecolor": C["text"], "edgecolor": C["accent"], "size": 11})
        s.ax.set_facecolor(C["panel"])
        s.label.set_color(C["text"]); s.label.set_fontsize(11)
        s.valtext.set_color(C["muted"]); s.valtext.set_fontsize(10)
        s.on_changed(schedule)
        return s

    S_I1  = slider(0.075, 0.183, 0.165, r"$I_1$", 0.2, 5., 1.)
    S_I2  = slider(0.075, 0.148, 0.165, r"$I_2$", 0.2, 5., 2.)
    S_I3  = slider(0.075, 0.113, 0.165, r"$I_3$", 0.2, 5., 3.)
    S_W   = slider(0.075, 0.078, 0.165, r"$\Omega$", 0.1, 3., 1.)
    S_eps = slider(0.075, 0.043, 0.165, r"$\log_{10}\varepsilon$", -8., -1., -3.)
    S_dt  = slider(0.355, 0.183, 0.120, r"$\log_{10}\Delta t$", -3., -0.3, -1.7)
    S_tf  = slider(0.355, 0.148, 0.120, r"$t_f$", 10., 150., 80., "%.0f")
    S_tol = slider(0.355, 0.113, 0.120, r"$\log_{10}$tol", -11., -3., -6.)

    def button(x, y, label, callback):
        b = Button(fig.add_axes([x, y, 0.075, 0.040]), label, color=C["line"], hovercolor="#30456E")
        b.label.set_color(C["text"]); b.label.set_fontsize(10)
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        b.on_clicked(callback)
        return b

    B_play  = button(0.300, 0.030, "Play / Pause", play_pause)
    B_reset = button(0.385, 0.030, "Reset", reset)

    def radio(rect, labels, active):
        ax = fig.add_axes(rect); ax.set_facecolor(C["panel"])
        for sp in ax.spines.values():
            sp.set_visible(False)
        r = RadioButtons(ax, labels, active=active, activecolor=C["accent"],
                         radio_props={"edgecolor": C["muted"], "s": 70})
        for txt in r.labels:
            txt.set_color(C["text"]); txt.set_fontsize(10.5)
        r.on_clicked(schedule)
        return r

    R_scheme = radio([0.530, 0.105, 0.125, 0.105], list(schemes), 2)      # 2 = "RK4" (indices desde 0)
    R_mode   = radio([0.530, 0.020, 0.125, 0.075], list(modes), 0)
    R_axis   = radio([0.660, 0.105, 0.140, 0.105], list(axes_names), 1)
    notes_text = fig.text(0.667, 0.085, "", fontsize=9, color=C["warn"], va="top", linespacing=1.5)
    fig.text(0.815, 0.200, "1 2 3 4    pages\nspace       play / pause\n← →         move in time\n"
             "↑ ↓          scheme\nm             fixed / adaptive step\na              spin axis\n"
             "+ −          speed      r  reset\nv  3D views    f  full screen",
             fontsize=8.8, color=C["muted"], va="top", linespacing=1.45)

    timer = fig.canvas.new_timer(interval=350)
    timer.single_shot = True
    timer.add_callback(compute)
    richardson_timer = fig.canvas.new_timer(interval=500)
    richardson_timer.single_shot = True
    richardson_timer.add_callback(lambda: show_page(3))
    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("draw_event", on_draw)
    fig.canvas.mpl_connect("close_event", on_close)

    for j, page in enumerate(pages):
        page.set_visible(j == 0)
    compute()
    S["animation"] = None
    if animate:                                     # ~60 Hz; cada tic solo repinta lo animado
        S["animation"] = fig.canvas.new_timer(interval=16)
        S["animation"].add_callback(frame)
        S["animation"].start()

    # se devuelven los controles para poder probarlos sin pantalla
    S.update(fig=fig, compute=compute, frame=frame, goto=goto, render=render, show_page=show_page, pages=pages,
             warning=warning, sliders=(S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf, S_tol), R_scheme=R_scheme,
             R_mode=R_mode, R_axis=R_axis, tabs=tabs, buttons=(B_play, B_reset), ensure_runs=ensure_runs)
    return S


if __name__ == "__main__":

    gui = build_gui()
    try:                                                      # abrir maximizada (TkAgg / Qt)
        manager = plt.get_current_fig_manager()
        if hasattr(manager, "window") and hasattr(manager.window, "state"):
            manager.window.state("zoomed")
        elif hasattr(manager, "window") and hasattr(manager.window, "showMaximized"):
            manager.window.showMaximized()
    except Exception:
        pass
    plt.show()