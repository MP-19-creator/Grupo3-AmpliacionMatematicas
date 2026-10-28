import os
os.environ['MPLBACKEND'] = 'Agg'
import sys, time, subprocess, types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib.pyplot as plt
from active.gui_reactive import gui

class NeverCancelled:
    def is_set(self): return False

def wait_ready(s, timeout=180):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        s['poll']()
        if s.get('error'): raise AssertionError(s['error'])
        if not s['jobs'] and s['ready']: return
        time.sleep(.05)
    raise AssertionError('Calculation timeout')

def main():
    out=Path('tmp/visual-review'); out.mkdir(parents=True,exist_ok=True)
    baseline=types.ModuleType('active.gui_reactive._baseline')
    source=subprocess.run(['git','show','HEAD:active/gui_reactive/gui.py'],check=True,capture_output=True,encoding='utf-8').stdout
    baseline.__file__=gui.__file__
    exec(compile(source,gui.__file__,'exec'),baseline.__dict__)
    for name in gui.schemes:
        for adaptive in (False,True):
            p=dict(I=(1.,2.,3.),axis=1,Omega=1.,eps=.001,tf=10.,dt=.03,tol=1e-6,name=name,adaptive=adaptive,scheme=gui.schemes[name])
            before=baseline._calculate_solution(p,NeverCancelled())
            after=gui._calculate_solution(p,NeverCancelled())
            for key in ('t','U','drifts'):
                np.testing.assert_array_equal(before[key],after[key])
    print('PASS: exact numerical equivalence for all 3 schemes, fixed and adaptive',flush=True)
    s=gui.build_gui(animate=False)
    try:
        wait_ready(s)
        for i in range(4):
            s['show_page'](i); wait_ready(s)
            s['goto'](s['t'][-1]*.55)
            plt.imsave(out/f'view-{i+1}.png',s['render']())
            print(f'PASS: page {i+1} rendered',flush=True)
        s['show_page'](0)
        for i in range(3):
            s['R_scheme'].set_active(i); s['compute'](); wait_ready(s)
        for i in (1,0):
            s['R_mode'].set_active(i); s['compute'](); wait_ready(s)
        for i in (0,2,1):
            s['R_axis'].set_active(i); s['compute'](); wait_ready(s)
        old=s['U'].copy()
        s['sliders'][0].set_val(4.)
        s['compute']()
        assert not s['busy'] and 'I₁ < I₂ < I₃' in s['warning'].get_text()
        np.testing.assert_array_equal(old,s['U'])
        s['reset'](); wait_ready(s)
        s['buttons'][0]._observers.process('clicked',None)
        assert not s['playing']
        s['goto'](10.)
        assert abs(s['tp']-10)<1e-10
        s['frame']()
        print('PASS: scheme/mode/axis changes, invalid inertia, reset, pause, seek, frame',flush=True)
    finally:
        s['close'](); plt.close('all')

if __name__=='__main__': main()
