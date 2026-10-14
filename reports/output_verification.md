# Yayımlama öncesi çıktı kontrolü

Bu kontrol mevcut sonuçların tutarlılığını doğrular; yeni test deneyi veya model seçimi değildir. Ham dosya SHA-256 kayıtla eşleşti.

- Üç dönemin tüm SQL özellik/etiket satırları CSV ve SQLite ile eşleşti; hedef pencereleri çakışmıyor.

- RFM eğitim eşikleri, üç dönemin tüm puan/segmentleri ve segment müşteri sayıları eşleşti.

- Kayıtlı olasılıklar, eşikler, AP/F1/precision/recall ve hata matrisleri yeniden hesaplandı: tümü eşleşti. Model eğitilmedi veya ayarlanmadı.

- requirements.txt içindeki 13 paket sürümü mevcut ortamla bire bir eşleşti.

- 36 Git adayı tarandı; tanınan anahtar kalıbı bulunmadı. Yerel veri/model/ortam dosyaları adaylarda yok.


## GitHub'a eklenecek mevcut dosyalar

- `.gitignore`
- `README.md`
- `TODO.md`
- `configs/rfm_thresholds.json`
- `docs/customer_feature_example.md`
- `docs/interview_notes.md`
- `docs/problem_definition.md`
- `exercises/01_veriyi_tanima.py`
- `exercises/02_fatura_ve_musteri_ozeti.py`
- `reports/baseline_model.md`
- `reports/data_profile.md`
- `reports/data_quality_eda.md`
- `reports/independent_installation.md`
- `reports/invoice_customer_summary.md`
- `reports/model_comparison.md`
- `reports/output_verification.md`
- `reports/publish_readiness.md`
- `reports/rfm_segments.md`
- `reports/sql_features.md`
- `requirements.txt`
- `scripts/analyze_data_quality.py`
- `scripts/build_customer_features.py`
- `scripts/build_rfm_segments.py`
- `scripts/compare_models.py`
- `scripts/create_learning_example.py`
- `scripts/download_data.py`
- `scripts/profile_data.py`
- `scripts/train_baseline.py`
- `scripts/verify_project.py`
- `sql/customer_features.sql`
- `sql/customer_labels.sql`
- `tests/test_baseline_model.py`
- `tests/test_model_comparison.py`
- `tests/test_reproducibility.py`
- `tests/test_rfm_segments.py`
- `tests/test_sql_features.py`


Anahtar taraması belirli kalıplarla sınırlıdır; her gizli değer türünü tespit ettiğine dair garanti değildir. Dosya içerikleri kontrolde ifşa edilmez. Commit/push/depo oluşturulmadı.
