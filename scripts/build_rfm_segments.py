"""Eğitimden öğrenilen sabit eşiklerle basit, üç puanlı RFM segmentasyonu."""
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
RFM_COLUMNS = ["recency_days", "frequency_180d", "monetary_180d_gbp"]
SEGMENTS = ["Yakın ve yüksek F/M", "Yakın, düşük sıklık", "Orta/yakın, sık",
            "Uzak, güçlü F/M geçmişi", "Uzak, düşük F/M", "Diğer"]


def validate_features(frame):
    if frame.empty or frame[RFM_COLUMNS].isna().any().any():
        raise ValueError("RFM girdisi boş veya eksik.")
    if not np.isfinite(frame[RFM_COLUMNS].to_numpy(dtype=float)).all():
        raise ValueError("RFM değerleri sonlu olmalı.")
    if not frame["recency_days"].ge(0).all():
        raise ValueError("Recency negatif olamaz.")
    if not frame["frequency_180d"].ge(1).all() or not frame["monetary_180d_gbp"].gt(0).all():
        raise ValueError("Alışveriş sıklığı en az 1, brüt harcama pozitif olmalı.")
    if frame.duplicated(["snapshot_date", "customer_id"]).any():
        raise ValueError("Tahmin tarihi/müşteri anahtarı tekrarlı.")


def fit_thresholds(train):
    validate_features(train)
    # Üç grup için 1/3 ve 2/3 kantilleri. Yalnızca train kullanılır.
    return {column: train[column].quantile([1 / 3, 2 / 3]).tolist()
            for column in RFM_COLUMNS}


def score_values(values, thresholds, reverse=False):
    # Eşiğe eşit değer alt aralıkta kalır. Aynı değer hep aynı puanı alır.
    # Eşikler aynıysa orta puan boş kalabilir; müşterileri keyfi sırayla bölmeyiz.
    scores = np.searchsorted(thresholds, values.to_numpy(), side="left") + 1
    if reverse:
        scores = 4 - scores  # Recency'de küçük değer daha yüksek puan alır.
    return pd.Series(scores, index=values.index, dtype="int64")


def assign_segments(features, thresholds):
    validate_features(features)
    result = features.copy()
    result["r_score"] = score_values(result["recency_days"], thresholds["recency_days"], reverse=True)
    result["f_score"] = score_values(result["frequency_180d"], thresholds["frequency_180d"])
    result["m_score"] = score_values(result["monetary_180d_gbp"], thresholds["monetary_180d_gbp"])
    r, f, m = result["r_score"], result["f_score"], result["m_score"]
    # np.select ilk uyan kuralı seçer; kuralların sırası önemlidir.
    result["segment"] = np.select([
        r.eq(3) & f.ge(2) & m.ge(2),
        r.eq(3) & f.eq(1),
        r.ge(2) & f.ge(2),
        r.eq(1) & (f.ge(2) | m.ge(2)),
        r.eq(1) & f.eq(1) & m.eq(1),
    ], SEGMENTS[:5], default=SEGMENTS[5])
    result["rfm_code"] = r.astype(str) + f.astype(str) + m.astype(str)
    assert len(result) == len(features)
    assert result[["r_score", "f_score", "m_score"]].isin([1, 2, 3]).all().all()
    return result


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    return "\n".join(lines)


def main():
    train = pd.read_csv(DATA_DIR / "train_features.csv")
    thresholds = fit_thresholds(train)
    config = {"fit_split": "train", "snapshot_date": str(train["snapshot_date"].iloc[0]),
              "quantiles": [1 / 3, 2 / 3], "scores": [1, 2, 3],
              "boundary_rule": "value <= threshold stays in lower numeric interval",
              "thresholds": thresholds}
    config_dir = ROOT / "configs"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "rfm_thresholds.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    report = ["# RFM segmentasyonu", "## Yöntem",
              "R: son alışverişten geçen tam gün. F: son 180 gündeki farklı fatura sayısı. "
              "M: aynı dönemdeki brüt filtrelenmiş fatura tutarı (GBP). R küçükken, F ve M "
              "büyükken puan yüksektir. Her boyut 1–3 puan alır.",
              "Eşikler yalnızca train özelliklerinin 1/3 ve 2/3 kantilleridir; "
              "validation ve testte yeniden hesaplanmaz. Eşiğe eşit değer alt sayısal "
              "aralıkta kalır. Eşit değerler aynı puanı alır; eşikler çakışırsa bazı "
              "puanlar boş kalabilir. Segmentlerin eşit büyüklükte olması beklenmez.",
              markdown_table(["Alan", "İlk eşik", "İkinci eşik"],
                             [(column, f"{edges[0]:.4f}", f"{edges[1]:.4f}") for column, edges in thresholds.items()]),
              "## Segment kuralları (ilk uyan kural)",
              markdown_table(["Segment", "Kural"], list(zip(SEGMENTS, [
                  "R=3, F≥2, M≥2", "R=3, F=1", "R≥2, F≥2",
                  "R=1 ve (F≥2 veya M≥2)",
                  "R=1, F=1, M=1", "Yukarıdakilerin dışında kalanlar"]))),
              "Yakın ve uzak, eğitim eşiklerine göre göreli tanımlardır. "
              "Yakın/düşük sıklık müşterisini yeni müşteri olarak yorumlamıyoruz; "
              "tüm geçmişte ilk kez alışveriş yaptığı bilinmiyor. Segmentler iş tarafından "
              "onaylanmış sınıflar veya eğitilmiş risk tahminleri değildir."]
    for split in ["train", "validation", "test"]:
        features = train if split == "train" else pd.read_csv(DATA_DIR / f"{split}_features.csv")
        segmented = assign_segments(features, thresholds)
        segmented.to_csv(DATA_DIR / f"{split}_rfm.csv", index=False)
        summary = segmented.groupby("segment").agg(
            customer_count=("customer_id", "size"),
            median_recency_days=("recency_days", "median"),
            median_frequency=("frequency_180d", "median"),
            median_monetary_gbp=("monetary_180d_gbp", "median"),
        ).reindex(SEGMENTS)
        summary["customer_count"] = summary["customer_count"].fillna(0).astype(int)
        summary["customer_share"] = summary["customer_count"] / len(segmented)
        summary.to_csv(DATA_DIR / f"{split}_rfm_summary.csv")
        assert summary["customer_count"].sum() == len(features)
        report += [f"## {split} ({len(features)} müşteri)",
                   markdown_table(["Segment", "Müşteri", "Pay", "Medyan R (gün)", "Medyan F", "Medyan M (GBP)"], [
                       (segment, int(row["customer_count"]), f"{row['customer_share']:.2%}",
                        *[f"{row[column]:.2f}" if pd.notna(row[column]) else "—" for column in
                          ["median_recency_days", "median_frequency", "median_monetary_gbp"]])
                       for segment, row in summary.iterrows()])]
        # Test hedefleri okunmaz. Son değerlendirme için tutulur.
        if split != "test":
            labels = pd.read_csv(DATA_DIR / f"{split}_labels.csv")
            joined = segmented.merge(labels, on=["snapshot_date", "customer_id"], how="left", validate="one_to_one")
            assert len(joined) == len(segmented) and joined["no_purchase_90d"].notna().all()
            observed = joined.groupby("segment")["no_purchase_90d"].agg(["count", "sum", "mean"]).reindex(SEGMENTS)
            report += ["### Sonraki 90 günde gözlenen alışveriş yapmama",
                       markdown_table(["Segment", "Alışveriş yapmayan / toplam", "Oran"], [
                           (segment, f"{int(row['sum'])}/{int(row['count'])}" if pd.notna(row['count']) else "0/0",
                            f"{row['mean']:.2%}" if pd.notna(row['mean']) else "Tanımsız")
                           for segment, row in observed.iterrows()])]
        print(f"{split}: {len(segmented)} müşteri segmentlendi.")
    report += ["## Yorum ve sınırlılıklar",
               "Segment tablolarındaki medyanlar tipik davranışı, paylar segment büyüklüğünü "
               "gösterir. Yakın/yüksek F-M grubu yakın dönemde sık ve yüksek tutarlı alışveriş "
               "yapanları; uzak/güçlü geçmiş grubu uzun süredir alışveriş yapmayan fakat "
               "gözlemde sıklığı veya harcaması güçlü olanları temsil eder. Bu gruplar "
               "iletişim stratejisi için hipotez üretmeye yardımcı olabilir; kampanya "
               "başarısı veya nedensel kazanç göstermez.",
               "Train/validation hedef oranları betimsel karşılaştırmadır. Kurallar "
               "bu oranlara göre ayarlanmadı. Küçük grupların oranları kararsız olabilir; "
               "müşteri sayısıyla birlikte okunmalıdır. Test hedefleri bu betikte okunmaz. "
               "Testteki tablo yalnızca geçmiş özelliklerin dağılımını gösterir; "
               "model/segment kuralı seçmek için kullanılmaz.",
               "M iadeler düşülmeden hesaplanır ve korunan sayfa içi tekrarları içerir. "
               "180 günlük müşteri evreni uzun süredir pasif müşterileri dışlar. "
               "Sabit eşikler dönem değişiminden etkilenebilir. 1–3 puanlı basit "
               "kuralların iş uygunluğu ayrıca doğrulanmalıdır.",
               "## Çıktılar ve doğrulama",
               "`configs/rfm_thresholds.json` yalnızca eğitim eşiklerini içerir. "
               "`data/processed/{train,validation,test}_rfm.csv` müşteri puan/segmentlerini; "
               "`*_rfm_summary.csv` segment özetlerini içerir. Yerel CSV'ler Git dışındadır. "
               "Müşteriler kaybolmadan tek segmente atanır, puanlar 1–3 aralığındadır. "
               "RFM betiği model eğitmez; güncel model sonuçları ayrı model karşılaştırması raporundadır."]
    report_path = ROOT / "reports" / "rfm_segments.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
