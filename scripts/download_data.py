"""UCI arşivini indirir; mevcut ham dosyaları değiştirmez."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
URL = 'https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip'
WORKBOOK = RAW / 'online_retail_II.xlsx'
ARCHIVE = RAW / 'online_retail_ii.zip'
METADATA = RAW / 'download_metadata.json'


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    if WORKBOOK.exists():
        if not zipfile.is_zipfile(WORKBOOK):
            raise ValueError('Mevcut Excel geçersiz; otomatik olarak üzerine yazılmadı.')
        if METADATA.exists():
            metadata = json.loads(METADATA.read_text(encoding='utf-8'))
            if sha256(WORKBOOK) != metadata['workbook_sha256']:
                raise ValueError('Excel SHA-256 kayıtla uyuşmuyor; dosya korunuyor.')
        print(f'Mevcut Excel kullanılıyor, indirme yapılmadı: {WORKBOOK}')
        return
    downloaded_at = None
    if not ARCHIVE.exists():
        temporary = ARCHIVE.with_suffix('.zip.part')
        request = urllib.request.Request(URL, headers={'User-Agent': 'RetailPortfolio/1.0'})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                with temporary.open('wb') as target:
                    shutil.copyfileobj(response, target)
            with zipfile.ZipFile(temporary) as archive:
                if archive.testzip() is not None:
                    raise ValueError('Arşiv bütünlük kontrolü başarısız.')
            temporary.rename(ARCHIVE)
            downloaded_at = datetime.now(timezone.utc).isoformat()
        finally:
            temporary.unlink(missing_ok=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        members = [n for n in archive.namelist() if Path(n).name == WORKBOOK.name]
        if len(members) != 1:
            raise ValueError('Arşivde beklenen tek Excel dosyası bulunamadı.')
        temporary = WORKBOOK.with_suffix('.xlsx.part')
        try:
            with archive.open(members[0]) as source, temporary.open('wb') as target:
                shutil.copyfileobj(source, target)
            if not zipfile.is_zipfile(temporary):
                raise ValueError('İndirilen dosya geçerli XLSX değil.')
            temporary.rename(WORKBOOK)
        finally:
            temporary.unlink(missing_ok=True)
    metadata = {
        'source_url': URL,
        'downloaded_at_utc': downloaded_at,
        'download_date_note': 'null ise mevcut arşivin indirme tarihi bilinmiyor.',
        'archive_sha256': sha256(ARCHIVE),
        'workbook_sha256': sha256(WORKBOOK),
        'workbook_bytes': WORKBOOK.stat().st_size,
    }
    METADATA.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
