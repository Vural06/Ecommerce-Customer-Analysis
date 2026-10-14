"""Alıştırma 1: İlk Excel sayfasını tanıma.

Yalnızca Year 2009-2010 sayfası okunur. Ham dosyaya yazılmaz.
Kodunu TODO açıklamalarının altına ekle ve sonuçlarını print ile göster.
Alışveriş filtreleri yalnızca bellekteki alt tablolara uygulanır.
df korunur; temizlenmiş dosya üretilmez, eksik değerler doldurulmaz.
"""

from pathlib import Path

import pandas as pd


# __file__ bu betiğin yoludur. parents[1], exercises klasörünün üstünü bulur.
# Böylece veri yolu terminalin hangi klasörde açıldığına bağlı olmaz.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"

if not EXCEL_PATH.is_file():
    raise FileNotFoundError(f"Ham Excel bulunamadı: {EXCEL_PATH}")

print("İlk sayfa okunuyor; büyük dosyanın yüklenmesi biraz sürebilir...", flush=True)

# Sayfa sıralaması sıfırdan başlar: sheet_name=0 yalnızca ilk sayfayı seçer.
# df, bellekte tutulan pandas tablosudur (DataFrame).
df = pd.read_excel(EXCEL_PATH, sheet_name=0, engine="openpyxl")

print("İlk sayfa yüklendi. TODO kodlarını aşağıya ekleyebilirsin.")

# TODO 1: İlk 5 satırı ve sütun adlarını göster.
# İpucu: DataFrame'in head metodunu ve columns özelliğini araştır.
print(df.head())
print("Sütun adları:", df.columns.tolist())


# TODO 2: Satır ve sütun sayısını ayrı etiketlerle yazdır.
# İpucu: shape özelliği iki değer verir; sıralama satır, ardından sütundur.
print("Satır sayısı:", df.shape[0])
print("Sütun sayısı:", df.shape[1])

# TODO 3: Customer ID eksik olan satırların sayısını ve oranını hesaplayıp yazdır.
# İpucu: Gerçek sütun adı "Customer ID" (arada boşluk var). isna ile eksikleri
# belirleyebilirsin. Oranın paydası ilk sayfadaki tüm satırlardır; yüzde için 100 ile çarp.
eksik_musteri_sayisi = df["Customer ID"].isna().sum()
eksik_musteri_orani = (eksik_musteri_sayisi / len(df)) * 100
print("Eksik Customer ID sayısı:", eksik_musteri_sayisi)
print(f"Eksik Customer ID oranı: %{eksik_musteri_orani:.2f}")

# TODO 4: Customer ID eksik olmayan benzersiz müşteri sayısını hesaplayıp yazdır.
# İpucu: nunique metodunu ve dropna parametresini araştır; aynı müşterinin
# birden fazla ürün satırı olabileceğini unutma. Satır sayısı müşteri sayısı değildir.
unique_customers = df["Customer ID"].nunique(dropna=True)
print("Benzersiz müşteri sayısı:", unique_customers)

# İptalleri ham tabloda say: sonraki filtreler bu satırları elemiş olabilir.
# string tipi eksik değerleri korur; na=False, eksik faturayı iptal saymaz.
raw_invoice_text = df["Invoice"].astype("string").str.strip()
raw_is_cancelled = raw_invoice_text.str.upper().str.startswith("C", na=False)
print("Ham tablodaki iptal satırı sayısı:", raw_is_cancelled.sum())

# Müşteri kimliği dolu satırları seç.
identified_sales = df[df["Customer ID"].notnull()]
print("Kimliği dolu satır sayısı:", len(identified_sales))

# Bu satırlar içinden miktarı pozitif olanları seç.
positive_quantity_sales = identified_sales[identified_sales["Quantity"] > 0]
print("Miktarı pozitif satır sayısı:", len(positive_quantity_sales))

# Müşteri kimliği dolu, miktarı ve fiyatı pozitif satırları seç.
positive_price_sales = positive_quantity_sales[positive_quantity_sales["Price"] > 0]

print("Fiyat filtresi sonrası satır sayısı:", len(positive_price_sales))

print("Fiyat filtresinde elenen satır sayısı:",len(positive_quantity_sales) - len(positive_price_sales))

# Hem eksik değerleri hem de boş/yalnızca boşluk içeren faturaları ele.
# strip yalnızca kontrol için kullanılır; özgün Invoice sütunu değişmez.
invoice_text = positive_price_sales["Invoice"].astype("string").str.strip()
has_invoice = invoice_text.notna() & invoice_text.ne("").fillna(False)
invoice_sales = positive_price_sales[has_invoice]

print("Faturası dolu satır sayısı:", len(invoice_sales))
print("Eksik fatura nedeniyle elenen:",len(positive_price_sales) - len(invoice_sales))

# Fatura numaralarını metne çevir ve C ile başlayanları belirle.
is_cancelled = (
    invoice_sales["Invoice"].astype("string").str.strip().str.upper()
    .str.startswith("C", na=False)
)

print("Kalan tablodaki iptal satırı sayısı:", is_cancelled.sum())
print("Önceki filtrelerde elenen iptal satırı:", raw_is_cancelled.sum() - is_cancelled.sum())

# İptal olmayan satırları seç.
valid_sales = invoice_sales[~is_cancelled].copy()

print("Geçerli satış satırı:", len(valid_sales))
print("Benzersiz fatura:", valid_sales["Invoice"].nunique())
print("Benzersiz müşteri:", valid_sales["Customer ID"].nunique())

# groupby müşterinin ürün satırlarını bir araya getirir.
# nunique aynı faturadaki birden fazla ürünü tek alışveriş olarak sayar.
customer_invoice_counts = valid_sales.groupby("Customer ID")["Invoice"].nunique()
print("Müşteri başına benzersiz fatura sayısı (ilk 5 müşteri):")
print(customer_invoice_counts.head())

# Bu seride yalnızca en az bir geçerli alışverişi olan müşteriler bulunur.
# Boolean değerlerin toplamı koşulu sağlayan müşteri sayısını verir.
repeat_customer_count = int((customer_invoice_counts >= 2).sum())
shopping_customer_count = len(customer_invoice_counts)
print("En az bir geçerli alışverişi olan müşteri:", shopping_customer_count)
print("En az iki farklı alışveriş faturası olan müşteri:", repeat_customer_count)

if shopping_customer_count > 0:
    repeat_customer_rate = repeat_customer_count / shopping_customer_count * 100
    print(f"Tekrar alışveriş oranı (alışveriş yapan müşteriler içinde): %{repeat_customer_rate:.2f}")
else:
    print("Tekrar alışveriş oranı hesaplanamadı: geçerli alışveriş yapan müşteri yok.")

# Bu oran yalnızca ilk sayfanın gözlem dönemini özetler.
# Gelecek dönem tahmin başarısı veya kampanya etkisi olarak yorumlanmaz.
