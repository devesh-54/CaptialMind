import unittest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forecasting_model import TimeSeriesForecaster

class TestTimeSeriesForecaster(unittest.TestCase):

    def setUp(self):
        self.forecaster = TimeSeriesForecaster()

    def test_calculate_metrics(self):
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 305.0])
        
        metrics = TimeSeriesForecaster.calculate_metrics(y_true, y_pred)
        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("mape", metrics)
        self.assertIn("r2", metrics)
        self.assertGreater(metrics["r2"], 0.8)

    def test_train_and_evaluate(self):
        res = self.forecaster.train_and_evaluate()
        self.assertIn("selected_forecast_strategy", res)
        self.assertIn("ml_metrics", res)
        self.assertIn("naive_metrics", res)
        self.assertIn("ma_metrics", res)
        self.assertIn("model_outperforms_baseline", res)
        self.assertIn("confidence_score", res)
        self.assertGreaterEqual(res["confidence_score"], 0.0)
        self.assertLessEqual(res["confidence_score"], 1.0)

    def test_predict_30d_bounds(self):
        pred = self.forecaster.predict_30d(current_cash=2554079.97)
        self.assertIn("projected_points", pred)
        self.assertIn("raw_projected_cash", pred)
        self.assertIn("display_projected_cash", pred)
        self.assertIn("liquidity_deficit", pred)
        
        for pt in pred["projected_points"]:
            self.assertIn("raw_cash", pt)
            self.assertIn("display_cash", pt)
            self.assertIn("liquidity_deficit", pt)
            self.assertGreaterEqual(pt["display_cash"], 0.0)

if __name__ == "__main__":
    unittest.main()
