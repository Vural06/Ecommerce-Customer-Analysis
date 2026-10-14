"""İki faturası olan bir eğitim müşterisini adım adım SQL ile karşılaştır."""
from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd

from build_customer_features import load_invoices, make_windows, create_snapshot
from train_baseline import table

ROOT = Path(__file__).resolve().parents[1]


def main():
    invoices, first, last = load_invoices()
    windows = make_windows("2011-01-01", first, last)
    with closing(sqlite3.connect(":memory:")) as connection:
        invoices.to_sql("invoices", connection, index=False)
        features, _ = create_snapshot(connection, windows)
    customer = features.loc[features["frequency_180d"].eq(2)].sort_values("customer_id").iloc[0]
    history = invoices.loc[invoices["customer_id"].eq(customer["customer_id"])
                           & invoices["event_date"].ge(windows["observation_start"])
                           & invoices["event_date"].lt(windows["cutoff"])].sort_values("event_date")
    cutoff = pd.Timestamp(windows["cutoff"])
    elapsed = cutoff - pd.Timestamp(history["event_date"].max())
    manual = {"recency_days": elapsed.days,
              "frequency_180d": history["invoice_id"].nunique(),
              "monetary_180d_gbp": history["amount_gbp"].sum(),
              "average_invoice_amount_gbp": history["amount_gbp"].sum() / len(history),
              "quantity_180d": history["total_quantity"].sum()}
    for column, value in manual.items():
        assert abs(value - customer[column]) < 1e-6
    report = ["# Eğitim müşterisi: elle özellik hesabı", "## Kapsam",
              "Gerçek eğitim verisinden iki faturası olan bir müşteri seçildi. "
              "Yayımlanan örnekte müşteri adı `Örnek A`, faturalar `Fatura A/B` "
              "olarak takma adlandırıldı. Özgün kimlik eşleştirmesi yalnızca "
              "Git dışındaki `data/processed/customer_example_private.md` dosyasındadır.",
              f"Tahmin tarihi: **{windows['cutoff']}**. Kullanılabilen geçmiş: "
              f"**{windows['observation_start']} ≤ fatura son kalem zamanı < {windows['cutoff']}**. "
              "Müşteri bilgisi tahmin tarihinden sonra tamamlanan faturalarla zenginleştirilmez.",
              "## Kullanılan geçmiş faturalar",
              table(["Takma fatura", "Son kalem zamanı", "Brüt tutar GBP", "Ürün miktarı"], [
                  (f"Fatura {chr(65 + index)}", row.event_date, f"{row.amount_gbp:.2f}", int(row.total_quantity))
                  for index, row in enumerate(history.itertuples())]),
              "Fatura tutarı önceki aşamada geçerli ürün kalemlerinin Quantity × Price "
              "toplamıdır. Burada fatura başına tek satır var; aynı faturadaki ürünler "
              "alışveriş sayısını artırmaz. İadeler brüt tutardan düşülmemiştir.",
              "## Hesap adımları",
              f"1. **Recency:** tahmin tarihi − son fatura zamanı = {elapsed.days} gün "
              f"{elapsed.components.hours:02d}:{elapsed.components.minutes:02d}:{elapsed.components.seconds:02d}. "
              f"SQL tam gün kısmını alır: **{manual['recency_days']} gün**. "
              "Saat farkını yukarı yuvarlamıyoruz.",
              f"2. **Frequency:** iki farklı fatura var; COUNT(DISTINCT invoice_id) = **{manual['frequency_180d']}**.",
              "3. **Monetary:** " + " + ".join(f"{value:.2f}" for value in history["amount_gbp"]) +
              f" = **{manual['monetary_180d_gbp']:.2f} GBP**.",
              f"4. **Ortalama fatura tutarı:** {manual['monetary_180d_gbp']:.2f} / "
              f"{manual['frequency_180d']} = **{manual['average_invoice_amount_gbp']:.2f} GBP**.",
              "5. **Miktar:** " + " + ".join(str(int(value)) for value in history["total_quantity"]) +
              f" = **{int(manual['quantity_180d'])} ürün birimi**; bu fatura sayısı değildir.",
              "## SQL ile karşılaştırma", table(["Özellik", "Elle hesap", "SQL", "Sonuç"], [
                  (column, f"{value:.4f}", f"{customer[column]:.4f}", "Eşleşti") for column, value in manual.items()]),
              "SQL: `sql/customer_features.sql`. Aynı tahmin/gözlem sınırlarıyla "
              "hesaplanan beş değer SQL çıktısıyla eşleşti. Gelecek faturalar "
              "bu hesapta yoktur; hedef örneğe eklenmedi.",
              "## Senin incelemen", "Bu örnek hazırlanmış ve otomatik kontrol edilmiştir. "
              "Öğrenciyle elle inceleme maddesi sen inceleyene kadar TODO'da açık kalır. "
              "Mülakatta ürün kalemi/fatura farkını, sağ sınırın neden hariç olduğunu "
              "ve brüt harcamanın net gelir olmadığını açıklayabilmelisin."]
    public_path = ROOT / "docs" / "customer_feature_example.md"
    public_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    private_path = ROOT / "data" / "processed" / "customer_example_private.md"
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_text(f"Örnek A müşteri kimliği: {int(customer['customer_id'])}\n" +
                           "\n".join(f"Fatura {chr(65 + i)}: {value}" for i, value in enumerate(history["invoice_id"])), encoding="utf-8")
    print("Öğrenme örneğinin beş hesabı SQL ile eşleşti; özgün kimlikler terminalde gösterilmedi.")


if __name__ == "__main__":
    main()
