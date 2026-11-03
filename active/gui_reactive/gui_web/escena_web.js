// Piezas 3D comunes de la GUI web (equivale a las ayudas de dibujo de style.py).
// Todo lo que hay aquí dibuja datos recibidos de Python: no hay física ni métodos numéricos.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export { THREE };

// Intensidad común de los brillos (bloom, cabezas de estela, flechas y halos).
// 1 = muy luminoso; bajar el número si los destellos tapan el contenido.
export const intensidadBrillo = .45;

// ------------------------------------------------------------ colores (definidos en style_web.css)
export function color(nombre) {
  return new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue(`--${nombre}`).trim());
}
export function temaOscuro() { return document.documentElement.dataset.tema !== 'claro'; }

// ------------------------------------------------------------ visor: renderizador, cámara, controles y bloom
export function crearVisor(contenedor, { arriba = [0, 0, 1], posicion = [2.4, -2.6, 1.6], fov = 32 } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  contenedor.appendChild(renderer.domElement);

  const etiquetas = new CSS2DRenderer();
  etiquetas.domElement.className = 'etiquetas-3d';
  contenedor.appendChild(etiquetas.domElement);

  const camara = new THREE.PerspectiveCamera(fov, 1, 0.01, 400);
  camara.up.set(...arriba);
  camara.position.set(...posicion);
  const controles = new OrbitControls(camara, renderer.domElement);
  controles.enableDamping = true;
  controles.dampingFactor = 0.08;
  controles.rotateSpeed = 0.7;
  controles.minDistance = 0.6;
  controles.maxDistance = 30;
  controles.autoRotateSpeed = 0.45;

  const escena = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  escena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  escena.environmentIntensity = 0.55;

  const composer = new EffectComposer(renderer);
  const pasoEscena = new RenderPass(escena, camara);
  const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), .6*intensidadBrillo, .4, .95);
  composer.addPass(pasoEscena);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  const visor = {
    renderer, escena, camara, controles, composer, bloom, etiquetas, contenedor, pasoEscena,
    ancho: 1, alto: 1, activo: true,
    usarEscena(otra, otraCamara = camara) {
      // Las etiquetas HTML de la escena que se deja no se repintan solas: se ocultan aquí.
      visor.escenaActual.traverse(o => { if (o.isCSS2DObject) o.element.style.display = 'none'; });
      pasoEscena.scene = otra; pasoEscena.camera = otraCamara; visor.escenaActual = otra;
    },
    escenaActual: escena,
    redimensionar() {
      const { width, height } = contenedor.getBoundingClientRect();
      if (width < 2 || height < 2) return;
      visor.ancho = width; visor.alto = height;
      renderer.setSize(width, height, false);
      renderer.domElement.style.width = `${width}px`;
      renderer.domElement.style.height = `${height}px`;
      composer.setSize(width, height);
      etiquetas.setSize(width, height);
      camara.aspect = width / height;
      camara.updateProjectionMatrix();
    },
    dibujar() {
      if (!visor.activo) return;
      if (visor.vuelo) visor.vuelo(performance.now());
      controles.update();
      bloom.enabled = temaOscuro() && visor.calidad !== 'baja';
      composer.render();
      etiquetas.render(visor.escenaActual, camara);
    },
    calidad: 'alta',
  };
  new ResizeObserver(() => visor.redimensionar()).observe(contenedor);
  visor.redimensionar();
  return visor;
}

// Transición suave de la cámara hacia una posición y un objetivo.
export function volarCamara(visor, posicion, objetivo = [0, 0, 0], arriba = null, duracion = 900) {
  const { camara, controles } = visor;
  const p0 = camara.position.clone(), o0 = controles.target.clone();
  const p1 = new THREE.Vector3(...posicion), o1 = new THREE.Vector3(...objetivo);
  const u0 = camara.up.clone(), u1 = arriba ? new THREE.Vector3(...arriba) : u0.clone();
  const inicio = performance.now();
  visor.vuelo = (ahora) => {
    const s = Math.min(1, (ahora - inicio) / duracion), e = s < .5 ? 4*s*s*s : 1 - Math.pow(-2*s + 2, 3)/2;
    camara.position.lerpVectors(p0, p1, e);
    controles.target.lerpVectors(o0, o1, e);
    camara.up.lerpVectors(u0, u1, e).normalize();
    camara.lookAt(controles.target);
    if (s >= 1) { visor.vuelo = null; reiniciarControles(visor); }
  };
}
// OrbitControls fija su eje vertical al crearse: al cambiar camera.up hay que recalcularlo.
function reiniciarControles(visor) {
  const c = visor.controles;
  c._quat?.setFromUnitVectors(visor.camara.up, new THREE.Vector3(0, 1, 0));
  c._quatInverse?.copy(c._quat).invert();
}

// ------------------------------------------------------------ fondo: cielo con estrellas fijas en ejes inerciales
export function crearCielo(escena) {
  const grupo = new THREE.Group();
  const fondo = new THREE.Mesh(new THREE.SphereGeometry(150, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { uA: { value: color('cielo-1') }, uB: { value: color('cielo-2') }, uC: { value: color('cielo-3') } },
    vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform vec3 uA; uniform vec3 uB; uniform vec3 uC; varying vec3 vDir;
      void main(){
        float n1 = pow(max(dot(vDir, normalize(vec3(.6,-.5,.35))),0.), 3.);
        float n2 = pow(max(dot(vDir, normalize(vec3(-.7,.4,-.3))),0.), 4.);
        gl_FragColor = vec4(uA + uB*n1*.55 + uC*n2*.4, 1.);
      }`,
  }));
  grupo.add(fondo);
  const aleatorio = semilla(7);
  for (const [n, tam, op] of [[1600, 1.1, .55], [450, 1.8, .8], [70, 2.8, 1.]]) {
    const pos = new Float32Array(n*3), col = new Float32Array(n*3);
    for (let i = 0; i < n; i++) {
      const z = 2*aleatorio() - 1, f = 2*Math.PI*aleatorio(), r = Math.sqrt(1 - z*z);
      pos.set([110*r*Math.cos(f), 110*r*Math.sin(f), 110*z], 3*i);
      const tinte = aleatorio();
      col.set(tinte < .2 ? [1, .85, .7] : tinte < .4 ? [.75, .82, 1] : [1, 1, 1], 3*i);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const estrellas = new THREE.Points(g, new THREE.PointsMaterial({ size: tam, sizeAttenuation: false, vertexColors: true,
      transparent: true, opacity: op, depthWrite: false }));
    estrellas.userData.opacidad = op;
    grupo.add(estrellas);
  }
  grupo.userData.fondo = fondo;
  escena.add(grupo);
  return grupo;
}
export function semilla(s) { return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// ------------------------------------------------------------ luces
export function crearLuces(escena) {
  const sol = new THREE.DirectionalLight(0xfff1dc, 2.6);
  sol.position.set(0.35*6, -0.55*6, 0.76*6);
  sol.castShadow = true;
  sol.shadow.mapSize.set(1024, 1024);
  sol.shadow.camera.left = sol.shadow.camera.bottom = -1.6;
  sol.shadow.camera.right = sol.shadow.camera.top = 1.6;
  sol.shadow.camera.near = 1; sol.shadow.camera.far = 14;
  sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.02;
  const relleno = new THREE.DirectionalLight(0x6f86ff, 0.55);
  relleno.position.set(-4, 3, -2);
  const ambiente = new THREE.AmbientLight(0x8090c0, 0.18);
  escena.add(sol, relleno, ambiente);
  return { sol, relleno, ambiente };
}

// ------------------------------------------------------------ tubos con estela: el tiempo va en cada vértice
// El tubo se construye una vez por cálculo; en cada fotograma solo cambia uTiempo.
const sombreadorTubo = {
  vertexShader: `
    attribute float aTiempo; attribute float aAvance;
    varying float vTiempo; varying float vAvance; varying vec3 vNormal; varying vec3 vVista;
    void main(){
      vTiempo = aTiempo; vAvance = aAvance;
      vec4 p = modelViewMatrix*vec4(position,1.);
      vNormal = normalize(normalMatrix*normal); vVista = normalize(-p.xyz);
      gl_Position = projectionMatrix*p;
    }`,
  fragmentShader: `
    uniform vec3 uColor; uniform float uTiempo; uniform float uVentana; uniform float uBase; uniform float uFuturo;
    uniform float uOpacidad; uniform float uDash; uniform float uBrillo;
    varying float vTiempo; varying float vAvance; varying vec3 vNormal; varying vec3 vVista;
    void main(){
      if (uDash > 0. && fract(vAvance/uDash) > .56) discard;
      float edad = uTiempo - vTiempo, a, cabeza = 0.;
      if (edad < 0.) a = uFuturo;
      else if (uVentana > 0.) { float s = clamp(1. - edad/uVentana, 0., 1.); a = max(uBase, pow(s, 1.6)); cabeza = smoothstep(.9, 1., s); }
      else { a = 1.; cabeza = 1. - smoothstep(0., abs(uVentana), edad); }   // uVentana < 0: todo el pasado, cabeza de |uVentana| s
      a *= uOpacidad;
      if (a < .01) discard;
      float luz = .55 + .45*abs(dot(vNormal, vVista));
      gl_FragColor = vec4(uColor*luz*(1. + uBrillo*cabeza), a);
    }`,
};

// ventana > 0: estela de esa duración · ventana < 0: todo el pasado, con cabeza de |ventana| s.
export function crearTubo(puntos, tiempos, { radio = .01, lados = 7, color: c = '#ffffff', ventana = -1e-3, base = 0,
  futuro = 0, opacidad = 1, dash = 0, brillo = 1.6, cerrar = false } = {}) {
  const n = puntos.length;
  const geometria = new THREE.BufferGeometry();
  if (n < 2) return new THREE.Mesh(geometria);
  const pos = new Float32Array(n*lados*3), nor = new Float32Array(n*lados*3);
  const tie = new Float32Array(n*lados), ava = new Float32Array(n*lados);
  const P = puntos.map(p => new THREE.Vector3(p[0], p[1], p[2]));
  // Marcos por transporte paralelo: el tubo no se retuerce.
  let tangente = new THREE.Vector3().subVectors(P[1], P[0]).normalize();
  let normal = new THREE.Vector3(0, 0, 1).cross(tangente);
  if (normal.lengthSq() < 1e-8) normal = new THREE.Vector3(0, 1, 0).cross(tangente);
  normal.normalize();
  let avance = 0;
  const binormal = new THREE.Vector3(), t2 = new THREE.Vector3(), eje = new THREE.Vector3(), v = new THREE.Vector3();
  for (let i = 0; i < n; i++) {
    if (i > 0) avance += P[i].distanceTo(P[i-1]);
    t2.subVectors(P[Math.min(i+1, n-1)], P[Math.max(i-1, 0)]);
    if (t2.lengthSq() > 1e-16) {
      t2.normalize();
      eje.crossVectors(tangente, t2);
      if (eje.lengthSq() > 1e-12) { eje.normalize(); normal.applyAxisAngle(eje, Math.acos(THREE.MathUtils.clamp(tangente.dot(t2), -1, 1))); }
      tangente.copy(t2);
    }
    binormal.crossVectors(tangente, normal).normalize();
    for (let k = 0; k < lados; k++) {
      const ang = 2*Math.PI*k/lados, j = i*lados + k;
      v.copy(normal).multiplyScalar(Math.cos(ang)).addScaledVector(binormal, Math.sin(ang));
      nor.set([v.x, v.y, v.z], 3*j);
      pos.set([P[i].x + radio*v.x, P[i].y + radio*v.y, P[i].z + radio*v.z], 3*j);
      tie[j] = tiempos ? tiempos[i] : -1e9;
      ava[j] = avance;
    }
  }
  const indices = [];
  for (let i = 0; i < n - 1 + (cerrar ? 1 : 0); i++) {
    const i2 = (i + 1) % n;
    for (let k = 0; k < lados; k++) {
      const a = i*lados + k, b = i*lados + (k+1)%lados, c2 = i2*lados + k, d = i2*lados + (k+1)%lados;
      indices.push(a, c2, b, b, c2, d);
    }
  }
  geometria.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geometria.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  geometria.setAttribute('aTiempo', new THREE.BufferAttribute(tie, 1));
  geometria.setAttribute('aAvance', new THREE.BufferAttribute(ava, 1));
  geometria.setIndex(n*lados > 65535 ? new THREE.Uint32BufferAttribute(indices, 1) : new THREE.Uint16BufferAttribute(indices, 1));
  const material = new THREE.ShaderMaterial({
    ...sombreadorTubo, transparent: true, depthWrite: false,
    uniforms: { uColor: { value: new THREE.Color(c) }, uTiempo: { value: 1e9 }, uVentana: { value: ventana },
      uBase: { value: base }, uFuturo: { value: futuro }, uOpacidad: { value: opacidad }, uDash: { value: dash },
      uBrillo: { value: brillo*intensidadBrillo } },
  });
  const malla = new THREE.Mesh(geometria, material);
  malla.renderOrder = 5;
  return malla;
}
export function liberar(objeto) {
  objeto?.traverse?.(o => { o.geometry?.dispose(); if (o.material && !o.material.userData?.compartido) o.material.dispose?.(); });
  objeto?.parent?.remove(objeto);
}

// ------------------------------------------------------------ flechas con brillo
export function crearFlecha(c, { radio = .012, punta = .07, emisivo = 1.4 } = {}) {
  const material = new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: emisivo*intensidadBrillo, roughness: .35, metalness: .1 });
  const grupo = new THREE.Group();
  const tallo = new THREE.Mesh(new THREE.CylinderGeometry(radio, radio, 1, 14), material);
  const cono = new THREE.Mesh(new THREE.ConeGeometry(radio*2.8, punta, 22), material);
  grupo.add(tallo, cono);
  const y = new THREE.Vector3(0, 1, 0), d = new THREE.Vector3();
  grupo.userData.material = material;
  grupo.apuntar = (vector, longitud = null) => {
    d.set(vector[0] ?? vector.x, vector[1] ?? vector.y, vector[2] ?? vector.z);
    const L = longitud ?? d.length();
    if (L < 1e-9) { grupo.visible = false; return; }
    grupo.visible = true;
    grupo.quaternion.setFromUnitVectors(y, d.normalize());
    const lt = Math.max(L - punta, 1e-3);
    tallo.scale.set(1, lt, 1); tallo.position.set(0, lt/2, 0);
    cono.position.set(0, lt + punta/2, 0);
  };
  return grupo;
}

// ------------------------------------------------------------ etiquetas HTML ancladas a un punto 3D
export function crearEtiqueta(html, clase = '') {
  const div = document.createElement('div');
  div.className = `etiqueta ${clase}`;
  div.innerHTML = html;
  const objeto = new CSS2DObject(div);
  objeto.center.set(.5, .5);
  return objeto;
}

// ------------------------------------------------------------ superficies a partir de las mallas de Python
// X, Y, Z: rejillas (n+1) x (m+1) de Ellipsoid(); las normales son las del elipsoide x²/a² + y²/b² + z²/c² = 1.
export function geometriaElipsoide(X, Y, Z) {
  const nu = X.length, nv = X[0].length;
  const a = maximoAbs(X), b = maximoAbs(Y), c = maximoAbs(Z);
  const pos = [], nor = [], ind = [];
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) {
    pos.push(X[i][j], Y[i][j], Z[i][j]);
    const n = new THREE.Vector3(X[i][j]/(a*a), Y[i][j]/(b*b), Z[i][j]/(c*c)).normalize();
    nor.push(n.x, n.y, n.z);
  }
  for (let i = 0; i < nu - 1; i++) for (let j = 0; j < nv - 1; j++) {
    const p = i*nv + j, q = (i+1)*nv + j;
    ind.push(p, q, p+1, p+1, q, q+1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setIndex(ind);
  g.userData.semiejes = [a, b, c];
  return g;
}
export function rejillaElipsoide(X, Y, Z, cada = 8, c = '#ffffff', opacidad = .12) {
  const nu = X.length, nv = X[0].length, pos = [];
  for (let i = 0; i < nu; i += cada) for (let j = 0; j < nv - 1; j++)
    pos.push(X[i][j], Y[i][j], Z[i][j], X[i][j+1], Y[i][j+1], Z[i][j+1]);
  for (let j = cada/2; j < nv; j += cada/2) for (let i = 0; i < nu - 1; i++)
    pos.push(X[i][j], Y[i][j], Z[i][j], X[i+1][j], Y[i+1][j], Z[i+1][j]);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: opacidad, depthWrite: false }));
}
function maximoAbs(M) { let m = 0; for (const fila of M) for (const v of fila) m = Math.max(m, Math.abs(v)); return m; }

// Superficie translúcida con borde iluminado (efecto Fresnel).
export function materialFresnel(c, { opacidad = .35, potencia = 2.2, nucleo = .05 } = {}) {
  return new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uColor: { value: new THREE.Color(c) }, uOpacidad: { value: opacidad }, uPotencia: { value: potencia }, uNucleo: { value: nucleo } },
    vertexShader: `varying vec3 vN; varying vec3 vV;
      void main(){ vec4 p = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-p.xyz); gl_Position = projectionMatrix*p; }`,
    fragmentShader: `uniform vec3 uColor; uniform float uOpacidad; uniform float uPotencia; uniform float uNucleo; varying vec3 vN; varying vec3 vV;
      void main(){ float f = pow(1. - abs(dot(normalize(vN), normalize(vV))), uPotencia); gl_FragColor = vec4(uColor*(.6 + 1.1*f), (uNucleo + f)*uOpacidad); }`,
  });
}

// ------------------------------------------------------------ halo (sprite con degradado radial)
let texturaHalo = null;
export function crearHalo(c, escala = .2, opacidad = .9) {
  if (!texturaHalo) {
    const lienzo = document.createElement('canvas'); lienzo.width = lienzo.height = 128;
    const g = lienzo.getContext('2d'), d = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    d.addColorStop(0, 'rgba(255,255,255,1)'); d.addColorStop(.18, 'rgba(255,255,255,.75)');
    d.addColorStop(.45, 'rgba(255,255,255,.18)'); d.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = d; g.fillRect(0, 0, 128, 128);
    texturaHalo = new THREE.CanvasTexture(lienzo);
  }
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texturaHalo, color: c, transparent: true, opacity: opacidad*intensidadBrillo,
    depthWrite: false, blending: THREE.AdditiveBlending }));
  sprite.scale.setScalar(escala);
  sprite.renderOrder = 10;
  return sprite;
}

// ------------------------------------------------------------ rotaciones: matriz de Python -> cuaternión
export function cuaternionesDesdeMatrices(rotaciones) {
  const m = new THREE.Matrix4();
  return rotaciones.map(R => {
    m.set(R[0][0], R[0][1], R[0][2], 0, R[1][0], R[1][1], R[1][2], 0, R[2][0], R[2][1], R[2][2], 0, 0, 0, 0, 1);
    return new THREE.Quaternion().setFromRotationMatrix(m);
  });
}
// Interpolación solo visual entre dos muestras calculadas (como en page_stability.py).
export function interpolarCuaternion(lista, indice, fraccion, destino) {
  const a = lista[indice], b = lista[Math.min(indice + 1, lista.length - 1)];
  return destino.slerpQuaternions(a, b, fraccion);
}
export function interpolarPunto(lista, indice, fraccion, destino) {
  const a = lista[indice], b = lista[Math.min(indice + 1, lista.length - 1)];
  return destino.set(a[0] + (b[0]-a[0])*fraccion, a[1] + (b[1]-a[1])*fraccion, a[2] + (b[2]-a[2])*fraccion);
}
