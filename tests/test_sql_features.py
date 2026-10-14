"""Zaman sınırları ve gelecek bilgi sızıntısı için küçük örnek kontrolleri."""
from pathlib import Path
from contextlib import closing
import sqlite3
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_customer_features import create_snapshot, make_windows


class SQLFeatureTests(unittest.TestCase):
    def setUp(self):
        self.windows = {"observation_start": "2010-07-05 00:00:00",
                        "cutoff": "2011-01-01 00:00:00",
                        "target_end": "2011-04-01 00:00:00"}
        self.rows = [
            (1, "A", "2010-07-05 00:00:00", 10., 1),
            (1, "B", "2010-12-31 00:00:00", 20., 2),
            (1, "C", "2011-01-01 00:00:00", 999., 3),
            (1, "D", "2011-04-01 00:00:00", 999., 3),
            (1, "E", "2010-07-04 23:59:59", 999., 3),
            (2, "F", "2011-01-02 00:00:00", 99., 1),
        ]

    def snapshot(self, rows):
        frame = pd.DataFrame(rows, columns=["customer_id", "invoice_id", "event_date", "amount_gbp", "total_quantity"])
        with closing(sqlite3.connect(":memory:")) as connection:
            frame.to_sql("invoices", connection, index=False)
            return create_snapshot(connection, self.windows)

    def test_boundaries_and_cohort(self):
        features, labels = self.snapshot(self.rows)
        self.assertEqual(features["customer_id"].tolist(), [1])
        self.assertEqual(features["frequency_180d"].iloc[0], 2)
        self.assertEqual(features["monetary_180d_gbp"].iloc[0], 30)
        self.assertEqual(features["recency_days"].iloc[0], 1)
        self.assertEqual(labels["future_invoice_count"].iloc[0], 1)
        self.assertEqual(labels["no_purchase_90d"].iloc[0], 0)

    def test_future_changes_do_not_change_features(self):
        # Önce geleceği kaldır, sonra dev tutarlı gelecekteki faturaları ekle.
        past = [row for row in self.rows if row[2] < self.windows["cutoff"]]
        features_before, labels_before = self.snapshot(past)
        features_after, labels_after = self.snapshot(self.rows)
        pd.testing.assert_frame_equal(features_before, features_after)
        self.assertEqual(labels_before["no_purchase_90d"].iloc[0], 1)
        self.assertEqual(labels_after["no_purchase_90d"].iloc[0], 0)

    def test_incomplete_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Hedef dönemi tamamlanmamış"):
            make_windows("2011-11-01", pd.Timestamp("2009-12-01"), pd.Timestamp("2011-12-09"))


if __name__ == "__main__":
    unittest.main()
