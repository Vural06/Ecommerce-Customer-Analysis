# E-ticaret Müşteri Analitiği

## Project Overview

E-ticaret müşterilerinin gelecek dönemde tekrar alışveriş yapmama riskini tahmin etmeyi amaçlayan bir veri bilimi portföy projesidir. Amaç; veri hazırlama, SQL ile özellik üretme, segmentasyon ve model değerlendirme kararlarını mülakatlarda açıklanabilecek, tekrarlanabilir bir çalışma içinde göstermektir.

## Projenin durumu

Veri seti olarak **UCI Online Retail II** seçildi. Veri profili, fatura/müşteri özetleri, zaman temelli SQL özellikleri, RFM ve model karşılaştırması tamamlandı. Çoğunluk referansı, lojistik regresyon ve tek Random Forest alternatifi aynı zaman ayrımında değerlendirildi. Model/eşik seçimi doğrulamada yapıldı, ardından test sonuçları raporlandı. Dashboard henüz yapılmadı; kampanya etkisi veya iş kazancı ölçülmedi.

Test edilen ortam Windows ve Python 3.13.9'dur. Doğrudan kullanılan paketler pandas 3.0.6, numpy 2.5.3, openpyxl 3.1.5, scikit-learn 1.9.1 ve model kaydı için joblib 1.6.0'dır. Geçişli bağımlılıklar dahil 13 paket sürümü `requirements.txt` içinde sabitlenmiş ve mevcut ortamla karşılaştırılmıştır. SQLite, unittest ve indirme araçları Python standart kütüphanesindendir. Hedef ve zaman pencereleri belirlenmiştir: 180 gün gözlem, 90 gün hedef; ayrıntılar [problem tanımında](docs/problem_definition.md).

## Dataset

- Kaynak: [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
- Resmî indirme: [UCI ZIP arşivi](https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip).
- İndirme tarihi: **19 Eylül 2026**, 19:32:19 UTC (22:32:19 Türkiye saati).
- Atıf: Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D).
- Lisans: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Yeniden kullanımda kaynak ve lisans belirtilmeli, değişiklik yapıldıysa açıklanmalıdır.
- Ham Excel değiştirilmez. ZIP içindeki Excel'in baytları doğrudan çıkarılır. İndirme zamanı (UTC), dosya boyutu ve SHA-256 değerleri yerel `data/raw/download_metadata.json` dosyasında tutulur.

UCI açıklamasındaki sütun adları ile dosyanın gerçek başlıkları farklı olabilir. Betik gerçek başlıkları ve pandas'ın okuduğu veri tiplerini raporlar. `Customer ID` müşteri tanımlayıcısıdır; ham müşteri kayıtları Git'te yayımlanmaz. Kategori, indirim, ödeme ve teslimat alanları varsayılmaz.

Dosyanın veri sözlüğü:

| Sütun | Anlam |
| --- | --- |
| Invoice | Fatura kimliği; C/c başlangıcı iptal işaretidir |
| StockCode | Ürün kodu |
| Description | Ürün açıklaması |
| Quantity | Fatura satırındaki ürün miktarı |
| InvoiceDate | Fatura tarih ve saati; saat dilimi belirtilmemiştir |
| Price | Birim fiyat (İngiliz sterlini) |
| Customer ID | Müşteri kimliği; eksik olabilir |
| Country | Müşterinin ülkesi |

## Project Structure

```text
configs/        Eğitim döneminden hesaplanan RFM eşikleri
docs/           Problem tanımı, öğrenme örneği ve mülakat notları
exercises/      Veri tanıma ve fatura/müşteri özetleri
reports/        Küçük, toplulaştırılmış analiz ve kontrol raporları
scripts/        İndirme, EDA, SQL, segmentasyon ve model betikleri
sql/            Geçmiş özellik ve gelecek hedef sorguları
tests/          Zaman sınırı, sızıntı ve tekrar üretilebilirlik testleri
README.md       Amaç, sonuçlar ve çalıştırma sırası
requirements.txt Sabitlenmiş Python bağımlılıkları
TODO.md         Tamamlanan ve açık kalan işler
```

Çalıştırma sırasında `data/` ve `artifacts/` yerel olarak oluşturulur; GitHub'a gönderilmez. Projede henüz notebook yok; mevcut akış küçük Python betikleriyle çalışır. Sonradan eklenen gerekli notebooklar korunur, checkpoint ve çıktı önbellekleri dışlanır.

## How to Run

Python 3.13 kurulu olmalıdır. Aşağıdaki örnek Windows PowerShell içindir; `py -3.13` kayıtlı bir Python 3.13 yorumlayıcısı gerektirir. Başlatıcı kurulumunuzu bulamıyorsa çalışan Python 3.13 yorumlayıcınızı kullanarak `.venv` oluşturun. Proje klasöründe ortamı aktive etmek gerekmez:

```powershell
git clone https://github.com/Vural06/Ecommerce-Customer-Analysis.git
cd Ecommerce-Customer-Analysis
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/download_data.py
.\.venv\Scripts\python.exe scripts/profile_data.py
.\.venv\Scripts\python.exe exercises/02_fatura_ve_musteri_ozeti.py
.\.venv\Scripts\python.exe scripts/analyze_data_quality.py
.\.venv\Scripts\python.exe scripts/build_customer_features.py
.\.venv\Scripts\python.exe scripts/create_learning_example.py
.\.venv\Scripts\python.exe scripts/build_rfm_segments.py
.\.venv\Scripts\python.exe scripts/train_baseline.py
.\.venv\Scripts\python.exe scripts/compare_models.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/verify_project.py
```

Klasörü zaten indirdiyseniz clone/cd, mevcut `.venv` varsa ortam oluşturma satırlarını atlayın. Python işlemlerinin kalanında projenin `.venv` yorumlayıcısı kullanılır. Ham/işlenmiş veri, model ve rapor klasörleri gerektiğinde oluşturulur. Veri indirme internet gerektirir; kalan adımlar yerel dosyalarla çalışır. İlk Excel okuması büyük dosya nedeniyle zaman alabilir.

13 test, küçük sentetik veriyle başlangıçta bulunmayan çıktı klasörlerinde tüm akışı doğrular. Ayrıca mevcut `.venv` değiştirilmeden bağımsız bir Python 3.13.9 sanal ortamına requirements.txt kuruldu; pip check ve 13 test geçti. Ayrıntılar [bağımsız kurulum raporunda](reports/independent_installation.md). Mevcut ham veri/çıktıların tutarlılığı `verify_project.py` ile kontrol edilir. Bağımsız kurulum aynı Windows makinesinde pip önbelleği kullanılarak yapıldı; başka makine/işletim sistemi için uyumluluk iddiası değildir.

Paketler zaten kuruluysa pip install komutuna gerek yoktur. İndirme betiği mevcut Excel'i yeniden indirmez; kayıtlı SHA-256 varsa doğrular. Excel yok ama ZIP mevcutsa yeniden indirmeden arşivi kullanır. Bozuk veya hash değeri değişmiş mevcut Excel'in üzerine yazmaz. Yarım indirmeler geçici dosyada tutulur. İndirme için internet gerekir; profil betiği yerel dosyayla çalışır.

Çıktı: [İlk veri inceleme raporu](reports/data_profile.md). Rapor bütün çalışma sayfalarını, ham birleşimi, eksikleri, iptalleri, tekrarları, sayfalar arası örtüşmeyi ve müşteri başına benzersiz alışveriş faturası dağılımını kapsar. Betik her çalıştırmada raporu günceller; temizlenmiş veri üretmez.

İlk ham profil: iki sayfada toplam 1.067.371 satır, 5.942 bilinen müşteri ve iptaller dahil 53.628 benzersiz fatura var. Tarih aralığı 1 Aralık 2009–9 Aralık 2011. Sayfalar Aralık 2010'da örtüşüyor; 22.202 farklı kayıt her iki sayfada da aynen bulunuyor. Ham sayfa birleşiminde ilk kopya dışındaki tam tekrar sayısı 34.335. Profil betiği bunları korur; sonraki özet betiği yalnızca sayfalar arası eşleşen kopyaları giderir. Müşteri kimliği ham satırların %22,7669'unda eksik. Ayrıntılı sayımlar, oran paydaları ve filtreler raporda bulunur.

İlk sürüm alışveriş filtresi: müşteri ve fatura kimliği dolu, fatura C/c ile başlamıyor, `Quantity > 0` ve `Price > 0`. En az bir satırı bu koşulları sağlayan fatura sayılır; müşteri başına benzersiz fatura kullanılır. İadeler satışlarla netleştirilmez. Rapordaki tüm dönem tekrar alışveriş oranı, sabit bir gelecek dönem hedefi ya da model performansı değildir.

## Exploratory Data Analysis

[EDA raporu](reports/data_quality_eda.md) filtrelerin ayrık etkisini, müşteri/fatura dağılımlarını, alışveriş aralıklarını, aylık hareketi ve aykırı değer duyarlılığını içerir. Sayfa içindeki eşit kalemlerin yanlış olduğunu doğrulayacak satır kimliği yoktur; 11.620 fazla geçerli kalem korunur. Brüt tutara katkıları 56.746,91 GBP (%0,3255). Büyük miktar/tutarlar otomatik silinmez; eğitim faturalarından hesaplanan IQR sınırları yalnızca tanısal işaretlemedir.

Temel bulgular: fatura tutarı medyanı 303,60 GBP; müşteri başına fatura medyanı 3; ardışık fatura aralığı medyanı 24,74 gün. En yüksek harcamalı yaklaşık %1'lik müşteri grubu brüt tutarın %31,89'unu oluşturur. Aralık 2011 kısmi ay olduğu için tam aylarla hacim karşılaştırmasına katılmaz. Bu bulgularla model/özellik/eşik ayarı yapılmadı.

## Data Cleaning

```powershell
.\.venv\Scripts\python.exe exercises/02_fatura_ve_musteri_ozeti.py
```

Betik ilk sayfa için ve iki sayfanın birleşimi için ayrı özetler üretir. Sayfalar arası tam eşleşen kayıtlar kopya sırasıyla eşleştirilir; ikinci sayfadaki eşleşen kopyalar çıkarılır. Aynı sayfa içindeki tekrarlar korunur. Bu çalışma varsayımı, tüm eşit satırların hatalı olduğunu kanıtlamaz.

`Quantity × Price` ürün tutarları müşteri ve fatura kimliğine göre toplanır. Fatura tarih tutarlılığı kontrol edilir; farklı zamanlar varsa ilk/son zaman ve zaman damgası sayısı saklanır. Müşteri özeti alışveriş faturası sayısı, brüt harcama ve ilk/son alışveriş tarihini içerir.

Çıktılar `data/processed/first_sheet_invoices.csv`, `first_sheet_customers.csv`, `combined_invoices.csv` ve `combined_customers.csv` dosyalarıdır; tamamı Git dışında tutulur. Kararlar ve kontroller [Fatura ve müşteri özetleri raporunda](reports/invoice_customer_summary.md) bulunur. Brüt tutarlar iadelerle netleştirilmez ve korunan tekrarları içerir. Bu özetler tüm gözlem dönemine aittir; zaman temelli model özellikleri değildir.

Birleşimde sayfalar arası 22.523 eşleşen kopya çıkarıldı; 1.044.848 girdi satırından filtrelerle 791.045 ürün satırı kaldı. Fatura özeti 36.969 satır, müşteri özeti 5.878 satır içerir. Birleşik dönemde 64 faturada farklı tarih/saatler vardır; ilk ve son zaman ayrı saklanır. Korunan tam tekrarların brüt tutara katkısı 56.746,91 GBP'dir; bu tutar hatalı kayıt olduğuna veya kayba ilişkin kanıt değildir.

## Amaç ve hedef tanımı

Başlangıç tanımı ve zaman sınırları [Problem tanımı](docs/problem_definition.md) içinde belgelendi: son 180 günde alışveriş yapan müşterinin sonraki 90 günde alışveriş yapmama durumu. Bunlar ilk sürüm varsayımlarıdır.

## Zaman temelli SQL özellikleri

Python ile gelen SQLite kullanılır; ek veritabanı paketi gerekmez. Kod basit Python betikleri ve ayrı SQL dosyalarından oluşur. Yeni bir altyapı katmanı veya API eklenmedi.

```powershell
.\.venv\Scripts\python.exe scripts/build_customer_features.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Özellik sorgusu `sql/customer_features.sql`; ayrı hedef sorgusu `sql/customer_labels.sql`. Özellikler recency, 180 günlük alışveriş sıklığı/brüt harcama, ortalama fatura tutarı ve miktardır. Hedef, gelecekteki 90 günde alışveriş yoksa 1'dir. İlk/son alışveriş zamanları denetim için saklanır.

Train, validation ve test için ayrı özellik/hedef CSV'leri ve `data/processed/customer_analytics.sqlite` üretilir. Tüm veri çıktıları Git dışındadır. Sonuçlar [SQL özellikleri raporunda](reports/sql_features.md) bulunur. Gelecek faturaların özellikleri değiştirmediği, sınır tarihlerinin doğru işlendiği ve tamamlanmamış hedeflerin reddedildiği test edildi.

## RFM Segmentation

```powershell
.\.venv\Scripts\python.exe scripts/build_rfm_segments.py
```

RFM'nin her boyutu 1–3 puan alır. Recency'de düşük değer, frequency ve monetary'de yüksek değer daha yüksek puandır. Eşikler yalnızca eğitim verisinin 1/3 ve 2/3 kantillerinden hesaplanıp `configs/rfm_thresholds.json` içine kaydedilir; validation/testte aynı eşikler kullanılır. Aynı değere sahip müşteriler aynı puanı alır; gruplar eşit büyüklükte olmayabilir.

Altı basit segment kuralı, dönem başına müşteri sayısı/pay ve medyan R/F/M değerleri [RFM raporunda](reports/rfm_segments.md) açıklanır. Train/validation'daki gelecek alışveriş oranları betimsel olarak raporlanır; test hedefleri okunmaz. Segmentler risk olasılığı veya kampanya etkisi değildir. Yerel çıktı dosyaları `data/processed/*_rfm.csv` ve `*_rfm_summary.csv` altında tutulur.

## Tahmin sırasında bilinen bilgiler

Bir tahmin tarihi itibarıyla bilinen müşteri ve işlem geçmişinden, müşterinin izleyen dönemde alışveriş yapmama olasılığını tahmin etmek hedeflenmektedir. Faturalar son kalem zamanı itibarıyla kullanılabilir sayılır; gelecekte tamamlanan faturanın toplam tutarı geçmiş özelliklere eklenmez. Belirli bir dönemde alışveriş yapmamak, müşterinin kalıcı olarak kaybedildiği anlamına gelmez.

## Machine Learning

```powershell
.\.venv\Scripts\python.exe scripts/train_baseline.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

scikit-learn 1.9.1 ve bağımlılıkları proje `.venv` ortamına kuruldu; sürümler `requirements.txt` içinde sabitlendi. Çoğunluk sınıfı referansı ile `StandardScaler + LogisticRegression` karşılaştırılır. Beş sayısal SQL özelliği kullanılır; müşteri kimlikleri ve gelecek dönem alanları model girdisi değildir. Ölçekleyici yalnızca eğitimde öğrenir.

Doğrulamada çoğunluk referansı AP=0,5208 / F1=0,6849; lojistik regresyon seçilen 0,6 eşikle AP=0,7203 / F1=0,7456 üretti. Eşik küçük bir aday listesinde validation F1 ile seçildi; aynı veride seçim yapıldığı için bu sonuç nihai bağımsız başarı değildir. Bu betik test verisini okumaz; test sonuçları sonraki karşılaştırma raporunda yer alır.

[Başlangıç modeli raporu](reports/baseline_model.md) metrikleri, eşik adaylarını, hata matrisini ve katsayıları açıklar. Kayıtlı model `artifacts/logistic_baseline.joblib`, ayarlar `artifacts/baseline_metadata.json`, müşteri tahminleri `data/processed/validation_baseline_predictions.csv` içindedir; hepsi Git dışında tutulur. Bu skorlar kampanya kazancı anlamına gelmez.

## Results

```powershell
.\.venv\Scripts\python.exe scripts/compare_models.py
```

Tek Random Forest alternatifi kullanılır (100 ağaç, max_depth=5, min_samples_leaf=20). Geniş ayar araması yoktur. Tüm modeller aynı beş özelliği kullanır. Doğrulama AP skoruna göre Random Forest seçildi; F1 ile seçilen eşik 0,5. Seçim test dosyaları okunmadan kaydedildi; testte model veya eşik değiştirilmedi.

| Test modeli | AP | F1 |
| --- | --- | --- |
| Çoğunluk referansı | 0,3929 | 0,5641 |
| Lojistik regresyon | 0,5821 | 0,6390 |
| Random Forest | 0,5858 | 0,6422 |

İki öğrenen modelin farkı küçüktür; istatistiksel üstünlük gösterilmedi. Seçilen modelin test precision/recall değerleri %49,17/%92,56'dır; çok sayıda yanlış pozitif üretir. Eğitim/doğrulama/test sonuçları, hata matrisi ve sınırlılıklar [Model karşılaştırması raporunda](reports/model_comparison.md) bulunur.

Test artık değerlendirilmiştir. Sonraki model değişikliklerinde bu dönem yeni ve görülmemiş test olarak sunulmaz. Seçilen model `artifacts/selected_model.joblib`, seçimi ve metrikleri `artifacts/model_comparison_metadata.json`, test tahminleri `data/processed/test_model_predictions.csv` içindedir. Veri ve model çıktıları Git dışındadır. Ham veriye dokunulmadı.

## Technologies Used

Python 3.13; pandas ve numpy (veri işleme), openpyxl (Excel okuma), SQLite (SQL), scikit-learn (lojistik regresyon ve Random Forest), joblib (yerel model kaydı), unittest (testler), Git/GitHub (sürüm kontrolü). requirements.txt, kullanılan doğrudan paketler ve gerekli geçişli bağımlılıkları sabitler. Streamlit henüz kurulmadı; planlanan dashboard aracıdır.

## İlk sürüm kapsamı

Proje junior seviyesinde açıklanabilir bir portföy olarak ilerler: pandas veri hazırlama, SQLite sorguları, basit RFM kuralları ve scikit-learn başlangıç modelleri. Küçük fonksiyonlar ve Türkçe yorumlar kullanılır. Başlangıçta kapsamlı hiperparametre araması veya ek altyapı kurulmaz; veri sızıntısı ve zaman sınırı kontrolleri korunur.

- Veri kalitesi kontrolleri, temizleme ve keşifsel veri analizi (EDA).
- SQL ile müşteri bazında özellik oluşturma.
- RFM: son alışverişten geçen süre, alışveriş sıklığı ve parasal değer üzerinden müşteri segmentasyonu.
- Basit bir başlangıç modeli ve alternatif modelin karşılaştırılması.
- Zaman temelli eğitim, doğrulama ve test ayrımı; veri sızıntısının önlenmesi.
- Müşteri segmentlerini, risk tahminlerini ve değerlendirme sonuçlarını sunan Streamlit dashboard.

## Future Improvements

- Streamlit dashboard: veri özeti, RFM segmentleri, risk dağılımı ve model değerlendirmesi.
- Yeni zaman pencereleriyle genelleme ve olasılık kalibrasyonu; görülmüş test dönemi yeni bir bağımsız test olarak kullanılmayacak.
- İade eşleştirme ve kampanya kapasitesine uygun eşik incelemesi, uygun yeni değerlendirme tasarımıyla.
- API ve Docker sonraki sürümde.

## Çalışma ilkeleri

- Küçük ve doğrulanabilir adımlar at; her adımın amacını ve sonucunu kaydet.
- Özellikleri yalnızca tahmin tarihinde bilinen bilgilerden üret. Gelecek dönemdeki işlemleri yalnızca hedefi oluşturmak için kullan.
- Hedef dönemi tamamen gözlenemeyen müşterileri otomatik olarak alışveriş yapmamış sayma.
- Ön işleme ve model seçiminde test verisini kullanma; test dönemini son değerlendirme için ayır.
- Başarı metriğini hedef, sınıf dağılımı ve kullanım amacı doğrultusunda seç; sonuç uydurma.
- Risk tahmini, kampanyanın etkisini göstermez. Gerçek bir deney olmadan kampanya kazancını kanıtlanmış sonuç olarak sunma.
- Gizli bilgileri, sanal ortamları ve ham verileri Git'e ekleme. Veri kaynağını ve veriyi yeniden edinme adımlarını belgele.

## Hazırlık dosyaları

- `TODO.md`: aşamalara ayrılmış çalışma listesi.
- `.gitignore`: yerel ortam, gizli bilgiler ve veri dosyaları için hariç tutma kuralları.

Ham veri `data/raw/` altında tutulur. Bu dizin ve `.venv/` Git dışında tutulur; küçük örnek veriler gerekirse anonimleştirme ve paylaşım uygunluğu kontrolünden sonra ayrıca ele alınır.

## Öğrenme ve yayımlama notları

- [İki faturalı müşteri örneği](docs/customer_feature_example.md): recency/frequency/monetary, ortalama fatura ve miktar adım adım SQL ile karşılaştırılır. Özgün kimlikler yerel tutulur. Öğrenciyle elle inceleme maddesi sen inceleyene kadar açık kalır.
- [Mülakat anlatımı](docs/interview_notes.md): açıklaman gereken kararlar ve ölçülmüş sonuçlar.
- [Yayımlama kontrolü](reports/publish_readiness.md) ve [çıktı doğrulaması](reports/output_verification.md).

GitHub'a kod, SQL, testler, `configs/` içindeki eğitim eşikleri, bağımlılık listesi ve toplulaştırılmış Markdown belgeleri eklenir. `.env`, erişim anahtarları, `.venv/`, `data/`, SQLite ve `artifacts/` eklenmez. Dashboard henüz tamamlanmadı; mevcut sürüm analiz/model portföyü olarak yayımlanabilir. Kod için ayrı bir yeniden kullanım lisansı seçilmedi; verinin CC BY 4.0 lisansı korunur.
