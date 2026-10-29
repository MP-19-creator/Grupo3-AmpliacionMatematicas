import os
os.environ['MPLBACKEND'] = 'Agg'
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from active.gui_reactive import gui


def wait(s):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        s['poll']()
        assert not s.get('error'), s.get('error')
        if not s['jobs'] and s['ready']:
            return
        time.sleep(.05)
    raise AssertionError('timeout')


def main():
    # A small step must stay small, including when the budget is reached.
    t, u, note = gui.Integrate(lambda u, t: u * 0, 80., np.ones(1), gui.schemes['Euler'], 1e-6)
    np.testing.assert_allclose(np.diff(t), 1e-6, rtol=1e-10)
    assert len(t) == gui.N_max['fast'] + 1 and t[-1] < 80 and note
    t, _, _ = gui.Integrate(lambda u, t: u * 0, 1., np.ones(1), gui.schemes['RK4'], .3)
    np.testing.assert_allclose(t, [0, .3, .6, .9, 1.])
    s = gui.build_gui(animate=False)
    try:
        wait(s)
        dt, eps, tf, tol = s['sliders'][4:]
        dt.set_val('0,0001')
        eps.set_val('0.002')
        tf.set_val(1)
        s['compute'](); wait(s)
        assert s['dt'] == .0001 and s['eps'] == .002
        np.testing.assert_allclose(np.diff(s['nodes'][0]), .0001)
        assert len(s['t']) <= gui.N_display
        dt.set_val('nan')
        assert dt.val == .0001 and 'introduce' in s['warning'].get_text()
        dt.set_val('0')
        assert dt.val == .0001
        dt.set_val('.02')
        s['compute'](); wait(s)
        for i in range(4):
            s['show_page'](i); wait(s)
            s['goto'](s['t'][-1] * .55)
            plt.imsave(f'tmp/gui-simple-{i}.png', s['render']())
        s['R_mode'].set_active(1)
        assert tol.ax.get_visible()
        s['compute'](); wait(s)
        s['reset'](); wait(s)
        assert dt.val == .02 and eps.val == .001 and not tol.ax.get_visible()
        print('PASS: exact dt, budget, final partial step, direct fields, invalid input, adaptive, reset and four views')
    finally:
        s['close']()
        plt.close('all')


if __name__ == '__main__':
    main()
