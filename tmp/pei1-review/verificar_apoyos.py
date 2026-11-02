"""Verifica los apoyos de defensa sin cambiar esquemas ni soluciones."""
import sys, time, json, warnings
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent, CloseEvent
import PEI1.PEI1 as main
warnings.filterwarnings('error',category=UserWarning)
out=root/'tmp/pei1-review/apoyos'
out.mkdir(exist_ok=True)
checks=[]; metrics=[]
calls=[]
integrate=main.integrar_trayectoria
def tracked(*args,**kwargs):
    calls.append(1)
    return integrate(*args,**kwargs)
main.integrar_trayectoria=tracked
s=main.iniciar_programa(False)
fig=s['figura']; window=fig.canvas.manager.window
window.geometry('1600x950+20+20')
plt.show(block=False); fig.canvas.flush_events()
def click(button):
    x,y=button.ax.transAxes.transform((.5,.5))
    for kind in ('button_press_event','button_release_event'):
        fig.canvas.callbacks.process(kind,MouseEvent(kind,fig.canvas,x,y,button=1))
    fig.canvas.flush_events()
def capture(name):
    fig.canvas.draw()
    plt.imsave(out/(name+'.png'),s['capturar_imagen']())
def check_frames(name):
    fig.canvas.draw()
    count=len(calls)
    artists=[(len(ax.lines),len(ax.collections)) for ax in s['paginas'][s['pagina_actual']].graficas]
    elapsed=[]
    for fraction in np.linspace(.15,.85,22):
        start=time.perf_counter(); s['mostrar_instante'](s['t'][-1]*fraction)
        elapsed.append(time.perf_counter()-start)
    assert len(calls)==count, 'La animación no debe integrar'
    assert artists==[(len(ax.lines),len(ax.collections)) for ax in s['paginas'][s['pagina_actual']].graficas]
    partial=np.asarray(fig.canvas.buffer_rgba()).copy()
    fig.canvas.draw()
    np.testing.assert_array_equal(partial,np.asarray(fig.canvas.buffer_rgba()))
    metrics.append(dict(view=name,window=window.geometry(),median_ms=float(np.median(elapsed[2:])*1000),
        p95_ms=float(np.percentile(elapsed[2:],95)*1000)))

s['selector_eje'].set_active(2)
s['controles_parametros'][5].set_val('.03')
s['controles_parametros'][4].set_val('.15')
s['controles_parametros'][6].set_val(40.)
s['solicitar_calculo']()
assert abs(s['control_dt_deslizador'].val-np.log10(.15))<1e-12
s['control_dt_deslizador'].set_val(np.log10(.2))
assert abs(s['controles_parametros'][4].val-.2)<1e-12
s['controles_parametros'][4].set_val('.15')
s['solicitar_calculo']()
s['mostrar_pagina'](1); fig.canvas.draw()
assert not s.get('error'),s.get('error')
aux=s['apoyo_comparacion']
assert set(s['comparacion_metodos'])=={'Euler','Crank-Nicolson','RK4'}
assert abs(aux['curvas']['Referencia RK4']['periodo']/aux['periodo_teorico']-1)<1e-3
for name,result in s['comparacion_metodos'].items():
    curve=aux['curvas'][name]
    indices=np.linspace(0,len(result['t'])-1,min(len(result['t']),main.max_puntos_curva),dtype=int)
    for j in range(3): np.testing.assert_allclose(np.abs(curve['derivas_signo'][j]),result['derivas'][j][indices],atol=3e-16)
checks.append('Tres integradores originales; referencia y derivas verificadas en los nodos completos')
p=s['paginas'][1]
for width,height in ((1600,950),(1200,800)):
    window.geometry(f'{width}x{height}+20+20'); fig.canvas.flush_events()
    s['mostrar_pagina'](0); capture(f'{width}-movimiento')
    s['mostrar_pagina'](1)
    if p.vista!='Derivas': click(p.controles[0])
    if p.con_signo: click(p.controles[1])
    check_frames(f'{width}-derivas'); capture(f'{width}-derivas')
    count=len(calls); click(p.controles[1])
    assert p.con_signo and len(calls)==count
    check_frames(f'{width}-signo'); capture(f'{width}-signo')
    click(p.controles[0]); assert p.vista=='Trayectorias'
    check_frames(f'{width}-trayectorias'); capture(f'{width}-trayectorias')
    s['mostrar_instante'](30.)
    if p.detalle: click(p.controles[2])
    click(p.controles[2])
    assert p.grafica_fase.get_xlim()[0]>0
    check_frames(f'{width}-detalle'); capture(f'{width}-detalle')
    s['mostrar_pagina'](2); assert not s.get('error')
    est=s['paginas'][2]
    if est.vista!='Regiones': click(est.control_vista)
    check_frames(f'{width}-regiones'); capture(f'{width}-regiones')
    count=len(calls); click(est.control_vista)
    assert est.vista=='Modo' and len(calls)==count
    demo=s['estabilidad']['demostracion']
    for name,curve in demo['curvas'].items():
        expected={'Euler':'Euler','Crank-Nicolson':'Crank_Nicolson','RK4':'RK4','Euler implícito':'Euler_implicit'}[name]
        r=main.stability_function(expected,1j*demo['y'])
        np.testing.assert_array_equal(curve['orbita'],r**demo['n'])
    check_frames(f'{width}-modo'); capture(f'{width}-modo')
    s['mostrar_pagina'](3); assert not s.get('error')
    capture(f'{width}-precision')
checks.append('Cuatro páginas, variantes y controles en 1600×950 y 1200×800')
checks.append('Cambiar representación y animar: cero integraciones y cero artistas nuevos')
checks.append('Repintado parcial y completo idénticos en todas las variantes')
checks.append('Modo oscilatorio coincide con R(z)^n; no cambia el conjunto de integradores del satélite')
# Local instability guide and zero perturbation.
s['selector_eje'].set_active(1)
s['controles_parametros'][5].set_val('.001')
s['solicitar_calculo'](); s['mostrar_pagina'](1)
assert len(s['apoyo_comparacion']['guia_crecimiento'][0])>1
capture('1200-crecimiento-intermedio')
s['controles_parametros'][5].set_val('0')
s['solicitar_calculo']()
assert len(s['apoyo_comparacion']['guia_crecimiento'][0])==0
assert all(not np.isfinite(c['periodo']) for c in s['apoyo_comparacion']['curvas'].values())
checks.append('Guía limitada al régimen local; perturbación nula sin periodo medido ficticio')
# A shortened method/reference must never extrapolate its moving marker.
ref=s['apoyo_comparacion']['curvas']['Referencia RK4']
fin=ref['fin']; ref['fin']=fin/4
s['mostrar_instante'](s['t'][-1]*.8)
assert len(p.marcadores['Referencia RK4'][0].get_xdata())==0
ref['fin']=fin
checks.append('No se extrapolan los marcadores de trayectorias truncadas')
# Reset restores both numerical input controls, including exact typed dt.
s['restablecer_parametros']()
assert s['controles_parametros'][4].val==.02
assert abs(s['control_dt_deslizador'].val-np.log10(.02))<1e-12
checks.append('Campo preciso y deslizador logarítmico Δt sincronizados y reiniciables')
fig.canvas.callbacks.process('close_event',CloseEvent('close_event',fig.canvas))
assert s['cerrada']
plt.close(fig)
(out/'verificacion.json').write_text(json.dumps(dict(checks=checks,frames=metrics),indent=2,ensure_ascii=False),encoding='utf-8')
for check in checks: print('PASS',check,flush=True)
print(json.dumps(metrics,indent=2),flush=True)
