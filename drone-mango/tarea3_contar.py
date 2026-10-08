"""TAREA 3 - Con imágenes de dron NUEVAS y el modelo de la tarea 2: ¿hay mangos? ¿cuántos? estadísticas.

Flujo: segmentar copas -> extraer descriptores -> clasificar con el modelo entrenado ->
contar y resumir:
  * presencia y número de árboles de mango (y de otras copas), con probabilidad por copa
  * densidad (árboles/ha), cobertura de copa (%), área y diámetro de copa (media, DE, cuartiles)
  * espaciamiento entre mangos (distancia al vecino más cercano), índice de Clark-Evans
  * mapa de densidad por celdas de grilla y conteo por celda
  * intervalo de confianza bootstrap del conteo esperado (suma de probabilidades)
  * (opcional) evaluación contra conteo de campo: precisión, recall, F1, error de conteo

    python tarea3_contar.py datos_demo/sector_nuevo.png --modelo resultados/tarea2/modelo_mango.joblib \
        --verdad datos_demo/sector_nuevo_verdad.csv --salida resultados/tarea3
"""
import argparse
import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from mango_uav import caracteristicas, imagen, segmentacion, utilidades


def describir(serie):
    if len(serie) == 0:
        return {}
    q = serie.quantile([0.25, 0.5, 0.75])
    return {"media": serie.mean(), "de": serie.std(ddof=1) if len(serie) > 1 else 0.0, "min": serie.min(),
            "q1": q[0.25], "mediana": q[0.5], "q3": q[0.75], "max": serie.max()}


def clark_evans(xy, area_m2):
    """R = distancia media al vecino más cercano observada / esperada bajo aleatoriedad (Clark & Evans 1954).
    R<1 agregado, R≈1 aleatorio, R>1 regular (típico de plantaciones en marco)."""
    n = len(xy)
    if n < 3:
        return np.nan, np.nan
    d, _ = cKDTree(xy).query(xy, k=2)
    nn = d[:, 1]
    esperado = 0.5 / np.sqrt(n / area_m2)
    return float(nn.mean() / esperado), nn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen", nargs="+", help="ortomosaico(s) nuevos")
    ap.add_argument("--modelo", required=True, help="modelo_mango.joblib de la tarea 2")
    ap.add_argument("--gsd", type=float)
    ap.add_argument("--banda-nir", type=int)
    ap.add_argument("--escala", type=float, default=1.0)
    ap.add_argument("--umbral", type=float, help="probabilidad mínima para considerar 'mango' (def.: el del modelo)")
    ap.add_argument("--diametro-min", type=float, default=2.5)
    ap.add_argument("--area-min", type=float, default=3.0)
    ap.add_argument("--celda-m", type=float, default=30.0, help="lado de celda para el mapa de densidad (m)")
    ap.add_argument("--verdad", nargs="*", help="CSV(s) de conteo de campo para evaluar")
    ap.add_argument("--radio-emparejar", type=float, default=2.0)
    ap.add_argument("--salida", default="resultados/tarea3")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)

    paquete = joblib.load(a.modelo)
    modelo, cols, objetivo = paquete["modelo"], paquete["columnas"], paquete["clase_objetivo"]
    umbral = a.umbral if a.umbral is not None else paquete.get("umbral", 0.5)
    rng = np.random.default_rng(0)
    resumenes = []

    for k, ruta in enumerate(a.imagen):
        nombre = Path(ruta).stem
        orto = imagen.leer(ruta, gsd=a.gsd, banda_nir=a.banda_nir, escala=a.escala)
        etiquetas, veg, _ = segmentacion.segmentar(orto, diametro_min_m=a.diametro_min, area_min_m2=a.area_min)
        copas = caracteristicas.tabla_copas(orto, etiquetas)
        area_m2 = orto.area_ha * 10_000
        if copas.empty:
            print(f"[{nombre}] no se detectó vegetación arbórea")
            continue
        copas["prob_mango"] = modelo.predict_proba(copas[cols].to_numpy(np.float64))[:, 1]
        copas["pred"] = np.where(copas["prob_mango"] >= umbral, objetivo, "otro")
        mangos = copas[copas["pred"] == objetivo]

        # --- Estadísticas ---
        n = len(mangos)
        p = copas["prob_mango"].to_numpy()
        # IC 95 % del conteo esperado: bootstrap paramétrico (cada copa es mango con prob. p)
        sim = (rng.random((2000, len(p))) < p).sum(axis=1)
        ce, nn = clark_evans(mangos[["x", "y"]].to_numpy(), area_m2) if n >= 3 else (np.nan, np.array([]))
        res = {
            "imagen": nombre,
            "gsd_m": orto.gsd,
            "area_analizada_ha": orto.area_ha,
            "hay_mangos": bool(n > 0),
            "n_copas_detectadas": int(len(copas)),
            "n_mangos": int(n),
            "n_otras_copas": int(len(copas) - n),
            "proporcion_mango_pct": 100 * n / len(copas),
            "conteo_esperado_mangos": float(p.sum()),
            "ic95_conteo_mangos": [float(np.percentile(sim, 2.5)), float(np.percentile(sim, 97.5))],
            "densidad_mangos_arb_ha": n / orto.area_ha,
            "cobertura_copa_mango_pct": 100 * mangos["area_m2"].sum() / area_m2,
            "cobertura_vegetal_total_pct": 100 * float(veg[orto.valido].mean()),
            "area_copa_mango_m2": describir(mangos["area_m2"]),
            "diametro_copa_mango_m": describir(mangos["diametro_m"]),
            "prob_media_mangos": float(mangos["prob_mango"].mean()) if n else None,
            "copas_dudosas_0.3_0.7": int(((p > 0.3) & (p < 0.7)).sum()),
            "distancia_vecino_mas_cercano_m": describir(pd.Series(nn)),
            "indice_clark_evans": ce,
        }

        # Mapa de densidad por celdas
        alto_m, ancho_m = np.array(etiquetas.shape) * orto.gsd
        nf, nc = max(1, int(np.ceil(alto_m / a.celda_m))), max(1, int(np.ceil(ancho_m / a.celda_m)))
        grilla = np.zeros((nf, nc), int)
        fi = np.minimum((mangos["fila"] * orto.gsd // a.celda_m).astype(int), nf - 1)
        ci = np.minimum((mangos["col"] * orto.gsd // a.celda_m).astype(int), nc - 1)
        np.add.at(grilla, (fi, ci), 1)
        celdas = pd.DataFrame([{"celda_fila": i, "celda_col": j, "n_mangos": grilla[i, j],
                                "densidad_arb_ha": grilla[i, j] / (a.celda_m ** 2 / 10_000)}
                               for i in range(nf) for j in range(nc)])
        celdas.to_csv(out / f"{nombre}_conteo_por_celda.csv", index=False)
        res["conteo_por_celda"] = describir(celdas["n_mangos"])

        # Evaluación con conteo de campo
        if a.verdad:
            verdad = utilidades.leer_verdad(a.verdad[k], orto)
            v_m = verdad[verdad["clase"] == objetivo]
            res["evaluacion_vs_campo"] = utilidades.evaluar_conteo(mangos[["x", "y"]].to_numpy(),
                                                                   v_m[["x", "y"]].to_numpy(), a.radio_emparejar)

        # --- Salidas ---
        copas.insert(1, "imagen", nombre)
        copas.drop(columns=[c for c in copas.columns if c.startswith("lbp_")]).to_csv(
            out / f"{nombre}_copas_clasificadas.csv", index=False)
        utilidades.exportar_geojson(copas, out / f"{nombre}_copas.geojson", crs=orto.crs,
                                    columnas=["id", "pred", "prob_mango", "area_m2", "diametro_m"])
        utilidades.mapa_copas(orto, etiquetas, copas, out / f"{nombre}_mapa_deteccion.png", columna_color="pred",
                              colores={objetivo: "red", "otro": "cyan"},
                              titulo=f"{nombre}: {n} mangos detectados ({res['densidad_mangos_arb_ha']:.0f} árb/ha)")

        fig, axs = plt.subplots(1, 3, figsize=(16, 4.5))
        axs[0].hist(mangos["diametro_m"], bins=20, color="#c0392b", alpha=0.8, label=objetivo)
        axs[0].hist(copas.loc[copas.pred != objetivo, "diametro_m"], bins=20, color="#16a085", alpha=0.6,
                    label="otro")
        axs[0].set_xlabel("diámetro de copa (m)"); axs[0].set_ylabel("nº copas"); axs[0].legend()
        axs[0].set_title("Distribución de tamaños de copa")
        axs[1].hist(copas["prob_mango"], bins=20, color="#7f8c8d")
        axs[1].axvline(umbral, color="k", ls="--", label=f"umbral {umbral}")
        axs[1].set_xlabel("probabilidad de mango"); axs[1].legend(); axs[1].set_title("Confianza del modelo")
        im = axs[2].imshow(grilla, cmap="YlOrRd", extent=(0, nc * a.celda_m, nf * a.celda_m, 0))
        for i in range(nf):
            for j in range(nc):
                axs[2].text((j + 0.5) * a.celda_m, (i + 0.5) * a.celda_m, grilla[i, j], ha="center", va="center",
                            fontsize=8)
        axs[2].set_title(f"Mangos por celda de {a.celda_m:.0f} m"); axs[2].set_xlabel("m"); axs[2].set_ylabel("m")
        fig.colorbar(im, ax=axs[2], shrink=0.8)
        fig.tight_layout(); fig.savefig(out / f"{nombre}_estadisticas.png", dpi=120); plt.close(fig)

        resumenes.append(res)
        print(f"\n[{nombre}] área {orto.area_ha:.2f} ha | ¿hay mangos? {'SÍ' if n else 'NO'}")
        print(f"  mangos detectados: {n}  (esperado {res['conteo_esperado_mangos']:.1f}, "
              f"IC95% {res['ic95_conteo_mangos'][0]:.0f}-{res['ic95_conteo_mangos'][1]:.0f})")
        print(f"  otras copas: {res['n_otras_copas']} | densidad: {res['densidad_mangos_arb_ha']:.1f} árb/ha | "
              f"cobertura de copa mango: {res['cobertura_copa_mango_pct']:.1f}%")
        if n:
            d = res["diametro_copa_mango_m"]
            print(f"  diámetro de copa: {d['media']:.2f} ± {d['de']:.2f} m (mediana {d['mediana']:.2f})")
            print(f"  vecino más cercano: {res['distancia_vecino_mas_cercano_m'].get('media', np.nan):.2f} m | "
                  f"Clark-Evans R={ce:.2f}")
        if "evaluacion_vs_campo" in res:
            e = res["evaluacion_vs_campo"]
            print(f"  vs. campo: real={e['conteo_real']} detectado={e['conteo_detectado']} "
                  f"(error {e['error_conteo_pct']:+.1f}%) | precisión={e['precision']:.3f} "
                  f"recall={e['recall']:.3f} F1={e['f1']:.3f}")

    with open(out / "resumen_conteo.json", "w", encoding="utf-8") as fh:
        json.dump(resumenes, fh, indent=2, ensure_ascii=False, default=float)
    plano = pd.json_normalize(resumenes, sep=".")
    plano.to_csv(out / "resumen_conteo.csv", index=False)
    print(f"\nResumen: {out / 'resumen_conteo.json'}")


if __name__ == "__main__":
    main()
