"""Cadencia efectiva de las dos vistas nuevas en el bucle real de Tk."""
import sys,time,json
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(root))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from PEI1.PEI1 import iniciar_programa
s=iniciar_programa(False)
fig=s['figura']; window=fig.canvas.manager.window
window.geometry('1600x950+20+20'); plt.show(block=False); fig.canvas.flush_events()
results=[]
for i in (1,2):
    s['mostrar_pagina'](i)
    s['paginas'][i].cambiar_vista()
    fig.canvas.flush_events(); fig.canvas.draw()
    timer=fig.canvas.new_timer(interval=33); s['temporizador']=timer
    ticks=[]
    def tick():
        ticks.append(time.perf_counter()); s['avanzar_animacion']()
    timer.add_callback(tick)
    timer.start(); window.after(3000,window.quit); window.mainloop(); timer.stop()
    intervals=np.diff(ticks)
    result=dict(page=i+1,view=s['paginas'][i].vista,frames=len(ticks),fps=float(1/np.mean(intervals)),
        median_ms=float(np.median(intervals)*1000),p95_ms=float(np.percentile(intervals,95)*1000))
    results.append(result); print(result,flush=True)
s['cerrar_interfaz'](); plt.close(fig)
(root/'tmp/pei1-review/apoyos/cadencia.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
