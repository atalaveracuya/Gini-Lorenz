"""TAREA 1 - Analizar imágenes de dron de un sector e identificar el cultivo (p. ej. mango).

Flujo:
  1. Lee el ortomosaico (GeoTIFF georreferenciado o JPG/PNG + --gsd).
  2. Calcula índices de vegetación (ExG, ExGR, VARI, GLI, NGRDI; NDVI si hay NIR).
  3. Segmenta la vegetación arbórea y separa cada copa (watershed).
  4. Extrae descriptores por copa (forma, color, índices, textura GLCM/LBP).
  5. Si se dan puntos de campo (--verdad), etiqueta cada copa con la especie observada
     -> tabla etiquetada para entrenar el modelo (tarea 2). Si no, deja la columna
     ``clase`` vacía para completarla a mano revisando el mapa numerado / los recortes.
  6. Caracteriza espectral y estructuralmente cada clase (firma del cultivo).

    python tarea1_identificar.py datos_demo/sector_entrenamiento.png \
        --verdad datos_demo/sector_entrenamiento_verdad.csv --salida resultados/tarea1
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from mango_uav import caracteristicas, imagen, indices, segmentacion, utilidades

FIRMA = ["diametro_m", "circularidad", "G_media", "H_media", "S_media", "V_media",
         "ExG_media", "VARI_media", "GLI_media", "glcm_contrast", "glcm_homogeneity", "glcm_entropia"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen", nargs="+", help="ortomosaico(s) del sector")
    ap.add_argument("--gsd", type=float, help="m/píxel si la imagen no está georreferenciada")
    ap.add_argument("--banda-nir", type=int, help="nº de banda NIR (cámaras multiespectrales)")
    ap.add_argument("--escala", type=float, default=1.0, help="factor de reducción para ortomosaicos grandes")
    ap.add_argument("--verdad", nargs="*", help="CSV(s) de puntos de campo (x,y,clase o fila,col,clase)")
    ap.add_argument("--radio-emparejar", type=float, default=2.0, help="m máx. entre copa y punto de campo")
    ap.add_argument("--diametro-min", type=float, default=2.5, help="diámetro mínimo esperado de copa (m)")
    ap.add_argument("--area-min", type=float, default=3.0, help="área mínima de copa (m²)")
    ap.add_argument("--recortes", action="store_true", help="guardar un PNG por copa (revisión / CNN)")
    ap.add_argument("--salida", default="resultados/tarea1")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)

    tablas = []
    for k, ruta in enumerate(a.imagen):
        nombre = Path(ruta).stem
        orto = imagen.leer(ruta, gsd=a.gsd, banda_nir=a.banda_nir, escala=a.escala)
        print(f"[{nombre}] {orto.rgb.shape[1]}x{orto.rgb.shape[0]} px, GSD={orto.gsd:.3f} m, "
              f"área={orto.area_ha:.2f} ha")

        # Índices de vegetación (mapas para inspección visual)
        idx = indices.todos(orto.rgb, orto.nir)
        fig, axs = plt.subplots(1, len(idx) + 1, figsize=(4 * (len(idx) + 1), 4))
        axs[0].imshow(orto.rgb); axs[0].set_title("RGB")
        for ax, (n, arr) in zip(axs[1:], idx.items()):
            lo, hi = np.percentile(arr[orto.valido], (2, 98))
            ax.imshow(arr, cmap="RdYlGn", vmin=lo, vmax=hi); ax.set_title(n)
        for ax in axs:
            ax.axis("off")
        fig.tight_layout(); fig.savefig(out / f"{nombre}_indices.png", dpi=110); plt.close(fig)

        # Segmentación de copas
        etiquetas, veg, umbral = segmentacion.segmentar(orto, diametro_min_m=a.diametro_min, area_min_m2=a.area_min)
        print(f"  umbral vegetación={umbral:.3f}, cobertura vegetal={100 * veg[orto.valido].mean():.1f}%, "
              f"copas segmentadas={etiquetas.max()}")
        np.save(out / f"{nombre}_etiquetas.npy", etiquetas)

        copas = caracteristicas.tabla_copas(orto, etiquetas)
        copas.insert(1, "imagen", nombre)

        if a.verdad:
            verdad = utilidades.leer_verdad(a.verdad[k], orto)
            copas = utilidades.etiquetar_con_verdad(copas, verdad, a.radio_emparejar)
            ev = utilidades.evaluar_conteo(copas[["x", "y"]].to_numpy(), verdad[["x", "y"]].to_numpy(),
                                           a.radio_emparejar)
            print(f"  segmentación vs. campo: precisión={ev['precision']:.3f} recall={ev['recall']:.3f} "
                  f"F1={ev['f1']:.3f}")
            with open(out / f"{nombre}_evaluacion_segmentacion.json", "w") as fh:
                json.dump(ev, fh, indent=2)
            utilidades.mapa_copas(orto, etiquetas, copas, out / f"{nombre}_mapa_clases.png", columna_color="clase",
                                  titulo=f"{nombre}: copas etiquetadas con puntos de campo",
                                  colores={"mango": "red", "otro": "cyan"})
        else:
            copas["clase"] = ""
        utilidades.mapa_copas(orto, etiquetas, copas, out / f"{nombre}_mapa_copas.png", numerar=True,
                              titulo=f"{nombre}: {len(copas)} copas segmentadas (id para etiquetar)")
        if a.recortes:
            utilidades.recortes(orto, copas, out / f"recortes_{nombre}", columna_clase="clase" if a.verdad else None)
        tablas.append(copas)

    import pandas as pd
    copas = pd.concat(tablas, ignore_index=True)
    copas.to_csv(out / "copas_caracteristicas.csv", index=False)
    print(f"Tabla de descriptores: {out / 'copas_caracteristicas.csv'} ({len(copas)} copas)")

    # Firma del cultivo: comparación de descriptores entre clases
    if a.verdad:
        firma = copas.groupby("clase")[FIRMA].agg(["mean", "std"]).T
        firma.to_csv(out / "firma_por_clase.csv")
        print("\nFirma por clase (media):")
        print(copas.groupby("clase")[FIRMA].mean().T.round(3).to_string())
        clases = sorted(copas["clase"].unique())
        fig, axs = plt.subplots(3, 4, figsize=(16, 10))
        for ax, col in zip(axs.ravel(), FIRMA):
            ax.boxplot([copas.loc[copas.clase == c, col] for c in clases], tick_labels=clases)
            ax.set_title(col)
        fig.suptitle("Tarea 1 - Firma espectral, estructural y textural por clase")
        fig.tight_layout(); fig.savefig(out / "firma_por_clase.png", dpi=110); plt.close(fig)


if __name__ == "__main__":
    main()
