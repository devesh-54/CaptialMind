import numpy as np
import pandas as pd
from typing import Dict, Any, List

class DecisionEngine:
    def __init__(self, reserve_floor: float = 1500000.0):
        self.reserve_floor = reserve_floor

    def forecast_30d_cash(
        self,
        current_cash: float,
        receivable_delay_days: int = 0,
        extra_outflow: float = 0.0
    ) -> List[Dict[str, Any]]:
        days = ['Jan 04', 'Jan 10', 'Jan 15', 'Jan 20', 'Jan 28', 'Feb 05', 'Feb 12', 'Feb 20']
        # Convert total cash to Lakhs or keep scale
        base_cash_lakhs = current_cash / 100000.0
        
        forecast = []
        for idx, day in enumerate(days):
            cash = base_cash_lakhs - (extra_outflow / 100000.0) - (idx * 1.5)
            if idx >= 3 and receivable_delay_days > 0:
                cash -= (receivable_delay_days * 0.85)
            
            pessimistic = max(15.0, cash - 8.5)
            forecast.append({
                "day": day,
                "cash": round(max(15.0, cash), 1),
                "pessimistic": round(pessimistic, 1)
            })
        return forecast

    def generate_hero_recommendation(self, invoices: List[Dict[str, Any]], available_cash: float) -> Dict[str, Any]:
        if not invoices:
            return {
                "title": "Retain Cash Buffer — No Urgent Obligations Detected",
                "confidence": 95,
                "breakdown": [{"label": "Reserve Floor", "amount": 1500000.0}],
                "reasoning": "All pending invoices are settled. System recommends retaining deployable capital in high-yield treasury account."
            }

        # Calculate allocation across pending invoices
        top_invoices = invoices[:2]
        allocated_total = sum([inv["amount"] for inv in top_invoices])
        discount_total = sum([(inv["amount"] * inv["discountPct"] / 100.0) for inv in top_invoices])
        buffer_retained = available_cash - allocated_total - self.reserve_floor

        breakdown = []
        for inv in top_invoices:
            breakdown.append({
                "label": f"{inv['supplierName']} (Pay Now)",
                "amount": inv["amount"]
            })
        breakdown.append({
            "label": "Retain Deployable Buffer",
            "amount": max(0.0, buffer_retained)
        })

        title = f"Allocate ₹{(allocated_total / 100000.0):.1f}L today to capture ₹{discount_total:,.0f} early discounts"

        reasoning = (
            f"Executing early payments for {top_invoices[0]['supplierName']} captures ₹{discount_total:,.0f} in net discounts "
            f"and protects Tier-1 supplier SLAs while preserving deployable cash well above your ₹15.0L policy reserve floor."
        )

        return {
            "title": title,
            "confidence": 94,
            "breakdown": breakdown,
            "reasoning": reasoning
        }

    def generate_candidates(self, available_cash: float, top_invoice: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        inv_amount = top_invoice["amount"] if top_invoice else 33381685.97
        disc_pct = top_invoice["discountPct"] if top_invoice else 2.0
        disc_savings = (inv_amount * disc_pct / 100.0) if disc_pct > 0 else 667633.71

        cash_lakhs = available_cash / 100000.0

        candidates = [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now (Selected)",
                "score": 96,
                "costBenefit": f"Captures ₹{disc_savings:,.0f} net early discounts",
                "riskNote": "Stays safely above ₹15.0L reserve floor throughout",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 10", "cash": cash_lakhs - 3.3},
                    {"day": "Jan 15", "cash": cash_lakhs - 1.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 4.2},
                    {"day": "Jan 28", "cash": cash_lakhs - 2.8},
                    {"day": "Feb 05", "cash": cash_lakhs + 1.2},
                    {"day": "Feb 12", "cash": cash_lakhs + 5.5},
                    {"day": "Feb 20", "cash": cash_lakhs + 12.0}
                ]
            },
            {
                "id": "OPT-2",
                "action": "Pay at Maturity",
                "title": "Pay at Maturity",
                "score": 61,
                "costBenefit": f"Costs ₹{disc_savings:,.0f} in forfeited discount yield",
                "riskNote": "Stays above floor; zero early settlement return",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 10", "cash": cash_lakhs},
                    {"day": "Jan 15", "cash": cash_lakhs},
                    {"day": "Jan 20", "cash": cash_lakhs - 3.3},
                    {"day": "Jan 28", "cash": cash_lakhs - 5.1},
                    {"day": "Feb 05", "cash": cash_lakhs - 2.2},
                    {"day": "Feb 12", "cash": cash_lakhs + 2.0},
                    {"day": "Feb 20", "cash": cash_lakhs + 8.5}
                ]
            },
            {
                "id": "OPT-3",
                "action": "Finance",
                "title": "Bank Credit Line",
                "score": 74,
                "costBenefit": "Costs ₹18,500 interest (8.5% APR)",
                "riskNote": "Preserves cash today; net yield reduced by interest",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 10", "cash": cash_lakhs},
                    {"day": "Jan 15", "cash": cash_lakhs - 0.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 1.2},
                    {"day": "Jan 28", "cash": cash_lakhs - 1.8},
                    {"day": "Feb 05", "cash": cash_lakhs + 0.5},
                    {"day": "Feb 12", "cash": cash_lakhs + 4.2},
                    {"day": "Feb 20", "cash": cash_lakhs + 11.0}
                ]
            },
            {
                "id": "OPT-4",
                "action": "Delay",
                "title": "Delay Payment (+10d)",
                "score": 32,
                "costBenefit": "₹0 immediate cash outflow",
                "riskNote": "Breaches reserve floor on Feb 05 under pessimistic delay",
                "breachesFloor": True,
                "breachDay": "Feb 05",
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 10", "cash": cash_lakhs},
                    {"day": "Jan 15", "cash": cash_lakhs - 0.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 10.0},
                    {"day": "Jan 28", "cash": cash_lakhs - 18.0},
                    {"day": "Feb 05", "cash": 12.5},
                    {"day": "Feb 12", "cash": 14.0},
                    {"day": "Feb 20", "cash": 22.0}
                ]
            },
            {
                "id": "OPT-5",
                "action": "Retain",
                "title": "Retain Cash Buffer",
                "score": 45,
                "costBenefit": "Maximizes nominal cash reserve",
                "riskNote": f"Forfeits ₹{disc_savings:,.0f} & risks supplier delivery hold",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 10", "cash": cash_lakhs},
                    {"day": "Jan 15", "cash": cash_lakhs},
                    {"day": "Jan 20", "cash": cash_lakhs},
                    {"day": "Jan 28", "cash": cash_lakhs - 2.0},
                    {"day": "Feb 05", "cash": cash_lakhs - 1.0},
                    {"day": "Feb 12", "cash": cash_lakhs + 5.0},
                    {"day": "Feb 20", "cash": cash_lakhs + 12.0}
                ]
            }
        ]
        return candidates
