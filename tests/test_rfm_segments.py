"""RFM eşit değer, puan yönü ve sabit eşik kontrolleri."""
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_rfm_segments import score_values, fit_thresholds, assign_segments


class RFMTests(unittest.TestCase):
    def test_score_direction_and_boundaries(self):
        values = pd.Series([1, 2, 3, 4, 5])
        self.assertEqual(score_values(values, [2, 4]).tolist(), [1, 1, 2, 2, 3])
        self.assertEqual(score_values(values, [2, 4], reverse=True).tolist(), [3, 3, 2, 2, 1])

    def test_ties_are_not_arbitrarily_split(self):
        self.assertEqual(score_values(pd.Series([1, 1, 1, 2]), [1, 1]).tolist(), [1, 1, 1, 3])

    def test_other_customers_do_not_change_fixed_scores(self):
        train = pd.DataFrame({"snapshot_date": ["2011-01-01"] * 3, "customer_id": [1, 2, 3],
                              "recency_days": [1, 30, 90], "frequency_180d": [1, 3, 10],
                              "monetary_180d_gbp": [10., 100., 1000.]})
        thresholds = fit_thresholds(train)
        before = assign_segments(train, thresholds)
        extra = train.iloc[[0]].copy()
        extra["customer_id"] = 4
        extra["monetary_180d_gbp"] = 999999
        after = assign_segments(pd.concat([train, extra], ignore_index=True), thresholds)
        pd.testing.assert_frame_equal(before, after.iloc[:3])


if __name__ == "__main__":
    unittest.main()
