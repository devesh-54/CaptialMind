import sys
import os
from typing import List, Dict, Any;
from app.models import Invoice, Receivable, Obligation, ScenarioRequest;

# Import TimeSeriesForecaster which loads arima_netflow_model.pkl
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from forecasting_model import TimeSeriesForecaster

REQUIRED_30DAY_FLOOR = 15.50  # ₹15.50 Cr minimum cash floor for Tata Motors Ltd

_global_forecaster = None

def get_forecaster() -> TimeSeriesForecaster:
    global _global_forecaster
    if _global_forecaster is None:
        try:
            _global_forecaster = TimeSeriesForecaster()
            _global_forecaster.train_and_evaluate()
        except Exception as e:
            print(f"Warning: Failed to initialize TimeSeriesForecaster: {e}")
            _global_forecaster = None
    return _global_forecaster

def calculate_30day_forecast(
    current_cash: float,
    invoices: List[Invoice],
    receivables: List[Receivable],
    obligations: List[Obligation],
    scenario: ScenarioRequest = ScenarioRequest()
) -> Dict[str, Any]:
    """
    30-day forecast engine powered by ARIMA_SARIMA (arima_netflow_model.pkl):
    - Uses arima_netflow_model.pkl to project 30-day net cash flow trajectories
    - Evaluates expected vs pessimistic scenario bounds against ₹15.50 Cr reserve floor
    """
    forecaster = get_forecaster()
    
    if forecaster and forecaster.is_validated:
        # Convert cash to Lakhs/Cr scale for model prediction
        pred = forecaster.predict_30d(
            current_cash=current_cash * 100.0,  # Cr to Lakhs conversion
            receivable_delay_days=scenario.ar_delay_days,
            extra_outflow=scenario.emergency_expense * 100.0,
            expected_inflows=sum(r.amount * 100.0 for r in receivables if r.status == "PENDING"),
            expected_inflow_prob=0.87
        )

        expected_daily = []
        pessimistic_daily = []

        for idx, pt in enumerate(pred.get("projected_points", [])):
            cash_cr = pt.get("cash", 45.0) / 100.0 if pt.get("cash", 45.0) > 200 else pt.get("cash", 45.0)
            pess_cr = pt.get("pessimistic", 42.0) / 100.0 if pt.get("pessimistic", 42.0) > 200 else pt.get("pessimistic", 42.0)
            
            expected_daily.append({
                "day": idx,
                "day_label": pt.get("day", f"Day {idx}"),
                "cash_balance": round(max(0.0, cash_cr), 2),
                "below_floor": cash_cr < REQUIRED_30DAY_FLOOR
            })
            pessimistic_daily.append({
                "day": idx,
                "cash_balance": round(max(0.0, pess_cr), 2),
                "below_floor": pess_cr < REQUIRED_30DAY_FLOOR
            })

        min_exp_floor = min((d["cash_balance"] for d in expected_daily), default=27.0)
        min_pess_floor = min((d["cash_balance"] for d in pessimistic_daily), default=25.0)

        return {
            "current_cash": round(current_cash, 2),
            "available_cash": round(max(0.0, current_cash - REQUIRED_30DAY_FLOOR), 2),
            "reserved_cash": REQUIRED_30DAY_FLOOR,
            "required_30day_floor": REQUIRED_30DAY_FLOOR,
            "min_expected_floor": round(min_exp_floor, 2),
            "min_pessimistic_floor": round(min_pess_floor, 2),
            "selected_strategy": forecaster.selected_strategy,
            "forecast_reason": forecaster.selected_reason,
            "expected_trajectory": expected_daily,
            "pessimistic_trajectory": pessimistic_daily
        }

    # Fallback heuristic calculation if model unavailable
    days = 30
    expected_daily = []
    pessimistic_daily = []
    cash_exp = current_cash - scenario.emergency_expense

    for day in range(days):
        cash_exp = max(15.0, cash_exp - 0.35)
        expected_daily.append({
            "day": day,
            "day_label": f"Day {day}",
            "cash_balance": round(cash_exp, 2),
            "below_floor": cash_exp < REQUIRED_30DAY_FLOOR
        })
        pessimistic_daily.append({
            "day": day,
            "cash_balance": round(max(12.0, cash_exp - 2.0), 2),
            "below_floor": (cash_exp - 2.0) < REQUIRED_30DAY_FLOOR
        })

    return {
        "current_cash": round(current_cash, 2),
        "available_cash": round(max(0.0, current_cash - REQUIRED_30DAY_FLOOR), 2),
        "reserved_cash": REQUIRED_30DAY_FLOOR,
        "required_30day_floor": REQUIRED_30DAY_FLOOR,
        "min_expected_floor": round(min(d["cash_balance"] for d in expected_daily), 2),
        "min_pessimistic_floor": round(min(d["cash_balance"] for d in pessimistic_daily), 2),
        "selected_strategy": "HEURISTIC_FALLBACK",
        "expected_trajectory": expected_daily,
        "pessimistic_trajectory": pessimistic_daily
    }
