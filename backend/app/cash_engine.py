import numpy as np
import pandas as pd
from typing import List, Dict, Any
from app.models import Invoice, InvoiceType, InvoiceStatus, ScenarioConfig

DAILY_FIXED_OPERATIONAL_BURN = 0.35  # ₹0.35 Cr daily baseline burn (~₹35 Lakhs)
MIN_CASH_RESERVE_TARGET = 18.5       # ₹18.5 Cr Minimum Safety Buffer

def calculate_daily_forecast(
    current_cash: float,
    invoices: List[Invoice],
    days: int = 30,
    scenario: ScenarioConfig = ScenarioConfig()
) -> List[Dict[str, Any]]:
    forecast = []
    cash = current_cash - scenario.emergency_expense
    daily_burn = DAILY_FIXED_OPERATIONAL_BURN * (1.0 + scenario.opex_scaling_percent / 100.0)

    inflows_by_day = {}
    outflows_by_day = {}

    for inv in invoices:
        if inv.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            continue

        amount = inv.amount
        due_day = inv.due_days

        if inv.type == InvoiceType.AR:
            amount *= (1.0 + scenario.revenue_change_percent / 100.0)
            due_day += scenario.ar_delay_days
            inflows_by_day[due_day] = inflows_by_day.get(due_day, 0.0) + amount
        elif inv.type == InvoiceType.AP:
            outflows_by_day[due_day] = outflows_by_day.get(due_day, 0.0) + amount

    for day in range(days):
        cash -= daily_burn
        
        today_inflow = inflows_by_day.get(day, 0.0)
        cash += today_inflow

        today_outflow = outflows_by_day.get(day, 0.0)
        cash -= today_outflow

        forecast.append({
            "day": day,
            "cash_balance": round(max(cash, -10.0), 2),
            "inflows": round(today_inflow, 2),
            "outflows": round(today_outflow + daily_burn, 2),
            "net_daily_change": round(today_inflow - today_outflow - daily_burn, 2),
            "is_below_reserve": cash < MIN_CASH_RESERVE_TARGET,
            "is_cash_depleted": cash <= 0.0
        })

    return forecast

def calculate_runway_days(forecast: List[Dict[str, Any]]) -> float:
    for item in forecast:
        if item["cash_balance"] <= MIN_CASH_RESERVE_TARGET:
            return float(item["day"])
    return float(len(forecast))

def get_liquidity_summary(
    current_cash: float,
    invoices: List[Invoice],
    scenario: ScenarioConfig = ScenarioConfig()
) -> Dict[str, Any]:
    forecast_30 = calculate_daily_forecast(current_cash, invoices, days=30, scenario=scenario)
    runway = calculate_runway_days(forecast_30)

    pending_ap = sum(inv.amount for inv in invoices if inv.type == InvoiceType.AP and inv.status == InvoiceStatus.PENDING)
    pending_ar = sum(inv.amount for inv in invoices if inv.type == InvoiceType.AR and inv.status == InvoiceStatus.PENDING)

    pending_ar_adjusted = pending_ar * (1.0 + scenario.revenue_change_percent / 100.0)
    net_working_capital = current_cash + pending_ar_adjusted - pending_ap - scenario.emergency_expense

    if runway < 7 or (current_cash - scenario.emergency_expense) < MIN_CASH_RESERVE_TARGET:
        health_status = "AT RISK"
        risk_level = "High"
    elif runway < 21:
        health_status = "WATCHLIST"
        risk_level = "Moderate"
    else:
        health_status = "HEALTHY"
        risk_level = "Low"

    return {
        "current_cash": round(current_cash, 2),
        "available_cash": round(current_cash - 20.0, 2),
        "reserved_cash": 20.0,
        "min_reserve_target": MIN_CASH_RESERVE_TARGET,
        "runway_days": runway,
        "pending_ap": round(pending_ap, 2),
        "pending_ar": round(pending_ar_adjusted, 2),
        "net_working_capital": round(net_working_capital, 2),
        "health_status": health_status,
        "risk_level": risk_level,
        "forecast_chart": forecast_30
    }
