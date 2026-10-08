"""Descriptores por copa: forma, color, índices de vegetación y textura (GLCM, LBP).

Las copas de mango son grandes, redondeadas, de follaje denso verde oscuro y textura
fina y homogénea; estos descriptores permiten distinguirlas de otros frutales, malezas
o árboles nativos (Haralick et al. 1973; Ojala et al. 2002; Sarron et al. 2018).
"""
import numpy as np
import pandas as pd
from skimage import color, measure
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

from . import indices

NIVELES_GLCM = 32
LBP_P, LBP_R = 8, 1


def tabla_copas(orto, etiquetas):
    """Devuelve un DataFrame con una fila por copa (id, posición, forma, color, textura)."""
    rgb = orto.rgb
    hsv = color.rgb2hsv(rgb)
    lab = color.rgb2lab(rgb)
    idx = indices.todos(rgb, orto.nir)
    gris = color.rgb2gray(rgb)
    gris_q = (gris * (NIVELES_GLCM - 1)).astype(np.uint8) + 1  # nivel 0 reservado para "fuera de copa"
    lbp = local_binary_pattern((gris * 255).astype(np.uint8), LBP_P, LBP_R, method="uniform")

    filas = []
    for reg in measure.regionprops(etiquetas):
        m = reg.image
        sl = reg.slice
        sel = lambda a: a[sl][m]
        f = {"id": reg.label}
        cy, cx = reg.centroid
        f["fila"], f["col"] = cy, cx
        f["x"], f["y"] = (float(v) for v in orto.pixel_a_mundo(cy, cx))

        # Forma (en metros)
        area_m2 = reg.area * orto.gsd ** 2
        f["area_m2"] = area_m2
        f["diametro_m"] = 2 * np.sqrt(area_m2 / np.pi)
        f["perimetro_m"] = reg.perimeter * orto.gsd
        f["circularidad"] = 4 * np.pi * reg.area / max(reg.perimeter, 1) ** 2
        f["solidez"] = reg.solidity
        f["excentricidad"] = reg.eccentricity
        f["elongacion"] = reg.axis_major_length / max(reg.axis_minor_length, 1e-6)

        # Color
        for i, c in enumerate("RGB"):
            v = sel(rgb[..., i]).astype(np.float32)
            f[f"{c}_media"], f[f"{c}_std"] = v.mean(), v.std()
        for i, c in enumerate(("H", "S", "V")):
            v = sel(hsv[..., i])
            f[f"{c}_media"], f[f"{c}_std"] = v.mean(), v.std()
        for i, c in enumerate(("L", "a", "b")):
            f[f"{c}_lab_media"] = sel(lab[..., i]).mean()

        # Índices de vegetación
        for nombre, arr in idx.items():
            v = sel(arr)
            f[f"{nombre}_media"], f[f"{nombre}_std"] = v.mean(), v.std()
            f[f"{nombre}_p90"] = np.percentile(v, 90)

        # Textura GLCM (Haralick) sólo sobre píxeles de la copa
        parche = np.where(m, gris_q[sl], 0)
        glcm = graycomatrix(parche, distances=[1, 2], angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
                            levels=NIVELES_GLCM + 1, symmetric=True, normed=False)
        glcm = glcm[1:, 1:].astype(np.float64)
        glcm /= np.maximum(glcm.sum(axis=(0, 1), keepdims=True), 1)
        for prop in ("contrast", "homogeneity", "energy", "correlation", "dissimilarity"):
            val = graycoprops(glcm, prop)
            f[f"glcm_{prop}"] = float(np.nan_to_num(val).mean())
        p = glcm.mean(axis=(2, 3))
        p = p[p > 0] / max(p.sum(), 1e-12)
        f["glcm_entropia"] = float(-(p * np.log2(p)).sum())

        # Textura LBP (histograma de patrones uniformes)
        hist, _ = np.histogram(sel(lbp), bins=LBP_P + 2, range=(0, LBP_P + 2), density=True)
        for i, h in enumerate(hist):
            f[f"lbp_{i}"] = h
        filas.append(f)

    return pd.DataFrame(filas)


# Columnas que no son descriptores (identificación / posición / etiquetas)
NO_DESCRIPTORES = {"id", "fila", "col", "x", "y", "clase", "imagen", "dist_verdad", "prob_mango", "pred"}


def columnas_descriptoras(df):
    return [c for c in df.columns if c not in NO_DESCRIPTORES and np.issubdtype(df[c].dtype, np.number)]
