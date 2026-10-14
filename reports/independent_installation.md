# Bağımsız sanal ortam kurulum kontrolü

Kontrol tarihi: 14 Ekim 2026. Sonuç: mevcut requirements.txt bağımsız ortamda kuruldu ve testler geçti. Çalışan proje `.venv` ortamı korunmuştur.

## Ortam ve kurulum

- Windows, Python **3.13.9**, temel yorumlayıcı Anaconda Python.
- Projenin Git dışındaki data/ klasöründe benzersiz geçici sanal ortam oluşturuldu; system_site_packages=False.
- Mevcut requirements.txt sürümleri değiştirilmeden 13 paket geçici ortama kuruldu. Paket wheel dosyaları pip önbelleğinden kullanıldı; mevcut .venv/site-packages kopyalanmadı veya paylaşılmadı.
- pandas, numpy, openpyxl, scikit-learn ve joblib dosya yollarının geçici ortamın kendi site-packages klasöründe olduğu doğrulandı. requirements.txt içindeki bütün sürümler bu ortamın kurulu paketleriyle eşleşti.
- pip check: **No broken requirements found**.
- unittest discover -s tests -v: **13/13 test geçti**, çıkış kodu 0.

İlk ortam hazırlama denemesi sandbox içinde ensurepip aşamasında başarısız oldu. Aynı hedefin izinli tekrarında ortam oluşturuldu, kurulum ve testler başarılı oldu. Belirli bir requirements paketinin sürüm/uyumluluk hatası görülmedi; hiçbir sürüm değiştirilmedi.

## Yapılan işlemler

Yeni ortamdaki python.exe ile şu işlemler yapıldı:

```powershell
& $geciciPython --version
& $geciciPython -m pip install --retries 1 --timeout 60 -r requirements.txt
& $geciciPython -m pip check
& $geciciPython -m unittest discover -s tests -v
```

$geciciPython, yalnızca bu kontrol için oluşturulan sanal ortamın Scripts/python.exe yoludur. Testlerin küçük model eğitimleri sentetik veride ve geçici test klasörlerinde çalıştı. Gerçek veride modeller yeniden eğitilmedi. Bu kontrol yeni bir model değerlendirmesi değildir.

## Koruma ve kapsam

Çalışan .venv'nin pip freeze çıktısı, requirements.txt, .venv/pyvenv.cfg, ham Excel ve yerel model/metadata dosyalarının hash değerleri kontrol öncesiyle karşılaştırıldı. Değişiklik bulunmadı. Sistem PATH ayarı değiştirilmedi. Commit, push veya GitHub deposu oluşturulmadı.

Bu sonuç aynı Windows makinesinde bağımsız sanal ortam ve mevcut pip önbelleğiyle doğrulandı. Başka işletim sistemi/makine veya tamamen boş indirme önbelleği için ayrıca uyumluluk iddiası değildir.

## GitHub aday listesi

Git tarafından belirlenen 36 aday dosya:

- .gitignore
- README.md
- TODO.md
- configs/rfm_thresholds.json
- docs/customer_feature_example.md
- docs/interview_notes.md
- docs/problem_definition.md
- exercises/01_veriyi_tanima.py
- exercises/02_fatura_ve_musteri_ozeti.py
- reports/baseline_model.md
- reports/data_profile.md
- reports/data_quality_eda.md
- reports/independent_installation.md
- reports/invoice_customer_summary.md
- reports/model_comparison.md
- reports/output_verification.md
- reports/publish_readiness.md
- reports/rfm_segments.md
- reports/sql_features.md
- requirements.txt
- scripts/analyze_data_quality.py
- scripts/build_customer_features.py
- scripts/build_rfm_segments.py
- scripts/compare_models.py
- scripts/create_learning_example.py
- scripts/download_data.py
- scripts/profile_data.py
- scripts/train_baseline.py
- scripts/verify_project.py
- sql/customer_features.sql
- sql/customer_labels.sql
- tests/test_baseline_model.py
- tests/test_model_comparison.py
- tests/test_reproducibility.py
- tests/test_rfm_segments.py
- tests/test_sql_features.py

__pycache__, .pyc, data, artifacts, .venv ve gizli dosyalar listede bulunmuyor. .gitignore yayımlanacak yapılandırma dosyası olarak tek nokta ile başlayan istisnadır. Tanınan anahtar kalıpları kontrolünde eşleşme yok; gizli değerler gösterilmedi.


## Geçici ortamın temizlenmesi

Kurulum kontrolü tamamlandıktan sonra geçici ortamın yolu data/ altındaki oluşturulan install_check_ klasörü olarak doğrulanıp kaldırıldı. Çalışan .venv, requirements.txt, ham Excel ve model dosyaları son hash/paket kontrolünde de değişmemiştir. Yerel denetim kaydı yalnızca Git dışındaki data/install_check_state.json içinde tutulur.
