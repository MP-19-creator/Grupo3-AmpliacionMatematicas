"""Medición TkAgg. --baseline lee HEAD sin cambiar el árbol de trabajo."""
import sys, time, json, subprocess, types, importlib
from pathlib import Path
import numpy as np
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

if '--baseline' in sys.argv:
    for name in ('style', 'page_attitude', 'page_invariants', 'page_stability', 'page_richardson', 'gui'):
        fullname = 'active.gui_reactive.' + name
        parent = importlib.import_module('active.gui_reactive')
        module = types.ModuleType(fullname)
        module.__file__ = str(root / ('active/gui_reactive/' + name + '.py'))
        sys.modules[fullname] = module
        setattr(parent, name, module)
        source = subprocess.check_output(['git', 'show', 'HEAD:active/gui_reactive/'+name+'.py'], cwd=root).decode('utf-8')
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
    main = types.ModuleType('baseline_main')
    main.__file__ = str(root / 'PEI1/PEI1.py')
    source = subprocess.check_output(['git', 'show', 'HEAD:PEI1/PEI1.py'], cwd=root).decode('utf-8')
    exec(compile(source, main.__file__, 'exec'), main.__dict__)
else:
    import PEI1.PEI1 as main

label = sys.argv[1]
out = Path(__file__).resolve().parent
timings, calls = {}, {}
for name in ('integrar_trayectoria', 'calcular_trayectoria', 'preparar_datos_movimiento',
             'comparar_metodos', 'preparar_datos_estabilidad', 'calcular_estudio_error'):
    original = getattr(main, name)
    def wrap(*a, _name=name, _fn=original, **kw):
        start = time.perf_counter()
        try: return _fn(*a, **kw)
        finally:
            timings.setdefault(_name, []).append(time.perf_counter()-start)
            calls[_name] = calls.get(_name, 0)+1
    setattr(main, name, wrap)

s = main.iniciar_programa(animar=False)
fig = s['figura']
window = fig.canvas.manager.window
window.geometry('1600x950+20+20')
plt.show(block=False)
fig.canvas.flush_events()
results = {'backend':matplotlib.get_backend(), 'version':matplotlib.__version__,
           'parameters':dict(I=[1,2,3],Omega=1,eps=.001,tf=80,dt=.02,tol=1e-6,metodo='RK4',adaptativo=False,eje=1),
           'pages':[]}
np.savez(out/f'{label}-solution.npz', t=s['solucion_completa'][0], U=s['solucion_completa'][1])
for size in ((1600,950),(1200,800)):
    window.geometry(f'{size[0]}x{size[1]}+20+20')
    fig.canvas.flush_events()
    for i in range(4):
        start=time.perf_counter(); s['mostrar_pagina'](i); prepared=time.perf_counter()-start
        fig.canvas.flush_events(); fig.canvas.draw()
        update, draw, frames = [], [], []
        idle=fig.canvas.draw_idle
        fig.canvas.draw_idle=lambda: None
        try:
            for fraction in np.linspace(.2,.8,33):
                start=time.perf_counter()
                s['mostrar_instante'](s['t'][-1]*fraction)
                total=time.perf_counter()-start
                if '--baseline' in sys.argv:
                    render_start=time.perf_counter()
                    if i != 3: fig.canvas.draw()
                    render=time.perf_counter()-render_start if i != 3 else 0.
                    frame=total+render
                else:
                    render=s.get('tiempo_dibujo_instante',0.) if i != 3 else 0.
                    frame=total
                    total=max(0.,total-render)
                update.append(total); draw.append(render); frames.append(frame)
        finally: fig.canvas.draw_idle=idle
        results['pages'].append(dict(size=size,canvas=fig.canvas.get_width_height(),page=i+1,
            prepare=prepared,update_median=float(np.median(update[3:])),
            draw_median=float(np.median(draw[3:])),frame_median=float(np.median(frames[3:])),
            frame_p95=float(np.percentile(frames[3:],95))))
        plt.imsave(out/f'{label}-{size[0]}-page-{i+1}.png', s['capturar_imagen']())
        print(label,results['pages'][-1],flush=True)
before=dict(calls); start=time.perf_counter(); s['solicitar_calculo'](); fig.canvas.draw()
results['repeat_calculate']={'seconds':time.perf_counter()-start,'calls':{k:calls[k]-before.get(k,0) for k in calls}}
before=dict(calls)
for i in (0,1,2,3,0): s['mostrar_pagina'](i)
results['revisit_calls']={k:calls[k]-before.get(k,0) for k in calls}
results['timings']=timings
if '--baseline' not in sys.argv:
    window.geometry('1600x950+20+20'); fig.canvas.flush_events()
    s['mostrar_pagina'](0); fig.canvas.draw()
    ticks=[]
    timer=fig.canvas.new_timer(interval=33)
    s['temporizador']=timer
    def tick():
        ticks.append(time.perf_counter()); s['avanzar_animacion']()
    timer.add_callback(tick)
    timer.start(); window.after(4000, window.quit); window.mainloop(); timer.stop()
    intervals=np.diff(ticks)
    results['playback']={'frames':len(ticks),'fps':float(1/np.mean(intervals)),
        'interval_median_ms':float(np.median(intervals)*1000),'interval_p95_ms':float(np.percentile(intervals,95)*1000)}
    print('PLAYBACK',results['playback'],flush=True)
(out/f'{label}-timings.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('DONE',label,flush=True)
if '--stay' in sys.argv:
    fig.canvas.manager.set_window_title('PEI1 · revisión final')
    s['temporizador'].start()
    plt.show()
else:
    s['cerrar_interfaz'](); plt.close(fig)
