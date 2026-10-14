# RFM segmentasyonu

## Yöntem

R: son alışverişten geçen tam gün. F: son 180 gündeki farklı fatura sayısı. M: aynı dönemdeki brüt filtrelenmiş fatura tutarı (GBP). R küçükken, F ve M büyükken puan yüksektir. Her boyut 1–3 puan alır.

Eşikler yalnızca train özelliklerinin 1/3 ve 2/3 kantilleridir; validation ve testte yeniden hesaplanmaz. Eşiğe eşit değer alt sayısal aralıkta kalır. Eşit değerler aynı puanı alır; eşikler çakışırsa bazı puanlar boş kalabilir. Segmentlerin eşit büyüklükte olması beklenmez.

| Alan | İlk eşik | İkinci eşik |
| --- | --- | --- |
| recency_days | 36.0000 | 74.0000 |
| frequency_180d | 1.0000 | 3.0000 |
| monetary_180d_gbp | 355.4500 | 942.4600 |

## Segment kuralları (ilk uyan kural)

| Segment | Kural |
| --- | --- |
| Yakın ve yüksek F/M | R=3, F≥2, M≥2 |
| Yakın, düşük sıklık | R=3, F=1 |
| Orta/yakın, sık | R≥2, F≥2 |
| Uzak, güçlü F/M geçmişi | R=1 ve (F≥2 veya M≥2) |
| Uzak, düşük F/M | R=1, F=1, M=1 |
| Diğer | Yukarıdakilerin dışında kalanlar |

Yakın ve uzak, eğitim eşiklerine göre göreli tanımlardır. Yakın/düşük sıklık müşterisini yeni müşteri olarak yorumlamıyoruz; tüm geçmişte ilk kez alışveriş yaptığı bilinmiyor. Segmentler iş tarafından onaylanmış sınıflar veya eğitilmiş risk tahminleri değildir.

## train (3415 müşteri)

| Segment | Müşteri | Pay | Medyan R (gün) | Medyan F | Medyan M (GBP) |
| --- | --- | --- | --- | --- | --- |
| Yakın ve yüksek F/M | 908 | 26.59% | 23.00 | 4.00 | 1427.98 |
| Yakın, düşük sıklık | 186 | 5.45% | 29.00 | 1.00 | 255.78 |
| Orta/yakın, sık | 716 | 20.97% | 49.00 | 2.00 | 802.89 |
| Uzak, güçlü F/M geçmişi | 630 | 18.45% | 99.00 | 2.00 | 601.17 |
| Uzak, düşük F/M | 488 | 14.29% | 110.00 | 1.00 | 186.38 |
| Diğer | 487 | 14.26% | 54.00 | 1.00 | 288.49 |

### Sonraki 90 günde gözlenen alışveriş yapmama

| Segment | Alışveriş yapmayan / toplam | Oran |
| --- | --- | --- |
| Yakın ve yüksek F/M | 319/908 | 35.13% |
| Yakın, düşük sıklık | 154/186 | 82.80% |
| Orta/yakın, sık | 405/716 | 56.56% |
| Uzak, güçlü F/M geçmişi | 434/630 | 68.89% |
| Uzak, düşük F/M | 412/488 | 84.43% |
| Diğer | 405/487 | 83.16% |

## validation (3049 müşteri)

| Segment | Müşteri | Pay | Medyan R (gün) | Medyan F | Medyan M (GBP) |
| --- | --- | --- | --- | --- | --- |
| Yakın ve yüksek F/M | 729 | 23.91% | 17.00 | 4.00 | 1314.69 |
| Yakın, düşük sıklık | 261 | 8.56% | 20.00 | 1.00 | 285.04 |
| Orta/yakın, sık | 421 | 13.81% | 50.00 | 3.00 | 777.18 |
| Uzak, güçlü F/M geçmişi | 678 | 22.24% | 142.00 | 2.00 | 580.21 |
| Uzak, düşük F/M | 635 | 20.83% | 153.00 | 1.00 | 190.55 |
| Diğer | 325 | 10.66% | 55.00 | 1.00 | 300.00 |

### Sonraki 90 günde gözlenen alışveriş yapmama

| Segment | Alışveriş yapmayan / toplam | Oran |
| --- | --- | --- |
| Yakın ve yüksek F/M | 163/729 | 22.36% |
| Yakın, düşük sıklık | 163/261 | 62.45% |
| Orta/yakın, sık | 146/421 | 34.68% |
| Uzak, güçlü F/M geçmişi | 423/678 | 62.39% |
| Uzak, düşük F/M | 488/635 | 76.85% |
| Diğer | 205/325 | 63.08% |

## test (2772 müşteri)

| Segment | Müşteri | Pay | Medyan R (gün) | Medyan F | Medyan M (GBP) |
| --- | --- | --- | --- | --- | --- |
| Yakın ve yüksek F/M | 765 | 27.60% | 14.00 | 4.00 | 1395.73 |
| Yakın, düşük sıklık | 224 | 8.08% | 18.00 | 1.00 | 300.95 |
| Orta/yakın, sık | 445 | 16.05% | 48.00 | 3.00 | 722.42 |
| Uzak, güçlü F/M geçmişi | 508 | 18.33% | 105.00 | 2.00 | 558.59 |
| Uzak, düşük F/M | 579 | 20.89% | 132.00 | 1.00 | 187.05 |
| Diğer | 251 | 9.05% | 55.00 | 1.00 | 243.76 |

## Yorum ve sınırlılıklar

Segment tablolarındaki medyanlar tipik davranışı, paylar segment büyüklüğünü gösterir. Yakın/yüksek F-M grubu yakın dönemde sık ve yüksek tutarlı alışveriş yapanları; uzak/güçlü geçmiş grubu uzun süredir alışveriş yapmayan fakat gözlemde sıklığı veya harcaması güçlü olanları temsil eder. Bu gruplar iletişim stratejisi için hipotez üretmeye yardımcı olabilir; kampanya başarısı veya nedensel kazanç göstermez.

Train/validation hedef oranları betimsel karşılaştırmadır. Kurallar bu oranlara göre ayarlanmadı. Küçük grupların oranları kararsız olabilir; müşteri sayısıyla birlikte okunmalıdır. Test hedefleri bu betikte okunmaz. Testteki tablo yalnızca geçmiş özelliklerin dağılımını gösterir; model/segment kuralı seçmek için kullanılmaz.

M iadeler düşülmeden hesaplanır ve korunan sayfa içi tekrarları içerir. 180 günlük müşteri evreni uzun süredir pasif müşterileri dışlar. Sabit eşikler dönem değişiminden etkilenebilir. 1–3 puanlı basit kuralların iş uygunluğu ayrıca doğrulanmalıdır.

## Çıktılar ve doğrulama

`configs/rfm_thresholds.json` yalnızca eğitim eşiklerini içerir. `data/processed/{train,validation,test}_rfm.csv` müşteri puan/segmentlerini; `*_rfm_summary.csv` segment özetlerini içerir. Yerel CSV'ler Git dışındadır. Müşteriler kaybolmadan tek segmente atanır, puanlar 1–3 aralığındadır. RFM betiği model eğitmez; güncel model sonuçları ayrı model karşılaştırması raporundadır.
