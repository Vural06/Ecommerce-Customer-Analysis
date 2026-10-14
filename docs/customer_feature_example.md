# Eğitim müşterisi: elle özellik hesabı

## Kapsam

Gerçek eğitim verisinden iki faturası olan bir müşteri seçildi. Yayımlanan örnekte müşteri adı `Örnek A`, faturalar `Fatura A/B` olarak takma adlandırıldı. Özgün kimlik eşleştirmesi yalnızca Git dışındaki `data/processed/customer_example_private.md` dosyasındadır.

Tahmin tarihi: **2011-01-01 00:00:00**. Kullanılabilen geçmiş: **2010-07-05 00:00:00 ≤ fatura son kalem zamanı < 2011-01-01 00:00:00**. Müşteri bilgisi tahmin tarihinden sonra tamamlanan faturalarla zenginleştirilmez.

## Kullanılan geçmiş faturalar

| Takma fatura | Son kalem zamanı | Brüt tutar GBP | Ürün miktarı |
| --- | --- | --- | --- |
| Fatura A | 2010-10-31 14:20:00 | 611.53 | 509 |
| Fatura B | 2010-12-07 14:57:00 | 711.79 | 319 |

Fatura tutarı önceki aşamada geçerli ürün kalemlerinin Quantity × Price toplamıdır. Burada fatura başına tek satır var; aynı faturadaki ürünler alışveriş sayısını artırmaz. İadeler brüt tutardan düşülmemiştir.

## Hesap adımları

1. **Recency:** tahmin tarihi − son fatura zamanı = 24 gün 09:03:00. SQL tam gün kısmını alır: **24 gün**. Saat farkını yukarı yuvarlamıyoruz.

2. **Frequency:** iki farklı fatura var; COUNT(DISTINCT invoice_id) = **2**.

3. **Monetary:** 611.53 + 711.79 = **1323.32 GBP**.

4. **Ortalama fatura tutarı:** 1323.32 / 2 = **661.66 GBP**.

5. **Miktar:** 509 + 319 = **828 ürün birimi**; bu fatura sayısı değildir.

## SQL ile karşılaştırma

| Özellik | Elle hesap | SQL | Sonuç |
| --- | --- | --- | --- |
| recency_days | 24.0000 | 24.0000 | Eşleşti |
| frequency_180d | 2.0000 | 2.0000 | Eşleşti |
| monetary_180d_gbp | 1323.3200 | 1323.3200 | Eşleşti |
| average_invoice_amount_gbp | 661.6600 | 661.6600 | Eşleşti |
| quantity_180d | 828.0000 | 828.0000 | Eşleşti |

SQL: `sql/customer_features.sql`. Aynı tahmin/gözlem sınırlarıyla hesaplanan beş değer SQL çıktısıyla eşleşti. Gelecek faturalar bu hesapta yoktur; hedef örneğe eklenmedi.

## Senin incelemen

Bu örnek hazırlanmış ve otomatik kontrol edilmiştir. Öğrenciyle elle inceleme maddesi sen inceleyene kadar TODO'da açık kalır. Mülakatta ürün kalemi/fatura farkını, sağ sınırın neden hariç olduğunu ve brüt harcamanın net gelir olmadığını açıklayabilmelisin.
