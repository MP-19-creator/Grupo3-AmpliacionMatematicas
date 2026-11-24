import sys, time, json, os
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import PEI1.PEI1 as main

label = sys.argv[1]
out = Path(__file__).resolve().parent
timings = {}
calls = {}
for name in ('integrar_trayectoria', 'preparar_datos_movimiento', 'comparar_metodos',
             'preparar_datos_estabilidad', 'calcular_estudio_error'):
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
results = {'backend':matplotlib.get_backend(), 'version':matplotlib.__version__, 'pages':[]}
np.savez(out/f'{label}-solution.npz', t=s['solucion_completa'][0], U=s['solucion_completa'][1])
for size in ((1600,950),(1200,800)):
    window.geometry(f'{size[0]}x{size[1]}+20+20')
    fig.canvas.flush_events()
    for i in range(4):
        start=time.perf_counter(); s['mostrar_pagina'](i); prepared=time.perf_counter()-start
        fig.canvas.draw()
        update=[]; draw=[]
        for fraction in np.linspace(.2,.8,7):
            # Suppress idle scheduling to measure artist updates and drawing separately.
            idle=fig.canvas.draw_idle; fig.canvas.draw_idle=lambda: None
            start=time.perf_counter(); s['mostrar_instante'](s['t'][-1]*fraction); update.append(time.perf_counter()-start)
            fig.canvas.draw_idle=idle
            start=time.perf_counter(); fig.canvas.draw(); draw.append(time.perf_counter()-start)
        plt.imsave(out/f'{label}-{size[0]}-page-{i+1}.png', s['capturar_imagen']())
        results['pages'].append(dict(size=size,page=i+1,prepare=prepared,update_median=float(np.median(update)),draw_median=float(np.median(draw))))
        print(label,size,i+1,results['pages'][-1],flush=True)
before=dict(calls); start=time.perf_counter(); s['solicitar_calculo'](); fig.canvas.draw()
results['repeat_calculate']={'seconds':time.perf_counter()-start,'calls':{k:calls[k]-before.get(k,0) for k in calls}}
before=dict(calls)
for i in (0,1,2,3,0): s['mostrar_pagina'](i)
results['revisit_calls']={k:calls[k]-before.get(k,0) for k in calls}
results['timings']=timings
(out/f'{label}-timings.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('DONE',label,flush=True)
# Leave the last page available for native inspection.
if '--stay' in sys.argv: plt.show()
else: s['cerrar_interfaz'](); plt.close(fig)
