from typing import Dict, Any
from .financial_state import FinancialState

class DynamicReserveCalculator:
    """
    Phase 5: Dynamic Cash Reserve Engine
    Calculates dynamic recommended reserve based on daily outflows, risk level,
    forecast reliability, and upcoming obligation uncertainty.
    """

    DEFAULT_RESERVE_DAYS = {
        "LOW": 7,
        "MEDIUM": 10,
        "HIGH": 15,
        "CRITICAL": 20
    }

    def __init__(self, reserve_days_config: Dict[str, int] = None):
        self.reserve_days_config = reserve_days_config if reserve_days_config else self.DEFAULT_RESERVE_DAYS

    def calculate_reserve(
        self,
        state: FinancialState,
        risk_level: str = "LOW",
        forecast_quality: Dict[str, Any] = None,
        avg_daily_outflow: float = None,
        ci_width: float = 0.0
    ) -> Dict[str, Any]:
        # 1. Base Reserve Days from Risk Level
        base_days = self.reserve_days_config.get(risk_level, 10)
        
        # 2. Dynamic Adjustments
        extra_days = 0
        
        if forecast_quality:
            status = forecast_quality.get("forecast_status", "RELIABLE")
            if status == "UNCERTAIN":
                extra_days += 2
            elif status == "UNRELIABLE":
                extra_days += 4

        # CI-width guard: wide ARIMA CI → more conservative reserve
        # Threshold: ci_width > 3 days of daily outflow burn
        if ci_width > 0.0:
            burn_3d = (avg_daily_outflow or state.cash.daily_outflow or 165000.0) * 3.0
            if ci_width > burn_3d:
                extra_days += 3

        unreliable_recs = [r for r in state.receivables if r.collection_probability < 0.75 or r.expected_delay_days > 5]
        if len(unreliable_recs) > 0:
            extra_days += 2

        if state.other_financials.unexpected_expenses > 0:
            extra_days += 1

        total_reserve_days = base_days + extra_days

        # 3. Daily Outflow calculation
        if avg_daily_outflow and avg_daily_outflow > 0:
            daily_outflow = avg_daily_outflow
        elif state.cash.daily_outflow > 0:
            daily_outflow = state.cash.daily_outflow
        else:
            daily_outflow = 165000.0

        calculated_reserve = daily_outflow * total_reserve_days
        recommended_reserve = max(state.configured_min_reserve, calculated_reserve)

        # 4. Cash Buffer & Status (using raw_projected_cash)
        raw_proj = state.forecast.raw_projected_cash
        cash_buffer = raw_proj - recommended_reserve

        if cash_buffer >= (recommended_reserve * 0.5):
            balance_status = "SURPLUS"
        elif cash_buffer >= 0:
            balance_status = "HEALTHY"
        elif cash_buffer >= -(recommended_reserve * 0.25):
            balance_status = "PRESSURE"
        elif cash_buffer >= -(recommended_reserve * 0.75):
            balance_status = "SHORTAGE"
        else:
            balance_status = "CRITICAL_SHORTAGE"

        return {
            "recommended_reserve": round(recommended_reserve, 2),
            "configured_min_reserve": round(state.configured_min_reserve, 2),
            "avg_daily_outflow": round(daily_outflow, 2),
            "reserve_days": total_reserve_days,
            "base_reserve_days": base_days,
            "extra_risk_days": extra_days,
            "cash_buffer": round(cash_buffer, 2),
            "balance_status": balance_status
        }
