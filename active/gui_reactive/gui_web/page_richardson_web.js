// Página 4 · RICHARDSON Y ORDEN DE CONVERGENCIA (versión web de page_richardson.py;
// enunciado 3: estimación de error por extrapolación de Richardson).
// No conocemos la solución exacta, pero sí cómo encoge el error de un esquema de orden q al partir
// el paso por dos: E_N ~ C Δt^q. Integrando con N y con 2N pasos:
//     U_N − U_2N = E_N − E_2N = E_N (1 − 2^−q)   →   E_N ≈ (U_N − U_2N) / (1 − 2^−q)
import { layoutBase, dibujarGrafica, linea, colorMetodo, css, tarjetaGrafica, nombreIngles, exp } from './graficas_web.js';

export class PaginaPrecision {
  titulo = '4  Richardson & order';

  constructor(contenedor, contexto) {
    this.contenedor = contenedor;
    this.ctx = contexto;
    this.estado = contexto.estado;
    this.necesitaDibujo = true;
    this.construirDOM();
  }
  $(s) { return this.contenedor.querySelector(s); }

  construirDOM() {
    const c = this.estado.configuracion.controles.tf_estudio;
    this.contenedor.innerHTML = `
    <div class="pagina-graficas">
      <div class="barra-pagina">
        <span class="rotulo">Study interval</span>
        <input type="range" id="tf-estudio" min="${c.minimo}" max="${c.maximo}" step="${c.paso}" value="${this.estado.tfEstudio}">
        <b class="mono" id="tf-estudio-valor">${this.estado.tfEstudio} s</b>
        <button class="chip" id="boton-estudio">Run study</button>
        <span class="contexto" id="contexto-precision"></span>
      </div>
      <div class="cuerpo-graficas trayectorias" id="graficas-precision">
        ${tarjetaGrafica('<b>Convergence</b> · slope = −order', 'g-convergencia')}
        ${tarjetaGrafica('<b>Error along the trajectory</b> · Richardson vs reference', 'g-error')}
        <div class="tarjeta explicacion">
          <div class="rotulo">How the error is estimated without the exact solution</div>
          <div class="formula-grande"><span>E<sub>N</sub> ≈</span><span class="fraccion"><span>U<sub>N</sub> − U<sub>2N</sub></span><span>1 − 2<sup>−q</sup></span></span></div>
          <p class="nota">A scheme of order q makes the error shrink like Δt<sup>q</sup>. Halving the step divides the difference
            D = |U<sub>N</sub>(t<sub>f</sub>) − U<sub>2N</sub>(t<sub>f</sub>)| by 2<sup>q</sup>:
            <b style="color:var(--euler)">2</b> for Euler, <b style="color:var(--cn)">4</b> for Crank–Nicolson,
            <b style="color:var(--rk4)">16</b> for RK4. On a log–log plot that is a straight line of slope −q.</p>
        </div>
      </div>
      <aside class="tarjeta lateral" id="lateral-precision"></aside>
      <div class="cargando" id="cargando-precision"><span>Integrating with N, 2N, 4N… steps</span></div>
    </div>`;
    const control = this.$('#tf-estudio');
    const pintar = () => control.style.setProperty('--pct', `${100*(control.value - c.minimo)/(c.maximo - c.minimo)}%`);
    pintar();
    control.addEventListener('input', () => {
      pintar();
      this.$('#tf-estudio-valor').textContent = `${control.value} s`;
      const pendiente = +control.value !== this.estudiado;
      this.$('#boton-estudio').classList.toggle('activo', pendiente);
      this.$('#contexto-precision').textContent = pendiente ? 'Interval changed · press Run study' : this.resumen ?? '';
    });
    this.$('#boton-estudio').addEventListener('click', () => {
      this.estado.tfEstudio = +control.value;
      this.dibujar();
    });
  }
  mostrar() {}
  cambiarTema() { if (this.datos) this.dibujarGraficas(); }

  async dibujar() {
    const resultado = this.estado.resultado;
    // El estudio integra cada esquema con N, 2N, 4N… pasos: puede tardar unos segundos (igual que en la v1).
    const cargando = this.$('#cargando-precision'), texto = cargando.querySelector('span'), inicio = performance.now();
    cargando.classList.add('visible');
    const reloj = setInterval(() => {
      texto.textContent = `Integrating each scheme with N, 2N, 4N… steps · ${((performance.now() - inicio)/1000).toFixed(0)} s`;
    }, 250);
    const datos = await this.ctx.pedirPagina(3);
    clearInterval(reloj);
    texto.textContent = 'Integrating each scheme with N, 2N, 4N… steps';
    cargando.classList.remove('visible');
    if (!datos || this.estado.resultado !== resultado) return;
    this.datos = datos.estudio_error;
    this.r = resultado;
    this.estudiado = this.datos.tf;
    this.$('#boton-estudio').classList.remove('activo');
    this.dibujarGraficas();
  }

  dibujarGraficas() {
    const d = this.datos, elegido = this.r.nombre_metodo;
    const trazas = [];
    for (const [n, c] of Object.entries(d.curvas_convergencia)) {
      const validos = c.N.map((_, i) => i).filter(i => c.D[i] !== null && c.D[i] > 0);
      const orden = c.pendiente === null ? '—' : (-c.pendiente).toFixed(2);
      trazas.push(linea(n, validos.map(i => Math.log10(c.N[i])), validos.map(i => Math.log10(c.D[i])),
        { seleccionado: n === elegido, mode: 'lines+markers', marker: { size: n === elegido ? 8 : 6 }, name: `${nombreIngles[n]} · order ${orden}`,
          hovertemplate: 'log N = %{x:.2f}<br>log D = %{y:.2f}' }));
      if (c.indices_ajuste.length >= 2 && c.pendiente !== null) {
        const x = c.indices_ajuste.map(i => Math.log10(c.N[i]));
        trazas.push({ type: 'scatter', mode: 'lines', x, y: x.map(v => c.pendiente*v + c.b), showlegend: false, hoverinfo: 'skip',
          line: { color: colorMetodo(n), width: 1.2, dash: 'dash' }, opacity: .6 });
      }
    }
    dibujarGrafica(this.$('#g-convergencia'), trazas, layoutBase({ x: { title: { text: 'log<sub>10</sub> N' } },
      y: { title: { text: 'log<sub>10</sub> D' } }, leyenda: true, hovermode: 'closest',
      legend: { orientation: 'v', x: .02, y: .02, xanchor: 'left', yanchor: 'bottom', font: { size: 11, color: css('texto-2') } } }));

    const [t, estimado, referencia, N] = d.errores;
    const salto = Math.max(1, Math.floor(N / 800)), indices = t.map((_, i) => i).filter(i => i > 0 && i % salto === 0);
    const suelo = (v) => v === null ? null : Math.max(v, 1e-17);
    if (estimado) {
      dibujarGrafica(this.$('#g-error'), [
        linea(elegido, indices.map(i => t[i]), indices.map(i => suelo(estimado[i])), { seleccionado: true, name: 'Richardson estimate' }),
        { ...linea('RK4', indices.map(i => t[i]), indices.map(i => suelo(referencia[i])), { discontinua: true, name: 'Reference RK4 · 8N steps' }),
          line: { color: css('punto'), width: 1.4, dash: 'dash' } },
      ], layoutBase({ x: { range: [0, t.at(-1)], title: { text: 't (s)' } }, y: { type: 'log', title: { text: '|error|' }, dtick: 1 }, leyenda: true }));
    } else {
      dibujarGrafica(this.$('#g-error'), [], layoutBase({ x: { visible: false }, y: { visible: false },
        annotations: [{ text: 'The scheme diverges in this interval. Reduce Δt.', showarrow: false, font: { color: css('aviso'), size: 13 } }] }));
    }

    const c = d.curvas_convergencia[elegido];
    const medido = c.pendiente === null ? null : -c.pendiente;
    const filas = c.N.map((n, i) => `<tr${i >= c.indices_ajuste[0] && i <= c.indices_ajuste.at(-1) ? ' class="ajuste"' : ''}>
      <td>${n.toLocaleString('en')}</td><td>${(d.tf / n).toFixed(4)}</td><td>${exp(c.D[i], 2)}</td>
      <td>${i < c.ordenes.length && c.ordenes[i] !== null ? c.ordenes[i].toFixed(2) : '—'}</td></tr>`).join('');
    const acuerdo = medido !== null && Math.abs(medido - this.r.orden) < .25;
    this.$('#lateral-precision').innerHTML = `
      <div class="rotulo"><span style="color:${colorMetodo(elegido)}">${nombreIngles[elegido]}</span> · order of convergence</div>
      <div class="ordenes">
        <div><span class="rotulo">Theory</span><b class="mono">${this.r.orden}</b></div>
        <div><span class="rotulo">Measured</span><b class="mono" style="color:${acuerdo ? 'var(--bien)' : 'var(--aviso)'}">${medido === null ? '—' : medido.toFixed(2)}</b></div>
      </div>
      <table class="tabla"><thead><tr><th>N</th><th>Δt</th><th>D</th><th>order</th></tr></thead><tbody>${filas}</tbody></table>
      <p class="nota">Highlighted rows: straight stretch used for the fit. Local order = log<sub>2</sub>(D<sub>N</sub>/D<sub>2N</sub>).</p>`;
    this.resumen = `Study over [0, ${d.tf}] s · computed in ${d.tiempo_calculo.toFixed(2)} s`;
    this.$('#contexto-precision').textContent = this.resumen;
  }

  dibujarInstante() {}
  fotograma() {}
}
