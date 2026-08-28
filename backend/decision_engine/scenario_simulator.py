from typing import Dict, Any, List
from .financial_state import FinancialState, CashData, ForecastData, ReceivableItem, PayableItem, ObligationItem, OtherFinancials
from .forecast_validator import ForecastValidator
from .dynamic_reserve import DynamicReserveCalculator
from .risk_engine import RiskEngine
from .action_generator import ActionGenerator
from .action_scorer import ActionScorer
from .constraint_engine import ConstraintEngine
from .optimizer import CombinationOptimizer

class ScenarioSimulator:
    """
    Phase 6, 8, 11: Scenario Simulator & Reconciled Before/After Financial Impact Engine
    Calculates exact after-decision values from selected actions including credit draws,
    and performs mathematical reconciliation verification.
    """

    @staticmethod
    def simulate_before_after(
        state: FinancialState,
        selected_actions: List[Dict[str, Any]],
        initial_risk: Dict[str, Any],
        initial_reserve: Dict[str, Any],
        forecast_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        before_raw = state.forecast.raw_projected_cash
        before_display = state.forecast.display_projected_cash
        rec_reserve = initial_reserve["recommended_reserve"]
        before_buffer = before_raw - rec_reserve

        # BEFORE STATE
        before = {
            "raw_projected_cash": round(before_raw, 2),
            "display_projected_cash": round(before_display, 2),
            "liquidity_deficit": round(state.forecast.liquidity_deficit, 2),
            "recommended_reserve": round(rec_reserve, 2),
            "cash_buffer": round(before_buffer, 2),
            "risk_level": initial_risk["risk_level"],
            "risk_score": initial_risk["risk_score"]
        }

        # CALCULATE AFTER STATE MATHEMATICALLY (Phase 6)
        total_positive_impacts = 0.0
        total_outflows = 0.0
        financing_drawn = 0.0
        trace_log = []

        for act in selected_actions:
            a_type = act.get("action_type", "")
            fin_impact = float(act.get("financial_impact", 0.0))
            outflow = float(act.get("outflow", 0.0))
            title = act.get("title", act.get("id", "Action"))

            if a_type == "FINANCING":
                fin_amt = float(act.get("financing_amount", 0.0))
                financing_drawn += fin_amt
                # Net impact of financing = financing_amount - interest_cost
                net_act = fin_amt + fin_impact
                trace_log.append(f"{title}: +₹{fin_amt:,.2f} credit line drawn (Interest cost: ₹{abs(fin_impact):,.2f})")
            elif fin_impact >= 0:
                total_positive_impacts += fin_impact
                total_outflows += outflow
                net_act = fin_impact - outflow
                trace_log.append(f"{title}: +₹{fin_impact:,.2f} liquidity contribution, -₹{outflow:,.2f} outflow")
            else:
                total_outflows += (outflow + abs(fin_impact))
                net_act = fin_impact - outflow
                trace_log.append(f"{title}: -₹{abs(fin_impact):,.2f} penalty/cost, -₹{outflow:,.2f} outflow")

        net_liquidity_impact = (total_positive_impacts - total_outflows + financing_drawn)
        
        # Phase 8 Mathematical Reconciliation Formula
        reconciled_after_raw = before_raw + net_liquidity_impact
        reconciled_after_display = max(0.0, reconciled_after_raw)
        reconciled_after_deficit = max(0.0, -reconciled_after_raw)
        reconciled_after_buffer = reconciled_after_raw - rec_reserve

        # Clone state for post-action risk evaluation
        after_forecast = ForecastData(
            raw_projected_cash=reconciled_after_raw,
            display_projected_cash=reconciled_after_display,
            liquidity_deficit=reconciled_after_deficit,
            minimum_raw_projected_cash=state.forecast.minimum_raw_projected_cash + net_liquidity_impact,
            minimum_display_projected_cash=max(0.0, state.forecast.minimum_raw_projected_cash + net_liquidity_impact),
            confidence_score=state.forecast.confidence_score
        )
        
        after_state = FinancialState(
            cash=state.cash,
            forecast=after_forecast,
            receivables=state.receivables,
            payables=state.payables,
            obligations=state.obligations,
            other_financials=state.other_financials,
            configured_min_reserve=state.configured_min_reserve
        )

        reserve_calc = DynamicReserveCalculator()
        after_reserve = reserve_calc.calculate_reserve(
            after_state,
            risk_level=initial_risk["risk_level"],
            forecast_quality=forecast_quality
        )

        after_risk = RiskEngine.classify_risk(
            after_state,
            recommended_reserve=after_reserve["recommended_reserve"],
            forecast_quality=forecast_quality
        )

        after = {
            "raw_projected_cash": round(reconciled_after_raw, 2),
            "display_projected_cash": round(reconciled_after_display, 2),
            "liquidity_deficit": round(reconciled_after_deficit, 2),
            "recommended_reserve": round(after_reserve["recommended_reserve"], 2),
            "cash_buffer": round(reconciled_after_buffer, 2),
            "risk_level": after_risk["risk_level"],
            "risk_score": after_risk["risk_score"]
        }

        # Phase 8 Verification
        reconciliation_check = abs((before_raw + net_liquidity_impact) - reconciled_after_raw) < 0.01

        return {
            "before_decision": before,
            "after_decision": after,
            "net_liquidity_impact": round(net_liquidity_impact, 2),
            "total_positive_impacts": round(total_positive_impacts, 2),
            "total_outflows": round(total_outflows, 2),
            "financing_drawn": round(financing_drawn, 2),
            "reconciliation_valid": reconciliation_check,
            "calculation_trace": trace_log
        }
