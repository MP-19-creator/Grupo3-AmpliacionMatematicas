// Página 2 · INVARIANTES (versión web de page_invariants.py; enunciado 3.2: conmutar integradores y
// contrastar la deriva de energía y momento).
// Los cuatro esquemas integran EXACTAMENTE el mismo problema con el mismo Δt (o la misma tolerancia).
// La física dice que 2T y L² no cambian: todo lo que se ve aquí es error numérico.
import { layoutBase, dibujarGrafica, linea, Capa, colorMetodo, css, simlog, marcasSimlog, tarjetaGrafica } from './graficas_web.js';

const suelo = 1e-17;                         // suelo para el logaritmo de derivas nulas
const metodos = ['Euler', 'Euler implícito', 'Crank-Nicolson', 'RK4'];
const cortos = { 'Euler': 'Euler', 'Euler implícito': 'Impl. Euler', 'Crank-Nicolson': 'CN', 'RK4': 'RK4', 'Referencia RK4': 'Ref. RK4' };

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
    <div class="pagina-graficas sin-lateral">
      <div class="barra-pagina">
        <div class="segmentado mini" id="vista-invariantes"><button data-vista="derivas">Drifts</button><button data-vista="trayectorias">Trajectories</button></div>
        <button class="chip" id="chip-signo">Signed</button>
        <button class="chip oculto" id="chip-detalle">Zoom on time</button>
        <span class="contexto" id="contexto-invariantes"></span>
      </div>
      <div class="cuerpo-graficas derivas" id="graficas-derivas">
        ${tarjetaGrafica('<b>Kinetic energy</b> · |2T/2T<sub>0</sub> − 1|', 'g-energia')}
        ${tarjetaGrafica('<b>Angular momentum</b> · |L²/L²<sub>0</sub> − 1|', 'g-momento')}
      </div>
      <div class="cuerpo-graficas trayectorias oculto" id="graficas-trayectorias">
        ${tarjetaGrafica('<b>Transverse projection</b> · body frame', 'g-proyeccion')}
        ${tarjetaGrafica('<b>Transverse component</b> · phase', 'g-fase')}
        ${tarjetaGrafica('<b>Transverse perturbation</b> · norm', 'g-perturbacion')}
      </div>
      <div class="cargando" id="cargando-invariantes"><span>Integrating Euler, implicit Euler, Crank–Nicolson and RK4…</span></div>
    </div>`;
    this.$('#vista-invariantes').addEventListener('click', e => e.target.dataset.vista && this.cambiarVista(e.target.dataset.vista));
    this.$('#chip-signo').addEventListener('click', () => { this.conSigno = !this.conSigno; this.redibujar(); });
    this.$('#chip-detalle').addEventListener('click', () => { this.detalle = !this.detalle; this.redibujar(); });
    this.capas = {};
    for (const id of ['g-energia', 'g-momento', 'g-proyeccion', 'g-fase', 'g-perturbacion'])
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

  // ------------------------------------------------------------ derivas de 2T y L²
  dibujarDerivas() {
    const { comparacion_metodos: comparacion, apoyo_comparacion: apoyo } = this.datos;
    const elegido = this.r.nombre_metodo, tf = this.r.t.at(-1);
    const ids = ['g-energia', 'g-momento'];
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
      const ultima = j === ids.length - 1;
      dibujarGrafica(this.$(`#${id}`), trazas, layoutBase({ x: { range: [0, tf], title: { text: ultima ? 't (s)' : '' } }, y,
        leyenda: j === 0, margen: { b: ultima ? 36 : 22 } }));
    });

    // Sin panel lateral: el único dato que no se ve en las gráficas (un esquema truncado) va a la línea de contexto.
    const truncados = metodos.filter(n => comparacion[n].aviso);
    this.$('#contexto-invariantes').textContent = (this.conSigno ? 'Signed: positive grows, negative shrinks · symmetric log scale'
      : this.r.adaptativo ? 'Same problem, same tolerance · compare the error and the steps each scheme needs'
      : 'Same problem, same parameters · compare the size of the numerical error')
      + (truncados.length ? ` · Truncated: ${truncados.map(n => `${cortos[n]} (${comparacion[n].aviso})`).join(' · ')}` : '');
  }

  // ------------------------------------------------------------ trayectorias transversales
  dibujarTrayectorias() {
    const apoyo = this.datos.apoyo_comparacion, elegido = this.r.nombre_metodo, tf = this.r.t.at(-1);
    const estable = this.r.eje !== 1;
    // Eje intermedio: la gráfica grande es el crecimiento e^{λt}; la proyección (una V sobre la separatriz) pasa a la derecha.
    this.$('#graficas-trayectorias').classList.toggle('inestable', !estable);
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
      y: { type: 'log', title: { text: 'norm (rad/s)' }, dtick: 1 }, leyenda: tg.length > 1 }));

    this.$('#contexto-invariantes').textContent = (estable ? 'Stable spin: compare amplitude and phase' : 'Intermediate axis: physical growth and numerical error coexist')
      + ' · axes follow the reference (RK4, Δt/4)' + (apoyo.referencia_aviso ? ' · reference truncated' : '');
  }

  // ------------------------------------------------------------ animación
  dibujarInstante(indice, fraccion, tiempo) {
    if (!this.datos) return;
    if (this.vista === 'derivas') {
      for (const id of ['g-energia', 'g-momento']) this.capas[id].vertical('t', tiempo);
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
