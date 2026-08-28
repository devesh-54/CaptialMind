from typing import List, Dict, Any
from app.models import Invoice, Receivable, Obligation, ScenarioRequest

REQUIRED_30DAY_FLOOR = 18.5  # ₹18.5 Cr minimum cash floor

def calculate_30day_forecast(
    current_cash: float,
    invoices: List[Invoice],
    receivables: List[Receivable],
    obligations: List[Obligation],
    scenario: ScenarioRequest = ScenarioRequest()
) -> Dict[str, Any]:
    """
    30-day forecast engine:
    - Expected Value: P(on_time) * inflow + P(late) * delayed_inflow
    - Pessimistic Scenario: all uncertain receivables delayed
    """
    days = 30
    expected_daily = []
    pessimistic_daily = []

    cash_exp = current_cash - scenario.emergency_expense
    cash_pess = current_cash - scenario.emergency_expense

    daily_fixed_burn = 0.35  # ₹0.35 Cr daily baseline operating burn

    for day in range(days):
        # Inflows expected today
        inflow_exp = 0.0
        inflow_pess = 0.0

        for r in receivables:
            if r.status != "PENDING":
                continue

            prob = max(0.1, r.collection_probability * (1.0 - scenario.revenue_shock_percent / 100.0))
            expected_due_day = r.due_days
            delayed_due_day = r.due_days + int(r.expected_delay_days) + scenario.ar_delay_days

            # Expected Value math
            if expected_due_day == day:
                inflow_exp += r.amount * prob
            if delayed_due_day == day:
                inflow_exp += r.amount * (1.0 - prob)

            # Pessimistic math (All delayed)
            if delayed_due_day == day:
                inflow_pess += r.amount * prob

        # Outflows expected today
        outflow = daily_fixed_burn
        for inv in invoices:
            if inv.status == "PENDING" and inv.due_days == day:
                outflow += inv.amount
        for ob in obligations:
            if ob.status == "PENDING" and ob.due_days == day:
                outflow += ob.amount

        # Update running balances
        cash_exp = cash_exp + inflow_exp - outflow
        cash_pess = cash_pess + inflow_pess - outflow

        expected_daily.append({
            "day": day,
            "day_label": f"Day {day}",
            "cash_balance": round(max(cash_exp, -10.0), 2),
            "inflow": round(inflow_exp, 2),
            "outflow": round(outflow, 2),
            "below_floor": cash_exp < REQUIRED_30DAY_FLOOR
        })

        pessimistic_daily.append({
            "day": day,
            "cash_balance": round(max(cash_pess, -10.0), 2),
            "below_floor": cash_pess < REQUIRED_30DAY_FLOOR
        })

    # Find minimum point on curve over 30 days
    min_exp_floor = min(d["cash_balance"] for d in expected_daily)
    min_pess_floor = min(d["cash_balance"] for d in pessimistic_daily)

    return {
        "current_cash": round(current_cash, 2),
        "available_cash": round(current_cash - 20.0, 2),
        "reserved_cash": 20.0,
        "required_30day_floor": REQUIRED_30DAY_FLOOR,
        "min_expected_floor": round(min_exp_floor, 2),
        "min_pessimistic_floor": round(min_pess_floor, 2),
        "expected_trajectory": expected_daily,
        "pessimistic_trajectory": pessimistic_daily
    }
