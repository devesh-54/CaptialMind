"""
test_pipeline_integration.py
─────────────────────────────
End-to-end integration test for the full CashPilot forecasting → decision pipeline.

Verifies:
1. forecast_model_selection block is present in the response contract.
2. The winner matches the forecaster's selected_strategy.
3. Confidence score propagates correctly into forecast_quality.
4. risk_level is one of the valid classifications.
5. Reconciliation is valid.
6. If ARIMA won, its candidate entry is present in forecast_model_selection.
7. All 5 candidate model metrics keys are present in all_model_metrics after training.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import DecisionEngine
from forecasting_model import TimeSeriesForecaster


class TestEndToEndPipeline(unittest.TestCase):
    """Full pipeline integration test: raw CSV in → forecast selection → decision contract out."""

    @classmethod
    def setUpClass(cls):
        """Instantiate engine once for all tests (expensive: trains models)."""
        cls.engine = DecisionEngine(reserve_floor=970000.0)
        cls.result = cls.engine.evaluate_full_pipeline(current_cash=5_000_000.0)

    # ── Task 5: forecast_model_selection block present in response ──────────────
    def test_01_forecast_model_selection_block_present(self):
        """Response contract must include forecast_model_selection."""
        self.assertIn(
            "forecast_model_selection",
            self.result,
            "Missing 'forecast_model_selection' key in output contract"
        )

    def test_02_winner_field_present(self):
        """forecast_model_selection must contain a 'winner' key."""
        sel = self.result["forecast_model_selection"]
        self.assertIn("winner", sel)

    def test_03_winner_matches_forecaster_strategy(self):
        """Winner in response must match the forecaster's internal selected_strategy."""
        reported_winner = self.result["forecast_model_selection"]["winner"]
        internal_winner = self.engine.forecaster.selected_strategy
        self.assertEqual(
            reported_winner, internal_winner,
            f"Mismatch: response says '{reported_winner}', forecaster says '{internal_winner}'"
        )

    def test_04_selection_criterion_present(self):
        """Selection criterion string must be non-empty."""
        sel = self.result["forecast_model_selection"]
        self.assertIn("selection_criterion", sel)
        self.assertTrue(len(sel["selection_criterion"]) > 0)

    def test_05_reason_string_non_empty(self):
        """Selection reason string must be non-empty after training."""
        sel = self.result["forecast_model_selection"]
        self.assertIn("reason", sel)
        self.assertTrue(len(sel["reason"]) > 0)

    # ── Task 6: confidence score propagates into final risk level ───────────────
    def test_06_confidence_score_in_valid_range(self):
        """Confidence score from forecast_quality must be between 0.0 and 1.0."""
        conf = self.result["forecast_quality"]["confidence_score"]
        self.assertIsInstance(conf, (int, float))
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)

    def test_07_risk_level_valid_classification(self):
        """risk_level must be one of LOW / MEDIUM / HIGH / CRITICAL."""
        risk = self.result["financial_health"]["risk_level"]
        self.assertIn(risk, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def test_08_reconciliation_valid(self):
        """Combination optimizer reconciliation must always pass."""
        self.assertTrue(
            self.result["optimal_combination_summary"]["reconciliation_valid"],
            "Combination optimizer reconciliation failed"
        )

    # ── Task 1: ARIMA candidate appears when model was evaluated ────────────────
    def test_09_arima_metrics_in_all_model_metrics(self):
        """all_model_metrics must contain arima_metrics after train_and_evaluate."""
        self.assertIn("arima_metrics", self.engine.forecaster.all_model_metrics)

    def test_10_five_candidates_evaluated(self):
        """All five model keys must appear in all_model_metrics."""
        metrics = self.engine.forecaster.all_model_metrics
        expected_keys = [
            "naive_metrics", "ma_metrics", "ml_metrics",
            "ensemble_metrics", "arima_metrics"
        ]
        for key in expected_keys:
            self.assertIn(key, metrics, f"Missing key: {key}")

    def test_11_arima_candidate_in_response_if_evaluated(self):
        """If ARIMA was successfully evaluated its entry appears in candidates dict."""
        arima_m = self.engine.forecaster.all_model_metrics.get("arima_metrics", {})
        arima_mae = arima_m.get("mae")
        if isinstance(arima_mae, (int, float)):
            # ARIMA was evaluated → must appear in response candidates
            candidates = self.result["forecast_model_selection"].get("candidates", {})
            self.assertIn(
                "ARIMA_SARIMA", candidates,
                "ARIMA_SARIMA was evaluated but is missing from forecast_model_selection.candidates"
            )

    # ── Task 2 & 3: CI propagation ──────────────────────────────────────────────
    def test_12_ci_fields_present_in_response(self):
        """forecast_model_selection must always contain ci_upper_bound and ci_lower_bound."""
        sel = self.result["forecast_model_selection"]
        self.assertIn("ci_upper_bound", sel)
        self.assertIn("ci_lower_bound", sel)

    def test_13_arima_winner_ci_nonzero(self):
        """When ARIMA wins, CI bounds must be non-zero."""
        winner = self.engine.forecaster.selected_strategy
        if winner == "ARIMA_SARIMA":
            self.assertNotEqual(self.engine.forecaster.ci_upper_bound, 0.0)
            self.assertNotEqual(self.engine.forecaster.ci_lower_bound, 0.0)

    # ── Task 4: display_projected_cash / liquidity_deficit shape ────────────────
    def test_14_financial_health_projected_cash_fields(self):
        """display_projected_cash and raw_projected_cash must be present in financial_health."""
        fh = self.result["financial_health"]
        self.assertIn("raw_projected_cash", fh)
        self.assertIn("display_projected_cash", fh)
        self.assertIn("liquidity_deficit", fh)
        # display_projected_cash must always be >= 0
        self.assertGreaterEqual(fh["display_projected_cash"], 0.0)

    # ── Forecaster unit-level: train_and_evaluate includes arima_metrics key ──
    def test_15_train_evaluate_returns_arima_metrics_key(self):
        """train_and_evaluate() return dict must include arima_metrics key."""
        fc = TimeSeriesForecaster()
        res = fc.train_and_evaluate()
        self.assertIn("arima_metrics", res)


if __name__ == "__main__":
    unittest.main()
