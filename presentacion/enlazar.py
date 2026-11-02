"""Navegacion interna del deck: accion de clic sobre la forma entera (sin texto subrayado).

  slide 18 (mapa de fases): cada nodo salta a la slide que indica el spec (tercera celda de cada linea del bloque)
  slides 19-25: el antetitulo vuelve al mapa de fases

Ejecutar despues de construir y antes del lint:  python presentacion/enlazar.py presentacion/PEI1_final.pptx
"""
import os
import sys

from pptx import Presentation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inyectar_contenido import leer_spec

MAPA = 18
ruta = sys.argv[1]
spec = leer_spec(os.path.join(os.path.dirname(os.path.abspath(__file__)), "PEI1_final.deck.md"))
destinos = [int(l.split(" | ")[2]) for l in spec["s%d" % MAPA]["block"]]

prs = Presentation(ruta)
slides = list(prs.slides)
nodos = [sh for sh in slides[MAPA - 1].shapes if sh.name == "slides-field:Block"]
assert len(nodos) == len(destinos), (len(nodos), len(destinos))
for nodo, destino in zip(nodos, destinos):
    nodo.click_action.target_slide = slides[destino - 1]
vueltas = 0
for numero in range(MAPA + 1, 26):
    for sh in slides[numero - 1].shapes:
        if sh.name == "deco-eyebrow":
            sh.click_action.target_slide = slides[MAPA - 1]
            vueltas += 1
prs.save(ruta)
print(f"{len(nodos)} nodos del mapa enlazados, {vueltas} antetitulos vuelven a la slide {MAPA}")
