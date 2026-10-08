"""Genera ortomosaicos SINTÉTICOS de una huerta (mango + otros árboles) con verdad terreno.

Sirve sólo para probar el flujo completo (tareas 1-3) sin imágenes reales.
Los resultados con datos sintéticos NO son evidencia de desempeño en campo.

    python generar_demo.py --salida datos_demo
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage as ndi

GSD = 0.10  # m/píxel (vuelo típico a ~70-100 m con cámara RGB de 20 MP)

ESPECIES = {
    # diámetro de copa (m), color RGB medio, rugosidad de textura, escala del grano de hoja (m)
    "mango": dict(diam=(3.5, 8.0), color=(45, 82, 38), textura=13, grano=0.25),
    "otro": dict(diam=(2.8, 5.5), color=(78, 112, 48), textura=8, grano=0.5),
}


def ruido_suave(shape, escala_px, rng):
    return ndi.gaussian_filter(rng.standard_normal(shape), max(escala_px, 0.5))


def generar(alto_m, ancho_m, bloques, rng):
    h, w = int(alto_m / GSD), int(ancho_m / GSD)
    # Suelo: marrón con manchas de pasto/maleza
    img = np.empty((h, w, 3), np.float32)
    img[:] = (150, 122, 92)
    img += ruido_suave((h, w), 30, rng)[..., None] * 60
    pasto = ruido_suave((h, w), 25, rng) > 0.25
    img[pasto] = img[pasto] * 0.6 + np.array([110, 120, 70]) * 0.4
    img += rng.normal(0, 6, img.shape)

    yy, xx = np.mgrid[0:h, 0:w]
    arboles = []
    for (f0, f1, c0, c1, especie, espaciado, prob_falta) in bloques:
        for y in np.arange(f0 + espaciado / 2, f1, espaciado):
            for x in np.arange(c0 + espaciado / 2, c1, espaciado):
                if rng.random() < prob_falta:
                    continue
                esp = especie if especie != "mixto" else rng.choice(["mango", "otro"], p=[0.5, 0.5])
                d = rng.uniform(*ESPECIES[esp]["diam"])
                arboles.append((y + rng.normal(0, 0.4), x + rng.normal(0, 0.4), esp, d))

    for (y_m, x_m, esp, d) in arboles:
        p = ESPECIES[esp]
        cy, cx, r = y_m / GSD, x_m / GSD, d / 2 / GSD
        y0, y1 = int(max(0, cy - r * 1.6)), int(min(h, cy + r * 1.6))
        x0, x1 = int(max(0, cx - r * 1.6)), int(min(w, cx + r * 1.6))
        if y1 <= y0 or x1 <= x0:
            continue
        sy, sx = yy[y0:y1, x0:x1], xx[y0:y1, x0:x1]
        ang = np.arctan2(sy - cy, sx - cx)
        borde = r * (1 + 0.08 * np.sin(5 * ang + rng.uniform(0, 6)) + 0.05 * np.sin(9 * ang + rng.uniform(0, 6)))
        dist = np.hypot(sy - cy, sx - cx)
        # Sombra proyectada (sol desde el noroeste)
        sh = np.hypot(sy - cy - 0.25 * r, sx - cx - 0.25 * r) < borde
        img[y0:y1, x0:x1][sh] *= 0.55
        copa = dist < borde
        hoja = ruido_suave(copa.shape, p["grano"] / GSD, rng)
        hoja = hoja / (hoja.std() + 1e-6)
        luz = 1.15 - 0.35 * (dist / np.maximum(borde, 1)) - 0.12 * ((sy - cy) + (sx - cx)) / (2 * r)
        tono = np.array(p["color"], np.float32) * rng.normal(1, 0.08) + rng.normal(0, 4, 3)  # variabilidad entre árboles
        col = tono * luz[..., None] + hoja[..., None] * p["textura"]
        img[y0:y1, x0:x1][copa] = col[copa]

    img = np.clip(img, 0, 255).astype(np.uint8)
    verdad = pd.DataFrame([{"fila": y / GSD, "col": x / GSD, "clase": e, "diametro_m": d}
                           for (y, x, e, d) in arboles
                           if 0 <= y / GSD < h and 0 <= x / GSD < w])
    return img, verdad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default="datos_demo")
    ap.add_argument("--semilla", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.semilla)
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)

    escenas = {
        # sector de entrenamiento: bloque de mango, bloque de otra especie y bloque mixto
        "sector_entrenamiento": (150, 150, [(0, 75, 0, 75, "mango", 10, 0.05),
                                            (0, 75, 75, 150, "otro", 6, 0.10),
                                            (75, 150, 0, 150, "mixto", 9, 0.10)]),
        # sector nuevo (tarea 3): distinta distribución y densidad
        "sector_nuevo": (120, 180, [(0, 120, 0, 110, "mango", 9, 0.12),
                                    (0, 60, 110, 180, "otro", 6, 0.15),
                                    (60, 120, 110, 180, "mixto", 8, 0.10)]),
    }
    for nombre, (alto, ancho, bloques) in escenas.items():
        img, verdad = generar(alto, ancho, bloques, rng)
        Image.fromarray(img).save(out / f"{nombre}.png")
        verdad.to_csv(out / f"{nombre}_verdad.csv", index=False)
        with open(out / f"{nombre}.json", "w") as fh:
            json.dump({"gsd_m": GSD, "sintetico": True}, fh)
        print(f"{nombre}: {img.shape[1]}x{img.shape[0]} px, GSD {GSD} m, "
              f"{(verdad.clase == 'mango').sum()} mangos, {(verdad.clase == 'otro').sum()} otros")


if __name__ == "__main__":
    main()
