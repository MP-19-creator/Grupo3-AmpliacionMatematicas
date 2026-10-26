"""
Capa de VISUALIZACION (gui_reactive).  Es la unica capa que conoce a las otras dos:
toma F de space_physics, la integra con numerical_engine y dibuja.

Cuadro de mando con estilo de presentacion: tema oscuro, animacion a velocidad de tiempo real
(independiente de los fotogramas por segundo) y atajos de teclado para la demo en directo.

Fluidez (blitting): redibujar toda la figura cuesta ~0.3 s.  Por eso lo estatico (ejes, elipsoides,
textos, controles) se dibuja una vez y se guarda como imagen de fondo; en cada fotograma solo se
restaura ese fondo y se pintan encima las piezas marcadas como animadas (set_animated(True)).
Solo se copia a la pantalla la franja de las graficas (no la banda de controles), y el temporizador
se adapta al coste real de cada fotograma para no saturar la cola de eventos en ordenadores lentos.
Ejecutar con el depurador de VS Code (F5) es mucho mas lento: usar Ctrl+F5 o 'python main.py'.

Atajos:  espacio  play/pausa      <- ->  mover el tiempo     1 2 3  eje de giro inicial
         arriba/abajo  esquema    c  comparar esquemas       v  recolocar las camaras 3D
         + -  velocidad           r  reset                   f  pantalla completa
         p  medidor de rendimiento (fps, ms por fotograma, backend, depurador)
         clic en las graficas de la derecha: saltar a ese instante
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
from numpy import array, abs, maximum, sqrt, errstate, argmin, linspace, arange, searchsorted, clip, cross
from numpy.linalg import norm
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
from matplotlib.widgets import Slider, Button, RadioButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Integration_stopped
from active.numerical_engine.Temporal_Schemes import Euler, Euler_implicit, Crank_Nicolson, RK4
from active.space_physics.eje_intermedio import (Rigid_body_problem, Initial_condition, Linear_eigenvalues,
    Kinetic_energy_2T, Angular_momentum_L2, Rotation_matrix, Energy_ellipsoid, Momentum_ellipsoid,
    Separatrix, Side_of_separatrix, Polhode_period, Is_physical, Box_dimensions)

schemes = { "Euler": Euler, "Crank-Nicolson": Crank_Nicolson,"RK4": RK4 }
slow = (Crank_Nicolson,)                   # TUPLA: los implicitos (Newton) son lentos
tol_adaptive = 1e-9
N_max = { "fast": 20000, "slow": 3000 }                   # la GUI no debe congelarse
axes_names = { "Minor axis  I1": 0, "Intermediate  I2": 1, "Major axis  I3": 2 }
floor = 1e-17                                             # suelo para el log de derivas nulas
N_draw = 2000                                             # puntos dibujados por curva (se integra con todos)
play_seconds = 20                                         # segundos reales que dura t in [0, tf] a velocidad x1

# Paleta: ejes del cuerpo e1 rojo, e2 verde, e3 azul (los mismos colores en toda la presentacion)
C = dict(bg="#0B1220", panel="#121B2E", line="#24324D", text="#E8EEF7", muted="#8B9BB8",
         accent="#5AA9FF", gold="#D4A246", e=("#FF6B5A", "#3DDC84", "#5AA9FF"),
         energy="#5AA9FF", momentum="#FFB347", polhode="#F4F7FB", separatrix="#FF4D6D", point="#FF4FD8",
         ok="#3DDC84", bad="#FF4D6D", warn="#FFC145", drift=("#C792EA", "#FFB347", "#8B9BB8"))
scheme_colors = { "Euler": "#FF8A5B", "Crank-Nicolson": "#4FD1C5","RK4": "#F4F7FB" }
light = array([0.35, -0.55, 0.76]) / norm([0.35, -0.55, 0.76])     # direccion de la luz que ilumina la caja


def Integrate(F, t, U0, scheme):
    """ Cauchy_problem protegido: si el esquema explota o Newton falla,
        devuelve lo calculado (corta donde |U| crece 1e6 veces) """
    try:
        with errstate(over="ignore", invalid="ignore"):
          U = Cauchy_problem(F, t, U0, scheme)
    except Integration_stopped as e:
        U = e.U_partial
        if e.t_partial is not None:
            t = e.t_partial
    with errstate(over="ignore", invalid="ignore"):
        bounded = norm(U, axis=1) < 1e6 * norm(U0)
    if not bounded.all():
        U = U[:argmin(bounded)]
    return t[:len(U)], U


def Zero_crossings(t, x):
    """ Instantes en que x cambia de signo (interpolacion lineal entre nodos) """
    i = ((x[1:] * x[:-1]) < 0).nonzero()[0]
    return t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])


def _font(candidates):
    available = {f.name for f in font_manager.fontManager.ttflist}
    return next((c for c in candidates if c in available), "DejaVu Sans")


def Presentation_style():
    """ Tema oscuro y teclas libres para los atajos (se quitan los atajos de matplotlib que chocan) """
    plt.rcParams.update({
        "toolbar": "None",
        "font.family": _font(["Segoe UI", "Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]),
        "mathtext.fontset": "stixsans",
        "figure.facecolor": C["bg"], "axes.facecolor": C["bg"], "savefig.facecolor": C["bg"],
        "axes.edgecolor": C["line"], "axes.labelcolor": C["muted"], "text.color": C["text"],
        "xtick.color": C["muted"], "ytick.color": C["muted"], "axes.titlecolor": C["muted"],
        "grid.color": C["line"], "grid.alpha": 0.7, "grid.linewidth": 0.6,
        "keymap.back": [], "keymap.forward": [], "keymap.home": ["h", "home"], "keymap.pan": [],
        "keymap.zoom": [], "keymap.grid": [], "keymap.grid_minor": [], "keymap.xscale": [],
        "keymap.yscale": [], "keymap.quit": ["ctrl+w", "cmd+w"], "keymap.save": ["ctrl+s"] })


def Debugger_attached():
    """ True si se ejecuta bajo un depurador (VS Code con F5 carga debugpy/pydevd) """
    return sys.gettrace() is not None or any(m in sys.modules for m in ("pydevd", "debugpy"))


def build_gui(animate=True):

    Presentation_style()
    S = {"playing": True, "speed": 1.0, "clock": time.perf_counter(), "tp": 0.0, "background": None,
         "closed": False, "show_perf": False, "cost": 0.01, "fps": 30.0, "interval": 16}

    # ------------------------------------------------------------ calculo
    def compute():
        I = (S_I1.val, S_I2.val, S_I3.val)
        Omega, dt, eps, tf = S_W.val, 10**S_dt.val, 10**S_eps.val, S_tf.val
        name = R_scheme.value_selected
        scheme = schemes[name]
        axis = axes_names[R_axis.value_selected]
        warning.set_text("")

        if not I[0] < I[1] < I[2]:
            warning.set_text("I1 < I2 < I3 required  ·  showing the last valid result")
            fig.canvas.draw_idle()
            return

        notes = []
        N = max(2, int(round(tf/dt)))
        Nm = N_max["slow" if scheme in slow else "fast"]
        if N > Nm:
            N = Nm
            notes.append(f"N capped at {Nm}  (dt = {tf/N:.3g})")
        t = linspace(0, tf, N+1)

        clock = time.perf_counter()
        t, U = Integrate(Rigid_body_problem(I), t, Initial_condition(axis, Omega, eps), scheme)
        S["cpu"] = time.perf_counter() - clock
        if len(U) < N+1:
            notes.append(f"{name} blows up near t = {t[-1]:.1f}")
        if len(U) < 2:
            warning.set_text("The solution blows up at the first step  ·  reduce dt")
            fig.canvas.draw_idle()
            return
        if not Is_physical(I):
            notes.append("I1 + I2 < I3: no real body")

        stride = max(1, (len(t) - 1) // N_draw)
        S.update(I=I, t=t, U=U, scheme=scheme, name=name, axis=axis, notes=notes, k=0, tp=0.0,
                 d=arange(0, len(t), stride), flips=Zero_crossings(t, U[:, axis]),
                 window=min(15.0, 0.2 * t[-1]))
        for line in S.get("comparison", []):
            line.remove()
        S["comparison"] = []
        draw_phase_space(); draw_body(); draw_time_series(); write_info()
        update_frame(0)
        fig.canvas.draw_idle()

    def schedule(_=None):
        """ Recalcula 350 ms despues del ultimo cambio (no en cada movimiento del raton) """
        timer.stop(); timer.start()

    def compare(_=None):
        """ Deriva de 2T con TODOS los esquemas (modelo de 3 variables, mismo dt) """
        if "U" not in S:
            return
        I, w0 = S["I"], S["U"][0, 0:3]
        N = min(len(S["t"]) - 1, N_max["slow"])
        t = linspace(0, S["t"][-1] * N / (len(S["t"]) - 1), N+1)
        for line in S["comparison"]:
            line.remove()
        S["comparison"] = []
        for name, scheme in schemes.items():
            if scheme is S["scheme"]:
                continue
            t1, U = Integrate(Rigid_body_problem(I, attitude=False), t, w0, scheme)
            d = maximum(abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(w0, I) - 1), floor)
            S["comparison"] += ax_drift.semilogy(t1, d, lw=1.0, color=scheme_colors[name], label=name)
        ax_drift.set_ylim(floor, 10)
        Legend(ax_drift, ncol=2)
        fig.canvas.draw_idle()

    # ------------------------------------------------------------ dibujo (una vez por calculo)
    def draw_phase_space():
        I, U, d = S["I"], S["U"], S["d"]
        T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
        ax_phase.clear(); ax_phase.set_axis_off()
        R = sqrt(T2 / I[0]) * 1.05
        for i, name in enumerate((r"$\omega_1$", r"$\omega_2$", r"$\omega_3$")):    # ejes cuerpo, sin cajas ni numeros
            e = [0, 0, 0]; e[i] = R
            ax_phase.plot([-e[0], e[0]], [-e[1], e[1]], [-e[2], e[2]], color=C["e"][i], lw=0.9, alpha=0.55)
            ax_phase.text(*(1.1 * array(e)), name, color=C["e"][i], fontsize=13, ha="center", va="center")
        ax_phase.plot_wireframe(*Energy_ellipsoid(I, T2, 36), color=C["energy"], lw=0.35, alpha=0.35,
                                rcount=14, ccount=14)
        ax_phase.plot_wireframe(*Momentum_ellipsoid(I, L2, 36), color=C["momentum"], lw=0.35, alpha=0.25,
                                rcount=14, ccount=14)
        for curve in Separatrix(I, T2):
            ax_phase.plot(*curve, color=C["separatrix"], lw=1.6, ls=(0, (5, 4)))
        ax_phase.plot(U[d, 0], U[d, 1], U[d, 2], color=C["polhode"], lw=0.8, alpha=0.35)
        S["recent"], = ax_phase.plot([], [], [], color=C["polhode"], lw=2.4, solid_capstyle="round")
        S["glow"], = ax_phase.plot([], [], [], "o", color=C["point"], ms=17, alpha=0.25, mew=0)
        S["point"], = ax_phase.plot([], [], [], "o", color=C["point"], ms=7, mec="white", mew=0.8)
        for a in (S["recent"], S["glow"], S["point"]):
            a.set_animated(True)
        ax_phase.set_xlim(-R, R); ax_phase.set_ylim(-R, R); ax_phase.set_zlim(-R, R)
        ax_phase.set_box_aspect((1, 1, 1), zoom=1.2)
        handles = [plt.Line2D([], [], color=C["energy"], lw=2, label="2T ellipsoid"),
                   plt.Line2D([], [], color=C["momentum"], lw=2, label=r"$L^2$ ellipsoid"),
                   plt.Line2D([], [], color=C["separatrix"], lw=2, ls=(0, (5, 4)), label="separatrix"),
                   plt.Line2D([], [], color=C["polhode"], lw=2, label="polhode (numerical)")]
        ax_phase.legend(handles=handles, loc="lower left", fontsize=8, frameon=False, labelcolor=C["muted"],
                        bbox_to_anchor=(0.0, 0.02))

    def draw_body():
        I, U = S["I"], S["U"]
        a, b, c = Box_dimensions(I)
        side = max(a, b, c)
        a, b, c = [max(s/side, 0.04) for s in (a, b, c)]          # placa plana: grosor minimo
        V = array([[sx*a/2, sy*b/2, sz*c/2] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
        normals = []
        for f in faces:                                            # normal exterior de cada cara
            n = cross(V[f[1]] - V[f[0]], V[f[2]] - V[f[0]])
            n = n / norm(n)
            normals.append(n if n @ V[f].mean(axis=0) > 0 else -n)
        S.update(vertices=V, faces=faces, normals=array(normals))

        ax_body.clear(); ax_body.set_axis_off(); ax_body.set_facecolor(C["bg"])
        S["trail"] = Line3DCollection([[(0, 0, 0), (0, 0, 0)]], linewidths=2.2, capstyle="round")
        ax_body.add_collection3d(S["trail"])
        S["box"] = Poly3DCollection([], edgecolor="#3A2A0C", linewidths=0.6)
        ax_body.add_collection3d(S["box"])
        S["arrows"] = [ax_body.plot([], [], [], color=C["e"][i], lw=3, solid_capstyle="round")[0] for i in range(3)]
        S["tips"] = [ax_body.plot([], [], [], "o", color=C["e"][i], ms=6)[0] for i in range(3)]
        L = Rotation_matrix(U[0, 3:7]) @ (array(I) * U[0, 0:3])
        L = 0.82 * L / norm(L)
        ax_body.plot([0, L[0]], [0, L[1]], [0, L[2]], color=C["text"], lw=1.4, ls=(0, (4, 3)))
        ax_body.text(*(1.1 * L), "L", color=C["text"], fontsize=13, fontweight="bold", ha="center", va="center")
        for lim in (ax_body.set_xlim, ax_body.set_ylim, ax_body.set_zlim):
            lim(-0.75, 0.75)
        ax_body.set_box_aspect((1, 1, 1), zoom=1.15)
        ax_body.view_init(elev=18, azim=-55)
        for a in (S["trail"], S["box"], *S["arrows"], *S["tips"]):
            a.set_animated(True)

    def draw_time_series():
        I, t, U, d = S["I"], S["t"], S["U"], S["d"]
        for i in range(3):
            lines_w_bg[i].set_data(t[d], U[d, i])
        dT = abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(U[0], I) - 1)
        dL = abs(Angular_momentum_L2(U, I) / Angular_momentum_L2(U[0], I) - 1)
        dq = abs((U[:, 3:7]**2).sum(axis=1) - 1)
        S["drifts"] = dT.max(), dL.max(), dq.max()
        line_T.set_data(t[d], maximum(dT[d], floor)); line_L.set_data(t[d], maximum(dL[d], floor))
        line_q.set_data(t[d], maximum(dq[d], floor))
        ax_w.set_xlim(0, t[-1])
        m = abs(U[:, 0:3]).max() * 1.15
        ax_w.set_ylim(-m, m)
        ax_drift.set_ylim(floor, max(10, 2 * max(S["drifts"])))
        Legend(ax_drift, ncol=3)
        ax_w.set_title(f"ANGULAR VELOCITY  ·  body frame  ·  {S['name']}", loc="left", fontsize=9)

    def write_info():
        I, t, U, axis = S["I"], S["t"], S["U"], S["axis"]
        T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
        lam = Linear_eigenvalues(I, axis, U[0, axis])[0]
        real = abs(lam.imag) < 1e-14
        side = {1: "around I3", -1: "around I1", 0: "separatrix"}[Side_of_separatrix(I, T2, L2)]
        c = Zero_crossings(t, U[:, 1])
        measured = f"{c[2] - c[0]:.3f}" if len(c) >= 3 else "not reached"
        rows = [ ("Linearised eigenvalue", f"±{abs(lam):.4f}{'' if real else ' i'}"),
                 ("Polhode  (L²/2T vs I₂)", f"{side}  ({L2/T2:.4f})"),
                 ("Period  exact 4K(k)/ν", f"{Polhode_period(I, T2, L2):.3f}"),
                 ("Period  measured", measured),
                 ("Max drift  2T  ·  L²", f"{S['drifts'][0]:.1e}  ·  {S['drifts'][1]:.1e}"),
                 ("Max drift  |q|", f"{S['drifts'][2]:.1e}"),
                 ("dt  ·  N  ·  CPU", f"{(t[-1]-t[0])/(len(t)-1):.3g}  ·  {len(t)-1}  ·  {S['cpu']:.2f} s") ]
        info_labels.set_text("\n".join(r[0] for r in rows))
        info.set_text("\n".join(r[1] for r in rows))
        notes.set_text("\n".join(S["notes"]))
        badge.set_text(f"{'UNSTABLE  ·  saddle point' if real else 'STABLE  ·  centre'}     "
                       f"λ = ±{abs(lam):.3f}{'' if real else ' i'}")
        badge.get_bbox_patch().set_facecolor(C["bad"] if real else C["ok"])
        flips_label.set_color(C["e"][axis]); flips.set_color(C["e"][axis])

    # ------------------------------------------------------------ animacion (cada fotograma)
    def update_frame(k):
        t, U, d, w = S["t"], S["U"], S["d"], S["window"]
        tp = t[k]
        # espacio de fases: punto, halo y tramo reciente de la polhoda
        S["point"].set_data_3d(U[k:k+1, 0], U[k:k+1, 1], U[k:k+1, 2])
        S["glow"].set_data_3d(U[k:k+1, 0], U[k:k+1, 1], U[k:k+1, 2])
        j0 = searchsorted(t, tp - 0.35 * w)
        seg = U[j0:k+1:max(1, (k - j0) // 120 or 1)]
        S["recent"].set_data_3d(seg[:, 0], seg[:, 1], seg[:, 2])
        # cuerpo
        move_body(k)
        # series temporales: se dibujan hasta el instante actual
        kd = searchsorted(d, k, side="right")
        for i in range(3):
            lines_w[i].set_data(t[d[:kd]], U[d[:kd], i])
        cursor_w.set_xdata([tp, tp]); cursor_d.set_xdata([tp, tp])
        clock_text.set_text(f"t = {tp:.1f}")
        flips.set_text(f"{searchsorted(S['flips'], tp)}")
        speed_text.set_text(f"speed ×{S['speed']:g}" + ("" if S["playing"] else "   paused"))
        if S["show_perf"]:
            perf_text.set_text(f"{S['fps']:4.0f} fps  ·  {1000*S['cost']:4.1f} ms/frame  ·  timer {S['interval']} ms  ·  "
                               f"{matplotlib.get_backend()}  ·  debugger {'ON' if Debugger_attached() else 'off'}")

    def move_body(k):
        U, axis = S["U"], S["axis"]
        R = Rotation_matrix(U[k, 3:7])
        v = S["vertices"] @ R.T
        S["box"].set_verts([[v[i] for i in face] for face in S["faces"]])
        shade = 0.28 + 0.72 * clip((S["normals"] @ R.T) @ light, 0, 1)
        gold = array(to_rgb(C["gold"]))
        S["box"].set_facecolor([(*(gold * s), 1.0) for s in shade])
        for i in range(3):
            e = 0.78 * R[:, i]
            S["arrows"][i].set_data_3d([0, e[0]], [0, e[1]], [0, e[2]])
            S["tips"][i].set_data_3d([e[0]], [e[1]], [e[2]])
        # estela de la punta del eje de giro inicial durante la ultima ventana de tiempo
        t = S["t"]
        idx = searchsorted(t, linspace(max(0., t[k] - S["window"]), t[k], 60)).clip(0, len(t) - 1)
        tips = array([0.78 * Rotation_matrix(U[j, 3:7])[:, axis] for j in idx])
        S["trail"].set_segments([tips[i:i+2] for i in range(len(tips) - 1)])
        col = array(to_rgb(C["e"][axis]))
        S["trail"].set_color([(*col, 0.9 * (i + 1) / len(tips)) for i in range(len(tips) - 1)])

    def frame(_=None):
        if "U" not in S or S["closed"]:
            return ()
        now = time.perf_counter()
        real_dt = min(now - S["clock"], 0.25)       # tiempo real, no fotogramas (tope: sin saltos tras una pausa)
        S["clock"] = now
        t = S["t"]
        if S["playing"]:
            S["tp"] = (S["tp"] + real_dt * S["speed"] * t[-1] / play_seconds) % t[-1]
        S["k"] = min(int(searchsorted(t, S["tp"])), len(t) - 1)
        update_frame(S["k"])
        try:
            blit()
        except (AttributeError, RuntimeError):      # la ventana se ha cerrado entre dos fotogramas
            on_close()
            return ()
        # medida del rendimiento y temporizador adaptativo
        cost = time.perf_counter() - now
        S["cost"] = 0.9 * S["cost"] + 0.1 * cost
        S["fps"] = 0.9 * S["fps"] + 0.1 / max(real_dt, 1e-3)
        if S.get("animation") is not None:
            target = int(clip(1250 * S["cost"], 16, 100))          # dejar ~20 % del tiempo libre para eventos
            if abs(target - S["interval"]) > 3:
                S["interval"] = target
                S["animation"].interval = target
        return ()

    def on_close(_=None):
        S["closed"] = True
        if S.get("animation") is not None:
            S["animation"].stop()

    def animated():
        """ Piezas que cambian en cada fotograma (el resto va en la imagen de fondo) """
        if "box" not in S:
            return []
        return [S["trail"], S["box"], *S["arrows"], *S["tips"], S["recent"], S["glow"], S["point"],
                *lines_w, cursor_w, cursor_d, clock_text, flips, speed_text, perf_text]

    def paint_animated():
        for a in animated():
            if hasattr(a, "do_3d_projection"):              # colecciones 3D: proyectar con la camara actual
                a.do_3d_projection()
            fig.draw_artist(a)

    # franja de la figura que cambia en cada fotograma: graficas y contador (no la banda de controles)
    band = Bbox([[0.0, 0.275], [1.0, 0.905]])

    def on_draw(_):
        """ Tras cada redibujado completo (calculo, raton, ventana): guardar el fondo y pintar lo animado """
        S["region"] = band.transformed(fig.transFigure)     # en pixeles, con el tamano actual de la ventana
        S["background"] = fig.canvas.copy_from_bbox(S["region"])
        paint_animated()

    def blit():
        if S["background"] is None:
            return
        fig.canvas.restore_region(S["background"])
        paint_animated()
        fig.canvas.blit(S["region"])

    def render():
        """ Imagen RGBA del estado actual (capturas y video sin pantalla) """
        fig.canvas.draw()
        blit()
        return array(fig.canvas.buffer_rgba())

    def goto(tp):
        """ Salta al instante tp (clic en las graficas, flechas, pruebas) """
        if "U" not in S:
            return
        S["tp"] = float(clip(tp, 0, S["t"][-1]))
        S["k"] = min(int(searchsorted(S["t"], S["tp"])), len(S["t"]) - 1)
        update_frame(S["k"])
        blit()

    def play_pause(_=None):
        S["playing"] = not S["playing"]

    def reset(_=None):
        for s in (S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf):
            s.reset()
        compute()

    def on_key(event):
        key, labels = event.key, list(schemes)
        if key == " ":
            play_pause()
        elif key in ("left", "right") and "t" in S:
            goto(S["tp"] + (0.04 if key == "right" else -0.04) * S["t"][-1])
        elif key in ("1", "2", "3"):
            R_axis.set_active(int(key) - 1)
        elif key in ("up", "down"):
            i = labels.index(R_scheme.value_selected)
            R_scheme.set_active((i + (1 if key == "down" else -1)) % len(labels))
        elif key == "c":
            compare()
        elif key == "v":
            ax_body.view_init(elev=18, azim=-55); ax_phase.view_init(elev=30, azim=-60)
            fig.canvas.draw_idle()
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
        if event.inaxes in (ax_w, ax_drift) and event.xdata is not None and event.button == 1:
            goto(event.xdata)

    # ------------------------------------------------------------ composicion (coordenadas de figura)
    fig = plt.figure(figsize=(16, 9))
    try:
        fig.canvas.manager.set_window_title("Intermediate axis theorem  ·  PEI 1")
    except AttributeError:
        pass

    # cabecera
    fig.text(0.018, 0.958, "The intermediate axis theorem", fontsize=22, fontweight="bold", va="center")
    fig.text(0.018, 0.918, r"Torque-free rigid body   $I\,\dot{\omega} + \omega \times I\omega = 0$"
             r"   ·   $I_1 < I_2 < I_3$   ·   attitude with quaternions", fontsize=10.5, color=C["muted"], va="center")
    badge = fig.text(0.982, 0.955, "", fontsize=13, fontweight="bold", ha="right", va="center", color=C["bg"],
                     bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.8", fc=C["ok"], ec="none"))
    warning = fig.text(0.5, 0.955, "", fontsize=12, color=C["warn"], ha="center", va="center", fontweight="bold")

    # paneles
    ax_body  = fig.add_axes([0.000, 0.285, 0.345, 0.600], projection="3d")
    ax_phase = fig.add_axes([0.330, 0.285, 0.345, 0.600], projection="3d")
    ax_w     = fig.add_axes([0.715, 0.625, 0.268, 0.225])
    ax_drift = fig.add_axes([0.715, 0.345, 0.268, 0.225], sharex=ax_w)
    fig.text(0.022, 0.868, "ATTITUDE  ·  inertial frame", fontsize=9, color=C["muted"])
    fig.text(0.350, 0.868, "PHASE SPACE  ·  body frame  (Poinsot)", fontsize=9, color=C["muted"])

    flips_label = fig.text(0.022, 0.415, "FLIPS", fontsize=9, fontweight="bold")
    flips = fig.text(0.020, 0.345, "0", fontsize=40, fontweight="bold", animated=True)
    clock_text = fig.text(0.075, 0.372, "", fontsize=16, color=C["text"], animated=True)
    speed_text = fig.text(0.075, 0.345, "", fontsize=9, color=C["muted"], animated=True)
    perf_text = fig.text(0.982, 0.893, "", fontsize=8.5, color=C["warn"], ha="right", animated=True)
    if Debugger_attached():
        fig.text(0.982, 0.905, "Debugger attached: animation is slower  ·  run with Ctrl+F5 or 'python main.py'",
                 fontsize=9, color=C["warn"], ha="right", va="bottom")

    lines_w_bg = [ax_w.plot([], [], color=C["e"][i], lw=1.0, alpha=0.22)[0] for i in range(3)]
    lines_w = [ax_w.plot([], [], color=C["e"][i], lw=1.8, label=fr"$\omega_{i+1}$")[0] for i in range(3)]
    Legend = lambda ax, ncol: ax.legend(loc="lower right", fontsize=8, ncol=ncol, facecolor=C["panel"],
                                        edgecolor=C["line"], labelcolor=C["text"], framealpha=0.9)
    Legend(ax_w, 3); ax_w.grid(True)
    cursor_w = ax_w.axvline(0, color=C["text"], lw=0.9, alpha=0.8, animated=True)
    for line in lines_w:
        line.set_animated(True)
    line_T, = ax_drift.semilogy([], [], color=C["drift"][0], lw=1.6, label=r"$|2T/2T_0-1|$")
    line_L, = ax_drift.semilogy([], [], color=C["drift"][1], lw=1.2, ls="--", label=r"$|L^2/L_0^2-1|$")
    line_q, = ax_drift.semilogy([], [], color=C["drift"][2], lw=1.0, label=r"$||q|-1|$")
    ax_drift.set_xlabel("t", labelpad=1); ax_drift.grid(True, which="major")
    ax_drift.set_title("RELATIVE DRIFT OF THE INVARIANTS", loc="left", fontsize=9)
    cursor_d = ax_drift.axvline(0, color=C["text"], lw=0.9, alpha=0.8, animated=True)
    for ax in (ax_w, ax_drift):
        ax.set_facecolor(C["panel"])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=8)

    # banda de controles
    fig.patches.append(FancyBboxPatch((0.012, 0.015), 0.976, 0.255, boxstyle="round,pad=0,rounding_size=0.006",
                                      transform=fig.transFigure, fc=C["panel"], ec=C["line"], lw=0.8, zorder=-1))
    for x, title in ((0.028, "BODY"), (0.300, "NUMERICS"), (0.535, "SCHEME"), (0.660, "INITIAL SPIN"),
                     (0.795, "THEORY  vs  SIMULATION")):
        fig.text(x, 0.243, title, fontsize=9, fontweight="bold", color=C["accent"])

    def slider(x, y, w, label, a, b, v, fmt="%.2f"):
        s = Slider(fig.add_axes([x, y, w, 0.018]), label, a, b, valinit=v, valfmt=fmt, color=C["accent"],
                   track_color=C["line"], initcolor="none",
                   handle_style={"facecolor": C["text"], "edgecolor": C["accent"], "size": 11})
        s.ax.set_facecolor(C["panel"])
        s.label.set_color(C["text"]); s.label.set_fontsize(11)
        s.valtext.set_color(C["muted"]); s.valtext.set_fontsize(10)
        s.on_changed(schedule)
        return s

    S_I1  = slider(0.080, 0.203, 0.165, r"$I_1$", 0.2, 5., 1.)
    S_I2  = slider(0.080, 0.166, 0.165, r"$I_2$", 0.2, 5., 2.)
    S_I3  = slider(0.080, 0.129, 0.165, r"$I_3$", 0.2, 5., 3.)
    S_W   = slider(0.080, 0.092, 0.165, r"$\Omega$", 0.1, 3., 1.)
    S_eps = slider(0.080, 0.055, 0.165, r"$\log_{10}\varepsilon$", -8., -1., -3.)
    S_dt  = slider(0.355, 0.203, 0.115, r"$\log_{10}\Delta t$", -2.5, -0.5, -1.7)
    S_tf  = slider(0.355, 0.166, 0.115, r"$t_f$", 10., 150., 80., "%.0f")

    def button(x, label, callback):
        b = Button(fig.add_axes([x, 0.100, 0.066, 0.040]), label, color=C["line"], hovercolor="#30456E")
        b.label.set_color(C["text"]); b.label.set_fontsize(10)
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        b.on_clicked(callback)
        return b

    B_play  = button(0.300, "Play / Pause", play_pause)
    B_comp  = button(0.371, "Compare all", compare)
    B_reset = button(0.442, "Reset", reset)

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

    R_scheme = radio([0.530, 0.035, 0.120, 0.195], list(schemes), 2)          # 3 = "RK4" (indices desde 0)
    R_axis   = radio([0.655, 0.110, 0.130, 0.120], list(axes_names), 1)
    notes = fig.text(0.662, 0.095, "", fontsize=8.5, color=C["warn"], va="top", linespacing=1.5)

    info_labels = fig.text(0.795, 0.222, "", fontsize=9.2, color=C["muted"], va="top", linespacing=1.6)
    info = fig.text(0.978, 0.222, "", fontsize=9.2, color=C["text"], va="top", ha="right", linespacing=1.6,
                    fontweight="bold")
    fig.text(0.028, 0.024, "space play/pause     ← →  scrub     1 2 3  spin axis     ↑ ↓  scheme     "
             "c  compare     v  reset 3D views     + −  speed     r  reset     f  fullscreen     "
             "p  performance     click a plot to jump in time", fontsize=8.5, color=C["muted"])

    timer = fig.canvas.new_timer(interval=350)
    timer.single_shot = True
    timer.add_callback(compute)
    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("draw_event", on_draw)
    fig.canvas.mpl_connect("close_event", on_close)

    compute()
    S["animation"] = None
    if animate:                                     # ~60 Hz; cada tic solo repinta lo animado
        S["animation"] = fig.canvas.new_timer(interval=16)
        S["animation"].add_callback(frame, None)
        S["animation"].start()

    # se devuelven los controles para poder probarlos sin pantalla
    S.update(fig=fig, compute=compute, compare=compare, frame=frame, goto=goto, render=render, info=info, warning=warning,
             sliders=(S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf), R_scheme=R_scheme, R_axis=R_axis,
             buttons=(B_play, B_comp, B_reset))
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
