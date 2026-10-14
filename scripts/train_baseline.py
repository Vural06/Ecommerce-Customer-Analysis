"""Çoğunluk sınıfı referansı ve basit lojistik regresyon; test verisi okunmaz."""
from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
FEATURES = ["recency_days", "frequency_180d", "monetary_180d_gbp",
            "average_invoice_amount_gbp", "quantity_180d"]
KEYS = ["snapshot_date", "customer_id"]


def load_snapshot(split):
    features = pd.read_csv(DATA_DIR / f"{split}_features.csv")
    labels = pd.read_csv(DATA_DIR / f"{split}_labels.csv")
    if features.duplicated(KEYS).any() or labels.duplicated(KEYS).any():
        raise ValueError("Müşteri/tarih anahtarları tekil olmalı.")
    joined = features.merge(labels[KEYS + ["no_purchase_90d"]],
                            on=KEYS, how="outer", validate="one_to_one", indicator=True)
    if not joined["_merge"].eq("both").all():
        raise ValueError("Özellik/hedef müşterileri tam eşleşmiyor.")
    X = joined[FEATURES].copy()
    # Önce doğrula: astype(int) yanlışlıkla 0,5 gibi etiketleri 0'a çevirebilir.
    if not joined["no_purchase_90d"].isin([0, 1]).all():
        raise ValueError("Hedef değerleri yalnızca 0 veya 1 olmalı.")
    y = joined["no_purchase_90d"].astype(int)
    if X.empty or not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Model girdisi boş, eksik veya sonlu olmayan değer içeriyor.")
    if set(y.unique()) != {0, 1}:
        raise ValueError("Bu değerlendirme için iki hedef sınıfı da gerekli.")
    return X, y, joined[KEYS]


def make_logistic_model():
    # Pipeline: ölçekleyici sadece fit sırasında eğitim verisinden öğrenir.
    # Daha büyük ölçekteki GBP/miktar değerlerini gün ve fatura sayısıyla hizalar.
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
    ])


def evaluate(y, probabilities, predictions):
    tn, fp, fn, tp = confusion_matrix(y, predictions, labels=[0, 1]).ravel()
    return {
        "average_precision": float(average_precision_score(y, probabilities)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "accuracy": float(accuracy_score(y, predictions)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def choose_threshold(y, probabilities):
    # Küçük, önceden belirlenen aday listesi. İş maliyeti bilinmediği için F1.
    rows = []
    for threshold in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        predictions = (probabilities >= threshold).astype(int)
        rows.append({"threshold": threshold,
                     "precision": precision_score(y, predictions, zero_division=0),
                     "recall": recall_score(y, predictions, zero_division=0),
                     "f1": f1_score(y, predictions, zero_division=0)})
    candidates = pd.DataFrame(rows)
    # F1 eşitse daha yüksek eşik: daha az müşteriyi riskli işaretler.
    best = candidates.sort_values(["f1", "threshold"], ascending=False).iloc[0]
    return float(best["threshold"]), candidates


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join(["---"] * len(headers)) + " |",
                      *["| " + " | ".join(map(str, row)) + " |" for row in rows]])


def main():
    X_train, y_train, train_keys = load_snapshot("train")
    X_val, y_val, val_keys = load_snapshot("validation")
    if not pd.to_datetime(train_keys["snapshot_date"]).max() < pd.to_datetime(val_keys["snapshot_date"]).min():
        raise ValueError("Eğitim tarihi doğrulamadan önce olmalı.")

    majority = DummyClassifier(strategy="prior")
    majority.fit(X_train, y_train)
    logistic = make_logistic_model()
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        logistic.fit(X_train, y_train)
    # Tahmin yapmak scaler parametrelerini değiştirmez.
    probabilities = logistic.predict_proba(X_val)[:, 1]
    threshold, candidates = choose_threshold(y_val, probabilities)
    scores = {
        "majority_validation": evaluate(y_val, majority.predict_proba(X_val)[:, 1], majority.predict(X_val)),
        "logistic_train_0.5": evaluate(y_train, logistic.predict_proba(X_train)[:, 1], logistic.predict(X_train)),
        "logistic_validation_0.5": evaluate(y_val, probabilities, (probabilities >= 0.5).astype(int)),
        "logistic_validation_selected": evaluate(y_val, probabilities, (probabilities >= threshold).astype(int)),
    }
    # Eğitim bittikten sonra aynı pipeline ve karar eşiği kaydedilir.
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(exist_ok=True)
    joblib.dump(logistic, artifact_dir / "logistic_baseline.joblib")
    metadata = {"features": FEATURES, "threshold": threshold,
                "sklearn_version": sklearn.__version__, "C": 1.0, "max_iter": 1000,
                "train_rows": len(X_train), "validation_rows": len(X_val),
                "selection_rule": "validation F1, ties prefer higher threshold",
                "metrics": scores, "test_evaluated": False}
    (artifact_dir / "baseline_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    predictions = val_keys.copy()
    predictions["actual_no_purchase_90d"] = y_val
    predictions["risk_score"] = probabilities
    predictions["predicted_no_purchase_90d"] = (probabilities >= threshold).astype(int)
    predictions.to_csv(DATA_DIR / "validation_baseline_predictions.csv", index=False)
    assert len(predictions) == len(X_val)
    assert np.allclose(logistic.named_steps["scaler"].mean_, X_train.mean().to_numpy())
    # Katsayılar standardize edilmiş değişkenlerin koşullu ilişkisini gösterir.
    coefficients = list(zip(FEATURES, logistic.named_steps["model"].coef_[0]))
    metrics_rows = [(name, *[f"{result[k]:.4f}" for k in
                            ["average_precision", "roc_auc", "precision", "recall", "f1", "accuracy"]])
                    for name, result in scores.items()]
    selected = scores["logistic_validation_selected"]
    report = ["# Başlangıç modelleri", "## Kapsam ve yöntem",
              f"Eğitim: {len(X_train)} müşteri; doğrulama: {len(X_val)} müşteri. "
              f"scikit-learn {sklearn.__version__}. Test dosyaları bu betikte okunmaz.",
              "Hedef=1: sonraki 90 günde alışveriş yapmama. Referans model her "
              "müşteriye eğitim çoğunluk sınıfını verir; risk puanı eğitimdeki "
              "sınıf oranıdır, müşteri bazında değişmez. Basit model StandardScaler "
              "+ LogisticRegression (C=1, max_iter=1000). Hiperparametre araması yoktur.",
              "Yalnızca beş sayısal SQL özelliği kullanılır: " + ", ".join(f"`{column}`" for column in FEATURES) + ". "
              "Kimlikler, tarihler, gelecek fatura sayısı ve RFM segmentleri modele verilmez. "
              "Ölçekleyici yalnızca train üzerinde öğrenir; validation fit işlemi görmez.",
              "## Sonuçlar", table(["Model/bölüm", "AP", "ROC-AUC", "Precision", "Recall", "F1", "Accuracy"], metrics_rows),
              "Average precision (AP), precision-recall eğrisinin eşiklere göre ağırlıklı "
              "özetidir; trapez PR-AUC hesabıyla bire bir aynı değildir. Sabit puanlı "
              "referansın AP'si değerlendirilen dönemin hedef=1 oranıdır. Precision: "
              "riskli işaretlenenlerin ne kadarı gerçekten alışveriş yapmadı? Recall: "
              "alışveriş yapmayanların ne kadarı yakalandı? F1 iki oranı dengeler. "
              "Accuracy sınıf dağılımından etkilenir. Eğitim skoru genel başarı değildir.",
              "## Karar eşiği", table(["Eşik", "Precision", "Recall", "F1"], [
                  (f"{r.threshold:.1f}", f"{r.precision:.4f}", f"{r.recall:.4f}", f"{r.f1:.4f}")
                  for r in candidates.itertuples()]),
              f"Seçilen eşik: **{threshold:.1f}**. Seçim yalnızca validation F1 üzerinden "
              "yapıldı; eşit F1'da yüksek eşik tercih edilir. İş maliyeti ve kampanya "
              "kapasitesi bilinmediğinden bu eşik operasyonel olarak en uygun eşik "
              "iddiası taşımaz. Seçim ve ölçüm aynı validation üzerinde olduğundan "
              "seçilen F1 iyimser olabilir; test sonuçları ayrı model karşılaştırması raporunda yer alır.",
              "## Doğrulama hata matrisi (seçilen eşik)",
              table(["Gerçek / tahmin", "0: alışveriş yapar", "1: alışveriş yapmaz"], [
                  ("0: alışveriş yaptı", selected["tn"], selected["fp"]),
                  ("1: alışveriş yapmadı", selected["fn"], selected["tp"])]),
              "## Lojistik regresyon katsayıları",
              table(["Özellik", "Standardize katsayı"], [(name, f"{value:.4f}") for name, value in coefficients]),
              "Pozitif katsayı, diğer girdiler sabitken hedef=1 yönündeki ilişkiyi "
              "gösterir. Katsayılar nedensel etki değildir; sıklık, harcama ve "
              "ortalama fatura tutarı birbiriyle ilişkilidir. Buradan bağımsız "
              "iş etkisi veya kesin özellik önemi çıkarılamaz.",
              "## Sınırlılıklar ve sonraki adım",
              "Başlangıç karşılaştırması yalnızca bir eğitim ve bir doğrulama "
              "tarihine dayanır. Müşteriler dönemler arasında tekrar bulunabilir. "
              "Brüt tutarlar iadelerle netleştirilmemiştir; sayfa içi tekrarlar korunur. "
              "Ham parasal/miktar girdileri aykırı değerlerden etkilenebilir. "
              "Olasılıklar ayrıca kalibre edilmedi; risk sıralaması ve karar eşiği "
              "başlangıç amaçlıdır. Kampanya kazancı ölçülmedi.",
              "Bu başlangıç betiği test verisini okumaz. Tek alternatif model "
              "ve sabit kararlarla test değerlendirmesi scripts/compare_models.py "
              "içinde yapılır. Güncel sonuçlar reports/model_comparison.md içindedir.",
              "## Yerel çıktılar",
              "`artifacts/logistic_baseline.joblib`, `artifacts/baseline_metadata.json` "
              "ve `data/processed/validation_baseline_predictions.csv`. Model "
              "dosyaları ve müşteri tahminleri Git dışındadır."]
    report_path = ROOT / "reports" / "baseline_model.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    print(f"Seçilen eşik: {threshold:.1f}")
    for name, result in scores.items():
        print(f"{name}: AP={result['average_precision']:.4f}, F1={result['f1']:.4f}")


if __name__ == "__main__":
    main()
