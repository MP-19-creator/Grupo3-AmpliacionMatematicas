// Gráficas 2D comunes de las páginas 2 a 4 (equivale a preparar_grafica y poner_leyenda de style.py).
// Plotly dibuja las curvas una vez por cálculo; el instante actual se marca con una capa HTML
// encima de cada gráfica, que se mueve a 60 fps sin volver a dibujar Plotly.
const Plotly = window.Plotly;

export const variableMetodo = { 'Euler': 'euler', 'Crank-Nicolson': 'cn', 'RK4': 'rk4', 'Referencia RK4': 'referencia', 'Euler implícito': 'implicito', 'Exacta': 'referencia' };
export const nombreIngles = { 'Euler': 'Euler', 'Crank-Nicolson': 'Crank–Nicolson', 'RK4': 'RK4', 'Referencia RK4': 'Reference RK4',
  'Euler implícito': 'Implicit Euler', 'Exacta': 'Exact' };

export function css(nombre) { return getComputedStyle(document.documentElement).getPropertyValue(`--${nombre}`).trim(); }
export function colorMetodo(nombre) { return css(variableMetodo[nombre] ?? 'texto'); }

// Ejes con el estilo de la GUI. Las opciones de cada eje se mezclan con las comunes.
export function layoutBase({ x = {}, y = {}, leyenda = false, margen = {}, ...resto } = {}) {
  const eje = ({ title, ...propio }) => ({
    gridcolor: css('linea'), zerolinecolor: css('linea-2'), linecolor: css('linea-2'), showline: false,
    tickfont: { family: css('mono'), size: 10, color: css('tenue') }, ticks: '', exponentformat: 'power', automargin: true,
    ...propio,
    title: { font: { size: 11, color: css('tenue') }, standoff: 8, ...(title ?? {}) },
  });
  return {
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 56, r: 12, t: 6, b: 36, ...margen },
    font: { family: css('sans'), size: 11, color: css('texto-2') },
    xaxis: eje(x), yaxis: eje(y),
    showlegend: leyenda,
    legend: { orientation: 'h', x: 1, xanchor: 'right', y: 1, yanchor: 'bottom', font: { size: 10, color: css('texto-2') }, bgcolor: 'rgba(0,0,0,0)' },
    hovermode: 'x unified',
    hoverlabel: { bgcolor: css('panel-solido'), bordercolor: css('linea-2'), font: { family: css('mono'), size: 11, color: css('texto') } },
    transition: { duration: 0 },
    ...resto,
  };
}

const configuracion = { displayModeBar: false, responsive: false, doubleClick: 'reset' };

export function dibujarGrafica(div, trazas, layout) {
  Plotly.react(div, trazas, layout, configuracion);
  if (!div.dataset.observado) {
    div.dataset.observado = '1';
    new ResizeObserver(() => { if (div.clientWidth > 10 && div._fullLayout) Plotly.Plots.resize(div); div.capa?.recolocar(); }).observe(div);
    div.on?.('plotly_relayout', () => div.capa?.recolocar());
  }
}

// Línea de una serie con el grosor de la v1: el método elegido más grueso y opaco.
export function linea(nombre, x, y, { seleccionado = false, discontinua = false, ...resto } = {}) {
  return {
    type: 'scatter', mode: 'lines', x, y, name: nombreIngles[nombre] ?? nombre,
    line: { color: colorMetodo(nombre), width: seleccionado ? 2.6 : 1.4, dash: discontinua ? 'dash' : 'solid' },
    opacity: seleccionado ? 1 : .8, hovertemplate: '%{y:.3e}', ...resto,
  };
}

// ------------------------------------------------------------ capa de cursores sobre una gráfica
export class Capa {
  constructor(div) {
    this.div = div;
    div.capa = this;
    this.raiz = document.createElement('div');
    this.raiz.className = 'capa-grafica';
    div.appendChild(this.raiz);
    this.elementos = {};
  }
  ejes(nombreX = 'xaxis', nombreY = 'yaxis') {
    const fl = this.div._fullLayout;
    return fl ? [fl[nombreX], fl[nombreY]] : [null, null];
  }
  // Línea vertical en x (en unidades de datos).
  vertical(clave, x, { color = css('texto'), discontinua = false } = {}) {
    const [xa, ya] = this.ejes();
    const e = this.elemento(clave, 'capa-vertical');
    if (!xa || x === null || x === undefined) { e.style.display = 'none'; return; }
    const px = xa._offset + xa.c2p(x);
    const visible = px >= xa._offset - 1 && px <= xa._offset + xa._length + 1;
    e.style.display = visible ? '' : 'none';
    e.style.transform = `translateX(${px}px)`;
    e.style.top = `${ya._offset}px`; e.style.height = `${ya._length}px`;
    e.style.borderColor = color;
    e.style.borderLeftStyle = discontinua ? 'dashed' : 'solid';
  }
  // Punto en (x, y) en unidades de datos.
  punto(clave, x, y, { color = css('punto'), tam = 9, forma = 'circulo' } = {}) {
    const [xa, ya] = this.ejes();
    const e = this.elemento(clave, `capa-punto ${forma}`);
    if (!xa || !Number.isFinite(x) || !Number.isFinite(y)) { e.style.display = 'none'; return; }
    const px = xa._offset + xa.c2p(x), py = ya._offset + ya.c2p(y);
    const dentro = px >= xa._offset - 2 && px <= xa._offset + xa._length + 2 && py >= ya._offset - 2 && py <= ya._offset + ya._length + 2;
    e.style.display = dentro ? '' : 'none';
    e.style.transform = `translate(${px - tam/2}px, ${py - tam/2}px)`;
    e.style.width = e.style.height = `${tam}px`;
    e.style.setProperty('--color', color);
  }
  ocultar(clave) { if (this.elementos[clave]) this.elementos[clave].style.display = 'none'; }
  elemento(clave, clase) {
    if (!this.elementos[clave]) {
      const e = document.createElement('div');
      e.className = clase;
      this.raiz.appendChild(e);
      this.elementos[clave] = e;
    }
    return this.elementos[clave];
  }
  recolocar() { this.alRecolocar?.(); }
}

// ------------------------------------------------------------ escala simétrica logarítmica (la v1 usa symlog)
// Plotly no la tiene: se transforma y -> sign(y)·log10(1 + |y|/ε) y se rotulan los valores originales.
export const umbralSimlog = 1e-12;
export function simlog(y) { return y === null ? null : Math.sign(y) * Math.log10(1 + Math.abs(y) / umbralSimlog); }
export function marcasSimlog(maximo) {
  const valores = [0];
  // ±10⁻¹² quedaría pegado al 0 en esta escala: las marcas empiezan en ±10⁻⁹.
  for (let e = -9; e <= 0; e += 3) if (10**e <= maximo * 1.0001) valores.push(10**e, -(10**e));
  valores.sort((a, b) => a - b);
  return { tickvals: valores.map(simlog), ticktext: valores.map(v => v === 0 ? '0' : `${v < 0 ? '−' : ''}10<sup>${Math.log10(Math.abs(v))}</sup>`) };
}

// ------------------------------------------------------------ utilidades de texto
export function exp(v, cifras = 1) {
  if (v === null || v === undefined || !isFinite(v)) return '—';
  if (v === 0) return '0';
  const [m, e] = v.toExponential(cifras).split('e');
  return `${m}·10<sup>${+e}</sup>`;
}
export function tarjetaGrafica(titulo, id, extra = '') {
  return `<div class="tarjeta grafica" id="tarjeta-${id}">
    <div class="cabecera-grafica"><div class="rotulo">${titulo}</div>${extra}</div>
    <div class="plot" id="${id}"></div></div>`;
}
