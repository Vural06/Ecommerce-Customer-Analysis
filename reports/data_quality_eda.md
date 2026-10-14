# Veri kalitesi ve keşifsel analiz

## Kapsam

Tüm dönem betimsel analizdir; sonuçlar model ayarı veya test skorunu iyileştirmek için kullanılmadı. Ham Excel değişmez. Müşteri kimlikleri ve fatura kayıtları bu raporda yayımlanmaz.

## Kayıt akışı

Ham sayfa toplamı: 1067371. Sayfalar arası bire bir eşleşen kopya: 22523. Sonraki tablo örtüşme sonrası girdiyle başlar; elenen sayılar adım sırasına bağlı ve birbirinden ayrıdır. İptal sayısı gibi bağımsız ham kontroller için ilk profil raporuna bakın.

| Adım | Kalan satır | Bu adımda elenen |
| --- | --- | --- |
| Örtüşme sonrası girdi | 1044848 | 0 |
| Müşteri kimliği dolu | 809561 | 235287 |
| Fatura kimliği dolu/boşluk değil | 809561 | 0 |
| C/c iptal faturası değil | 791115 | 18446 |
| Quantity > 0 | 791115 | 0 |
| Price > 0 | 791045 | 70 |

Sonuç: 791045 ürün satırı, 36969 fatura, 5878 müşteri. Sayım/tutarlar önceki kayıtlı özetlerle uyuştu; model girdisi değişmedi.

## İptal, iade ve değer kuralları

C/c faturalar alışveriş evreninden çıkarılır. Negatif miktarlar iade veya düzeltme olabilir; hata olarak adlandırılmaz. Sıfır miktar alışveriş hacmi oluşturmaz. Negatif fiyat düzeltme olabilir; sıfır fiyat ücretsiz ürün/eksik fiyat olabilir. Pozitif fiyat/miktar koşulu bu ilk sürümün ücretli alışveriş tanımıdır. Bu kayıtların tamamı ham dosyada kalır; satışlarla iadeler eşleştirilip netleştirilmez. Eksik müşteri kimliği doldurulmaz; müşteriye ait geçmiş kurulamıyor. Açıklama eksikleri satış kimliği/tutarı hesaplarına engel olmadığından tek başına eleme nedeni değildir.

## Sayfa içi tekrar kararı

| Ölçüm | Değer |
| --- | --- |
| Örtüşme sonrası tüm satırlardaki fazla tam kopya | 11812 |
| Geçerli ürün satırlarındaki fazla tam kopya | 11620 |
| Bu kopyalardan etkilenen benzersiz fatura | 4274 |
| Bu kopyalardan etkilenen müşteri | 1580 |
| Kopyaların brüt tutara katkısı (GBP) | 56746.91 |
| Toplam brüt tutardaki payı | 0.3255% |
| Hepsi çıkarılsaydı ürün satırı (duyarlılık) | 779425 |
| Hepsi çıkarılsaydı brüt tutar (GBP, duyarlılık) | 17374804.27 |

Bir faturada aynı ürünün ayrı kalemlere bölünmesi mümkün; kaynakta benzersiz satır kimliği bulunmuyor. Bu nedenle aynı sayfa içindeki eşit kalemlerin hatalı olup olmadığı kesinleşmiyor. Koruma kararı uygulanır. Yukarıdaki silme senaryosu yalnızca tutar hassasiyetini gösterir; yeni temizlenmiş veri veya model üretilmedi. Aynı tam kopyaları kaldırmak benzersiz müşteri/fatura sayılarını değiştirmez, miktar ve tutarı değiştirir.

## Dağılımlar

### Fatura brüt tutarı (GBP)

| İstatistik | Değer |
| --- | --- |
| count | 36969.0000 |
| mean | 471.5181 |
| std | 1359.8832 |
| min | 0.3800 |
| 25% | 159.0000 |
| 50% | 303.6000 |
| 75% | 479.4500 |
| 95% | 1236.3000 |
| 99% | 3610.5000 |
| max | 168469.6000 |

### Fatura ürün miktarı

| İstatistik | Değer |
| --- | --- |
| count | 36969.0000 |
| mean | 285.3147 |
| std | 1232.5484 |
| min | 1.0000 |
| 25% | 72.0000 |
| 50% | 152.0000 |
| 75% | 288.0000 |
| 95% | 777.0000 |
| 99% | 2264.5600 |
| max | 87167.0000 |

### Müşteri başına benzersiz fatura

| İstatistik | Değer |
| --- | --- |
| count | 5878.0000 |
| mean | 6.2894 |
| std | 13.0094 |
| min | 1.0000 |
| 25% | 1.0000 |
| 50% | 3.0000 |
| 75% | 7.0000 |
| 95% | 21.0000 |
| 99% | 46.0000 |
| max | 398.0000 |

### Müşteri başına brüt harcama (GBP)

| İstatistik | Değer |
| --- | --- |
| count | 5878.0000 |
| mean | 2965.5582 |
| std | 14446.5820 |
| min | 2.9500 |
| 25% | 344.2575 |
| 50% | 869.8000 |
| 75% | 2259.3975 |
| 95% | 9431.7945 |
| 99% | 29205.9010 |
| max | 580987.0400 |

En yüksek brüt harcamaya sahip yaklaşık %1'lik grup (59 müşteri), toplam brüt tutarın %31.89'ini oluşturuyor. Üst kuyruk otomatik veri hatası değildir; UCI kaynağı toptan alıcıların bulunduğunu belirtir. Büyük tutarlar modele etki edebilir.

## Alışveriş aralıkları

Müşterinin ardışık farklı faturalarının son kalem zamanları arasındaki gün farkı hesaplandı. İlk fatura aralık üretmez. Aynı anda farklı faturalar varsa fark sıfır olabilir. Özet her müşteriye eşit ağırlık vermez; sık alışveriş yapanlar daha fazla aralık üretir. Son faturadan veri sonuna kadarki süre aralık değildir ve sağdan sansürlüdür.

Aralık sayısı: 31091; sıfır günlük aralık: 182.

### Ardışık fatura aralığı (gün)

| İstatistik | Değer |
| --- | --- |
| count | 31091.0000 |
| mean | 51.6867 |
| std | 75.7889 |
| min | 0.0000 |
| 25% | 6.9833 |
| 50% | 24.7431 |
| 75% | 61.8104 |
| 95% | 206.4267 |
| 99% | 368.7408 |
| max | 714.1521 |

## Aylık değişim

Fatura son kalem tarihinin ayına atanır. Aylık müşteri sayıları toplanarak tüm dönem müşteri sayısı elde edilmez; müşteriler aylar arasında tekrar bulunur. Aralık 2011 yalnızca 9 Aralık'a kadar gözlenmiştir; önceki tam aylarla hacim karşılaştırması yapılmaz.

| Ay | Fatura | Müşteri | Brüt tutar GBP | Kapsam |
| --- | --- | --- | --- | --- |
| 2009-12 | 1512 | 955 | 686654.16 | Gözlenen ay |
| 2010-01 | 1011 | 720 | 557319.06 | Gözlenen ay |
| 2010-02 | 1104 | 772 | 506371.07 | Gözlenen ay |
| 2010-03 | 1524 | 1057 | 699608.99 | Gözlenen ay |
| 2010-04 | 1329 | 942 | 594609.19 | Gözlenen ay |
| 2010-05 | 1377 | 966 | 599985.79 | Gözlenen ay |
| 2010-06 | 1497 | 1041 | 639066.58 | Gözlenen ay |
| 2010-07 | 1381 | 928 | 591636.74 | Gözlenen ay |
| 2010-08 | 1293 | 911 | 604242.65 | Gözlenen ay |
| 2010-09 | 1689 | 1145 | 831615.00 | Gözlenen ay |
| 2010-10 | 2133 | 1497 | 1036680.00 | Gözlenen ay |
| 2010-11 | 2587 | 1607 | 1172336.04 | Gözlenen ay |
| 2010-12 | 1400 | 885 | 572713.89 | Gözlenen ay |
| 2011-01 | 987 | 741 | 569445.04 | Gözlenen ay |
| 2011-02 | 997 | 758 | 447137.35 | Gözlenen ay |
| 2011-03 | 1321 | 974 | 595500.76 | Gözlenen ay |
| 2011-04 | 1149 | 856 | 469200.36 | Gözlenen ay |
| 2011-05 | 1555 | 1056 | 678594.56 | Gözlenen ay |
| 2011-06 | 1393 | 991 | 661213.69 | Gözlenen ay |
| 2011-07 | 1331 | 949 | 600091.01 | Gözlenen ay |
| 2011-08 | 1280 | 935 | 645343.90 | Gözlenen ay |
| 2011-09 | 1755 | 1266 | 952838.38 | Gözlenen ay |
| 2011-10 | 1929 | 1364 | 1039318.79 | Gözlenen ay |
| 2011-11 | 2657 | 1664 | 1161817.38 | Gözlenen ay |
| 2011-12 | 778 | 615 | 518210.79 | Kısmi ay: 1–9 Aralık |

Kısmi son ay hariç, en çok geçerli fatura gözlenen ay 2011-11: 2657 fatura. Aylık hareket mevsimsellik hipotezi üretir; yalnızca iki yıllık veriyle kalıcı mevsimsellik veya kampanya etkisi kanıtlanmaz.

## Aykırı değer kararı

Tanısal üst sınır: Q3 + 1,5 × IQR. Eşikler yalnızca eğitim gözlem penceresindeki faturalarla hesaplandı. Tablodaki iki işaretleme örtüşebilir; sayılar ve tutar payları toplanmaz. Bunlar model ön işleme eşikleri değildir; kesme, winsorization veya eleme uygulanmadı.

| Alan | Train IQR üst sınırı | Tüm dönemde işaretli fatura | Fatura payı | Brüt tutar payı |
| --- | --- | --- | --- | --- |
| invoice_amount_gbp | 972.33 | 2831 | 7.66% | 39.24% |
| total_quantity | 600.00 | 2823 | 7.64% | 35.76% |

Büyük miktar/tutar tek başına yanlış değildir. İlk sürümde koruyoruz; StandardScaler aykırı değerlere dayanıklı değildir ve lojistik regresyon bundan etkilenebilir. Test görülmüş olduğundan bu analiz üzerinden özellik/model ayarı değiştirilmedi. Farklı dönüşümler ancak yeni bir değerlendirme tasarımıyla incelenebilir.

## Tutarlılık

Filtrelerde elenen + kalan = örtüşme sonrası girdi. Ürün kalemi sayısı kayıtlı fatura line_count toplamına eşit. Fatura/müşteri sayıları ve tutarlar mevcut CSV'lerle eşleşti. Aylık fatura ve tutar toplamları tüm dönemle uyuştu. Ham dosya hash'i değişmedi.
