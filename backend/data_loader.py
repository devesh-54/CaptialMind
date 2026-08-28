import os
import json
from typing import Dict, Any, List
from build_unified_dataset import build_unified_dataset, OUTPUT_JSON_PATH

class DataLoader:
    def __init__(self):
        if not os.path.exists(OUTPUT_JSON_PATH):
            self.dataset = build_unified_dataset()
        else:
            try:
                with open(OUTPUT_JSON_PATH, "r", encoding="utf-8") as f:
                    self.dataset = json.load(f)
            except Exception:
                self.dataset = build_unified_dataset()

    def load_company(self) -> Dict[str, Any]:
        return self.dataset.get("company", {
            "company_id": "TATA001",
            "name": "Tata Consumer Products",
            "currency": "INR",
            "minimum_cash_reserve": 970000.0,
            "operating_reserve_floor": 1500000.0
        })

    def load_cash(self) -> float:
        accounts = self.dataset.get("cash_accounts", [])
        if accounts:
            return float(accounts[0].get("current_balance", 2554079.97))
        return 2554079.97

    def load_customers(self) -> List[Dict[str, Any]]:
        return self.dataset.get("customers", [])

    def load_suppliers(self) -> List[Dict[str, Any]]:
        suppliers_raw = self.dataset.get("suppliers", [])
        suppliers = []
        for s in suppliers_raw:
            suppliers.append({
                "id": s.get("supplier_id"),
                "name": s.get("name"),
                "category": s.get("category"),
                "strategicImportance": s.get("strategic_importance_rating", 4),
                "isCritical": s.get("is_critical", True),
                "liquidityRisk": s.get("liquidity_risk", "LOW"),
                "outstandingInvoices": 2,
                "outstandingAmount": 140555.66,
                "onTimePaymentPct": 94.0,
                "capturedDiscountTotal": s.get("captured_discount_total", 142000.0)
            })
        return suppliers

    def load_invoices(self) -> List[Dict[str, Any]]:
        invoices_raw = self.dataset.get("invoices", [])
        suppliers_dict = {s["supplier_id"]: s for s in self.dataset.get("suppliers", [])}
        
        invoices = []
        # Filter open future invoices first
        future_invs = [inv for inv in invoices_raw if inv.get("data_stream_type") == "FUTURE_STREAMING"]
        if not future_invs:
            future_invs = invoices_raw

        for inv in future_invs[:10]:
            sup_id = inv.get("supplier_id")
            sup_info = suppliers_dict.get(sup_id, {"name": f"Supplier ({sup_id})", "category": "Components", "strategic_importance_rating": 4})
            amt = float(inv.get("amount", 68902.88))
            disc_pct = float(inv.get("discount_percentage", 0.0))
            
            invoices.append({
                "id": inv.get("invoice_id"),
                "supplierId": sup_id,
                "supplierName": sup_info.get("name", "Bosch Ltd"),
                "supplierCategory": sup_info.get("category", "Components"),
                "amount": amt,
                "dueDate": inv.get("due_date", "2026-08-28"),
                "discountPct": disc_pct,
                "discountDeadline": inv.get("discount_deadline", "-"),
                "priorityScore": inv.get("ai_priority_score", 95 if disc_pct > 0 else 82),
                "aiAction": inv.get("recommended_action", "Pay Now"),
                "strategicImportance": sup_info.get("strategic_importance_rating", 4),
                "reasoning": f"Relational link to Supplier {sup_info.get('name')} ({sup_id}). Terms and discount captured."
            })
        return invoices

    def load_receivables(self) -> List[Dict[str, Any]]:
        receivables_raw = self.dataset.get("receivables", [])
        customers_dict = {c["customer_id"]: c for c in self.dataset.get("customers", [])}

        receivables = []
        future_recs = [rec for rec in receivables_raw if rec.get("data_stream_type") == "FUTURE_STREAMING"]
        if not future_recs:
            future_recs = receivables_raw

        for rec in future_recs[:8]:
            cust_id = rec.get("customer_id")
            cust_info = customers_dict.get(cust_id, {"name": f"Customer ({cust_id})", "alpha_prior": 10, "beta_prior": 2, "observations_count": 12, "on_time_probability": 87.0})
            
            receivables.append({
                "id": rec.get("receivable_id"),
                "customerId": cust_id,
                "customerName": cust_info.get("name", f"Customer ({cust_id})"),
                "amount": float(rec.get("amount", 31760.96)),
                "expectedDate": rec.get("expected_date", "2026-09-28"),
                "collectionProbability": float(rec.get("collection_probability", 87.0)),
                "expectedDelayDays": int(rec.get("expected_delay_days", 1)),
                "alpha": cust_info.get("alpha_prior", 10),
                "beta": cust_info.get("beta_prior", 2),
                "observationsCount": cust_info.get("observations_count", 12),
                "status": rec.get("status", "On Time")
            })
        return receivables

    def load_obligations(self) -> List[Dict[str, Any]]:
        obligations_raw = self.dataset.get("obligations", [])
        obligations = []
        for ob in obligations_raw:
            obligations.append({
                "id": ob.get("obligation_id"),
                "supplierId": ob.get("supplier_id"),
                "supplierName": ob.get("description"),
                "amount": float(ob.get("amount", 100000.0)),
                "dueDate": ob.get("due_date"),
                "priority": ob.get("priority", "HIGH"),
                "aiAction": ob.get("ai_action", "Must Pay")
            })
        return obligations

    def load_future_daily_sequence(self) -> List[Dict[str, Any]]:
        return self.dataset.get("future_daily_sequence", [])

    def load_decisions(self) -> List[Dict[str, Any]]:
        decisions_raw = self.dataset.get("decisions", [])
        decisions = []
        for d in decisions_raw:
            decisions.append({
                "id": d.get("decision_id"),
                "timestamp": d.get("timestamp"),
                "triggerEvent": d.get("trigger_event"),
                "decision": d.get("title"),
                "amount": float(d.get("allocated_amount", 68902.88)),
                "confidence": d.get("confidence_score", 96),
                "status": d.get("status", "ACTIVE"),
                "version": d.get("version", "v2.0"),
                "validUntil": d.get("valid_until"),
                "reasons": d.get("reasons", [])
            })
        return decisions
