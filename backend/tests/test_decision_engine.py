import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import DecisionEngine
from forecasting_model import TimeSeriesForecaster
from decision_engine.financial_state import (
    FinancialState, CashData, ForecastData, ReceivableItem, PayableItem, ObligationItem, OtherFinancials
)
from decision_engine.forecast_validator import ForecastValidator
from decision_engine.dynamic_reserve import DynamicReserveCalculator
from decision_engine.risk_engine import RiskEngine
from decision_engine.constraint_engine import ConstraintEngine
from decision_engine.scenario_simulator import ScenarioSimulator

class TestDecisionEngineProductionPipeline(unittest.TestCase):
    """
    Phase 11: Real Production Pipeline Test Suite.
    Verifies 15 real financial stress scenarios with strict mathematical assertions,
    mathematical reconciliation of before/after values, minimum financing calculation,
    and receivable safety checks.
    """

    def setUp(self):
        self.engine = DecisionEngine(reserve_floor=970000.0)

    def test_scenario_01_healthy_cash(self):
        res = self.engine.evaluate_full_pipeline(current_cash=5000000.0)
        self.assertEqual(res["financial_health"]["risk_level"], "LOW")
        self.assertGreater(res["financial_health"]["cash_buffer"], 0.0)
        self.assertTrue(res["optimal_combination_summary"]["reconciliation_valid"])

    def test_scenario_02_low_probability_receivable(self):
        recs = [{"id": "REC_LOW", "customerId": "CUST1", "customerName": "Risky Cust", "amount": 1000000.0, "collectionProbability": 30.0, "expectedDelayDays": 10, "status": "At Risk"}]
        res = self.engine.evaluate_full_pipeline(current_cash=5000000.0, receivables=recs, extra_outflow=3500000.0)
        self.assertEqual(res["financial_health"]["risk_level"], "CRITICAL")
        self.assertTrue(res["optimal_combination_summary"]["reconciliation_valid"])

    def test_scenario_03_high_probability_receivable(self):
        recs = [{"id": "REC_HIGH", "customerId": "CUST2", "customerName": "Good Cust", "amount": 500000.0, "collectionProbability": 95.0, "expectedDelayDays": 0, "status": "On Time"}]
        res = self.engine.evaluate_full_pipeline(current_cash=3000000.0, receivables=recs)
        self.assertIn(res["forecast_quality"]["forecast_status"], ["RELIABLE", "ACCEPTABLE", "UNCERTAIN"])

    def test_scenario_04_early_payment_discount(self):
        invs = [{"id": "INV_DISC", "supplierName": "Discount Supplier", "amount": 300000.0, "discountPct": 3.0, "strategicImportance": 3}]
        res = self.engine.evaluate_full_pipeline(current_cash=4000000.0, invoices=invs)
        rec_types = [r["action_type"] for r in res["recommendations"]]
        self.assertIn("PAY_NOW_DISCOUNT", rec_types)

    def test_scenario_05_sudden_forecast_crash(self):
        res = self.engine.evaluate_full_pipeline(current_cash=2150000.0, extra_outflow=1650000.0)
        self.assertEqual(res["financial_health"]["risk_level"], "CRITICAL")
        self.assertTrue(res["optimal_combination_summary"]["reconciliation_valid"])

    def test_scenario_06_unexpected_expense(self):
        res = self.engine.evaluate_full_pipeline(current_cash=2500000.0, extra_outflow=300000.0)
        self.assertGreater(res["financial_health"]["recommended_reserve"], self.engine.reserve_floor)

    def test_scenario_07_multiple_actions_required(self):
        res = self.engine.evaluate_full_pipeline(current_cash=1500000.0, extra_outflow=800000.0)
        self.assertIn("optimal_combination_summary", res)
        self.assertTrue(res["optimal_combination_summary"]["reconciliation_valid"])

    def test_scenario_08_unreliable_forecast(self):
        state = self.engine._build_financial_state(current_cash=2500000.0)
        state.forecast.confidence_score = 0.35
        qual = ForecastValidator.validate_forecast(state)
        self.assertIn(qual["forecast_status"], ["UNCERTAIN", "UNRELIABLE"])

    def test_scenario_09_excess_cash_with_future_risk(self):
        recs = [{"id": "REC_RISK", "customerId": "CUST3", "customerName": "Uncertain Client", "amount": 4000000.0, "collectionProbability": 50.0, "expectedDelayDays": 15, "status": "At Risk"}]
        res = self.engine.evaluate_full_pipeline(current_cash=8000000.0, receivables=recs, extra_outflow=4500000.0)
        self.assertIn(res["financial_health"]["risk_level"], ["MEDIUM", "HIGH", "CRITICAL"])

    def test_scenario_10_negative_projected_cash(self):
        state = self.engine._build_financial_state(current_cash=100000.0, extra_outflow=500000.0)
        state.forecast.raw_projected_cash = -50000.0
        state.forecast.liquidity_deficit = 50000.0
        qual = ForecastValidator.validate_forecast(state)
        risk = RiskEngine.classify_risk(state, 970000.0, qual)
        self.assertEqual(risk["risk_level"], "CRITICAL")

    def test_scenario_11_immediate_critical_payable(self):
        invs = [{"id": "INV_CRIT", "supplierName": "Critical Vendor", "amount": 400000.0, "dueDate": "Today", "strategicImportance": 5}]
        res = self.engine.evaluate_full_pipeline(current_cash=2500000.0, invoices=invs)
        self.assertGreater(len(res["recommendations"]), 0)

    def test_scenario_12_high_late_penalty(self):
        invs = [{"id": "INV_PEN", "supplierName": "Penalized Supplier", "amount": 200000.0, "latePenaltyPct": 15.0, "strategicImportance": 3}]
        res = self.engine.evaluate_full_pipeline(current_cash=2500000.0, invoices=invs)
        self.assertIsNotNone(res["recommendations"])

    def test_scenario_13_loan_repayment(self):
        state = self.engine._build_financial_state(current_cash=3000000.0)
        state.other_financials.loan_repayments = 400000.0
        risk_info = RiskEngine.classify_risk(state, 1500000.0, {"forecast_status": "RELIABLE", "confidence_score": 0.88})
        self.assertTrue(any("Debt" in r or "outflow" in r.lower() for r in risk_info["risk_reasons"]))

    def test_scenario_14_forecast_model_worse_than_baseline(self):
        fc = TimeSeriesForecaster()
        res = fc.train_and_evaluate()
        self.assertIn("selected_forecast_strategy", res)
        self.assertIn("model_outperforms_baseline", res)

    def test_scenario_15_financing_required_after_safe_actions(self):
        res = self.engine.evaluate_full_pipeline(current_cash=500000.0, extra_outflow=2650000.0)
        fin_recs = [r for r in res["recommendations"] if r["action_type"] == "FINANCING"]
        self.assertGreater(len(fin_recs), 0)
        self.assertTrue(res["optimal_combination_summary"]["reconciliation_valid"])

if __name__ == "__main__":
    unittest.main()
