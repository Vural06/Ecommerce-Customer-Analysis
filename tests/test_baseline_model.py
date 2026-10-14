"""Ölçekleme sızıntısı ve eşik/hata matrisi kontrolleri."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from train_baseline import FEATURES, choose_threshold, evaluate, make_logistic_model, load_snapshot


class BaselineTests(unittest.TestCase):
    def test_fractional_target_is_rejected_before_integer_conversion(self):
        features = pd.DataFrame({name: [1., 2.] for name in FEATURES})
        features["snapshot_date"] = "2011-01-01"
        features["customer_id"] = [1, 2]
        labels = features[["snapshot_date", "customer_id"]].copy()
        labels["no_purchase_90d"] = [.5, 1.]
        with patch("train_baseline.pd.read_csv", side_effect=[features, labels]):
            with self.assertRaisesRegex(ValueError, "yalnızca 0 veya 1"):
                load_snapshot("train")

    def test_scaler_does_not_learn_from_prediction_data(self):
        X = pd.DataFrame({name: [1., 2., 3., 4.] for name in FEATURES})
        model = make_logistic_model()
        model.fit(X, [0, 0, 1, 1])
        scaler = model.named_steps["scaler"]
        before = scaler.mean_.copy()
        shifted = pd.DataFrame({name: [10000.] for name in FEATURES})
        model.predict_proba(shifted)
        np.testing.assert_array_equal(scaler.mean_, before)
        np.testing.assert_allclose(before, X.mean())
        self.assertNotIn("customer_id", FEATURES)
        self.assertNotIn("future_invoice_count", FEATURES)

    def test_threshold_tie_and_confusion_matrix(self):
        y = np.array([1, 0])
        probabilities = np.array([0.9, 0.1])
        threshold, _ = choose_threshold(y, probabilities)
        self.assertEqual(threshold, 0.8)
        result = evaluate(y, probabilities, np.array([1, 1]))
        self.assertEqual((result["tn"], result["fp"], result["fn"], result["tp"]), (0, 1, 0, 1))
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 1)


if __name__ == "__main__":
    unittest.main()
