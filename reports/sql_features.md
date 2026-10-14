# Zaman pencereleri ve SQL özellikleri

Tanım ve kararlar: [Problem tanımı](../docs/problem_definition.md). Girdi: `data/processed/combined_invoices.csv`. SQL motoru SQLite 3.51.0. Rapor üretimi (UTC): 2026-10-14T18:32:56+00:00.

Özellikler ve hedefler ayrı CSV/SQL tablolarında tutulur. Müşteri kimliği eşleştirme anahtarıdır; model girdisi olarak kullanılmayacak.

| Bölüm | Gözlem başlangıcı | Tahmin tarihi | Hedef sonu (hariç) | Müşteri | Hedef=1 | Hedef=1 oranı |
| --- | --- | --- | --- | --- | --- | --- |
| train | 2010-07-05 | 2011-01-01 | 2011-04-01 | 3415 | 2129 | 62.34% |
| validation | 2010-11-02 | 2011-05-01 | 2011-07-30 | 3049 | 1588 | 52.08% |
| test | 2011-03-05 | 2011-09-01 | 2011-11-30 | 2772 | 1089 | 39.29% |


## Kontroller

Üç dönemin hedef penceresi de veri sonundan önce tamamlanır. Müşteri anahtarları tekildir ve özellik/hedef tabloları eşleşir. Son alışveriş tarihi tahmin tarihinden küçüktür. Her dönemde üç müşterinin sıklık, harcama, recency ve hedef hesapları pandas ile doğrulandı.

Train/validation ortak müşterileri: 2414. Validation/test ortak müşterileri: 2053. Aynı müşterinin farklı tarihlerde bulunması, mevcut müşteriye tekrar tahmin yapma kullanımına uygundur; yeni müşterilere genelleme testi değildir. Tek bir tarih örneği mevsimsel değişimleri tam ölçmez.

Oranlar gerçek gözlenen etiket dağılımlarıdır; model başarısı veya kampanya kazancı değildir. Bu betik RFM değerlerini üretir; segment puanları ve model karşılaştırması ayrı betiklerde yapılır.


## Yerel çıktılar

`data/processed/{train,validation,test}_features.csv`, aynı bölümlerin `*_labels.csv` dosyaları ve `customer_analytics.sqlite`. SQL dosyaları `sql/customer_features.sql` ve `sql/customer_labels.sql`. Veri çıktıları Git dışındadır.
