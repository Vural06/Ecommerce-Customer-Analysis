# Fatura ve müşteri özetleri

## Kapsam ve kararlar

Kaynak: `data/raw/online_retail_II.xlsx`. Sayfalar: Year 2009-2010, Year 2010-2011. Ham dosya SHA-256: `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`. İlk sayfa ve iki sayfanın birleşimi ayrı özetlenir.

Bir satır ürün kalemidir. Müşteri/fatura kimliği dolu, fatura C/c ile başlamayan, Quantity > 0 ve Price > 0 satırlar alışveriş olarak kullanılır. En az bir geçerli ürün satırı bulunan fatura sayılır. Filtrelenmiş bir faturanın tutarı yalnızca bu satırların toplamıdır; iadeler netleştirilmez.

Sayfalar arasındaki sekiz sütunu aynı kayıtlar kopya sırasıyla eşleştirildi; ikinci sayfadan 22523 eşleşen satır çıkarıldı. Aynı kayıt için iki sayfadaki kopya sayılarının büyüğü korunur. Bu, kayıt örtüşmesi için açık bir çalışma varsayımıdır; eşit satırların tümünün hatalı olduğunu kanıtlamaz. Sayfa içi tekrarlar korunur; hepsini silmek meşru ürün kalemlerini de silebilir.

Satır tutarı Quantity × Price; fatura tutarı bunun toplamıdır. Fatura Customer ID + Invoice ile gruplanır. Faturada farklı tarihler varsa en erken tarih başlangıç, en geç tarih son kalem zamanı olarak saklanır; zaman damgası sayısı ayrıca raporlanır. Müşterinin son alışverişi son kalem zamanından alınır. Bir fatura birden çok müşteriye bağlıysa betik hata verir.

Müşteri tablosu alışveriş sayısı, brüt harcama, ilk ve son alışveriş tarihini içerir. İptal/iade düşülmediği ve sayfa içi tekrarlar korunduğu için tutar net gelir veya kesin müşteri değeri değildir. Tekrarların toplam tutara katkısı duyarlılık ölçümü olarak gösterilir; tekrarları silme kararı değildir.

Bunlar tüm gözlem dönemine ait betimsel özetlerdir; tahmin tarihinde bilinen özellikler olarak doğrudan modele verilemez. Zamana bağlı SQL özellikleri ve RFM ayrı betiklerde üretilir; bu betik yalnızca fatura/müşteri özetidir.

## first_sheet

| Ölçüm | Değer |
| --- | --- |
| Girdi satırı | 525461 |
| Ham girdi tam tekrarları (ilk kopya hariç) | 6865 |
| Filtrelenmiş ürün satırı | 407664 |
| Filtrelenmiş tam tekrar (korundu) | 6748 |
| Benzersiz alışveriş faturası / özet satırı | 19213 |
| Birden fazla tarih/saat taşıyan fatura | 35 |
| En az bir alışverişi olan müşteri | 4312 |
| En az iki faturası olan müşteri | 2893 |
| Tekrar alışveriş oranı | 67.0918% |
| İlk alışveriş tarihi | 2009-12-01 07:45:00 |
| Son alışveriş tarihi | 2010-12-09 20:01:00 |
| Filtrelenmiş brüt ürün tutarı (GBP) | 8832003.27 |
| Korunan tam tekrarların tutara katkısı (GBP) | 33769.53 |

Yerel çıktılar: `data/processed/first_sheet_invoices.csv` ve `data/processed/first_sheet_customers.csv`.

## combined

| Ölçüm | Değer |
| --- | --- |
| Girdi satırı | 1044848 |
| Ham girdi tam tekrarları (ilk kopya hariç) | 11812 |
| Filtrelenmiş ürün satırı | 791045 |
| Filtrelenmiş tam tekrar (korundu) | 11620 |
| Benzersiz alışveriş faturası / özet satırı | 36969 |
| Birden fazla tarih/saat taşıyan fatura | 64 |
| En az bir alışverişi olan müşteri | 5878 |
| En az iki faturası olan müşteri | 4255 |
| Tekrar alışveriş oranı | 72.3886% |
| İlk alışveriş tarihi | 2009-12-01 07:45:00 |
| Son alışveriş tarihi | 2011-12-09 12:50:00 |
| Filtrelenmiş brüt ürün tutarı (GBP) | 17431551.18 |
| Korunan tam tekrarların tutara katkısı (GBP) | 56746.91 |

Yerel çıktılar: `data/processed/combined_invoices.csv` ve `data/processed/combined_customers.csv`.

## Doğrulama

Fatura satır sayısı benzersiz faturalarla; müşteri alışveriş sayıları toplamı fatura sayısıyla; ürün satır sayıları girdi satırlarıyla eşleşir. Ürün, fatura ve müşteri tutar toplamları sayısal tolerans içinde aynıdır. Ham Excel hash değeri değişmemiştir. CSV çıktıları müşteri kimliği içerir ve data/ ile birlikte Git dışında tutulur.
