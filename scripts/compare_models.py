"""Bir Random Forest alternatifi; validation seçimi sonrası sabit test değerlendirmesi."""
from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier

from train_baseline import (FEATURES, choose_threshold, evaluate, load_snapshot,
                            make_logistic_model, table)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DATA_DIR = ROOT / "data" / "processed"


def make_random_forest():
    # Tek, küçük ve sabit ayar seti: geniş hiperparametre araması yok.
    # Derinlik ve yaprak boyutu eğitim verisini ezberleme eğilimini sınırlar.
    return RandomForestClassifier(n_estimators=100, max_depth=5,
                                  min_samples_leaf=20, random_state=42, n_jobs=1)


def select_model(validation_scores):
    # Öncelik risk sıralaması (AP); eşitlikte F1, yine eşitse basit lojistik model.
    logistic = validation_scores["logistic"]
    forest = validation_scores["random_forest"]
    logistic_scores = (logistic["average_precision"], logistic["f1"])
    forest_scores = (forest["average_precision"], forest["f1"])
    if forest_scores > logistic_scores:
        return "random_forest"
    return "logistic"  # Tam eşitlikte basit modeli seç.


def metrics_table(scores, thresholds):
    return table(["Model", "Eşik", "AP", "ROC-AUC", "Precision", "Recall", "F1", "Accuracy"], [
        (name, thresholds.get(name, "Çoğunluk"), *[f"{result[column]:.4f}" for column in
            ["average_precision", "roc_auc", "precision", "recall", "f1", "accuracy"]])
        for name, result in scores.items()])


def main():
    X_train, y_train, train_keys = load_snapshot("train")
    X_val, y_val, val_keys = load_snapshot("validation")
    assert pd.to_datetime(train_keys["snapshot_date"]).max() < pd.to_datetime(val_keys["snapshot_date"]).min()
    models = {"majority": DummyClassifier(strategy="prior"),
              "logistic": make_logistic_model(), "random_forest": make_random_forest()}
    thresholds = {}
    validation_scores = {}
    train_scores = {}
    candidate_tables = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        val_probability = model.predict_proba(X_val)[:, 1]
        if name == "majority":
            train_prediction = model.predict(X_train)
            val_prediction = model.predict(X_val)
        else:
            threshold, candidates = choose_threshold(y_val, val_probability)
            thresholds[name] = threshold
            candidate_tables += [f"### {name}", table(["Eşik", "Precision", "Recall", "F1"], [
                (f"{row.threshold:.1f}", f"{row.precision:.4f}", f"{row.recall:.4f}", f"{row.f1:.4f}")
                for row in candidates.itertuples()])]
            train_prediction = (model.predict_proba(X_train)[:, 1] >= threshold).astype(int)
            val_prediction = (val_probability >= threshold).astype(int)
        train_scores[name] = evaluate(y_train, model.predict_proba(X_train)[:, 1], train_prediction)
        validation_scores[name] = evaluate(y_val, val_probability, val_prediction)
    selected_name = select_model(validation_scores)
    ARTIFACT_DIR.mkdir(exist_ok=True)
    # Karar önce kaydedilir. Test verisi ancak bundan sonra okunur.
    selection = {"selected_model": selected_name, "selected_threshold": thresholds[selected_name],
                 "features": FEATURES, "thresholds": thresholds,
                 "selection_rule": "validation AP, then F1, then logistic simplicity",
                 "forest_parameters": models["random_forest"].get_params(),
                 "validation_metrics": validation_scores, "test_used_for_selection": False,
                 "training_policy": "train only; no refit on validation"}
    selection_path = ARTIFACT_DIR / "model_comparison_metadata.json"
    selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    joblib.dump(models[selected_name], ARTIFACT_DIR / "selected_model.joblib")
    joblib.dump(models["random_forest"], ARTIFACT_DIR / "random_forest.joblib")
    print(f"Doğrulamada seçilen model: {selected_name}, eşik: {thresholds[selected_name]}", flush=True)

    X_test, y_test, test_keys = load_snapshot("test")
    assert pd.to_datetime(val_keys["snapshot_date"]).max() < pd.to_datetime(test_keys["snapshot_date"]).min()
    test_scores = {}
    predictions = test_keys.copy()
    predictions["actual_no_purchase_90d"] = y_test
    for name, model in models.items():
        probabilities = model.predict_proba(X_test)[:, 1]
        predicted = model.predict(X_test) if name == "majority" else (probabilities >= thresholds[name]).astype(int)
        test_scores[name] = evaluate(y_test, probabilities, predicted)
        predictions[f"{name}_risk_score"] = probabilities
        predictions[f"{name}_prediction"] = predicted
        print(f"Test {name}: AP={test_scores[name]['average_precision']:.4f}, F1={test_scores[name]['f1']:.4f}")
    predictions.to_csv(DATA_DIR / "test_model_predictions.csv", index=False)
    selection["test_metrics"] = test_scores
    selection["test_evaluated"] = True
    selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    result = test_scores[selected_name]
    errors = X_test.copy()
    errors["actual"] = y_test
    errors["prediction"] = predictions[f"{selected_name}_prediction"]
    error_rows = []
    for label, mask in [("Yanlış pozitif (alışveriş yaptı, riskli işaretlendi)", errors["actual"].eq(0) & errors["prediction"].eq(1)),
                        ("Yanlış negatif (alışveriş yapmadı, risksiz işaretlendi)", errors["actual"].eq(1) & errors["prediction"].eq(0))]:
        group = errors.loc[mask]
        error_rows.append((label, len(group), *[f"{group[col].median():.2f}" if len(group) else "—"
                          for col in ["recency_days", "frequency_180d", "monetary_180d_gbp"]]))
    report = ["# Alternatif model ve son zaman temelli değerlendirme",
              "## Kararlar",
              "Modeller: çoğunluk sınıfı referansı, StandardScaler + LogisticRegression "
              "ve tek bir RandomForestClassifier. Hepsi aynı beş SQL özelliğini ve "
              "aynı train/validation/test tarihlerini kullanır. Random Forest için "
              "100 ağaç, max_depth=5, min_samples_leaf=20, random_state=42; "
              "başka ayar denenmedi. Ağaç modeli ölçekleme gerektirmez.",
              "İki öğrenen modelin karar eşiği validation F1 ile 0,2–0,8 adaylarından seçilir. "
              "Model seçiminde birincil ölçüt validation average precision (AP), "
              "eşitlikte F1, yine eşitse daha basit lojistik regresyondur. "
              "Bu kurallar test dosyaları okunmadan uygulanıp kaydedilir. "
              "Validation üzerinde yeniden eğitim yapılmaz; tüm modeller yalnızca train'de öğrenir.",
              f"Veri büyüklükleri: train={len(X_train)}, validation={len(X_val)}, test={len(X_test)}. "
              f"Hedef=1 oranları: %{y_train.mean()*100:.2f}, %{y_val.mean()*100:.2f}, %{y_test.mean()*100:.2f}.",
              "## Eğitim (validation'da seçilen sabit eşiklerle)", metrics_table(train_scores, thresholds),
              "## Doğrulama", metrics_table(validation_scores, thresholds),
              f"Testten önce seçilen model: **{selected_name}**, karar eşiği **{thresholds[selected_name]}**. "
              "Eşik ve model seçimi aynı doğrulama verisinde yapıldığından doğrulama skorları iyimser olabilir.",
              "## Eşik adayları", *candidate_tables,
              "## Son test değerlendirmesi", metrics_table(test_scores, thresholds),
              "Test sonuçları yalnızca sabit modellerin raporlanması içindir; "
              "testte farklı model daha yüksek skor alsa bile seçim değiştirilmez. "
              "Bu test artık görülmüştür: sonraki değişikliklerde bağımsız, görülmemiş "
              "test olarak kullanılamaz. Betik tekrar çalıştırılırsa aynı sabit "
              "karşılaştırma yeniden üretilir; yeni bir bağımsız deney oluşmaz.",
              "## Seçilen modelin test hata matrisi",
              table(["Gerçek / tahmin", "0", "1"], [("0: alışveriş yaptı", result["tn"], result["fp"]),
                                                        ("1: alışveriş yapmadı", result["fn"], result["tp"])]),
              "## Hata grupları", table(["Grup", "Müşteri", "Medyan R (gün)", "Medyan F", "Medyan M (GBP)"], error_rows),
              "Hata medyanları tanısal betimlemedir; hata nedenini veya nedensel ilişkiyi kanıtlamaz. "
              "Bu tabloyla model yeniden ayarlanmadı. Bireysel müşteri bilgileri raporda yayımlanmaz.",
              "## Yorum ve sınırlılıklar",
              f"Random Forest ile lojistik regresyon arasındaki test AP farkı "
              f"{test_scores['random_forest']['average_precision'] - test_scores['logistic']['average_precision']:.4f}; "
              "bu küçük fark için istatistiksel üstünlük testi yapılmadı. "
              f"Seçilen modelin test precision değeri %{result['precision']*100:.2f}, "
              f"recall değeri %{result['recall']*100:.2f}. Bu eşik birçok "
              "alışveriş yapmayan müşteriyi yakalarken çok sayıda yanlış pozitif üretir.",
              "AP sıralama kalitesini, precision/recall/F1 sabit karar eşiğinin "
              "davranışını gösterir. AP, trapez PR-AUC ile aynı hesap değildir. "
              "Sabit risk puanlı çoğunluk referansının AP'si ilgili dönemin hedef oranına eşittir. "
              "Eğitim/doğrulama farkı genelleme sorununun bir işareti olabilir; "
              "dönemler farklı olduğu için farkın tamamı ezberlemeye bağlanamaz.",
              "Hedef oranları zamanla değişiyor. Tek test tarihi mevsimselliği veya "
              "kalıcı performansı ölçmez. Aynı müşteriler farklı dönemlerde bulunabilir; "
              "bu mevcut müşterilere tekrar tahmin yapma senaryosudur. İadeler "
              "netleştirilmedi, sayfa içi tekrarlar korundu ve olasılıklar "
              "kalibre edilmedi. Kampanya etkisi ölçülmedi. Bu sonuçlar üretim "
              "performansı veya kanıtlanmış iş kazancı değildir.",
              "## Çalıştırma ve yerel çıktılar",
              "`.venv\\Scripts\\python.exe scripts/compare_models.py`. "
              "Seçim bilgisi `artifacts/model_comparison_metadata.json`, model "
              "`artifacts/selected_model.joblib`, alternatif `artifacts/random_forest.joblib`, "
              "müşteri tahminleri `data/processed/test_model_predictions.csv`. Hepsi Git dışında tutulur."]
    report_path = ROOT / "reports" / "model_comparison.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
