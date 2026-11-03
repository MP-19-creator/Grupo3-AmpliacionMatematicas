// Página 1 · ACTITUD Y ESPACIO DE FASES (versión web de page_attitude.py, enunciado 3.3)
//   - izquierda: el cuerpo girando en ejes inerciales, o la construcción de Poinsot completa
//   - centro:    espacio de fases (ω1, ω2, ω3) con los elipsoides de 2T y L², la separatriz y la polhoda
//   - derecha:   teoría frente a simulación (autovalor, periodo, intervalo entre volteos, derivas)
//   - abajo:     ω(t) en ejes cuerpo, que se dibuja hasta el instante actual
// Todo se dibuja con datos de Python; el navegador solo interpola entre muestras para que se vea fluido.
import {
  THREE, crearVisor, volarCamara, crearCielo, crearLuces, crearTubo, liberar, crearFlecha, crearEtiqueta,
  geometriaElipsoide, rejillaElipsoide, materialFresnel, crearHalo, cuaternionesDesdeMatrices, interpolarCuaternion,
  interpolarPunto, color, temaOscuro, intensidadBrillo,
} from './escena_web.js';
import { crearCuerpo, crearFantasma, tiposCuerpo } from './cuerpos_web.js';

const nombresEje = ['I₁', 'I₂', 'I₃'];
const variableMetodo = { 'Euler': 'euler', 'Crank-Nicolson': 'cn', 'RK4': 'rk4' };
const largoEjes = .86;
// Cámara del espacio de fases proporcional al tamaño del elipsoide (radio R que envía Python).
const vistaFases = (R) => [2.1*R, -3.6*R, 2.4*R];

export class PaginaMovimiento {
  titulo = '1  Attitude & phase space';

  constructor(contenedor, contexto) {
    this.contenedor = contenedor;
    this.ctx = contexto;
    this.estado = contexto.estado;
    this.vista = 'cuerpo';
    this.tipoCuerpo = 'caja';
    this.opciones = { estelas: true, vectores: true, integradores: false, familia: false, elipsoides: true };
    this.necesitaDibujo = true;
    this.visible = false;
    this.volteosMostrados = 0;
    this.ultimaInteraccion = performance.now();
    this.construirDOM();
    this.construirEscenas();
    this.grafica = new GraficaOmega(this.$('#grafica-omega'), this);
  }

  $(selector) { return this.contenedor.querySelector(selector); }

  // ------------------------------------------------------------ estructura de la página
  construirDOM() {
    const botonesCuerpo = Object.entries(tiposCuerpo).map(([k, v]) => `<button data-cuerpo="${k}">${v.nombre}</button>`).join('');
    this.contenedor.innerHTML = `
    <div class="movimiento">
      <div class="tarjeta visor" id="visor-actitud">
        <div class="visor-superior">
          <div class="visor-titulo"><div class="rotulo"><b>Attitude</b> · inertial frame</div>
            <div class="sub" id="sub-actitud">Body axes, the spin vector ω and the fixed angular momentum L</div></div>
          <div class="herramientas">
            <div class="segmentado mini" id="selector-vista"><button data-vista="cuerpo">Body</button><button data-vista="poinsot">Poinsot</button></div>
            <div class="segmentado mini" id="selector-cuerpo">${botonesCuerpo}</div>
            <div class="fila-chips">
              <button class="chip" data-opcion="estelas">Trails</button>
              <button class="chip" data-opcion="vectores">L & ω</button>
              <button class="chip" data-opcion="integradores">3 integrators<span class="tecla">C</span></button>
              <button class="chip grabar" id="boton-grabar" title="Record this view as a video (G)"><i></i><span class="texto">Record</span><span class="tecla">G</span></button>
            </div>
          </div>
        </div>
        <div class="visor-inferior">
          <div class="volteos">
            <div class="volteos-numero" id="volteos">0</div>
            <div class="volteos-texto"><div class="rotulo">Flips of the spin axis</div><div class="detalle" id="volteos-detalle"></div></div>
          </div>
          <div class="nota-cuerpo" id="nota-cuerpo"></div>
        </div>
        <div class="destello" id="destello-actitud"></div>
        <div class="cargando" id="cargando-actitud"><span>Integrating Euler, Crank–Nicolson and RK4…</span></div>
      </div>

      <div class="tarjeta visor" id="visor-fases">
        <div class="visor-superior">
          <div class="visor-titulo"><div class="rotulo"><b>Phase space</b> · body frame</div>
            <div class="sub">The polhode is where the 2T and L² ellipsoids meet</div></div>
          <div class="herramientas">
            <div class="fila-chips">
              <button class="chip" data-opcion="elipsoides">Ellipsoids</button>
              <button class="chip" data-opcion="familia">All polhodes</button>
            </div>
          </div>
        </div>
        <div class="visor-inferior">
          <div class="leyenda" id="leyenda-fases">
            <span style="color:var(--energia)"><i></i>Energy 2T</span>
            <span style="color:var(--momento)"><i></i>Momentum L²</span>
            <span style="color:var(--separatriz)"><i class="discontinua"></i>Separatrix</span>
            <span style="color:var(--polhoda)"><i></i>Polhode</span>
          </div>
          <div class="leyenda oculto" id="leyenda-integradores">
            <span style="color:var(--euler)"><i></i>Euler</span><span style="color:var(--cn)"><i></i>CN</span><span style="color:var(--rk4)"><i></i>RK4</span>
          </div>
        </div>
        <div class="destello" id="destello-fases"></div>
      </div>

      <aside class="tarjeta teoria">
        <div class="insignia" id="insignia"><span class="estado" id="estado-estabilidad">—</span><span class="tipo" id="tipo-estabilidad"></span></div>
        <div>
          <div class="rotulo">Linearised eigenvalues</div>
          <div class="autovalor" id="autovalor">—</div>
        </div>
        <div class="comparacion">
          <div class="rotulo">Flip interval · theory vs simulation</div>
          <div class="fila"><span>Theory · P/2</span><span id="flip-teoria">—</span></div>
          <div class="fila"><span>Simulation · mean</span><span id="flip-medido">—</span></div>
          <div class="acuerdo" id="flip-acuerdo"></div>
        </div>
        <dl class="datos">
          <dt>Polhode period P</dt><dd id="d-periodo">—</dd>
          <dt>Polhode</dt><dd id="d-lado">—</dd>
          <dt>C = L² − 2T·I<sub>2</sub></dt><dd id="d-casimir">—</dd>
          <dt>Step</dt><dd id="d-paso">—</dd>
        </dl>
        <div>
          <div class="rotulo" style="margin-bottom:9px">Max drift of the invariants</div>
          <div class="barras" id="barras-derivas"></div>
          <div class="escala-derivas"><span>10<sup>−16</sup></span><span>10<sup>−8</sup></span><span>1</span></div>
        </div>
      </aside>

      <div class="tarjeta grafica-omega">
        <div class="cabecera">
          <div class="rotulo"><b>Angular velocity</b> · body frame (rad/s)</div>
          <div class="leyenda-omega" id="leyenda-omega">
            <span style="color:var(--e1)"><i></i>ω<sub>1</sub> <b class="mono" data-k="0"></b></span>
            <span style="color:var(--e2)"><i></i>ω<sub>2</sub> <b class="mono" data-k="1"></b></span>
            <span style="color:var(--e3)"><i></i>ω<sub>3</sub> <b class="mono" data-k="2"></b></span>
          </div>
        </div>
        <canvas id="grafica-omega"></canvas>
      </div>
    </div>`;

    this.$('#selector-vista').addEventListener('click', e => e.target.dataset.vista && this.cambiarVista(e.target.dataset.vista));
    this.$('#selector-cuerpo').addEventListener('click', e => e.target.dataset.cuerpo && this.cambiarCuerpo(e.target.dataset.cuerpo));
    this.contenedor.querySelectorAll('[data-opcion]').forEach(b => b.addEventListener('click', () => this.alternar(b.dataset.opcion)));
    this.$('#boton-grabar').addEventListener('click', () => this.grabar());
    this.actualizarBotones();
  }

  // Graba el visor de actitud (cuerpo o Poinsot) en .webm para usarlo en las diapositivas.
  grabar() {
    const boton = this.$('#boton-grabar');
    if (this.grabadora) { this.grabadora.stop(); return; }
    const flujo = this.visorActitud.renderer.domElement.captureStream(60);
    const tipo = ['video/webm;codecs=vp9', 'video/webm'].find(t => MediaRecorder.isTypeSupported(t));
    const partes = [];
    this.grabadora = new MediaRecorder(flujo, { mimeType: tipo, videoBitsPerSecond: 12e6 });
    this.grabadora.ondataavailable = e => e.data.size && partes.push(e.data);
    this.grabadora.onstop = () => {
      const enlace = document.createElement('a');
      enlace.href = URL.createObjectURL(new Blob(partes, { type: 'video/webm' }));
      const r = this.r;
      enlace.download = `orbita_${this.vista}_${this.tipoCuerpo}_eje${r ? r.eje + 1 : ''}_${r ? r.nombre_metodo : ''}.webm`;
      enlace.click();
      this.grabadora = null;
      boton.classList.remove('activo');
      boton.querySelector('.texto').textContent = 'Record';
      this.ctx.aviso('Video saved to the Downloads folder');
    };
    this.grabadora.start(250);
    boton.classList.add('activo');
    boton.querySelector('.texto').textContent = 'Stop';
  }

  actualizarBotones() {
    this.contenedor.querySelectorAll('[data-opcion]').forEach(b => b.classList.toggle('activo', !!this.opciones[b.dataset.opcion]));
    this.$('#selector-vista').querySelectorAll('button').forEach(b => b.classList.toggle('activo', b.dataset.vista === this.vista));
    this.$('#selector-cuerpo').querySelectorAll('button').forEach(b => b.classList.toggle('activo', b.dataset.cuerpo === this.tipoCuerpo));
    this.$('#selector-cuerpo').classList.toggle('oculto', this.vista !== 'cuerpo');
    this.$('#nota-cuerpo').textContent = this.vista === 'cuerpo' ? tiposCuerpo[this.tipoCuerpo].nota
      : 'Energy ellipsoid fixed to the body, rolling without slipping on the invariable plane';
    this.$('#sub-actitud').textContent = this.vista === 'cuerpo' ? 'Body axes, the spin vector ω and the fixed angular momentum L'
      : 'Polhode traced on the ellipsoid · herpolhode traced on the plane ⊥ L';
    this.$('#leyenda-integradores').classList.toggle('oculto', !this.opciones.integradores);
  }

  // ------------------------------------------------------------ escenas (una vez)
  construirEscenas() {
    this.visorActitud = crearVisor(this.$('#visor-actitud'), { posicion: [2.35, -2.95, 1.35] });
    this.visorFases = crearVisor(this.$('#visor-fases'), { posicion: vistaFases(1.48) });
    for (const visor of [this.visorActitud, this.visorFases])
      visor.controles.addEventListener('start', () => { this.ultimaInteraccion = performance.now(); visor.controles.autoRotate = false; });

    // Escena del cuerpo
    this.escenaCuerpo = this.visorActitud.escena;
    this.cielos = [crearCielo(this.escenaCuerpo)];
    crearLuces(this.escenaCuerpo);
    this.grupoCuerpo = new THREE.Group();
    this.escenaCuerpo.add(this.grupoCuerpo);
    this.flechasEjes = [0, 1, 2].map(k => {
      const flecha = crearFlecha(color(`e${k+1}`), { radio: .009, punta: .06, emisivo: 1.8 });
      flecha.apuntar([k === 0 ? 1 : 0, k === 1 ? 1 : 0, k === 2 ? 1 : 0], largoEjes);
      const etiqueta = crearEtiqueta(`e<sub>${k+1}</sub>`);
      etiqueta.element.style.color = `var(--e${k+1})`;
      etiqueta.position.set(k === 0 ? largoEjes + .08 : 0, k === 1 ? largoEjes + .08 : 0, k === 2 ? largoEjes + .08 : 0);
      this.grupoCuerpo.add(flecha, etiqueta);
      return flecha;
    });
    this.esferaPuntas = esferaReticula(largoEjes);
    this.escenaCuerpo.add(this.esferaPuntas);
    this.flechaL = crearFlecha(color('momento-l'), { radio: .009, punta: .075, emisivo: .35 });
    this.flechaOmega = crearFlecha(color('omega'), { radio: .011, punta: .08, emisivo: 2 });
    this.etiquetaL = crearEtiqueta('L', 'grande'); this.etiquetaL.element.style.color = 'var(--momento-l)';
    this.etiquetaOmega = crearEtiqueta('ω', 'grande'); this.etiquetaOmega.element.style.color = 'var(--omega)';
    this.grupoVectores = new THREE.Group();
    this.grupoVectores.add(this.flechaL, this.flechaOmega, this.etiquetaL, this.etiquetaOmega);
    this.escenaCuerpo.add(this.grupoVectores);
    this.grupoEstelas = new THREE.Group();
    this.escenaCuerpo.add(this.grupoEstelas);
    this.grupoFantasmas = new THREE.Group();
    this.escenaCuerpo.add(this.grupoFantasmas);

    // Escena de Poinsot (mismo visor, se alterna)
    this.escenaPoinsot = new THREE.Scene();
    this.escenaPoinsot.environment = this.escenaCuerpo.environment;
    this.escenaPoinsot.environmentIntensity = .5;
    this.cielos.push(crearCielo(this.escenaPoinsot));
    crearLuces(this.escenaPoinsot);
    this.grupoPoinsot = new THREE.Group();
    this.escenaPoinsot.add(this.grupoPoinsot);

    // Escena del espacio de fases
    this.escenaFases = this.visorFases.escena;
    this.cielos.push(crearCielo(this.escenaFases));
    crearLuces(this.escenaFases);
    this.grupoFases = new THREE.Group();
    this.escenaFases.add(this.grupoFases);
    this.ajustarCielos();
  }

  ajustarCielos() {
    for (const cielo of this.cielos) {
      const u = cielo.userData.fondo.material.uniforms;
      u.uA.value = color('cielo-1'); u.uB.value = color('cielo-2'); u.uC.value = color('cielo-3');
      cielo.children.forEach(o => { if (o.isPoints) o.visible = temaOscuro(); });
    }
    // En el espacio de fases las estrellas solo acompañan: la mitad de intensidad.
    this.cielos[2].children.forEach(o => { if (o.isPoints) o.material.opacity = o.userData.opacidad * .5; });
  }

  // ------------------------------------------------------------ dibujo estático (una vez por cálculo)
  dibujar() {
    const r = this.estado.resultado;
    this.r = r;
    this.quats = cuaternionesDesdeMatrices(r.movimiento.rotaciones);
    this.omegaMax = Math.max(...r.web.herpolhoda.map(w => Math.hypot(...w)));
    this.colorEje = color(`e${r.eje + 1}`);
    this.contenedor.style.setProperty('--eje-color', `var(--e${r.eje + 1})`);
    this.fantasmas = null;
    this.dibujarCuerpo();
    this.dibujarEstelas();
    this.dibujarPoinsot();
    this.dibujarEspacioFases();
    this.escribirInformacion();
    this.grafica.datos(r);
    if (this.vista === 'poinsot') volarCamara(this.visorActitud, this.vistaPoinsot.posicion, this.vistaPoinsot.objetivo, this.vistaPoinsot.arriba, 800);
    this.volteosMostrados = -1;
    this.vaciar(this.grupoFantasmas);
    if (this.opciones.integradores) this.cargarFantasmas();
  }

  vaciar(grupo) { for (const hijo of [...grupo.children]) liberar(hijo); }

  dibujarCuerpo() {
    if (this.cuerpo) liberar(this.cuerpo);
    this.cuerpo = crearCuerpo(this.tipoCuerpo, this.r.movimiento.dimensiones);
    this.grupoCuerpo.add(this.cuerpo);
    this.flechasEjes.forEach((f, k) => f.userData.material.emissiveIntensity = (k === this.r.eje ? 2.6 : 1.2)*intensidadBrillo);
  }

  dibujarEstelas() {
    this.vaciar(this.grupoEstelas);
    const { t, ventana_estela: ventana, eje } = this.r;
    const R = this.r.movimiento.rotaciones;
    this.tubos = [];
    // Puntas de los tres ejes del cuerpo en ejes inerciales: columnas de R(q).
    for (let k = 0; k < 3; k++) {
      const puntas = R.map(M => [M[0][k]*largoEjes, M[1][k]*largoEjes, M[2][k]*largoEjes]);
      const principal = k === eje;
      const tubo = crearTubo(puntas, t, { radio: principal ? .011 : .0065, color: color(`e${k+1}`), ventana,
        opacidad: principal ? 1 : .5, brillo: principal ? 2.2 : 1.2 });
      this.grupoEstelas.add(tubo); this.tubos.push(tubo);
    }
    // Cono del espacio: la dirección de ω en ejes inerciales.
    if (this.tuboOmega) liberar(this.tuboOmega);
    const direcciones = this.r.web.herpolhoda.map(w => { const n = Math.hypot(...w); return [w[0]/n*1.12, w[1]/n*1.12, w[2]/n*1.12]; });
    this.tuboOmega = crearTubo(direcciones, t, { radio: .006, color: color('omega'), ventana, opacidad: .75, brillo: 1.8 });
    this.grupoVectores.add(this.tuboOmega); this.tubos.push(this.tuboOmega);
    const L = this.r.movimiento.vector_momento, nL = Math.hypot(...L);
    this.flechaL.apuntar(L.map(v => v/nL), 1.22);
    this.etiquetaL.position.set(...L.map(v => v/nL*1.32));
  }

  dibujarPoinsot() {
    this.vaciar(this.grupoPoinsot);
    const { t, U, web, movimiento } = this.r;
    const R = movimiento.radio;
    this.escalaPoinsot = R;
    // Elipsoide de energía unido al cuerpo, con la polhoda que va dejando.
    this.elipsoidePoinsot = new THREE.Group();
    const [X, Y, Z] = web.elipsoide_energia;
    const malla = new THREE.Mesh(geometriaElipsoide(X, Y, Z), materialFresnel(color('energia'), { opacidad: .6, nucleo: .1 }));
    malla.renderOrder = 2;
    this.elipsoidePoinsot.add(malla, rejillaElipsoide(X, Y, Z, 8, color('energia'), .28));
    const polhoda = crearTubo(U.map(u => [u[0], u[1], u[2]]), t, { radio: .012*R, color: color('polhoda'), ventana: -2, brillo: 1.6 });
    this.elipsoidePoinsot.add(polhoda); this.tubos.push(polhoda);
    for (let k = 0; k < 3; k++) {
      const semieje = [X, Y, Z][k].flat().reduce((m, v) => Math.max(m, Math.abs(v)), 0);
      const linea = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(k === 0, k === 1, k === 2).multiplyScalar(semieje*1.25)]),
        new THREE.LineBasicMaterial({ color: color(`e${k+1}`), transparent: true, opacity: .9 }));
      this.elipsoidePoinsot.add(linea);
    }
    this.grupoPoinsot.add(this.elipsoidePoinsot);

    // Plano invariable: perpendicular a L, a distancia 2T/|L| del centro.
    const n = new THREE.Vector3(...web.normal_plano), d = web.distancia_plano;
    const radioPlano = 2.6*R;
    const plano = new THREE.Mesh(new THREE.CircleGeometry(radioPlano, 96), new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
      uniforms: { uColor: { value: color('acento') }, uRadio: { value: radioPlano }, uPaso: { value: R/4 }, uOscuro: { value: temaOscuro() ? 1 : 0 } },
      vertexShader: `varying vec2 vP; void main(){ vP = position.xy; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
      fragmentShader: `uniform vec3 uColor; uniform float uRadio; uniform float uPaso; uniform float uOscuro; varying vec2 vP;
        void main(){
          vec2 g = abs(fract(vP/uPaso - .5) - .5)/fwidth(vP/uPaso);
          float linea = 1. - min(min(g.x, g.y), 1.);
          float r = length(vP)/uRadio, borde = 1. - smoothstep(.55, 1., r);
          gl_FragColor = vec4(uColor*(.6 + .8*linea), (.05 + .42*linea + .06*(1.-r))*borde);
        }`,
    }));
    plano.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
    plano.position.copy(n).multiplyScalar(d);
    plano.renderOrder = 1;
    this.grupoPoinsot.add(plano);
    const herpolhoda = crearTubo(web.herpolhoda.map(w => [w[0] - n.x*.003*R, w[1] - n.y*.003*R, w[2] - n.z*.003*R]), t,
      { radio: .011*R, color: color('punto'), ventana: -3, brillo: 2.2 });
    this.grupoPoinsot.add(herpolhoda); this.tubos.push(herpolhoda);
    this.contacto = new THREE.Mesh(new THREE.SphereGeometry(.03*R, 24, 16), new THREE.MeshBasicMaterial({ color: color('punto') }));
    this.haloContacto = crearHalo(color('punto'), .32*R);
    this.flechaLPoinsot = crearFlecha(color('momento-l'), { radio: .007*R, punta: .07*R, emisivo: .3 });
    this.flechaLPoinsot.apuntar(n, d*1.55);
    this.flechaOmegaPoinsot = crearFlecha(color('omega'), { radio: .008*R, punta: .07*R, emisivo: 2 });
    const eL = crearEtiqueta('L', 'grande'); eL.element.style.color = 'var(--momento-l)'; eL.position.copy(n).multiplyScalar(d*1.68);
    this.etiquetaOmegaPoinsot = crearEtiqueta('ω', 'grande'); this.etiquetaOmegaPoinsot.element.style.color = 'var(--omega)';
    const eP = crearEtiqueta('invariable plane', 'pequena'); eP.element.style.color = 'var(--acento)';
    const u = new THREE.Vector3().crossVectors(n, Math.abs(n.z) < .9 ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0)).normalize();
    eP.position.copy(n).multiplyScalar(d).addScaledVector(u, -radioPlano*.42);
    this.grupoPoinsot.add(this.contacto, this.haloContacto, this.flechaLPoinsot, this.flechaOmegaPoinsot, eL, this.etiquetaOmegaPoinsot, eP);

    // Cámara: L hacia arriba, el plano encima y el elipsoide rodando por debajo (la figura clásica).
    const v = new THREE.Vector3().crossVectors(n, u);
    this.vistaPoinsot = {
      posicion: n.clone().multiplyScalar(-.55*R).addScaledVector(u, 3.9*R).addScaledVector(v, -1.9*R).toArray(),
      objetivo: n.clone().multiplyScalar(d*.35).toArray(), arriba: n.toArray(),
    };
  }

  dibujarEspacioFases() {
    this.vaciar(this.grupoFases);
    const { t, U, web, movimiento, ventana_estela } = this.r;
    const R = movimiento.radio;
    // Si cambia el tamaño, la cámara se acerca o aleja conservando el ángulo elegido.
    if (this.escalaFases && Math.abs(R/this.escalaFases - 1) > 1e-6) {
      const k = R/this.escalaFases, c = this.visorFases;
      volarCamara(c, c.camara.position.clone().multiplyScalar(k).toArray(), c.controles.target.clone().multiplyScalar(k).toArray(), null, 800);
    }
    this.escalaFases = R;
    for (let k = 0; k < 3; k++) {
      const e = new THREE.Vector3(k === 0, k === 1, k === 2);
      const linea = new THREE.Line(new THREE.BufferGeometry().setFromPoints([e.clone().multiplyScalar(-R), e.clone().multiplyScalar(R)]),
        new THREE.LineBasicMaterial({ color: color(`e${k+1}`), transparent: true, opacity: .7 }));
      const etiqueta = crearEtiqueta(`ω<sub>${k+1}</sub>`, 'grande');
      etiqueta.element.style.color = `var(--e${k+1})`;
      etiqueta.position.copy(e).multiplyScalar(R*1.12);
      this.grupoFases.add(linea, etiqueta);
    }
    this.elipsoides = new THREE.Group();
    const [Xe, Ye, Ze] = web.elipsoide_energia, [Xm, Ym, Zm] = web.elipsoide_momento;
    const energia = new THREE.Mesh(geometriaElipsoide(Xe, Ye, Ze), materialFresnel(color('energia'), { opacidad: .55, nucleo: .08 }));
    const momento = new THREE.Mesh(geometriaElipsoide(Xm, Ym, Zm), materialFresnel(color('momento'), { opacidad: .4, nucleo: .05 }));
    energia.renderOrder = momento.renderOrder = 2;
    this.elipsoides.add(energia, momento, rejillaElipsoide(Xe, Ye, Ze, 8, color('energia'), .16), rejillaElipsoide(Xm, Ym, Zm, 12, color('momento'), .08));
    this.grupoFases.add(this.elipsoides);
    for (const curva of movimiento.separatriz) {
      const puntos = curva[0].map((x, i) => [x, curva[1][i], curva[2][i]]);
      this.grupoFases.add(crearTubo(puntos, null, { radio: .0065*R, color: color('separatriz'), dash: .05*R, brillo: 0, cerrar: true }));
    }
    const polhoda = crearTubo(U.map(u => [u[0], u[1], u[2]]), t, { radio: .011*R, color: color('polhoda'), ventana: .35*ventana_estela,
      base: .16, futuro: .16, brillo: 1.8 });
    this.grupoFases.add(polhoda); this.tubos.push(polhoda);
    // Familia de polhodas del mismo |L| (integradas en Python con RK4).
    this.familia = new THREE.Group();
    const sobreI3 = web.familia_polhodas.length / 2;
    web.familia_polhodas.forEach((curva, i) => this.familia.add(crearTubo(curva, null, {
      radio: .0045*R, color: color(i < sobreI3 ? 'e3' : 'e1'), opacidad: .55, brillo: 0 })));
    for (const curva of web.separatriz_momento) {
      const puntos = curva[0].map((x, i) => [x, curva[1][i], curva[2][i]]);
      this.familia.add(crearTubo(puntos, null, { radio: .0045*R, color: color('separatriz'), dash: .04*R, opacidad: .8, brillo: 0 }));
    }
    this.grupoFases.add(this.familia);
    this.puntoFases = new THREE.Mesh(new THREE.SphereGeometry(.028*R, 24, 16), new THREE.MeshBasicMaterial({ color: color('punto') }));
    this.haloFases = crearHalo(color('punto'), .3*R);
    this.pulso = crearHalo(color(`e${this.r.eje + 1}`), .1*R, 0);
    this.grupoFases.add(this.puntoFases, this.haloFases, this.pulso);
    this.fantasmasFases = new THREE.Group();
    this.grupoFases.add(this.fantasmasFases);
    this.aplicarOpciones();
  }

  escribirInformacion() {
    const r = this.r, m = r.movimiento;
    const real = Math.abs(m.autovalor.im) < 1e-14;
    const modulo = Math.hypot(m.autovalor.re, m.autovalor.im);
    const insignia = this.$('#insignia');
    insignia.style.setProperty('--color-estado', real ? 'var(--mal)' : 'var(--bien)');
    this.$('#estado-estabilidad').textContent = real ? 'UNSTABLE' : 'STABLE';
    this.$('#tipo-estabilidad').innerHTML = `Spin about ${['minor', 'intermediate', 'major'][r.eje]} axis<br>${real ? 'saddle · real λ' : 'centre · imaginary λ'}`;
    this.$('#autovalor').innerHTML = `λ = ±${modulo.toFixed(4)}${real ? '' : ' i'}<small>s⁻¹</small>`;
    const { teorico, medido } = r.web.intervalo_volteos;
    const hayVolteos = medido !== null;
    this.$('#flip-teoria').textContent = real || r.eje === 1 ? (teorico ? `${teorico.toFixed(3)} s` : '∞ (separatrix)') : 'no flips';
    this.$('#flip-medido').textContent = hayVolteos ? `${medido.toFixed(3)} s` : r.instantes_volteo.length ? '1 flip only' : 'no flips';
    this.$('#flip-acuerdo').textContent = hayVolteos && teorico ? `relative difference ${(100*Math.abs(medido/teorico - 1)).toExponential(1)} %`
      : real ? 'Extend t_f to see two flips' : 'Stable spin: ω stays close to the axis';
    const escribir = (id, texto) => { const e = this.$(id); if (e.textContent !== texto) { e.textContent = texto; e.classList.remove('cambio'); void e.offsetWidth; e.classList.add('cambio'); } };
    escribir('#d-periodo', m.periodo ? `${m.periodo.toFixed(3)} s` : '∞');
    escribir('#d-lado', { 1: 'around I3', '-1': 'around I1', 0: 'separatrix' }[m.lado_separatriz]);
    this.$('#d-lado').innerHTML = this.$('#d-lado').textContent.replace(/I(\d)/, 'I<sub>$1</sub>');
    escribir('#d-casimir', m.casimir.toExponential(2));
    escribir('#d-paso', r.adaptativo ? `adaptive · tol ${r.tol.toExponential(0)}` : `Δt = ${this.ctx.formatoNumero(r.dt_utilizado)} s`);
    this.$('#barras-derivas').innerHTML = ['2T', 'L²', '|q|'].map((nombre, k) => {
      const d = r.derivas[k], fraccion = d > 0 ? Math.min(Math.max((Math.log10(d) + 16)/16, .015), 1) : .015;
      return `<div class="barra-deriva"><div class="cabeza"><span>${nombre}</span><span>${d ? d.toExponential(1) : '0'}</span></div>
        <div class="carril"><div class="relleno" data-ancho="${fraccion}"></div></div></div>`;
    }).join('');
    requestAnimationFrame(() => this.contenedor.querySelectorAll('.relleno').forEach(b => {
      b.style.setProperty('--ancho-total', `${b.parentElement.clientWidth}px`); b.style.width = `${100*b.dataset.ancho}%`; }));
  }

  // ------------------------------------------------------------ tres integradores a la vez
  async cargarFantasmas() {
    this.$('#cargando-actitud').classList.add('visible');
    const datos = await this.ctx.pedirPagina(0);
    this.$('#cargando-actitud').classList.remove('visible');
    if (!datos || this.estado.resultado !== this.r) return;
    this.vaciar(this.grupoFantasmas);
    this.vaciar(this.fantasmasFases);
    this.fantasmas = Object.entries(datos.fantasmas).map(([nombre, f]) => {
      const c = color(variableMetodo[nombre]);
      const seleccionado = nombre === this.r.nombre_metodo;
      const cuerpo = seleccionado ? null : crearFantasma(this.cuerpo, c);
      const flecha = crearFlecha(c, { radio: .007, punta: .05, emisivo: 2.2 });
      const etiqueta = crearEtiqueta(this.ctx.nombresCortos[nombre], 'pequena'); etiqueta.element.style.color = `var(--${variableMetodo[nombre]})`;
      etiqueta.userData.orden = Object.keys(variableMetodo).indexOf(nombre);
      const grupo = new THREE.Group();
      if (cuerpo) grupo.add(cuerpo);
      grupo.add(flecha, etiqueta);
      this.grupoFantasmas.add(grupo);
      const punto = new THREE.Mesh(new THREE.SphereGeometry(.022*this.escalaFases, 16, 12), new THREE.MeshBasicMaterial({ color: c }));
      punto.add(crearHalo(c, .22*this.escalaFases, .8));
      this.fantasmasFases.add(punto);
      return { nombre, grupo, cuerpo, flecha, etiqueta, punto, quats: cuaternionesDesdeMatrices(f.rotaciones), omega: f.omega, fin: f.fin };
    });
    this.aplicarOpciones();
  }

  // ------------------------------------------------------------ opciones y vistas
  alternar(opcion) {
    this.opciones[opcion] = !this.opciones[opcion];
    if (opcion === 'integradores' && this.opciones.integradores && this.r && !this.fantasmas) this.cargarFantasmas();
    this.aplicarOpciones();
  }
  aplicarOpciones() {
    this.grupoEstelas.visible = this.opciones.estelas;
    this.esferaPuntas.visible = this.opciones.estelas;
    this.grupoVectores.visible = this.opciones.vectores;
    this.grupoFantasmas.visible = this.opciones.integradores;
    if (this.fantasmasFases) this.fantasmasFases.visible = this.opciones.integradores;
    if (this.elipsoides) this.elipsoides.visible = this.opciones.elipsoides;
    if (this.familia) this.familia.visible = this.opciones.familia;
    this.actualizarBotones();
  }
  cambiarVista(vista) {
    if (vista === this.vista) return;
    this.vista = vista;
    if (vista === 'poinsot') {
      this.visorActitud.usarEscena(this.escenaPoinsot, this.visorActitud.camara);
      const { posicion, objetivo, arriba } = this.vistaPoinsot;
      volarCamara(this.visorActitud, posicion, objetivo, arriba, 1100);
    } else {
      this.visorActitud.usarEscena(this.escenaCuerpo, this.visorActitud.camara);
      volarCamara(this.visorActitud, [2.35, -2.95, 1.35], [0, 0, 0], [0, 0, 1], 1100);
    }
    this.actualizarBotones();
  }
  cambiarCuerpo(tipo) {
    this.tipoCuerpo = tipo;
    if (this.vista !== 'cuerpo') this.cambiarVista('cuerpo');
    if (this.r) {
      this.dibujarCuerpo();
      if (this.fantasmas) for (const f of this.fantasmas) if (f.cuerpo) {
        const nuevo = crearFantasma(this.cuerpo, color(variableMetodo[f.nombre]));
        liberar(f.cuerpo); f.grupo.add(nuevo); f.cuerpo = nuevo;
      }
    }
    this.actualizarBotones();
  }
  restablecerCamaras() {
    if (this.vista === 'poinsot') volarCamara(this.visorActitud, this.vistaPoinsot.posicion, this.vistaPoinsot.objetivo, this.vistaPoinsot.arriba);
    else volarCamara(this.visorActitud, [2.35, -2.95, 1.35], [0, 0, 0], [0, 0, 1]);
    volarCamara(this.visorFases, vistaFases(this.escalaFases ?? 1.48), [0, 0, 0], [0, 0, 1]);
  }
  pulsarTecla(tecla) {
    const cuerpos = Object.keys(tiposCuerpo);
    const acciones = {
      b: () => this.cambiarCuerpo(cuerpos[(cuerpos.indexOf(this.tipoCuerpo) + 1) % cuerpos.length]),
      o: () => this.cambiarVista(this.vista === 'cuerpo' ? 'poinsot' : 'cuerpo'),
      c: () => this.alternar('integradores'), v: () => this.restablecerCamaras(), g: () => this.grabar(),
    };
    if (!acciones[tecla]) return false;
    acciones[tecla]();
    return true;
  }
  cambiarTema() {
    this.ajustarCielos();
    this.flechasEjes.forEach((f, k) => { f.userData.material.color = color(`e${k+1}`); f.userData.material.emissive = color(`e${k+1}`); });
    for (const [flecha, nombre] of [[this.flechaL, 'momento-l'], [this.flechaOmega, 'omega']]) {
      flecha.userData.material.color = color(nombre); flecha.userData.material.emissive = color(nombre);
    }
    this.esferaPuntas.material.color = color('reticula');
    if (this.r) this.dibujar();
  }
  alEntrar() {
    // Entrada cinematográfica: la cámara llega desde lejos.
    const c = this.visorActitud.camara;
    c.position.set(7, -9, 5.5);
    volarCamara(this.visorActitud, [2.35, -2.95, 1.35], [0, 0, 0], [0, 0, 1], 2600);
    const R = this.escalaFases ?? 1.48;
    this.visorFases.camara.position.set(4*R, -6*R, 4.6*R);
    volarCamara(this.visorFases, vistaFases(R), [0, 0, 0], [0, 0, 1], 2800);
  }

  mostrar(visible) {
    this.visible = visible;
    this.visorActitud.activo = this.visorFases.activo = visible;
  }

  // ------------------------------------------------------------ animación (cada fotograma)
  dibujarInstante(indice, fraccion, tiempo) {
    if (!this.r || this.necesitaDibujo) return;
    const r = this.r;
    for (const tubo of this.tubos) tubo.material.uniforms.uTiempo.value = tiempo;
    // Cuerpo: orientación interpolada entre las dos muestras más próximas.
    interpolarCuaternion(this.quats, indice, fraccion, this.grupoCuerpo.quaternion);
    const w = interpolarPunto(r.web.herpolhoda, indice, fraccion, this._w ??= new THREE.Vector3());
    const modulo = w.length();
    this.flechaOmega.apuntar(w.clone().divideScalar(modulo), 1.12);
    this.etiquetaOmega.position.copy(w).multiplyScalar(1.24/modulo);
    // Poinsot: el elipsoide gira con el cuerpo y toca el plano en ω.
    this.elipsoidePoinsot.quaternion.copy(this.grupoCuerpo.quaternion);
    this.contacto.position.copy(w); this.haloContacto.position.copy(w);
    this.flechaOmegaPoinsot.apuntar(w, modulo);
    this.etiquetaOmegaPoinsot.position.copy(w).multiplyScalar(.55).add(new THREE.Vector3(...r.web.normal_plano).multiplyScalar(-.12*this.escalaPoinsot));
    // Espacio de fases
    const p = interpolarPunto(r.U, indice, fraccion, this._p ??= new THREE.Vector3());
    this.puntoFases.position.copy(p); this.haloFases.position.copy(p); this.pulso.position.copy(p);
    if (this.fantasmas) for (const f of this.fantasmas) {
      const vivo = tiempo <= f.fin;
      f.grupo.visible = f.punto.visible = vivo;
      if (!vivo) continue;
      interpolarCuaternion(f.quats, indice, fraccion, f.grupo.quaternion);
      const e = [0, 0, 0]; e[r.eje] = 1;
      f.flecha.apuntar(e, .98);
      f.etiqueta.position.set(...e.map(v => v*(1.1 + .13*f.etiqueta.userData.orden)));
      interpolarPunto(f.omega, indice, fraccion, f.punto.position);
    }
    // Volteos: contador, destello y pulso cuando el eje de giro cambia de sentido.
    const volteos = r.instantes_volteo;
    let n = 0;
    while (n < volteos.length && volteos[n] <= tiempo) n++;
    if (n !== this.volteosMostrados) {
      const nuevo = n === this.volteosMostrados + 1 && this.volteosMostrados >= 0;
      this.volteosMostrados = n;
      const numero = this.$('#volteos');
      numero.textContent = n;
      if (nuevo) {
        numero.classList.remove('salto'); void numero.offsetWidth; numero.classList.add('salto');
        for (const id of ['#destello-actitud', '#destello-fases']) {
          const d = this.$(id); d.classList.remove('activo'); void d.offsetWidth; d.classList.add('activo');
        }
        this.inicioPulso = performance.now();
      }
    }
    const siguiente = volteos.find(v => v > tiempo);
    this.$('#volteos-detalle').textContent = Math.abs(r.movimiento.autovalor.im) > 1e-14
      ? 'Stable spin · no flips' : siguiente !== undefined ? `next flip in ${(siguiente - tiempo).toFixed(1)} s` : 'no more flips before t_f';
    this.grafica.dibujar(indice, fraccion, tiempo);
  }

  fotograma(ahora) {
    if (!this.visible) return;
    if (this.inicioPulso !== undefined && this.pulso) {
      const s = (ahora - this.inicioPulso) / 900;
      if (s < 1) { this.pulso.scale.setScalar((.1 + 1.1*s)*this.escalaFases); this.pulso.material.opacity = (1 - s)*intensidadBrillo; }
      else { this.pulso.material.opacity = 0; this.inicioPulso = undefined; }
    }
    // En reposo, la cámara gira despacio por sí sola.
    const quieto = !this.estado.reproduciendo && ahora - this.ultimaInteraccion > 5000;
    this.visorActitud.controles.autoRotate = this.visorFases.controles.autoRotate = quieto;
    this.visorActitud.dibujar();
    this.visorFases.dibujar();
  }
}

// Esfera de referencia para las puntas de los ejes: meridianos y paralelos cada 30°.
function esferaReticula(radio) {
  const pos = [];
  for (let m = 0; m < 6; m++) for (let k = 0; k < 64; k++) {
    const f = m*Math.PI/6, a = k*Math.PI/32, b = (k+1)*Math.PI/32;
    pos.push(radio*Math.sin(a)*Math.cos(f), radio*Math.sin(a)*Math.sin(f), radio*Math.cos(a),
             radio*Math.sin(b)*Math.cos(f), radio*Math.sin(b)*Math.sin(f), radio*Math.cos(b));
  }
  for (const lat of [-60, -30, 0, 30, 60]) for (let k = 0; k < 96; k++) {
    const z = radio*Math.sin(lat*Math.PI/180), r = radio*Math.cos(lat*Math.PI/180), a = k*Math.PI/48, b = (k+1)*Math.PI/48;
    pos.push(r*Math.cos(a), r*Math.sin(a), z, r*Math.cos(b), r*Math.sin(b), z);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: color('reticula'), transparent: true, opacity: .09, depthWrite: false }));
}

// ------------------------------------------------------------ gráfica ω(t): lienzo 2D propio (60 fps)
class GraficaOmega {
  constructor(lienzo, pagina) {
    this.lienzo = lienzo;
    this.pagina = pagina;
    this.g = lienzo.getContext('2d');
    this.margen = { izquierda: 44, derecha: 10, arriba: 8, abajo: 20 };
    this.raton = null;
    new ResizeObserver(() => this.redimensionar()).observe(lienzo);
    const tiempoEn = (e) => {
      const caja = lienzo.getBoundingClientRect(), x = e.clientX - caja.left;
      return Math.min(Math.max((x - this.margen.izquierda) / (caja.width - this.margen.izquierda - this.margen.derecha), 0), 1) * (this.tf ?? 0);
    };
    lienzo.addEventListener('pointerdown', e => {
      if (!this.t) return;
      lienzo.setPointerCapture(e.pointerId);
      pagina.estado.arrastrando = true;
      pagina.ctx.mostrarInstante(tiempoEn(e));
    });
    lienzo.addEventListener('pointermove', e => {
      const caja = lienzo.getBoundingClientRect();
      this.raton = e.clientX - caja.left;
      if (pagina.estado.arrastrando && this.t) pagina.ctx.mostrarInstante(tiempoEn(e));
    });
    lienzo.addEventListener('pointerleave', () => { this.raton = null; });
    lienzo.addEventListener('pointerup', () => { pagina.estado.arrastrando = false; });
  }

  redimensionar() {
    const caja = this.lienzo.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio, 2);
    this.ancho = caja.width; this.alto = caja.height; this.dpr = dpr;
    this.lienzo.width = Math.max(1, caja.width * dpr); this.lienzo.height = Math.max(1, caja.height * dpr);
    this.estatica = null;
  }

  datos(r) {
    this.t = r.t; this.U = r.U; this.d = r.indices_dibujo; this.volteos = r.instantes_volteo; this.tf = r.t.at(-1);
    let m = 0;
    for (const u of r.U) m = Math.max(m, Math.abs(u[0]), Math.abs(u[1]), Math.abs(u[2]));
    this.m = m * 1.15;
    this.estatica = null;
  }

  x(t) { return this.margen.izquierda + t / this.tf * (this.ancho - this.margen.izquierda - this.margen.derecha); }
  y(v) { return this.margen.arriba + (1 - (v + this.m) / (2*this.m)) * (this.alto - this.margen.arriba - this.margen.abajo); }

  colores() {
    const estilo = getComputedStyle(document.documentElement), v = n => estilo.getPropertyValue(`--${n}`).trim();
    return { ejes: [v('e1'), v('e2'), v('e3')], linea: v('linea'), linea2: v('linea-2'), tenue: v('tenue'), texto: v('texto'), eje: v(`e${this.pagina.r.eje + 1}`) };
  }

  dibujarEstatica() {
    const c = document.createElement('canvas');
    c.width = this.lienzo.width; c.height = this.lienzo.height;
    const g = c.getContext('2d'), col = this.colores();
    g.scale(this.dpr, this.dpr);
    g.font = `10px ${getComputedStyle(document.documentElement).getPropertyValue('--mono')}`;
    g.fillStyle = col.tenue; g.strokeStyle = col.linea; g.lineWidth = 1;
    const marcas = [-this.m/1.15, -this.m/2.3, 0, this.m/2.3, this.m/1.15];
    for (const v of marcas) {
      g.beginPath(); g.moveTo(this.margen.izquierda, this.y(v)); g.lineTo(this.ancho - this.margen.derecha, this.y(v));
      g.strokeStyle = v === 0 ? col.linea2 : col.linea; g.stroke();
      g.textAlign = 'right'; g.textBaseline = 'middle'; g.fillText(v.toFixed(2), this.margen.izquierda - 6, this.y(v));
    }
    const paso = [1, 2, 5, 10, 20, 25, 50][[1, 2, 5, 10, 20, 25, 50].findIndex(p => this.tf / p <= 10)] ?? 50;
    g.textAlign = 'center'; g.textBaseline = 'top';
    for (let t = 0; t <= this.tf + 1e-9; t += paso) g.fillText(`${t} s`, this.x(t), this.alto - this.margen.abajo + 5);
    g.setLineDash([3, 4]); g.strokeStyle = col.eje; g.globalAlpha = .55;
    for (const t of this.volteos) { g.beginPath(); g.moveTo(this.x(t), this.margen.arriba); g.lineTo(this.x(t), this.alto - this.margen.abajo); g.stroke(); }
    g.setLineDash([]); g.globalAlpha = .22; g.lineWidth = 1.2;
    for (let k = 0; k < 3; k++) {
      g.strokeStyle = col.ejes[k]; g.beginPath();
      this.d.forEach((i, j) => j ? g.lineTo(this.x(this.t[i]), this.y(this.U[i][k])) : g.moveTo(this.x(this.t[i]), this.y(this.U[i][k])));
      g.stroke();
    }
    this.estatica = c; this.col = col;
  }

  dibujar(indice, fraccion, tiempo) {
    if (!this.t || this.ancho < 10) return;
    if (!this.estatica) this.dibujarEstatica();
    const g = this.g, col = this.col;
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.clearRect(0, 0, this.lienzo.width, this.lienzo.height);
    g.drawImage(this.estatica, 0, 0);
    g.scale(this.dpr, this.dpr);
    // Búsqueda del último punto dibujable antes del instante actual.
    let a = 0, b = this.d.length;
    while (a < b) { const m = (a + b) >> 1; if (this.d[m] <= indice) a = m + 1; else b = m; }
    const actual = this.pagina.r.U[indice], siguiente = this.pagina.r.U[Math.min(indice + 1, this.t.length - 1)];
    g.lineWidth = 1.9; g.lineJoin = 'round';
    if (temaOscuro()) g.shadowBlur = 8;
    for (let k = 0; k < 3; k++) {
      g.strokeStyle = g.shadowColor = col.ejes[k];
      g.beginPath();
      for (let j = 0; j < a; j++) { const i = this.d[j]; j ? g.lineTo(this.x(this.t[i]), this.y(this.U[i][k])) : g.moveTo(this.x(this.t[i]), this.y(this.U[i][k])); }
      const v = actual[k] + (siguiente[k] - actual[k]) * fraccion;
      g.lineTo(this.x(tiempo), this.y(v));
      g.stroke();
    }
    g.shadowBlur = 0;
    g.strokeStyle = col.texto; g.globalAlpha = .7; g.lineWidth = 1;
    g.beginPath(); g.moveTo(this.x(tiempo), this.margen.arriba); g.lineTo(this.x(tiempo), this.alto - this.margen.abajo); g.stroke();
    g.globalAlpha = 1;
    const valores = this.pagina.contenedor.querySelectorAll('#leyenda-omega b');
    for (let k = 0; k < 3; k++) {
      const v = actual[k] + (siguiente[k] - actual[k]) * fraccion;
      g.fillStyle = col.ejes[k]; g.beginPath(); g.arc(this.x(tiempo), this.y(v), 3.6, 0, 2*Math.PI); g.fill();
      valores[k].textContent = (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(3);
    }
    if (this.raton !== null && this.raton > this.margen.izquierda) {
      g.strokeStyle = col.tenue; g.setLineDash([2, 3]);
      g.beginPath(); g.moveTo(this.raton, this.margen.arriba); g.lineTo(this.raton, this.alto - this.margen.abajo); g.stroke();
      g.setLineDash([]);
    }
  }
}
