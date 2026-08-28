import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple

class DecisionEngine:
    def __init__(self, reserve_floor: float = 1500000.0):
        self.reserve_floor = reserve_floor

    def forecast_30d_cash(
        self,
        current_cash: float,
        receivable_delay_days: int = 0,
        extra_outflow: float = 0.0
    ) -> List[Dict[str, Any]]:
        days = ['Aug 28', 'Aug 30', 'Sep 02', 'Sep 05', 'Sep 08', 'Sep 12', 'Sep 18', 'Sep 25']
        baseline_cash_lakhs = [48.2, 38.8, 42.1, 36.5, 29.4, 34.0, 41.5, 52.0]
        
        forecast = []
        for idx, day in enumerate(days):
            cash = baseline_cash_lakhs[idx] - (extra_outflow / 100000.0)
            if idx >= 3 and receivable_delay_days > 0:
                cash -= (receivable_delay_days * 0.45)
            
            pessimistic = max(10.0, cash - 5.5)
            forecast.append({
                "day": day,
                "cash": round(max(8.0, cash), 1),
                "pessimistic": round(pessimistic, 1)
            })
        return forecast

    def generate_candidates(self, available_cash: float) -> List[Dict[str, Any]]:
        candidates = [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now (Selected)",
                "score": 96,
                "costBenefit": "Captures ₹33,440 net early discounts",
                "riskNote": "Stays safely above ₹15.0L floor throughout",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 48.2},
                    {"day": "Aug 30", "cash": 38.8},
                    {"day": "Sep 02", "cash": 42.1},
                    {"day": "Sep 05", "cash": 36.5},
                    {"day": "Sep 08", "cash": 29.4},
                    {"day": "Sep 12", "cash": 34.0},
                    {"day": "Sep 18", "cash": 41.5},
                    {"day": "Sep 25", "cash": 52.0}
                ]
            },
            {
                "id": "OPT-2",
                "action": "Pay at Maturity",
                "title": "Pay at Maturity",
                "score": 61,
                "costBenefit": "Costs ₹33,440 in forfeited discount yield",
                "riskNote": "Stays above floor; zero early settlement return",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 48.2},
                    {"day": "Aug 30", "cash": 48.2},
                    {"day": "Sep 02", "cash": 48.2},
                    {"day": "Sep 05", "cash": 29.8},
                    {"day": "Sep 08", "cash": 27.2},
                    {"day": "Sep 12", "cash": 31.5},
                    {"day": "Sep 18", "cash": 39.0},
                    {"day": "Sep 25", "cash": 48.5}
                ]
            },
            {
                "id": "OPT-3",
                "action": "Finance",
                "title": "Bank Credit Line",
                "score": 74,
                "costBenefit": "Costs ₹18,000 interest (8.5% APR)",
                "riskNote": "Preserves cash today; net yield reduced by interest",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 48.2},
                    {"day": "Aug 30", "cash": 48.2},
                    {"day": "Sep 02", "cash": 45.0},
                    {"day": "Sep 05", "cash": 40.5},
                    {"day": "Sep 08", "cash": 35.0},
                    {"day": "Sep 12", "cash": 38.2},
                    {"day": "Sep 18", "cash": 44.0},
                    {"day": "Sep 25", "cash": 52.0}
                ]
            },
            {
                "id": "OPT-4",
                "action": "Delay",
                "title": "Delay Payment (+10d)",
                "score": 32,
                "costBenefit": "₹0 immediate cash outflow",
                "riskNote": "Breaches reserve floor (₹12.5L) on Day 18",
                "breachesFloor": True,
                "breachDay": "Sep 18",
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 48.2},
                    {"day": "Aug 30", "cash": 48.2},
                    {"day": "Sep 02", "cash": 45.0},
                    {"day": "Sep 05", "cash": 22.0},
                    {"day": "Sep 08", "cash": 18.0},
                    {"day": "Sep 12", "cash": 16.5},
                    {"day": "Sep 18", "cash": 12.5},
                    {"day": "Sep 25", "cash": 29.0}
                ]
            },
            {
                "id": "OPT-5",
                "action": "Retain",
                "title": "Retain Cash Buffer",
                "score": 45,
                "costBenefit": "Maximizes nominal cash reserve",
                "riskNote": "Forfeits ₹33.4k & risks supplier delivery hold",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 48.2},
                    {"day": "Aug 30", "cash": 48.2},
                    {"day": "Sep 02", "cash": 48.2},
                    {"day": "Sep 05", "cash": 48.2},
                    {"day": "Sep 08", "cash": 42.0},
                    {"day": "Sep 12", "cash": 40.0},
                    {"day": "Sep 18", "cash": 45.0},
                    {"day": "Sep 25", "cash": 52.0}
                ]
            }
        ]
        return candidates

    def calculate_tradeoff_explanation(self, selected: Dict[str, Any], runner_up: Dict[str, Any]) -> str:
        return (
            f"Pay Now scores highest ({selected['score']}/100) because it captures {selected['costBenefit']} "
            f"while keeping the 30-day reserve floor breach risk at zero; {runner_up['title']} ({runner_up['score']}/100) "
            f"incurs higher costs for no net liquidity benefit."
        )
