from typing import Dict, Any, List
from .financial_state import FinancialState

class RiskEngine:
    """
    Phase 5 & 8: Financial Risk Classification Engine
    Uses raw_projected_cash and liquidity_deficit for calculations.
    Enforces CRITICAL risk level unconditionally when a genuine liquidity deficit exists.
    """

    @staticmethod
    def classify_risk(
        state: FinancialState,
        recommended_reserve: float,
        forecast_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        risk_reasons = []
        score = 0  # Risk score accumulator (0 to 100)

        raw_proj_cash = state.forecast.raw_projected_cash
        deficit = state.forecast.liquidity_deficit
        min_raw_proj = state.forecast.minimum_raw_projected_cash
        curr_cash = state.cash.current_cash
        cash_buffer = raw_proj_cash - recommended_reserve

        # Phase 5 Rule: Unconditional CRITICAL risk when genuine negative liquidity deficit exists
        if deficit > 0 or raw_proj_cash < 0 or min_raw_proj < 0:
            score += 70
            risk_reasons.append(
                f"CRITICAL Deficit: Genuine liquidity deficit of ₹{max(deficit, abs(raw_proj_cash)):,.2f} detected in forecast horizon."
            )

        # 1. Reserve Floor Breaches & Shortage
        if min_raw_proj < recommended_reserve:
            shortage = recommended_reserve - min_raw_proj
            score += 45
            risk_reasons.append(
                f"Minimum projected cash (₹{min_raw_proj:,.2f}) drops below recommended reserve (₹{recommended_reserve:,.2f}) by ₹{shortage:,.2f}."
            )
        elif cash_buffer < 0:
            score += 35
            risk_reasons.append(
                f"Projected cash (₹{raw_proj_cash:,.2f}) is below recommended reserve (₹{recommended_reserve:,.2f})."
            )
        elif cash_buffer < (recommended_reserve * 0.2):
            score += 15
            risk_reasons.append("Cash buffer is thin (<20% above recommended reserve).")

        # 2. Critical Obligations & Payroll Due Today/Soon
        crit_obligations = state.total_critical_obligations
        if crit_obligations > 0 and curr_cash < (crit_obligations + recommended_reserve):
            score += 30
            risk_reasons.append(
                f"Immediate critical obligations & payroll (₹{crit_obligations:,.2f}) threaten liquid reserve capacity."
            )

        # 3. Customer Receivable Delay & Collection Uncertainty
        delayed_recs = [r for r in state.receivables if r.expected_delay_days >= 3 or r.collection_probability < 0.80]
        if delayed_recs:
            score += 20
            total_delayed_amt = sum([r.amount for r in delayed_recs])
            risk_reasons.append(
                f"{len(delayed_recs)} key receivable(s) totalling ₹{total_delayed_amt:,.2f} have collection delay >3d or <80% probability."
            )

        # 4. Forecast Reliability & Uncertainty
        if forecast_quality.get("forecast_status") in ["UNCERTAIN", "UNRELIABLE"]:
            score += 25
            conf_display = int(forecast_quality.get('confidence_score', 0.5) * 100)
            risk_reasons.append(
                f"Forecast reliability is {forecast_quality.get('forecast_status')} (Confidence: {conf_display}%)."
            )

        # 5. Unexpected Expenses / Interest / Loan Repayments
        unex = state.other_financials.unexpected_expenses
        loan_rep = state.other_financials.loan_repayments + state.other_financials.interest_payments
        if unex > 0 or loan_rep > 0:
            score += 15
            risk_reasons.append(
                f"Additional outflow pressure detected (Unexpected: ₹{unex:,.2f}, Debt obligations: ₹{loan_rep:,.2f})."
            )

        # Final Risk Level Determination
        if score >= 65 or deficit > 0 or raw_proj_cash < 0:
            risk_level = "CRITICAL"
        elif score >= 40:
            risk_level = "HIGH"
        elif score >= 20:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if not risk_reasons:
            risk_reasons.append("Projected cash balance comfortably exceeds dynamic cash reserve requirements.")

        return {
            "risk_level": risk_level,
            "risk_score": score,
            "risk_reasons": risk_reasons
        }
