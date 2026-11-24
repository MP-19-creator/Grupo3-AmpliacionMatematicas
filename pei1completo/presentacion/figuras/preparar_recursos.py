"""Recursos de imagen del deck: tira de logos MUSE y recortes de las capturas reales de la GUI.

Ejecutar despues de capturar_gui.py, desde la raiz del repositorio:
    python presentacion/figuras/preparar_recursos.py
"""
import os

import fitz
from PIL import Image

aqui = os.path.dirname(os.path.abspath(__file__))
logos = r"C:\Users\igper\.claude\MUSE_plantilla_memoria\memoria\logos"
salida = os.path.join(aqui, "recursos")
os.makedirs(salida, exist_ok=True)

# ---------------------------------------------------------------- logos
pix = fitz.open(os.path.join(logos, "logo_idr.pdf"))[0].get_pixmap(dpi=300)
idr = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def recortar_blanco(img):
    gris = img.convert("L").point(lambda v: 255 if v < 245 else 0)
    caja = gris.getbbox()
    return img.crop(caja) if caja else img


alto = 160
fila = [recortar_blanco(Image.open(os.path.join(logos, n)).convert("RGB"))
        for n in ("logo_upm.jpg", "logo_etsiae.jpg")] + [recortar_blanco(idr)]
fila = [im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS) for im in fila]
hueco = 70
tira = Image.new("RGB", (sum(im.width for im in fila) + hueco * (len(fila) - 1), alto), "white")
x = 0
for im in fila:
    tira.paste(im, (x, 0))
    x += im.width + hueco
tira.save(os.path.join(salida, "logos_upm_etsiae_idr.png"))
muse = recortar_blanco(Image.open(os.path.join(logos, "logo_muse.png")).convert("RGBA"))
muse.save(os.path.join(salida, "logo_muse.png"))
print("logos:", tira.size, muse.size)

# ---------------------------------------------------------------- recortes de la GUI (capturas 1920 x 1120)
gui = os.path.join(aqui, "gui")
recortes = {
    "caja_eje2.png": ("eje2_intermedio_RK4_p1.png", (560, 330, 920, 640)),
    "poinsot_eje2.png": ("eje2_intermedio_RK4_p1.png", (985, 330, 1480, 740)),
    "omega_eje2.png": ("eje2_intermedio_RK4_p1.png", (500, 825, 1485, 1005)),
    "poinsot_eje1.png": ("eje1_menor_RK4_p1.png", (985, 330, 1480, 740)),
    "poinsot_eje3.png": ("eje3_mayor_RK4_p1.png", (985, 330, 1480, 740)),
    "omega_eje1.png": ("eje1_menor_RK4_p1.png", (500, 825, 1485, 1005)),
    "omega_eje3.png": ("eje3_mayor_RK4_p1.png", (500, 825, 1485, 1005)),
    "convergencia.png": ("eje2_intermedio_RK4_p4.png", (505, 240, 1130, 935)),
    "richardson.png": ("eje2_intermedio_RK4_p4.png", (1170, 240, 1890, 610)),
    "deriva_2T.png": ("eje2_intermedio_Euler_p2.png", (495, 215, 1175, 600)),
    "deriva_q.png": ("eje2_intermedio_Euler_p2.png", (495, 645, 990, 985)),
    "tabla_derivas.png": ("eje2_intermedio_Euler_p2.png", (1515, 675, 1890, 815)),
    "prediccion_estabilidad.png": ("eje2_intermedio_Euler_p3.png", (1470, 575, 1900, 855)),
    "estabilidad_gui.png": ("eje2_intermedio_Euler_p3.png", (490, 305, 1420, 925)),
}
for nombre, (origen, caja) in recortes.items():
    Image.open(os.path.join(gui, origen)).crop(caja).save(os.path.join(salida, nombre))

# GUI completa, pagina por pagina (para la slide de recorrido)
for i, origen in enumerate(("eje2_intermedio_RK4_p1.png", "eje2_intermedio_Euler_p2.png",
                            "eje2_intermedio_Euler_p3.png", "eje2_intermedio_RK4_p4.png"), 1):
    Image.open(os.path.join(gui, origen)).save(os.path.join(salida, f"gui_p{i}.png"))
print("recortes:", len(recortes))
