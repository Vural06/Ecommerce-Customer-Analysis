"""Model seçimi ölçütü ve aynı risk puanının korunması."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from compare_models import make_random_forest, select_model
from train_baseline import FEATURES


class ComparisonTests(unittest.TestCase):
    def test_selection_uses_ap_before_f1_and_prefers_simple_tie(self):
        scores = {"logistic": {"average_precision": .8, "f1": .5},
                  "random_forest": {"average_precision": .7, "f1": .9}}
        self.assertEqual(select_model(scores), "logistic")
        scores["random_forest"] = dict(scores["logistic"])
        self.assertEqual(select_model(scores), "logistic")

    def test_predicting_other_rows_does_not_change_a_customer_score(self):
        X = pd.DataFrame({name: range(80) for name in FEATURES})
        model = make_random_forest().fit(X, [0]*40 + [1]*40)
        one = model.predict_proba(X.iloc[[0]])
        many = model.predict_proba(X)
        np.testing.assert_allclose(one[0], many[0])


if __name__ == "__main__":
    unittest.main()
