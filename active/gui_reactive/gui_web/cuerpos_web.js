// Modelos 3D de los cuerpos que se pueden ver girar (página de movimiento).
// Ejes del cuerpo: e1 = x, e2 = y, e3 = z, los mismos que usa Python.
// La caja tiene las proporciones exactas de I1, I2, I3 (Box_dimensions, en Python).
// Los demás cuerpos son ilustrativos: su forma reparte la masa como sugieren I1 < I2 < I3,
// pero la dinámica que se ve es siempre la de los deslizadores.
import { THREE, materialFresnel } from './escena_web.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const tiposCuerpo = {
  caja: { nombre: 'Box', nota: 'Exact proportions of I₁, I₂, I₃' },
  tuerca: { nombre: 'T-handle', nota: 'Illustrative · Dzhanibekov' },
  raqueta: { nombre: 'Racket', nota: 'Illustrative · tennis racket' },
  satelite: { nombre: 'Satellite', nota: 'Illustrative · panels along e₁' },
};

// ------------------------------------------------------------ texturas generadas
const texturas = {};
function lienzo(n, dibujar, enColor = false) {
  const c = document.createElement('canvas'); c.width = c.height = n;
  dibujar(c.getContext('2d'), n);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  if (enColor) t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function aleatorio(s) { return () => (s = (s * 16807) % 2147483647) / 2147483647; }

// Lámina aislante multicapa (MLI): arrugas que reflejan la luz de forma irregular.
function texturaMLI() {
  return texturas.mli ??= lienzo(512, (g, n) => {
    const r = aleatorio(11);
    g.fillStyle = '#808080'; g.fillRect(0, 0, n, n);
    for (let k = 0; k < 2600; k++) {
      const x = r()*n, y = r()*n, l = 8 + r()*46, a = r()*Math.PI, w = 2 + r()*10, v = 60 + r()*150;
      g.save(); g.translate(x, y); g.rotate(a);
      g.fillStyle = `rgba(${v},${v},${v},${.10 + r()*.22})`;
      g.beginPath(); g.moveTo(-l/2, 0); g.lineTo(0, -w/2); g.lineTo(l/2, 0); g.lineTo(0, w/2); g.closePath(); g.fill();
      g.restore();
    }
    g.filter = 'blur(1.2px)'; g.drawImage(g.canvas, 0, 0); g.filter = 'none';
  });
}
// Células solares: rejilla de celdas azules con conductores plateados.
function texturaPanel() {
  return texturas.panel ??= lienzo(512, (g, n) => {
    g.fillStyle = '#b9c2d6'; g.fillRect(0, 0, n, n);
    const filas = 6, columnas = 4, m = 5, cw = n/columnas, ch = n/filas;
    for (let i = 0; i < columnas; i++) for (let j = 0; j < filas; j++) {
      const d = g.createLinearGradient(i*cw, j*ch, (i+1)*cw, (j+1)*ch);
      d.addColorStop(0, '#13204a'); d.addColorStop(.55, '#0b1533'); d.addColorStop(1, '#1a2c63');
      g.fillStyle = d; g.fillRect(i*cw + m, j*ch + m, cw - 2*m, ch - 2*m);
      g.strokeStyle = 'rgba(170,190,230,.22)'; g.lineWidth = 1;
      for (let k = 1; k < 6; k++) { g.beginPath(); g.moveTo(i*cw + m, j*ch + k*ch/6); g.lineTo((i+1)*cw - m, j*ch + k*ch/6); g.stroke(); }
    }
  }, true);
}
// Empuñadura con cinta enrollada.
function texturaGrip() {
  return texturas.grip ??= lienzo(256, (g, n) => {
    g.fillStyle = '#d9d4c7'; g.fillRect(0, 0, n, n);
    g.strokeStyle = 'rgba(60,55,45,.55)'; g.lineWidth = 3;
    for (let k = -n; k < 2*n; k += 22) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k + n*.45, n); g.stroke(); }
  }, true);
}

// ------------------------------------------------------------ materiales
function materiales() {
  const mli = texturaMLI();
  return {
    oro: new THREE.MeshPhysicalMaterial({ color: '#d9a443', metalness: 1, roughness: .42, bumpMap: mli, bumpScale: 2.2,
      roughnessMap: mli, clearcoat: .25, clearcoatRoughness: .5, envMapIntensity: .85 }),
    plata: new THREE.MeshPhysicalMaterial({ color: '#d7dde8', metalness: 1, roughness: .22, envMapIntensity: 1.1 }),
    grafito: new THREE.MeshPhysicalMaterial({ color: '#2a3040', metalness: .55, roughness: .38, clearcoat: .6 }),
    blanco: new THREE.MeshPhysicalMaterial({ color: '#eef1f6', metalness: .05, roughness: .45, clearcoat: .3 }),
    panel: new THREE.MeshPhysicalMaterial({ map: texturaPanel(), metalness: .45, roughness: .22, clearcoat: 1,
      clearcoatRoughness: .08, envMapIntensity: 1.4 }),
    carbono: new THREE.MeshPhysicalMaterial({ color: '#171b26', metalness: .35, roughness: .3, clearcoat: 1, clearcoatRoughness: .1 }),
    acento: new THREE.MeshPhysicalMaterial({ color: '#8f7dff', metalness: .3, roughness: .3, clearcoat: 1,
      emissive: '#3a2a9a', emissiveIntensity: .35 }),
    grip: new THREE.MeshPhysicalMaterial({ map: texturaGrip(), roughness: .8, metalness: 0 }),
    cuerdas: new THREE.LineBasicMaterial({ color: '#efe6cf', transparent: true, opacity: .7 }),
    titanio: new THREE.MeshPhysicalMaterial({ color: '#aeb7c6', metalness: 1, roughness: .36, clearcoat: .2, envMapIntensity: .8 }),
  };
}

// ------------------------------------------------------------ cuerpos
export function crearCuerpo(tipo, dimensiones) {
  const m = materiales();
  const grupo = new THREE.Group();
  ({ caja: caja, tuerca: tuerca, raqueta: raqueta, satelite: satelite }[tipo] ?? caja)(grupo, m, dimensiones);
  grupo.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  normalizar(grupo, tipo === 'satelite' ? .72 : tipo === 'caja' ? .5 : .62);
  grupo.userData.tipo = tipo;
  return grupo;
}

function caja(grupo, m, [a, b, c]) {
  const mayor = Math.max(a, b, c);
  [a, b, c] = [a, b, c].map(s => Math.max(s/mayor, .04));      // placa plana: grosor mínimo, como en la v1
  const radio = Math.min(a, b, c) * .12;
  const malla = new THREE.Mesh(new RoundedBoxGeometry(a, b, c, 3, Math.min(radio, .03)), m.oro);
  const bordes = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(a*1.002, b*1.002, c*1.002)),
    new THREE.LineBasicMaterial({ color: '#ffe3a3', transparent: true, opacity: .25 }));
  grupo.add(malla, bordes);
}

function tuerca(grupo, m) {
  // Vástago a lo largo de e1 y travesaño a lo largo de e2: e3, normal al plano de la T, es el eje mayor.
  const vastago = new THREE.Mesh(new THREE.CapsuleGeometry(.055, .95, 8, 28), m.titanio);
  vastago.rotation.z = -Math.PI/2;
  vastago.position.x = -.05;
  const travesano = new THREE.Mesh(new THREE.CapsuleGeometry(.07, .62, 8, 28), m.grafito);
  travesano.position.x = .5;
  const union = new THREE.Mesh(new THREE.SphereGeometry(.1, 32, 20), m.titanio);
  union.position.x = .5;
  const anillo = new THREE.Mesh(new THREE.TorusGeometry(.064, .012, 12, 40), m.acento);
  anillo.rotation.y = Math.PI/2; anillo.position.x = -.42;
  const pieza = new THREE.Group();
  pieza.add(vastago, travesano, union, anillo);
  pieza.position.x = -.21;                                  // centro de masas aproximado en el origen
  grupo.add(pieza);
}

function raqueta(grupo, m) {
  // Mango a lo largo de e1 (I1, el menor) y cabeza en el plano e1–e2: e3, normal a las cuerdas, es el mayor.
  const pieza = new THREE.Group();
  const cabeza = new THREE.Mesh(new THREE.TorusGeometry(1, .07, 20, 96), m.carbono);
  cabeza.scale.set(.34, .26, .34);
  cabeza.position.x = .38;
  const franja = new THREE.Mesh(new THREE.TorusGeometry(1, .074, 8, 96, Math.PI*.5), m.acento);
  franja.scale.set(.34, .26, .34); franja.position.x = .38; franja.rotation.z = -Math.PI/4;
  const cuerdas = [];
  for (let k = -9; k <= 9; k++) {
    const y = k*.026, x = .34*Math.sqrt(Math.max(0, 1 - (y/.26)**2))*.96;
    cuerdas.push(.38 - x, y, 0, .38 + x, y, 0);
    const xx = k*.034, yy = .26*Math.sqrt(Math.max(0, 1 - (xx/.34)**2))*.96;
    cuerdas.push(.38 + xx, -yy, 0, .38 + xx, yy, 0);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(cuerdas, 3));
  const red = new THREE.LineSegments(g, m.cuerdas);
  const garganta = [1, -1].map(s => {
    const brazo = new THREE.Mesh(new THREE.CylinderGeometry(.018, .022, .3, 12), m.carbono);
    brazo.position.set(-.06, s*.06, 0); brazo.rotation.z = Math.PI/2 + s*.42;
    return brazo;
  });
  const mango = new THREE.Mesh(new THREE.CylinderGeometry(.036, .04, .42, 8), m.grip);
  mango.rotation.z = Math.PI/2; mango.position.x = -.37;
  const tapa = new THREE.Mesh(new THREE.CylinderGeometry(.046, .046, .02, 8), m.acento);
  tapa.rotation.z = Math.PI/2; tapa.position.x = -.59;
  pieza.add(cabeza, franja, red, ...garganta, mango, tapa);
  pieza.position.x = -.12;
  grupo.add(pieza);
}

function satelite(grupo, m) {
  // Paneles a lo largo de ±e1 (I1 el menor), antena en +e3.
  const bus = new THREE.Mesh(new RoundedBoxGeometry(.34, .3, .4, 3, .015), m.oro);
  grupo.add(bus);
  const tapa = new THREE.Mesh(new THREE.BoxGeometry(.3, .26, .012), m.blanco);
  tapa.position.z = .206; grupo.add(tapa);
  for (const s of [1, -1]) {
    const brazo = new THREE.Mesh(new THREE.CylinderGeometry(.008, .008, .16, 10), m.plata);
    brazo.rotation.z = Math.PI/2; brazo.position.x = s*.25; grupo.add(brazo);
    const yugo = new THREE.Mesh(new THREE.BoxGeometry(.02, .05, .02), m.grafito);
    yugo.position.x = s*.33; grupo.add(yugo);
    for (const k of [0, 1]) {
      const panel = new THREE.Mesh(new THREE.BoxGeometry(.4, .3, .01), [m.grafito, m.grafito, m.grafito, m.grafito, m.panel, m.panel]);
      panel.position.x = s*(.545 + k*.41);
      grupo.add(panel);
    }
  }
  const perfil = [];
  for (let k = 0; k <= 16; k++) { const r = .15*k/16; perfil.push(new THREE.Vector2(r, .06*(r/.15)**2)); }
  const plato = new THREE.Mesh(new THREE.LatheGeometry(perfil, 48), m.blanco);
  plato.rotation.x = Math.PI/2; plato.position.set(.02, 0, .25);
  plato.material = m.blanco.clone(); plato.material.side = THREE.DoubleSide;
  const mastil = new THREE.Mesh(new THREE.CylinderGeometry(.006, .006, .14, 8), m.plata);
  mastil.rotation.x = Math.PI/2; mastil.position.set(.02, 0, .3);
  const alimentador = new THREE.Mesh(new THREE.ConeGeometry(.018, .035, 16), m.grafito);
  alimentador.rotation.x = -Math.PI/2; alimentador.position.set(.02, 0, .37);
  const sensor = new THREE.Mesh(new THREE.CylinderGeometry(.03, .035, .07, 20), m.grafito);
  sensor.position.set(-.11, .09, .23); sensor.rotation.x = Math.PI/2;
  grupo.add(plato, mastil, alimentador, sensor);
  for (const [x, y] of [[.12, .1], [-.12, .1], [.12, -.1], [-.12, -.1]]) {
    const tobera = new THREE.Mesh(new THREE.ConeGeometry(.022, .04, 16, 1, true), m.plata);
    tobera.position.set(x, y, -.22); tobera.rotation.x = -Math.PI/2; grupo.add(tobera);
  }
}

function normalizar(grupo, semitamano) {
  const caja = new THREE.Box3().setFromObject(grupo);
  const mayor = Math.max(...caja.max.toArray().map(Math.abs), ...caja.min.toArray().map(Math.abs));
  grupo.scale.multiplyScalar(semitamano / mayor);
}

// Copia translúcida del cuerpo para comparar integradores.
export function crearFantasma(cuerpo, c) {
  const fantasma = cuerpo.clone(true);
  const material = materialFresnel(c, { opacidad: .9, potencia: 1.6, nucleo: .14 });
  const lineas = new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: .35 });
  fantasma.traverse(o => {
    if (o.isMesh) { o.material = material; o.castShadow = o.receiveShadow = false; o.renderOrder = 3; }
    else if (o.isLineSegments) o.material = lineas;
  });
  return fantasma;
}
