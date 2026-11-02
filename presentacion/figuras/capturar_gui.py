"""Capturas reales de la GUI para la presentacion, sin abrir ventana (backend Agg).

Ejecutar desde la raiz del repositorio:  python presentacion/figuras/capturar_gui.py
Usa solo la API que devuelve crear_interfaz(); no modifica nada de active/ ni de PEI1/.
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"
raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, raiz)

from PEI1.PEI1 import iniciar_programa

salida = os.path.join(os.path.dirname(__file__), "gui")
os.makedirs(salida, exist_ok=True)

# Cada caso: nombre, eje (0 menor, 1 intermedio, 2 mayor), metodo, paginas a capturar, instante relativo
casos = [
    ("eje1_menor_RK4", 0, 2, (0, 2), 0.6),
    ("eje2_intermedio_RK4", 1, 2, (0, 1, 2, 3), 0.45),
    ("eje3_mayor_RK4", 2, 2, (0, 2), 0.6),
    ("eje2_intermedio_Euler", 1, 0, (0, 1, 2), 0.45),
]

interfaz = iniciar_programa(animar=False)
figura = interfaz["figura"]
for nombre, eje, metodo, paginas, instante in casos:
    interfaz["selector_eje"].set_active(eje)
    interfaz["selector_metodo"].set_active(metodo)
    interfaz["solicitar_calculo"]()
    for pagina in paginas:
        interfaz["mostrar_pagina"](pagina)
        interfaz["mostrar_instante"](instante * interfaz["t"][-1])
        figura.savefig(os.path.join(salida, f"{nombre}_p{pagina + 1}.png"), dpi=100)
        print(nombre, pagina + 1, interfaz["texto_aviso"].get_text())
