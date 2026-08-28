from typing import Dict, Any, List
from .financial_state import FinancialState

class ExplanationEngine:
    """
    Phase 13 & 14: Output Contract & Evidence Explanation Engine
    Formats the final structured result JSON payload with complete calculation trace,
    receivable expected value breakdown, early discount validation, and mathematical reconciliation.
    """

    @staticmethod
    def build_output_contract(
        state: FinancialState,
        forecast_quality: Dict[str, Any],
        reserve_info: Dict[str, Any],
        risk_info: Dict[str, Any],
        ranked_safe_actions: List[Dict[str, Any]],
        selected_combination: Dict[str, Any],
        before_after_simulation: Dict[str, Any],
        all_model_metrics: Dict[str, Any] = None,
        forecast_selection_reason: str = ""
    ) -> Dict[str, Any]:
        
        # 1. Financial Health Section
        financial_health = {
            "current_cash": round(state.cash.current_cash, 2),
            "raw_projected_cash": round(state.forecast.raw_projected_cash, 2),
            "display_projected_cash": round(state.forecast.display_projected_cash, 2),
            "liquidity_deficit": round(state.forecast.liquidity_deficit, 2),
            "recommended_reserve": round(reserve_info["recommended_reserve"], 2),
            "cash_buffer": round(reserve_info["cash_buffer"], 2),
            "risk_level": risk_info["risk_level"],
            "risk_score": risk_info["risk_score"],
            "balance_status": reserve_info["balance_status"]
        }

        # 2. Problem Detection Section
        cash_buffer = reserve_info["cash_buffer"]
        if state.forecast.liquidity_deficit > 0:
            prob_type = "GENUINE_CASH_DEFICIT"
            prob_amount = round(state.forecast.liquidity_deficit, 2)
        elif cash_buffer < 0:
            prob_type = "LIQUIDITY_SHORTAGE"
            prob_amount = round(abs(cash_buffer), 2)
        elif risk_info["risk_level"] in ["HIGH", "CRITICAL"]:
            prob_type = "HIGH_LIQUIDITY_RISK"
            prob_amount = round(reserve_info["recommended_reserve"] - state.forecast.minimum_display_projected_cash, 2)
        else:
            prob_type = "NONE"
            prob_amount = 0.0

        # 2b. Dynamic Expected Date Determination
        from datetime import datetime
        exp_date = datetime.now().strftime("%Y-%m-%d")
        if state.forecast.projected_points:
            min_pt = min(state.forecast.projected_points, key=lambda x: x.get("raw_cash", 0.0))
            if min_pt and min_pt.get("day"):
                exp_date = str(min_pt.get("day"))

        problem_detected = {
            "type": prob_type,
            "amount": max(0.0, prob_amount),
            "expected_date": exp_date,
            "risk_reasons": risk_info.get("risk_reasons", [])
        }

        # 3. Recommendations Section
        recommendations = []
        for idx, act in enumerate(ranked_safe_actions[:5], 1):
            is_selected = act in selected_combination.get("selected_actions", [])
            rec_item = {
                "priority": idx,
                "action": act.get("title", act.get("id")),
                "action_type": act.get("action_type"),
                "score": act.get("score", 0.0),
                "score_100": act.get("score_100", 0),
                "subScores": act.get("subScores", {}),
                "reason": act.get("description", ""),
                "financial_impact": act.get("financial_impact", 0.0),
                "outflow": act.get("outflow", 0.0),
                "risk_reduction": act.get("subScores", {}).get("risk", 70),
                "selected_in_optimal_combination": is_selected,
                "warnings": act.get("warnings", [])
            }

            # Phase 9: Receivable safety fields
            if act.get("action_type") == "ACCELERATE_RECEIVABLE":
                rec_item["receivable_details"] = {
                    "invoice_amount": act.get("invoice_amount", 0.0),
                    "collection_probability": act.get("collection_probability", 0.0),
                    "expected_liquidity_contribution": act.get("expected_liquidity_contribution", 0.0),
                    "expected_delay_days": act.get("expected_delay", 0)
                }

            # Phase 10: Early discount validation fields
            if act.get("action_type") == "PAY_NOW_DISCOUNT":
                rec_item["discount_details"] = {
                    "invoice_amount": act.get("invoice_amount", 0.0),
                    "discount_percentage": act.get("discount_percentage", 0.0),
                    "discount_benefit": act.get("discount_benefit", 0.0),
                    "cash_buffer_before": round(reserve_info["cash_buffer"], 2),
                    "cash_buffer_after": round(reserve_info["cash_buffer"] - act.get("outflow", 0.0) + act.get("discount_benefit", 0.0), 2)
                }

            recommendations.append(rec_item)

        # 4. Warnings aggregation
        global_warnings = list(forecast_quality.get("warnings", []))
        if cash_buffer < 0:
            global_warnings.append(f"Immediate liquidity gap of ₹{abs(cash_buffer):,.2f} requires working capital action.")

        # 5. Forecast Model Selection block
        candidate_metrics = {}
        if all_model_metrics:
            name_map = {
                "naive_metrics": "NAIVE_BASELINE",
                "ma_metrics": "MOVING_AVERAGE_7D",
                "ml_metrics": "RIDGE_ML",
                "ensemble_metrics": "WEIGHTED_ENSEMBLE",
                "arima_metrics": "ARIMA_SARIMA",
            }
            for key, label in name_map.items():
                m = all_model_metrics.get(key, {})
                if m and isinstance(m.get("mae"), (int, float)):
                    candidate_metrics[label] = {
                        "mae": m.get("mae"),
                        "mape": m.get("mape"),
                        "r2": m.get("r2")
                    }

        forecast_model_selection = {
            "winner": state.forecast.selected_strategy,
            "selection_criterion": "lowest test-period MAE (80/20 chronological split)",
            "candidates": candidate_metrics,
            "reason": forecast_selection_reason,
            "ci_upper_bound": round(state.forecast.ci_upper_bound, 2),
            "ci_lower_bound": round(state.forecast.ci_lower_bound, 2),
        }

        return {
            "financial_health": financial_health,
            "forecast_quality": forecast_quality,
            "forecast_model_selection": forecast_model_selection,
            "problem_detected": problem_detected,
            "recommendations": recommendations,
            "optimal_combination_summary": {
                "selected_count": len(selected_combination.get("selected_actions", [])),
                "combined_financial_impact": selected_combination.get("combined_financial_impact", 0.0),
                "net_cash_delta": selected_combination.get("net_cash_delta", 0.0),
                "solves_liquidity_gap": selected_combination.get("solves_liquidity_gap", True),
                "reconciliation_valid": before_after_simulation.get("reconciliation_valid", True),
                "calculation_trace": before_after_simulation.get("calculation_trace", [])
            },
            "before_decision": before_after_simulation["before_decision"],
            "after_decision": before_after_simulation["after_decision"],
            "warnings": global_warnings
        }
