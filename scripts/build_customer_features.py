"""SQL ile zamana bağlı müşteri özellikleri ve ayrı hedef tabloları üretir."""
from datetime import datetime, timedelta, timezone
from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "combined_invoices.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
OBSERVATION_DAYS = 180
TARGET_DAYS = 90
SNAPSHOTS = {"train": "2011-01-01", "validation": "2011-05-01", "test": "2011-09-01"}


def make_windows(cutoff_text, first_available, last_available):
    cutoff = pd.Timestamp(cutoff_text)
    start = cutoff - timedelta(days=OBSERVATION_DAYS)
    end = cutoff + timedelta(days=TARGET_DAYS)
    if start < first_available:
        raise ValueError("Gözlem döneminin tamamı veri kapsamında değil.")
    if end > last_available:
        raise ValueError("Hedef dönemi tamamlanmamış; bu tarihe etiket üretilemez.")
    return {"observation_start": start.strftime("%Y-%m-%d %H:%M:%S"),
            "cutoff": cutoff.strftime("%Y-%m-%d %H:%M:%S"),
            "target_end": end.strftime("%Y-%m-%d %H:%M:%S")}


def load_invoices():
    source = pd.read_csv(INPUT_PATH, dtype={"Invoice": "string"})
    required = ["Customer ID", "Invoice", "invoice_date", "invoice_last_line_date",
                "invoice_amount_gbp", "total_quantity"]
    if source[required].isna().any().any():
        raise ValueError("Fatura tablosunda gerekli alanlar eksik.")
    if not source["Customer ID"].mod(1).eq(0).all():
        raise ValueError("Müşteri kimlikleri tam sayı olmalı.")
    if source.duplicated(["Customer ID", "Invoice"]).any():
        raise ValueError("Müşteri/fatura anahtarı tekrarlı.")
    if source.groupby("Invoice")["Customer ID"].nunique().gt(1).any():
        raise ValueError("Bir fatura farklı müşterilere bağlı.")
    first_dates = pd.to_datetime(source["invoice_date"], errors="raise")
    event_dates = pd.to_datetime(source["invoice_last_line_date"], errors="raise")
    if not event_dates.ge(first_dates).all():
        raise ValueError("Son kalem zamanı ilk zamandan önce olamaz.")
    if not source["invoice_amount_gbp"].gt(0).all():
        raise ValueError("Alışveriş faturası tutarları pozitif olmalı.")
    invoices = pd.DataFrame({
        "customer_id": source["Customer ID"].astype("int64"),
        "invoice_id": source["Invoice"],
        "event_date": event_dates.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "amount_gbp": source["invoice_amount_gbp"],
        "total_quantity": source["total_quantity"],
    })
    return invoices, first_dates.min(), event_dates.max()


def create_snapshot(connection, windows):
    # SQL dosyaları koddan ayrı: sorguları mülakatta da okuyup açıklayabilirsin.
    feature_sql = (ROOT / "sql" / "customer_features.sql").read_text(encoding="utf-8")
    label_sql = (ROOT / "sql" / "customer_labels.sql").read_text(encoding="utf-8")
    features = pd.read_sql_query(feature_sql, connection, params=windows)
    features.to_sql("snapshot_features", connection, if_exists="replace", index=False)
    labels = pd.read_sql_query(label_sql, connection, params=windows)
    assert features["customer_id"].is_unique
    assert features["customer_id"].tolist() == labels["customer_id"].tolist()
    assert features["frequency_180d"].ge(1).all()
    assert features["recency_days"].between(0, OBSERVATION_DAYS).all()
    assert features["last_observed_purchase"].lt(windows["cutoff"]).all()
    assert labels["no_purchase_90d"].isin([0, 1]).all()
    assert labels["no_purchase_90d"].eq(labels["future_invoice_count"].eq(0).astype(int)).all()
    return features, labels


def check_against_pandas(invoices, features, labels, windows):
    # SQL sonucunu üç temsilî müşteride bağımsız pandas hesabıyla kontrol et.
    customer_ids = features["customer_id"].iloc[[0, len(features) // 2, -1]].unique()
    for customer_id in customer_ids:
        history = invoices.loc[
            invoices["customer_id"].eq(customer_id)
            & invoices["event_date"].ge(windows["observation_start"])
            & invoices["event_date"].lt(windows["cutoff"])]
        row = features.set_index("customer_id").loc[customer_id]
        assert row["frequency_180d"] == history["invoice_id"].nunique()
        assert abs(row["monetary_180d_gbp"] - history["amount_gbp"].sum()) < 1e-6
        days = (pd.Timestamp(windows["cutoff"]) - pd.Timestamp(history["event_date"].max())).days
        assert row["recency_days"] == days
        future = invoices.loc[invoices["customer_id"].eq(customer_id)
                              & invoices["event_date"].ge(windows["cutoff"])
                              & invoices["event_date"].lt(windows["target_end"])]
        assert labels.set_index("customer_id").loc[customer_id, "future_invoice_count"] == future["invoice_id"].nunique()


def main():
    invoices, first_available, last_available = load_invoices()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    id_sets = {}
    with closing(sqlite3.connect(":memory:")) as connection:
        invoices.to_sql("invoices", connection, index=False)
        for split, cutoff in SNAPSHOTS.items():
            windows = make_windows(cutoff, first_available, last_available)
            features, labels = create_snapshot(connection, windows)
            if features.empty:
                raise ValueError(f"{split}: müşteri bulunamadı.")
            check_against_pandas(invoices, features, labels, windows)
            features.insert(0, "snapshot_date", windows["cutoff"])
            labels.insert(0, "snapshot_date", windows["cutoff"])
            features.to_csv(OUTPUT_DIR / f"{split}_features.csv", index=False)
            labels.to_csv(OUTPUT_DIR / f"{split}_labels.csv", index=False)
            features.to_sql(f"{split}_features", connection, index=False)
            labels.to_sql(f"{split}_labels", connection, index=False)
            id_sets[split] = set(features["customer_id"])
            rows.append((split, windows, len(features), int(labels["no_purchase_90d"].sum()),
                         labels["no_purchase_90d"].mean()))
            print(f"{split}: {len(features)} müşteri, alışveriş yapmama oranı %{labels['no_purchase_90d'].mean()*100:.2f}")
        connection.execute("DROP TABLE snapshot_features")
        connection.commit()
        with closing(sqlite3.connect(OUTPUT_DIR / "customer_analytics.sqlite")) as destination:
            connection.backup(destination)
    report = ["# Zaman pencereleri ve SQL özellikleri",
              "Tanım ve kararlar: [Problem tanımı](../docs/problem_definition.md). "
              "Girdi: `data/processed/combined_invoices.csv`. SQL motoru SQLite "
              f"{sqlite3.sqlite_version}. Rapor üretimi (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}.",
              "Özellikler ve hedefler ayrı CSV/SQL tablolarında tutulur. "
              "Müşteri kimliği eşleştirme anahtarıdır; model girdisi olarak kullanılmayacak."]
    table = ["| Bölüm | Gözlem başlangıcı | Tahmin tarihi | Hedef sonu (hariç) | Müşteri | Hedef=1 | Hedef=1 oranı |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for split, windows, count, positives, rate in rows:
        table.append(f"| {split} | {windows['observation_start'][:10]} | {windows['cutoff'][:10]} | "
                      f"{windows['target_end'][:10]} | {count} | {positives} | {rate:.2%} |")
    report.append("\n".join(table))
    report += ["\n## Kontroller",
               "Üç dönemin hedef penceresi de veri sonundan önce tamamlanır. "
               "Müşteri anahtarları tekildir ve özellik/hedef tabloları eşleşir. "
               "Son alışveriş tarihi tahmin tarihinden küçüktür. Her dönemde üç "
               "müşterinin sıklık, harcama, recency ve hedef hesapları pandas ile doğrulandı.",
               f"Train/validation ortak müşterileri: {len(id_sets['train'] & id_sets['validation'])}. "
               f"Validation/test ortak müşterileri: {len(id_sets['validation'] & id_sets['test'])}. "
               "Aynı müşterinin farklı tarihlerde bulunması, mevcut müşteriye tekrar "
               "tahmin yapma kullanımına uygundur; yeni müşterilere genelleme testi değildir. "
               "Tek bir tarih örneği mevsimsel değişimleri tam ölçmez.",
               "Oranlar gerçek gözlenen etiket dağılımlarıdır; model başarısı veya "
               "kampanya kazancı değildir. Bu betik RFM değerlerini üretir; "
               "segment puanları ve model karşılaştırması ayrı betiklerde yapılır.",
               "\n## Yerel çıktılar",
               "`data/processed/{train,validation,test}_features.csv`, aynı bölümlerin "
               "`*_labels.csv` dosyaları ve `customer_analytics.sqlite`. SQL dosyaları "
               "`sql/customer_features.sql` ve `sql/customer_labels.sql`. Veri çıktıları Git dışındadır."]
    report_path = ROOT / "reports" / "sql_features.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
