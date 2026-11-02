"""Regresión científica y controles reales TkAgg, sin modificar el motor."""
import sys, types, subprocess, json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent, MouseEvent, CloseEvent
import PEI1.PEI1 as actual
original=types.ModuleType('original')
original.__file__=str(root/'PEI1/PEI1.py')
source=subprocess.check_output(['git','show','HEAD:PEI1/PEI1.py'],cwd=root).decode('utf-8')
exec(compile(source,original.__file__,'exec'),original.__dict__)
checks=[]
for name in actual.metodos:
    for adaptive in (False,True):
        p=dict(I=(1.,2.,3.),eje=1,Omega=1.,eps=.001,tf=6.,dt=.03,tol=1e-6,
               nombre_metodo=name,adaptativo=adaptive)
        before=original.calcular_trayectoria(dict(p,metodo=original.metodos[name]))
        after=actual.calcular_trayectoria(dict(p,metodo=actual.metodos[name]))
        for key in ('t','U','derivas','indices_dibujo','puntas_estela','instantes_volteo'):
            np.testing.assert_array_equal(before[key],after[key],err_msg=f'{name}/{adaptive}/{key}')
        for a,b in zip(before['solucion_completa'],after['solucion_completa']): np.testing.assert_array_equal(a,b)
        for key in ('rotaciones','vector_momento','dimensiones'):
            np.testing.assert_array_equal(before['movimiento'][key],after['movimiento'][key])
        checks.append(f'Equivalencia exacta: {name}, adaptativo={adaptive}')
base=np.load(root/'tmp/pei1-review/baseline-solution.npz')
final=np.load(root/'tmp/pei1-review/final-solution.npz')
for key in base.files: np.testing.assert_array_equal(base[key],final[key])
checks.append('Equivalencia exacta: caso inicial completo (4001 nodos)')
s=actual.iniciar_programa(animar=True)
fig=s['figura']; window=fig.canvas.manager.window
window.geometry('1200x800+20+20'); plt.show(block=False); fig.canvas.flush_events()
# Keep automated control assertions deterministic, using the actual Tk canvas.
s['temporizador'].stop()
def key(k): fig.canvas.callbacks.process('key_press_event',KeyEvent('key_press_event',fig.canvas,key=k))
def click(ax,x=None):
    px,py=ax.transAxes.transform((.5,.5)) if x is None else ax.transData.transform((x,0))
    for kind in ('button_press_event','button_release_event'):
        fig.canvas.callbacks.process(kind,MouseEvent(kind,fig.canvas,px,py,button=1))
for i in range(4):
    click(s['pestanas'][i].ax); fig.canvas.flush_events()
    assert s['pagina_actual']==i and s['lista_para_dibujar'] and not s.get('error')
    key(str((i+1)%4+1)); assert s['pagina_actual']==(i+1)%4
checks.append('Cuatro pestañas: clic y teclado')
s['mostrar_pagina'](0); fig.canvas.draw()
s['mostrar_instante'](0.)
key(' '); assert not s['reproduciendo']
key('right'); assert s['tiempo_actual']>0
key('left'); assert s['tiempo_actual']==0
click(s['paginas'][0].linea_tiempo,s['t'][-1]*.5)
assert abs(s['tiempo_actual']-s['t'][-1]*.5)<1
key('+'); assert s['velocidad']==2
key('-'); assert s['velocidad']==1
key(' '); assert s['reproduciendo']
key('v'); fig.canvas.draw()
checks.append('Reproducción, pausa, velocidad, búsqueda temporal y cámaras')
for index in range(3):
    s['selector_metodo'].set_active(index)
    s['controles_parametros'][6].set_val(6.)
    s['solicitar_calculo'](); assert s['lista_para_dibujar']
for index in (1,0):
    s['selector_paso'].set_active(index)
    assert s['controles_parametros'][7].ax.get_visible()==bool(index)
    s['solicitar_calculo'](); assert s['adaptativo']==bool(index)
for index in (0,2,1):
    s['selector_eje'].set_active(index); s['solicitar_calculo'](); assert s['eje']==index
checks.append('Tres métodos, tres ejes y ambos tipos de paso')
old=s['solucion_completa'][1].copy()
s['controles_parametros'][0].set_val(4.)
s['solicitar_calculo']()
np.testing.assert_array_equal(old,s['solucion_completa'][1])
assert 'No se pudo' in s['texto_aviso'].get_text()
s['restablecer_parametros'](); assert s['tiempo_actual']==0 and not s['cambios_pendientes']
key('right'); s['restablecer_parametros'](); assert s['tiempo_actual']==0
checks.append('Error de inercias conserva datos; reinicio con y sin cambios')
# Changing the study alone must never reintegrate the trajectory.
calls=[]; integrate=actual.integrar_trayectoria
def track(*a,**kw): calls.append(1); return integrate(*a,**kw)
actual.integrar_trayectoria=track
s['mostrar_pagina'](3)
s['paginas'][3].control_tf_estudio.set_val(5.)
s['solicitar_calculo']()
assert s['estudio_error']['tf']==5 and not calls and not s.get('estudio_pendiente')
s['paginas'][3].control_tf_estudio.set_val(20.)
s['solicitar_calculo'](); assert not calls
checks.append('Intervalo de precisión independiente y reutilización de estudios')
for size in ((1600,950),(1200,800)):
    window.geometry(f'{size[0]}x{size[1]}+20+20'); fig.canvas.flush_events()
    for i in range(4):
        s['mostrar_pagina'](i); fig.canvas.draw()
        counts=[(len(ax.lines),len(ax.collections)) for ax in s['paginas'][i].graficas]
        for fraction in np.linspace(.1,.9,12): s['mostrar_instante'](s['t'][-1]*fraction)
        assert counts==[(len(ax.lines),len(ax.collections)) for ax in s['paginas'][i].graficas]
        partial=np.asarray(fig.canvas.buffer_rgba()).copy()
        fig.canvas.draw()
        full=np.asarray(fig.canvas.buffer_rgba()).copy()
        # Identical canvas after a partial update and a rebuilt background.
        np.testing.assert_array_equal(partial,full,err_msg=f'partial redraw page {i+1}')
checks.append('Redimensionado de cuatro páginas; artistas estables; repintado parcial idéntico')
s['mostrar_pagina'](0); fig.canvas.draw()
fig.savefig(root/'tmp/pei1-review/export-check.png')
s['mostrar_instante'](s['t'][-1]*.5); fig.canvas.flush_events()
assert s['capturar_imagen']().shape[2]==4
checks.append('Captura y exportación PNG con cuerpo 3D')
fig.canvas.callbacks.process('close_event',CloseEvent('close_event',fig.canvas))
assert s['cerrada'] and s['temporizador']._timer is None
plt.close(fig)
checks.append('Cierre detiene el temporizador')
(root/'tmp/pei1-review/verificacion.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
for check in checks: print('PASS',check,flush=True)
