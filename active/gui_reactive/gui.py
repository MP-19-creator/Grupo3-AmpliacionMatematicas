"""
Capa de VISUALIZACION (gui_reactive).  Es la unica capa que conoce a las otras dos:
toma F de space_physics, la integra con numerical_engine y dibuja.

Cuaderno ÓRBITA en CUATRO PAGINAS (pestañas arriba, banco de controles lateral):
    1  Attitude & phase space   la caja girando, Poinsot, separatriz, polhoda, w(t)          (enunciado 3.3)
    2  Invariants               deriva de 2T, L^2 y |q| con los tres esquemas y el mismo dt   (enunciado 3.2)
    3  Stability regions        |R(z)| <= 1 con los autovalores z = lambda dt del problema   (enunciado 3)
    4  Richardson & order       log D frente a log N con su pendiente y el error estimado     (enunciado 3)
Los sliders (I1, I2, I3, Omega, dt, ...) son comunes. El calculo se hace en un trabajador cancelable;
solo el hilo de la ventana modifica Matplotlib. Las paginas de analisis se preparan bajo demanda.
Esquemas: solo los del enunciado (Euler, Crank-Nicolson, RK4), con paso fijo o adaptativo (Richardson).

Fluidez: cache acotada de resultados, estela 3D precalculada, blitting de la pagina visible y pausa del
repintado cuando no hay cambios. Los cambios de pagina invalidan el fondo antes de redibujar.
Ejecutar con el depurador de VS Code (F5) es mucho mas lento: usar Ctrl+F5 o 'python PEI1/PEI1.py'.

Atajos:  1 2 3 4  paginas            espacio  play/pausa          <- ->  mover el tiempo
         a  eje de giro inicial      arriba/abajo  esquema         m  paso fijo / adaptativo
         + -  velocidad              v  recolocar camaras 3D       r  reset      f  pantalla completa
         p  medidor de rendimiento   clic en una grafica temporal: saltar a ese instante
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
from concurrent.futures import ProcessPoolExecutor, CancelledError
from multiprocessing import get_context
from types import SimpleNamespace
from collections import OrderedDict
from inspect import signature
from numpy import array, argmin, arange, clip, errstate, interp, linspace, searchsorted, isfinite, eye, maximum, log10, ceil
from numpy.linalg import norm, solve, LinAlgError
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox

from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Cauchy_problem_adaptive, Integration_stopped
from active.numerical_engine.temporal_schemes import Euler, Crank_Nicolson, RK4
from active.space_physics.eje_intermedio import Rigid_body_problem, Initial_condition, Is_physical
from active.gui_reactive.style import C, Presentation_style, Debugger_attached
from active.gui_reactive.page_attitude import Attitude_page, Zero_crossings
from active.gui_reactive.page_invariants import Invariants_page, Drifts
from active.gui_reactive.page_stability import Stability_page
from active.gui_reactive.page_richardson import Richardson_page
from active.gui_reactive.style import scheme_colors, Legend
from active.gui_reactive.page_attitude import light
from matplotlib.colors import to_rgb
from active.numerical_engine.NewtonRaphson import Newton, Newton_failed
from active.numerical_engine.Errores_Convergencia import ordenes_locales
from active.space_physics.eje_intermedio import Rotation_matrix

class _GuiScheme:
    """Metadatos locales: no se modifican las funciones del motor importado."""
    def __init__(self, function, order):
        self.function, self.order = function, order
        self.__name__ = function.__name__

    def __call__(self, U, dt, t, F):
        return self.function(U, dt, t, F)


def _compatible_cn(U, dt, t, F):
    """Adaptador GUI para versiones de Newton que solo aceptan (F, U0).

    Mantiene la regla del trapecio y el Jacobiano exacto sin alterar el motor.
    Los fallos son ArithmeticError, como espera Cauchy_problem.
    """
    A = U + dt / 2 * F(U, t)
    X = Euler(U, dt, t, F)
    for _ in range(25):
        residual = X - A - dt / 2 * F(X, t + dt)
        if not isfinite(residual).all():
            raise Newton_failed("non-finite residual")
        if norm(residual) <= 1e-10:
            return X
        try:
            X = X - solve(eye(len(U)) - dt / 2 * F.jacobian(X, t + dt), residual)
        except LinAlgError as exc:
            raise Newton_failed("singular Jacobian") from exc
    raise Newton_failed("Newton iteration limit")


_compatible_cn.__name__ = "Crank_Nicolson"
_cn = Crank_Nicolson if len(signature(Newton).parameters) >= 3 else _compatible_cn
schemes = {"Euler": _GuiScheme(Euler, 1), "Crank-Nicolson": _GuiScheme(_cn, 2), "RK4": _GuiScheme(RK4, 4)}
slow = (schemes["Crank-Nicolson"],)
N_max = { "fast": 100000, "slow": 30000 }                  # calculo cancelable y memoria acotada
axes_names = { "Menor  I₁": 0, "Intermedio  I₂": 1, "Mayor  I₃": 2 }
modes = ("Paso fijo", "Adaptativo")
N_display = 4000                                          # puntos para animar una solucion adaptativa
N_draw = 2000                                             # puntos dibujados por curva (se integra con todos)
play_seconds = 20                                         # segundos reales que dura t in [0, tf] a velocidad x1


_worker_generation = None


def _initialize_worker(generation):
    global _worker_generation
    _worker_generation = generation


class _Cancellation:
    def __init__(self, generation, expected):
        self.generation, self.expected = generation, expected

    def is_set(self):
        return self.generation.value != self.expected


def _run_calculation(kind, snapshot, extra, expected):
    """Entrada serializable del proceso: nunca recibe figuras, callbacks o widgets."""
    cancelled = _Cancellation(_worker_generation, expected)
    if cancelled.is_set():
        raise CancelledError()
    snapshot["scheme"] = schemes[snapshot["name"]]
    if kind == "solution":
        return _calculate_solution(snapshot, cancelled)
    if kind == "runs":
        return _calculate_runs(snapshot, cancelled)
    return _calculate_study(snapshot, *extra, cancelled)


def Integrate(F, tf, U0, scheme, dt, adaptive=False, tol=1e-8):
    """
    Cauchy_problem (o el adaptativo) protegido: si el esquema explota o Newton falla devuelve lo calculado
    y una nota. Paso fijo: conserva dt y acorta el horizonte si alcanza N_max.
    """
    note = ""
    try:
        with errstate(over="ignore", invalid="ignore"):
            if adaptive:
                t, U = Cauchy_problem_adaptive(F, tf, U0, scheme, tol=tol, dt0=dt,
                                               max_steps=N_max["slow" if scheme in slow else "fast"])
            else:
                N = max(1, int(ceil(tf / dt)))
                Nm = N_max["slow" if scheme in slow else "fast"]
                if N > Nm:
                    N = Nm
                    note = f"Límite de {Nm:,} pasos: t = {N*dt:g} s (Δt = {dt:g})"
                t = arange(N + 1, dtype=float) * dt
                t[-1] = min(t[-1], tf)
                U = Cauchy_problem(F, t, U0, scheme)
    except Integration_stopped as e:
        U, t = e.U_partial, e.t_partial
        note = (f"step limit reached at t = {t[-1]:.1f}" if "steps" in str(e) else f"stopped at t = {t[-1]:.1f}")
    with errstate(over="ignore", invalid="ignore"):
        bounded = norm(U, axis=1) < 1e6 * norm(U0)        # cortar donde |U| crece 1e6 veces
    if not bounded.all():
        end = max(1, int(argmin(bounded)))
        U, t = U[:end], t[:end]
        note = f"Divergencia cerca de t = {t[-1]:.3g} s"
    return t, U, note


def _checked_scheme(scheme, cancelled):
    def step(U, dt, t, F):
        if cancelled.is_set():
            raise CancelledError()
        return scheme(U, dt, t, F)
    step.__name__ = scheme.__name__
    return _GuiScheme(step, scheme.order)


def _checked_field(I, cancelled):
    original = Rigid_body_problem(I)
    def F(U, t):
        if cancelled.is_set():
            raise CancelledError()
        return original(U, t)
    F.jacobian = original.jacobian
    return F


def _calculate_solution(params, cancelled):
    """Solo arrays y numeros en el trabajador; Matplotlib queda en el hilo UI."""
    start = time.perf_counter()
    I = params["I"]
    tn, Un, note = Integrate(_checked_field(I, cancelled), params["tf"],
                             Initial_condition(params["axis"], params["Omega"], params["eps"]),
                             params["scheme"], params["dt"], params["adaptive"], params["tol"])
    if len(tn) < 2:
        raise ValueError("La solución diverge al empezar. Aumenta la precisión del paso.")
    if params["adaptive"]:
        t = linspace(tn[0], tn[-1], N_display)
        U = array([interp(t, tn, Un[:, j]) for j in range(Un.shape[1])]).T
    else:
        indices = linspace(0, len(tn)-1, min(len(tn), N_display), dtype=int)
        t, U = tn[indices], Un[indices]
    stride = max(1, (len(t) + N_draw - 1) // N_draw)
    d = arange(0, len(t), stride)
    if d[-1] != len(t) - 1:
        d = array([*d, len(t) - 1])
    # La estela 3D reutiliza estas rotaciones: antes se calculaban 60 por frame.
    tips = array([0.78 * Rotation_matrix(q)[:, params["axis"]] for q in U[:, 3:7]])
    notes = ([f"{params['name']}: {note}"] if note else [])
    if not Is_physical(I):
        notes.append("I1 + I2 < I3: no real body")
    return dict(nodes=(tn, Un), t=t, U=U, cpu=time.perf_counter()-start, notes=notes,
                note=note, k=0, tp=0.0, d=d, trail_tips=tips,
                flips=Zero_crossings(tn, Un[:, params["axis"]]), window=min(15., .2*t[-1]),
                dt_used=tn[1]-tn[0], drifts=[v.max() for v in Drifts(Un, I)])


def _calculate_runs(snapshot, cancelled):
    runs = {}
    U0 = Initial_condition(snapshot["axis"], snapshot["Omega"], snapshot["eps"])
    for name, scheme in schemes.items():
        if scheme is snapshot["scheme"]:
            t, U = snapshot["nodes"]
            note = snapshot["note"]
        else:
            t, U, note = Integrate(_checked_field(snapshot["I"], cancelled), snapshot["tf"], U0, scheme,
                                   snapshot["dt"],
                                   snapshot["adaptive"], snapshot["tol"])
        runs[name] = dict(t=t, U=U, note=note)
    return runs


def _calculate_study(snapshot, tf, curves, cancelled):
    start = time.perf_counter()
    checked = {name: _checked_scheme(scheme, cancelled) for name, scheme in schemes.items()}
    state = dict(snapshot, scheme=checked[snapshot["name"]])
    # Los metodos de calculo existentes se reutilizan con un contexto sin figura.
    context = SimpleNamespace(S=state, tf_study=SimpleNamespace(val=tf), schemes=checked, cache={})
    with errstate(over="ignore", invalid="ignore", divide="ignore"):
        res = curves if curves is not None else Richardson_page.study(context)
        N = int(min(max(round(tf/snapshot["dt"]), 20), 2000))
        t = linspace(0, tf, N+1)
        F = _checked_field(snapshot["I"], cancelled)
        U0 = Initial_condition(snapshot["axis"], snapshot["Omega"], snapshot["eps"])
        try:
            U1 = Cauchy_problem(F, t, U0, checked[snapshot["name"]])
            U2 = Cauchy_problem(F, linspace(0, tf, 2*N+1), U0, checked[snapshot["name"]])
            reference = Cauchy_problem(F, linspace(0, tf, 8*N+1), U0, checked["RK4"])
            errors = (t, norm(U1-U2[::2], axis=1)/(1-2.**-state["scheme"].order),
                      norm(U1-reference[::8], axis=1), N)
        except ArithmeticError:
            errors = (t, None, None, N)
    return res, errors, time.perf_counter()-start


class _StudyPage(Richardson_page):
    """Dibujo a partir de datos preparados, sin draw/flush_events recursivos."""
    def refresh(self):
        res, (t, estimated, reference, N), cpu = self.prepared
        S, ax = self.S, self.ax_conv
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        for name, r in res.items():
            col = scheme_colors[name]
            valid = isfinite(r["D"]) & (r["D"] > 0)
            selected = name == S["name"]
            ax.plot(log10(r["N"][valid]), log10(r["D"][valid]), "o-", color=col,
                    lw=2.4 if selected else 1.1, ms=5, label=f"{name} · orden {-r['slope']:.2f}")
            idx = r["idx"]
            if len(idx) >= 2 and isfinite(r["slope"]):
                x = log10(r["N"][idx])
                ax.plot(x, r["slope"]*x+r["b"], "--", color=col, alpha=.65)
        ax.relim(); ax.autoscale_view()
        Legend(ax, loc="lower left", fontsize=9)
        ax = self.ax_rich
        for a in list(ax.lines) + list(ax.texts):
            a.remove()
        if estimated is not None:
            d = slice(1, None, max(1, N//800))
            ax.plot(t[d], maximum(estimated[d], 1e-17), color=scheme_colors[S["name"]], lw=2,
                    label="Estimación de Richardson")
            ax.plot(t[d], maximum(reference[d], 1e-17), color=C["point"], ls="--", lw=1.2,
                    label="Referencia RK4 · 8N pasos")
            ax.set_xlim(0, t[-1])
            Legend(ax, fontsize=8, loc="lower right")
        else:
            ax.text(.05, .5, "El método diverge en este intervalo. Reduce Δt.", transform=ax.transAxes,
                    color=C["warn"], fontsize=10)
        ax.relim(); ax.autoscale_view()
        r = res[S["name"]]
        with errstate(invalid="ignore", divide="ignore"):
            orders = ordenes_locales(r["D"])
        rows = [f"{'N':>7} {'Δt':>9} {'Diferencia D':>14} {'Orden':>8}"]
        for k, n in enumerate(r["N"]):
            order = f"{orders[k]:8.2f}" if k < len(orders) and isfinite(orders[k]) else "       —"
            rows.append(f"{n:7d} {self.tf_study.val/n:9.4f} {r['D'][k]:14.3e} {order}")
        self.table_title.set_text(f"{S['name'].upper()}  /  ORDEN TEÓRICO {S['scheme'].order}")
        self.table.set_text("\n".join(rows))
        self.side.set_text("CÓMO LEERLO\n\nDuplicar N reduce Δt\na la mitad.\n\nLa pendiente mide\nel orden observado.\n\nD compara las mallas\nN y 2N, sin solución\nexacta conocida.")
        self.status.set_text(f"Estudio completo · t = {self.tf_study.val:.0f} · cálculo {cpu:.2f} s · resultados en caché")
        self.status.set_color(C["muted"])


class _AttitudePage(Attitude_page):
    def refresh(self):
        super().refresh()
        for ax in (self.ax_body, self.ax_phase):
            ax.set_facecolor(C["panel"])

    def move_body(self, k):
        # El resto de la geometria sigue el mismo modelo; solo se evita recalcular la estela.
        S = self.S
        R = Rotation_matrix(S["U"][k, 3:7])
        v = self.vertices @ R.T
        self.box.set_verts([[v[i] for i in face] for face in self.faces])
        shade = .28 + .72 * clip((self.normals @ R.T) @ light, 0, 1)
        gold = array(to_rgb(C["gold"]))
        self.box.set_facecolor([(*(gold*s), 1.) for s in shade])
        for i in range(3):
            e = .78 * R[:, i]
            self.arrows[i].set_data_3d([0, e[0]], [0, e[1]], [0, e[2]])
            self.tips[i].set_data_3d([e[0]], [e[1]], [e[2]])
        t = S["t"]
        idx = searchsorted(t, linspace(max(0., t[k]-S["window"]), t[k], 48)).clip(0, len(t)-1)
        tips = S["trail_tips"][idx]
        self.trail.set_segments(array([tips[:-1], tips[1:]]).transpose(1, 0, 2))
        col = array(to_rgb(C["e"][S["axis"]]))
        self.trail.set_color([(*col, .9*(i+1)/len(tips)) for i in range(len(tips)-1)])


def build_gui(animate=True):

    Presentation_style()
    S = {"playing": True, "speed": 1.0, "clock": time.perf_counter(), "tp": 0.0, "k": 0, "background": None,
         "closed": False, "show_perf": False, "cost": 0.01, "fps": 30.0, "interval": 16, "version": 0,
         "runs_version": -1, "page": 0, "request": 0, "busy": False, "ready": False,
         "transition": False, "last_frame": None}

    fig = plt.figure(figsize=(19.2, 11.2))
    # Los widgets solicitan un dibujo al construirse. Agruparlos evita decenas
    # de renders completos durante el arranque (solo afecta a esta figura).
    initial_draw_idle = fig.canvas.draw_idle
    fig.canvas.draw_idle = lambda *args, **kwargs: None
    context = get_context("spawn")
    generation = context.Value("q", 0, lock=False)
    executor = ProcessPoolExecutor(max_workers=1, mp_context=context,
                                   initializer=_initialize_worker, initargs=(generation,))
    jobs = {}
    cache = OrderedDict()
    study_cache = OrderedDict()
    try:
        fig.canvas.manager.set_window_title("ÓRBITA · Cuaderno de dinámica / PEI 1")
    except AttributeError:
        pass

    # ------------------------------------------------------------ calculo
    def read_controls():
        params = dict(I=(S_I1.val, S_I2.val, S_I3.val), Omega=S_W.val, dt=S_dt.val, eps=S_eps.val,
                 tf=S_tf.val, tol=S_tol.val, name=R_scheme.value_selected,
                 adaptive=R_mode.value_selected == modes[1], axis=axes_names[R_axis.value_selected])
        params["scheme"] = schemes[params["name"]]
        return params

    def remember(target, key, value):
        target[key] = value
        target.move_to_end(key)
        while len(target) > 4:
            target.popitem(last=False)

    def cancel_jobs():
        generation.value += 1
        for future, *_ in jobs.values():
            future.cancel()
        jobs.clear()

    def submit(kind, snapshot, *extra):
        if kind in jobs:
            return
        keys = ("I", "Omega", "eps", "axis", "name", "dt", "adaptive", "tol", "tf")
        data = {key: snapshot[key] for key in keys}
        if kind == "runs":
            data.update(nodes=snapshot["nodes"], note=snapshot["note"], dt_used=snapshot["dt_used"])
        cancelled = _Cancellation(generation, generation.value)
        jobs[kind] = (executor.submit(_run_calculation, kind, data, extra, generation.value),
                      cancelled, S["request"], S["version"])

    def status(message, error=False):
        warning.set_text(message)
        warning.set_color(C["warn"] if error else C["muted"])
        fig.canvas.draw_idle()

    def apply_solution(params, result):
        S.pop("error", None)
        S.update(params)
        S.update(result)
        S.update(version=S["version"]+1, busy=False, clock=time.perf_counter(), last_frame=None)
        notes_text.set_text("")
        transport.set_text(f"{S['name']}  ·  {len(S['nodes'][0])-1:,} pasos  ·  {S['cpu']:.2f} s")
        show_page(S["page"], force=True)

    def compute():
        """Encola una instantanea; nunca integra dentro de un evento de la ventana."""
        timer.stop()
        cancel_jobs()
        S.pop("error", None)
        S["request"] += 1
        params = read_controls()
        I = params["I"]
        if not I[0] < I[1] < I[2]:
            S["busy"] = False
            if "U" in S and not S["ready"]:
                show_page(0)
            status("Se requiere I₁ < I₂ < I₃ · se conserva el último resultado válido", True)
            return
        S["pending_params"] = params
        key = tuple(params.values())
        S["pending_key"] = key
        if key in cache:
            apply_solution(params, cache[key])
        else:
            S["busy"] = True
            status("Calculando trayectoria… Puedes seguir navegando y ajustar los controles.")
            submit("solution", params)

    def ensure_runs():
        """Comparacion diferida, compartida por invariantes y estabilidad."""
        if S["runs_version"] == S["version"]:
            return True
        if not S["busy"]:
            submit("runs", S)
        return False

    def poll():
        """Aplica solo resultados vigentes, siempre en el hilo de Matplotlib."""
        if S["closed"]:
            return
        for kind, job in list(jobs.items()):
            future, cancelled, request, version = job
            if not future.done():
                continue
            del jobs[kind]
            if cancelled.is_set() or request != S["request"]:
                continue
            try:
                result = future.result()
                if kind == "solution":
                    remember(cache, S["pending_key"], result)
                    apply_solution(S["pending_params"], result)
                elif version == S["version"]:
                    if kind == "runs":
                        S.update(runs=result, runs_version=version)
                    else:
                        remember(study_cache, S["study_key"], result)
                        pages[3].prepared = result
                    if S["page"] in ((1, 2) if kind == "runs" else (3,)):
                        show_page(S["page"], force=True)
            except CancelledError:
                pass
            except Exception as exc:
                S["busy"] = False
                S["error"] = str(exc)
                status(f"No se pudo completar el cálculo: {exc}", True)
                if not S["ready"]:
                    placeholder.set_text("No se pudo calcular esta vista\nAjusta los parámetros y vuelve a intentarlo.")
                    placeholder.set_visible(True)
                    fig.canvas.draw_idle()

    def schedule(_=None):
        """ Recalcula 350 ms despues del ultimo cambio (no en cada movimiento del raton) """
        cancel_jobs()
        S["request"] += 1
        S["busy"] = True
        status("Parámetros modificados · preparando nueva simulación…")
        timer.stop()
        timer.start()

    # ------------------------------------------------------------ paginas
    def show_page(i, force=False):
        if S["closed"] or not 0 <= i < len(pages):
            return
        S["transition"] = True
        S["background"] = None
        S["page"] = i
        S["last_frame"] = None
        page = pages[i]
        prepared = "U" in S
        loading = "Calculando trayectoria…"
        if prepared and i in (1, 2):
            prepared = ensure_runs()
            loading = "Comparando Euler, Crank–Nicolson y RK4…"
        elif prepared and i == 3:
            key = (S["I"], S["Omega"], S["eps"], S["axis"], S["name"], S["dt"], float(page.tf_study.val))
            S["study_key"] = key
            prepared = key in study_cache
            if prepared:
                page.prepared = study_cache[key]
            elif not S["busy"]:
                curves = next((value[0] for previous, value in study_cache.items()
                               if previous[:4] == key[:4] and previous[-1] == key[-1]), None)
                submit("study", S, float(page.tf_study.val), curves)
            loading = "Preparando el estudio de convergencia… La navegación sigue disponible."
        S["ready"] = prepared
        for j, page in enumerate(pages):
            page.set_visible(j == i and prepared)
            if j == 3:
                page.tf_study.set_active(j == i)
                page.slider_ax.set_visible(j == i)
            tabs[j].ax.set_facecolor(C["accent"] if j == i else C["bg"])
            tabs[j].color = C["accent"] if j == i else C["bg"]
            tabs[j].label.set_color(C["bg"] if j == i else C["text"])
        page = pages[i]
        placeholder.set_visible(not prepared)
        placeholder.set_text(loading + "\nPuedes cambiar de pestaña mientras se completa el cálculo.")
        try:
            if prepared and (force or getattr(page, "version", -1) != S["version"]):
                page.refresh()
                page.version = S["version"]
            if prepared:
                page.update_frame(S["k"])
                if i == 2:
                    page.legend_text.set_position((content_x(.355), .827))
                    page.legend_text.set_fontsize(9)
                    page.legend_text.set_text("Rojo: amplificación extra · Azul: amortiguamiento extra · Puntos: λΔt del estado actual")
                warning.set_text("Calculando nueva trayectoria…" if S["busy"] else " · ".join(S["notes"]) or "Listo")
            else:
                warning.set_text(loading)
            for card in attitude_cards:
                card.set_visible(i == 0 and prepared)
        except Exception as exc:
            S["ready"] = False
            S["error"] = str(exc)
            page.set_visible(False)
            placeholder.set_text(f"No se pudo dibujar esta vista\n{exc}\nPuedes seguir usando las otras pestañas.")
            placeholder.set_visible(True)
            warning.set_text("Error de visualización · ajusta los controles para reintentar")
        finally:
            S["transition"] = False
        fig.canvas.draw_idle()

    def richardson_changed():
        if "study" in jobs:
            # Cambiar el estudio invalida tambien cualquier analisis en cola.
            cancel_jobs()
        pages[3].version = -1
        if S["page"] == 3:
            richardson_timer.stop(); richardson_timer.start()

    # ------------------------------------------------------------ animacion
    def frame(_=None):
        if "U" not in S or S["closed"] or S["transition"] or not S["ready"]:
            return
        now = time.perf_counter()
        real_dt = min(now - S["clock"], 0.25)       # tiempo real, no fotogramas (tope: sin saltos tras una pausa)
        S["clock"] = now
        t = S["t"]
        if S["playing"]:
            S["tp"] = (S["tp"] + real_dt * S["speed"] * t[-1] / play_seconds) % t[-1]
        S["k"] = min(int(searchsorted(t, S["tp"])), len(t) - 1)
        current = (S["page"], S["k"], S["playing"], S["speed"], S["show_perf"])
        if current == S["last_frame"] and not S["show_perf"]:
            return
        S["last_frame"] = current
        if S["page"] == 3 and not S["show_perf"]:
            return                    # Richardson estatico: no repintar 60 veces por segundo
        pages[S["page"]].update_frame(S["k"])
        if S["show_perf"]:
            perf_text.set_text(f"{S['fps']:4.0f} fps  ·  {1000*S['cost']:4.1f} ms/frame  ·  timer {S['interval']} ms  ·  "
                               f"{matplotlib.get_backend()}  ·  debugger {'ON' if Debugger_attached() else 'off'}")
        try:
            blit()
        except (AttributeError, RuntimeError):
            S.update(background=None, last_frame=None)
            if not S["closed"]:
                fig.canvas.draw_idle()
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
        cancel_jobs()
        executor.shutdown(wait=False, cancel_futures=True)
        for tm in (S.get("animation"), timer, richardson_timer, poll_timer):
            if tm is not None:
                tm.stop()

    def animated():
        if not S["ready"] or S["transition"]:
            return []
        return pages[S["page"]].animated() + [perf_text]

    def paint_animated():
        for a in animated():
            if not a.get_visible() or (a.axes is not None and not a.axes.get_visible()):
                continue
            if hasattr(a, "do_3d_projection"):              # colecciones 3D: proyectar con la camara actual
                a.do_3d_projection()
            fig.draw_artist(a)

    band = Bbox([[0.25, 0.075], [1.0, 0.855]])

    def on_draw(_):
        """ Tras cada redibujado completo: guardar el fondo y pintar encima lo animado """
        if S["closed"] or S["transition"]:
            return
        if not fig.canvas.supports_blit:
            return
        S["region"] = band.transformed(fig.transFigure)
        S["background"] = fig.canvas.copy_from_bbox(S["region"])
        paint_animated()

    def blit():
        if not fig.canvas.supports_blit:
            for artist in animated():
                artist.set_animated(False)
            fig.canvas.draw_idle()
            return
        if S["background"] is None:
            fig.canvas.draw_idle()
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
        if S["ready"]:
            pages[S["page"]].update_frame(S["k"])
            blit()

    # ------------------------------------------------------------ teclado y raton
    def play_pause(_=None):
        S["playing"] = not S["playing"]
        S["clock"] = time.perf_counter()
        B_play.label.set_text("Pausar" if S["playing"] else "Reproducir")
        fig.canvas.draw_idle()

    def reset(_=None):
        for s in (S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf, S_tol):
            s.eventson = False
            s.reset()
            s.eventson = True
        for r, active in ((R_scheme, 2), (R_mode, 0), (R_axis, 1)):
            r.eventson = False
            r.set_active(active)
            r.eventson = True
        S_tol.ax.set_visible(False)
        S.update(speed=1., playing=True)
        B_play.label.set_text("Pausar")
        compute()

    def on_key(event):
        if any(control.capturekeystrokes for control in (S_eps, S_dt, S_tol)):
            return
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
                blit()
        elif key == "f":
            fig.canvas.manager.full_screen_toggle()

    def on_click(event):
        if S["ready"] and event.button == 1 and event.xdata is not None:
            if S["page"] == 0 and event.inaxes is timeline:
                goto(event.xdata)
                return
            tp = pages[S["page"]].click_time(event)
            if tp is not None:
                goto(tp)

    # ------------------------------------------------------------ cuaderno / composición
    # La retícula transforma únicamente artistas. Los datos y callbacks conservan su contrato.
    def content_x(x):
        return .255 + .735*x

    def content_y(y):
        return .105 + (y-.255)*1.10

    fig.patches.append(FancyBboxPatch((.012, .018), .227, .964,
        boxstyle="round,pad=0,rounding_size=0.018", transform=fig.transFigure,
        fc=C["panel"], ec=C["line"], lw=.8, zorder=-3))
    fig.text(.030, .950, "ÓRBITA", fontsize=29, fontweight="bold", color=C["accent"])
    fig.text(.031, .924, "DINÁMICA DEL SÓLIDO", fontsize=9, color=C["muted"])
    fig.text(.266, .952, "Teorema del eje intermedio", fontsize=27, fontweight="bold", color=C["ink"])
    fig.text(.267, .920, "Ajusta los parámetros y compara los métodos", fontsize=10, color=C["muted"])
    fig.text(.982, .950, "I₁ < I₂ < I₃", fontsize=17, ha="right", color=C["accent"], family="monospace")
    transport = fig.text(.982, .920, "Preparando simulación", fontsize=8.5, color=C["muted"], ha="right")
    warning = fig.text(.267, .032, "", fontsize=9, color=C["muted"], va="center")
    perf_text = fig.text(.982, .084, "", fontsize=8, color=C["warn"], ha="right", animated=True)

    pages = [_AttitudePage(fig, S), Invariants_page(fig, S), Stability_page(fig, S),
             _StudyPage(fig, S, schemes, lambda: richardson_changed())]
    for page in pages:
        for ax in page.axes:
            x, y, w, h = ax.get_position().bounds
            ax.set_position([content_x(x), content_y(y), w*.735, h*1.10])
            ax.title.set_fontsize(9)
        for text in page.texts:
            x, y = text.get_position()
            text.set_position((content_x(x), content_y(y)))
            text.set_fontsize(min(text.get_fontsize(), 9))

    attitude = pages[0]
    attitude.texts[0].set_text("ORIENTACIÓN / referencia inercial")
    attitude.texts[1].set_text("POINSOT / espacio de fases")
    attitude.texts[2].set_text("TEORÍA Y SIMULACIÓN")
    attitude.flips_label.set_text("VOLTEOS DEL EJE DE GIRO")
    attitude.ax_w.set_title("VELOCIDAD ANGULAR / ejes del cuerpo", loc="left", fontsize=9, color=C["muted"])
    attitude.info_labels.set_fontsize(8)
    attitude.info.set_fontsize(8)
    attitude.badge.set_fontsize(10)
    attitude.flips.set_fontsize(48)
    attitude.clock.set_fontsize(16)
    attitude.info_labels.set_x(content_x(.737))
    original_info = attitude.write_info
    def compact_info():
        original_info()
        values = attitude.info.get_text().splitlines()
        attitude.info_labels.set_text("Autovalor λ\nPeriodo exacto\nDeriva 2T · L²\nDeriva |q|")
        attitude.info.set_text("\n".join(values[i] for i in (0, 2, 4, 5)))
        attitude.badge.set_text(attitude.badge.get_text().replace("UNSTABLE  ·  saddle", "INESTABLE").replace("STABLE  ·  centre", "ESTABLE"))
    attitude.write_info = compact_info
    # Micrográfica de transporte: el tiempo se sigue leyendo de la solución real.
    timeline = fig.add_axes([content_x(.738), content_y(.530), .232*.735, .018])
    timeline.set_facecolor(C["panel"])
    timeline.set_ylim(-1, 1); timeline.set_yticks([])
    timeline.tick_params(axis="x", colors=C["muted"], labelsize=8, length=0, pad=6)
    for spine in timeline.spines.values():
        spine.set_visible(False)
    timeline.axhline(0, color=C["line"], lw=4, solid_capstyle="round")
    progress, = timeline.plot([], [], color=C["accent"], lw=4, solid_capstyle="round", animated=True)
    playhead, = timeline.plot([], [], "o", color=C["accent"], ms=7, mec=C["panel"], animated=True)
    timeline_title = fig.text(content_x(.737), content_y(.570), "RECORRIDO TEMPORAL", fontsize=8.5, fontweight="bold", color=C["accent"])
    timeline_hint = fig.text(content_x(.737), content_y(.478), "Pulsa la línea para explorar el tiempo.", fontsize=8, color=C["muted"])
    attitude.axes.append(timeline)
    attitude.texts += [timeline_title, timeline_hint]
    original_refresh, original_frame, original_animated = attitude.refresh, attitude.update_frame, attitude.animated
    def refresh_attitude():
        original_refresh()
        timeline.set_xlim(0, S["t"][-1])
        timeline.set_xticks([0, S["t"][-1]])
        timeline.set_xticklabels(["0 s", f"{S['t'][-1]:g} s"])
    def update_attitude(k):
        original_frame(k)
        progress.set_data([0, S["t"][k]], [0, 0])
        playhead.set_data([S["t"][k]], [0])
    attitude.refresh = refresh_attitude
    attitude.update_frame = update_attitude
    attitude.animated = lambda: original_animated() + [progress, playhead]
    attitude_cards = []
    for x, w in ((.005, .698), (.720, .280)):
        card = FancyBboxPatch((content_x(x), .099), w*.735, .720,
            boxstyle="round,pad=0,rounding_size=0.012", transform=fig.transFigure,
            fc=C["panel"], ec=C["line"], lw=.8, zorder=-2)
        fig.patches.append(card); attitude_cards.append(card)
    placeholder = fig.text(.62, .48, "Preparando simulación…", ha="center", va="center", fontsize=13,
        color=C["muted"], linespacing=2, bbox=dict(boxstyle="round,pad=2", fc=C["panel"], ec=C["line"]))
    tabs = []
    for i, label in enumerate(("Movimiento", "Conservación", "Estabilidad", "Precisión")):
        b = Button(fig.add_axes([.266 + .183*i, .861, .174, .037]), label,
                   color=C["bg"], hovercolor=C["soft"])
        b.label.set_fontsize(10); b.label.set_fontweight("bold"); b.label.set_color(C["text"])
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        b.on_clicked(lambda _, i=i: show_page(i))
        tabs.append(b)

    # ------------------------------------------------------------ banco lateral
    def section(y, number, title):
        fig.text(.031, y, number, fontsize=9, color=C["accent"], fontweight="bold", family="monospace")
        fig.text(.055, y, title, fontsize=9, color=C["text"], fontweight="bold")
        fig.add_artist(plt.Line2D([.031, .220], [y-.012, y-.012], transform=fig.transFigure, color=C["line"], lw=.8))
    section(.846, "01", "PROPIEDADES DEL SÓLIDO")
    section(.625, "02", "RESOLUCIÓN TEMPORAL")
    section(.467, "03", "INTEGRACIÓN")
    section(.285, "04", "EJE DE GIRO INICIAL")

    def slider(x, y, w, label, a, b, v, fmt="%.2f"):
        s = Slider(fig.add_axes([x, y, w, .016]), label, a, b, valinit=v, valfmt=fmt,
            color=C["accent"], track_color=C["line"], initcolor="none",
            handle_style={"facecolor": C["panel"], "edgecolor": C["accent"], "size": 9})
        s.ax.set_facecolor(C["panel"])
        s.label.set_color(C["text"]); s.label.set_fontsize(10)
        s.valtext.set_color(C["accent"]); s.valtext.set_fontsize(9)
        s.on_changed(schedule)
        return s

    S_I1  = slider(.080, .803, .122, r"$I_1$", .2, 5., 1.)
    S_I2  = slider(.080, .767, .122, r"$I_2$", .2, 5., 2.)
    S_I3  = slider(.080, .731, .122, r"$I_3$", .2, 5., 3.)
    S_W   = slider(.080, .695, .122, r"$\Omega$", .1, 3., 1.)
    def number(y, label, initial, minimum, maximum):
        field = TextBox(fig.add_axes([.100, y-.004, .110, .028]), label + "  ",
                        initial=f"{initial:g}", color=C["bg"], hovercolor=C["soft"])
        field.val = initial
        field.label.set_fontsize(10)
        field.text_disp.set_fontsize(10)
        for spine in field.ax.spines.values():
            spine.set_edgecolor(C["line"])

        def submitted(text):
            try:
                value = float(text.replace(",", "."))
                if not isfinite(value) or not minimum <= value <= maximum:
                    raise ValueError()
            except ValueError:
                status(f"{label}: introduce un valor entre {minimum:g} y {maximum:g}", True)
                return
            field.val = value
            schedule()

        field.on_submit(submitted)
        def reset_number():
            field.val = initial
            field.set_val(f"{initial:g}")
        field.reset = reset_number
        return field

    S_eps = number(.659, "ε", .001, 0., 1.)
    S_dt  = number(.582, "Δt (s)", .02, 1e-6, 2.)
    S_tf  = slider(.080, .539, .122, r"$t_f$", 1., 150., 80., "%.0f")
    S_tol = number(.499, "Tolerancia", 1e-6, 1e-12, .01)
    S_tol.ax.set_visible(False)

    def button(x, y, label, callback, width=.089, primary=False):
        b = Button(fig.add_axes([x, y, width, .035]), label,
                   color=C["accent"] if primary else C["soft"], hovercolor=C["muted"] if primary else C["line"])
        b.label.set_color(C["panel"] if primary else C["accent"]); b.label.set_fontsize(9)
        b.label.set_fontweight("bold")
        for sp in b.ax.spines.values():
            sp.set_visible(False)
        b.on_clicked(callback)
        return b

    B_play = button(.031, .111, "Pausar", play_pause, primary=True)
    B_reset = button(.131, .111, "Restablecer", reset)

    def radio(rect, labels, active):
        ax = fig.add_axes(rect); ax.set_facecolor(C["panel"])
        for sp in ax.spines.values():
            sp.set_visible(False)
        r = RadioButtons(ax, labels, active=active, activecolor=C["accent"],
                         radio_props={"edgecolor": C["muted"], "s": 48})
        for txt in r.labels:
            txt.set_color(C["text"]); txt.set_fontsize(9.5)
        r.on_clicked(schedule)
        return r

    R_scheme = radio([.030, .365, .192, .090], list(schemes), 2)
    R_mode = radio([.030, .300, .192, .060], list(modes), 0)
    def mode_changed(label):
        S_tol.ax.set_visible(label == modes[1])
        fig.canvas.draw_idle()
    R_mode.on_clicked(mode_changed)
    R_axis = radio([.030, .181, .192, .090], list(axes_names), 1)
    notes_text = fig.text(.031, .169, "", fontsize=7.5, color=C["warn"], va="top", linespacing=1.3)
    fig.text(.031, .087, "Espacio / pausa    ·    1–4 / vistas\n← → tiempo    ·    + − velocidad\nArrastra el 3D    ·    V / cámara    ·    F / ampliar",
             fontsize=7.5, color=C["muted"], va="top", linespacing=1.7)

    timer = fig.canvas.new_timer(interval=350)
    timer.single_shot = True
    timer.add_callback(compute)
    richardson_timer = fig.canvas.new_timer(interval=500)
    richardson_timer.single_shot = True
    richardson_timer.add_callback(lambda: show_page(3) if S["page"] == 3 else None)
    poll_timer = fig.canvas.new_timer(interval=60)
    poll_timer.add_callback(poll)
    poll_timer.start()
    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("draw_event", on_draw)
    fig.canvas.mpl_connect("close_event", on_close)
    fig.canvas.mpl_connect("resize_event", lambda _: S.update(background=None, last_frame=None))

    for j, page in enumerate(pages):
        page.set_visible(False)
    show_page(0)
    compute()
    S["animation"] = None
    if animate:                                     # ~60 Hz; cada tic solo repinta lo animado
        S["animation"] = fig.canvas.new_timer(interval=16)
        S["animation"].add_callback(frame)
        S["animation"].start()

    # se devuelven los controles para poder probarlos sin pantalla
    S.update(fig=fig, compute=compute, frame=frame, goto=goto, render=render, show_page=show_page, pages=pages,
             warning=warning, sliders=(S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf, S_tol), R_scheme=R_scheme,
             R_mode=R_mode, R_axis=R_axis, tabs=tabs, buttons=(B_play, B_reset), ensure_runs=ensure_runs,
             poll=poll, close=on_close, jobs=jobs, reset=reset)
    fig.canvas.draw_idle = initial_draw_idle
    fig.canvas.draw_idle()
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
