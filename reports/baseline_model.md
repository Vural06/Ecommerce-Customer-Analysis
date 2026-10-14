# Başlangıç modelleri

## Kapsam ve yöntem

Eğitim: 3415 müşteri; doğrulama: 3049 müşteri. scikit-learn 1.9.1. Test dosyaları bu betikte okunmaz.

Hedef=1: sonraki 90 günde alışveriş yapmama. Referans model her müşteriye eğitim çoğunluk sınıfını verir; risk puanı eğitimdeki sınıf oranıdır, müşteri bazında değişmez. Basit model StandardScaler + LogisticRegression (C=1, max_iter=1000). Hiperparametre araması yoktur.

Yalnızca beş sayısal SQL özelliği kullanılır: `recency_days`, `frequency_180d`, `monetary_180d_gbp`, `average_invoice_amount_gbp`, `quantity_180d`. Kimlikler, tarihler, gelecek fatura sayısı ve RFM segmentleri modele verilmez. Ölçekleyici yalnızca train üzerinde öğrenir; validation fit işlemi görmez.

## Sonuçlar

| Model/bölüm | AP | ROC-AUC | Precision | Recall | F1 | Accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| majority_validation | 0.5208 | 0.5000 | 0.5208 | 1.0000 | 0.6849 | 0.5208 |
| logistic_train_0.5 | 0.8084 | 0.7576 | 0.7279 | 0.9108 | 0.8091 | 0.7321 |
| logistic_validation_0.5 | 0.7203 | 0.7461 | 0.6040 | 0.9395 | 0.7353 | 0.6478 |
| logistic_validation_selected | 0.7203 | 0.7461 | 0.6413 | 0.8904 | 0.7456 | 0.6835 |

Average precision (AP), precision-recall eğrisinin eşiklere göre ağırlıklı özetidir; trapez PR-AUC hesabıyla bire bir aynı değildir. Sabit puanlı referansın AP'si değerlendirilen dönemin hedef=1 oranıdır. Precision: riskli işaretlenenlerin ne kadarı gerçekten alışveriş yapmadı? Recall: alışveriş yapmayanların ne kadarı yakalandı? F1 iki oranı dengeler. Accuracy sınıf dağılımından etkilenir. Eğitim skoru genel başarı değildir.

## Karar eşiği

| Eşik | Precision | Recall | F1 |
| --- | --- | --- | --- |
| 0.2 | 0.5508 | 0.9906 | 0.7079 |
| 0.3 | 0.5643 | 0.9843 | 0.7173 |
| 0.4 | 0.5821 | 0.9666 | 0.7266 |
| 0.5 | 0.6040 | 0.9395 | 0.7353 |
| 0.6 | 0.6413 | 0.8904 | 0.7456 |
| 0.7 | 0.6846 | 0.7462 | 0.7141 |
| 0.8 | 0.7503 | 0.4049 | 0.5260 |

Seçilen eşik: **0.6**. Seçim yalnızca validation F1 üzerinden yapıldı; eşit F1'da yüksek eşik tercih edilir. İş maliyeti ve kampanya kapasitesi bilinmediğinden bu eşik operasyonel olarak en uygun eşik iddiası taşımaz. Seçim ve ölçüm aynı validation üzerinde olduğundan seçilen F1 iyimser olabilir; test sonuçları ayrı model karşılaştırması raporunda yer alır.

## Doğrulama hata matrisi (seçilen eşik)

| Gerçek / tahmin | 0: alışveriş yapar | 1: alışveriş yapmaz |
| --- | --- | --- |
| 0: alışveriş yaptı | 670 | 791 |
| 1: alışveriş yapmadı | 174 | 1414 |

## Lojistik regresyon katsayıları

| Özellik | Standardize katsayı |
| --- | --- |
| recency_days | 0.2389 |
| frequency_180d | -1.8215 |
| monetary_180d_gbp | -0.2767 |
| average_invoice_amount_gbp | -0.1912 |
| quantity_180d | 0.2385 |

Pozitif katsayı, diğer girdiler sabitken hedef=1 yönündeki ilişkiyi gösterir. Katsayılar nedensel etki değildir; sıklık, harcama ve ortalama fatura tutarı birbiriyle ilişkilidir. Buradan bağımsız iş etkisi veya kesin özellik önemi çıkarılamaz.

## Sınırlılıklar ve sonraki adım

Başlangıç karşılaştırması yalnızca bir eğitim ve bir doğrulama tarihine dayanır. Müşteriler dönemler arasında tekrar bulunabilir. Brüt tutarlar iadelerle netleştirilmemiştir; sayfa içi tekrarlar korunur. Ham parasal/miktar girdileri aykırı değerlerden etkilenebilir. Olasılıklar ayrıca kalibre edilmedi; risk sıralaması ve karar eşiği başlangıç amaçlıdır. Kampanya kazancı ölçülmedi.

Bu başlangıç betiği test verisini okumaz. Tek alternatif model ve sabit kararlarla test değerlendirmesi scripts/compare_models.py içinde yapılır. Güncel sonuçlar reports/model_comparison.md içindedir.

## Yerel çıktılar

`artifacts/logistic_baseline.joblib`, `artifacts/baseline_metadata.json` ve `data/processed/validation_baseline_predictions.csv`. Model dosyaları ve müşteri tahminleri Git dışındadır.
