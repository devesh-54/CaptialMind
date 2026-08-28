from typing import Dict, Any, List, Tuple
from .financial_state import FinancialState
from .constraint_engine import ConstraintEngine

class CombinationOptimizer:
    """
    Phase 8 & 10: Combination Decision Optimizer
    Evaluates combinations of candidate actions to find the minimal safe set
    that restores raw projected cash balance above the dynamic recommended reserve.
    """

    PREFERRED_ORDER = [
        "ACCELERATE_RECEIVABLE",
        "PAY_NOW_DISCOUNT",
        "PAY_AT_MATURITY",
        "REDUCE_EXPENSE",
        "PREPAY_DEBT",
        "DELAY_PAYABLE",
        "FINANCING"
    ]

    @staticmethod
    def _order_key(action: Dict[str, Any]) -> Tuple[int, float]:
        a_type = action.get("action_type", "")
        prio_idx = CombinationOptimizer.PREFERRED_ORDER.index(a_type) if a_type in CombinationOptimizer.PREFERRED_ORDER else 99
        score = action.get("score", 0.0)
        return (prio_idx, -score)

    @staticmethod
    def optimize_combination(
        safe_actions: List[Dict[str, Any]],
        state: FinancialState,
        recommended_reserve: float
    ) -> Dict[str, Any]:
        raw_proj_cash = state.forecast.raw_projected_cash
        required_gap = max(0.0, recommended_reserve - raw_proj_cash)

        sorted_candidates = sorted(safe_actions, key=CombinationOptimizer._order_key)

        selected = []
        accumulated_impact = 0.0
        accumulated_outflow = 0.0

        current_sim_cash = raw_proj_cash

        for action in sorted_candidates:
            fin_impact = float(action.get("financial_impact", 0.0))
            outflow = float(action.get("outflow", 0.0))
            a_type = action.get("action_type", "")
            
            if a_type == "FINANCING":
                net_delta = float(action.get("financing_amount", 0.0)) + fin_impact
            else:
                net_delta = fin_impact - outflow

            if required_gap > 0:
                selected.append(action)
                accumulated_impact += fin_impact
                accumulated_outflow += outflow
                current_sim_cash += net_delta
                
                if current_sim_cash >= recommended_reserve:
                    break
            else:
                if not selected:
                    selected.append(action)
                    accumulated_impact += fin_impact
                    accumulated_outflow += outflow
                    current_sim_cash += net_delta
                    break

        solves_gap = current_sim_cash >= recommended_reserve

        return {
            "selected_actions": selected,
            "combined_financial_impact": round(accumulated_impact, 2),
            "combined_outflow": round(accumulated_outflow, 2),
            "net_cash_delta": round(current_sim_cash - raw_proj_cash, 2),
            "projected_cash_after_combination": round(current_sim_cash, 2),
            "solves_liquidity_gap": solves_gap
        }
