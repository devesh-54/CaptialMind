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
        
        # 1. Receivable delay > 3 days
        if delay_days >= 3:
            return True, f"Material Receivable Delay: Expected payment delayed by +{delay_days} days."

        # 2. Cash balance / outflow change > 2% of deployable capital (> ₹5.0L)
        if outflow_lakhs >= 5.0:
            return True, f"Material Cash Outflow: Significant capital shift of ₹{outflow_lakhs:.1f}L."

        # 3. Collection probability shift > 15% (e.g. 85% -> 55%)
        if abs(prob_delta) >= 15.0:
            return True, f"Material Bayesian Probability Shift: Customer collection confidence shifted by {prob_delta:.1f}%."

        # 4. Supplier risk shift (e.g. LOW -> HIGH)
        if risk_shift:
            return True, "Material Supplier Risk Shift: Tier-1 supplier liquidity risk escalated."

        # 5. Financing APR rate shift > 1.5%
        if abs(rate_shift_pct) >= 1.5:
            return True, f"Material Interest Rate Shift: Financing line APR changed by {rate_shift_pct:.1f}%."

        # 6. Specific explicit event overrides
        if event_type in ["RECEIVABLE_DELAYED", "REOPTIMIZE_TRIGGER"]:
            return True, f"Material Trigger Event: {event_type} invoked."

        # Non-material telemetry ping (e.g. minor cash fluctuation <2%)
        return False, "Monitored telemetry update — below materiality threshold (<2% cash delta, <3d delay). Strategy retained."


class DecisionEngine:
    def __init__(self, reserve_floor: float = 1500000.0):
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
        days = ['Jan 04', 'Jan 05 (Salary)', 'Jan 10', 'Jan 15 (Customer A)', 'Jan 20', 'Feb 05', 'Feb 12', 'Feb 20']
        base_cash_lakhs = current_cash / 100000.0
        
        cust_a_prob = 0.95
        if receivables and len(receivables) > 0:
            cust_a_prob = (receivables[0].get("collectionProbability", 95.0)) / 100.0

        forecast = []
        for idx, day in enumerate(days):
            cash = base_cash_lakhs - (extra_outflow / 100000.0) - (idx * 1.5)
            if idx == 1:
                cash -= 41.0  # Salary payroll outflow (₹4.10Cr)
            if idx == 3:
                expected_inflow = 24.5 * cust_a_prob
                if receivable_delay_days > 0:
                    expected_inflow = expected_inflow * max(0.2, 1.0 - (receivable_delay_days * 0.1))
                cash += expected_inflow
            
            pessimistic = max(15.0, cash - 8.5)
            forecast.append({
                "day": day,
                "cash": round(max(15.0, cash), 1),
                "pessimistic": round(pessimistic, 1)
            })
        return forecast

    def generate_hero_recommendation(
        self, 
        invoices: List[Dict[str, Any]], 
        available_cash: float,
        receivables: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        top_inv = invoices[0] if invoices else {"amount": 33381685.97, "supplierName": "Valeo India Pvt Ltd", "discountPct": 2.0}
        discount_savings = top_inv["amount"] * (top_inv.get("discountPct", 2.0) / 100.0)
        salary_payroll = 41005965.89

        cust_a_name = receivables[0]["customerName"] if receivables else "Mahindra Logistics"
        cust_a_prob = receivables[0]["collectionProbability"] if receivables else 95.0

        remaining_cash = available_cash - top_inv["amount"] - salary_payroll - self.reserve_floor

        breakdown = [
            {"label": "Employee Salary Payroll (Due Tomorrow)", "amount": salary_payroll},
            {"label": f"{top_inv['supplierName']} (Pay Now)", "amount": top_inv["amount"]},
            {"label": "Retain Deployable Buffer", "amount": max(0.0, remaining_cash)}
        ]

        title = f"Reserve ₹4.10Cr for Employee Salary tomorrow + Pay ₹3.34Cr to {top_inv['supplierName']} today to capture ₹{discount_savings:,.0f} discount"

        reasoning = (
            f"Employee Monthly Salary Payroll (₹4.10Cr) is due tomorrow and prioritized as CRITICAL. "
            f"Executing early payment for {top_inv['supplierName']} (₹3.34Cr) today captures ₹{discount_savings:,.0f} in net early discounts (2.0%), "
            f"before Customer A ({cust_a_name}) inflows ₹2.45Cr on Jan 15th ({cust_a_prob}% Bayesian confidence), preserving deployable cash above ₹15.0L floor."
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
        inv_amount = top_invoice["amount"] if top_invoice else 33381685.97
        disc_pct = top_invoice.get("discountPct", 2.0) if top_invoice else 2.0
        disc_savings = (inv_amount * disc_pct / 100.0) if disc_pct > 0 else 667633.71

        cust_a_prob = receivables[0]["collectionProbability"] if receivables else 95.0
        cash_lakhs = available_cash / 100000.0

        candidates = [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now + Reserve Salary (Selected)",
                "score": 96,
                "subScores": { "liquidity": 98, "financial": 95, "supplier": 92, "risk": 96 },
                "costBenefit": f"Captures ₹{disc_savings:,.0f} discount & covers ₹4.10Cr Salary tomorrow",
                "riskNote": f"Customer A inflow (₹2.45Cr) on Jan 15 ({cust_a_prob}% Bayesian prob) guarantees floor safety",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 05", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 10", "cash": cash_lakhs - 44.3},
                    {"day": "Jan 15", "cash": cash_lakhs - 19.8},
                    {"day": "Jan 20", "cash": cash_lakhs - 22.0},
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
                "subScores": { "liquidity": 65, "financial": 42, "supplier": 78, "risk": 62 },
                "costBenefit": f"Forfeits ₹{disc_savings:,.0f} discount; holds cash for Salary",
                "riskNote": "Covers Salary payroll tomorrow; zero early settlement return",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 05", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 10", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 15", "cash": cash_lakhs - 16.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 49.8},
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
                "subScores": { "liquidity": 90, "financial": 65, "supplier": 85, "risk": 58 },
                "costBenefit": "Costs ₹18,500 interest (8.5% APR)",
                "riskNote": "Frees cash for Salary Day & buffers Customer A delay risk",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 05", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 10", "cash": cash_lakhs - 41.5},
                    {"day": "Jan 15", "cash": cash_lakhs - 17.0},
                    {"day": "Jan 20", "cash": cash_lakhs - 18.2},
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
                "subScores": { "liquidity": 40, "financial": 25, "supplier": 30, "risk": 28 },
                "costBenefit": "₹0 supplier outflow today",
                "riskNote": "If Customer A is delayed >7d, breaches reserve floor on Feb 05",
                "breachesFloor": True,
                "breachDay": "Feb 05",
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 05", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 10", "cash": cash_lakhs - 41.5},
                    {"day": "Jan 15", "cash": cash_lakhs - 41.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 74.8},
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
                "subScores": { "liquidity": 85, "financial": 20, "supplier": 35, "risk": 40 },
                "costBenefit": "Maximizes nominal liquidity buffer",
                "riskNote": f"Forfeits ₹{disc_savings:,.0f} & risks Valeo India delivery hold",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Jan 04", "cash": cash_lakhs},
                    {"day": "Jan 05", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 10", "cash": cash_lakhs - 41.0},
                    {"day": "Jan 15", "cash": cash_lakhs - 16.5},
                    {"day": "Jan 20", "cash": cash_lakhs - 16.5},
                    {"day": "Feb 05", "cash": cash_lakhs - 1.0},
                    {"day": "Feb 12", "cash": cash_lakhs + 5.0},
                    {"day": "Feb 20", "cash": cash_lakhs + 12.0}
                ]
            }
        ]
        return candidates
