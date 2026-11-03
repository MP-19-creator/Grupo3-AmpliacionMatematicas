// Página 2 · INVARIANTES (versión web de page_invariants.py; enunciado 3.2: conmutar integradores y
// contrastar la deriva de energía y momento).
// Los tres esquemas integran EXACTAMENTE el mismo problema con el mismo Δt (o la misma tolerancia).
// La física dice que 2T, L² y |q| no cambian: todo lo que se ve aquí es error numérico.
import { layoutBase, dibujarGrafica, linea, Capa, colorMetodo, css, simlog, marcasSimlog, exp, tarjetaGrafica, nombreIngles } from './graficas_web.js';

const suelo = 1e-17;                         // suelo para el logaritmo de derivas nulas
const metodos = ['Euler', 'Crank-Nicolson', 'RK4'];
const cortos = { 'Euler': 'Euler', 'Crank-Nicolson': 'CN', 'RK4': 'RK4', 'Referencia RK4': 'Ref. RK4' };

export class PaginaConservacion {
  titulo = '2  Invariants';

  constructor(contenedor, contexto) {
    this.contenedor = contenedor;
    this.ctx = contexto;
    this.estado = contexto.estado;
    this.vista = 'derivas';
    this.conSigno = false;
    this.detalle = false;
    this.necesitaDibujo = true;
    this.construirDOM();
  }
  $(s) { return this.contenedor.querySelector(s); }

  construirDOM() {
    this.contenedor.innerHTML = `
    <div class="pagina-graficas">
      <div class="barra-pagina">
        <div class="segmentado mini" id="vista-invariantes"><button data-vista="derivas">Drifts</button><button data-vista="trayectorias">Trajectories</button></div>
        <button class="chip" id="chip-signo">Signed</button>
        <button class="chip oculto" id="chip-detalle">Zoom on time</button>
        <span class="contexto" id="contexto-invariantes"></span>
      </div>
      <div class="cuerpo-graficas" id="graficas-derivas">
        ${tarjetaGrafica('<b>Kinetic energy</b> · |2T/2T<sub>0</sub> − 1|', 'g-energia')}
        ${tarjetaGrafica('<b>Angular momentum</b> · |L²/L²<sub>0</sub> − 1|', 'g-momento')}
        ${tarjetaGrafica('<b>Quaternion norm</b> · ||q| − 1|', 'g-norma')}
        ${tarjetaGrafica('<b>Time step used</b> · Δt(t)', 'g-paso')}
      </div>
      <div class="cuerpo-graficas trayectorias oculto" id="graficas-trayectorias">
        ${tarjetaGrafica('<b>Transverse projection</b> · body frame', 'g-proyeccion')}
        ${tarjetaGrafica('<b>Transverse component</b> · phase', 'g-fase')}
        ${tarjetaGrafica('<b>Transverse perturbation</b> · norm', 'g-perturbacion')}
      </div>
      <aside class="tarjeta lateral" id="lateral-invariantes"></aside>
      <div class="cargando" id="cargando-invariantes"><span>Integrating Euler, Crank–Nicolson and RK4…</span></div>
    </div>`;
    this.$('#vista-invariantes').addEventListener('click', e => e.target.dataset.vista && this.cambiarVista(e.target.dataset.vista));
    this.$('#chip-signo').addEventListener('click', () => { this.conSigno = !this.conSigno; this.redibujar(); });
    this.$('#chip-detalle').addEventListener('click', () => { this.detalle = !this.detalle; this.redibujar(); });
    this.capas = {};
    for (const id of ['g-energia', 'g-momento', 'g-norma', 'g-paso', 'g-proyeccion', 'g-fase', 'g-perturbacion'])
      this.capas[id] = new Capa(this.$(`#${id}`));
    this.actualizarBotones();
  }

  actualizarBotones() {
    this.$('#vista-invariantes').querySelectorAll('button').forEach(b => b.classList.toggle('activo', b.dataset.vista === this.vista));
    this.$('#chip-signo').classList.toggle('activo', this.conSigno);
    this.$('#chip-signo').classList.toggle('oculto', this.vista !== 'derivas');
    this.$('#chip-detalle').classList.toggle('activo', this.detalle);
    this.$('#chip-detalle').classList.toggle('oculto', this.vista !== 'trayectorias');
    this.$('#graficas-derivas').classList.toggle('oculto', this.vista !== 'derivas');
    this.$('#graficas-trayectorias').classList.toggle('oculto', this.vista !== 'trayectorias');
  }
  cambiarVista(vista) { this.vista = vista; this.redibujar(); }
  redibujar() { this.actualizarBotones(); if (this.datos) this.dibujarVista(); }
  mostrar() {}
  cambiarTema() { if (this.datos) this.dibujarVista(); }

  async dibujar() {
    const resultado = this.estado.resultado;
    this.$('#cargando-invariantes').classList.add('visible');
    const datos = await this.ctx.pedirPagina(1);
    this.$('#cargando-invariantes').classList.remove('visible');
    if (!datos || this.estado.resultado !== resultado) return;
    this.datos = datos;
    this.r = resultado;
    this.dibujarVista();
  }

  dibujarVista() {
    this.actualizarBotones();
    if (this.vista === 'derivas') this.dibujarDerivas(); else this.dibujarTrayectorias();
    this.dibujarInstante(this.estado.indice, this.estado.fraccion, this.estado.tiempo);
  }

  // ------------------------------------------------------------ derivas de 2T, L² y |q|
  dibujarDerivas() {
    const { comparacion_metodos: comparacion, apoyo_comparacion: apoyo } = this.datos;
    const elegido = this.r.nombre_metodo, tf = this.r.t.at(-1);
    const ids = ['g-energia', 'g-momento', 'g-norma'];
    ids.forEach((id, j) => {
      let trazas, y;
      if (this.conSigno) {
        let m = 1e-12;
        for (const c of Object.values(apoyo.curvas)) for (const v of c.derivas_signo[j]) if (v !== null) m = Math.max(m, Math.abs(v));
        trazas = metodos.map(n => {
          const c = apoyo.curvas[n];
          return linea(n, c.t, c.derivas_signo[j].map(simlog), { seleccionado: n === elegido, customdata: c.derivas_signo[j],
            hovertemplate: '%{customdata:.2e}' });
        });
        y = { range: [-simlog(m)*1.15, simlog(m)*1.15], ...marcasSimlog(m), zeroline: true, title: { text: 'signed drift' } };
      } else {
        trazas = metodos.map(n => {
          const c = comparacion[n];
          return linea(n, c.t, c.derivas[j].map(v => v === null ? null : Math.max(v, suelo)), { seleccionado: n === elegido });
        });
        y = { type: 'log', range: [-17, 1], tickvals: [1e-16, 1e-12, 1e-8, 1e-4, 1], title: { text: 'relative drift' } };
      }
      dibujarGrafica(this.$(`#${id}`), trazas, layoutBase({ x: { range: [0, tf], title: { text: j === 2 ? 't (s)' : '' } }, y,
        leyenda: j === 0, margen: { b: j === 2 ? 36 : 22 } }));
    });
    // Paso usado: constante con paso fijo; con paso adaptativo se ve cómo lo ajusta cada método.
    let lo = Infinity, hi = 0;
    const trazas = metodos.map(n => {
      const c = comparacion[n];
      for (const h of c.paso) if (h > 0) { lo = Math.min(lo, h); hi = Math.max(hi, h); }
      return linea(n, c.t.slice(1), c.paso, { seleccionado: n === elegido });
    });
    const constante = hi / lo < 1 + 1e-8;
    dibujarGrafica(this.$('#g-paso'), trazas, layoutBase({ x: { range: [0, tf], title: { text: 't (s)' } },
      y: { type: 'log', range: [Math.log10(lo/3), Math.log10(hi*3)], title: { text: 'Δt (s)' }, ...(constante ? { tickvals: [lo], ticktext: [lo.toPrecision(3)] } : {}) } }));

    const filas = metodos.map(n => {
      const c = comparacion[n];
      return `<tr class="${n === elegido ? 'elegido' : ''}"><td><span class="metodo" style="--c:${colorMetodo(n)}"><i></i>${cortos[n]}</span></td>
        ${c.maximos.map(v => `<td>${exp(v)}</td>`).join('')}<td>${c.pasos >= 1e4 ? `${Math.round(c.pasos/1e3)}k` : c.pasos >= 1e3 ? `${(c.pasos/1e3).toFixed(1)}k` : c.pasos}</td></tr>`;
    }).join('');
    const truncados = metodos.filter(n => comparacion[n].aviso);
    this.$('#lateral-invariantes').innerHTML = `
      <div class="rotulo">Max drift · |·|</div>
      <table class="tabla"><thead><tr><th>Scheme</th><th>2T</th><th>L²</th><th>|q|</th><th>N</th></tr></thead><tbody>${filas}</tbody></table>
      <p class="nota">2T, L² and |q| are exact invariants of the rigid body: <b>every curve on this page is numerical error</b>.</p>
      <div class="dato-grande"><span class="rotulo">${this.r.adaptativo ? 'Adaptive step' : 'Fixed step'}</span>
        <b class="mono">${this.r.adaptativo ? `tol ${this.r.tol.toExponential(0)}` : `Δt = ${this.ctx.formatoNumero(this.r.dt_utilizado)} s`}</b></div>
      ${truncados.length ? `<p class="nota aviso">Truncated: ${truncados.map(n => `${cortos[n]} (${comparacion[n].aviso})`).join(' · ')}</p>` : ''}
      <p class="nota"><b style="color:var(--euler)">Euler</b> (order 1): the drift accumulates, as |R(iy)| &gt; 1 predicts.<br>
        <b style="color:var(--cn)">Crank–Nicolson</b> (order 2): it oscillates without accumulating (|R(iy)| = 1).<br>
        <b style="color:var(--rk4)">RK4</b> (order 4): the smallest error at the same Δt.</p>`;
    this.$('#contexto-invariantes').textContent = this.conSigno ? 'Signed: positive grows, negative shrinks · symmetric log scale'
      : 'Same problem, same parameters · compare the size of the numerical error';
  }

  // ------------------------------------------------------------ trayectorias transversales
  dibujarTrayectorias() {
    const apoyo = this.datos.apoyo_comparacion, elegido = this.r.nombre_metodo, tf = this.r.t.at(-1);
    const [j, k] = apoyo.transversales;
    const curvas = Object.entries(apoyo.curvas);
    const referencia = apoyo.curvas['Referencia RK4'];
    const maximo = (c) => Math.max(1e-9, ...referencia.transversal.map(p => Math.abs(p[c]))) * 1.35;
    const [mx, my] = [maximo(0), maximo(1)];
    dibujarGrafica(this.$('#g-proyeccion'), curvas.map(([n, c]) => linea(n, c.transversal.map(p => p[0]), c.transversal.map(p => p[1]),
      { seleccionado: n === elegido, discontinua: n === 'Referencia RK4', hovertemplate: '(%{x:.3f}, %{y:.3f})' })),
      layoutBase({ x: { range: [-mx, mx], title: { text: `ω<sub>${j+1}</sub> (rad/s)` } },
        y: { range: [-my, my], title: { text: `ω<sub>${k+1}</sub> (rad/s)` }, scaleanchor: 'x' }, leyenda: true, hovermode: 'closest' }));

    const P = apoyo.periodo_teorico;
    let ancho = this.detalle ? (P && isFinite(P) ? Math.min(tf, 2*P) : tf/4) : tf;
    ancho = Math.max(ancho, Math.min(tf, this.r.dt_utilizado));
    this.ventana = { ancho, inicio: this.detalle ? Math.min(Math.max(this.estado.tiempo - ancho/2, 0), tf - ancho) : 0 };
    const rango = [this.ventana.inicio, this.ventana.inicio + ancho];
    dibujarGrafica(this.$('#g-fase'), curvas.map(([n, c]) => linea(n, c.t, c.transversal.map(p => p[0]),
      { seleccionado: n === elegido, discontinua: n === 'Referencia RK4' })),
      layoutBase({ x: { range: rango, title: { text: 't (s)' } }, y: { range: [-mx, mx], title: { text: `ω<sub>${j+1}</sub> (rad/s)` } } }));
    const [tg, guia] = apoyo.guia_crecimiento;
    const trazas = curvas.map(([n, c]) => linea(n, c.t, c.amplitud.map(v => Math.max(v ?? suelo, suelo)),
      { seleccionado: n === elegido, discontinua: n === 'Referencia RK4' }));
    if (tg.length > 1) trazas.push({ type: 'scatter', mode: 'lines', x: tg, y: guia, name: 'Local guide ∝ e<sup>λt</sup>',
      line: { color: css('mal'), width: 1.4, dash: 'dot' }, hovertemplate: '%{y:.2e}' });
    dibujarGrafica(this.$('#g-perturbacion'), trazas, layoutBase({ x: { range: rango, title: { text: 't (s)' } },
      y: { type: 'log', title: { text: 'norm (rad/s)' }, tickformat: '.0e' }, leyenda: tg.length > 1 }));

    const filas = curvas.map(([n, c]) => {
      const error = P && isFinite(P) && c.periodo ? 100*(c.periodo/P - 1) : null;
      return `<tr class="${n === elegido ? 'elegido' : ''}"><td><span class="metodo" style="--c:${colorMetodo(n)}"><i></i>${cortos[n]}</span></td>
        <td>${c.periodo ? c.periodo.toPrecision(4) : '—'}</td><td>${error === null ? '—' : error.toPrecision(3)}</td></tr>`;
    }).join('');
    const estable = this.r.eje !== 1;
    this.$('#lateral-invariantes').innerHTML = `
      <div class="rotulo">Mean period · upward crossings</div>
      <table class="tabla"><thead><tr><th>Scheme</th><th>P (s)</th><th>ΔP/P (%)</th></tr></thead><tbody>${filas}</tbody></table>
      <div class="dato-grande"><span class="rotulo">Theory</span><b class="mono">P = ${P && isFinite(P) ? P.toPrecision(4) : '∞'} s</b></div>
      <p class="nota${apoyo.referencia_aviso ? ' aviso' : ''}">Reference: RK4 with Δt/4 (approximate)${apoyo.referencia_aviso ? ' · truncated' : ''}. — means no complete cycles.</p>
      <p class="nota">${estable ? 'Stable spin: the transverse motion is a small ellipse. Compare amplitude and phase.'
        : 'Intermediate axis: the perturbation grows like e<sup>λt</sup> (physics) while the schemes add their own error.'}</p>`;
    this.$('#contexto-invariantes').textContent = (estable ? 'Stable spin: compare amplitude and phase' : 'Intermediate axis: physical growth and numerical error coexist')
      + ' · axes follow the reference';
  }

  // ------------------------------------------------------------ animación
  dibujarInstante(indice, fraccion, tiempo) {
    if (!this.datos) return;
    if (this.vista === 'derivas') {
      for (const id of ['g-energia', 'g-momento', 'g-norma', 'g-paso']) this.capas[id].vertical('t', tiempo);
      return;
    }
    // Con el detalle activo, la ventana sigue al instante actual.
    if (this.detalle && (tiempo < this.ventana.inicio || tiempo > this.ventana.inicio + this.ventana.ancho)) {
      const tf = this.r.t.at(-1);
      this.ventana.inicio = Math.min(Math.max(tiempo - this.ventana.ancho/2, 0), tf - this.ventana.ancho);
      const rango = [this.ventana.inicio, this.ventana.inicio + this.ventana.ancho];
      for (const id of ['g-fase', 'g-perturbacion']) window.Plotly.relayout(this.$(`#${id}`), { 'xaxis.range': rango });
    }
    for (const id of ['g-fase', 'g-perturbacion']) this.capas[id].vertical('t', tiempo, { color: css('tenue') });
    for (const [n, c] of Object.entries(this.datos.apoyo_comparacion.curvas)) {
      const vivo = tiempo <= c.fin, [x, y] = c.marcadores[indice];
      if (!vivo) { this.capas['g-proyeccion'].ocultar(n); this.capas['g-fase'].ocultar(n); continue; }
      this.capas['g-proyeccion'].punto(n, x, y, { color: colorMetodo(n), tam: 9 });
      this.capas['g-fase'].punto(n, tiempo, x, { color: colorMetodo(n), tam: 8 });
    }
  }
  fotograma() {}
}
