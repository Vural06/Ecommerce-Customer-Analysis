"""Gerçek veriyi değiştirmeden küçük sentetik Excel ile temiz klasörlerde akış."""
from contextlib import redirect_stdout
from importlib import import_module
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "exercises"))
import download_data
import profile_data
import build_customer_features
import build_rfm_segments
import train_baseline
import compare_models

summary = import_module("02_fatura_ve_musteri_ozeti")


class ReproducibilityTests(unittest.TestCase):
    def test_fresh_folders_and_complete_small_pipeline(self):
        # İki müşterinin her hedef döneminde 0/1 örneği var; bu veri gerçek skor değildir.
        events = [(1, "2009-12-01"), (1, "2010-08-01"), (1, "2010-12-15"),
                  (2, "2010-12-01"), (1, "2011-02-01"), (2, "2011-04-02"),
                  (1, "2011-06-01"), (2, "2011-08-01"), (1, "2011-09-15"),
                  (1, "2011-12-09")]
        rows = [(100 + i, "A", "Ürün", 2, pd.Timestamp(date), 10., customer, "UK")
                for i, (customer, date) in enumerate(events)]
        with tempfile.TemporaryDirectory(prefix="retail_repro_") as directory:
            root = Path(directory)
            raw = root / "data" / "raw"
            processed = root / "data" / "processed"
            raw.mkdir(parents=True)
            fixture = root / "fixture.xlsx"
            with pd.ExcelWriter(fixture, engine="openpyxl") as writer:
                pd.DataFrame(rows[:4], columns=summary.COLUMNS).to_excel(writer, sheet_name="Year 2009-2010", index=False)
                pd.DataFrame([rows[3]] + rows[4:], columns=summary.COLUMNS).to_excel(writer, sheet_name="Year 2010-2011", index=False)
            archive = raw / "online_retail_ii.zip"
            workbook = raw / "online_retail_II.xlsx"
            with zipfile.ZipFile(archive, "w") as zipped:
                zipped.write(fixture, arcname=workbook.name)
            (root / "sql").mkdir()
            for source in (ROOT / "sql").glob("*.sql"):
                (root / "sql" / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                with patch.multiple(download_data, ROOT=root, RAW=raw, ARCHIVE=archive, WORKBOOK=workbook, METADATA=raw / "download_metadata.json"):
                    with patch("urllib.request.urlopen", side_effect=AssertionError("Yerel arşiv yeniden indirilmemeli")):
                        download_data.main()
                        download_data.main()
                before = summary.file_hash(workbook)
                with patch.multiple(profile_data, ROOT=root, WORKBOOK=workbook):
                    profile_data.main()
                with patch.multiple(summary, PROJECT_ROOT=root, EXCEL_PATH=workbook, OUTPUT_DIR=processed):
                    summary.main()
                with patch.multiple(build_customer_features, ROOT=root, INPUT_PATH=processed / "combined_invoices.csv", OUTPUT_DIR=processed):
                    build_customer_features.main()
                with patch.multiple(build_rfm_segments, ROOT=root, DATA_DIR=processed):
                    build_rfm_segments.main()
                with patch.multiple(train_baseline, ROOT=root, DATA_DIR=processed):
                    train_baseline.main()
                    with patch.multiple(compare_models, ROOT=root, DATA_DIR=processed, ARTIFACT_DIR=root / "artifacts"):
                        compare_models.main()
            self.assertEqual(before, summary.file_hash(workbook))
            self.assertTrue((root / "reports" / "model_comparison.md").is_file())
            self.assertTrue((processed / "customer_analytics.sqlite").is_file())
            self.assertTrue((root / "configs" / "rfm_thresholds.json").is_file())
            self.assertTrue((root / "artifacts" / "selected_model.joblib").is_file())
            self.assertEqual(len(pd.read_csv(processed / "combined_invoices.csv")), len(rows))

    def test_overlap_keeps_largest_copy_count_and_original_frames(self):
        row = [1, "A", None, 2, pd.Timestamp("2010-01-01"), 3., 1, "UK"]
        first = pd.DataFrame([row, row], columns=summary.COLUMNS)
        second = pd.DataFrame([row, row, row], columns=summary.COLUMNS)
        before = first.copy(deep=True)
        combined, removed = summary.combine_without_sheet_overlap(first, second)
        self.assertEqual(removed, 2)
        self.assertEqual(len(combined), 3)
        pd.testing.assert_frame_equal(first, before)


if __name__ == "__main__":
    unittest.main()
