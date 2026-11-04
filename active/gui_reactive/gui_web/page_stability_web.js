// Página 3 · REGIONES DE ESTABILIDAD ABSOLUTA explicadas con los AUTOVALORES del problema
// (versión web de page_stability.py; enunciado 3, |R(z)| ≤ 1).
// Cerca de un estado, el error se comporta como dE/dt = J E y cada modo propio de J es una ecuación
// test dU/dt = λU. Un esquema multiplica ese modo por R(z), z = λΔt, en CADA paso: basta con mirar
// dónde caen los puntos z = λΔt respecto de la región |R(z)| ≤ 1.
//   ×  dinámica en el equilibrio  ·  ◆ cinemática del cuaternión  ·  ● J(ω(t)) en el instante actual
import { layoutBase, dibujarGrafica, linea, Capa, colorMetodo, css, tarjetaGrafica, nombreIngles, exp } from './graficas_web.js';

const metodos = ['Euler', 'Euler implícito', 'Crank-Nicolson', 'RK4'];
// Planos complejos con la misma escala en Re z e Im z: la región de Euler es un círculo, no una elipse.
// Se encoge el recuadro de la gráfica (domain) en vez de alargar un rango, para no salirse de la malla calculada.
const escalaIgual = { scaleanchor: 'x', scaleratio: 1, constrain: 'domain' };

function conAlfa(hex, a) {
  const c = hex.replace('#', ''), n = parseInt(c.length === 3 ? c.replace(/./g, '$&$&') : c, 16);
  return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`;
}

export class PaginaEstabilidad {
  titulo = '3  Stability regions';

  constructor(contenedor, contexto) {
    this.contenedor = contenedor;
    this.ctx = contexto;
    this.estado = contexto.estado;
    this.vista = 'regiones';
    this.necesitaDibujo = true;
    this.construirDOM();
  }
  $(s) { return this.contenedor.querySelector(s); }

  construirDOM() {
    this.contenedor.innerHTML = `
    <div class="pagina-graficas">
      <div class="barra-pagina">
        <div class="segmentado mini" id="vista-estabilidad"><button data-vista="regiones">Regions</button><button data-vista="modo">Amplitude & phase</button></div>
        <span class="contexto" id="contexto-estabilidad"></span>
      </div>
      <div class="cuerpo-graficas regiones" id="graficas-regiones">
        ${tarjetaGrafica('<b>Regions</b> · |R(z)| ≤ 1', 'g-regiones')}
        ${tarjetaGrafica('<b>Close-up</b> · log|R(z)| − Re z', 'g-detalle', '<span class="leyenda-mapa"><i class="rojo"></i>amplifies <i class="azul"></i>damps</span>')}
      </div>
      <div class="cuerpo-graficas trayectorias oculto" id="graficas-modo">
        ${tarjetaGrafica('<b>Oscillatory test mode</b> · u<sub>n</sub> in the complex plane', 'g-espiral')}
        ${tarjetaGrafica('<b>Amplitude per step</b> · |R(iy)|', 'g-ganancia')}
        ${tarjetaGrafica('<b>Phase error per step</b> · arg R(iy) − y', 'g-desfase')}
      </div>
      <aside class="tarjeta lateral" id="lateral-estabilidad"></aside>
      <div class="cargando" id="cargando-estabilidad"><span>Computing regions and eigenvalues…</span></div>
    </div>`;
    this.$('#vista-estabilidad').addEventListener('click', e => {
      if (!e.target.dataset.vista) return;
      this.vista = e.target.dataset.vista;
      if (this.datos) this.dibujarVista(); else this.actualizarBotones();
    });
    this.capas = {};
    for (const id of ['g-regiones', 'g-detalle', 'g-espiral', 'g-ganancia', 'g-desfase'])
      this.capas[id] = new Capa(this.$(`#${id}`));
    this.actualizarBotones();
  }

  actualizarBotones() {
    this.$('#vista-estabilidad').querySelectorAll('button').forEach(b => b.classList.toggle('activo', b.dataset.vista === this.vista));
    this.$('#graficas-regiones').classList.toggle('oculto', this.vista !== 'regiones');
    this.$('#graficas-modo').classList.toggle('oculto', this.vista !== 'modo');
  }
  mostrar() {}
  cambiarTema() { if (this.datos) this.dibujarVista(); }

  async dibujar() {
    const resultado = this.estado.resultado;
    this.$('#cargando-estabilidad').classList.add('visible');
    const datos = await this.ctx.pedirPagina(2);
    this.$('#cargando-estabilidad').classList.remove('visible');
    if (!datos || this.estado.resultado !== resultado) return;
    this.datos = datos.estabilidad;
    this.r = resultado;
    this.dibujarVista();
  }

  dibujarVista() {
    this.actualizarBotones();
    if (this.vista === 'regiones') this.dibujarRegiones(); else this.dibujarModo();
    this.dtVista = null;
    this.dibujarInstante(this.estado.indice, this.estado.fraccion, this.estado.tiempo);
  }

  // ------------------------------------------------------------ regiones y autovalores
  trazasRegiones(regiones, rellenar) {
    const elegido = this.r.nombre_metodo, trazas = [];
    // Relleno de la región del método elegido: solo las celdas con |R| ≤ 1 (las demás, vacías).
    if (rellenar) {
      const r = regiones[elegido];
      trazas.push({ type: 'heatmap', x: r.x, y: r.y, z: r.z.map(fila => fila.map(v => v !== null && v <= 1 ? 1 : null)),
        colorscale: [[0, conAlfa(colorMetodo(elegido), .16)], [1, conAlfa(colorMetodo(elegido), .16)]], showscale: false,
        hoverinfo: 'skip', zsmooth: false, showlegend: false });
    }
    // Contorno |R| = 1 de los cuatro métodos.
    for (const n of metodos) {
      const r = regiones[n], c = colorMetodo(n), sel = n === elegido;
      trazas.push({ type: 'contour', x: r.x, y: r.y, z: r.z, showscale: false, hoverinfo: 'skip', name: nombreIngles[n], showlegend: true,
        contours: { start: 1, end: 1, size: 1, coloring: 'lines' }, colorscale: [[0, c], [1, c]],
        line: { width: sel ? 2.6 : 1.3, smoothing: 1 } });
    }
    return trazas;
  }
  trazasAutovalores() {
    const [zw, zq] = this.datos.autovalores_iniciales;
    return [
      { type: 'scatter', mode: 'markers', x: zw.re, y: zw.im, name: 'Equilibrium (ω)', hovertemplate: 'z = %{x:.3g} %{y:+.3g}i',
        marker: { symbol: 'x', size: 13, color: css(`e${this.r.eje + 1}`), line: { color: '#fff', width: 1 } } },
      { type: 'scatter', mode: 'markers', x: zq.re, y: zq.im, name: 'Quaternion', hovertemplate: 'z = %{x:.3g} %{y:+.3g}i',
        marker: { symbol: 'diamond', size: 10, color: css('momento'), line: { color: '#fff', width: 1 } } },
    ];
  }
  dibujarRegiones() {
    const d = this.datos, r = d.radio;
    const ejes = { zeroline: true, zerolinecolor: css('tenue'), zerolinewidth: 1 };
    dibujarGrafica(this.$('#g-regiones'), [...this.trazasRegiones(d.regiones_completas, true), ...this.trazasAutovalores()],
      layoutBase({ x: { range: [-3.4, 2.4], title: { text: 'Re z' }, ...ejes, constrain: 'domain' }, y: { range: [-3.2, 3.2], title: { text: 'Im z' }, ...ejes, ...escalaIgual },
        // Leyenda en la franja libre de encima: con la escala igual, el recuadro de la gráfica no llena la tarjeta.
        leyenda: true, hovermode: 'closest', legend: { orientation: 'h', x: .5, y: 1, xanchor: 'center', yanchor: 'top',
          font: { size: 10, color: css('texto-2') } } }));
    const G = d.color_ampliacion;
    let m = 1e-12;
    for (const fila of G.z) for (const v of fila) if (v !== null) m = Math.max(m, Math.abs(v));
    const mapa = { type: 'heatmap', x: G.x, y: G.y, z: G.z, zmin: -m, zmax: m, zmid: 0, showscale: false, hoverinfo: 'skip', opacity: .9,
      colorscale: [[0, '#2b6cff'], [.5, 'rgba(0,0,0,0)'], [1, '#ff3d5e']] };
    dibujarGrafica(this.$('#g-detalle'), [mapa, ...this.trazasRegiones(d.regiones_ampliadas, false), ...this.trazasAutovalores()],
      layoutBase({ x: { range: [-r, r], title: { text: 'Re z' }, ...ejes, constrain: 'domain' }, y: { range: [-r, r], title: { text: 'Im z' }, ...ejes, ...escalaIgual }, hovermode: 'closest' }));

    const [zw] = d.autovalores_iniciales;
    const real = Math.abs(zw.im[0]) < 1e-14;
    this.$('#lateral-estabilidad').innerHTML = `
      <div class="rotulo">Prediction vs simulation</div>
      ${this.tablaPrediccion(d.prediccion)}
      <p class="nota"><b style="color:var(--e${this.r.eje + 1})">×</b> equilibrium eigenvalues λΔt (${real ? 'real: saddle' : 'imaginary: centre'})<br>
        <b style="color:var(--momento)">◆</b> quaternion kinematics ±i|ω|Δt/2 (explains the drift of |q|)<br>
        <b style="color:var(--punto)">●</b> eigenvalues of J(ω(t))·Δt now: they move with the animation</p>
      <p class="nota" id="nota-previa"></p>`;
    this.$('#contexto-estabilidad').textContent = 'Each step multiplies every mode by R(λΔt): |R| > 1 grows, |R| = 1 is kept, |R| < 1 is damped';
  }

  // Tabla de predicción: |R(z)| frente a |e^z| en el equilibrio y |q(t_f)| − 1 predicho frente al simulado.
  tablaPrediccion({ z, filas }) {
    const elegido = this.r.nombre_metodo, cifras = (v) => v === null ? '—' : v.toFixed(6);
    const textoZ = Math.abs(z.im) < 1e-14 ? z.re.toPrecision(3) : `${z.re.toPrecision(3)} ${z.im < 0 ? '−' : '+'} ${Math.abs(z.im).toPrecision(3)}i`;
    const fila = (f, a, b) => `<tr class="${f.nombre === elegido ? 'elegido' : ''}">
      <td><span class="metodo" style="--c:${colorMetodo(f.nombre)}"><i></i>${nombreIngles[f.nombre]}</span></td><td>${a}</td><td>${b}</td></tr>`;
    return `
      <table class="tabla">
        <caption>Equilibrium · z = λΔt = ${textoZ}</caption>
        <thead><tr><th></th><th>|R(z)|</th><th>|e<sup>z</sup>|</th></tr></thead>
        <tbody>${filas.map(f => fila(f, cifras(f.R), cifras(f.exacta))).join('')}</tbody>
      </table>
      <table class="tabla">
        <caption>Quaternion · |q(t<sub>f</sub>)| − 1</caption>
        <thead><tr><th></th><th>Prediction</th><th>Simulation</th></tr></thead>
        <tbody>${filas.map(f => fila(f, exp(f.prediccion, 2), exp(f.simulacion, 2))).join('')}</tbody>
      </table>`;
  }

  // ------------------------------------------------------------ modo oscilatorio test u' = iσu
  dibujarModo() {
    const d = this.datos.demostracion;
    const curvas = { ...d.curvas, 'Exacta': { orbita: d.exacta } };
    const trazas = Object.entries(curvas).map(([n, c]) => linea(n, c.orbita.re, c.orbita.im,
      { seleccionado: n === this.r.nombre_metodo, discontinua: n === 'Exacta', mode: 'lines+markers', marker: { size: 4 }, hovertemplate: '(%{x:.2f}, %{y:.2f})' }));
    dibujarGrafica(this.$('#g-espiral'), trazas, layoutBase({ x: { range: [-3.3, 3.3], title: { text: 'Re u' } },
      y: { range: [-3.3, 3.3], title: { text: 'Im u' }, scaleanchor: 'x' }, leyenda: true, hovermode: 'closest' }));
    const y = d.barrido;
    const lineaH = (v) => ({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: v, y1: v, line: { color: css('tenue'), width: 1, dash: 'dot' } });
    dibujarGrafica(this.$('#g-ganancia'), [...Object.entries(d.curvas).map(([n, c]) => linea(n, y, c.ganancia, { seleccionado: n === this.r.nombre_metodo })),
      linea('Exacta', y, y.map(() => 1), { discontinua: true })],
      layoutBase({ x: { range: [0, y.at(-1)], title: { text: 'y = σΔt' } }, y: { range: [0, 3.2] }, shapes: [lineaH(1)] }));
    dibujarGrafica(this.$('#g-desfase'), [...Object.entries(d.curvas).map(([n, c]) => linea(n, y, c.fase, { seleccionado: n === this.r.nombre_metodo })),
      linea('Exacta', y, y.map(() => 0), { discontinua: true })],
      layoutBase({ x: { range: [0, y.at(-1)], title: { text: 'y = σΔt' } }, y: { range: [-1.7, 1.7], title: { text: 'rad' } }, shapes: [lineaH(0)] }));
    this.$('#lateral-estabilidad').innerHTML = `
      <div class="rotulo">Test mode</div>
      <div class="dato-grande"><span class="rotulo">u′ = iσu</span><b class="mono">σΔt = ${d.y}</b></div>
      <p class="nota">A pure oscillation: the exact solution turns on the unit circle forever.</p>
      <p class="nota"><b style="color:var(--euler)">Explicit Euler</b> amplifies: |R| &gt; 1, the spiral opens.<br>
        <b style="color:var(--implicito)">Implicit Euler</b> damps: the spiral closes.<br>
        <b style="color:var(--cn)">Crank–Nicolson</b> keeps |u| exactly but lags in phase.<br>
        <b style="color:var(--rk4)">RK4</b> damps slightly for small σΔt and keeps the phase best.</p>
      <p class="nota">Linear comparison, not the satellite trajectory.</p>`;
    this.$('#contexto-estabilidad').textContent = `Test mode u′ = iσu · σΔt = ${d.y} · markers advance one step every ${(this.r.t.at(-1)/(d.n.length - 1)).toFixed(1)} s of animation`;
  }

  // ------------------------------------------------------------ animación
  dibujarInstante(indice, fraccion, tiempo) {
    if (!this.datos) return;
    if (this.vista === 'modo') {
      const d = this.datos.demostracion;
      const paso = tiempo / this.r.t.at(-1) * (d.n.length - 1), n = Math.min(d.n.length - 2, Math.floor(paso)), f = paso - n;
      const curvas = { ...d.curvas, 'Exacta': { orbita: d.exacta } };
      for (const [nombre, c] of Object.entries(curvas)) {
        // Interpolación exclusivamente visual entre los pasos calculados.
        const x = c.orbita.re[n] + f*(c.orbita.re[n+1] - c.orbita.re[n]), y = c.orbita.im[n] + f*(c.orbita.im[n+1] - c.orbita.im[n]);
        this.capas['g-espiral'].punto(nombre, x, y, { color: colorMetodo(nombre), tam: 9 });
      }
      return;
    }
    const z = this.datos.autovalores_por_instante;
    for (let k = 0; k < z.re[indice].length; k++)
      for (const id of ['g-regiones', 'g-detalle']) this.capas[id].punto(`z${k}`, z.re[indice][k], z.im[indice][k], { color: css('punto'), tam: 9 });
    this.vistaPrevia();
  }

  // Vista previa: dónde caería λΔt con el Δt que hay ahora en los controles (antes de pulsar Compute).
  vistaPrevia() {
    const f = this.ctx.formulario, aplicado = this.r.dt_utilizado;
    const activa = !f.adaptativo && !this.r.adaptativo && f.dt !== aplicado;
    const [zw, zq] = this.datos.autovalores_iniciales, k = f.dt / aplicado;
    for (const id of ['g-regiones', 'g-detalle']) {
      [...zw.re.map((x, i) => [x, zw.im[i]]), ...zq.re.map((x, i) => [x, zq.im[i]])].forEach(([x, y], i) => {
        if (activa) this.capas[id].punto(`previa${i}`, x*k, y*k, { color: i < zw.re.length ? css(`e${this.r.eje + 1}`) : css('momento'), tam: 12, forma: 'hueco' });
        else this.capas[id].ocultar(`previa${i}`);
      });
    }
    if (this.dtVista === (activa ? f.dt : 0)) return;
    this.dtVista = activa ? f.dt : 0;
    const nota = this.$('#nota-previa');
    if (nota) nota.innerHTML = activa ? `<b style="color:var(--acento)">○</b> preview with Δt = ${this.ctx.formatoNumero(f.dt)} s (×${k.toPrecision(3)}): press Compute to apply` : '';
  }
  fotograma() {}
}
