"""Ruta alternativa con DEEP LEARNING (tareas 2 y 3): detector de objetos YOLO (Ultralytics).

Recomendada cuando hay cientos/miles de copas etiquetadas y las copas se tocan o se
solapan (la segmentación clásica falla), siguiendo la línea de MangoYOLO
(Koirala et al. 2019), Xiong et al. (2020) y Neupane et al. (2019).

Subcomandos:
  exportar  convierte la salida de la tarea 1 (copas etiquetadas) a un dataset YOLO
            (teselas + cajas), con partición espacial train/val por teselas.
  entrenar  entrena un YOLO (requiere ``pip install ultralytics``).
  contar    aplica el detector a un ortomosaico nuevo por teselas con solape, fusiona
            detecciones duplicadas y entrega conteo + CSV/GeoJSON (tarea 3).

    python yolo_mango.py exportar datos_demo/sector_entrenamiento.png \
        --copas resultados/tarea1/copas_caracteristicas.csv \
        --etiquetas resultados/tarea1/sector_entrenamiento_etiquetas.npy --salida dataset_yolo
    python yolo_mango.py entrenar --datos dataset_yolo/data.yaml --modelo yolov8n.pt --epocas 100
    python yolo_mango.py contar datos_demo/sector_nuevo.png --pesos runs/detect/train/weights/best.pt
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from skimage import measure

from mango_uav import imagen, utilidades


def teselas(alto, ancho, lado, solape):
    paso = max(1, int(lado * (1 - solape)))
    filas = list(range(0, max(alto - lado, 0) + 1, paso))
    cols = list(range(0, max(ancho - lado, 0) + 1, paso))
    if filas[-1] + lado < alto:
        filas.append(alto - lado)
    if cols[-1] + lado < ancho:
        cols.append(ancho - lado)
    return [(max(f, 0), max(c, 0)) for f in filas for c in cols]


def exportar(a):
    orto = imagen.leer(a.imagen, gsd=a.gsd)
    etiquetas = np.load(a.etiquetas)
    copas = pd.read_csv(a.copas)
    if "imagen" in copas:
        copas = copas[copas["imagen"] == Path(a.imagen).stem]
    clases = sorted(copas["clase"].dropna().astype(str).unique()) if not a.solo_mango else ["mango"]
    if a.solo_mango:
        copas = copas[copas["clase"] == "mango"]
    id_clase = dict(zip(copas["id"], copas["clase"].astype(str)))
    cajas = [(r.label, *r.bbox) for r in measure.regionprops(etiquetas) if r.label in id_clase]

    out = Path(a.salida)
    alto, ancho = etiquetas.shape
    rng = np.random.default_rng(a.semilla)
    n = {"train": 0, "val": 0}
    for (f0, c0) in teselas(alto, ancho, a.lado, a.solape):
        f1, c1 = min(f0 + a.lado, alto), min(c0 + a.lado, ancho)
        lineas = []
        for (lab, y0, x0, y1, x1) in cajas:
            iy0, ix0, iy1, ix1 = max(y0, f0), max(x0, c0), min(y1, f1), min(x1, c1)
            if iy1 <= iy0 or ix1 <= ix0:
                continue
            if (iy1 - iy0) * (ix1 - ix0) < 0.5 * (y1 - y0) * (x1 - x0):  # copa mayormente fuera de la tesela
                continue
            h, w = f1 - f0, c1 - c0
            cx, cy = ((ix0 + ix1) / 2 - c0) / w, ((iy0 + iy1) / 2 - f0) / h
            lineas.append(f"{clases.index(id_clase[lab])} {cx:.6f} {cy:.6f} {(ix1 - ix0) / w:.6f} {(iy1 - iy0) / h:.6f}")
        particion = "val" if rng.random() < a.frac_val else "train"
        nombre = f"{Path(a.imagen).stem}_{f0}_{c0}"
        (out / "images" / particion).mkdir(parents=True, exist_ok=True)
        (out / "labels" / particion).mkdir(parents=True, exist_ok=True)
        Image.fromarray(orto.rgb[f0:f1, c0:c1]).save(out / "images" / particion / f"{nombre}.jpg", quality=95)
        (out / "labels" / particion / f"{nombre}.txt").write_text("\n".join(lineas))
        n[particion] += 1
    (out / "data.yaml").write_text(
        f"path: {out.resolve()}\ntrain: images/train\nval: images/val\n"
        f"names:\n" + "".join(f"  {i}: {c}\n" for i, c in enumerate(clases)))
    print(f"Dataset YOLO en {out}: {n['train']} teselas train, {n['val']} val, clases={clases}")


def entrenar(a):
    from ultralytics import YOLO
    YOLO(a.modelo).train(data=a.datos, epochs=a.epocas, imgsz=a.lado, batch=a.lote, seed=a.semilla,
                         degrees=90, flipud=0.5, fliplr=0.5, hsv_v=0.3)  # aumentos: vista cenital invariante a rotación


def contar(a):
    from ultralytics import YOLO
    det = YOLO(a.pesos)
    orto = imagen.leer(a.imagen, gsd=a.gsd)
    alto, ancho = orto.rgb.shape[:2]
    filas = []
    for (f0, c0) in teselas(alto, ancho, a.lado, a.solape):
        res = det.predict(orto.rgb[f0:f0 + a.lado, c0:c0 + a.lado], conf=a.conf, imgsz=a.lado, verbose=False)[0]
        for (x0, y0, x1, y1), conf, cls in zip(res.boxes.xyxy.cpu().numpy(), res.boxes.conf.cpu().numpy(),
                                               res.boxes.cls.cpu().numpy().astype(int)):
            filas.append({"fila": f0 + (y0 + y1) / 2, "col": c0 + (x0 + x1) / 2, "conf": float(conf),
                          "clase": res.names[cls],
                          "diametro_m": float(np.sqrt((x1 - x0) * (y1 - y0))) * orto.gsd})
    d = pd.DataFrame(filas)
    if d.empty:
        print("Sin detecciones."); return
    # Fusión de duplicados entre teselas solapadas: se conserva la de mayor confianza
    d = d.sort_values("conf", ascending=False).reset_index(drop=True)
    xy = d[["fila", "col"]].to_numpy() * orto.gsd
    keep = np.ones(len(d), bool)
    for i in range(len(d)):
        if keep[i]:
            cerca = np.linalg.norm(xy[i + 1:] - xy[i], axis=1) < a.dist_fusion
            keep[i + 1:][cerca & (d["clase"].to_numpy()[i + 1:] == d["clase"].iat[i])] = False
    d = d[keep].reset_index(drop=True)
    d.insert(0, "id", np.arange(1, len(d) + 1))
    d["x"], d["y"] = orto.pixel_a_mundo(d["fila"], d["col"])
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    nombre = Path(a.imagen).stem
    d.to_csv(out / f"{nombre}_detecciones_yolo.csv", index=False)
    utilidades.exportar_geojson(d, out / f"{nombre}_detecciones_yolo.geojson", crs=orto.crs,
                                columnas=["id", "clase", "conf", "diametro_m"])
    resumen = {"imagen": nombre, "area_ha": orto.area_ha,
               "conteo_por_clase": d["clase"].value_counts().to_dict(),
               "densidad_arb_ha": (d["clase"].value_counts() / orto.area_ha).to_dict()}
    if a.verdad:
        verdad = utilidades.leer_verdad(a.verdad, orto)
        m, v = d[d.clase == "mango"], verdad[verdad.clase == "mango"]
        resumen["evaluacion_vs_campo"] = utilidades.evaluar_conteo(m[["x", "y"]].to_numpy(), v[["x", "y"]].to_numpy(),
                                                                   a.radio_emparejar)
    (out / f"{nombre}_resumen_yolo.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False, default=float))
    print(json.dumps(resumen, indent=2, ensure_ascii=False, default=float))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exportar")
    e.add_argument("imagen"); e.add_argument("--copas", required=True); e.add_argument("--etiquetas", required=True)
    e.add_argument("--gsd", type=float); e.add_argument("--lado", type=int, default=640)
    e.add_argument("--solape", type=float, default=0.2); e.add_argument("--frac-val", type=float, default=0.2)
    e.add_argument("--solo-mango", action="store_true", help="una sola clase 'mango'")
    e.add_argument("--semilla", type=int, default=0); e.add_argument("--salida", default="dataset_yolo")
    t = sub.add_parser("entrenar")
    t.add_argument("--datos", required=True); t.add_argument("--modelo", default="yolov8n.pt")
    t.add_argument("--epocas", type=int, default=100); t.add_argument("--lado", type=int, default=640)
    t.add_argument("--lote", type=int, default=16); t.add_argument("--semilla", type=int, default=0)
    c = sub.add_parser("contar")
    c.add_argument("imagen"); c.add_argument("--pesos", required=True); c.add_argument("--gsd", type=float)
    c.add_argument("--lado", type=int, default=640); c.add_argument("--solape", type=float, default=0.2)
    c.add_argument("--conf", type=float, default=0.25)
    c.add_argument("--dist-fusion", type=float, default=2.0, help="m: detecciones más cercanas se fusionan")
    c.add_argument("--verdad"); c.add_argument("--radio-emparejar", type=float, default=2.0)
    c.add_argument("--salida", default="resultados/tarea3_yolo")
    a = ap.parse_args()
    {"exportar": exportar, "entrenar": entrenar, "contar": contar}[a.cmd](a)


if __name__ == "__main__":
    main()
