import os
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from app.models import (
    Company, CashAccount, Supplier, Customer, Invoice, Receivable, Obligation,
    FinancingOption, EventPayload, Decision, SupplierArchetype, EntityArchetype, ActionType
)
from app.historical_data import generate_historical_transactions, preprocess_customer_history
from app.supabase_service import sync_stream_event_to_supabase, fetch_supabase_stream_records
from app.dataset_loader import (
    load_tata_suppliers, load_tata_customers, load_tata_open_invoices, load_tata_receivables
)

HISTORICAL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "historical_data_cashpilot", "data", "historical")
FUTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data")

class DataStore:
    def __init__(self):
        self.stream_ledger: List[Dict[str, Any]] = []
        self.reset_to_defaults()

    def reset_to_defaults(self):
        self.company = Company(
            id="COMP001",
            name="Tata Motors Ltd",
            currency="INR",
            minimum_30day_reserve=50.0  # ₹50.0L reserve floor
        )

        # Cash Accounts for Tata Motors Ltd
        self.accounts: List[CashAccount] = [
            CashAccount(id="ACC001", name="HDFC Operating Treasury", account_type="Operating Cash", balance=380.0, available_balance=380.0, yield_rate=0.04),
            CashAccount(id="ACC002", name="ICICI Reserve Liquidity Buffer", account_type="Reserved Buffer", balance=100.0, available_balance=100.0, yield_rate=0.065),
            CashAccount(id="ACC003", name="SBI Working Capital Credit Line", account_type="Credit Line", balance=250.0, available_balance=250.0, yield_rate=0.085),
        ]

        # Load real suppliers from dataset
        loaded_suppliers = load_tata_suppliers()
        self.suppliers: List[Supplier] = loaded_suppliers if loaded_suppliers else [
            Supplier(id="SUP001", name="Tata Steel Ltd", strategic_importance=0.93, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP002", name="JSW Steel Ltd", strategic_importance=0.88, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP003", name="Bosch Ltd", strategic_importance=0.91, liquidity_risk="Low", payment_terms="2/10 Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP008", name="Bharat Forge Ltd", strategic_importance=0.68, liquidity_risk="Moderate", payment_terms="Net-45", archetype=SupplierArchetype.STANDARD),
        ]

        # Load real customers from dataset
        loaded_customers = load_tata_customers()
        self.customers: List[Customer] = loaded_customers if loaded_customers else [
            Customer(id="CUST001", name="Concorde Motors", archetype=EntityArchetype.RELIABLE, alpha=22, beta=4, on_time_probability=0.88, average_delay_days=15.3),
            Customer(id="CUST015", name="TCI Express Ltd", archetype=EntityArchetype.AVERAGE, alpha=15, beta=5, on_time_probability=0.78, average_delay_days=21.8),
            Customer(id="CUST016", name="VRL Logistics Ltd", archetype=EntityArchetype.AVERAGE, alpha=19, beta=9, on_time_probability=0.69, average_delay_days=23.2),
        ]

        # Load real open invoices from dataset
        loaded_invoices = load_tata_open_invoices(self.suppliers)
        self.invoices: List[Invoice] = loaded_invoices if loaded_invoices else [
            Invoice(id="INV00002", supplier_id="SUP010", supplier_name="Valeo India Pvt Ltd", amount=227.21, issue_date="2025-12-15", due_date="2026-01-04", due_days=0, discount_percentage=2.0, discount_deadline_days=2, late_penalty_percentage=0.0, priority_score=95.0, recommended_action=ActionType.PAY_NOW, action_reason="Valeo India Lighting Systems invoice. 2.0% early discount active."),
            Invoice(id="INV00024", supplier_id="SUP003", supplier_name="Bosch Ltd", amount=124.91, issue_date="2025-12-18", due_date="2025-12-25", due_days=1, discount_percentage=2.0, discount_deadline_days=0, late_penalty_percentage=2.0, priority_score=89.0, recommended_action=ActionType.PAY_NOW, action_reason="Bosch Engine Components invoice."),
        ]

        # Load real open receivables from dataset
        loaded_receivables = load_tata_receivables(self.customers)
        self.receivables: List[Receivable] = loaded_receivables if loaded_receivables else [
            Receivable(id="REC00001", customer_id="CUST016", customer_name="VRL Logistics Ltd", amount=158.40, expected_date="2026-09-28", due_days=31, collection_probability=0.69, expected_delay_days=23, probability_history=[0.65, 0.67, 0.69]),
            Receivable(id="REC00002", customer_id="CUST015", customer_name="TCI Express Ltd", amount=243.00, expected_date="2026-10-18", due_days=51, collection_probability=0.78, expected_delay_days=21, probability_history=[0.74, 0.76, 0.78]),
        ]

        # Obligations
        self.obligations: List[Obligation] = [
            Obligation(id="ob_1", description="Plant Operating Expense & Assembly Worker Payroll", amount=165.0, due_days=0, priority="CRITICAL"),
            Obligation(id="ob_2", description="Valeo India Lighting Systems Invoice INV00002", amount=227.21, due_days=0, priority="High"),
            Obligation(id="ob_3", description="Bosch Ltd Invoice INV00024", amount=124.91, due_days=1, priority="High"),
        ]

        # Financing Options
        self.financing_options: List[FinancingOption] = [
            FinancingOption(id="fin_1", provider="HDFC Treasury", type="Internal Cash Deployment", interest_rate_annual=0.0, credit_limit=380.0, available_amount=380.0, processing_fee=0.0, recommended=True),
            FinancingOption(id="fin_2", provider="ICICI Bank", type="Dynamic Bank Credit Line", interest_rate_annual=8.5, credit_limit=250.0, available_amount=250.0, processing_fee=0.1, recommended=False),
        ]

        self.events_log: List[Dict[str, Any]] = [
            {"id": "evt_101", "time": "20:01:04", "event_type": "CASH_UPDATED", "payload": {"text": "Tata Motors Cash Position Verified: ₹480.00L across HDFC & ICICI Treasury"}},
            {"id": "evt_102", "time": "20:01:08", "event_type": "PAYMENT_RECEIVED", "payload": {"text": "VRL Logistics Ltd fleet purchase wire expected Sep 28: ₹158.40L incoming"}},
            {"id": "evt_103", "time": "20:01:21", "event_type": "DISCOUNT_EXPIRING", "payload": {"text": "Valeo India Lighting Systems INV00002 payment scheduled for today"}},
        ]

        self.decisions_history: List[Decision] = []

    def ingest_and_process_stream_record(self, record: Dict[str, Any]):
        """
        Stores streamed data into persistent Supabase DB & memory & disk ledger, updates entity states,
        and derives updated parameters consumed by the 0/1 Knapsack DP decision pipeline!
        """
        self.stream_ledger.insert(0, record)
        
        # 1. Sync to Supabase Database
        sync_stream_event_to_supabase(record)

        # 2. Save persistent JSON ledger to disk
        try:
            ledger_path = os.path.join(FUTURE_DIR, "stored_stream_records.json")
            with open(ledger_path, "w") as f:
                json.dump(self.stream_ledger[:500], f, indent=2)
        except Exception:
            pass

        # 3. Update cash balances and invoice/receivable states based on streamed transaction
        amount = record.get("amount", 0.0)
        event_type = record.get("event_type", "")

        if event_type in ["RECEIVABLE_INFLOW", "PAYMENT_RECEIVED"]:
            # Add inflow to operating cash balance
            delta = amount / 100000.0 if amount > 100 else amount
            self.accounts[0].balance += delta
            self.accounts[0].available_balance = self.accounts[0].balance
        elif event_type in ["OPEX_OUTFLOW", "EMERGENCY_EXPENSE"]:
            # Deduct outflow from operating cash balance
            delta = amount / 100000.0 if amount > 100 else amount
            self.accounts[0].balance = max(50.0, self.accounts[0].balance - delta)
            self.accounts[0].available_balance = self.accounts[0].balance

    def get_total_cash(self) -> float:
        return sum(acc.balance for acc in self.accounts)

store = DataStore()
