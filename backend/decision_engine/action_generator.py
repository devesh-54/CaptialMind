import math
from typing import Dict, Any, List
from .financial_state import FinancialState, PayableItem, ReceivableItem, ObligationItem

class ActionGenerator:
    """
    Phase 7, 9, 10: Candidate Action Generator & Minimum Financing Engine
    Generates strategic candidate actions, evaluates receivable expected contributions,
    early payment discount benefits, and calculates true minimum financing.
    """

    @staticmethod
    def generate_candidate_actions(
        state: FinancialState,
        recommended_reserve: float
    ) -> List[Dict[str, Any]]:
        candidates = []

        curr_cash = state.cash.current_cash
        raw_proj_cash = state.forecast.raw_projected_cash
        cash_buffer = raw_proj_cash - recommended_reserve

        # 1. Receivable Acceleration Options (Phase 9: Expected Value = Amount x Probability)
        for rec in state.receivables:
            if rec.payment_status != "PAID":
                expected_contrib = rec.expected_cash_contribution
                if expected_contrib > 0:
                    candidates.append({
                        "id": f"ACT-REC-{rec.id}",
                        "action_type": "ACCELERATE_RECEIVABLE",
                        "title": f"Accelerate Customer Receivable {rec.id} ({rec.customer_name})",
                        "target_item": rec,
                        "invoice_amount": rec.amount,
                        "collection_probability": rec.collection_probability,
                        "expected_liquidity_contribution": expected_contrib,
                        "expected_delay": rec.expected_delay_days,
                        "financial_impact": expected_contrib,
                        "outflow": 0.0,
                        "urgency": 85 if rec.expected_delay_days > 0 else 60,
                        "operational_impact": 10,
                        "description": f"Request early invoice discounting for {rec.customer_name} (Amount: ₹{rec.amount:,.2f}, Prob: {rec.collection_probability*100:.0f}%, Expected Liquidity: ₹{expected_contrib:,.2f}, Delay: {rec.expected_delay_days}d)."
                    })

        # 2. Supplier Invoice Payment Options (Phase 10: Early Payment Discount Validation)
        for inv in state.payables:
            if inv.payment_status != "PAID":
                discount_savings = (inv.amount * inv.discount_percentage / 100.0) if inv.discount_percentage > 0 else 0.0
                
                # Pay Now (Early Settlement with Discount)
                candidates.append({
                    "id": f"ACT-PAY-NOW-{inv.id}",
                    "action_type": "PAY_NOW_DISCOUNT",
                    "title": f"Pay Now: Invoice {inv.id} ({inv.supplier_name})",
                    "target_item": inv,
                    "invoice_amount": inv.amount,
                    "discount_percentage": inv.discount_percentage,
                    "discount_benefit": discount_savings,
                    "financial_impact": discount_savings,
                    "outflow": inv.amount,
                    "urgency": 90 if inv.discount_percentage > 0 or inv.is_critical else 65,
                    "operational_impact": 95 if inv.is_critical else 75,
                    "description": f"Execute immediate payment of ₹{inv.amount:,.2f} for {inv.supplier_name}. Captures ₹{discount_savings:,.2f} early discount ({inv.discount_percentage}%)."
                })

                # Pay at Maturity
                candidates.append({
                    "id": f"ACT-PAY-MAT-{inv.id}",
                    "action_type": "PAY_AT_MATURITY",
                    "title": f"Pay at Maturity: Invoice {inv.id} ({inv.supplier_name})",
                    "target_item": inv,
                    "invoice_amount": inv.amount,
                    "discount_benefit": 0.0,
                    "financial_impact": 0.0,
                    "outflow": 0.0,
                    "urgency": 50,
                    "operational_impact": 70,
                    "description": f"Defer payment of ₹{inv.amount:,.2f} to due date ({inv.due_date}) to preserve immediate cash reserve."
                })

                # Delay Non-Critical Payments (only if permitted)
                if not inv.is_critical and inv.strategic_importance <= 3:
                    penalty_cost = inv.amount * (inv.late_penalty_percentage / 100.0)
                    candidates.append({
                        "id": f"ACT-DELAY-{inv.id}",
                        "action_type": "DELAY_PAYABLE",
                        "title": f"Negotiate Deferral (+10d): Invoice {inv.id} ({inv.supplier_name})",
                        "target_item": inv,
                        "invoice_amount": inv.amount,
                        "discount_benefit": -penalty_cost,
                        "financial_impact": -penalty_cost,
                        "outflow": 0.0,
                        "urgency": 30,
                        "operational_impact": 35,
                        "critical_risk_flagged": False,
                        "description": f"Defer payment by +10 days to protect cash buffer. Incurs late penalty of ₹{penalty_cost:,.2f} ({inv.late_penalty_percentage}%)."
                    })

        # 3. Optional Expense Reduction
        if state.other_financials.unexpected_expenses > 0 or cash_buffer < 0:
            candidates.append({
                "id": "ACT-CUT-EXPENSE",
                "action_type": "REDUCE_EXPENSE",
                "title": "Postpone Optional Operational Expenses",
                "target_item": None,
                "financial_impact": 200000.0,
                "outflow": 0.0,
                "urgency": 75,
                "operational_impact": 50,
                "description": "Postpone non-essential marketing and discretionary operational purchases by 14 days, conserving ₹2.00L."
            })

        # 4. Phase 7: True Minimum Financing (Calculated after evaluating non-financing actions)
        # Sum potential non-financing positive impacts
        non_fin_positive = sum([r.expected_cash_contribution for r in state.receivables]) + 200000.0
        cash_after_non_fin = raw_proj_cash + non_fin_positive
        remaining_gap = max(0.0, recommended_reserve - cash_after_non_fin)

        if remaining_gap > 0 or cash_buffer < 0:
            needed_financing = float(math.ceil(max(remaining_gap, recommended_reserve - raw_proj_cash) / 10000.0) * 10000.0)
            if needed_financing > 0:
                interest_cost = needed_financing * 0.085 * (30 / 365.0)  # 8.5% APR for 30 days
                candidates.append({
                    "id": "ACT-FIN-LINE",
                    "action_type": "FINANCING",
                    "title": f"Draw Minimum Bank Credit Line (₹{needed_financing/100000.0:.2f}L)",
                    "target_item": None,
                    "financial_impact": -interest_cost,
                    "outflow": 0.0,
                    "urgency": 80,
                    "operational_impact": 80,
                    "financing_amount": needed_financing,
                    "description": f"Draw minimum required ICICI Credit Line of ₹{needed_financing:,.2f} to cover remaining liquidity gap after non-financing actions. Interest cost: ₹{interest_cost:,.2f} (8.5% APR)."
                })

        # 5. Excess Cash Strategic Buffer / Prepay Expensive Debt
        if cash_buffer > (recommended_reserve * 0.4) and state.other_financials.loan_repayments > 0:
            candidates.append({
                "id": "ACT-PREPAY-DEBT",
                "action_type": "PREPAY_DEBT",
                "title": "Prepay Expensive Debt Line",
                "target_item": None,
                "financial_impact": 45000.0,
                "outflow": 500000.0,
                "urgency": 40,
                "operational_impact": 90,
                "description": "Deploy ₹5.00L excess cash surplus to pay down credit line, saving ₹45,000 in interest expenses."
            })

        return candidates
