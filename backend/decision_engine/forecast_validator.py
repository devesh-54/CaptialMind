from typing import Dict, Any, List
from .financial_state import FinancialState

class ForecastValidator:
    """
    Phase 3 & 4: Forecast Reliability Layer
    Evaluates historical error metrics, dynamic confidence score, business bounds,
    and returns a structured reliability report with explicit reasons.
    """

    @staticmethod
    def validate_forecast(
        state: FinancialState,
        forecast_metrics: Dict[str, Any] = None,
        confidence_score: float = None,
        ci_width: float = 0.0
    ) -> Dict[str, Any]:
        warnings = []
        reasons = []
        
        # 1. Dynamic Error Metrics
        metrics = forecast_metrics if forecast_metrics else {
            "mae": state.forecast.mae,
            "rmse": state.forecast.rmse,
            "mape": state.forecast.mape,
            "r2": state.forecast.r2
        }

        mape = metrics.get("mape")
        r2 = metrics.get("r2")

        # 2. Confidence Score Determination
        if confidence_score is None:
            confidence = state.forecast.confidence_score
        else:
            confidence = max(0.0, min(1.0, confidence_score))

        # 2b. CI-width penalty (model-agnostic: only applies when ci_width > 0)
        # A wide confidence interval relative to the historical balance std-dev signals
        # elevated forecast uncertainty → reduce confidence by up to 15%.
        if ci_width > 0.0:
            raw_cash = abs(state.forecast.raw_projected_cash)
            ref_scale = max(1.0, raw_cash)
            ci_ratio = ci_width / ref_scale
            # Scale: ci_ratio >= 1.0 → full 15% penalty; ci_ratio <= 0 → no penalty
            ci_penalty = min(0.15, max(0.0, ci_ratio * 0.15))
            confidence = round(confidence * (1.0 - ci_penalty), 2)

        # 3. Business Bound & Anomaly Checks
        raw_proj_cash = state.forecast.raw_projected_cash
        deficit = state.forecast.liquidity_deficit
        min_raw_proj = state.forecast.minimum_raw_projected_cash
        curr_cash = state.cash.current_cash

        # Unrealistic jumps (>50% single-day change without recorded transaction)
        if curr_cash > 0 and abs(raw_proj_cash - curr_cash) / curr_cash > 0.5:
            warnings.append("Significant cash flow jump detected between current cash and projected cash.")
            reasons.append("Significant cash flow jump detected between current cash and projected cash.")
            confidence = round(confidence * 0.85, 2)

        # Genuine Negative Cash Deficit
        if deficit > 0 or raw_proj_cash < 0 or min_raw_proj < 0:
            warnings.append(f"Forecast projects genuine cash deficit of ₹{max(deficit, abs(raw_proj_cash)):,.2f}.")
            reasons.append("Forecast projects genuine liquidity deficit in 30-day horizon.")
            confidence = round(confidence * 0.75, 2)

        # High receivable collection uncertainty check
        high_risk_receivables = [r for r in state.receivables if r.collection_probability < 0.70 or r.expected_delay_days > 5]
        if high_risk_receivables:
            warnings.append(f"{len(high_risk_receivables)} customer receivable(s) have high collection uncertainty or severe delay.")
            reasons.append(f"{len(high_risk_receivables)} customer receivable(s) have collection uncertainty or delay >5d.")
            confidence = round(confidence * 0.90, 2)

        # 4. Determine Forecast Status
        if isinstance(mape, (int, float)) and isinstance(r2, (int, float)):
            if confidence >= 0.80 and mape <= 8.0:
                status = "RELIABLE"
            elif confidence >= 0.60 and mape <= 15.0:
                status = "ACCEPTABLE"
            elif confidence >= 0.40:
                status = "UNCERTAIN"
                warnings.append("Forecast reliability is UNCERTAIN. Dynamic safety buffer increased.")
                reasons.append("Recent prediction uncertainty elevated.")
            else:
                status = "UNRELIABLE"
                warnings.append("Forecast reliability is UNRELIABLE. Conservative capital deployment enforced.")
                reasons.append("Forecast error metrics exceed reliability threshold.")
        else:
            status = "ACCEPTABLE"

        if not reasons:
            reasons.append("Selected forecasting model error metrics meet reliability thresholds.")

        return {
            "forecast_status": status,
            "confidence_score": round(confidence, 2),
            "mae": metrics.get("mae", "NOT AVAILABLE"),
            "rmse": metrics.get("rmse", "NOT AVAILABLE"),
            "mape": metrics.get("mape", "NOT AVAILABLE"),
            "r2": metrics.get("r2", "NOT AVAILABLE"),
            "reasons": reasons,
            "warnings": warnings,
            "requires_conservative_buffer": status in ["UNCERTAIN", "UNRELIABLE"]
        }
