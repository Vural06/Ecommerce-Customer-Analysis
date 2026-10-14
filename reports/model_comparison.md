# Alternatif model ve son zaman temelli değerlendirme

## Kararlar

Modeller: çoğunluk sınıfı referansı, StandardScaler + LogisticRegression ve tek bir RandomForestClassifier. Hepsi aynı beş SQL özelliğini ve aynı train/validation/test tarihlerini kullanır. Random Forest için 100 ağaç, max_depth=5, min_samples_leaf=20, random_state=42; başka ayar denenmedi. Ağaç modeli ölçekleme gerektirmez.

İki öğrenen modelin karar eşiği validation F1 ile 0,2–0,8 adaylarından seçilir. Model seçiminde birincil ölçüt validation average precision (AP), eşitlikte F1, yine eşitse daha basit lojistik regresyondur. Bu kurallar test dosyaları okunmadan uygulanıp kaydedilir. Validation üzerinde yeniden eğitim yapılmaz; tüm modeller yalnızca train'de öğrenir.

Veri büyüklükleri: train=3415, validation=3049, test=2772. Hedef=1 oranları: %62.34, %52.08, %39.29.

## Eğitim (validation'da seçilen sabit eşiklerle)

| Model | Eşik | AP | ROC-AUC | Precision | Recall | F1 | Accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| majority | Çoğunluk | 0.6234 | 0.5000 | 0.6234 | 1.0000 | 0.7680 | 0.6234 |
| logistic | 0.6 | 0.8084 | 0.7576 | 0.7579 | 0.8220 | 0.7886 | 0.7253 |
| random_forest | 0.5 | 0.8442 | 0.7929 | 0.7604 | 0.8854 | 0.8181 | 0.7546 |

## Doğrulama

| Model | Eşik | AP | ROC-AUC | Precision | Recall | F1 | Accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| majority | Çoğunluk | 0.5208 | 0.5000 | 0.5208 | 1.0000 | 0.6849 | 0.5208 |
| logistic | 0.6 | 0.7203 | 0.7461 | 0.6413 | 0.8904 | 0.7456 | 0.6835 |
| random_forest | 0.5 | 0.7284 | 0.7494 | 0.6257 | 0.9213 | 0.7453 | 0.6720 |

Testten önce seçilen model: **random_forest**, karar eşiği **0.5**. Eşik ve model seçimi aynı doğrulama verisinde yapıldığından doğrulama skorları iyimser olabilir.

## Eşik adayları

### logistic

| Eşik | Precision | Recall | F1 |
| --- | --- | --- | --- |
| 0.2 | 0.5508 | 0.9906 | 0.7079 |
| 0.3 | 0.5643 | 0.9843 | 0.7173 |
| 0.4 | 0.5821 | 0.9666 | 0.7266 |
| 0.5 | 0.6040 | 0.9395 | 0.7353 |
| 0.6 | 0.6413 | 0.8904 | 0.7456 |
| 0.7 | 0.6846 | 0.7462 | 0.7141 |
| 0.8 | 0.7503 | 0.4049 | 0.5260 |

### random_forest

| Eşik | Precision | Recall | F1 |
| --- | --- | --- | --- |
| 0.2 | 0.5501 | 0.9956 | 0.7087 |
| 0.3 | 0.5760 | 0.9836 | 0.7265 |
| 0.4 | 0.6079 | 0.9471 | 0.7405 |
| 0.5 | 0.6257 | 0.9213 | 0.7453 |
| 0.6 | 0.6421 | 0.8835 | 0.7437 |
| 0.7 | 0.6878 | 0.7254 | 0.7061 |
| 0.8 | 0.7407 | 0.4370 | 0.5497 |

## Son test değerlendirmesi

| Model | Eşik | AP | ROC-AUC | Precision | Recall | F1 | Accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| majority | Çoğunluk | 0.3929 | 0.5000 | 0.3929 | 1.0000 | 0.5641 | 0.3929 |
| logistic | 0.6 | 0.5821 | 0.7225 | 0.5008 | 0.8825 | 0.6390 | 0.6082 |
| random_forest | 0.5 | 0.5858 | 0.7268 | 0.4917 | 0.9256 | 0.6422 | 0.5949 |

Test sonuçları yalnızca sabit modellerin raporlanması içindir; testte farklı model daha yüksek skor alsa bile seçim değiştirilmez. Bu test artık görülmüştür: sonraki değişikliklerde bağımsız, görülmemiş test olarak kullanılamaz. Betik tekrar çalıştırılırsa aynı sabit karşılaştırma yeniden üretilir; yeni bir bağımsız deney oluşmaz.

## Seçilen modelin test hata matrisi

| Gerçek / tahmin | 0 | 1 |
| --- | --- | --- |
| 0: alışveriş yaptı | 641 | 1042 |
| 1: alışveriş yapmadı | 81 | 1008 |

## Hata grupları

| Grup | Müşteri | Medyan R (gün) | Medyan F | Medyan M (GBP) |
| --- | --- | --- | --- | --- |
| Yanlış pozitif (alışveriş yaptı, riskli işaretlendi) | 1042 | 69.00 | 1.00 | 391.04 |
| Yanlış negatif (alışveriş yapmadı, risksiz işaretlendi) | 81 | 26.00 | 4.00 | 1390.27 |

Hata medyanları tanısal betimlemedir; hata nedenini veya nedensel ilişkiyi kanıtlamaz. Bu tabloyla model yeniden ayarlanmadı. Bireysel müşteri bilgileri raporda yayımlanmaz.

## Yorum ve sınırlılıklar

Random Forest ile lojistik regresyon arasındaki test AP farkı 0.0037; bu küçük fark için istatistiksel üstünlük testi yapılmadı. Seçilen modelin test precision değeri %49.17, recall değeri %92.56. Bu eşik birçok alışveriş yapmayan müşteriyi yakalarken çok sayıda yanlış pozitif üretir.

AP sıralama kalitesini, precision/recall/F1 sabit karar eşiğinin davranışını gösterir. AP, trapez PR-AUC ile aynı hesap değildir. Sabit risk puanlı çoğunluk referansının AP'si ilgili dönemin hedef oranına eşittir. Eğitim/doğrulama farkı genelleme sorununun bir işareti olabilir; dönemler farklı olduğu için farkın tamamı ezberlemeye bağlanamaz.

Hedef oranları zamanla değişiyor. Tek test tarihi mevsimselliği veya kalıcı performansı ölçmez. Aynı müşteriler farklı dönemlerde bulunabilir; bu mevcut müşterilere tekrar tahmin yapma senaryosudur. İadeler netleştirilmedi, sayfa içi tekrarlar korundu ve olasılıklar kalibre edilmedi. Kampanya etkisi ölçülmedi. Bu sonuçlar üretim performansı veya kanıtlanmış iş kazancı değildir.

## Çalıştırma ve yerel çıktılar

`.venv\Scripts\python.exe scripts/compare_models.py`. Seçim bilgisi `artifacts/model_comparison_metadata.json`, model `artifacts/selected_model.joblib`, alternatif `artifacts/random_forest.joblib`, müşteri tahminleri `data/processed/test_model_predictions.csv`. Hepsi Git dışında tutulur.
