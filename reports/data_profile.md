# UCI Online Retail II — ilk veri incelemesi

Rapor zamanı (UTC): 2026-09-19T19:33:53.919524+00:00

[Resmî kaynak](https://archive.ics.uci.edu/dataset/502/online+retail+ii). Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. [DOI](https://doi.org/10.24432/C5CG6D). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Girdi: `data/raw/online_retail_II.xlsx`; SHA-256: `bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980`.

Python 3.13.9, pandas 3.0.6, openpyxl 3.1.5.

## Sayım yöntemi ve sınırlar

Bir satır bir ürün/fatura kalemidir; sipariş sayısı değildir. Alışveriş sayımında `Invoice` dolu, C/c ile başlamayan, `Quantity > 0`, `Price > 0` ve `Customer ID` dolu satırlar kullanılır. Bir faturanın en az bir satırının bu filtreyi geçmesi yeterlidir. Her müşteri için `Invoice.nunique()` hesaplanır. İptal/iade satırları özgün satışlarla eşleştirilip netleştirilmemiştir. Bu geçici inceleme tanımıdır; nihai temizleme veya hedef tanımı değildir.

Ham dosya ve satırlar değiştirilmez. Filtreler ve tekilleştirme yalnızca bellekte özet hesaplamak içindir; temizlenmiş veri yazılmaz. Eksik oranlarının paydası ilgili bölümün tüm satırlarıdır. Benzersiz sayılar eksik kimlikleri içermez. Tam tekrar, sekiz sütunun tümünün eşitliğidir; eksikler eşit kabul edilir. Veri tipleri Excel hücre biçimi değil pandas okuma sonucudur. Birleşik bölüm sayfaların ham birleşimidir; örtüşen satırlar korunur, benzersiz faturalar yeniden sayılır. Yüzdeler yuvarlanmıştır.

Kategori, indirim, ödeme ve teslimat alanları yoktur. StockCode ürün kodu, Description açıklama, Country ülke bilgisidir; ek alanlar türetilmemiştir. Tüm dönem tekrar alışveriş oranı geleceğe yönelik model başarısı veya kampanya etkisi değildir. Müşterilerin gözlenme süreleri farklıdır.

## Çalışma sayfaları

| Sayfa | Satır | Sütun |
| --- | --- | --- |
| Year 2009-2010 | 525461 | 8 |
| Year 2010-2011 | 541910 | 8 |


## Year 2009-2010

| Ölçüm | Değer |
| --- | --- |
| Satır (ürün satırı) | 525461 |
| İlk tarih | 2009-12-01 07:45:00 |
| Son tarih | 2010-12-09 20:01:00 |
| Benzersiz müşteri (eksik hariç) | 4383 |
| Benzersiz fatura (iptaller dahil, eksik hariç) | 28816 |
| İptal satırı (Invoice C/c ile başlıyor) | 10206 |
| Benzersiz iptal faturası | 4592 |
| Quantity < 0 satır | 12326 |
| Quantity = 0 satır | 0 |
| Price < 0 satır | 3 |
| Price = 0 satır | 3687 |
| Tam tekrar: ilk kopya dışındaki satırlar | 6865 |
| Tam tekrar gruplarındaki tüm satırlar | 13283 |
| Alışveriş filtresinden geçen satır | 407664 |
| Filtrelenmiş benzersiz alışveriş faturası | 19213 |
| En az bir alışveriş faturası olan müşteri | 4312 |
| Kimliği bilinen, geçerli alışverişi olmayan müşteri | 71 |
| En az iki alışveriş faturası olan müşteri | 2893 |
| Tekrar alışveriş oranı (payda: en az bir alışveriş yapanlar) | 67.0918% |
| Tekrar alışveriş oranı (payda: tüm bilinen müşteriler) | 66.0050% |
| Birden çok müşteriye bağlı fatura sayısı | 0 |


### Gerçek sütunlar, pandas veri tipleri ve eksikler

| Sütun | Veri tipi | Eksik sayı | Eksik oranı |
| --- | --- | --- | --- |
| Invoice | object | 0 | 0.0000% |
| StockCode | object | 0 | 0.0000% |
| Description | object | 2928 | 0.5572% |
| Quantity | int64 | 0 | 0.0000% |
| InvoiceDate | datetime64[us] | 0 | 0.0000% |
| Price | float64 | 0 | 0.0000% |
| Customer ID | float64 | 107927 | 20.5395% |
| Country | str | 0 | 0.0000% |


### Müşteri başına benzersiz alışveriş faturası dağılımı

Aşağıdaki özetin paydası en az bir geçerli alışverişi olan müşterilerdir.

| İstatistik | Fatura sayısı |
| --- | --- |
| count | 4312.0000 |
| mean | 4.4557 |
| std | 8.1702 |
| min | 1.0000 |
| 25% | 1.0000 |
| 50% | 2.0000 |
| 75% | 5.0000 |
| 90% | 9.0000 |
| 95% | 13.0000 |
| 99% | 31.0000 |
| max | 205.0000 |


Aralık tablosu tüm kimliği bilinen müşterileri kapsar (0 dahil).

| Fatura sayısı | Müşteri sayısı | Müşteri oranı |
| --- | --- | --- |
| 0 | 71 | 1.6199% |
| 1 | 1419 | 32.3751% |
| 2 | 810 | 18.4805% |
| 3–5 | 1141 | 26.0324% |
| 6–10 | 607 | 13.8490% |
| 11–20 | 242 | 5.5213% |
| 21+ | 93 | 2.1218% |


## Year 2010-2011

| Ölçüm | Değer |
| --- | --- |
| Satır (ürün satırı) | 541910 |
| İlk tarih | 2010-12-01 08:26:00 |
| Son tarih | 2011-12-09 12:50:00 |
| Benzersiz müşteri (eksik hariç) | 4372 |
| Benzersiz fatura (iptaller dahil, eksik hariç) | 25900 |
| İptal satırı (Invoice C/c ile başlıyor) | 9288 |
| Benzersiz iptal faturası | 3836 |
| Quantity < 0 satır | 10624 |
| Quantity = 0 satır | 0 |
| Price < 0 satır | 2 |
| Price = 0 satır | 2515 |
| Tam tekrar: ilk kopya dışındaki satırlar | 5268 |
| Tam tekrar gruplarındaki tüm satırlar | 10147 |
| Alışveriş filtresinden geçen satır | 397885 |
| Filtrelenmiş benzersiz alışveriş faturası | 18532 |
| En az bir alışveriş faturası olan müşteri | 4338 |
| Kimliği bilinen, geçerli alışverişi olmayan müşteri | 34 |
| En az iki alışveriş faturası olan müşteri | 2845 |
| Tekrar alışveriş oranı (payda: en az bir alışveriş yapanlar) | 65.5832% |
| Tekrar alışveriş oranı (payda: tüm bilinen müşteriler) | 65.0732% |
| Birden çok müşteriye bağlı fatura sayısı | 0 |


### Gerçek sütunlar, pandas veri tipleri ve eksikler

| Sütun | Veri tipi | Eksik sayı | Eksik oranı |
| --- | --- | --- | --- |
| Invoice | object | 0 | 0.0000% |
| StockCode | object | 0 | 0.0000% |
| Description | object | 1454 | 0.2683% |
| Quantity | int64 | 0 | 0.0000% |
| InvoiceDate | datetime64[us] | 0 | 0.0000% |
| Price | float64 | 0 | 0.0000% |
| Customer ID | float64 | 135080 | 24.9266% |
| Country | str | 0 | 0.0000% |


### Müşteri başına benzersiz alışveriş faturası dağılımı

Aşağıdaki özetin paydası en az bir geçerli alışverişi olan müşterilerdir.

| İstatistik | Fatura sayısı |
| --- | --- |
| count | 4338.0000 |
| mean | 4.2720 |
| std | 7.6980 |
| min | 1.0000 |
| 25% | 1.0000 |
| 50% | 2.0000 |
| 75% | 5.0000 |
| 90% | 9.0000 |
| 95% | 13.0000 |
| 99% | 30.0000 |
| max | 209.0000 |


Aralık tablosu tüm kimliği bilinen müşterileri kapsar (0 dahil).

| Fatura sayısı | Müşteri sayısı | Müşteri oranı |
| --- | --- | --- |
| 0 | 34 | 0.7777% |
| 1 | 1493 | 34.1491% |
| 2 | 835 | 19.0988% |
| 3–5 | 1138 | 26.0293% |
| 6–10 | 535 | 12.2370% |
| 11–20 | 242 | 5.5352% |
| 21+ | 95 | 2.1729% |


## Sayfalar arası örtüşme

### Year 2009-2010 / Year 2010-2011

| Kontrol | Sonuç |
| --- | --- |
| Tarih aralığı kesişimi | 2010-12-01 08:26:00 — 2010-12-09 20:01:00 |
| Ortak takvim günü | 8 |
| Ortak zaman damgası | 921 |
| Ortak benzersiz fatura | 1088 |
| Ortak benzersiz müşteri | 2813 |
| Sekiz sütunu eşit ortak benzersiz kayıt | 22202 |
| Year 2009-2010: karşı sayfada aynısı olan satır | 22523 |
| Year 2010-2011: karşı sayfada aynısı olan satır | 22523 |


Ortak müşteri tek başına mükerrer kayıt değildir. Ortak gün/zaman da tam kayıt eşitliği anlamına gelmez. Birleşik satır sayısı bu yüzden otomatik olarak tekil işlem sayısı kabul edilmemelidir.

## Birleşik dönem (ham satırlar korunarak)

| Ölçüm | Değer |
| --- | --- |
| Satır (ürün satırı) | 1067371 |
| İlk tarih | 2009-12-01 07:45:00 |
| Son tarih | 2011-12-09 12:50:00 |
| Benzersiz müşteri (eksik hariç) | 5942 |
| Benzersiz fatura (iptaller dahil, eksik hariç) | 53628 |
| İptal satırı (Invoice C/c ile başlıyor) | 19494 |
| Benzersiz iptal faturası | 8292 |
| Quantity < 0 satır | 22950 |
| Quantity = 0 satır | 0 |
| Price < 0 satır | 5 |
| Price = 0 satır | 6202 |
| Tam tekrar: ilk kopya dışındaki satırlar | 34335 |
| Tam tekrar gruplarındaki tüm satırlar | 67242 |
| Alışveriş filtresinden geçen satır | 805549 |
| Filtrelenmiş benzersiz alışveriş faturası | 36969 |
| En az bir alışveriş faturası olan müşteri | 5878 |
| Kimliği bilinen, geçerli alışverişi olmayan müşteri | 64 |
| En az iki alışveriş faturası olan müşteri | 4255 |
| Tekrar alışveriş oranı (payda: en az bir alışveriş yapanlar) | 72.3886% |
| Tekrar alışveriş oranı (payda: tüm bilinen müşteriler) | 71.6089% |
| Birden çok müşteriye bağlı fatura sayısı | 0 |


### Gerçek sütunlar, pandas veri tipleri ve eksikler

| Sütun | Veri tipi | Eksik sayı | Eksik oranı |
| --- | --- | --- | --- |
| Invoice | object | 0 | 0.0000% |
| StockCode | object | 0 | 0.0000% |
| Description | object | 4382 | 0.4105% |
| Quantity | int64 | 0 | 0.0000% |
| InvoiceDate | datetime64[us] | 0 | 0.0000% |
| Price | float64 | 0 | 0.0000% |
| Customer ID | float64 | 243007 | 22.7669% |
| Country | str | 0 | 0.0000% |


### Müşteri başına benzersiz alışveriş faturası dağılımı

Aşağıdaki özetin paydası en az bir geçerli alışverişi olan müşterilerdir.

| İstatistik | Fatura sayısı |
| --- | --- |
| count | 5878.0000 |
| mean | 6.2894 |
| std | 13.0094 |
| min | 1.0000 |
| 25% | 1.0000 |
| 50% | 3.0000 |
| 75% | 7.0000 |
| 90% | 13.0000 |
| 95% | 21.0000 |
| 99% | 46.0000 |
| max | 398.0000 |


Aralık tablosu tüm kimliği bilinen müşterileri kapsar (0 dahil).

| Fatura sayısı | Müşteri sayısı | Müşteri oranı |
| --- | --- | --- |
| 0 | 64 | 1.0771% |
| 1 | 1623 | 27.3140% |
| 2 | 944 | 15.8869% |
| 3–5 | 1510 | 25.4123% |
| 6–10 | 925 | 15.5671% |
| 11–20 | 579 | 9.7442% |
| 21+ | 297 | 4.9983% |


## Doğrulama

Ham dosyanın SHA-256 değeri inceleme öncesi ve sonrası aynıdır. Sayfa satır toplamı birleşik satır sayısına eşittir. Müşteri-fatura tekil çift sayısı, müşteri bazlı fatura sayılarının toplamına eşittir. Profil betiği model veya dashboard üretmez; güncel proje durumu README içindedir.
