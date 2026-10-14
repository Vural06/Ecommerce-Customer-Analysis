"""Tekrar/filtre etkileri, dağılımlar ve zaman değişimi; ham veri korunur."""
from importlib import import_module
from pathlib import Path
import math
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "exercises"))
# Numaralı alıştırmanın mevcut kurallarını kullan; ikinci bir temizleme kuralı oluşturma.
summary_code = import_module("02_fatura_ve_musteri_ozeti")


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(map(str, row)) + " |")
    return "\n".join(lines)


def describe(name, values):
    stats = values.describe(percentiles=[.25, .5, .75, .95, .99])
    return [f"### {name}", table(["İstatistik", "Değer"], [(key, f"{value:.4f}") for key, value in stats.items()])]


def filter_steps(frame):
    """Ayrık elenme sayıları: her satır ilk başarısız olduğu adımda sayılır."""
    invoice = frame["Invoice"].astype("string").str.strip()
    rules = [
        ("Müşteri kimliği dolu", frame["Customer ID"].notna()),
        ("Fatura kimliği dolu/boşluk değil", invoice.notna() & invoice.ne("").fillna(False)),
        ("C/c iptal faturası değil", ~invoice.str.upper().str.startswith("C", na=False)),
        ("Quantity > 0", frame["Quantity"].gt(0)),
        ("Price > 0", frame["Price"].gt(0)),
    ]
    keep = pd.Series(True, index=frame.index)
    rows = [("Örtüşme sonrası girdi", len(frame), 0)]
    for name, valid in rules:
        before = int(keep.sum())
        keep = keep & valid
        rows.append((name, int(keep.sum()), before - int(keep.sum())))
    assert sum(row[2] for row in rows) + int(keep.sum()) == len(frame)
    return frame.loc[keep].copy(), rows


def main():
    raw_path = ROOT / "data" / "raw" / "online_retail_II.xlsx"
    before_hash = summary_code.file_hash(raw_path)
    with pd.ExcelFile(raw_path, engine="openpyxl") as workbook:
        frames = []
        for name in workbook.sheet_names:
            print(f"EDA için okunuyor: {name}", flush=True)
            frames.append(pd.read_excel(workbook, sheet_name=name))
    if len(frames) != 2:
        raise ValueError("İki çalışma sayfası bekleniyor.")
    combined, overlap_count = summary_code.combine_without_sheet_overlap(*frames)
    sales, steps = filter_steps(combined)
    invoices, customers, _ = summary_code.build_summaries(combined)
    # Önceki üretimin değişmediğini sayılar ve tutarlarla karşılaştır.
    saved_invoices = pd.read_csv(ROOT / "data" / "processed" / "combined_invoices.csv")
    saved_customers = pd.read_csv(ROOT / "data" / "processed" / "combined_customers.csv")
    assert len(invoices) == len(saved_invoices) and len(customers) == len(saved_customers)
    assert len(sales) == int(saved_invoices["line_count"].sum())
    assert math.isclose(invoices["invoice_amount_gbp"].sum(), saved_invoices["invoice_amount_gbp"].sum(), abs_tol=1e-6)
    report = ["# Veri kalitesi ve keşifsel analiz", "## Kapsam",
              "Tüm dönem betimsel analizdir; sonuçlar model ayarı veya test skorunu "
              "iyileştirmek için kullanılmadı. Ham Excel değişmez. Müşteri kimlikleri "
              "ve fatura kayıtları bu raporda yayımlanmaz.",
              "## Kayıt akışı", f"Ham sayfa toplamı: {sum(len(frame) for frame in frames)}. "
              f"Sayfalar arası bire bir eşleşen kopya: {overlap_count}. "
              "Sonraki tablo örtüşme sonrası girdiyle başlar; elenen sayılar adım "
              "sırasına bağlı ve birbirinden ayrıdır. İptal sayısı gibi bağımsız "
              "ham kontroller için ilk profil raporuna bakın.",
              table(["Adım", "Kalan satır", "Bu adımda elenen"], steps),
              f"Sonuç: {len(sales)} ürün satırı, {len(invoices)} fatura, {len(customers)} müşteri. "
              "Sayım/tutarlar önceki kayıtlı özetlerle uyuştu; model girdisi değişmedi.",
              "## İptal, iade ve değer kuralları",
              "C/c faturalar alışveriş evreninden çıkarılır. Negatif miktarlar iade "
              "veya düzeltme olabilir; hata olarak adlandırılmaz. Sıfır miktar "
              "alışveriş hacmi oluşturmaz. Negatif fiyat düzeltme olabilir; sıfır "
              "fiyat ücretsiz ürün/eksik fiyat olabilir. Pozitif fiyat/miktar koşulu "
              "bu ilk sürümün ücretli alışveriş tanımıdır. Bu kayıtların tamamı ham "
              "dosyada kalır; satışlarla iadeler eşleştirilip netleştirilmez. "
              "Eksik müşteri kimliği doldurulmaz; müşteriye ait geçmiş kurulamıyor. "
              "Açıklama eksikleri satış kimliği/tutarı hesaplarına engel olmadığından "
              "tek başına eleme nedeni değildir."]
    duplicate = sales.duplicated(subset=summary_code.COLUMNS)
    duplicate_amount = float((sales.loc[duplicate, "Quantity"] * sales.loc[duplicate, "Price"]).sum())
    total_amount = float(invoices["invoice_amount_gbp"].sum())
    duplicate_invoices = sales.loc[duplicate, "Invoice"].nunique()
    report += ["## Sayfa içi tekrar kararı", table(["Ölçüm", "Değer"], [
        ("Örtüşme sonrası tüm satırlardaki fazla tam kopya", int(combined.duplicated().sum())),
        ("Geçerli ürün satırlarındaki fazla tam kopya", int(duplicate.sum())),
        ("Bu kopyalardan etkilenen benzersiz fatura", duplicate_invoices),
        ("Bu kopyalardan etkilenen müşteri", sales.loc[duplicate, "Customer ID"].nunique()),
        ("Kopyaların brüt tutara katkısı (GBP)", f"{duplicate_amount:.2f}"),
        ("Toplam brüt tutardaki payı", f"{duplicate_amount / total_amount:.4%}"),
        ("Hepsi çıkarılsaydı ürün satırı (duyarlılık)", len(sales) - int(duplicate.sum())),
        ("Hepsi çıkarılsaydı brüt tutar (GBP, duyarlılık)", f"{total_amount - duplicate_amount:.2f}")]),
        "Bir faturada aynı ürünün ayrı kalemlere bölünmesi mümkün; kaynakta benzersiz "
        "satır kimliği bulunmuyor. Bu nedenle aynı sayfa içindeki eşit kalemlerin "
        "hatalı olup olmadığı kesinleşmiyor. Koruma kararı uygulanır. Yukarıdaki "
        "silme senaryosu yalnızca tutar hassasiyetini gösterir; yeni temizlenmiş "
        "veri veya model üretilmedi. Aynı tam kopyaları kaldırmak benzersiz "
        "müşteri/fatura sayılarını değiştirmez, miktar ve tutarı değiştirir.",
        "## Dağılımlar"]
    for name, values in [
        ("Fatura brüt tutarı (GBP)", invoices["invoice_amount_gbp"]),
        ("Fatura ürün miktarı", invoices["total_quantity"]),
        ("Müşteri başına benzersiz fatura", customers["purchase_invoice_count"]),
        ("Müşteri başına brüt harcama (GBP)", customers["gross_purchase_amount_gbp"]),
    ]:
        report += describe(name, values)
    top_count = max(1, math.ceil(len(customers) * .01))
    top_share = customers["gross_purchase_amount_gbp"].nlargest(top_count).sum() / total_amount
    report.append(f"En yüksek brüt harcamaya sahip yaklaşık %1'lik grup ({top_count} müşteri), "
                  f"toplam brüt tutarın %{top_share*100:.2f}'ini oluşturuyor. "
                  "Üst kuyruk otomatik veri hatası değildir; UCI kaynağı toptan alıcıların "
                  "bulunduğunu belirtir. Büyük tutarlar modele etki edebilir.")
    ordered = invoices.sort_values(["Customer ID", "invoice_last_line_date"]).copy()
    gaps = ordered.groupby("Customer ID")["invoice_last_line_date"].diff().dt.total_seconds() / 86400
    gaps = gaps.dropna()
    assert gaps.ge(0).all()
    report += ["## Alışveriş aralıkları",
               "Müşterinin ardışık farklı faturalarının son kalem zamanları arasındaki "
               "gün farkı hesaplandı. İlk fatura aralık üretmez. Aynı anda farklı "
               "faturalar varsa fark sıfır olabilir. Özet her müşteriye eşit ağırlık "
               "vermez; sık alışveriş yapanlar daha fazla aralık üretir. Son faturadan "
               "veri sonuna kadarki süre aralık değildir ve sağdan sansürlüdür.",
               f"Aralık sayısı: {len(gaps)}; sıfır günlük aralık: {int(gaps.eq(0).sum())}."]
    report += describe("Ardışık fatura aralığı (gün)", gaps)
    invoice_months = invoices.copy()
    invoice_months["month"] = invoice_months["invoice_last_line_date"].dt.to_period("M").astype(str)
    monthly = invoice_months.groupby("month").agg(
        invoice_count=("Invoice", "nunique"), customer_count=("Customer ID", "nunique"),
        amount_gbp=("invoice_amount_gbp", "sum"))
    report += ["## Aylık değişim",
               "Fatura son kalem tarihinin ayına atanır. Aylık müşteri sayıları "
               "toplanarak tüm dönem müşteri sayısı elde edilmez; müşteriler aylar "
               "arasında tekrar bulunur. Aralık 2011 yalnızca 9 Aralık'a kadar "
               "gözlenmiştir; önceki tam aylarla hacim karşılaştırması yapılmaz.",
               table(["Ay", "Fatura", "Müşteri", "Brüt tutar GBP", "Kapsam"], [
                   (month, int(row.invoice_count), int(row.customer_count), f"{row.amount_gbp:.2f}",
                    "Kısmi ay: 1–9 Aralık" if month == "2011-12" else "Gözlenen ay")
                   for month, row in monthly.iterrows()])]
    assert monthly["invoice_count"].sum() == len(invoices)
    assert math.isclose(monthly["amount_gbp"].sum(), total_amount, abs_tol=1e-6)
    full_months = monthly.drop(index="2011-12", errors="ignore")
    peak = full_months["invoice_count"].idxmax()
    report.append(f"Kısmi son ay hariç, en çok geçerli fatura gözlenen ay {peak}: "
                  f"{int(full_months.loc[peak, 'invoice_count'])} fatura. "
                  "Aylık hareket mevsimsellik hipotezi üretir; yalnızca iki yıllık "
                  "veriyle kalıcı mevsimsellik veya kampanya etkisi kanıtlanmaz.")
    training_start = pd.Timestamp("2010-07-05")
    training_end = pd.Timestamp("2011-01-01")
    training_invoices = invoices.loc[invoices["invoice_last_line_date"].ge(training_start)
                                    & invoices["invoice_last_line_date"].lt(training_end)]
    outlier_rows = []
    for column in ["invoice_amount_gbp", "total_quantity"]:
        q1, q3 = training_invoices[column].quantile([.25, .75])
        upper = q3 + 1.5 * (q3 - q1)
        flagged = invoices[column].gt(upper)
        amount_share = invoices.loc[flagged, "invoice_amount_gbp"].sum() / total_amount
        outlier_rows.append((column, f"{upper:.2f}", int(flagged.sum()), f"{flagged.mean():.2%}", f"{amount_share:.2%}"))
    report += ["## Aykırı değer kararı",
               "Tanısal üst sınır: Q3 + 1,5 × IQR. Eşikler yalnızca eğitim gözlem "
               "penceresindeki faturalarla hesaplandı. Tablodaki iki işaretleme "
               "örtüşebilir; sayılar ve tutar payları toplanmaz. Bunlar model "
               "ön işleme eşikleri değildir; kesme, winsorization veya eleme uygulanmadı.",
               table(["Alan", "Train IQR üst sınırı", "Tüm dönemde işaretli fatura", "Fatura payı", "Brüt tutar payı"], outlier_rows),
               "Büyük miktar/tutar tek başına yanlış değildir. İlk sürümde koruyoruz; "
               "StandardScaler aykırı değerlere dayanıklı değildir ve lojistik "
               "regresyon bundan etkilenebilir. Test görülmüş olduğundan bu analiz "
               "üzerinden özellik/model ayarı değiştirilmedi. Farklı dönüşümler "
               "ancak yeni bir değerlendirme tasarımıyla incelenebilir.",
               "## Tutarlılık",
               "Filtrelerde elenen + kalan = örtüşme sonrası girdi. Ürün kalemi "
               "sayısı kayıtlı fatura line_count toplamına eşit. Fatura/müşteri "
               "sayıları ve tutarlar mevcut CSV'lerle eşleşti. Aylık fatura ve "
               "tutar toplamları tüm dönemle uyuştu. Ham dosya hash'i değişmedi."]
    assert summary_code.file_hash(raw_path) == before_hash
    report_path = ROOT / "reports" / "data_quality_eda.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    print(f"EDA raporu: {report_path}", flush=True)


if __name__ == "__main__":
    main()
