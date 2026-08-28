import math
from typing import Dict, Any, List, Tuple
from .financial_state import FinancialState, PayableItem, ReceivableItem, ObligationItem

class ConstraintEngine:
    """
    Phase 6 & 10: Hard Financial Constraints Engine
    Validates candidate actions against hard liquidity safety rules and business constraints.
    Rejects unsafe recommendations.
    """

    @staticmethod
    def validate_action(
        action: Dict[str, Any],
        state: FinancialState,
        recommended_reserve: float,
        forecast_quality: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        violations = []
        action_type = action.get("action_type", "")
        financial_impact = float(action.get("financial_impact", 0.0))
        outflow = float(action.get("outflow", 0.0))
        target_item = action.get("target_item")

        # 0. Check NaN / Infinity / Invalid numerical values
        for k, v in action.items():
            if isinstance(v, (int, float)):
                if math.isnan(v) or math.isinf(v):
                    violations.append(f"Hard Constraint Violation: Field '{k}' contains invalid NaN/Inf numeric value.")
                    return False, violations

        raw_proj_after = state.forecast.raw_projected_cash + financial_impact - outflow

        # 1. Floor Breach Constraint
        if action_type != "FINANCING" and raw_proj_after < recommended_reserve:
            shortage = recommended_reserve - raw_proj_after
            violations.append(
                f"Hard Constraint Violation: Action reduces projected cash below recommended reserve by ₹{shortage:,.2f}."
            )

        # 2. Critical Obligation Delay Constraint
        if action_type == "DELAY_PAYABLE" and target_item:
            if isinstance(target_item, PayableItem) and target_item.is_critical:
                if not action.get("critical_risk_flagged", False):
                    violations.append(
                        f"Hard Constraint Violation: Un-flagged delay of CRITICAL supplier obligation ({target_item.supplier_name})."
                    )

        # 3. Receivable Realism Constraint (Phase 9: <40% probability cannot be accelerated as guaranteed cash)
        if action_type == "ACCELERATE_RECEIVABLE" and target_item:
            if isinstance(target_item, ReceivableItem):
                if target_item.collection_probability < 0.40:
                    violations.append(
                        f"Hard Constraint Violation: Cannot accelerate receivable ({target_item.id}) with collection probability <40%."
                    )

        # 4. Early Discount vs Liquidity Cost Constraint (Phase 10)
        if action_type == "PAY_NOW_DISCOUNT" and target_item:
            if isinstance(target_item, PayableItem):
                discount_savings = target_item.amount * (target_item.discount_percentage / 100.0)
                cash_buffer_after = raw_proj_after - recommended_reserve
                
                if discount_savings <= 0:
                    violations.append("Hard Constraint Violation: Early discount yield is not positive.")
                elif cash_buffer_after < 0:
                    violations.append(
                        f"Hard Constraint Violation: Early payment creates liquidity shortage of ₹{abs(cash_buffer_after):,.2f} below reserve."
                    )

        # 5. Low Forecast Reliability Penalty
        if forecast_quality.get("requires_conservative_buffer") and action_type in ["PAY_NOW_DISCOUNT", "PREPAY_DEBT"]:
            if raw_proj_after < (recommended_reserve * 1.15):
                violations.append(
                    "Hard Constraint Violation: Aggressive deployment rejected due to UNCERTAIN/UNRELIABLE forecast quality."
                )

        is_safe = len(violations) == 0
        return is_safe, violations
