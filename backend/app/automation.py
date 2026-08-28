from typing import List, Dict, Any
from app.models import AutomationRule, Invoice, InvoiceStatus, InvoiceType
from app.data_store import store

def evaluate_and_run_rules() -> List[Dict[str, Any]]:
    """
    Evaluates enabled autonomous rules against current cash balance and invoices.
    Executes automated actions if rule conditions are satisfied.
    """
    results = []
    total_cash = store.get_total_cash()
    
    for rule in store.rules:
        if not rule.enabled:
            continue

        triggered = False
        action_msg = ""

        if rule.rule_type == "Runway Shield":
            # If cash < threshold, auto-defer low priority marketing invoices
            if total_cash < 100000.0:  # Threshold triggered
                for inv in store.invoices:
                    if inv.type == InvoiceType.AP and inv.priority == "Low" and inv.status == InvoiceStatus.PENDING:
                        inv.status = InvoiceStatus.DEFERRED
                        inv.action_reason = f"Auto-deferred by Autonomous Rule: {rule.name}"
                        triggered = True
                action_msg = "Shield activated: Low priority marketing payouts auto-deferred."

        elif rule.rule_type == "Early Payment Discount":
            # If discount >= 2.5%, auto-mark for payment
            for inv in store.invoices:
                if inv.type == InvoiceType.AP and inv.discount_percent >= rule.threshold_value and inv.status == InvoiceStatus.PENDING:
                    inv.recommended_action = "Pay Today (Auto-Rule)"
                    inv.action_reason = f"Auto-selected by Rule: {rule.name} to capture {inv.discount_percent}% discount."
                    triggered = True
            action_msg = f"Auto-captured early payment discount opportunities >= {rule.threshold_value}%."

        elif rule.rule_type == "Emergency Stop":
            # Penalty rate prevention
            for inv in store.invoices:
                if inv.due_days <= 0 and inv.penalty_rate_monthly >= rule.threshold_value and inv.status == InvoiceStatus.PENDING:
                    inv.priority = "High"
                    inv.recommended_action = "Pay Immediately (Emergency Rule)"
                    triggered = True
            action_msg = "Emergency Rule triggered: Overdue high-penalty debt auto-prioritized."

        if triggered:
            rule.trigger_count += 1
            rule.last_triggered = "Today (Just now)"
            results.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "status": "Triggered",
                "message": action_msg
            })

    return results
