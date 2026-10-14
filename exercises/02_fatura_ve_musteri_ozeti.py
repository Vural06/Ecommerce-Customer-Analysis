"""İlk sayfa ve örtüşmesi giderilmiş birleşim için fatura/müşteri özetleri.

Ham dosya değişmez. Çıktılar Git dışındaki data/processed klasörüne yazılır.
"""
from pathlib import Path
import hashlib
import math

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
COLUMNS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate",
           "Price", "Customer ID", "Country"]


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def combine_without_sheet_overlap(first, second):
    """Aynı satırın sayfa içindeki çoklu kopyalarını koruyarak sayfaları birleştir.

    Bir kayıt ilk sayfada 2, ikinci sayfada 3 kez varsa birleşimde 3 kez kalır.
    cumcount her aynı kaydın kaçıncı kopyası olduğunu verir; dropna=False
    eksik hücreli kayıtların da eşleştirilmesini sağlar.
    """
    left = first.copy()
    right = second.copy()
    left["_occurrence"] = left.groupby(COLUMNS, dropna=False).cumcount()
    right["_occurrence"] = right.groupby(COLUMNS, dropna=False).cumcount()
    matched = right.merge(
        left[COLUMNS + ["_occurrence"]],
        on=COLUMNS + ["_occurrence"], how="left", indicator=True,
        validate="one_to_one", sort=False,
    )
    remaining = matched.loc[matched["_merge"].eq("left_only"), COLUMNS]
    removed = int(matched["_merge"].eq("both").sum())
    combined = pd.concat([first, remaining], ignore_index=True)
    assert len(combined) == len(first) + len(second) - removed
    return combined, removed


def build_summaries(frame):
    # Filtreler yeni bir tabloya uygulanır; girdi tablo korunur.
    invoice_text = frame["Invoice"].astype("string").str.strip()
    cancelled = invoice_text.str.upper().str.startswith("C", na=False)
    mask = (frame["Customer ID"].notna() & invoice_text.notna()
            & invoice_text.ne("").fillna(False) & ~cancelled
            & frame["Quantity"].gt(0) & frame["Price"].gt(0))
    sales = frame.loc[mask].copy()
    if sales.empty:
        raise ValueError("Geçerli alışveriş satırı yok.")
    if sales["InvoiceDate"].isna().any():
        raise ValueError("Geçerli satışta eksik tarih var; tarih kararı gerekli.")
    if sales.groupby("Invoice")["Customer ID"].nunique().gt(1).any():
        raise ValueError("Bir fatura birden fazla müşteriye bağlı; özet durduruldu.")

    # Her satırın brüt ürün tutarı: adet × birim fiyat (GBP).
    sales["line_amount_gbp"] = sales["Quantity"] * sales["Price"]
    if not sales["line_amount_gbp"].map(math.isfinite).all():
        raise ValueError("Sonlu olmayan satır tutarı bulundu.")

    # agg tek gruptan farklı özetler üretir. Fatura için iki kimlik birlikte kullanılır.
    invoices = sales.groupby(["Customer ID", "Invoice"], as_index=False).agg(
        invoice_date=("InvoiceDate", "min"),
        invoice_last_line_date=("InvoiceDate", "max"),
        distinct_timestamp_count=("InvoiceDate", "nunique"),
        invoice_amount_gbp=("line_amount_gbp", "sum"),
        line_count=("Invoice", "size"),
        total_quantity=("Quantity", "sum"),
    )
    # Bir müşteri için her fatura artık tek satırdır.
    customers = invoices.groupby("Customer ID", as_index=False).agg(
        purchase_invoice_count=("Invoice", "nunique"),
        gross_purchase_amount_gbp=("invoice_amount_gbp", "sum"),
        first_purchase_date=("invoice_date", "min"),
        last_purchase_date=("invoice_last_line_date", "max"),
    )

    assert len(invoices) == sales["Invoice"].nunique()
    assert customers["purchase_invoice_count"].sum() == len(invoices)
    assert invoices["line_count"].sum() == len(sales)
    assert len(customers) == sales["Customer ID"].nunique()
    line_total = float(sales["line_amount_gbp"].sum())
    assert math.isclose(line_total, invoices["invoice_amount_gbp"].sum(), rel_tol=1e-12, abs_tol=1e-6)
    assert math.isclose(line_total, customers["gross_purchase_amount_gbp"].sum(), rel_tol=1e-12, abs_tol=1e-6)

    # Bu fark yalnızca duyarlılık ölçümüdür; aynı sayfa tekrarları silinmez.
    without_exact_repeats = sales.drop_duplicates(subset=COLUMNS)
    duplicate_amount = line_total - float(without_exact_repeats["line_amount_gbp"].sum())
    metrics = [
        ("Girdi satırı", len(frame)),
        ("Ham girdi tam tekrarları (ilk kopya hariç)", int(frame.duplicated().sum())),
        ("Filtrelenmiş ürün satırı", len(sales)),
        ("Filtrelenmiş tam tekrar (korundu)", int(sales.duplicated(subset=COLUMNS).sum())),
        ("Benzersiz alışveriş faturası / özet satırı", len(invoices)),
        ("Birden fazla tarih/saat taşıyan fatura", int(invoices["distinct_timestamp_count"].gt(1).sum())),
        ("En az bir alışverişi olan müşteri", len(customers)),
        ("En az iki faturası olan müşteri", int(customers["purchase_invoice_count"].ge(2).sum())),
        ("Tekrar alışveriş oranı", f"{customers['purchase_invoice_count'].ge(2).mean():.4%}"),
        ("İlk alışveriş tarihi", invoices["invoice_date"].min()),
        ("Son alışveriş tarihi", invoices["invoice_last_line_date"].max()),
        ("Filtrelenmiş brüt ürün tutarı (GBP)", f"{line_total:.2f}"),
        ("Korunan tam tekrarların tutara katkısı (GBP)", f"{duplicate_amount:.2f}"),
    ]
    return invoices, customers, metrics


def main():
    before = file_hash(EXCEL_PATH)
    frames = []
    names = []
    with pd.ExcelFile(EXCEL_PATH, engine="openpyxl") as workbook:
        for name in workbook.sheet_names:
            print(f"Sayfa okunuyor: {name}", flush=True)
            frame = pd.read_excel(workbook, sheet_name=name)
            if list(frame.columns) != COLUMNS:
                raise ValueError(f"Beklenmeyen sütunlar: {name}")
            names.append(name)
            frames.append(frame)
    if len(frames) != 2:
        raise ValueError("Bu alıştırma iki sayfalı Online Retail II dosyası için yazıldı.")
    combined, removed = combine_without_sheet_overlap(*frames)
    print(f"Sayfalar arası eşleşen kopya çıkarıldı: {removed}", flush=True)
    report = [
        "# Fatura ve müşteri özetleri",
        "## Kapsam ve kararlar",
        f"Kaynak: `data/raw/online_retail_II.xlsx`. Sayfalar: {', '.join(names)}. "
        f"Ham dosya SHA-256: `{before}`. İlk sayfa ve iki sayfanın birleşimi ayrı özetlenir.",
        "Bir satır ürün kalemidir. Müşteri/fatura kimliği dolu, fatura C/c ile "
        "başlamayan, Quantity > 0 ve Price > 0 satırlar alışveriş olarak kullanılır. "
        "En az bir geçerli ürün satırı bulunan fatura sayılır. Filtrelenmiş bir "
        "faturanın tutarı yalnızca bu satırların toplamıdır; iadeler netleştirilmez.",
        f"Sayfalar arasındaki sekiz sütunu aynı kayıtlar kopya sırasıyla eşleştirildi; "
        f"ikinci sayfadan {removed} eşleşen satır çıkarıldı. Aynı kayıt için "
        "iki sayfadaki kopya sayılarının büyüğü korunur. Bu, kayıt örtüşmesi için "
        "açık bir çalışma varsayımıdır; eşit satırların tümünün hatalı olduğunu kanıtlamaz. "
        "Sayfa içi tekrarlar korunur; hepsini silmek meşru ürün kalemlerini de silebilir.",
        "Satır tutarı Quantity × Price; fatura tutarı bunun toplamıdır. Fatura "
        "Customer ID + Invoice ile gruplanır. Faturada farklı tarihler varsa en erken "
        "tarih başlangıç, en geç tarih son kalem zamanı olarak saklanır; zaman damgası "
        "sayısı ayrıca raporlanır. Müşterinin son alışverişi son kalem zamanından alınır. "
        "Bir fatura birden çok müşteriye bağlıysa betik hata verir.",
        "Müşteri tablosu alışveriş sayısı, brüt harcama, ilk ve son alışveriş "
        "tarihini içerir. İptal/iade düşülmediği ve sayfa içi tekrarlar korunduğu için "
        "tutar net gelir veya kesin müşteri değeri değildir. Tekrarların toplam "
        "tutara katkısı duyarlılık ölçümü olarak gösterilir; tekrarları silme kararı değildir.",
        "Bunlar tüm gözlem dönemine ait betimsel özetlerdir; tahmin tarihinde "
        "bilinen özellikler olarak doğrudan modele verilemez. Zamana bağlı SQL "
        "özellikleri ve RFM ayrı betiklerde üretilir; bu betik yalnızca fatura/müşteri özetidir.",
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for label, frame in [("first_sheet", frames[0]), ("combined", combined)]:
        print(f"Özetleniyor: {label}", flush=True)
        invoices, customers, metrics = build_summaries(frame)
        invoices.to_csv(OUTPUT_DIR / f"{label}_invoices.csv", index=False)
        customers.to_csv(OUTPUT_DIR / f"{label}_customers.csv", index=False)
        report += [f"## {label}", "| Ölçüm | Değer |\n| --- | --- |\n" +
                   "\n".join(f"| {key} | {value} |" for key, value in metrics),
                   f"Yerel çıktılar: `data/processed/{label}_invoices.csv` ve "
                   f"`data/processed/{label}_customers.csv`."]
        print(f"Fatura: {len(invoices)}, müşteri: {len(customers)}", flush=True)
    assert file_hash(EXCEL_PATH) == before, "Ham dosya değişti!"
    report += ["## Doğrulama",
               "Fatura satır sayısı benzersiz faturalarla; müşteri alışveriş "
               "sayıları toplamı fatura sayısıyla; ürün satır sayıları girdi "
               "satırlarıyla eşleşir. Ürün, fatura ve müşteri tutar toplamları "
               "sayısal tolerans içinde aynıdır. Ham Excel hash değeri değişmemiştir. "
               "CSV çıktıları müşteri kimliği içerir ve data/ ile birlikte Git dışında tutulur."]
    path = PROJECT_ROOT / "reports" / "invoice_customer_summary.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n\n".join(report) + "\n", encoding="utf-8")
    print(f"Rapor oluşturuldu: {path}", flush=True)


if __name__ == "__main__":
    main()
