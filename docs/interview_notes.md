# Mülakatta projeyi anlatma

“Bu projede yakın dönemde alışveriş yapan e-ticaret müşterisinin sonraki 90 günde tekrar alışveriş yapmama durumunu tahmin ettim. Veri UCI Online Retail II; müşteri kaybını doğrudan gözlemlemiyorum, bu nedenle hedefi belirli bir dönemde alışveriş yapmama olarak tanımladım.”

## Açıklayabilmem gereken kararlar

1. **Ürün kalemi ile alışveriş farkı:** Excel satırı bir ürün kalemi. Faturayı müşteri ve fatura kimliğiyle gruplayıp farklı faturaları alışveriş sayıyorum.
2. **Veri kalitesi:** sayfalar Aralık 2010'da örtüşüyor. Aynı kayıtları sayfalar arasında kopya sırasıyla eşleştiriyorum. Sayfa içi tekrarların hatalı olduğunu kanıtlayamadığım için koruyorum; tutara etkilerini raporluyorum.
3. **İptal/iade:** C/c faturalar ile pozitif olmayan miktar/fiyatları ücretli alışveriş tanımından çıkarıyorum. Orijinal dosya korunuyor. Para özelliği net gelir değil, filtrelenmiş brüt ürün tutarıdır.
4. **Zaman:** her tahmin için 180 günlük geçmiş ve 90 günlük hedef var. Sağ sınır hariç. Fatura tutarı son kalem zamanında kullanılabilir sayılır; gelecekte tamamlanan fatura geçmişe eklenmez.
5. **SQL:** geçmiş faturalar müşteri bazında gruplanır. Recency, frequency, monetary, ortalama fatura ve miktar üretilir. Gelecek fatura sayısı ayrı hedef sorgusunda kalır. Kimlikleri modele vermiyorum.
6. **RFM:** 1–3 puanlı, basit altı segment. Eşikler yalnızca train kantilleri; başka dönemlerde sabit. Eşit değerleri keyfi sıralamayla bölmüyorum.
7. **Model:** çoğunluk sınıfı, lojistik regresyon ve tek küçük Random Forest. Geniş ayar araması yapmadım. StandardScaler yalnızca train'de öğrenir; Random Forest ölçekleme gerektirmez.
8. **Seçim:** model validation AP, eşik validation F1 ile seçildi. Sonuçlar görüldükten sonra testte model değiştirilmedi. Test artık görülmüş bir dönemdir.

## Ölçülen sonuçları dürüstçe anlatma

Random Forest test AP=0,5858 ve F1=0,6422 üretti; çoğunluk referansı AP=0,3929 ve F1=0,5641. Lojistik regresyon AP=0,5821 ve F1=0,6390 ile çok yakındı. Küçük fark için istatistiksel üstünlük testi yapmadım.

Random Forest precision %49,17 ve recall %92,56. 1.008 alışveriş yapmayan müşteriyi yakaladı; 81'ini kaçırdı; 1.042 alışveriş yapan müşteriyi yanlışlıkla riskli işaretledi. Bu karar eşiği yüksek recall yanında çok sayıda yanlış alarm üretiyor. Kampanya maliyeti bilinmediği için ticari olarak en iyi eşik olduğunu söylemiyorum.

## Sınırlılıklar

Tek eğitim/doğrulama/test tarihi, mevsimsel genellemeyi tam ölçmez. Kimliği eksik ve son 180 günde alışveriş yapmayan müşteriler evren dışında. İadeler netleştirilmedi; uç değerler ve sayfa içi tekrarlar korunuyor. Olasılıklar ayrıca kalibre edilmedi. Kampanyanın nedensel etkisi gerçek deney gerektirir. Dashboard henüz yapılmadı; API ve Docker sonraki sürüm.

## Pratik

[İki faturalı örneği](customer_feature_example.md) kendin hesapla. “Neden recency 25 değil 24 gün?”, “Bir faturanın 10 ürünü varsa frequency kaç olur?”, “Testte daha iyi eşik görünürse neden değiştirmiyoruz?” sorularını kodu ezberlemeden açıklamaya çalış. Öğrenciyle inceleme TODO'su bu pratik tamamlanana kadar açıktır.
