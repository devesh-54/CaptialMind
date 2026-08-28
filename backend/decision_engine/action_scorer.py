from typing import Dict, Any, List
from .financial_state import FinancialState

class ActionScorer:
    """
    Phase 9: Action Scoring Engine
    Scores candidate actions using configurable multi-factor weighting.
    Factors: Liquidity (35%), Financial Benefit (20%), Risk Reduction (20%), Urgency (15%), Operational (10%).
    """

    DEFAULT_WEIGHTS = {
        "liquidity": 0.35,
        "financial": 0.20,
        "risk": 0.20,
        "urgency": 0.15,
        "operational": 0.10
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights if weights else self.DEFAULT_WEIGHTS
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    def score_action(
        self,
        action: Dict[str, Any],
        state: FinancialState,
        recommended_reserve: float,
        risk_level: str
    ) -> Dict[str, Any]:
        action_type = action.get("action_type", "")
        fin_impact = float(action.get("financial_impact", 0.0))
        outflow = float(action.get("outflow", 0.0))
        urgency_raw = float(action.get("urgency", 50))
        op_impact_raw = float(action.get("operational_impact", 50))

        raw_proj_cash = state.forecast.raw_projected_cash
        cash_buffer = raw_proj_cash - recommended_reserve

        # 1. Liquidity Improvement Sub-score (0 to 100)
        net_liquidity_delta = fin_impact - outflow
        if action_type == "FINANCING":
            fin_amt = float(action.get("financing_amount", 0.0))
            liquidity_sub = min(100.0, max(20.0, (fin_amt / max(1.0, recommended_reserve)) * 100.0))
        elif net_liquidity_delta >= 0:
            liquidity_sub = min(100.0, 50.0 + (net_liquidity_delta / 10000.0))
        else:
            if cash_buffer >= abs(net_liquidity_delta):
                liquidity_sub = max(40.0, 80.0 - (abs(net_liquidity_delta) / 20000.0))
            else:
                liquidity_sub = max(10.0, 30.0 - (abs(net_liquidity_delta) / 10000.0))

        # 2. Financial Benefit Sub-score (0 to 100)
        if fin_impact > 0:
            financial_sub = min(100.0, 70.0 + (fin_impact / 5000.0))
        elif fin_impact == 0:
            financial_sub = 50.0
        else:
            financial_sub = max(10.0, 50.0 - (abs(fin_impact) / 1000.0))

        # 3. Risk Reduction Sub-score (0 to 100)
        if risk_level in ["HIGH", "CRITICAL"]:
            if action_type in ["ACCELERATE_RECEIVABLE", "FINANCING", "REDUCE_EXPENSE"]:
                risk_sub = 90.0
            elif action_type == "PAY_NOW_DISCOUNT" and cash_buffer > outflow:
                risk_sub = 85.0
            elif action_type == "DELAY_PAYABLE":
                risk_sub = 30.0
            else:
                risk_sub = 50.0
        else:
            if action_type in ["PAY_NOW_DISCOUNT", "PREPAY_DEBT"]:
                risk_sub = 95.0
            elif action_type == "FINANCING":
                risk_sub = 55.0
            else:
                risk_sub = 75.0

        # 4. Urgency & Operational Impact Sub-scores
        urgency_sub = float(max(0.0, min(100.0, urgency_raw)))
        operational_sub = float(max(0.0, min(100.0, op_impact_raw)))

        composite_score = (
            (liquidity_sub * self.weights["liquidity"]) +
            (financial_sub * self.weights["financial"]) +
            (risk_sub * self.weights["risk"]) +
            (urgency_sub * self.weights["urgency"]) +
            (operational_sub * self.weights["operational"])
        )

        final_score_normalized = round(composite_score / 100.0, 2)
        score_100 = int(round(composite_score))

        return {
            "score": final_score_normalized,
            "score_100": score_100,
            "subScores": {
                "liquidity": int(round(liquidity_sub)),
                "financial": int(round(financial_sub)),
                "risk": int(round(risk_sub)),
                "urgency": int(round(urgency_sub)),
                "operational": int(round(operational_sub))
            }
        }
