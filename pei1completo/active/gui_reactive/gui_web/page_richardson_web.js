// Página 4 · RICHARDSON Y ORDEN DE CONVERGENCIA (versión web de page_richardson.py;
// enunciado 3: estimación de error por extrapolación de Richardson).
// No conocemos la solución exacta, pero sí cómo encoge el error de un esquema de orden q al partir
// el paso por dos: E_N ~ C Δt^q. Integrando con N y con 2N pasos:
//     U_N − U_2N = E_N − E_2N = E_N (1 − 2^−q)   →   E_N ≈ (U_N − U_2N) / (1 − 2^−q)
import { layoutBase, dibujarGrafica, linea, colorMetodo, css, tarjetaGrafica, nombreIngles, variableMetodo } from './graficas_web.js';

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
    <div class="pagina-graficas sin-lateral">
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
          <div class="rotulo"><b>Richardson extrapolation</b> · no exact solution needed</div>
          <div class="formula-richardson">
            <div class="fila-formula">
              <div class="ecuacion"><span>E<sub>N</sub></span><span class="op">≈</span>
                <span class="fraccion"><span>U<sub>N</sub> − U<sub>2N</sub></span><span>1 − 2<sup>−q</sup></span></span></div>
              <ul class="lectura">
                <li><b>U<sub>N</sub>, U<sub>2N</sub></b>the same scheme with N and 2N steps</li>
                <li><b>q</b>its order: the error shrinks like Δt<sup>q</sup></li>
              </ul>
            </div>
            <p class="nota"><span class="definicion-compacta">U<sub>N</sub> and U<sub>2N</sub>: the same scheme with N and 2N steps; q is its order. </span>Each time N doubles, D = |U<sub>N</sub>(t<sub>f</sub>) − U<sub>2N</sub>(t<sub>f</sub>)| is divided by
              2<sup>q</sup>: on the log–log plot every scheme falls on a straight line of slope −q.</p>
          </div>
          <div class="factores" id="factores-richardson"></div>
        </div>
      </div>
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
    this.pintarFactores();
  }

  // Una tarjeta por esquema: cuánto divide D cada vez que N se duplica (2^q) y el orden que mide el estudio.
  pintarFactores() {
    const ordenes = this.estado.configuracion.ordenes ?? {}, curvas = this.datos?.curvas_convergencia ?? {};
    const elegido = this.r?.nombre_metodo ?? this.estado.resultado?.nombre_metodo;
    this.$('#factores-richardson').innerHTML = Object.entries(ordenes).map(([n, q]) => {
      const medido = curvas[n]?.pendiente;
      return `<div class="factor${n === elegido ? ' elegido' : ''}" style="--c:var(--${variableMetodo[n]})">
        <span class="nombre">${nombreIngles[n]}</span>
        <span class="divisor">÷${2**q}</span>
        <span class="medido">q = ${q} · fit <b>${medido === null || medido === undefined ? '—' : (-medido).toFixed(2)}</b></span></div>`;
    }).join('');
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

    // Sin panel lateral: el orden medido de cada esquema ya figura en la leyenda de la gráfica de convergencia.
    this.pintarFactores();
    this.resumen = `Study over [0, ${d.tf}] s · computed in ${d.tiempo_calculo.toFixed(2)} s`;
    this.$('#contexto-precision').textContent = this.resumen;
  }

  dibujarInstante() {}
  fotograma() {}
}
