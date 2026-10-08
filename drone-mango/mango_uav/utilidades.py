"""Etiquetado con puntos de campo, emparejamiento con verdad terreno, mapas y exportación."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from skimage import segmentation


def leer_verdad(ruta, orto):
    """Lee puntos de campo (CSV con columnas x, y, clase). Coordenadas en el CRS del ortomosaico
    o, si la imagen no está georreferenciada, en píxeles de la imagen ORIGINAL (columnas ``col``, ``fila``)."""
    v = pd.read_csv(ruta)
    if {"fila", "col"}.issubset(v.columns):
        v["x"], v["y"] = orto.pixel_a_mundo(v["fila"] * orto.escala, v["col"] * orto.escala)
    elif not {"x", "y"}.issubset(v.columns):
        raise ValueError("El CSV de verdad terreno debe tener columnas x,y,clase o fila,col,clase")
    v["clase"] = v["clase"].astype(str).str.strip().str.lower()
    return v


def emparejar(det_xy, verdad_xy, radio):
    """Emparejamiento uno a uno (algoritmo húngaro) entre detecciones y puntos de verdad dentro de ``radio``.
    Devuelve lista de pares (i_det, j_verdad, distancia)."""
    if len(det_xy) == 0 or len(verdad_xy) == 0:
        return []
    d = np.linalg.norm(det_xy[:, None, :] - verdad_xy[None, :, :], axis=2)
    costo = np.where(d <= radio, d, 1e9)
    filas, cols = linear_sum_assignment(costo)
    return [(i, j, d[i, j]) for i, j in zip(filas, cols) if d[i, j] <= radio]


def etiquetar_con_verdad(copas, verdad, radio, clase_fondo="otro"):
    """Asigna a cada copa la clase del punto de campo emparejado; las no emparejadas reciben ``clase_fondo``."""
    copas = copas.copy()
    copas["clase"] = clase_fondo
    copas["dist_verdad"] = np.nan
    pares = emparejar(copas[["x", "y"]].to_numpy(), verdad[["x", "y"]].to_numpy(), radio)
    for i, j, dist in pares:
        copas.iat[i, copas.columns.get_loc("clase")] = verdad["clase"].iat[j]
        copas.iat[i, copas.columns.get_loc("dist_verdad")] = dist
    return copas


def evaluar_conteo(det_xy, verdad_xy, radio):
    pares = emparejar(det_xy, verdad_xy, radio)
    vp = len(pares)
    fp, fn = len(det_xy) - vp, len(verdad_xy) - vp
    prec = vp / max(vp + fp, 1)
    rec = vp / max(vp + fn, 1)
    return {"verdaderos_positivos": vp, "falsos_positivos": fp, "falsos_negativos": fn,
            "precision": prec, "recall": rec, "f1": 2 * prec * rec / max(prec + rec, 1e-12),
            "conteo_detectado": int(len(det_xy)), "conteo_real": int(len(verdad_xy)),
            "error_conteo_pct": 100 * (len(det_xy) - len(verdad_xy)) / max(len(verdad_xy), 1)}


def mapa_copas(orto, etiquetas, copas, ruta, columna_color=None, titulo="", colores=None, numerar=False):
    """Superpone los contornos de las copas sobre la imagen, coloreados por clase."""
    alto, ancho = etiquetas.shape
    fig, ax = plt.subplots(figsize=(12, 12 * alto / ancho))
    ax.imshow(orto.rgb)
    if columna_color is None:
        bordes = segmentation.find_boundaries(etiquetas, mode="outer")
        ax.imshow(np.ma.masked_where(~bordes, bordes), cmap=ListedColormap(["yellow"]), interpolation="none")
    else:
        colores = colores or {}
        paleta = plt.get_cmap("tab10")
        for k, clase in enumerate(sorted(copas[columna_color].astype(str).unique())):
            ids = copas.loc[copas[columna_color].astype(str) == clase, "id"].to_numpy()
            bordes = segmentation.find_boundaries(np.isin(etiquetas, ids) * etiquetas, mode="outer")
            c = colores.get(clase, paleta(k))
            ax.imshow(np.ma.masked_where(~bordes, bordes), cmap=ListedColormap([c]), interpolation="none")
            ax.plot([], [], "s", color=c, label=f"{clase} ({len(ids)})")
        ax.legend(loc="upper right", framealpha=0.85)
    if numerar:
        for _, r in copas.iterrows():
            ax.text(r["col"], r["fila"], str(int(r["id"])), color="white", fontsize=6, ha="center", va="center")
    ax.set_title(titulo)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def exportar_geojson(copas, ruta, crs=None, columnas=None):
    columnas = columnas or [c for c in copas.columns if c not in ("x", "y")]
    feats = []
    for _, r in copas.iterrows():
        props = {c: (r[c].item() if hasattr(r[c], "item") else r[c]) for c in columnas}
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(r["x"]), float(r["y"])]},
                      "properties": props})
    gj = {"type": "FeatureCollection", "features": feats}
    if crs is not None:
        gj["crs"] = {"type": "name", "properties": {"name": str(crs)}}
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(gj, fh, ensure_ascii=False)


def recortes(orto, copas, carpeta, margen_m=0.5, columna_clase=None):
    """Guarda un recorte PNG por copa (útil para revisar/etiquetar o entrenar una CNN)."""
    from PIL import Image
    m = int(round(margen_m / orto.gsd))
    for _, r in copas.iterrows():
        rad = int(round(r["diametro_m"] / 2 / orto.gsd)) + m
        f0, c0 = int(r["fila"]), int(r["col"])
        rec = orto.rgb[max(0, f0 - rad):f0 + rad, max(0, c0 - rad):c0 + rad]
        sub = carpeta / str(r[columna_clase]) if columna_clase else carpeta
        sub.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rec).save(sub / f"copa_{int(r['id']):05d}.png")
