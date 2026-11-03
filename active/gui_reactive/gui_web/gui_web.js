// GUI web del eje intermedio: la parte de gui.py que se ejecuta en el navegador.
// 1. ACCIONES  · leer los controles, pedir cálculos a Python y recibir sus datos
// 2. CONTROLES · crear deslizadores, campos y selectores a partir de la configuración de gui_web.py
// 3. RELOJ     · una sola línea de tiempo recorre los estados ya calculados (no vuelve a integrar)
// 4. EVENTOS   · teclado, ratón y pestañas
import { PaginaMovimiento } from './page_attitude_web.js';
import { PaginaConservacion } from './page_invariants_web.js';
import { PaginaEstabilidad } from './page_stability_web.js';
import { PaginaPrecision } from './page_richardson_web.js';

const $ = (selector) => document.querySelector(selector);
const estado = {
  configuracion: null, resultado: null, parametrosAplicados: null, datosPagina: {},
  tiempo: 0, indice: 0, fraccion: 0, reproduciendo: true, velocidad: 1, pagina: 0,
  cambiosPendientes: false, calculando: false, arrastrando: false, cuerpo: 'caja', tfEstudio: 20,
};
const formulario = {};                // valores actuales de los controles
const entradas = {};                  // elementos de cada control, para escribir en ellos
const paginas = [];
const nombresCortos = { 'Euler': 'Euler', 'Crank-Nicolson': 'CN', 'RK4': 'RK4' };
const velocidades = [.25, .5, 1, 2, 4, 8];
const pasosLargos = 20000;            // a partir de aquí el cálculo tarda varios segundos
const atajos = [['Space', 'Play / pause'], ['← →', 'Step through time'], ['1 – 4', 'Pages'], ['↵', 'Compute'],
  ['A', 'Cycle initial spin axis'], ['↑ ↓', 'Cycle integrator'], ['M', 'Fixed / adaptive step'], ['+ −', 'Playback speed'],
  ['B', 'Cycle body shape'], ['O', 'Body / Poinsot view'], ['C', 'Compare the three integrators'], ['V', 'Reset cameras'], ['G', 'Record the 3D view (.webm)'],
  ['R', 'Reset parameters'], ['P', 'Presentation mode'], ['T', 'Projector theme'], ['F', 'Full screen'], ['?', 'This help']];

// ------------------------------------------------------------ 1. ACCIONES
async function pedir(ruta, cuerpo) {
  const respuesta = await fetch(ruta, cuerpo === undefined ? {} :
    { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) });
  return respuesta.json();
}

function leerParametros() {
  return { I: [formulario.I1, formulario.I2, formulario.I3], Omega: formulario.Omega, dt: formulario.dt, eps: formulario.eps,
    tf: formulario.tf, tol: formulario.tol, nombre_metodo: formulario.metodo, adaptativo: formulario.adaptativo, eje: formulario.eje };
}
function igualesParametros(a, b) {
  if (!a || !b) return false;
  return ['Omega', 'dt', 'eps', 'tf', 'tol', 'nombre_metodo', 'adaptativo', 'eje'].every(k => a[k] === b[k])
    && a.I.every((v, i) => v === b.I[i]);
}

function marcarCambios() {
  estado.cambiosPendientes = !igualesParametros(leerParametros(), estado.parametrosAplicados);
  $('#boton-calcular').classList.toggle('pendiente', estado.cambiosPendientes);
  $('#boton-calcular .texto').textContent = estado.cambiosPendientes ? 'Compute · pending' : 'Compute';
  const { I1, I2, I3 } = formulario, orden = $('#orden-inercias');
  const bien = I1 < I2 && I2 < I3;
  orden.classList.toggle('mal', !bien);
  // Un solo <span>: en el contenedor flex, cada subíndice suelto quedaría separado por el hueco.
  orden.innerHTML = `<span>${bien ? (I1 + I2 >= I3 ? 'I<sub>1</sub> &lt; I<sub>2</sub> &lt; I<sub>3</sub> · physical body'
    : 'I<sub>1</sub> &lt; I<sub>2</sub> &lt; I<sub>3</sub> · I<sub>1</sub> + I<sub>2</sub> &lt; I<sub>3</sub>: not a real body')
    : 'Requires I<sub>1</sub> &lt; I<sub>2</sub> &lt; I<sub>3</sub>'}</span>`;
  marcarPasos();
}

// Pasos que dará el paso fijo, antes de pulsar Compute (N = t_f/Δt, como en integrar_trayectoria).
function marcarPasos() {
  const indicador = $('#pasos-estimados');
  if (formulario.adaptativo) {
    indicador.className = 'orden';
    indicador.textContent = 'Adaptive step · N set by the tolerance';
    return;
  }
  const N = Math.max(1, Math.ceil(formulario.tf / formulario.dt)), limite = estado.configuracion.limite_pasos?.[formulario.metodo];
  const texto = `N = ${N.toLocaleString('en')} steps`;
  if (limite && N > limite) {
    indicador.className = 'orden mal';
    indicador.textContent = `${texto} · over the ${limite.toLocaleString('en')}-step limit: t_f will be cut`;
  } else if (N > pasosLargos) {
    indicador.className = 'orden lento';
    indicador.textContent = `${texto} · long computation`;
  } else {
    indicador.className = 'orden';
    indicador.textContent = texto;
  }
}

function mostrarOcupado(texto, ocupado = true, error = false) {
  const indicador = $('#estado-calculo');
  indicador.classList.toggle('ocupado', ocupado);
  indicador.classList.toggle('error', error);
  indicador.querySelector('.texto').textContent = texto;
}

// Al pulsar Compute: leer valores, avisar al principal y recibir resultados.
async function solicitarCalculo() {
  if (estado.calculando) return;
  const parametros = leerParametros();
  if (igualesParametros(parametros, estado.parametrosAplicados)) {
    estado.tiempo = 0;
    marcarCambios();
    return;
  }
  estado.calculando = true;
  $('#boton-calcular').classList.add('calculando');
  mostrarOcupado('Integrating…');
  try {
    const datos = await pedir('/api/calcular', parametros);
    if (datos.error) {
      aviso(datos.error, true);
      mostrarOcupado('Last valid result kept', false, true);
      $('#resumen').classList.add('error');
      $('#resumen').textContent = datos.error;
      return;
    }
    recibirResultado(datos, parametros);
  } catch (exc) {
    aviso('Python is not answering. Is PEI1_web.py still running?', true);
    mostrarOcupado('No connection', false, true);
  } finally {
    estado.calculando = false;
    $('#boton-calcular').classList.remove('calculando');
  }
}

function recibirResultado(datos, parametros) {
  estado.resultado = datos;
  estado.parametrosAplicados = parametros;
  estado.datosPagina = {};
  estado.tiempo = 0;
  for (const pagina of paginas) pagina.necesitaDibujo = true;
  $('#resumen').classList.remove('error');
  $('#resumen').innerHTML = `${datos.nombre_metodo} · ${datos.pasos.toLocaleString('en')} steps · ${datos.tiempo_calculo.toFixed(2)} s`
    + (datos.avisos.length ? `<br><span style="color:var(--aviso)">${datos.avisos.join(' · ')}</span>` : '');
  for (const texto of datos.avisos) aviso(texto);
  estado.resumenCalculo = `${nombresCortos[datos.nombre_metodo]} · ${datos.pasos.toLocaleString('en')} steps · ${datos.tiempo_calculo.toFixed(2)} s`;
  mostrarOcupado(estado.resumenCalculo, false);
  $('#reloj-total').textContent = `/ ${formatoTiempo(datos.t.at(-1))} s`;
  dibujarVolteosPista();
  marcarCambios();
  mostrarPagina(estado.pagina);
}

// Datos que una página necesita y que se calculan solo cuando se miran (como en la v1).
async function pedirPagina(numero) {
  const clave = numero === 3 ? `3:${estado.tfEstudio}` : String(numero);
  if (estado.datosPagina[clave]) return estado.datosPagina[clave];
  mostrarOcupado(numero === 0 ? 'Integrating the three schemes…' : 'Preparing view…');
  const datos = await pedir('/api/pagina', { numero, tf_estudio: estado.tfEstudio });
  mostrarOcupado(datos.error ? 'Error in this view' : estado.resumenCalculo ?? 'Ready', false, !!datos.error);
  if (datos.error) { aviso(datos.error, true); return null; }
  return (estado.datosPagina[clave] = datos);
}

// Al cambiar de página: dibujar lo que falte y mostrarla.
function mostrarPagina(numero) {
  estado.pagina = numero;
  document.querySelectorAll('.pestana').forEach((b, i) => b.classList.toggle('activa', i === numero));
  paginas.forEach((pagina, i) => {
    pagina.contenedor.classList.toggle('activa', i === numero);
    pagina.mostrar(i === numero);
  });
  const pagina = paginas[numero];
  if (estado.resultado && pagina.necesitaDibujo) {
    pagina.necesitaDibujo = false;
    pagina.dibujar();
  }
}

// ------------------------------------------------------------ avisos
function aviso(texto, error = false) {
  const div = document.createElement('div');
  div.className = `aviso${error ? ' error' : ''}`;
  div.textContent = texto;
  $('#avisos').appendChild(div);
  setTimeout(() => { div.classList.add('saliendo'); setTimeout(() => div.remove(), 400); }, error ? 6000 : 3800);
}

// ------------------------------------------------------------ 2. CONTROLES
function formatoNumero(v) {
  if (v === 0) return '0';
  const a = Math.abs(v);
  return a >= 1e-3 && a < 1e4 ? String(+v.toPrecision(4)) : v.toExponential(1).replace('e', 'e');
}
function formatoTiempo(t) { return t >= 100 ? t.toFixed(0) : t.toFixed(1); }
// «I₁» -> I<sub>1</sub>, «t_f» -> t<sub>f</sub>
function etiquetaHTML(texto) {
  return texto.replace(/([₁₂₃])/g, m => `<sub>${'₁₂₃'.indexOf(m) + 1}</sub>`).replace(/_(\w+)/, '<sub>$1</sub>');
}

function crearDeslizador(contenedor, nombre, { logaritmico = false } = {}) {
  const c = estado.configuracion.controles[nombre];
  const div = document.createElement('div');
  div.className = 'control';
  const minimo = logaritmico ? Math.log10(c.minimo) : c.minimo, maximo = logaritmico ? Math.log10(c.maximo) : c.maximo;
  div.innerHTML = `<label title="${c.unidad}">${etiquetaHTML(c.etiqueta)}</label>
    <input type="range" min="${minimo}" max="${maximo}" step="${logaritmico ? .01 : c.paso}">
    <input type="text" inputmode="decimal" spellcheck="false">`;
  const [deslizador, campo] = div.querySelectorAll('input');
  const escribir = (valor, desde) => {
    formulario[nombre] = valor;
    if (desde !== deslizador) deslizador.value = logaritmico ? Math.log10(valor) : valor;
    if (desde !== campo) campo.value = formatoNumero(valor);
    deslizador.style.setProperty('--pct', `${100 * (deslizador.value - minimo) / (maximo - minimo)}%`);
    div.classList.remove('invalido');
  };
  deslizador.addEventListener('input', () => {
    const v = logaritmico ? +Math.pow(10, +deslizador.value).toPrecision(3) : +deslizador.value;
    escribir(v, deslizador); marcarCambios();
  });
  campo.addEventListener('change', () => {
    const v = parseFloat(campo.value.replace(',', '.'));
    if (!isFinite(v) || v < c.minimo || v > c.maximo) {
      div.classList.add('invalido');
      aviso(`${c.etiqueta.replace('_', '')}: enter a value between ${c.minimo} and ${c.maximo}`, true);
      return;
    }
    escribir(v, campo); marcarCambios();
  });
  campo.addEventListener('keydown', e => { if (e.key === 'Enter') campo.blur(); });
  entradas[nombre] = escribir;
  contenedor.appendChild(div);
  return div;
}

function crearCampo(contenedor, nombre) {
  const c = estado.configuracion.controles[nombre];
  const div = document.createElement('div');
  div.className = 'control campo-solo';
  div.innerHTML = `<label>${c.etiqueta.length > 3 ? '' : c.etiqueta}</label><input type="text" inputmode="decimal" spellcheck="false" title="${c.etiqueta}">`;
  if (c.etiqueta.length > 3) { div.style.gridTemplateColumns = '1fr 120px'; div.querySelector('label').textContent = c.etiqueta; div.querySelector('label').style.fontFamily = 'var(--sans)'; div.querySelector('label').style.fontSize = '.8rem'; }
  const campo = div.querySelector('input');
  const escribir = (valor) => { formulario[nombre] = valor; campo.value = formatoNumero(valor); div.classList.remove('invalido'); };
  campo.addEventListener('change', () => {
    const v = parseFloat(campo.value.replace(',', '.'));
    if (!isFinite(v) || v < c.minimo || v > c.maximo) {
      div.classList.add('invalido');
      aviso(`${c.etiqueta}: enter a value between ${c.minimo} and ${c.maximo}`, true);
      return;
    }
    escribir(v); marcarCambios();
  });
  campo.addEventListener('keydown', e => { if (e.key === 'Enter') campo.blur(); });
  entradas[nombre] = escribir;
  contenedor.appendChild(div);
  return div;
}

function crearSegmentado(contenedor, nombre, opciones, { vertical = false, alCambiar } = {}) {
  const div = document.createElement('div');
  div.className = `segmentado${vertical ? ' vertical' : ''}`;
  for (const [valor, html, titulo] of opciones) {
    const b = document.createElement('button');
    b.innerHTML = html;
    if (titulo) b.title = titulo;
    b.addEventListener('click', () => { escribir(valor); alCambiar?.(valor); marcarCambios(); });
    b.dataset.valor = JSON.stringify(valor);
    div.appendChild(b);
  }
  const escribir = (valor) => {
    formulario[nombre] = valor;
    div.querySelectorAll('button').forEach(b => b.classList.toggle('activo', b.dataset.valor === JSON.stringify(valor)));
  };
  entradas[nombre] = escribir;
  contenedor.appendChild(div);
  return div;
}

function crearControles() {
  const { controles, nombres_metodos, nombres_ejes, escenarios } = estado.configuracion;
  for (const nombre of ['I1', 'I2', 'I3', 'Omega']) crearDeslizador($('#controles-solido'), nombre);
  crearCampo($('#controles-tiempo'), 'eps');
  crearDeslizador($('#controles-tiempo'), 'dt', { logaritmico: true });
  crearDeslizador($('#controles-tiempo'), 'tf');
  crearSegmentado($('#controles-integracion'), 'metodo', nombres_metodos.map(n => [n, n === 'Crank-Nicolson' ? 'Crank–Nicolson' : n]));
  const tolerancia = crearCampo($('#controles-integracion'), 'tol');
  crearSegmentado($('#controles-integracion'), 'adaptativo', [[false, 'Fixed step'], [true, 'Adaptive']],
    { alCambiar: (v) => tolerancia.classList.toggle('oculto', !v) });
  tolerancia.remove(); $('#controles-integracion').appendChild(tolerancia);
  entradas.tolerancia = tolerancia;
  crearSegmentado($('#controles-eje'), 'eje', Object.entries(nombres_ejes).map(([texto, eje]) => {
    const [nombre] = texto.split(/\s+/);
    return [eje, `${nombre}<span class="marca-eje">I<sub>${eje + 1}</sub></span>`, texto];
  }), { vertical: true });

  const lista = $('#escenarios');
  for (const escenario of escenarios) {
    const b = document.createElement('button');
    b.className = 'escenario';
    b.innerHTML = `<b>${escenario.nombre}</b><small>${escenario.descripcion}</small>`;
    b.addEventListener('click', () => aplicarEscenario(escenario, b));
    lista.appendChild(b);
  }

  // Pestañas y velocidades
  ['Attitude', 'Invariants', 'Stability', 'Richardson'].forEach((titulo, i) => {
    const b = document.createElement('button');
    b.className = 'pestana';
    b.innerHTML = `<span class="numero">${i + 1}</span>${titulo}`;
    b.addEventListener('click', () => mostrarPagina(i));
    $('#pestanas').appendChild(b);
  });
  for (const v of velocidades) {
    const b = document.createElement('button');
    b.textContent = `×${v}`;
    b.addEventListener('click', () => cambiarVelocidad(v));
    $('#velocidades').appendChild(b);
  }
  cambiarVelocidad(1);
  $('#lista-atajos').innerHTML = atajos.map(([k, d]) => `<dt><kbd>${k}</kbd></dt><dd>${d}</dd>`).join('');
}

function escribirParametros(p) {
  entradas.I1(p.I[0]); entradas.I2(p.I[1]); entradas.I3(p.I[2]);
  for (const nombre of ['Omega', 'dt', 'eps', 'tf', 'tol']) entradas[nombre](p[nombre]);
  entradas.metodo(p.nombre_metodo); entradas.adaptativo(p.adaptativo); entradas.eje(p.eje);
  entradas.tolerancia.classList.toggle('oculto', !p.adaptativo);
}
function valoresIniciales() {
  const c = estado.configuracion.controles;
  return { I: [c.I1.inicial, c.I2.inicial, c.I3.inicial], Omega: c.Omega.inicial, dt: c.dt.inicial, eps: c.eps.inicial, tf: c.tf.inicial,
    tol: c.tol.inicial, nombre_metodo: estado.configuracion.nombres_metodos.at(-1), adaptativo: false, eje: 1 };
}

function aplicarEscenario(escenario, boton) {
  const v = escenario.valores;
  escribirParametros({ I: [v.I1, v.I2, v.I3], Omega: v.Omega, dt: v.dt, eps: v.eps, tf: v.tf, tol: formulario.tol,
    nombre_metodo: v.metodo, adaptativo: v.adaptativo, eje: v.eje });
  document.querySelectorAll('.escenario').forEach(b => b.classList.toggle('activo', b === boton));
  paginas[0].cambiarCuerpo(escenario.cuerpo);
  marcarCambios();
  solicitarCalculo();
}

function restablecerParametros() {
  escribirParametros(valoresIniciales());
  document.querySelectorAll('.escenario').forEach(b => b.classList.remove('activo'));
  cambiarVelocidad(1);
  reproducir(true);
  marcarCambios();
  solicitarCalculo();
}

// ------------------------------------------------------------ 3. RELOJ
function cambiarVelocidad(v) {
  estado.velocidad = v;
  $('#velocidades').querySelectorAll('button').forEach((b, i) => b.classList.toggle('activo', velocidades[i] === v));
}
function reproducir(si = !estado.reproduciendo) {
  estado.reproduciendo = si;
  document.body.classList.toggle('pausado', !si);
}

// Cada fotograma recorre la solución ya calculada; no vuelve a integrar.
let ultimoFotograma = performance.now();
function avanzarAnimacion(ahora) {
  const transcurrido = Math.min((ahora - ultimoFotograma) / 1000, .25);
  ultimoFotograma = ahora;
  const r = estado.resultado;
  if (r) {
    const tf = r.t.at(-1);
    if (estado.reproduciendo && !estado.arrastrando)
      estado.tiempo = (estado.tiempo + transcurrido * estado.velocidad * tf / estado.configuracion.duracion_reproduccion) % tf;
    mostrarInstante(estado.tiempo);
  }
  paginas[estado.pagina]?.fotograma(ahora);
  requestAnimationFrame(avanzarAnimacion);
}

function mostrarInstante(tiempo) {
  const t = estado.resultado.t, tf = t.at(-1);
  estado.tiempo = Math.min(Math.max(tiempo, 0), tf);
  // Búsqueda binaria del intervalo [t_i, t_i+1] que contiene el instante.
  let a = 0, b = t.length - 1;
  while (b - a > 1) { const m = (a + b) >> 1; if (t[m] <= estado.tiempo) a = m; else b = m; }
  estado.indice = a;
  estado.fraccion = t[b] > t[a] ? Math.min(1, (estado.tiempo - t[a]) / (t[b] - t[a])) : 0;
  $('#reloj-t').textContent = formatoTiempo(estado.tiempo);
  const pct = `${100 * estado.tiempo / tf}%`;
  $('#pista-progreso').style.width = pct;
  $('#pista-mando').style.left = pct;
  const volteos = estado.resultado.instantes_volteo;
  let pasados = 0;
  while (pasados < volteos.length && volteos[pasados] <= estado.tiempo) pasados++;
  if (pasados !== estado.volteosPista) {
    estado.volteosPista = pasados;
    $('#pista-volteos').querySelectorAll('i').forEach((i, k) => i.classList.toggle('pasado', k < pasados));
  }
  paginas[estado.pagina]?.dibujarInstante(estado.indice, estado.fraccion, estado.tiempo);
}

function dibujarVolteosPista() {
  const r = estado.resultado, tf = r.t.at(-1);
  document.documentElement.style.setProperty('--eje-color', `var(--e${r.eje + 1})`);
  $('#pista-volteos').innerHTML = r.instantes_volteo.map(t => `<i style="left:${100 * t / tf}%" title="Flip at ${t.toFixed(2)} s"></i>`).join('');
  estado.volteosPista = -1;
}

function prepararPista() {
  const pista = $('#pista'), globo = $('#pista-globo');
  const tiempoEn = (x) => {
    const caja = pista.getBoundingClientRect();
    return Math.min(Math.max((x - caja.left) / caja.width, 0), 1) * (estado.resultado?.t.at(-1) ?? 0);
  };
  pista.addEventListener('pointerdown', e => {
    if (!estado.resultado) return;
    estado.arrastrando = true; pista.setPointerCapture(e.pointerId); mostrarInstante(tiempoEn(e.clientX));
  });
  pista.addEventListener('pointermove', e => {
    const caja = pista.getBoundingClientRect();
    globo.style.left = `${Math.min(Math.max(e.clientX - caja.left, 0), caja.width)}px`;
    globo.textContent = `${tiempoEn(e.clientX).toFixed(2)} s`;
    if (estado.arrastrando) mostrarInstante(tiempoEn(e.clientX));
  });
  const soltar = () => { estado.arrastrando = false; };
  pista.addEventListener('pointerup', soltar);
  pista.addEventListener('pointercancel', soltar);
}

// ------------------------------------------------------------ 4. EVENTOS
function pulsarTecla(e) {
  if ($('#bienvenida').classList.contains('fuera') === false) {
    if (e.key === 'Enter' || e.key === ' ') entrar();
    return;
  }
  if (e.target.matches('input')) return;
  const ayuda = $('#ayuda');
  if (e.key === '?' || (e.key === 'Escape' && ayuda.classList.contains('visible'))) { ayuda.classList.toggle('visible'); return; }
  const tecla = e.key.length === 1 ? e.key.toLowerCase() : e.key;
  const r = estado.resultado;
  const acciones = {
    ' ': () => reproducir(), 'Enter': () => solicitarCalculo(),
    'ArrowLeft': () => r && mostrarInstante(estado.tiempo - .04 * r.t.at(-1)),
    'ArrowRight': () => r && mostrarInstante(estado.tiempo + .04 * r.t.at(-1)),
    '1': () => mostrarPagina(0), '2': () => mostrarPagina(1), '3': () => mostrarPagina(2), '4': () => mostrarPagina(3),
    'a': () => { entradas.eje((formulario.eje + 1) % 3); marcarCambios(); },
    'ArrowUp': () => cambiarMetodo(-1), 'ArrowDown': () => cambiarMetodo(1),
    'm': () => { entradas.adaptativo(!formulario.adaptativo); entradas.tolerancia.classList.toggle('oculto', !formulario.adaptativo); marcarCambios(); },
    '+': () => cambiarVelocidad(velocidades[Math.min(velocidades.indexOf(estado.velocidad) + 1, velocidades.length - 1)]),
    '=': () => cambiarVelocidad(velocidades[Math.min(velocidades.indexOf(estado.velocidad) + 1, velocidades.length - 1)]),
    '-': () => cambiarVelocidad(velocidades[Math.max(velocidades.indexOf(estado.velocidad) - 1, 0)]),
    'r': () => restablecerParametros(), 'f': () => pantallaCompleta(), 'p': () => modoPresentacion(), 't': () => cambiarTema(),
  };
  if (acciones[tecla]) { e.preventDefault(); acciones[tecla](); return; }
  if (paginas[estado.pagina]?.pulsarTecla?.(tecla)) e.preventDefault();
}
function cambiarMetodo(paso) {
  const lista = estado.configuracion.nombres_metodos;
  entradas.metodo(lista[(lista.indexOf(formulario.metodo) + paso + lista.length) % lista.length]);
  marcarCambios();
}
function pantallaCompleta() {
  if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen();
}
function modoPresentacion() {
  const activo = !document.body.classList.contains('presentacion');
  document.body.classList.toggle('presentacion', activo);
  $('#app').classList.toggle('sin-cajon', activo);
}
function cambiarTema() {
  const raiz = document.documentElement;
  raiz.dataset.tema = raiz.dataset.tema === 'claro' ? 'oscuro' : 'claro';
  for (const pagina of paginas) pagina.cambiarTema?.();
  window.Plotly && document.querySelectorAll('.plot').forEach(div => div.capa?.recolocar());
}

function entrar() {
  const bienvenida = $('#bienvenida');
  if (bienvenida.classList.contains('fuera')) return;
  bienvenida.classList.add('fuera');
  paginas[0].alEntrar?.();
}

// ------------------------------------------------------------ arranque
async function iniciar() {
  const inicio = await pedir('/api/inicio');
  estado.configuracion = inicio.configuracion;
  estado.tfEstudio = inicio.configuracion.controles.tf_estudio.inicial;
  crearControles();
  escribirParametros(inicio.parametros ?? valoresIniciales());
  marcarCambios();

  // Las cuatro páginas, como en gui.py: cada una dibuja los datos que le entrega el principal.
  const contexto = { estado, formulario, pedirPagina, aviso, mostrarInstante, nombresCortos, formatoNumero };
  [PaginaMovimiento, PaginaConservacion, PaginaEstabilidad, PaginaPrecision].forEach((Pagina, i) =>
    paginas.push(new Pagina($(`#pagina-${i}`), contexto)));
  if (window.__depurar) window.__orbita = { estado, paginas };      // solo para las pruebas automáticas

  $('#boton-calcular').addEventListener('click', solicitarCalculo);
  $('#boton-restablecer').addEventListener('click', restablecerParametros);
  $('#boton-reproducir').addEventListener('click', () => reproducir());
  $('#boton-cajon').addEventListener('click', () => $('#app').classList.toggle('sin-cajon'));
  $('#boton-tema').addEventListener('click', cambiarTema);
  $('#boton-ayuda').addEventListener('click', () => $('#ayuda').classList.toggle('visible'));
  $('#ayuda').addEventListener('click', e => { if (e.target.id === 'ayuda') $('#ayuda').classList.remove('visible'); });
  $('#boton-pantalla').addEventListener('click', pantallaCompleta);
  $('#boton-entrar').addEventListener('click', entrar);
  document.addEventListener('keydown', pulsarTecla);
  prepararPista();
  // Cerrar la ventana termina el programa de Python (recargar la página no).
  window.addEventListener('pagehide', () => navigator.sendBeacon('/api/cerrar', '{}'));

  if (inicio.resultado) recibirResultado(inicio.resultado, inicio.parametros);
  else mostrarPagina(0);
  const r = estado.resultado;
  $('#bienvenida-carga').textContent = r ? `Ready · ${r.nombre_metodo} · ${r.pasos.toLocaleString('en')} steps in ${r.tiempo_calculo.toFixed(2)} s` : '';
  if (new URLSearchParams(location.search).has('directo')) entrar();
  requestAnimationFrame(avanzarAnimacion);
}

iniciar().catch(exc => { console.error(exc); aviso(`Could not start: ${exc.message}`, true); });
