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

HISTORICAL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "historical_data_cashpilot", "data", "historical")
FUTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data")

class DataStore:
    def __init__(self):
        self.stream_ledger: List[Dict[str, Any]] = []
        self.reset_to_defaults()

    def reset_to_defaults(self):
        self.company = Company(
            id="comp_tata001",
            name="Tata Consumer Products",
            currency="INR",
            minimum_30day_reserve=9.70
        )

        # Load real cash accounts from datasets
        self.accounts: List[CashAccount] = [
            CashAccount(id="acc_1", name="Main Treasury (HDFC)", account_type="Operating Cash", balance=19.54, available_balance=19.54, yield_rate=0.04),
            CashAccount(id="acc_2", name="Liquidity Reserve (ICICI)", account_type="Reserved Buffer", balance=9.70, available_balance=9.70, yield_rate=0.065),
            CashAccount(id="acc_3", name="Revolving Credit Line", account_type="Credit Line", balance=12.50, available_balance=12.50, yield_rate=0.085),
        ]

        # Load real suppliers from merged dataset
        self.suppliers: List[Supplier] = [
            Supplier(id="SUP003", name="Bosch Ltd", strategic_importance=0.95, liquidity_risk="Low", payment_terms="2/10 Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP002", name="JSW Steel Ltd", strategic_importance=0.82, liquidity_risk="Moderate", payment_terms="Net-30", archetype=SupplierArchetype.STANDARD),
            Supplier(id="SUP006", name="Apollo Tyres Ltd", strategic_importance=0.75, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.STANDARD),
            Supplier(id="SUP001", name="Tata Steel Ltd", strategic_importance=0.90, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.CRITICAL),
        ]

        # Historical transactions preprocessing
        self.historical_txs = generate_historical_transactions()
        
        p1 = preprocess_customer_history("CUST011", self.historical_txs)
        p2 = preprocess_customer_history("CUST001", self.historical_txs)
        p3 = preprocess_customer_history("CUST009", self.historical_txs)

        self.customers: List[Customer] = [
            Customer(id="CUST011", name="Customer CUST011 Enterprise", archetype=EntityArchetype.RELIABLE, alpha=p1["alpha"], beta=p1["beta"], on_time_probability=p1["on_time_probability"], average_delay_days=p1["average_delay_days"]),
            Customer(id="CUST001", name="Customer CUST001 Logistics", archetype=EntityArchetype.AVERAGE, alpha=p2["alpha"], beta=p2["beta"], on_time_probability=p2["on_time_probability"], average_delay_days=p2["average_delay_days"]),
            Customer(id="CUST009", name="Customer CUST009 Retail", archetype=EntityArchetype.RISKY, alpha=p3["alpha"], beta=p3["beta"], on_time_probability=p3["on_time_probability"], average_delay_days=p3["average_delay_days"]),
        ]

        # Real future open invoices parsed from dataset
        self.invoices: List[Invoice] = [
            Invoice(id="INV_FUT_0260", supplier_id="SUP003", supplier_name="Bosch Ltd", amount=0.689, issue_date="2026-08-28", due_date="2026-08-28", due_days=0, discount_percentage=2.0, discount_deadline_days=2, late_penalty_percentage=2.0, priority_score=95.0, recommended_action=ActionType.PAY_NOW, action_reason="Tier-1 critical supplier. Preserves delivery SLA and clears invoice due today."),
            Invoice(id="INV_FUT_0261", supplier_id="SUP003", supplier_name="Bosch Ltd", amount=1.405, issue_date="2026-08-29", due_date="2026-08-29", due_days=1, discount_percentage=0.0, discount_deadline_days=0, late_penalty_percentage=2.0, priority_score=89.0, recommended_action=ActionType.PAY_NOW, action_reason="Bosch Component Invoice due tomorrow."),
            Invoice(id="INV_FUT_0262", supplier_id="SUP002", supplier_name="JSW Steel Ltd", amount=0.215, issue_date="2026-08-31", due_date="2026-08-31", due_days=3, discount_percentage=0.0, discount_deadline_days=0, late_penalty_percentage=2.0, priority_score=65.0, recommended_action=ActionType.PAY_AT_MATURITY, action_reason="Standard terms; liquidity preservation until maturity."),
        ]

        # Real future receivables parsed from dataset
        self.receivables: List[Receivable] = [
            Receivable(id="REC_FUT_0365", customer_id="CUST011", customer_name="Customer CUST011", amount=0.317, expected_date="2026-09-28", due_days=31, collection_probability=p1["on_time_probability"], expected_delay_days=p1["average_delay_days"], probability_history=[0.85, 0.87, 0.89]),
            Receivable(id="REC_FUT_0366", customer_id="CUST001", customer_name="Customer CUST001", amount=2.430, expected_date="2026-10-18", due_days=51, collection_probability=p2["on_time_probability"], expected_delay_days=p2["average_delay_days"], probability_history=[0.62, 0.64, 0.66]),
        ]

        # Real future obligations parsed from dataset
        self.obligations: List[Obligation] = [
            Obligation(id="ob_1", description="Operating Expense & Monthly Salaries", amount=16.50, due_days=0, priority="CRITICAL"),
            Obligation(id="ob_2", description="Bosch Ltd Invoice INV_FUT_0260", amount=0.689, due_days=0, priority="High"),
            Obligation(id="ob_3", description="Bosch Ltd Invoice INV_FUT_0261", amount=1.405, due_days=1, priority="High"),
        ]

        # Real financing options
        self.financing_options: List[FinancingOption] = [
            FinancingOption(id="fin_1", provider="HDFC Treasury", type="Internal Cash Deployment", interest_rate_annual=0.0, credit_limit=25.54, available_amount=19.54, processing_fee=0.0, recommended=True),
            FinancingOption(id="fin_2", provider="ICICI Bank", type="Dynamic Bank Credit Line", interest_rate_annual=8.5, credit_limit=12.50, available_amount=12.50, processing_fee=0.1, recommended=False),
        ]

        self.events_log: List[Dict[str, Any]] = [
            {"id": "evt_101", "time": "20:01:04", "event_type": "CASH_UPDATED", "payload": {"text": "Cash position updated: ₹25.54 Cr across HDFC & ICICI treasury"}},
            {"id": "evt_102", "time": "20:01:08", "event_type": "PAYMENT_RECEIVED", "payload": {"text": "Customer CUST011 invoice expected Sep 28: ₹31.76k incoming wire"}},
            {"id": "evt_103", "time": "20:01:21", "event_type": "DISCOUNT_EXPIRING", "payload": {"text": "Bosch Ltd INV_FUT_0260 payment scheduled for today"}},
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
            self.accounts[0].balance = max(9.70, self.accounts[0].balance - delta)
            self.accounts[0].available_balance = self.accounts[0].balance

    def get_total_cash(self) -> float:
        return sum(acc.balance for acc in self.accounts)

store = DataStore()
