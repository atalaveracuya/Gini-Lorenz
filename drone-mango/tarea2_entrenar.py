"""TAREA 2 - Entrenar un modelo de machine learning para reconocer copas de mango.

Entrada: la tabla etiquetada de la tarea 1 (copas_caracteristicas.csv, columna ``clase``).
Compara varios clasificadores con validación cruzada (k-fold estratificada y, por
defecto, también ESPACIAL por bloques para no sobreestimar el desempeño por
autocorrelación espacial; Roberts et al. 2017; Ploton et al. 2020), elige el mejor por F1
de la clase objetivo, lo reentrena con todos los datos y lo guarda (joblib).

Modelos: Random Forest (Breiman 2001), SVM-RBF (Cortes & Vapnik 1995),
Gradient Boosting (Friedman 2001) y regresión logística (línea base).

    python tarea2_entrenar.py resultados/tarea1/copas_caracteristicas.csv --salida resultados/tarea2
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
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report, cohen_kappa_score,
                             confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from mango_uav.caracteristicas import columnas_descriptoras


def modelos(semilla):
    return {
        "random_forest": RandomForestClassifier(n_estimators=500, min_samples_leaf=2, class_weight="balanced",
                                                n_jobs=-1, random_state=semilla),
        "svm_rbf": make_pipeline(StandardScaler(), CalibratedClassifierCV(
            SVC(C=10, gamma="scale", class_weight="balanced", random_state=semilla), method="sigmoid", cv=3)),
        "gradient_boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05,
                                                            class_weight="balanced", random_state=semilla),
        "regresion_logistica": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000,
                                                                                  class_weight="balanced")),
    }


def metricas(y, pred, prob):
    return {"exactitud": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0), "f1": f1_score(y, pred, zero_division=0),
            "kappa": cohen_kappa_score(y, pred), "auc_roc": roc_auc_score(y, prob) if len(set(y)) > 1 else np.nan}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tabla", nargs="+", help="CSV(s) etiquetados de la tarea 1")
    ap.add_argument("--clase-objetivo", default="mango")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--bloque-m", type=float, default=30.0, help="lado de bloque (m) para la CV espacial; 0 = no")
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--salida", default="resultados/tarea2")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.concat([pd.read_csv(t) for t in a.tabla], ignore_index=True)
    df = df[df["clase"].notna() & (df["clase"].astype(str).str.strip() != "")]
    df["clase"] = df["clase"].astype(str).str.strip().str.lower()
    cols = columnas_descriptoras(df)
    X = df[cols].to_numpy(np.float64)
    y = (df["clase"] == a.clase_objetivo).astype(int).to_numpy()
    print(f"{len(df)} copas etiquetadas: {y.sum()} '{a.clase_objetivo}', {len(y) - y.sum()} otras; "
          f"{len(cols)} descriptores")
    if y.sum() < a.folds or (len(y) - y.sum()) < a.folds:
        raise SystemExit("Muy pocas muestras por clase para la validación cruzada.")

    esquemas = {"kfold_estratificado": (StratifiedKFold(a.folds, shuffle=True, random_state=a.semilla), None)}
    if a.bloque_m > 0:
        # Bloques espaciales: copas del mismo bloque nunca están a la vez en entrenamiento y prueba
        img = df["imagen"].astype(str) if "imagen" in df else pd.Series("img", index=df.index)
        bloque = (img + "_" + (df["x"] // a.bloque_m).astype(int).astype(str) + "_"
                  + (df["y"] // a.bloque_m).astype(int).astype(str))
        grupos = pd.factorize(bloque)[0]
        if len(np.unique(grupos)) >= a.folds:
            esquemas["espacial_por_bloques"] = (GroupKFold(a.folds), grupos)

    filas, preds = [], {}
    for nombre, modelo in modelos(a.semilla).items():
        for esquema, (cv, grupos) in esquemas.items():
            prob = cross_val_predict(clone(modelo), X, y, cv=cv, groups=grupos, method="predict_proba")[:, 1]
            pred = (prob >= 0.5).astype(int)
            m = metricas(y, pred, prob)
            filas.append({"modelo": nombre, "validacion": esquema, **m})
            preds[(nombre, esquema)] = pred
    res = pd.DataFrame(filas)
    res.to_csv(out / "comparacion_modelos.csv", index=False)
    print("\nValidación cruzada (clase positiva = %s):" % a.clase_objetivo)
    print(res.round(3).to_string(index=False))

    # Selección: mejor F1 bajo el esquema más exigente disponible
    esquema_sel = "espacial_por_bloques" if "espacial_por_bloques" in esquemas else "kfold_estratificado"
    mejor = res[res.validacion == esquema_sel].sort_values("f1", ascending=False).iloc[0]["modelo"]
    print(f"\nModelo seleccionado: {mejor} (por F1 en validación '{esquema_sel}')")

    pred = preds[(mejor, esquema_sel)]
    nombres = ["otro", a.clase_objetivo]
    print(classification_report(y, pred, target_names=nombres, digits=3))
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay(confusion_matrix(y, pred), display_labels=nombres).plot(ax=ax, cmap="Greens",
                                                                                 colorbar=False)
    ax.set_title(f"{mejor} - CV {esquema_sel}")
    fig.tight_layout(); fig.savefig(out / "matriz_confusion.png", dpi=120); plt.close(fig)

    final = clone(modelos(a.semilla)[mejor]).fit(X, y)

    # Importancia de variables por permutación (sobre datos de entrenamiento: orientativa)
    imp = permutation_importance(final, X, y, scoring="f1", n_repeats=10, random_state=a.semilla, n_jobs=-1)
    imp = pd.Series(imp.importances_mean, index=cols).sort_values(ascending=False)
    imp.to_csv(out / "importancia_variables.csv", header=["importancia"])
    top = imp.head(15)[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(top.index, top.values, color="#3a7d44")
    ax.set_xlabel("caída media de F1 al permutar"); ax.set_title("Variables más importantes")
    fig.tight_layout(); fig.savefig(out / "importancia_variables.png", dpi=120); plt.close(fig)

    joblib.dump({"modelo": final, "columnas": cols, "clase_objetivo": a.clase_objetivo,
                 "nombre_modelo": mejor, "umbral": 0.5}, out / "modelo_mango.joblib")
    with open(out / "resumen_entrenamiento.json", "w") as fh:
        json.dump({"modelo": mejor, "validacion_seleccion": esquema_sel, "n_copas": int(len(y)),
                   "n_positivos": int(y.sum()),
                   "metricas_cv": res[(res.modelo == mejor)].set_index("validacion").to_dict(orient="index")},
                  fh, indent=2, default=float)
    print(f"Modelo guardado en {out / 'modelo_mango.joblib'}")


if __name__ == "__main__":
    main()
