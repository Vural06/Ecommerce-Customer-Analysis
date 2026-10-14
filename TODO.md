# Yapılacaklar

Her aşamada yapılan işlem, gerekçesi ve doğrulama sonucu kısa biçimde kaydedilecek. Bir aşama doğrulanmadan sonraki aşamaya geçilmeyecek.

## 0. İlk hazırlık

- [x] Çalışma klasörünü, mevcut dosyaları ve AGENTS.md talimatlarını kontrol et.
- [x] Python ve Git erişimini, sürüm bilgisini ve Git durumunu kontrol et.
- [x] README.md, TODO.md ve .gitignore oluştur.
- [x] Python ortamını erişilebilir hâle getir ve sürümünü doğrula. Anaconda Python 3.13.9 ile proje `.venv` ortamı oluşturuldu; Python ve pip doğrulandı.

## 1. Ortam ve veri seti kararı

- [x] Python sürümü ve bu aşamanın bağımlılıklarını belirle; sanal ortamı kur. pandas/openpyxl ve geçişli bağımlılıklar requirements.txt içinde sabitlendi.
- [x] Veri seti kararını kaydet: kullanıcı UCI Online Retail II'yi seçti; alternatif aday karşılaştırması yapılmadı.
- [x] Lisans, erişim koşulları, kişisel veri riski ve zaman kapsamını kontrol et. UCI CC BY 4.0; müşteri kimlikli ham kayıtlar Git dışında tutuluyor. Gözlenen dönem: 2009-12-01–2011-12-09.
- [x] Veri setini seç; kaynak, veri sözlüğü ve yeniden edinme adımlarını belgele.
- [x] Ham veriyi `data/raw/` altında sakla ve Git tarafından dışlandığını doğrula.
- [x] Tekrar çalıştırılabilir indirme betiğini oluştur; ikinci çalıştırmada indirmeyi atladığını doğrula.
- [x] Tüm Excel sayfalarını inceleyen betiği ve `reports/data_profile.md` raporunu oluştur.
- [x] Ham Excel'in SHA-256 değerinin inceleme öncesi/sonrası değişmediğini doğrula.

## 2. Tahmin problemini tanımlama

- [x] Müşteri ve geçerli alışveriş tanımlarını belirle; iptal/iade işlemlerinin nasıl ele alınacağını yaz.
- [x] Gözlem penceresi, tahmin tarihi ve hedef dönemini belirle: 180 gün gözlem, 90 gün hedef; üç tarihli başlangıç düzeni.
- [x] Hedefi tanımla: hedef döneminde geçerli alışveriş yoksa 1, varsa 0.
- [x] Hedef dönemi tamamlanmamış kayıtları ele alma kuralını belirle: ilgili tahmin tarihine etiket üretilmez, betik durur.
- [x] Kullanım amacı ve sınıf dağılımına göre başlangıç başarı metriklerini gerekçelendir; sayısal başarı hedefi belirlenmedi.

## 3. Veri temizleme ve EDA

- [x] Şema, veri tipleri, eksik değerler, tekrarlar ve tarih aralığını kontrol et.
- [x] İptal faturalarını, negatif/sıfır miktar ve fiyatları, sayfalar arası örtüşmeyi ve müşteri bazlı benzersiz fatura dağılımını raporla.
- [x] Sayfalar arasındaki örtüşme için çalışma kuralını uygula: tam kayıtları kopya sırasıyla eşleştir, iki sayfadaki kopya sayısının büyüğünü koru; ham Excel değişmez.
- [x] Sayfa içi tekrarları değerlendir: satır kimliği olmadığı için hatalı oldukları kesinleştirilemedi; koruma kararı ve %0,3255 brüt tutar etkisi EDA raporunda gerekçelendirildi.
- [x] Fatura tarihlerini kontrol ederek ilk sayfa ve birleşik dönem fatura/müşteri özetlerini üret ve tutar/sayım kontrollerini doğrula. Birleşimde 64 faturada farklı zaman damgaları var; ilk/son zamanlar korunuyor.
- [x] İptal, iade ve aykırı değer kararlarını belgele; ücretli alışveriş filtresi, brüt tutar, korunan uç değerler ve eğitim IQR tanısı açıklanmıştır.
- [x] Müşteri/fatura dağılımları, ardışık fatura aralıkları ve aylık değişimi incele; son kısmi ayı ayrıca işaretle.
- [x] Filtreleme öncesi/sonrası kayıt sayıları ve tutarlılık kontrollerini kaydet; örtüşme sonrası 1.044.848 → 791.045 ürün satırı, kayıtlı özetlerle eşleşir.

## 4. SQL özellikleri ve RFM

- [x] Kullanılacak SQL motorunu ve veri tablolarını belirle: SQLite, invoices, bölüm bazlı features/labels.
- [x] Yalnızca tahmin tarihinden önceki verilerle müşteri özelliklerini üret.
- [x] RFM değerlerini ve segment kurallarını oluştur; kesim noktalarını eğitim döneminden belirle. Üç puanlı sistem ve altı açıklanabilir segment kullanıldı.
- [x] Her dönemde üç müşteriyi bağımsız pandas hesabıyla SQL çıktısıyla karşılaştır.
- [ ] Bir müşteri hesabını öğrenciyle adım adım elle incele. İki faturalı örnek `docs/customer_feature_example.md` içinde hazır; öğrenci incelemesi bekleniyor.
- [x] Segmentlerin büyüklüğünü ve davranışlarını yorumla; train/validation hedef oranlarını raporla, test hedeflerini kullanma.

## 5. Zaman temelli değerlendirme ve modeller

- [x] Eğitim, doğrulama ve test dönemlerini belirle; hedef pencerelerinin sınırları aşarak sızıntı yaratmasını önle.
- [x] Aynı müşterinin farklı tarihlerde bulunmasını raporla; mevcut müşteri kullanımını ve yeni müşterilere genelleme sınırlamasını belgele.
- [x] Ön işleme adımlarını yalnızca eğitim verisine uydur: StandardScaler + LogisticRegression pipeline; validation tahminlerinde scaler değişmediği test edildi.
- [x] Basit bir referans yaklaşım ve başlangıç modeli oluştur: çoğunluk sınıfı ve lojistik regresyon, beş sayısal özellik.
- [x] Bir alternatif modeli aynı veri bölünmesi ve metriklerle karşılaştır: tek, sabit ayarlı Random Forest.
- [x] Başlangıç modelinin karar eşiğini doğrulama verisinde belirle: adaylar 0,2–0,8; F1 ile 0,6 seçildi.
- [x] Alternatif model ile model seçimini doğrulamada tamamla; kilitli model/eşiklerle testte son değerlendirmeyi gerçekleştir. Validation AP ile Random Forest, validation F1 ile 0,5 eşik seçildi.
- [x] Sınıf dağılımını, hata gruplarını, dönemlere göre performansı ve sınırlılıkları raporla. Test görülmüştür; sonraki değişikliklerde görülmemiş test olarak sunulmayacak.

## 6. Streamlit dashboard

- [ ] Veri özeti, RFM segmentleri, risk dağılımı ve model değerlendirmesi görünümlerini tasarla.
- [ ] Tarih/segment filtreleri ve açıklayıcı metinler ekle.
- [ ] Tahminlerin belirsizliğini ve kampanya etkisini kanıtlamadığını açıkla.
- [ ] Dashboard sayıları ile analiz çıktılarının tutarlılığını kontrol et.

## 7. Portföy anlatımı

- [x] Veri edinme ve ilk inceleme betiklerinin çalıştırma adımlarını ve bağımlılıklarını belgele.
- [x] SQL, RFM ve başlangıç modelinin çalıştırma adımlarını ve bağımlılıklarını ekle.
- [x] Alternatif model karşılaştırmasının çalıştırma adımlarını ekle.
- [ ] Dashboard çalıştırma adımlarını ekle.
- [x] Problem, veri, yöntem, sızıntı önlemleri ve sonuçları mülakat anlatımına dönüştür: docs/interview_notes.md.
- [x] Yalnızca ölçülmüş sonuçları paylaş; sınırlılıkları ve sonraki geliştirmeleri belgele.
- [x] Git adaylarını veri/model/ortam dışlamaları ve tanınan anahtar kalıpları açısından kontrol et; değerler ifşa edilmedi, izlenen dosya yok.
- [x] 13 bağımlılık sürümünü ortamla karşılaştır, pip check ve 13 testi çalıştır; küçük sentetik veriyle temiz çıktı klasörlerinde tüm akışı doğrula.
- [x] Mevcut .venv'ye dokunmadan bağımsız Python 3.13.9 ortamına requirements.txt kur; pip check ve 13 testi bu ortamda doğrula. Pip önbelleği kullanıldı, sürümler değişmedi.
- [x] SQL/CSV/SQLite, RFM ve kayıtlı model/tahmin/metrik tutarlılığını doğrula; skorlar değişmedi.

## Sonraki sürüm

- [ ] API.
- [ ] Docker.

İlk hazırlık, veri profili, fatura/müşteri özetleri, SQL özellikleri, RFM ve model karşılaştırması tamamlandı. Bu aşamada dashboard, commit ve push yapılmadı.

Problem tanımı `docs/problem_definition.md`, SQL sonuçları `reports/sql_features.md`, segment yorumu `reports/rfm_segments.md`, başlangıç modeli `reports/baseline_model.md`, son model karşılaştırması `reports/model_comparison.md` içindedir. Sonraki aşama basit Streamlit dashboard'dur.
