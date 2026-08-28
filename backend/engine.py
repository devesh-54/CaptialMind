import numpy as np
import pandas as pd
import time
from typing import Dict, Any, List, Tuple

class MaterialityChangeDetector:
    """Evaluates whether an incoming financial telemetry event constitutes a material change requiring re-optimization."""

    @staticmethod
    def is_material_change(
        event_type: str,
        delay_days: int = 0,
        outflow_lakhs: float = 0.0,
        prob_delta: float = 0.0,
        risk_shift: bool = False,
        rate_shift_pct: float = 0.0
    ) -> Tuple[bool, str]:
        
        if delay_days >= 3:
            return True, f"Material Receivable Delay: Expected payment delayed by +{delay_days} days."

        if outflow_lakhs >= 1.0:
            return True, f"Material Cash Outflow: Significant capital shift of ₹{outflow_lakhs:.1f}L."

        if abs(prob_delta) >= 15.0:
            return True, f"Material Bayesian Probability Shift: Customer collection confidence shifted by {prob_delta:.1f}%."

        if risk_shift:
            return True, "Material Supplier Risk Shift: Tier-1 supplier liquidity risk escalated."

        if abs(rate_shift_pct) >= 1.5:
            return True, f"Material Interest Rate Shift: Financing line APR changed by {rate_shift_pct:.1f}%."

        if event_type in ["RECEIVABLE_DELAYED", "REOPTIMIZE_TRIGGER"]:
            return True, f"Material Trigger Event: {event_type} invoked."

        return False, "Monitored telemetry update — below materiality threshold (<2% cash delta, <3d delay). Strategy retained."


class DecisionEngine:
    def __init__(self, reserve_floor: float = 970000.0):
        self.reserve_floor = reserve_floor
        self.change_detector = MaterialityChangeDetector()

    def update_bayesian_probability(self, receivable: Dict[str, Any], on_time: bool = False) -> Dict[str, Any]:
        """Performs Beta-Binomial updating on customer collection probability: Beta(alpha + 1, beta) or Beta(alpha, beta + 1)"""
        alpha = receivable.get("alpha", 10)
        beta = receivable.get("beta", 2)
        obs = receivable.get("observationsCount", 11) + 1

        if on_time:
            alpha += 1
        else:
            beta += 1

        new_prob = round((alpha / (alpha + beta)) * 100.0, 1)
        new_delay = 0 if new_prob >= 90 else 4 if new_prob >= 75 else 10
        status = "On Time" if new_delay == 0 else "Slight Delay" if new_delay <= 5 else "At Risk"

        receivable["alpha"] = alpha
        receivable["beta"] = beta
        receivable["observationsCount"] = obs
        receivable["collectionProbability"] = new_prob
        receivable["expectedDelayDays"] = new_delay
        receivable["status"] = status
        return receivable

    def forecast_30d_cash(
        self,
        current_cash: float,
        receivables: List[Dict[str, Any]] = None,
        receivable_delay_days: int = 0,
        extra_outflow: float = 0.0
    ) -> List[Dict[str, Any]]:
        days = ['Aug 28', 'Aug 29 (Opex)', 'Sep 01', 'Sep 05', 'Sep 15 (REC_0365)', 'Sep 28', 'Oct 08', 'Oct 18']
        base_cash_lakhs = current_cash / 100000.0
        
        cust_a_prob = 0.87
        if receivables and len(receivables) > 0:
            cust_a_prob = (receivables[0].get("collectionProbability", 87.0)) / 100.0

        forecast = []
        for idx, day in enumerate(days):
            cash = base_cash_lakhs - (extra_outflow / 100000.0) - (idx * 0.15)
            if idx == 1:
                cash -= 16.5  # Daily operating expense & salary outflow (₹16.5L)
            if idx == 4:
                expected_inflow = 0.317 * cust_a_prob  # REC_FUT_0365 (₹31.76k)
                if receivable_delay_days > 0:
                    expected_inflow = expected_inflow * max(0.2, 1.0 - (receivable_delay_days * 0.1))
                cash += expected_inflow
            
            pessimistic = max(9.7, cash - 1.5)
            forecast.append({
                "day": day,
                "cash": round(max(9.7, cash), 1),
                "pessimistic": round(pessimistic, 1)
            })
        return forecast

    def generate_hero_recommendation(
        self, 
        invoices: List[Dict[str, Any]], 
        available_cash: float,
        receivables: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        top_inv = invoices[0] if invoices else {"amount": 68902.88, "supplierName": "Bosch Ltd (INV_FUT_0260)", "discountPct": 0.0}
        inv_2 = invoices[1] if len(invoices) > 1 else {"amount": 140555.66, "supplierName": "Bosch Ltd (INV_FUT_0261)", "discountPct": 0.0}
        opex_amount = 1650000.0  # Daily Opex & Payroll from future_daily_consolidated.csv

        cust_name = receivables[0]["customerName"] if receivables else "CUST011"
        cust_prob = receivables[0]["collectionProbability"] if receivables else 87.0

        total_alloc = top_inv["amount"] + inv_2["amount"]
        remaining_cash = available_cash - total_alloc - opex_amount - self.reserve_floor

        breakdown = [
            {"label": "Operating Expense & Payroll (Due Today)", "amount": opex_amount},
            {"label": f"{top_inv['supplierName']} (Pay Now)", "amount": top_inv["amount"]},
            {"label": f"{inv_2['supplierName']} (Pay Now)", "amount": inv_2["amount"]},
            {"label": "Retain Deployable Buffer", "amount": max(0.0, remaining_cash)}
        ]

        title = f"Reserve ₹16.5L for Opex & Payroll + Pay ₹2.09L for Invoices INV_FUT_0260 & 0261 today"

        reasoning = (
            f"Operating Expense & Payroll (₹16.50L) is due today and prioritized as CRITICAL from future_daily_consolidated.csv. "
            f"Executing payments for open future invoices INV_FUT_0260 (₹68.9k) & INV_FUT_0261 (₹1.41L) today "
            f"preserves Tier-1 supplier delivery SLAs before Customer {cust_name} inflows ₹31.76k on Sep 28 ({cust_prob}% Bayesian probability), maintaining ₹9.70L reserve floor."
        )

        return {
            "title": title,
            "confidence": 96,
            "breakdown": breakdown,
            "reasoning": reasoning
        }

    def generate_candidates(
        self, 
        available_cash: float, 
        top_invoice: Dict[str, Any] = None,
        receivables: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        inv_amount = top_invoice["amount"] if top_invoice else 68902.88
        disc_pct = top_invoice.get("discountPct", 0.0) if top_invoice else 0.0
        disc_savings = (inv_amount * disc_pct / 100.0) if disc_pct > 0 else 0

        cust_prob = receivables[0]["collectionProbability"] if receivables else 87.0
        cash_lakhs = available_cash / 100000.0

        candidates = [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now + Reserve Opex (Selected)",
                "score": 96,
                "subScores": { "liquidity": 98, "financial": 95, "supplier": 92, "risk": 96 },
                "costBenefit": f"Covers ₹16.5L Opex & clears INV_FUT_0260 (₹68.9k)",
                "riskNote": f"Customer CUST011 inflow (₹31.7k) on Sep 28 ({cust_prob}% Bayesian prob) guarantees floor safety",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Aug 28", "cash": cash_lakhs},
                    {"day": "Aug 29", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 01", "cash": cash_lakhs - 17.2},
                    {"day": "Sep 05", "cash": cash_lakhs - 17.5},
                    {"day": "Sep 15", "cash": cash_lakhs - 17.2},
                    {"day": "Sep 28", "cash": cash_lakhs + 0.3},
                    {"day": "Oct 08", "cash": cash_lakhs + 1.2},
                    {"day": "Oct 18", "cash": cash_lakhs + 2.5}
                ]
            },
            {
                "id": "OPT-2",
                "action": "Pay at Maturity",
                "title": "Pay at Maturity",
                "score": 61,
                "subScores": { "liquidity": 65, "financial": 42, "supplier": 78, "risk": 62 },
                "costBenefit": "Holds cash for Opex; defers payment to due date",
                "riskNote": "Covers Opex today; zero early settlement return",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": cash_lakhs},
                    {"day": "Aug 29", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 01", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 05", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 15", "cash": cash_lakhs - 17.2},
                    {"day": "Sep 28", "cash": cash_lakhs + 0.3},
                    {"day": "Oct 08", "cash": cash_lakhs + 1.2},
                    {"day": "Oct 18", "cash": cash_lakhs + 2.0}
                ]
            },
            {
                "id": "OPT-3",
                "action": "Finance",
                "title": "Bank Credit Line",
                "score": 74,
                "subScores": { "liquidity": 90, "financial": 65, "supplier": 85, "risk": 58 },
                "costBenefit": "Costs ₹1,250 interest (8.5% APR)",
                "riskNote": "Frees cash for Opex & buffers Customer CUST011 delay risk",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": cash_lakhs},
                    {"day": "Aug 29", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 01", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 05", "cash": cash_lakhs - 16.6},
                    {"day": "Sep 15", "cash": cash_lakhs - 16.3},
                    {"day": "Sep 28", "cash": cash_lakhs + 0.5},
                    {"day": "Oct 08", "cash": cash_lakhs + 1.5},
                    {"day": "Oct 18", "cash": cash_lakhs + 2.8}
                ]
            },
            {
                "id": "OPT-4",
                "action": "Delay",
                "title": "Delay Payment (+10d)",
                "score": 32,
                "subScores": { "liquidity": 40, "financial": 25, "supplier": 30, "risk": 28 },
                "costBenefit": "₹0 supplier outflow today",
                "riskNote": "If CUST011 delay exceeds >7d, breaches ₹9.7L floor on Oct 08",
                "breachesFloor": True,
                "breachDay": "Oct 08",
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": cash_lakhs},
                    {"day": "Aug 29", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 01", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 05", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 15", "cash": cash_lakhs - 17.2},
                    {"day": "Sep 28", "cash": 9.2},
                    {"day": "Oct 08", "cash": 8.8},
                    {"day": "Oct 18", "cash": 12.0}
                ]
            },
            {
                "id": "OPT-5",
                "action": "Retain",
                "title": "Retain Cash Buffer",
                "score": 45,
                "subScores": { "liquidity": 85, "financial": 20, "supplier": 35, "risk": 40 },
                "costBenefit": "Maximizes nominal liquidity buffer",
                "riskNote": "Risks supplier delivery hold on Bosch Ltd (INV_FUT_0260)",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": cash_lakhs},
                    {"day": "Aug 29", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 01", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 05", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 15", "cash": cash_lakhs - 16.5},
                    {"day": "Sep 28", "cash": cash_lakhs + 0.3},
                    {"day": "Oct 08", "cash": cash_lakhs + 1.2},
                    {"day": "Oct 18", "cash": cash_lakhs + 2.5}
                ]
            }
        ]
        return candidates
