"""Interfaz web del eje intermedio (versión web de gui.py).

Igual que gui.py, recibe nombres, datos y acciones del programa principal y no
importa ni el motor ni la física. La diferencia es dónde se dibuja:
  - Python sirve la página (carpeta gui_web/) en http://localhost y responde a sus peticiones.
  - El navegador dibuja y anima con la GPU (Three.js y Plotly); no calcula nada.

Peticiones del navegador:
  GET  /api/inicio     controles, escenarios y el último resultado calculado
  POST /api/calcular   parámetros de los controles -> al_calcular -> datos de la trayectoria
  POST /api/pagina     número de página -> al_preparar_pagina -> datos de esa página
  POST /api/cerrar     la ventana se ha cerrado: termina el programa
"""
import json
import os
import re
import shutil
import subprocess
import threading
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from numpy import floating, generic, isfinite, iscomplexobj, linspace, ndarray, complexfloating

carpeta_web = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui_web")
tipos_contenido = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                   ".css": "text/css; charset=utf-8", ".woff2": "font/woff2", ".json": "application/json",
                   ".txt": "text/plain; charset=utf-8", ".md": "text/plain; charset=utf-8", ".svg": "image/svg+xml"}
max_puntos_envio = 2000

# Controles: los mismos rangos y valores iniciales que gui.py.
nombres_ejes = {"Minor  I₁": 0, "Intermediate  I₂": 1, "Major  I₃": 2}
controles = dict(
    I1=dict(etiqueta="I₁", minimo=.2, maximo=5., inicial=1., paso=.01, unidad="kg·m²"),
    I2=dict(etiqueta="I₂", minimo=.2, maximo=5., inicial=2., paso=.01, unidad="kg·m²"),
    I3=dict(etiqueta="I₃", minimo=.2, maximo=5., inicial=3., paso=.01, unidad="kg·m²"),
    Omega=dict(etiqueta="Ω", minimo=.1, maximo=3., inicial=1., paso=.01, unidad="rad/s"),
    eps=dict(etiqueta="ε", minimo=0., maximo=1., inicial=.001, unidad=""),
    # Δt mínimo 10⁻³ s (la v1 admite 10⁻⁶): más fino, el cálculo tarda demasiado para una demostración.
    dt=dict(etiqueta="Δt", minimo=1e-3, maximo=2., inicial=.02, unidad="s"),
    tf=dict(etiqueta="t_f", minimo=1., maximo=150., inicial=80., paso=1., unidad="s"),
    tol=dict(etiqueta="Tolerance", minimo=1e-12, maximo=.01, inicial=1e-6, unidad=""),
    tf_estudio=dict(etiqueta="Study interval", minimo=5., maximo=40., inicial=20., paso=1., unidad="s"),
)
# Escenarios para la demostración: solo fijan valores de los controles.
escenarios = [
    dict(nombre="Dzhanibekov nut", descripcion="Intermediate axis · T-handle", cuerpo="tuerca",
         valores=dict(I1=1., I2=2., I3=3., Omega=2., eps=.001, dt=.01, tf=80., metodo="RK4", adaptativo=False, eje=1)),
    dict(nombre="Tennis racket", descripcion="Intermediate axis · racket", cuerpo="raqueta",
         valores=dict(I1=.4, I2=2.2, I3=2.5, Omega=1.5, eps=.002, dt=.01, tf=80., metodo="RK4", adaptativo=False, eje=1)),
    dict(nombre="Stable minor axis", descripcion="Centre · no flips", cuerpo="satelite",
         valores=dict(I1=1., I2=2., I3=3., Omega=1., eps=.05, dt=.02, tf=80., metodo="RK4", adaptativo=False, eje=0)),
    dict(nombre="Stable major axis", descripcion="Centre · no flips", cuerpo="satelite",
         valores=dict(I1=1., I2=2., I3=3., Omega=1., eps=.05, dt=.02, tf=80., metodo="RK4", adaptativo=False, eje=2)),
    dict(nombre="Euler drifts away", descripcion="Explicit Euler · Δt = 0.05", cuerpo="caja",
         valores=dict(I1=1., I2=2., I3=3., Omega=1., eps=.001, dt=.05, tf=80., metodo="Euler", adaptativo=False, eje=1)),
    dict(nombre="Near the separatrix", descripcion="ε = 10⁻⁷ · long wait between flips", cuerpo="caja",
         valores=dict(I1=1., I2=2., I3=3., Omega=1., eps=1e-7, dt=.02, tf=150., metodo="RK4", adaptativo=False, eje=1)),
]
duracion_reproduccion = 20
# Avisos del principal y del motor (en español en la v1) traducidos al idioma de la GUI web.
traducciones = [
    (r"Se requiere I₁ < I₂ < I₃ · se conserva el último resultado válido", "Requires I₁ < I₂ < I₃ · last valid result kept"),
    (r"La solución diverge al empezar\. Aumenta la precisión del paso\.", "The solution diverges from the first steps. Reduce Δt."),
    (r"Límite de ([\d,]+) pasos: t = (\S+) s \(Δt = (\S+)\)", r"\1-step limit: integrated up to t = \2 s (Δt = \3)"),
    (r"Limite de pasos en t = (\S+)", r"Step limit reached at t = \1 s"),
    (r"Integracion detenida en t = (\S+)", r"Integration stopped at t = \1 s"),
    (r"Divergencia cerca de t = (\S+) s", r"Diverges near t = \1 s"),
    (r"I1 \+ I2 < I3: inercias no fisicas", "I₁ + I₂ < I₃: not a physical body"),
    (r"Residuo no finito", "Newton: non-finite residual"),
    (r"Jacobiana singular", "Newton: singular Jacobian"),
    (r"Limite de iteraciones de Newton", "Newton: iteration limit reached"),
]
puerto_inicial = int(os.environ.get("ORBITA_PUERTO", 8765))


class Servidor(ThreadingHTTPServer):
    # En Windows, reutilizar la dirección deja que dos programas escuchen en el mismo puerto y se
    # repartan las peticiones. Sin reutilizarla, un segundo programa abierto usa otro puerto libre.
    allow_reuse_address = False
    daemon_threads = True


def crear_interfaz_web(nombres_metodos, al_calcular, al_preparar_pagina, puerto=puerto_inicial):
    """Crea el servidor de la página; el programa principal proporciona las acciones."""
    estado = dict(resultado=None, parametros_aplicados=None, aviso_inicio=None)
    bloqueo = threading.Lock()                    # un cálculo cada vez, como en la v1
    configuracion = dict(nombres_metodos=list(nombres_metodos), nombres_ejes=nombres_ejes,
                         controles=controles, escenarios=escenarios, duracion_reproduccion=duracion_reproduccion)

    def parametros_iniciales():
        c = {nombre: control['inicial'] for nombre, control in controles.items()}
        return dict(I=(c['I1'], c['I2'], c['I3']), Omega=c['Omega'], dt=c['dt'], eps=c['eps'], tf=c['tf'],
                    tol=c['tol'], nombre_metodo=list(nombres_metodos)[-1], adaptativo=False, eje=1)

    # 1. ACCIONES: las mismas que en gui.py, ahora llamadas desde el navegador.
    def solicitar_calculo(parametros=None):
        parametros = parametros or parametros_iniciales()
        with bloqueo:
            try:
                resultado = al_calcular(parametros)
            except (ArithmeticError, ValueError, RuntimeError) as exc:
                return dict(error=f"Could not compute the trajectory: {traducir(exc)}")
            estado.update(resultado=resultado, parametros_aplicados=dict(parametros))
        return preparar_envio(resultado)

    def solicitar_pagina(numero_pagina, tf_estudio):
        with bloqueo:
            try:
                datos = al_preparar_pagina(numero_pagina, tf_estudio)
            except (ArithmeticError, ValueError, RuntimeError) as exc:
                return dict(error=f"Could not compute this view: {traducir(exc)}")
        return preparar_envio_pagina(datos)

    # 2. PETICIONES: cada ruta llama a una acción y devuelve JSON.
    class Peticiones(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def responder(self, contenido, tipo, codigo=200):
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(contenido)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(contenido)

        def responder_json(self, datos):
            self.responder(json.dumps(a_json(datos), allow_nan=False, separators=(",", ":")).encode(),
                           "application/json")

        def do_GET(self):
            ruta = self.path.split("?")[0]
            if ruta == "/api/inicio":
                estado['ultima_conexion'] = True
                resultado = estado['resultado']
                self.responder_json(dict(configuracion=configuracion,
                                         parametros=parametros_web(estado['parametros_aplicados']),
                                         resultado=preparar_envio(resultado) if resultado else None))
                return
            ruta = "/index_web.html" if ruta == "/" else ruta
            fichero = os.path.normpath(os.path.join(carpeta_web, ruta.lstrip("/")))
            if not fichero.startswith(carpeta_web) or not os.path.isfile(fichero):
                self.responder(b"No encontrado", "text/plain", 404)
                return
            with open(fichero, "rb") as f:
                self.responder(f.read(), tipos_contenido.get(os.path.splitext(fichero)[1], "application/octet-stream"))

        def do_POST(self):
            longitud = int(self.headers.get("Content-Length", 0))
            peticion = json.loads(self.rfile.read(longitud) or b"{}")
            if self.path == "/api/calcular":
                self.responder_json(solicitar_calculo(parametros_python(peticion)))
            elif self.path == "/api/pagina":
                self.responder_json(solicitar_pagina(int(peticion['numero']), float(peticion['tf_estudio'])))
            elif self.path == "/api/cerrar":
                self.responder_json(dict(ok=True))
                # Recargar la página vuelve a conectar antes de que venza la espera.
                estado['ultima_conexion'] = False
                threading.Timer(4., lambda: None if estado['ultima_conexion'] else servidor.shutdown()).start()
            else:
                self.responder(b"No encontrado", "text/plain", 404)

    def parametros_python(peticion):
        """Del formulario del navegador al diccionario que espera calcular_simulacion."""
        return dict(I=tuple(float(v) for v in peticion['I']), Omega=float(peticion['Omega']),
                    dt=float(peticion['dt']), eps=float(peticion['eps']), tf=float(peticion['tf']),
                    tol=float(peticion['tol']), nombre_metodo=str(peticion['nombre_metodo']),
                    adaptativo=bool(peticion['adaptativo']), eje=int(peticion['eje']))

    def parametros_web(parametros):
        return dict(parametros, I=list(parametros['I'])) if parametros else None

    servidor = None

    # 3. BUCLE DE EVENTOS: abrir la ventana y atender peticiones (equivale a plt.show()).
    def servir(abrir_ventana=True):
        nonlocal servidor
        try:
            servidor = Servidor(("127.0.0.1", puerto), Peticiones)
        except OSError:
            servidor = Servidor(("127.0.0.1", 0), Peticiones)          # puerto ocupado: otro libre
        direccion = f"http://127.0.0.1:{servidor.server_address[1]}/"
        print(f"ORBITA web en {direccion}  -  Ctrl+C o cerrar la ventana para terminar", flush=True)
        if abrir_ventana:
            abrir_navegador(direccion)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()

    def servir_en_segundo_plano():
        """Para comprobaciones automáticas: arranca el servidor sin abrir ventana."""
        hilo = threading.Thread(target=servir, kwargs=dict(abrir_ventana=False), daemon=True)
        hilo.start()
        return hilo

    # 4. Devolver al principal las acciones, como crear_interfaz.
    estado.update(solicitar_calculo=solicitar_calculo, solicitar_pagina=solicitar_pagina, servir=servir,
                  servir_en_segundo_plano=servir_en_segundo_plano, configuracion=configuracion,
                  detener=lambda: servidor and servidor.shutdown())
    return estado


def abrir_navegador(direccion):
    """Ventana de aplicación (sin pestañas ni barra) si hay Chrome o Edge; si no, el navegador por defecto."""
    candidatos = [shutil.which("chrome"), shutil.which("msedge"),
                  os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                  os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                  os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                  os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                  os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")]
    for ejecutable in candidatos:
        if ejecutable and os.path.isfile(ejecutable):
            subprocess.Popen([ejecutable, f"--app={direccion}", "--start-maximized"])
            return
    webbrowser.open(direccion)


# ------------------------------------------------------------ datos -> JSON
def preparar_envio(datos):
    """Quita lo que el navegador no dibuja (la solución completa puede tener 10⁵ pasos)."""
    datos = dict(datos)
    tn, _ = datos.pop('solucion_completa')
    datos['pasos'] = len(tn) - 1
    for clave in ('puntas_estela', 'comparacion_metodos', 'apoyo_comparacion', 'estabilidad', 'estudio_error',
                  'fantasmas', 'volteos_metodos'):
        datos.pop(clave, None)
    datos['avisos'] = [traducir(aviso) for aviso in datos['avisos']]
    datos['aviso'] = traducir(datos['aviso'])
    return datos


def preparar_envio_pagina(datos):
    """Reduce las series largas a lo que se ve, como hacen las páginas de la v1 al dibujar."""
    datos = dict(datos)
    if 'comparacion_metodos' in datos:
        comparacion = {}
        for nombre, r in datos['comparacion_metodos'].items():
            indices = muestras(len(r['t']))
            t = r['t']
            # Paso usado en cada muestra: el que llega a ese instante (la primera muestra no tiene).
            comparacion[nombre] = dict(t=t[indices], derivas=[d[indices] for d in r['derivas']],
                                       paso=(t[1:] - t[:-1])[indices[1:] - 1] if len(t) > 1 else t[:0],
                                       maximos=[float(d.max()) for d in r['derivas']], pasos=len(t) - 1,
                                       aviso=traducir(r['aviso']))
        datos['comparacion_metodos'] = comparacion
    if 'apoyo_comparacion' in datos:
        apoyo = {k: v for k, v in datos['apoyo_comparacion'].items() if k != 'referencia_completa'}
        apoyo['referencia_aviso'] = traducir(apoyo['referencia_aviso'])
        apoyo['curvas'] = {nombre: dict(c, aviso=traducir(c['aviso'])) for nombre, c in apoyo['curvas'].items()}
        datos['apoyo_comparacion'] = apoyo
    if 'estabilidad' in datos:
        # Las mallas X, Y de meshgrid se repiten fila a fila: basta con sus ejes (de 30 MB a ~3 MB).
        estabilidad = dict(datos['estabilidad'])
        malla = lambda X, Y, A: dict(x=X[0], y=Y[:, 0], z=A)
        for clave in ('regiones_completas', 'regiones_ampliadas'):
            estabilidad[clave] = {nombre: malla(*r) for nombre, r in estabilidad[clave].items()}
        estabilidad['color_ampliacion'] = malla(*estabilidad['color_ampliacion'])
        datos['estabilidad'] = estabilidad
    return datos


def traducir(texto):
    texto = str(texto)
    for patron, ingles in traducciones:
        texto = re.sub(patron, ingles, texto)
    return texto


def muestras(n):
    return linspace(0, n - 1, min(n, max_puntos_envio)).astype(int)


def a_json(valor):
    """numpy -> tipos de JSON; complejos como {re, im}; NaN e infinito como null."""
    if isinstance(valor, dict):
        return {str(k): a_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [a_json(v) for v in valor]
    if isinstance(valor, ndarray):
        if iscomplexobj(valor):
            return dict(re=a_json(valor.real), im=a_json(valor.imag))
        if valor.dtype.kind == "f":
            objeto = valor.astype(object)
            objeto[~isfinite(valor)] = None
            return objeto.tolist()
        return valor.tolist()
    if isinstance(valor, (complex, complexfloating)):
        return dict(re=a_json(valor.real), im=a_json(valor.imag))
    if isinstance(valor, (float, floating)):
        return float(valor) if isfinite(valor) else None
    if isinstance(valor, generic):
        return valor.item()
    return valor
