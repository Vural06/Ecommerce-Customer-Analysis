"""Tüm sayfaları salt okunur inceler; yalnızca Markdown raporu üretir."""
from datetime import datetime, timezone
from itertools import combinations
import platform

import openpyxl
import pandas as pd

from download_data import ROOT, WORKBOOK, sha256


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join([
        '| ' + ' | '.join(map(cell, headers)) + ' |',
        '| ' + ' | '.join(['---'] * len(headers)) + ' |',
        *['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows],
    ]) + '\n'


def invoice_text(frame):
    return frame['Invoice'].astype('string')


def purchases(frame):
    invoice = invoice_text(frame)
    mask = (invoice.notna() & ~invoice.str.upper().str.startswith('C', na=False)
            & frame['Quantity'].gt(0) & frame['Price'].gt(0)
            & frame['Customer ID'].notna())
    return frame.loc[mask], mask


def section(name, frame):
    invoice = invoice_text(frame)
    cancelled = invoice.str.upper().str.startswith('C', na=False)
    valid, mask = purchases(frame)
    counts = valid.groupby('Customer ID')['Invoice'].nunique()
    all_customers = frame['Customer ID'].dropna().unique()
    inclusive = counts.reindex(all_customers, fill_value=0)
    repeat = int(counts.ge(2).sum())
    metrics = [
        ('Satır (ürün satırı)', len(frame)),
        ('İlk tarih', frame['InvoiceDate'].min()),
        ('Son tarih', frame['InvoiceDate'].max()),
        ('Benzersiz müşteri (eksik hariç)', frame['Customer ID'].nunique()),
        ('Benzersiz fatura (iptaller dahil, eksik hariç)', invoice.nunique()),
        ('İptal satırı (Invoice C/c ile başlıyor)', int(cancelled.sum())),
        ('Benzersiz iptal faturası', invoice[cancelled].nunique()),
        ('Quantity < 0 satır', int(frame['Quantity'].lt(0).sum())),
        ('Quantity = 0 satır', int(frame['Quantity'].eq(0).sum())),
        ('Price < 0 satır', int(frame['Price'].lt(0).sum())),
        ('Price = 0 satır', int(frame['Price'].eq(0).sum())),
        ('Tam tekrar: ilk kopya dışındaki satırlar', int(frame.duplicated().sum())),
        ('Tam tekrar gruplarındaki tüm satırlar', int(frame.duplicated(keep=False).sum())),
        ('Alışveriş filtresinden geçen satır', int(mask.sum())),
        ('Filtrelenmiş benzersiz alışveriş faturası', valid['Invoice'].nunique()),
        ('En az bir alışveriş faturası olan müşteri', len(counts)),
        ('Kimliği bilinen, geçerli alışverişi olmayan müşteri', int(inclusive.eq(0).sum())),
        ('En az iki alışveriş faturası olan müşteri', repeat),
        ('Tekrar alışveriş oranı (payda: en az bir alışveriş yapanlar)',
         f'{repeat / len(counts):.4%}' if len(counts) else 'Tanımsız'),
        ('Tekrar alışveriş oranı (payda: tüm bilinen müşteriler)',
         f'{repeat / len(inclusive):.4%}' if len(inclusive) else 'Tanımsız'),
        ('Birden çok müşteriye bağlı fatura sayısı',
         int(frame.groupby('Invoice')['Customer ID'].nunique().gt(1).sum())),
    ]
    result = [f'## {name}', table(['Ölçüm', 'Değer'], metrics),
              '### Gerçek sütunlar, pandas veri tipleri ve eksikler',
              table(['Sütun', 'Veri tipi', 'Eksik sayı', 'Eksik oranı'], [
                  (col, frame[col].dtype, int(frame[col].isna().sum()),
                   f'{frame[col].isna().mean():.4%}') for col in frame.columns]),
              '### Müşteri başına benzersiz alışveriş faturası dağılımı',
              'Aşağıdaki özetin paydası en az bir geçerli alışverişi olan müşterilerdir.',
              table(['İstatistik', 'Fatura sayısı'], [
                  (label, f'{value:.4f}') for label, value in
                  counts.describe(percentiles=[.25, .5, .75, .9, .95, .99]).items()]),
              'Aralık tablosu tüm kimliği bilinen müşterileri kapsar (0 dahil).',
              table(['Fatura sayısı', 'Müşteri sayısı', 'Müşteri oranı'], [
                  (label, int(selected.sum()), f'{selected.mean():.4%}')
                  for label, selected in [
                      ('0', inclusive.eq(0)), ('1', inclusive.eq(1)),
                      ('2', inclusive.eq(2)), ('3–5', inclusive.between(3, 5)),
                      ('6–10', inclusive.between(6, 10)),
                      ('11–20', inclusive.between(11, 20)), ('21+', inclusive.ge(21))]])]
    assert counts.sum() == len(valid[['Customer ID', 'Invoice']].drop_duplicates())
    assert len(inclusive) == frame['Customer ID'].nunique()
    return '\n\n'.join(result)


def main():
    before = sha256(WORKBOOK)
    frames = {}
    with pd.ExcelFile(WORKBOOK, engine='openpyxl') as workbook:
        for name in workbook.sheet_names:
            print(f'Okunuyor: {name}', flush=True)
            frames[name] = pd.read_excel(workbook, sheet_name=name)
    expected = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate',
                'Price', 'Customer ID', 'Country']
    for name, frame in frames.items():
        if list(frame.columns) != expected:
            raise ValueError(f'Beklenmeyen şema ({name}): {list(frame.columns)}')
        if not pd.api.types.is_datetime64_any_dtype(frame['InvoiceDate']):
            raise ValueError(f'Tarih tipi doğrulanamadı: {name}')
    output = [
        '# UCI Online Retail II — ilk veri incelemesi',
        f'Rapor zamanı (UTC): {datetime.now(timezone.utc).isoformat()}',
        '[Resmî kaynak](https://archive.ics.uci.edu/dataset/502/online+retail+ii). '
        'Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. '
        '[DOI](https://doi.org/10.24432/C5CG6D). '
        '[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).',
        f'Girdi: `data/raw/{WORKBOOK.name}`; SHA-256: `{before}`.',
        f'Python {platform.python_version()}, pandas {pd.__version__}, openpyxl {openpyxl.__version__}.',
        '## Sayım yöntemi ve sınırlar',
        'Bir satır bir ürün/fatura kalemidir; sipariş sayısı değildir. Alışveriş sayımında '
        '`Invoice` dolu, C/c ile başlamayan, `Quantity > 0`, `Price > 0` ve '
        '`Customer ID` dolu satırlar kullanılır. Bir faturanın en az bir satırının bu '
        'filtreyi geçmesi yeterlidir. Her müşteri için `Invoice.nunique()` hesaplanır. '
        'İptal/iade satırları özgün satışlarla eşleştirilip netleştirilmemiştir. '
        'Bu geçici inceleme tanımıdır; nihai temizleme veya hedef tanımı değildir.',
        'Ham dosya ve satırlar değiştirilmez. Filtreler ve tekilleştirme yalnızca '
        'bellekte özet hesaplamak içindir; temizlenmiş veri yazılmaz. Eksik oranlarının '
        'paydası ilgili bölümün tüm satırlarıdır. Benzersiz sayılar eksik kimlikleri '
        'içermez. Tam tekrar, sekiz sütunun tümünün eşitliğidir; eksikler eşit kabul edilir. '
        'Veri tipleri Excel hücre biçimi değil pandas okuma sonucudur. Birleşik bölüm '
        'sayfaların ham birleşimidir; örtüşen satırlar korunur, benzersiz faturalar '
        'yeniden sayılır. Yüzdeler yuvarlanmıştır.',
        'Kategori, indirim, ödeme ve teslimat alanları yoktur. StockCode ürün kodu, '
        'Description açıklama, Country ülke bilgisidir; ek alanlar türetilmemiştir. '
        'Tüm dönem tekrar alışveriş oranı geleceğe yönelik model başarısı veya kampanya '
        'etkisi değildir. Müşterilerin gözlenme süreleri farklıdır.',
        '## Çalışma sayfaları',
        table(['Sayfa', 'Satır', 'Sütun'], [(n, len(f), len(f.columns)) for n, f in frames.items()]),
    ]
    for name, frame in frames.items():
        output.append(section(name, frame))
    output.append('## Sayfalar arası örtüşme')
    for (an, a), (bn, b) in combinations(frames.items(), 2):
        start = max(a['InvoiceDate'].min(), b['InvoiceDate'].min())
        end = min(a['InvoiceDate'].max(), b['InvoiceDate'].max())
        common_days = set(a['InvoiceDate'].dt.date.dropna()) & set(b['InvoiceDate'].dt.date.dropna())
        common_times = set(a['InvoiceDate'].dropna()) & set(b['InvoiceDate'].dropna())
        # Tam satır eşitliği: karma değer tahmini yerine sütunların tamamıyla birleştirme.
        common = a.drop_duplicates().merge(b.drop_duplicates(), on=expected, how='inner', validate='one_to_one')
        a_matched = len(a.merge(common, on=expected, how='inner', validate='many_to_one'))
        b_matched = len(b.merge(common, on=expected, how='inner', validate='many_to_one'))
        output += [f'### {an} / {bn}', table(['Kontrol', 'Sonuç'], [
            ('Tarih aralığı kesişimi', f'{start} — {end}' if start <= end else 'Yok'),
            ('Ortak takvim günü', len(common_days)),
            ('Ortak zaman damgası', len(common_times)),
            ('Ortak benzersiz fatura', len(set(invoice_text(a).dropna()) & set(invoice_text(b).dropna()))),
            ('Ortak benzersiz müşteri', len(set(a['Customer ID'].dropna()) & set(b['Customer ID'].dropna()))),
            ('Sekiz sütunu eşit ortak benzersiz kayıt', len(common)),
            (f'{an}: karşı sayfada aynısı olan satır', a_matched),
            (f'{bn}: karşı sayfada aynısı olan satır', b_matched),
        ]), 'Ortak müşteri tek başına mükerrer kayıt değildir. Ortak gün/zaman da '
            'tam kayıt eşitliği anlamına gelmez. Birleşik satır sayısı bu yüzden '
            'otomatik olarak tekil işlem sayısı kabul edilmemelidir.']
    combined = pd.concat(frames.values(), ignore_index=True)
    assert len(combined) == sum(map(len, frames.values()))
    output.append(section('Birleşik dönem (ham satırlar korunarak)', combined))
    after = sha256(WORKBOOK)
    assert before == after, 'İnceleme sırasında ham dosya değişti!'
    output.append('## Doğrulama\n\nHam dosyanın SHA-256 değeri inceleme öncesi ve '
                  'sonrası aynıdır. Sayfa satır toplamı birleşik satır sayısına eşittir. '
                  'Müşteri-fatura tekil çift sayısı, müşteri bazlı fatura sayılarının '
                  'toplamına eşittir. Profil betiği model veya dashboard üretmez; '
                  'güncel proje durumu README içindedir.')
    report = ROOT / 'reports' / 'data_profile.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('\n\n'.join(output) + '\n', encoding='utf-8')
    print(f'Rapor: {report}', flush=True)


if __name__ == '__main__':
    main()
