"""Cadencia real Tk, misma ventana y parámetros de comparacion.py."""
import sys, time, json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from PEI1.PEI1 import iniciar_programa
s=iniciar_programa(False)
fig=s['figura']; window=fig.canvas.manager.window
window.geometry('1600x950+20+20')
plt.show(block=False); fig.canvas.flush_events(); fig.canvas.draw()
ticks=[]; timer=fig.canvas.new_timer(interval=33); s['temporizador']=timer
def tick():
    ticks.append(time.perf_counter()); s['avanzar_animacion']()
timer.add_callback(tick)
timer.start(); window.after(4000,window.quit); window.mainloop(); timer.stop()
intervals=np.diff(ticks)
result=dict(frames=len(ticks),fps=float(1/np.mean(intervals)),
    interval_median_ms=float(np.median(intervals)*1000),interval_p95_ms=float(np.percentile(intervals,95)*1000))
path=root/'tmp/pei1-review/final-timings.json'
data=json.loads(path.read_text(encoding='utf-8'))
data['playback_before_timer_adjustment']=data['playback']
data['playback']=result
path.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(result,flush=True)
s['cerrar_interfaz'](); plt.close(fig)
