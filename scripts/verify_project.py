"""Kayıtlı SQL/ML çıktıları, bağımlılıklar ve Git adaylarını değer ifşa etmeden kontrol et."""
from contextlib import closing
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import sqlite3
import subprocess

import joblib
import numpy as np
import pandas as pd

from build_customer_features import SNAPSHOTS, create_snapshot, load_invoices, make_windows
from build_rfm_segments import fit_thresholds, assign_segments, SEGMENTS, markdown_table
from compare_models import metrics_table, select_model
from train_baseline import FEATURES, choose_threshold, evaluate, load_snapshot, table

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def compare_metrics(actual, expected):
    for name, value in actual.items():
        if not np.isclose(value, expected[name], rtol=0, atol=1e-12):
            raise ValueError(f"Kayıtlı metrik uyuşmuyor: {name}")


def check_sql():
    invoices, first, last = load_invoices()
    with closing(sqlite3.connect(":memory:")) as connection:
        invoices.to_sql("invoices", connection, index=False)
        previous_target_end = None
        for split, cutoff in SNAPSHOTS.items():
            windows = make_windows(cutoff, first, last)
            if previous_target_end is not None:
                assert previous_target_end <= windows["cutoff"]
            previous_target_end = windows["target_end"]
            features, labels = create_snapshot(connection, windows)
            stored_features = pd.read_csv(DATA_DIR / f"{split}_features.csv").drop(columns="snapshot_date")
            stored_labels = pd.read_csv(DATA_DIR / f"{split}_labels.csv").drop(columns="snapshot_date")
            pd.testing.assert_frame_equal(features, stored_features, check_dtype=False, rtol=1e-12, atol=1e-9)
            pd.testing.assert_frame_equal(labels, stored_labels, check_dtype=False)
    database = DATA_DIR / "customer_analytics.sqlite"
    with closing(sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)) as connection:
        for split in SNAPSHOTS:
            for kind in ["features", "labels"]:
                stored = pd.read_sql_query(f"SELECT * FROM {split}_{kind}", connection)
                exported = pd.read_csv(DATA_DIR / f"{split}_{kind}.csv")
                pd.testing.assert_frame_equal(stored, exported, check_dtype=False, rtol=1e-12, atol=1e-9)
    return "Üç dönemin tüm SQL özellik/etiket satırları CSV ve SQLite ile eşleşti; hedef pencereleri çakışmıyor."


def check_models():
    baseline = read_json(ROOT / "artifacts" / "baseline_metadata.json")
    comparison = read_json(ROOT / "artifacts" / "model_comparison_metadata.json")
    logistic = joblib.load(ROOT / "artifacts" / "logistic_baseline.joblib")
    forest = joblib.load(ROOT / "artifacts" / "random_forest.joblib")
    X_train, y_train, _ = load_snapshot("train")
    X_val, y_val, val_keys = load_snapshot("validation")
    X_test, y_test, test_keys = load_snapshot("test")
    np.testing.assert_allclose(logistic.named_steps["scaler"].mean_, X_train.mean(), rtol=0, atol=1e-10)
    assert logistic.named_steps["scaler"].n_samples_seen_ == len(X_train)
    assert baseline["features"] == comparison["features"] == FEATURES
    assert select_model(comparison["validation_metrics"]) == comparison["selected_model"]
    assert comparison["selected_threshold"] == comparison["thresholds"][comparison["selected_model"]]
    assert comparison["test_used_for_selection"] is False
    validation_predictions = pd.read_csv(DATA_DIR / "validation_baseline_predictions.csv")
    pd.testing.assert_frame_equal(val_keys, validation_predictions[val_keys.columns])
    np.testing.assert_array_equal(y_val, validation_predictions["actual_no_purchase_90d"])
    val_probabilities = logistic.predict_proba(X_val)[:, 1]
    np.testing.assert_allclose(val_probabilities, validation_predictions["risk_score"], rtol=0, atol=1e-12)
    np.testing.assert_array_equal((val_probabilities >= baseline["threshold"]).astype(int), validation_predictions["predicted_no_purchase_90d"])
    baseline_scores = {
        "majority_validation": evaluate(y_val, np.full(len(y_val), y_train.mean()), np.full(len(y_val), int(y_train.mean() > .5))),
        "logistic_train_0.5": evaluate(y_train, logistic.predict_proba(X_train)[:, 1], logistic.predict(X_train)),
        "logistic_validation_0.5": evaluate(y_val, val_probabilities, (val_probabilities >= .5).astype(int)),
        "logistic_validation_selected": evaluate(y_val, val_probabilities, (val_probabilities >= baseline["threshold"]).astype(int)),
    }
    for name, score in baseline_scores.items():
        compare_metrics(score, baseline["metrics"][name])
    expected_table = table(["Model/bölüm", "AP", "ROC-AUC", "Precision", "Recall", "F1", "Accuracy"], [
        (name, *[f"{metrics[key]:.4f}" for key in ["average_precision", "roc_auc", "precision", "recall", "f1", "accuracy"]])
        for name, metrics in baseline_scores.items()])
    assert expected_table in (ROOT / "reports" / "baseline_model.md").read_text(encoding="utf-8")
    saved = pd.read_csv(DATA_DIR / "test_model_predictions.csv")
    pd.testing.assert_frame_equal(test_keys, saved[test_keys.columns])
    np.testing.assert_array_equal(y_test, saved["actual_no_purchase_90d"])
    test_scores = {}
    validation_scores = {}
    training_scores = {}
    for name in ["majority", "logistic", "random_forest"]:
        if name == "majority":
            probabilities = np.full(len(y_test), y_train.mean())
            predictions = np.full(len(y_test), int(y_train.mean() > .5))
            val_probabilities = np.full(len(y_val), y_train.mean())
            val_predictions = np.full(len(y_val), int(y_train.mean() > .5))
            train_probabilities = np.full(len(y_train), y_train.mean())
            train_predictions = np.full(len(y_train), int(y_train.mean() > .5))
        else:
            model = logistic if name == "logistic" else forest
            probabilities = model.predict_proba(X_test)[:, 1]
            predictions = (probabilities >= comparison["thresholds"][name]).astype(int)
            val_probabilities = model.predict_proba(X_val)[:, 1]
            val_predictions = (val_probabilities >= comparison["thresholds"][name]).astype(int)
            # Yalnızca kayıtlı validation kararını yeniden üret; yeni eşik denemesi yok.
            threshold, _ = choose_threshold(y_val, val_probabilities)
            assert threshold == comparison["thresholds"][name]
            train_probabilities = model.predict_proba(X_train)[:, 1]
            train_predictions = (train_probabilities >= comparison["thresholds"][name]).astype(int)
        np.testing.assert_allclose(probabilities, saved[f"{name}_risk_score"], rtol=0, atol=1e-12)
        np.testing.assert_array_equal(predictions, saved[f"{name}_prediction"])
        test_scores[name] = evaluate(y_test, probabilities, predictions)
        validation_scores[name] = evaluate(y_val, val_probabilities, val_predictions)
        training_scores[name] = evaluate(y_train, train_probabilities, train_predictions)
        compare_metrics(test_scores[name], comparison["test_metrics"][name])
        compare_metrics(validation_scores[name], comparison["validation_metrics"][name])
    report = (ROOT / "reports" / "model_comparison.md").read_text(encoding="utf-8")
    assert metrics_table(test_scores, comparison["thresholds"]) in report
    assert metrics_table(validation_scores, comparison["thresholds"]) in report
    assert metrics_table(training_scores, comparison["thresholds"]) in report
    selected = comparison["selected_model"]
    matrix = test_scores[selected]
    assert table(["Gerçek / tahmin", "0", "1"], [("0: alışveriş yaptı", matrix["tn"], matrix["fp"]),
                                                   ("1: alışveriş yapmadı", matrix["fn"], matrix["tp"])]) in report
    selected_model = joblib.load(ROOT / "artifacts" / "selected_model.joblib")
    np.testing.assert_allclose(selected_model.predict_proba(X_test)[:, 1], saved[f"{selected}_risk_score"], atol=1e-12)
    return "Kayıtlı olasılıklar, eşikler, AP/F1/precision/recall ve hata matrisleri yeniden hesaplandı: tümü eşleşti. Model eğitilmedi veya ayarlanmadı."


def check_dependencies():
    count = 0
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8-sig").splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        if version(name) != expected:
            raise ValueError(f"requirements/ortam sürümü farklı: {name}")
        count += 1
    return f"requirements.txt içindeki {count} paket sürümü mevcut ortamla bire bir eşleşti."


def check_rfm():
    train = pd.read_csv(DATA_DIR / "train_features.csv")
    thresholds = fit_thresholds(train)
    config = read_json(ROOT / "configs" / "rfm_thresholds.json")
    assert config["fit_split"] == "train"
    for column, edges in thresholds.items():
        np.testing.assert_allclose(edges, config["thresholds"][column], rtol=0, atol=1e-10)
    report = (ROOT / "reports" / "rfm_segments.md").read_text(encoding="utf-8")
    for split in SNAPSHOTS:
        features = pd.read_csv(DATA_DIR / f"{split}_features.csv")
        expected = assign_segments(features, thresholds)
        stored = pd.read_csv(DATA_DIR / f"{split}_rfm.csv", dtype={"rfm_code": str})
        pd.testing.assert_frame_equal(expected, stored, check_dtype=False, rtol=1e-12, atol=1e-9)
        summary = pd.read_csv(DATA_DIR / f"{split}_rfm_summary.csv").set_index("segment")
        counts = expected.groupby("segment").size()
        assert summary["customer_count"].sum() == len(features)
        for segment, count in counts.items():
            assert summary.loc[segment, "customer_count"] == count
        for segment, group in expected.groupby("segment"):
            assert np.isclose(summary.loc[segment, "median_recency_days"], group["recency_days"].median())
            assert np.isclose(summary.loc[segment, "median_frequency"], group["frequency_180d"].median())
            assert np.isclose(summary.loc[segment, "median_monetary_gbp"], group["monetary_180d_gbp"].median())
        if split != "test":
            labels = pd.read_csv(DATA_DIR / f"{split}_labels.csv")
            joined = expected.merge(labels, on=["snapshot_date", "customer_id"], validate="one_to_one")
            observed = joined.groupby("segment")["no_purchase_90d"].agg(["count", "sum", "mean"]).reindex(SEGMENTS)
            rows = []
            for segment, row in observed.iterrows():
                rows.append((segment, f"{int(row['sum'])}/{int(row['count'])}", f"{row['mean']:.2%}"))
            assert markdown_table(["Segment", "Alışveriş yapmayan / toplam", "Oran"], rows) in report
    return "RFM eğitim eşikleri, üç dönemin tüm puan/segmentleri ve segment müşteri sayıları eşleşti."


def check_git_candidates():
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    candidates = sorted(set(result.stdout.splitlines()))
    forbidden_suffixes = {".csv", ".xlsx", ".sqlite", ".db", ".joblib", ".pem", ".key", ".pkl"}
    patterns = {"özel anahtar": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                "AWS erişim anahtarı": r"(?:AKIA|ASIA)[A-Z0-9]{16}",
                "GitHub token": r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
                "API anahtarı": r"sk-[A-Za-z0-9_-]{30,}"}
    for name in candidates:
        path = Path(name)
        if path.parts[0] in {"data", "artifacts", ".venv", "secrets", ".aws", ".ssh"} or path.suffix in forbidden_suffixes:
            raise ValueError(f"Git adayı yerel/hassas dosya içeriyor: {name}")
        if path.name.startswith(".env") and path.name != ".env.example":
            raise ValueError("Git adaylarında .env dosyası var; içerik gösterilmedi.")
        content = (ROOT / path).read_text(encoding="utf-8-sig")
        for category, pattern in patterns.items():
            if re.search(pattern, content):
                raise ValueError(f"Olası {category}: {name}; eşleşen değer gösterilmedi.")
    ignored = [".env", ".env.local", ".aws/credentials", ".venv/Scripts/python.exe",
               "data/raw/online_retail_II.xlsx", "data/processed/train_features.csv",
               "data/processed/customer_analytics.sqlite", "artifacts/selected_model.joblib"]
    for name in ignored:
        result = subprocess.run(["git", "check-ignore", "--quiet", "--no-index", name], cwd=ROOT)
        if result.returncode != 0:
            raise ValueError(f"Beklenen dışlama kuralı yok: {name}")
    return candidates


def main():
    metadata = read_json(ROOT / "data" / "raw" / "download_metadata.json")
    with (ROOT / "data" / "raw" / "online_retail_II.xlsx").open("rb") as source:
        assert hashlib.file_digest(source, "sha256").hexdigest() == metadata["workbook_sha256"]
    checks = [check_sql(), check_rfm(), check_models(), check_dependencies()]
    candidates = check_git_candidates()
    checks.append(f"{len(candidates)} Git adayı tarandı; tanınan anahtar kalıbı bulunmadı. Yerel veri/model/ortam dosyaları adaylarda yok.")
    report = ["# Yayımlama öncesi çıktı kontrolü",
              "Bu kontrol mevcut sonuçların tutarlılığını doğrular; yeni test deneyi "
              "veya model seçimi değildir. Ham dosya SHA-256 kayıtla eşleşti."]
    report += [f"- {message}" for message in checks]
    report += ["\n## GitHub'a eklenecek mevcut dosyalar", "\n".join(f"- `{name}`" for name in candidates),
               "\nAnahtar taraması belirli kalıplarla sınırlıdır; her gizli değer "
               "türünü tespit ettiğine dair garanti değildir. Dosya içerikleri "
               "kontrolde ifşa edilmez. Commit/push/depo oluşturulmadı."]
    report_path = ROOT / "reports" / "output_verification.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    for message in checks:
        print(message)


if __name__ == "__main__":
    main()
