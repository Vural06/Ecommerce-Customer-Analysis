# Dashboard öncesi yayımlama kontrolü

Denetim: 14 Ekim 2026. Bu sürüm analiz ve model portföyü olarak yayımlanmaya hazırdır; tamamlanmış dashboard sürümü değildir. Commit, push ve GitHub deposu oluşturulmadı.

## İncelenen durum

Çalışma klasörü `p1`. Üst klasörler ve proje içinde AGENTS.md bulunmadı. Git `main` dalında, henüz commit ve izlenen dosya yok. Çalışmalar korundu. GitHub adayları `reports/output_verification.md` içinde listelenir.

## Bulunan sorunlar ve düzeltmeler

- README hedef/pencereleri henüz belirlenmemiş gibi anlatıyordu. 180 günlük gözlem, 90 günlük hedef ve üç tahmin tarihiyle uyumlu hâle getirildi.
- Bağımlılık açıklaması yalnızca pandas/openpyxl'i kapsıyordu. Doğrudan kullanılan numpy/scikit-learn/joblib ve 13 sabit paketle uyumlu hâle getirildi.
- Tek komut listesi indirme/profil aşamasında bitiyordu. Fatura özeti, EDA, SQL, öğrenme örneği, RFM, model ve denetim adımları doğru sırayla eklendi.
- Eski raporların “model eğitilmedi / sonraki aşama” cümleleri projenin güncel durumuyla karışabiliyordu. İlgili betiğin kapsamını anlatacak biçimde düzeltildi; sayısal sonuçlar korunuyor.
- Sayfa içi tekrarların etkisi zaten hesaplanmıştı, karar gerekçesi ve TODO durumu eksikti. Koruma kararı, 11.620 fazla geçerli satır ve 56.746,91 GBP (%0,3255) duyarlılığı raporlandı.
- Gerçekten eksik aylık hareket, alışveriş aralığı ve müşteri/fatura dağılımları `data_quality_eda.md` içinde tamamlandı. Kısmi son ay ve aralık sansürü açıklandı.
- İptal/iade/ücretsiz veya negatif fiyatlı satırlar “hata” sayılmadan, ücretli alışveriş tanımının dışında bırakılma gerekçesi belgelendi. İadeler netleştirilmez. Büyük faturalar korunur; eğitim IQR sınırları sadece tanısaldır.
- `load_snapshot` hedefi doğrulamadan tam sayıya çeviriyordu; 0,5 etiketi yanlışlıkla 0 olabilirdi. Önce 0/1 kontrolü eklendi ve regresyon testi yazıldı. Mevcut etiketler doğru olduğundan model sonuçları etkilenmedi.
- Çıktı rapor klasörünü varsayan betiklere açık klasör oluşturma eklendi. Küçük sentetik verili temiz klasör testi tüm akışı doğruluyor.
- Model seçiminin karmaşık `max/lambda` ifadesi açık iki karşılaştırma ve if ile sadeleştirildi. AP → F1 → basit model sırası değişmedi.
- .gitignore'a bulut/SSH kimlik klasörleri, ek anahtar dosya adları ve SQLite yan dosyaları eklendi.

## Çalıştırılan kontroller

| Kontrol | Sonuç |
| --- | --- |
| Mevcut anlamlı testler ve yeni regresyon testleri | 13/13 geçti |
| Temiz klasör, küçük sentetik Excel/arşiv ve uçtan uca akış | Geçti; mevcut bağımlılıklarla, ağ indirmesi taklit edilerek |
| Windows sandbox geçici dizin denemesi | İzin engeline takıldı; izinli yeniden çalıştırmada geçti |
| pip check | Bozuk bağımlılık yok |
| requirements.txt / ortam | 13 sürüm bire bir eşleşti |
| Ham Excel SHA-256 | İndirme kaydıyla aynı |
| Yeniden indirme | Mevcut dosya doğrulanıp indirme atlandı |
| Tüm SQL özellik/etiket satırları | Yeniden sorguyla CSV ve SQLite eşleşti |
| Zaman sınırları | Geçmiş sağ sınır hariç; hedef başlangıcı dahil, sonu hariç; hedefler bir sonraki tahminden önce biter |
| Gelecek bilgi / ölçekleme | Gelecek eklemek geçmişi değiştirmiyor; scaler yalnızca eğitim örnekleriyle öğrenmiş |
| RFM | Train eşikleri ve üç dönemin puan/segmentleri kayıtlı çıktılarla eşleşti |
| Model/eşik seçimi | Validation AP ve F1 kurallarıyla kaydedilen seçim yeniden doğrulandı |
| Olasılıklar / metrikler | Kayıtlı modeller, tahmin CSV'leri, metadata ve raporlar eşleşti |
| Gizli bilgi / veri dışlamaları | Git adaylarında veri, model, ortam veya tanınan anahtar kalıbı yok; değerler gösterilmedi |

Anahtar taraması belirli kalıpları kapsar; bütün olası gizli değer türlerini tespit ettiği iddia edilmez. İzlenen dosya olmaması, .gitignore'un ileride zorla eklenen bir dosyayı koruyacağı anlamına gelmez. Dosyalar eklenmeden önce tekrar aday listesi kontrol edilmelidir.

## Model sonuçları değişti mi?

Hayır. Gerçek veride model yeniden eğitilmedi; özellik/model/eşik ayarı yapılmadı. Kayıtlı olasılıklar üzerinden denetim amaçlı yeniden hesaplandı. Mevcut test artık görülmüş durumdadır; bu kontrol yeni bir bağımsız test değildir.

| Test modeli | AP | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Çoğunluk referansı | 0,3929 | 0,3929 | 1,0000 | 0,5641 |
| Lojistik regresyon, eşik 0,6 | 0,5821 | 0,5008 | 0,8825 | 0,6390 |
| Random Forest, eşik 0,5 | 0,5858 | 0,4917 | 0,9256 | 0,6422 |

Random Forest validation AP ile seçilmişti. Test hata matrisi TN=641, FP=1.042, FN=81, TP=1.008. İki öğrenen modelin farkı küçük; istatistiksel üstünlük veya kampanya kazancı gösterilmedi.

## Öğrenme örneği

`docs/customer_feature_example.md`: takma adlı iki gerçek geçmiş faturası, tahmin tarihi 2011-01-01. Recency=24 gün, frequency=2, monetary=1.323,32 GBP, ortalama=661,66 GBP ve miktar=828. Beş değer SQL ile eşleşti. Özgün kimlikler yalnızca yerel `data/processed/customer_example_private.md` dosyasında kalır. Öğrenciyle inceleme TODO'su açık tutuldu.

## GitHub kapsamı

Eklenecekler: `.gitignore`, `README.md`, `TODO.md`, `requirements.txt`, `scripts/`, `exercises/`, `sql/`, `tests/`, `configs/rfm_thresholds.json`, `docs/` ve toplulaştırılmış `reports/*.md`. Tam mevcut dosya listesi çıktı denetimindedir.

Eklenmeyecekler: `.env` ve kimlik bilgileri, `.venv/`, `data/raw/`, `data/processed/`, SQLite/yan dosyaları, `artifacts/`, yerel model ve müşteri tahminleri. UCI kaynak/DOI/CC BY 4.0 atıfları korunur.

## Açık kalanlar ve sınırlar

- Öğrencinin müşteri örneğini incelemesi.
- Streamlit dashboard ve onun sayı/filtre doğrulamaları.
- API ve Docker sonraki sürümde.
- Kod için ayrı yeniden kullanım lisansı seçimi isteğe bağlı olarak kullanıcıya bırakıldı; veri lisansı kod lisansı yerine geçmez.
- Bağımsız Python 3.13.9 sanal ortamına requirements.txt kurulumu, pip check ve 13 test ayrıca geçti; ayrıntılar independent_installation.md içinde. Bu aynı Windows makinesinde pip önbelleğiyle yapıldı; başka makine/işletim sistemi uyumluluğu ayrıca denenmedi.
- Sayfa içi kopyaların yanlışlığını kanıtlayacak satır kimliği yok; aykırı değerler/iadeler hakkındaki ilk sürüm kararları sınırlılıklarıyla belgelenmiştir. Bu, eksik uygulanmış bir filtre değil bilinçli kapsam kararıdır.

Mülakatta açıklanması gerekenler: ürün kalemi/fatura farkı; brüt tutar; 180/90 günlük varsayım; son kalem zamanının bilgi kullanılabilirliği; yalnızca eğitimde öğrenilen ölçekleme/RFM eşikleri; validation seçimi ve görülmüş test; yüksek recall yanında yanlış pozitiflerin maliyeti.
