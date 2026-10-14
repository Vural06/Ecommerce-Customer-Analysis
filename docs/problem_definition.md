# İlk sürüm problem tanımı

Amaç: yakın dönemde alışveriş yapan müşterinin izleyen 90 günde geçerli bir alışveriş yapmama riskini tahmin etmek. Bu durum kalıcı müşteri kaybı olarak yorumlanmaz.

## Müşteri, alışveriş ve hedef

- Evren: tahmin tarihinden önceki 180 günde en az bir geçerli alışveriş faturası olan, kimliği bilinen müşteriler. Eski ama bu dönemde alışveriş yapmayan müşteriler kapsam dışıdır.
- Geçerli alışveriş: müşteri/fatura kimliği dolu, C/c iptal işareti taşımayan, miktarı ve fiyatı pozitif satırlardan en az birini içeren fatura. Ürün satırı alışveriş sayılmaz.
- Hedef `no_purchase_90d`: izleyen 90 günde geçerli alışveriş faturası yoksa 1, varsa 0. Kimliği eksik müşteriler hakkında etiket üretilmez.
- İade ve iptaller satışlarla netleştirilmez; parasal özellik brüt filtrelenmiş ürün tutarıdır. Sayfa içi tekrarlar korunur; bu varsayım parasal özellikleri etkileyebilir.

180/90 gün basit başlangıç varsayımıdır; iş tarafından doğrulanmış en uygun süre değildir. Sonraki sürümde farklı süreler eğitim/doğrulama dönemlerinde karşılaştırılabilir.

## Zaman sınırları

Gözlem: `[tahmin tarihi - 180 gün, tahmin tarihi)`. Hedef: `[tahmin tarihi, tahmin tarihi + 90 gün)`. Sol sınır dahil, sağ sınır hariçtir; gün sonu belirsizliği oluşmaz. Veri saat dilimi belirtilmediğinden saat dilimsiz zamanlar korunur.

Bir faturada farklı tarih/saatler bulunabiliyor. Önceki aşamada bütün kalemlerin toplam tutarı üretildiği için faturayı **son kalem zamanı itibarıyla** kullanılabilir sayıyoruz. Böylece henüz tamamlanmamış faturanın ilerideki ürün tutarı geçmiş özelliklere girmez. Bu tarih, müşterinin ilk sipariş verme anından farklı olabilir; fatura tamamlanmasına dayanan açık bir çalışma varsayımıdır.

| Bölüm | Tahmin tarihi | Gözlem | Hedef |
| --- | --- | --- | --- |
| train | 2011-01-01 | Önceki 180 gün | Sonraki 90 gün |
| validation | 2011-05-01 | Önceki 180 gün | Sonraki 90 gün |
| test | 2011-09-01 | Önceki 180 gün | Sonraki 90 gün |

Hedef pencereleri bir sonraki bölümün tahmin tarihinden önce tamamlanır. Her gözlem ve hedef penceresi dosyanın tarih kapsamına sığmalıdır; hedef sonu gözlenen son zamandan sonraysa betik durur. Dosyanın tüm işlem dönemini kapsadığı UCI açıklamasına dayanan bir varsayımdır; yalnızca son zaman damgası kesintisiz veri toplandığını kanıtlamaz.

## Basit özellikler

- `recency_days`: tahmin tarihi ile gözlemdeki son tamamlanmış fatura arasındaki tam gün.
- `frequency_180d`: gözlem dönemindeki benzersiz fatura sayısı.
- `monetary_180d_gbp`: gözlem dönemindeki brüt fatura tutarı toplamı.
- `average_invoice_amount_gbp`: ortalama brüt fatura tutarı.
- `quantity_180d`: toplam ürün miktarı.

İlk/son gözlenen alışveriş zamanları denetim için saklanır. Müşteri kimliği ve tahmin tarihi eşleştirme/denetim alanlarıdır; doğrudan model özelliği yapılmaz. Tüm dönem müşteri özetindeki harcama ve son alışveriş değerleri kullanılmaz. Gelecek fatura sayısı yalnızca hedef tablosundadır.

## Uygulanan değerlendirme

Çoğunluk sınıfı referansı, lojistik regresyon ve tek Random Forest alternatifi karşılaştırıldı. Riskli müşterileri sıralamak için average precision (AP), karar eşiği için validation F1 kullanıldı; precision/recall ve accuracy birlikte raporlandı. AP, trapez PR-AUC ile aynı hesap değildir. Accuracy tek başına seçim ölçütü yapılmadı. Kampanya kapasitesi belirlenirse precision@k ayrıca değerlendirilebilir. Başarı hedefi veya beklenen kazanç uydurulmadı.

Model validation AP ile seçildi; eşitlikte F1, yine eşitse lojistik regresyon tercih edilir. Lojistik regresyon eşiği 0,6, Random Forest eşiği 0,5 olarak validation F1 ile belirlendi. Random Forest seçimi testten önce kaydedildi. Ön işleme yalnızca eğitim verisinde öğrenildi; validation üzerinde yeniden eğitim yapılmadı. Sonra sabit seçimler testte raporlandı. Test artık görülmüştür ve yeni bir bağımsız test olarak sunulamaz. Aynı müşteriler farklı dönemlerde bulunabilir; hedef mevcut müşterileri zaman içinde tekrar değerlendirmektir. Üç tarihli başlangıç düzeni mevsimselliği ve yeni müşteri performansını tam ölçmez. Kampanya etkisi gerçek deney gerektirir.
