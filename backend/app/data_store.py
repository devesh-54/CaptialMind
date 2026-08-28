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
            id="comp_tatamotors_001",
            name="Tata Motors Ltd",
            currency="INR",
            minimum_30day_reserve=15.50
        )

        # Cash Accounts for Tata Motors Ltd
        self.accounts: List[CashAccount] = [
            CashAccount(id="acc_1", name="Main Operating Cash (HDFC Treasury)", account_type="Operating Cash", balance=29.54, available_balance=29.54, yield_rate=0.04),
            CashAccount(id="acc_2", name="Liquidity Reserve (ICICI Treasury)", account_type="Reserved Buffer", balance=15.50, available_balance=15.50, yield_rate=0.065),
            CashAccount(id="acc_3", name="Revolving Working Capital Line (SBI)", account_type="Credit Line", balance=25.00, available_balance=25.00, yield_rate=0.085),
        ]

        # Automotive Suppliers for Tata Motors Ltd
        self.suppliers: List[Supplier] = [
            Supplier(id="SUP001", name="Bosch Ltd (Powertrain Electronics)", strategic_importance=0.95, liquidity_risk="Low", payment_terms="2/10 Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP002", name="JSW Steel Ltd (Auto Sheet Metal)", strategic_importance=0.88, liquidity_risk="Moderate", payment_terms="Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP003", name="Bharat Forge Ltd (Chassis & Forgings)", strategic_importance=0.92, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.CRITICAL),
            Supplier(id="SUP004", name="Apollo Tyres Ltd (Commercial CV Radial)", strategic_importance=0.82, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.STANDARD),
            Supplier(id="SUP005", name="Exide Industries Ltd (EV Battery Packs)", strategic_importance=0.85, liquidity_risk="Low", payment_terms="Net-30", archetype=SupplierArchetype.STANDARD),
        ]

        # Historical transactions preprocessing for Tata Motors Customer Accounts
        self.historical_txs = generate_historical_transactions()
        
        p1 = preprocess_customer_history("CUST011", self.historical_txs)
        p2 = preprocess_customer_history("CUST001", self.historical_txs)
        p3 = preprocess_customer_history("CUST009", self.historical_txs)

        self.customers: List[Customer] = [
            Customer(id="CUST011", name="VRL Logistics Ltd (Fleet Buyer)", archetype=EntityArchetype.RELIABLE, alpha=p1["alpha"], beta=p1["beta"], on_time_probability=p1["on_time_probability"], average_delay_days=p1["average_delay_days"]),
            Customer(id="CUST001", name="TCI Express Ltd (Transport Operator)", archetype=EntityArchetype.AVERAGE, alpha=p2["alpha"], beta=p2["beta"], on_time_probability=p2["on_time_probability"], average_delay_days=p2["average_delay_days"]),
            Customer(id="CUST009", name="South Eastern Freight Carriers", archetype=EntityArchetype.RISKY, alpha=p3["alpha"], beta=p3["beta"], on_time_probability=p3["on_time_probability"], average_delay_days=p3["average_delay_days"]),
        ]

        # Tata Motors Open Invoices parsed from dynamic dataset
        self.invoices: List[Invoice] = [
            Invoice(id="INV_TML_0260", supplier_id="SUP001", supplier_name="Bosch Ltd (Powertrain Electronics)", amount=1.689, issue_date="2026-08-28", due_date="2026-08-28", due_days=0, discount_percentage=2.0, discount_deadline_days=2, late_penalty_percentage=2.0, priority_score=95.0, recommended_action=ActionType.PAY_NOW, action_reason="Tier-1 critical powertrain supplier. Preserves vehicle assembly SLA and clears invoice due today."),
            Invoice(id="INV_TML_0261", supplier_id="SUP002", supplier_name="JSW Steel Ltd (Auto Sheet Metal)", amount=4.405, issue_date="2026-08-29", due_date="2026-08-29", due_days=1, discount_percentage=0.0, discount_deadline_days=0, late_penalty_percentage=2.0, priority_score=89.0, recommended_action=ActionType.PAY_NOW, action_reason="JSW Automotive Sheet Metal Invoice due tomorrow."),
            Invoice(id="INV_TML_0262", supplier_id="SUP003", supplier_name="Bharat Forge Ltd (Chassis Components)", amount=2.215, issue_date="2026-08-31", due_date="2026-08-31", due_days=3, discount_percentage=0.0, discount_deadline_days=0, late_penalty_percentage=2.0, priority_score=65.0, recommended_action=ActionType.PAY_AT_MATURITY, action_reason="Standard terms; liquidity preservation until maturity."),
        ]

        # Tata Motors Fleet Purchase Receivables
        self.receivables: List[Receivable] = [
            Receivable(id="REC_TML_0365", customer_id="CUST011", customer_name="VRL Logistics Ltd (Fleet CV Purchase)", amount=3.176, expected_date="2026-09-28", due_days=31, collection_probability=p1["on_time_probability"], expected_delay_days=p1["average_delay_days"], probability_history=[0.85, 0.87, 0.89]),
            Receivable(id="REC_TML_0366", customer_id="CUST001", customer_name="TCI Express Ltd (Transport Delivery)", amount=24.30, expected_date="2026-10-18", due_days=51, collection_probability=p2["on_time_probability"], expected_delay_days=p2["average_delay_days"], probability_history=[0.62, 0.64, 0.66]),
        ]

        # Tata Motors Obligations
        self.obligations: List[Obligation] = [
            Obligation(id="ob_1", description="Plant Operating Expense & Assembly Worker Payroll", amount=16.50, due_days=0, priority="CRITICAL"),
            Obligation(id="ob_2", description="Bosch Ltd Invoice INV_TML_0260 (Powertrain Systems)", amount=1.689, due_days=0, priority="High"),
            Obligation(id="ob_3", description="JSW Steel Ltd Invoice INV_TML_0261 (Body Stampings)", amount=4.405, due_days=1, priority="High"),
        ]

        # Tata Motors Financing Options
        self.financing_options: List[FinancingOption] = [
            FinancingOption(id="fin_1", provider="HDFC Treasury", type="Internal Cash Deployment", interest_rate_annual=0.0, credit_limit=29.54, available_amount=29.54, processing_fee=0.0, recommended=True),
            FinancingOption(id="fin_2", provider="ICICI Bank", type="Dynamic Bank Credit Line", interest_rate_annual=8.5, credit_limit=15.50, available_amount=15.50, processing_fee=0.1, recommended=False),
        ]

        self.events_log: List[Dict[str, Any]] = [
            {"id": "evt_101", "time": "20:01:04", "event_type": "CASH_UPDATED", "payload": {"text": "Tata Motors Cash Position Verified: ₹45.04 Cr across HDFC & ICICI Treasury"}},
            {"id": "evt_102", "time": "20:01:08", "event_type": "PAYMENT_RECEIVED", "payload": {"text": "VRL Logistics Ltd fleet purchase wire expected Sep 28: ₹3.17L incoming"}},
            {"id": "evt_103", "time": "20:01:21", "event_type": "DISCOUNT_EXPIRING", "payload": {"text": "Bosch Ltd Powertrain INV_TML_0260 payment scheduled for today"}},
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
            self.accounts[0].balance = max(15.50, self.accounts[0].balance - delta)
            self.accounts[0].available_balance = self.accounts[0].balance

    def get_total_cash(self) -> float:
        return sum(acc.balance for acc in self.accounts)

store = DataStore()
