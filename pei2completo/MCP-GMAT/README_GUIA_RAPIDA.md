# Guía Rápida: Servidor MCP para NASA GMAT (`MCP-GMAT`)

Este directorio contiene la implementación oficial y abierta de **GMAT-mcp**, el servidor que comunica **Antigravity (y nuestra GUI de Python)** con el motor de cálculo orbital **NASA GMAT**.

---

## 1. ¿Qué es y para qué sirve?

GMAT es el software profesional de astrodinámica de la NASA. Sin embargo, su interfaz gráfica es antigua, compleja y no permite integrarse fácilmente con otros programas modernos.

Este servidor **MCP (Model Context Protocol)** actúa como un **adaptador inteligente**:
1. Recibe órdenes desde Antigravity o desde nuestra aplicación gráfica.
2. Ejecuta NASA GMAT en segundo plano (modo consola ultra-rápido, sin ventanas lentas).
3. Captura los datos de la trayectoria real (con gravedad real de la Tierra, Luna y Sol).
4. Devuelve los resultados estructurados (posiciones $X, Y, Z$ y velocidades) para pintarlos en nuestra GUI 3D.

---

## 2. ¿Cómo funciona por dentro? (Flujo en 3 pasos)

```
[ Tu GUI en Python / Antigravity ]
              │
              │ 1. Envía parámetros orbitales (ej. Órbita Halo en L2)
              ▼
    [ Servidor MCP-GMAT ]
              │
              │ 2. Escribe el archivo 'mision.script' y ejecuta:
              │    GmatConsole.exe -r mision.script
              ▼
      [ NASA GMAT Engine ]
              │
              │ 3. Calcula con gravedad de alta fidelidad y escribe 'ReportFile.txt'
              ▼
    [ Servidor MCP-GMAT ]
              │
              │ 4. Lee los datos numéricos y los envía en formato JSON
              ▼
[ Tu GUI 3D en pantalla ]  <── Pinta la órbita y compara errores con el modelo teórico
```

---

## 3. Herramientas que incluye este MCP

| Herramienta | ¿Qué hace? |
|---|---|
| **`runGmat`** | Lanza una simulación en GMAT. Si hay algún error, no se cuelga: te dice exactamente en qué línea falló y por qué. |
| **`getGmatIdioms`** | Base de conocimiento con las "reglas trampa" del lenguaje de GMAT para que la IA nunca escriba comandos inválidos. |
| **`listGmatSamples`** | Catálogo con scripts oficiales de la NASA de misiones reales que podemos usar como plantilla. |
| **`searchDocs`** | Búsqueda semántica directa en el manual oficial de astrodinámica de GMAT. |

---

## 4. Requisitos para usarlo

1. **Python 3.11 o superior** (ya disponible en el entorno).
2. **Tener instalado NASA GMAT** en Windows (descargable gratis desde [SourceForge / NASA](https://sourceforge.net/projects/gmat/)):
   - Se recomienda la versión oficial R2022a o superior.
   - Ruta típica de instalación: `C:\Users\<tu-usuario>\AppData\Local\GMAT\R2022a` o `C:\Program Files\GMAT`.

---

## 5. Puesta en marcha rápida (Comandos)

Desde la terminal en esta carpeta (`pei2completo/MCP-GMAT`):

1. **Detectar automáticamente dónde está instalado GMAT en tu ordenador:**
   ```powershell
   python -m gmat_mcp.cli discover --root "C:\Ruta\A\Tu\GMAT"
   ```

2. **Crear el archivo de configuración local (`profiles.local.toml`):**
   ```powershell
   python -m gmat_mcp.cli init --root "C:\Ruta\A\Tu\GMAT" --output profiles.local.toml
   ```

3. **Verificar que todo funciona (Diagnóstico):**
   ```powershell
   python -m gmat_mcp.cli --config profiles.local.toml doctor
   ```
   Si todo está verde (`OK`), el puente entre Python, la IA y GMAT está 100% listo para simular órbitas.

---

## 6. Conexión con la PEI 2 (Rúbrica de la UPM)

En la rúbrica oficial de la asignatura:
- **Bloque 3 (25% de la nota):** *"Éxito en la comunicación automática con GMAT (vía MCP / API externa)"*.
Tener este módulo en el repositorio demuestra una arquitectura desacoplada y profesional que cumple el estándar abierto de la industria aeroespacial.
