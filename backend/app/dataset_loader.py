import os
import json
import pandas as pd
from typing import List, Dict, Any
from app.models import (
    Company, CashAccount, Supplier, Customer, Invoice, Receivable, Obligation,
    FinancingOption, SupplierArchetype, EntityArchetype, ActionType
)

BASE_HISTORICAL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "historical_data_cashpilot", "data", "historical")
BASE_FUTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data")

def load_tata_suppliers() -> List[Supplier]:
    suppliers_csv = os.path.join(BASE_HISTORICAL_DIR, "suppliers.csv")
    if not os.path.exists(suppliers_csv):
        return []

    df = pd.read_csv(suppliers_csv)
    suppliers = []
    for _, row in df.iterrows():
        importance = float(row.get("strategic_importance_score", 0.8))
        archetype = SupplierArchetype.CRITICAL if importance >= 0.85 else SupplierArchetype.STANDARD
        suppliers.append(
            Supplier(
                id=str(row["supplier_id"]),
                company_id="COMP001",
                name=str(row["name"]),
                strategic_importance=importance,
                liquidity_risk=str(row.get("liquidity_risk", "Low")),
                payment_terms=f"Net-{row.get('payment_terms_days', 30)}",
                archetype=archetype
            )
        )
    return suppliers

def load_tata_customers() -> List[Customer]:
    customers_csv = os.path.join(BASE_HISTORICAL_DIR, "customers.csv")
    if not os.path.exists(customers_csv):
        return []

    df = pd.read_csv(customers_csv)
    customers = []
    for _, row in df.iterrows():
        tier = str(row.get("payment_history_tier", "average")).lower()
        archetype = (
            EntityArchetype.RELIABLE if "reliable" in tier else
            EntityArchetype.RISKY if "risky" in tier else
            EntityArchetype.AVERAGE
        )
        on_time_prob = float(row.get("on_time_probability", 0.75))
        total_p = int(row.get("total_historical_payments", 20))
        on_time_c = int(row.get("on_time_payments", int(total_p * on_time_prob)))
        late_c = max(1, total_p - on_time_c)

        customers.append(
            Customer(
                id=str(row["customer_id"]),
                name=str(row["customer_name"]),
                archetype=archetype,
                alpha=on_time_c + 1,
                beta=late_c + 1,
                on_time_probability=on_time_prob,
                average_delay_days=float(row.get("average_delay_days", 15.0))
            )
        )
    return customers

def load_tata_open_invoices(suppliers: List[Supplier]) -> List[Invoice]:
    invoices_csv = os.path.join(BASE_HISTORICAL_DIR, "invoices.csv")
    if not os.path.exists(invoices_csv):
        return []

    supplier_map = {s.id: s.name for s in suppliers}
    df = pd.read_csv(invoices_csv)
    pending_df = df[df["status"].astype(str).str.upper() == "PENDING"].head(10)

    invoices = []
    for idx, row in pending_df.iterrows():
        amt_raw = float(row["amount"])
        amt_lakhs = round(amt_raw / 100000.0, 3)
        supp_id = str(row["supplier_id"])
        supp_name = supplier_map.get(supp_id, f"Tata Tier-1 Supplier ({supp_id})")
        disc_pct = float(row.get("discount_percentage", 0.0))

        action = ActionType.PAY_NOW if (disc_pct > 0 or idx == 0) else ActionType.PAY_AT_MATURITY
        reason = f"Tata Motors Tier-1 OEM Invoice ({supp_name}). Priority score evaluated under 0/1 Knapsack DP."

        invoices.append(
            Invoice(
                id=str(row["invoice_id"]),
                supplier_id=supp_id,
                supplier_name=supp_name,
                amount=amt_lakhs,
                issue_date=str(row.get("issue_date", "2026-08-28")),
                due_date=str(row.get("issue_date", "2026-08-28")),
                due_days=idx,
                discount_percentage=disc_pct,
                discount_deadline_days=2 if disc_pct > 0 else 0,
                late_penalty_percentage=float(row.get("late_penalty_percentage", 2.0)),
                priority_score=round(85.0 + (10.0 if disc_pct > 0 else 0.0) - idx * 2.0, 1),
                recommended_action=action,
                action_reason=reason
            )
        )
    return invoices

def load_tata_receivables(customers: List[Customer]) -> List[Receivable]:
    receivables_csv = os.path.join(BASE_HISTORICAL_DIR, "receivables.csv")
    if not os.path.exists(receivables_csv):
        return []

    cust_map = {c.id: c for c in customers}
    df = pd.read_csv(receivables_csv)
    pending_df = df[df["status"].astype(str).str.upper() == "PENDING"].head(10)

    receivables = []
    for idx, row in pending_df.iterrows():
        amt_raw = float(row["amount"])
        amt_lakhs = round(amt_raw / 100000.0, 3)
        cust_id = str(row["customer_id"])
        cust_obj = cust_map.get(cust_id)
        cust_name = cust_obj.name if cust_obj else f"Tata Motors Dealer ({cust_id})"
        prob = cust_obj.on_time_probability if cust_obj else float(row.get("collection_probability", 0.85))
        delay = cust_obj.average_delay_days if cust_obj else int(row.get("expected_delay_days", 14))

        receivables.append(
            Receivable(
                id=str(row["receivable_id"]),
                customer_id=cust_id,
                customer_name=cust_name,
                amount=amt_lakhs,
                expected_date=str(row.get("expected_date", "2026-09-28")),
                due_days=30 + idx * 5,
                collection_probability=prob,
                expected_delay_days=int(delay),
                probability_history=[round(prob - 0.04, 2), round(prob - 0.02, 2), round(prob, 2)]
            )
        )
    return receivables
