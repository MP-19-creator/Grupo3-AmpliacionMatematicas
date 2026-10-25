import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
from numpy import array, abs, maximum, sqrt, errstate, argmin, linspace
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from active.numerical_engine.Cauchy_Problem import Cauchy_problem, Integration_stopped
from active.numerical_engine.Temporal_Schemes import (Euler, Euler_implicit, Crank_Nicolson,RK4)
from active.space_physics.eje_intermedio import (Rigid_body_problem, Initial_condition, Linear_eigenvalues,
    Kinetic_energy_2T, Angular_momentum_L2, Rotation_matrix, Energy_ellipsoid, Momentum_ellipsoid,
    Separatrix, Side_of_separatrix, Polhode_period, Is_physical, Box_dimensions)

schemes = { "Euler": Euler, "Euler (implicit)": Euler_implicit, "Crank-Nicolson": Crank_Nicolson, "RK4": RK4 }
slow = (Crank_Nicolson)
N_max = { "fast": 20000, "slow": 3000 }                   # the GUI must not freeze
axes_names = { "Minor axis (I1)": 0, "Intermediate (I2)": 1, "Major axis (I3)": 2 }
floor = 1e-17                                             # log of zero drifts
colors = ("tab:red", "tab:green", "tab:blue")

def Integrate(F, t, U0, scheme):
    """ Cauchy_problem protected: if the scheme blows up or Newton fails,
        it returns what was computed (cut where |U| grows 1e6 times) """
    try:
        with errstate(over="ignore", invalid="ignore"):
            U = Cauchy_problem(F, t, U0, scheme)
    except Integration_stopped as e:
        U = e.U_partial
    with errstate(over="ignore", invalid="ignore"):
        bounded = norm(U, axis=1) < 1e6 * norm(U0)
    if not bounded.all():
        U = U[:argmin(bounded)]
    return t[:len(U)], U


def Zero_crossings(t, x):
    """ Times where x changes sign (linear interpolation between nodes) """
    i = ((x[1:] * x[:-1]) < 0).nonzero()[0]
    return t[i] - x[i] * (t[i+1] - t[i]) / (x[i+1] - x[i])


def build_gui(animate=True):

  S = {}                                         # state shared by the callbacks

  # ------------------------------------------------------------ computation
  def compute():
    I = (S_I1.val, S_I2.val, S_I3.val)
    Omega, dt, eps, tf = S_W.val, 10**S_dt.val, 10**S_eps.val, S_tf.val
    scheme = schemes[R_scheme.value_selected]
    axis = axes_names[R_axis.value_selected]
    warning.set_text("")

    if not I[0] < I[1] < I[2]:
      warning.set_text("I1 < I2 < I3 is required: the last valid result is kept")
      fig.canvas.draw_idle()
      return

    notes = []
    N = max(2, int(round(tf/dt)))
    Nm = N_max["slow" if scheme in slow else "fast"]
    if N > Nm:
      N = Nm
      notes.append(f"N limited to {Nm}: effective dt = {tf/N:.3g}")
    t = linspace(0, tf, N+1)

    clock = time.perf_counter()
    t, U = Integrate(Rigid_body_problem(I), t, Initial_condition(axis, Omega, eps), scheme)
    S["cpu"] = time.perf_counter() - clock
    if len(U) < N+1:
      notes.append(f"{scheme.__name__} fails or blows up near t = {t[-1]:.2f}: reduce dt")
    if len(U) < 2:
      warning.set_text("The solution blows up at the first step: reduce dt")
      fig.canvas.draw_idle()
      return

    S.update(I=I, t=t, U=U, scheme=scheme, axis=axis, notes=notes, k=0)
    for line in S.get("comparison", []):
      line.remove()
    S["comparison"] = []
    draw_phase_space(); draw_body(); draw_time_series(); write_info()
    fig.canvas.draw_idle()

  def schedule(_=None):
    """ Recompute 350 ms after the last change (not at every mouse move) """
    timer.stop(); timer.start()

  def compare(_=None):
    """ Drift of 2T with ALL the schemes (3D model, same dt) """
    if "U" not in S:
      return
    I, w0 = S["I"], S["U"][0, 0:3]
    N = min(len(S["t"]) - 1, N_max["slow"])
    t = linspace(0, S["t"][-1] * N / (len(S["t"]) - 1), N+1)
    for name, scheme in schemes.items():
      if scheme is S["scheme"]:
        continue
      t1, U = Integrate(Rigid_body_problem(I, attitude=False), t, w0, scheme)
      d = maximum(abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(w0, I) - 1), floor)
      S["comparison"] += ax_drift.semilogy(t1, d, lw=0.7, label=name)
    ax_drift.legend(fontsize=7, loc="lower right", ncol=2)
    ax_drift.set_ylim(floor, 10)
    fig.canvas.draw_idle()

  # ------------------------------------------------------------ drawing
  def draw_phase_space():
    I, U = S["I"], S["U"]
    T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
    ax_phase.clear()
    ax_phase.plot_wireframe(*Energy_ellipsoid(I, T2, 28), color="tab:blue", lw=0.3, alpha=0.35)
    ax_phase.plot_wireframe(*Momentum_ellipsoid(I, L2, 28), color="tab:orange", lw=0.3, alpha=0.35)
    for j, curve in enumerate(Separatrix(I, T2)):
      ax_phase.plot(*curve, "r--", lw=1.3, label="separatrix" if j == 0 else None)
    ax_phase.plot(U[:, 0], U[:, 1], U[:, 2], "k", lw=1, label="numerical polhode")
    S["point"], = ax_phase.plot(U[0:1, 0], U[0:1, 1], U[0:1, 2], "o", color="magenta", ms=7)
    R = sqrt(T2 / I[0]) * 1.05
    ax_phase.set_xlim(-R, R); ax_phase.set_ylim(-R, R); ax_phase.set_zlim(-R, R)
    ax_phase.set_box_aspect((1, 1, 1))
    ax_phase.set_xlabel(r"$\omega_1$"); ax_phase.set_ylabel(r"$\omega_2$"); ax_phase.set_zlabel(r"$\omega_3$")
    ax_phase.set_title("Phase space: 2T (blue) and $L^2$ (orange) ellipsoids", fontsize=9)
    ax_phase.legend(fontsize=7, loc="upper left")

  def draw_body():
    I, U = S["I"], S["U"]
    a, b, c = Box_dimensions(I)
    side = max(a, b, c)
    a, b, c = [max(s/side, 0.04) for s in (a, b, c)]          # flat plate: minimum thickness
    S["vertices"] = array([[sx*a/2, sy*b/2, sz*c/2] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    S["faces"] = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    ax_body.clear()
    S["box"] = Poly3DCollection([], facecolor="lightsteelblue", edgecolor="k", lw=0.5, alpha=0.55)
    ax_body.add_collection3d(S["box"])
    S["arrows"] = [ax_body.plot([], [], [], col, lw=2.5)[0] for col in colors]
    L = Rotation_matrix(U[0, 3:7]) @ (array(I) * U[0, 0:3])
    L = 0.9 * L / norm(L)
    ax_body.plot([0, L[0]], [0, L[1]], [0, L[2]], "k", lw=1.5)
    ax_body.text(*L, "L (fixed)", fontsize=8)
    for lim in (ax_body.set_xlim, ax_body.set_ylim, ax_body.set_zlim):
      lim(-0.8, 0.8)
    ax_body.set_box_aspect((1, 1, 1))
    ax_body.set_title("Orientation in inertial axes (red e1, green e2, blue e3)", fontsize=9)
    move_body(0)

  def move_body(k):
    R = Rotation_matrix(S["U"][k, 3:7])
    v = S["vertices"] @ R.T
    S["box"].set_verts([[v[i] for i in face] for face in S["faces"]])
    for i, arrow in enumerate(S["arrows"]):
      e = 0.75 * R[:, i]
      arrow.set_data_3d([0, e[0]], [0, e[1]], [0, e[2]])

  def draw_time_series():
    I, t, U = S["I"], S["t"], S["U"]
    for i, line in enumerate(lines_w):
      line.set_data(t, U[:, i])
    dT = abs(Kinetic_energy_2T(U, I) / Kinetic_energy_2T(U[0], I) - 1)
    dL = abs(Angular_momentum_L2(U, I) / Angular_momentum_L2(U[0], I) - 1)
    dq = abs((U[:, 3:7]**2).sum(axis=1) - 1)
    S["drifts"] = dT.max(), dL.max(), dq.max()
    line_T.set_data(t, maximum(dT, floor)); line_L.set_data(t, maximum(dL, floor))
    line_q.set_data(t, maximum(dq, floor))
    ax_w.set_xlim(0, t[-1])
    m = abs(U[:, 0:3]).max() * 1.1
    ax_w.set_ylim(-m, m)
    ax_drift.set_ylim(floor, max(10, 2 * max(S["drifts"])))
    ax_drift.legend(fontsize=7, loc="lower right", ncol=3)
    ax_w.set_title(f"Angular velocity in body axes - {S['scheme'].__name__}", fontsize=9)

  def write_info():
    I, t, U, axis = S["I"], S["t"], S["U"], S["axis"]
    T2, L2 = Kinetic_energy_2T(U[0], I), Angular_momentum_L2(U[0], I)
    lam = Linear_eigenvalues(I, axis, U[0, axis])[0]
    kind = "real -> saddle, UNSTABLE" if abs(lam.imag) < 1e-14 else "imaginary -> center, stable"
    side = {1: "goes around I3", -1: "goes around I1", 0: "IS the separatrix"}[Side_of_separatrix(I, T2, L2)]
    c = Zero_crossings(t, U[:, 1])
    measured = f"{c[2] - c[0]:.3f}" if len(c) >= 3 else "not completed in tf"
    lines = [ f"lambda(J at w*) = +-{abs(lam):.4f}{'i' if abs(lam.imag) > 1e-14 else ''}  ({kind})",
              f"L^2/(2T) = {L2/T2:.6f}  vs  I2 = {I[1]:.3f}: the polhode {side}",
              f"Exact period 4K(k)/nu = {Polhode_period(I, T2, L2):.3f}   measured = {measured}",
              f"dt = {t[1]-t[0]:.4g}  N = {len(t)-1}  cpu {S['cpu']:.2f} s",
              "max drift: 2T {:.1e}   L^2 {:.1e}   |q| {:.1e}".format(*S["drifts"]) ]
    if not Is_physical(I):
      lines.append("WARNING: I1 + I2 < I3, no real body has these inertias")
    info.set_text("\n".join(lines + S["notes"]))

  def frame(_):
    if "U" not in S or not S["playing"]:
      return ()
    S["k"] = (S["k"] + max(1, len(S["t"]) // 600)) % len(S["t"])
    k, U = S["k"], S["U"]
    S["point"].set_data_3d(U[k:k+1, 0], U[k:k+1, 1], U[k:k+1, 2])
    move_body(k)
    cursor_w.set_xdata([S["t"][k]] * 2); cursor_d.set_xdata([S["t"][k]] * 2)
    return ()

  def play_pause(_):
    S["playing"] = not S["playing"]

  def reset(_):
    for s in (S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf):
      s.reset()
    compute()

  # ------------------------------------------------------------ layout
  fig = plt.figure(figsize=(16, 9))
  fig.suptitle("Intermediate axis theorem: Euler equations of a free rigid body", fontweight="bold")
  ax_phase = fig.add_axes([0.00, 0.37, 0.31, 0.57], projection="3d")
  ax_body  = fig.add_axes([0.29, 0.37, 0.31, 0.57], projection="3d")
  ax_w     = fig.add_axes([0.65, 0.70, 0.33, 0.23])
  ax_drift = fig.add_axes([0.65, 0.40, 0.33, 0.23], sharex=ax_w)

  lines_w = [ax_w.plot([], [], col, lw=1.2, label=fr"$\omega_{i+1}$")[0] for i, col in enumerate(colors)]
  ax_w.legend(loc="upper right", fontsize=8, ncol=3); ax_w.grid(alpha=0.3)
  cursor_w = ax_w.axvline(0, color="k", lw=0.8)
  line_T, = ax_drift.semilogy([], [], "tab:purple", lw=1.4, label=r"$|2T/2T_0-1|$")
  line_L, = ax_drift.semilogy([], [], "tab:orange", lw=1.0, ls="--", label=r"$|L^2/L_0^2-1|$")
  line_q, = ax_drift.semilogy([], [], "tab:gray", lw=0.8, label=r"$||q|-1|$")
  ax_drift.set_xlabel("t"); ax_drift.set_ylabel("relative drift"); ax_drift.grid(alpha=0.3, which="both")
  cursor_d = ax_drift.axvline(0, color="k", lw=0.8)
  info = fig.text(0.65, 0.035, "", fontsize=8.5, family="monospace", va="bottom")
  warning = fig.text(0.30, 0.345, "", fontsize=10, color="tab:red", ha="center")

  def slider(row, label, a, b, v, fmt="%.2f"):
    s = Slider(fig.add_axes([0.07, 0.30 - 0.04*row, 0.33, 0.025]), label, a, b, valinit=v, valfmt=fmt)
    s.on_changed(schedule)
    return s

  S_I1  = slider(0, r"$I_1$", 0.2, 5., 1.)
  S_I2  = slider(1, r"$I_2$", 0.2, 5., 2.)
  S_I3  = slider(2, r"$I_3$", 0.2, 5., 3.)
  S_W   = slider(3, r"$\Omega$", 0.1, 3., 1.)
  S_dt  = slider(4, r"$\log_{10}\Delta t$", -2.5, -0.5, -1.7)
  S_eps = slider(5, r"$\log_{10}\varepsilon$", -8., -1., -3.)
  S_tf  = slider(6, r"$t_f$", 10., 150., 80., "%.0f")

  ax = fig.add_axes([0.44, 0.04, 0.10, 0.27]); ax.set_title("Scheme", fontsize=9)
  R_scheme = RadioButtons(ax, list(schemes), active=4); R_scheme.on_clicked(schedule)
  ax = fig.add_axes([0.545, 0.17, 0.10, 0.14]); ax.set_title("Initial spin", fontsize=9)
  R_axis = RadioButtons(ax, list(axes_names), active=1); R_axis.on_clicked(schedule)
  B_play = Button(fig.add_axes([0.545, 0.115, 0.10, 0.04]), "Pause / Play"); B_play.on_clicked(play_pause)
  B_comp = Button(fig.add_axes([0.545, 0.065, 0.10, 0.04]), "Compare all"); B_comp.on_clicked(compare)
  B_reset = Button(fig.add_axes([0.545, 0.015, 0.10, 0.04]), "Reset"); B_reset.on_clicked(reset)

  timer = fig.canvas.new_timer(interval=350)
  timer.single_shot = True
  timer.add_callback(compute)

  S["playing"] = True
  compute()
  S["animation"] = FuncAnimation(fig, frame, interval=40, cache_frame_data=False) if animate else None

  # the controls are returned so that they can be tested without a screen
  S.update(fig=fig, compute=compute, compare=compare, frame=frame, info=info, warning=warning,
           sliders=(S_I1, S_I2, S_I3, S_W, S_dt, S_eps, S_tf), R_scheme=R_scheme, R_axis=R_axis)
  return S


if __name__ == "__main__":

    gui = build_gui()
    plt.show()