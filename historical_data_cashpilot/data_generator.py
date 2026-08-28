"""
CashPilot AI – Financial Data Generator
========================================
Generates 365 days of realistic, inter-connected financial data for an
autonomous working-capital management agent.

Author : CashPilot AI Team
Created: 2026-08-28
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from faker import Faker

import config as cfg

# ---------------------------------------------------------------------------
# Initialise randomness & Faker
# ---------------------------------------------------------------------------
random.seed(cfg.RANDOM_SEED)
np.random.seed(cfg.RANDOM_SEED)
fake = Faker("en_IN")
Faker.seed(cfg.RANDOM_SEED)


# ═══════════════════════════════════════════════════════════════════════════
# Helper utilities
# ═══════════════════════════════════════════════════════════════════════════

def _uid(prefix: str = "") -> str:
    """Short deterministic-ish ID (prefix + 8 hex chars)."""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def _random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between *start* and *end*."""
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))


# ═══════════════════════════════════════════════════════════════════════════
# Main generator class
# ═══════════════════════════════════════════════════════════════════════════

class FinancialDataGenerator:
    """
    Generates all 13 data entities for CashPilot AI in dependency order.

    Usage
    -----
    >>> gen = FinancialDataGenerator()
    >>> data = gen.generate_all()
    >>> data["cash_accounts"].head()
    """

    def __init__(self):
        # Stores generated data
        self.company: Dict[str, Any] = {}
        self.customers_df: pd.DataFrame = pd.DataFrame()
        self.suppliers_df: pd.DataFrame = pd.DataFrame()
        self.financing_options_df: pd.DataFrame = pd.DataFrame()
        self.invoices_df: pd.DataFrame = pd.DataFrame()
        self.receivables_df: pd.DataFrame = pd.DataFrame()
        self.obligations_df: pd.DataFrame = pd.DataFrame()
        self.transactions_df: pd.DataFrame = pd.DataFrame()
        self.cash_accounts_df: pd.DataFrame = pd.DataFrame()
        self.events_df: pd.DataFrame = pd.DataFrame()
        self.decisions_df: pd.DataFrame = pd.DataFrame()
        self.decision_items_df: pd.DataFrame = pd.DataFrame()
        self.scenarios_df: pd.DataFrame = pd.DataFrame()

        # Internal bookkeeping
        self._transactions: List[Dict] = []
        self._events: List[Dict] = []

    # ───────────────────────────────────────────────────────────────────
    # 1. Company
    # ───────────────────────────────────────────────────────────────────

    def generate_company(self) -> Dict[str, Any]:
        """Create the Tata Motors company profile."""
        self.company = {
            "company_id": "COMP001",
            "company_name": "Tata Motors Ltd",
            "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
            "currency": cfg.CURRENCY,
            "starting_cash": cfg.STARTING_CASH,
        }
        return self.company

    # ───────────────────────────────────────────────────────────────────
    # 2. Customers
    # ───────────────────────────────────────────────────────────────────

    def generate_customers(self) -> pd.DataFrame:
        """Generate 20-30 customers (dealerships, fleet operators, OEMs) split across three risk tiers."""
        # Realistic Tata Motors customer names
        customer_names = [
            # Major dealership groups
            "Concorde Motors", "Pinnacle Motors", "Jayem Automotives",
            "Ganganagar Motors", "Bimal Auto Agency", "Kiran Motors",
            "Prabhu Motors", "Prerana Motors", "Sai Service Pvt Ltd",
            "Shivam Autozone", "Tirupati Motors", "Vinayak Motors",
            # Fleet operators
            "BlueDart Express Ltd", "Rivigo Services Pvt Ltd",
            "TCI Express Ltd", "VRL Logistics Ltd", "Gati Ltd",
            "Eicher Trucks & Buses (Fleet Div)",
            # Institutional / OEM customers
            "Indian Army (DGOF)", "ONGC Ltd", "NTPC Ltd",
            "Tata Steel Ltd (Internal)", "Indian Railways",
            "Ashok Leyland (Cross-supply)", "Mahindra & Mahindra (Cross-supply)",
            "State Road Transport Corporations", "Municipal Corporations Fleet",
            "Delhi Transport Corporation", "BEST Undertaking Mumbai",
            "Ola Fleet Technologies", "Lithium Urban Technologies",
        ]
        n = random.randint(cfg.NUM_CUSTOMERS_MIN, cfg.NUM_CUSTOMERS_MAX)
        rows: List[Dict] = []

        # Tier distribution: ~30 % reliable, ~50 % average, ~20 % risky
        tier_weights = ["reliable"] * 3 + ["average"] * 5 + ["risky"] * 2

        for i in range(n):
            tier = tier_weights[i % len(tier_weights)]
            cust_id = f"CUST{i + 1:03d}"

            if tier == "reliable":
                otp = round(random.uniform(0.85, 0.98), 2)
                avg_delay = random.randint(0, 5)
                terms = random.choice([15, 30])
                risk = "LOW"
            elif tier == "average":
                otp = round(random.uniform(0.60, 0.85), 2)
                avg_delay = random.randint(5, 15)
                terms = random.choice([30, 45])
                risk = "MEDIUM"
            else:
                otp = round(random.uniform(0.30, 0.60), 2)
                avg_delay = random.randint(15, 45)
                terms = random.choice([45, 60])
                risk = "HIGH"

            rows.append({
                "customer_id": cust_id,
                "customer_name": customer_names[i] if i < len(customer_names) else fake.company(),
                "payment_history": tier,
                "on_time_probability": otp,
                "average_delay_days": avg_delay,
                "historical_delay_count": random.randint(0, 20) if risk != "LOW" else random.randint(0, 3),
                "payment_terms": terms,
                "risk_category": risk,
            })

        self.customers_df = pd.DataFrame(rows)
        return self.customers_df

    # ───────────────────────────────────────────────────────────────────
    # 3. Suppliers
    # ───────────────────────────────────────────────────────────────────

    def generate_suppliers(self) -> pd.DataFrame:
        """Generate 10-15 automotive industry suppliers across importance tiers."""
        # Realistic Tata Motors supplier names
        supplier_names = [
            # Critical (steel, powertrain, electronics)
            "Tata Steel Ltd", "JSW Steel Ltd", "Bosch Ltd",
            "Denso India Pvt Ltd",
            # Medium importance (tyres, interiors, components)
            "MRF Ltd", "Apollo Tyres Ltd", "Motherson Sumi Systems Ltd",
            "Bharat Forge Ltd", "Sundaram-Clayton Ltd", "Valeo India Pvt Ltd",
            "ZF Commercial Vehicle Control Systems",
            # Low importance (consumables, services)
            "Saint-Gobain India", "3M India Ltd",
            "Asian Paints Industrial", "Castrol India Ltd",
        ]
        n = random.randint(cfg.NUM_SUPPLIERS_MIN, cfg.NUM_SUPPLIERS_MAX)
        rows: List[Dict] = []

        tier_cycle = ["critical", "medium", "medium", "low"]

        for i in range(n):
            tier = tier_cycle[i % len(tier_cycle)]
            sup_id = f"SUP{i + 1:03d}"

            if tier == "critical":
                si_score = round(random.uniform(0.85, 1.0), 2)
                lr_score = round(random.uniform(0.05, 0.30), 2)
                terms = random.choice([15, 30])
            elif tier == "medium":
                si_score = round(random.uniform(0.40, 0.85), 2)
                lr_score = round(random.uniform(0.20, 0.60), 2)
                terms = random.choice([30, 45])
            else:
                si_score = round(random.uniform(0.10, 0.40), 2)
                lr_score = round(random.uniform(0.40, 0.80), 2)
                terms = random.choice([45, 60])

            rows.append({
                "supplier_id": sup_id,
                "supplier_name": supplier_names[i] if i < len(supplier_names) else fake.company(),
                "strategic_importance": tier.upper(),
                "strategic_importance_score": si_score,
                "liquidity_risk": "HIGH" if lr_score > 0.5 else ("MEDIUM" if lr_score > 0.25 else "LOW"),
                "liquidity_risk_score": lr_score,
                "payment_terms": terms,
                "financing_terms": f"Net {terms} days",
            })

        self.suppliers_df = pd.DataFrame(rows)
        return self.suppliers_df

    # ───────────────────────────────────────────────────────────────────
    # 4. Financing Options
    # ───────────────────────────────────────────────────────────────────

    def generate_financing_options(self) -> pd.DataFrame:
        """Generate ≥5 financing options of different types (Tata Motors scale)."""
        options = [
            {
                "financing_option_id": "FIN001",
                "provider": "State Bank of India",
                "type": "BANK_LOAN",
                "interest_rate": 0.095,
                "credit_limit": 500_000_000,
                "available_credit": 500_000_000,
                "repayment_terms": "12 monthly instalments",
            },
            {
                "financing_option_id": "FIN002",
                "provider": "HDFC Bank",
                "type": "LINE_OF_CREDIT",
                "interest_rate": 0.105,
                "credit_limit": 300_000_000,
                "available_credit": 250_000_000,
                "repayment_terms": "Revolving – minimum 5 % monthly",
            },
            {
                "financing_option_id": "FIN003",
                "provider": "ICICI Bank",
                "type": "WORKING_CAPITAL_LOAN",
                "interest_rate": 0.10,
                "credit_limit": 400_000_000,
                "available_credit": 400_000_000,
                "repayment_terms": "6 monthly instalments",
            },
            {
                "financing_option_id": "FIN004",
                "provider": "Kotak Mahindra Bank",
                "type": "INVOICE_FINANCING",
                "interest_rate": 0.12,
                "credit_limit": 200_000_000,
                "available_credit": 180_000_000,
                "repayment_terms": "Against invoice settlement",
            },
            {
                "financing_option_id": "FIN005",
                "provider": "Tata Capital Financial Services",
                "type": "SUPPLIER_FINANCING",
                "interest_rate": 0.085,
                "credit_limit": 150_000_000,
                "available_credit": 120_000_000,
                "repayment_terms": "90 days from drawdown",
            },
        ]
        self.financing_options_df = pd.DataFrame(options)
        return self.financing_options_df

    # ───────────────────────────────────────────────────────────────────
    # 5. Invoices
    # ───────────────────────────────────────────────────────────────────

    def generate_invoices(self) -> pd.DataFrame:
        """
        Generate 300-600 invoices.  Invoice status is driven by the
        customer's risk tier and on-time probability.
        """
        n = random.randint(cfg.NUM_INVOICES_MIN, cfg.NUM_INVOICES_MAX)
        cust_list = self.customers_df.to_dict("records")
        rows: List[Dict] = []

        end_date = cfg.END_DATE

        for i in range(n):
            cust = random.choice(cust_list)
            inv_id = f"INV{i + 1:05d}"
            inv_date = _random_date(cfg.START_DATE, end_date - timedelta(days=10))
            terms = cust["payment_terms"]
            due_date = inv_date + timedelta(days=terms)

            amount = round(random.uniform(2_000_000, 80_000_000), 2)
            discount_pct = round(random.choice([0, 0, 0, 1.0, 1.5, 2.0, 2.5]), 2)
            discount_deadline = inv_date + timedelta(days=max(terms // 3, 7)) if discount_pct > 0 else None
            late_penalty = round(random.choice([0, 0, 1.0, 1.5, 2.0]), 2)

            # ----- determine payment status based on customer behaviour -----
            otp = cust["on_time_probability"]
            avg_delay = cust["average_delay_days"]
            roll = random.random()

            if due_date > end_date:
                # Invoice not yet due → PENDING
                status = "PENDING"
                actual_payment_date = None
            elif roll < otp:
                # Paid on time
                status = "PAID"
                actual_payment_date = due_date - timedelta(days=random.randint(0, 3))
            elif roll < otp + (1 - otp) * 0.5:
                # Paid late
                status = "PAID"
                delay = random.randint(1, avg_delay + 10)
                actual_payment_date = due_date + timedelta(days=delay)
            else:
                # Still unpaid
                if due_date < end_date - timedelta(days=5):
                    status = "OVERDUE"
                else:
                    status = "PENDING"
                actual_payment_date = None

            rows.append({
                "invoice_id": inv_id,
                "customer_id": cust["customer_id"],
                "invoice_date": inv_date,
                "amount": amount,
                "due_date": due_date,
                "payment_terms": terms,
                "discount_percentage": discount_pct,
                "discount_deadline": discount_deadline,
                "late_penalty_percentage": late_penalty,
                "status": status,
                "actual_payment_date": actual_payment_date,
            })

        self.invoices_df = pd.DataFrame(rows)
        return self.invoices_df

    # ───────────────────────────────────────────────────────────────────
    # 6. Receivables
    # ───────────────────────────────────────────────────────────────────

    def generate_receivables(self) -> pd.DataFrame:
        """
        Create receivable records for every PENDING / OVERDUE invoice.
        Collection probability mirrors the customer risk profile.
        """
        pending = self.invoices_df[self.invoices_df["status"].isin(["PENDING", "OVERDUE"])]
        cust_map = self.customers_df.set_index("customer_id").to_dict("index")
        rows: List[Dict] = []

        for _, inv in pending.iterrows():
            cust = cust_map[inv["customer_id"]]
            otp = cust["on_time_probability"]
            avg_delay = cust["average_delay_days"]

            # Collection probability decays if overdue
            if inv["status"] == "OVERDUE":
                cp = round(max(otp - random.uniform(0.05, 0.20), 0.10), 2)
                exp_delay = random.randint(avg_delay, avg_delay + 20)
            else:
                cp = round(otp + random.uniform(-0.05, 0.05), 2)
                cp = min(max(cp, 0.10), 1.0)
                exp_delay = random.randint(0, avg_delay + 5)

            rows.append({
                "receivable_id": _uid("RCV"),
                "invoice_id": inv["invoice_id"],
                "customer_id": inv["customer_id"],
                "amount": inv["amount"],
                "expected_date": inv["due_date"] + timedelta(days=exp_delay),
                "collection_probability": cp,
                "expected_delay_days": exp_delay,
                "status": inv["status"],
            })

        self.receivables_df = pd.DataFrame(rows)
        return self.receivables_df

    # ───────────────────────────────────────────────────────────────────
    # 7. Obligations / Payables
    # ───────────────────────────────────────────────────────────────────

    def generate_obligations(self) -> pd.DataFrame:
        """
        Generate 150-300 supplier payment obligations.  Priority is
        derived from supplier strategic importance, amount, and urgency.
        """
        n = random.randint(cfg.NUM_OBLIGATIONS_MIN, cfg.NUM_OBLIGATIONS_MAX)
        sup_list = self.suppliers_df.to_dict("records")
        rows: List[Dict] = []

        end_date = cfg.END_DATE

        for i in range(n):
            sup = random.choice(sup_list)
            obl_id = f"OBL{i + 1:05d}"
            issue_date = _random_date(cfg.START_DATE, end_date - timedelta(days=15))
            terms = sup["payment_terms"]
            due_date = issue_date + timedelta(days=terms)
            amount = round(random.uniform(3_000_000, 60_000_000), 2)

            # Priority logic
            si = sup["strategic_importance_score"]
            urgency = max(0, 1 - (due_date - end_date).days / 60) if due_date >= end_date else 1.0
            score = 0.4 * si + 0.3 * (amount / 60_000_000) + 0.3 * urgency

            if score > 0.75:
                priority = "CRITICAL"
            elif score > 0.55:
                priority = "HIGH"
            elif score > 0.35:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            # Status
            if due_date > end_date:
                status = "PENDING"
            elif random.random() < 0.65:
                status = "PAID"
            else:
                status = "OVERDUE" if due_date < end_date - timedelta(days=5) else "PENDING"

            rows.append({
                "obligation_id": obl_id,
                "supplier_id": sup["supplier_id"],
                "amount": amount,
                "issue_date": issue_date,
                "due_date": due_date,
                "priority": priority,
                "status": status,
            })

        self.obligations_df = pd.DataFrame(rows)
        return self.obligations_df

    # ───────────────────────────────────────────────────────────────────
    # 8. Transactions  (builds the ledger that drives cash accounts)
    # ───────────────────────────────────────────────────────────────────

    def generate_transactions(self) -> pd.DataFrame:
        """
        Create realistic transactions from paid invoices, paid obligations,
        daily operating expenses, and sporadic unexpected expenses.
        These transactions are aggregated to produce the daily cash account.
        """
        txns: List[Dict] = []

        # -- Customer payments (from PAID invoices) --
        paid_inv = self.invoices_df[self.invoices_df["status"] == "PAID"]
        for _, inv in paid_inv.iterrows():
            pay_date = inv["actual_payment_date"]
            if pay_date is None:
                continue
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": pay_date,
                "transaction_type": "CUSTOMER_PAYMENT",
                "entity_type": "INVOICE",
                "entity_id": inv["invoice_id"],
                "amount": inv["amount"],
                "cash_impact": inv["amount"],  # positive = inflow
                "description": f"Payment received for {inv['invoice_id']} from {inv['customer_id']}",
            })

        # -- Supplier payments (from PAID obligations) --
        paid_obl = self.obligations_df[self.obligations_df["status"] == "PAID"]
        for _, obl in paid_obl.iterrows():
            pay_date = obl["due_date"] - timedelta(days=random.randint(0, 3))
            if pay_date < cfg.START_DATE:
                pay_date = cfg.START_DATE
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": pay_date,
                "transaction_type": "SUPPLIER_PAYMENT",
                "entity_type": "OBLIGATION",
                "entity_id": obl["obligation_id"],
                "amount": obl["amount"],
                "cash_impact": -obl["amount"],  # negative = outflow
                "description": f"Payment to {obl['supplier_id']} for {obl['obligation_id']}",
            })

        # -- Daily operating expenses --
        for d in range(cfg.NUM_DAYS):
            date = cfg.START_DATE + timedelta(days=d)
            weekday = date.weekday()
            # Lower expenses on weekends
            if weekday >= 5:
                base = random.uniform(500_000, 2_000_000)
            else:
                base = random.uniform(3_000_000, 12_000_000)
            # Month-end spike
            if date.day >= 28:
                base *= random.uniform(1.3, 1.8)

            txns.append({
                "transaction_id": _uid("TXN"),
                "date": date,
                "transaction_type": "OPERATING_EXPENSE",
                "entity_type": "COMPANY",
                "entity_id": self.company["company_id"],
                "amount": round(base, 2),
                "cash_impact": -round(base, 2),
                "description": "Daily operating expenses",
            })

        # -- Unexpected expenses (inject 2-3 liquidity crises) --
        crisis_days = sorted(random.sample(range(60, 340), 3))
        for cd in crisis_days:
            date = cfg.START_DATE + timedelta(days=cd)
            shock = round(random.uniform(40_000_000, 90_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": date,
                "transaction_type": "UNEXPECTED_EXPENSE",
                "entity_type": "COMPANY",
                "entity_id": self.company["company_id"],
                "amount": shock,
                "cash_impact": -shock,
                "description": f"Unexpected expense – equipment failure / regulatory fine (day {cd})",
            })

        # -- Loan draws (occasional) --
        for _ in range(random.randint(2, 5)):
            date = _random_date(cfg.START_DATE + timedelta(days=30),
                                cfg.END_DATE - timedelta(days=30))
            fin = self.financing_options_df.sample(1).iloc[0]
            draw = round(random.uniform(20_000_000, float(fin["available_credit"])), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": date,
                "transaction_type": "LOAN_DRAW",
                "entity_type": "FINANCING_OPTION",
                "entity_id": fin["financing_option_id"],
                "amount": draw,
                "cash_impact": draw,
                "description": f"Loan drawdown from {fin['provider']} ({fin['type']})",
            })

        # -- Loan repayments --
        for _ in range(random.randint(2, 4)):
            date = _random_date(cfg.START_DATE + timedelta(days=60),
                                cfg.END_DATE - timedelta(days=10))
            fin = self.financing_options_df.sample(1).iloc[0]
            repay = round(random.uniform(10_000_000, 50_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": date,
                "transaction_type": "LOAN_REPAYMENT",
                "entity_type": "FINANCING_OPTION",
                "entity_id": fin["financing_option_id"],
                "amount": repay,
                "cash_impact": -repay,
                "description": f"Loan repayment to {fin['provider']}",
            })

        # -- Interest payments (quarterly) --
        for q in [90, 180, 270, 360]:
            if q >= cfg.NUM_DAYS:
                continue
            date = cfg.START_DATE + timedelta(days=q)
            interest = round(random.uniform(3_000_000, 15_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "date": date,
                "transaction_type": "INTEREST_PAYMENT",
                "entity_type": "FINANCING_OPTION",
                "entity_id": "FIN001",
                "amount": interest,
                "cash_impact": -interest,
                "description": "Quarterly interest payment",
            })

        self._transactions = txns
        self.transactions_df = pd.DataFrame(txns)
        self.transactions_df["date"] = pd.to_datetime(self.transactions_df["date"])
        self.transactions_df.sort_values("date", inplace=True)
        self.transactions_df.reset_index(drop=True, inplace=True)
        return self.transactions_df

    # ───────────────────────────────────────────────────────────────────
    # 9. Daily Cash Accounts  (aggregated from transactions)
    # ───────────────────────────────────────────────────────────────────

    def generate_cash_accounts(self) -> pd.DataFrame:
        """
        Build 365 consecutive daily cash-account rows.
        Balance is computed from aggregated transactions.
        Seasonality & trend are embedded via the transactions themselves.
        """
        dates = pd.date_range(cfg.START_DATE, periods=cfg.NUM_DAYS, freq="D")
        txn = self.transactions_df.copy()

        # Aggregate inflows / outflows per day
        txn["inflow"] = txn["cash_impact"].clip(lower=0)
        txn["outflow"] = (-txn["cash_impact"]).clip(lower=0)
        daily = txn.groupby(txn["date"].dt.date).agg(
            daily_inflow=("inflow", "sum"),
            daily_outflow=("outflow", "sum"),
        )
        daily.index = pd.to_datetime(daily.index)

        rows: List[Dict] = []
        balance = cfg.STARTING_CASH

        for date in dates:
            opening = balance
            inflow = daily.loc[date, "daily_inflow"] if date in daily.index else 0.0
            outflow = daily.loc[date, "daily_outflow"] if date in daily.index else 0.0
            closing = round(opening + inflow - outflow, 2)
            avail = round(max(closing - cfg.MINIMUM_CASH_RESERVE, 0), 2)

            rows.append({
                "date": date,
                "company_id": self.company["company_id"],
                "cash_account_id": "CASH001",
                "opening_balance": round(opening, 2),
                "daily_inflow": round(inflow, 2),
                "daily_outflow": round(outflow, 2),
                "balance": closing,
                "available_balance": avail,
            })
            balance = closing

        self.cash_accounts_df = pd.DataFrame(rows)
        return self.cash_accounts_df

    # ───────────────────────────────────────────────────────────────────
    # 10. Historical Events
    # ───────────────────────────────────────────────────────────────────

    def generate_events(self) -> pd.DataFrame:
        """Generate 100-200 historical financial events with payloads."""
        n = random.randint(cfg.NUM_EVENTS_MIN, cfg.NUM_EVENTS_MAX)
        event_types = [
            "PAYMENT_RECEIVED", "INVOICE_CREATED",
            "RECEIVABLE_DELAYED", "SUPPLIER_PAYMENT",
            "NEW_OBLIGATION", "FINANCING_DRAWN",
            "INTEREST_RATE_CHANGED", "UNEXPECTED_EXPENSE",
        ]
        rows: List[Dict] = []

        for _ in range(n):
            etype = random.choice(event_types)
            ts = _random_date(cfg.START_DATE, cfg.END_DATE)

            if etype == "PAYMENT_RECEIVED":
                cust = self.customers_df.sample(1).iloc[0]
                payload = {
                    "amount": round(random.uniform(2_000_000, 50_000_000), 2),
                    "customer_id": cust["customer_id"],
                }
                impact = "MEDIUM" if payload["amount"] > 20_000_000 else "LOW"
            elif etype == "INVOICE_CREATED":
                cust = self.customers_df.sample(1).iloc[0]
                payload = {
                    "amount": round(random.uniform(3_000_000, 60_000_000), 2),
                    "customer_id": cust["customer_id"],
                    "payment_terms": int(cust["payment_terms"]),
                }
                impact = "LOW"
            elif etype == "RECEIVABLE_DELAYED":
                cust = self.customers_df.sample(1).iloc[0]
                delay = random.randint(5, 30)
                payload = {
                    "customer_id": cust["customer_id"],
                    "delay_days": delay,
                    "amount": round(random.uniform(5_000_000, 40_000_000), 2),
                }
                impact = "HIGH" if delay > 15 else "MEDIUM"
            elif etype == "SUPPLIER_PAYMENT":
                sup = self.suppliers_df.sample(1).iloc[0]
                payload = {
                    "supplier_id": sup["supplier_id"],
                    "amount": round(random.uniform(3_000_000, 50_000_000), 2),
                }
                impact = "MEDIUM"
            elif etype == "NEW_OBLIGATION":
                sup = self.suppliers_df.sample(1).iloc[0]
                payload = {
                    "supplier_id": sup["supplier_id"],
                    "amount": round(random.uniform(5_000_000, 60_000_000), 2),
                    "due_days": random.choice([15, 30, 45, 60]),
                }
                impact = "HIGH" if payload["amount"] > 40_000_000 else "MEDIUM"
            elif etype == "FINANCING_DRAWN":
                fin = self.financing_options_df.sample(1).iloc[0]
                payload = {
                    "financing_option_id": fin["financing_option_id"],
                    "amount": round(random.uniform(10_000_000, 100_000_000), 2),
                }
                impact = "HIGH"
            elif etype == "INTEREST_RATE_CHANGED":
                payload = {
                    "old_rate": round(random.uniform(0.08, 0.12), 3),
                    "new_rate": round(random.uniform(0.10, 0.16), 3),
                }
                impact = "HIGH" if abs(payload["new_rate"] - payload["old_rate"]) > 0.02 else "MEDIUM"
            else:  # UNEXPECTED_EXPENSE
                payload = {
                    "amount": round(random.uniform(10_000_000, 80_000_000), 2),
                    "reason": random.choice([
                        "Equipment failure",
                        "Regulatory fine",
                        "Emergency repair",
                        "Legal settlement",
                        "Product recall costs",
                    ]),
                }
                impact = "CRITICAL" if payload["amount"] > 50_000_000 else "HIGH"

            rows.append({
                "event_id": _uid("EVT"),
                "timestamp": ts,
                "event_type": etype,
                "payload": payload,
                "impact_level": impact,
            })

        self.events_df = pd.DataFrame(rows)
        self.events_df.sort_values("timestamp", inplace=True)
        self.events_df.reset_index(drop=True, inplace=True)
        return self.events_df

    # ───────────────────────────────────────────────────────────────────
    # 11. Decisions
    # ───────────────────────────────────────────────────────────────────

    def generate_decisions(self) -> pd.DataFrame:
        """
        Generate rule-based historical decisions using the current cash
        position, obligations, and receivables.
        """
        all_actions = [
            "PAY_NOW", "PAY_AT_MATURITY", "DELAY_PAYMENT",
            "CAPTURE_DISCOUNT", "BANK_FINANCE",
            "SUPPLIER_FINANCE", "RETAIN_CASH",
        ]
        cash_map = self.cash_accounts_df.set_index("date")["available_balance"].to_dict()
        rows: List[Dict] = []
        di_rows: List[Dict] = []  # decision items

        # Sample a subset of obligations as decision triggers
        trigger_obls = self.obligations_df.sample(
            min(80, len(self.obligations_df)), random_state=cfg.RANDOM_SEED
        ).to_dict("records")

        for obl in trigger_obls:
            dec_date = obl["due_date"] - timedelta(days=random.randint(1, 10))
            if dec_date < cfg.START_DATE:
                dec_date = cfg.START_DATE
            if dec_date > cfg.END_DATE:
                dec_date = cfg.END_DATE

            avail = cash_map.get(pd.Timestamp(dec_date), cfg.STARTING_CASH * 0.3)
            amt = obl["amount"]
            priority = obl["priority"]

            # ---- Rule-based decision logic ----
            if avail > amt * 2 and priority in ("CRITICAL", "HIGH"):
                chosen = "PAY_NOW"
                reasoning = (
                    f"Available balance ₹{avail:,.0f} is comfortable; "
                    f"priority is {priority} – paying immediately."
                )
                confidence = round(random.uniform(0.80, 0.95), 2)
            elif avail > amt * 1.2 and priority == "MEDIUM":
                chosen = "PAY_AT_MATURITY"
                reasoning = (
                    "Sufficient cash but not urgent – scheduling at maturity."
                )
                confidence = round(random.uniform(0.70, 0.85), 2)
            elif avail < amt and priority in ("CRITICAL", "HIGH"):
                chosen = "BANK_FINANCE"
                reasoning = (
                    f"Available balance ₹{avail:,.0f} < obligation ₹{amt:,.0f}; "
                    f"drawing bank finance to cover critical payment."
                )
                confidence = round(random.uniform(0.60, 0.80), 2)
            elif avail < amt * 0.5:
                chosen = "DELAY_PAYMENT"
                reasoning = "Cash very tight – delaying non-critical payment."
                confidence = round(random.uniform(0.50, 0.70), 2)
            else:
                # Check for discount opportunity
                if random.random() < 0.3:
                    chosen = "CAPTURE_DISCOUNT"
                    reasoning = "Early-payment discount available; cash adequate."
                    confidence = round(random.uniform(0.75, 0.90), 2)
                else:
                    chosen = "RETAIN_CASH"
                    reasoning = "Preserving liquidity for upcoming obligations."
                    confidence = round(random.uniform(0.55, 0.75), 2)

            # Build alternatives with scores
            alternatives = []
            scores = {}
            for act in all_actions:
                s = round(random.uniform(0.1, 0.9), 2) if act != chosen else round(confidence, 2)
                scores[act] = s
                alternatives.append(act)

            weights = {
                "cash_availability": round(random.uniform(0.2, 0.4), 2),
                "supplier_importance": round(random.uniform(0.15, 0.3), 2),
                "discount_value": round(random.uniform(0.05, 0.2), 2),
                "penalty_risk": round(random.uniform(0.1, 0.25), 2),
                "financing_cost": round(random.uniform(0.05, 0.15), 2),
            }

            dec_id = _uid("DEC")
            rows.append({
                "decision_id": dec_id,
                "decision_date": dec_date,
                "decision_type": "OBLIGATION_PAYMENT",
                "chosen_action": chosen,
                "alternatives": alternatives,
                "weights": weights,
                "scores": scores,
                "assumptions": {
                    "available_balance": round(avail, 2),
                    "obligation_amount": amt,
                    "priority": priority,
                },
                "reasoning": reasoning,
                "confidence": confidence,
            })

            # Decision item
            di_rows.append({
                "decision_item_id": _uid("DI"),
                "decision_id": dec_id,
                "entity_type": "OBLIGATION",
                "entity_id": obl["obligation_id"],
                "action": chosen,
                "amount": amt,
            })

        self.decisions_df = pd.DataFrame(rows)
        self.decisions_df.sort_values("decision_date", inplace=True)
        self.decisions_df.reset_index(drop=True, inplace=True)

        self.decision_items_df = pd.DataFrame(di_rows)
        return self.decisions_df

    # ───────────────────────────────────────────────────────────────────
    # 12. Decision Items  (already built inside generate_decisions)
    # ───────────────────────────────────────────────────────────────────

    def generate_decision_items(self) -> pd.DataFrame:
        """Return the decision items (generated alongside decisions)."""
        return self.decision_items_df

    # ───────────────────────────────────────────────────────────────────
    # 13. What-If Scenarios
    # ───────────────────────────────────────────────────────────────────

    def generate_scenarios(self) -> pd.DataFrame:
        """Generate 10-20 what-if scenarios with parameters and results."""
        templates = [
            {
                "name": "Customer payment delayed by 10 days",
                "params": {"delay_days": 10, "affected_customers": "ALL"},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(30_000_000, 70_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "WARNING",
                    "recommended_action": "USE_FINANCING",
                },
            },
            {
                "name": "Receivable collection probability reduced by 20 %",
                "params": {"probability_reduction": 0.20},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(20_000_000, 55_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "DRAW_LINE_OF_CREDIT",
                },
            },
            {
                "name": "Unexpected expense increased by ₹5 Crore",
                "params": {"additional_expense": 50_000_000},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(10_000_000, 40_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "DELAY_PAYMENTS_AND_FINANCE",
                },
            },
            {
                "name": "Supplier payment increased by 15 %",
                "params": {"increase_percentage": 15},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(35_000_000, 65_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "WARNING",
                    "recommended_action": "NEGOTIATE_TERMS",
                },
            },
            {
                "name": "Interest rate increased by 2 %",
                "params": {"rate_increase": 0.02},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(40_000_000, 70_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "STABLE",
                    "recommended_action": "REFINANCE",
                },
            },
            {
                "name": "Major customer defaults on ₹10 Crore",
                "params": {"default_amount": 100_000_000, "customer_id": "CUST003"},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(5_000_000, 30_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "EMERGENCY_FINANCING",
                },
            },
            {
                "name": "All receivables collected on time",
                "params": {"collection_probability_override": 1.0},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(150_000_000, 300_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "HEALTHY",
                    "recommended_action": "CAPTURE_DISCOUNTS",
                },
            },
            {
                "name": "Operating expenses rise 25 %",
                "params": {"opex_increase_pct": 25},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(20_000_000, 50_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "WARNING",
                    "recommended_action": "COST_REDUCTION",
                },
            },
            {
                "name": "New ₹20 Crore contract signed – inflow boost",
                "params": {"contract_value": 200_000_000, "payment_schedule": "monthly"},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(200_000_000, 400_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "HEALTHY",
                    "recommended_action": "INVEST_SURPLUS",
                },
            },
            {
                "name": "Currency depreciation (INR weakens 5 %)",
                "params": {"depreciation_pct": 5},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(35_000_000, 60_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "WARNING",
                    "recommended_action": "HEDGE_CURRENCY",
                },
            },
            {
                "name": "Credit limit reduced by 50 %",
                "params": {"credit_reduction_pct": 50},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(15_000_000, 40_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "SEEK_ALTERNATIVE_FINANCING",
                },
            },
            {
                "name": "Two critical suppliers (Tata Steel, Bosch) demand early payment",
                "params": {"early_payment_days": 15, "suppliers": ["SUP001", "SUP003"]},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(25_000_000, 50_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "WARNING",
                    "recommended_action": "NEGOTIATE_OR_FINANCE",
                },
            },
            {
                "name": "Tax liability of ₹8 Crore due next month",
                "params": {"tax_amount": 80_000_000, "due_in_days": 30},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(10_000_000, 35_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "RESERVE_CASH",
                },
            },
            {
                "name": "Best-case: high collections + low expenses",
                "params": {"collection_boost_pct": 30, "opex_reduction_pct": 20},
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(300_000_000, 500_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "HEALTHY",
                    "recommended_action": "EARLY_PAY_AND_INVEST",
                },
            },
            {
                "name": "Worst-case: low collections + high expenses + rate hike",
                "params": {
                    "collection_reduction_pct": 40,
                    "opex_increase_pct": 30,
                    "rate_increase": 0.03,
                },
                "result_fn": lambda: {
                    "projected_cash_floor": round(random.uniform(-20_000_000, 10_000_000), 2),
                    "minimum_cash_reserve": cfg.MINIMUM_CASH_RESERVE,
                    "liquidity_status": "CRITICAL",
                    "recommended_action": "EMERGENCY_MEASURES",
                },
            },
        ]

        n = random.randint(cfg.NUM_SCENARIOS_MIN, cfg.NUM_SCENARIOS_MAX)
        chosen = templates[:n]

        rows: List[Dict] = []
        for idx, t in enumerate(chosen):
            rows.append({
                "scenario_id": f"SCN{idx + 1:03d}",
                "scenario_name": t["name"],
                "parameters": t["params"],
                "result": t["result_fn"](),
            })

        self.scenarios_df = pd.DataFrame(rows)
        return self.scenarios_df

    # ───────────────────────────────────────────────────────────────────
    # 14. Orchestrator
    # ───────────────────────────────────────────────────────────────────

    def generate_all(self) -> Dict[str, Any]:
        """
        Generate every entity in dependency order and return a dictionary
        keyed by entity name → DataFrame (or dict for company).
        """
        self.generate_company()
        self.generate_customers()
        self.generate_suppliers()
        self.generate_financing_options()
        self.generate_invoices()
        self.generate_receivables()
        self.generate_obligations()
        self.generate_transactions()
        self.generate_cash_accounts()
        self.generate_events()
        self.generate_decisions()
        self.generate_decision_items()
        self.generate_scenarios()

        return {
            "company": self.company,
            "customers": self.customers_df,
            "suppliers": self.suppliers_df,
            "financing_options": self.financing_options_df,
            "invoices": self.invoices_df,
            "receivables": self.receivables_df,
            "obligations": self.obligations_df,
            "transactions": self.transactions_df,
            "cash_accounts": self.cash_accounts_df,
            "events": self.events_df,
            "decisions": self.decisions_df,
            "decision_items": self.decision_items_df,
            "scenarios": self.scenarios_df,
        }

    # ───────────────────────────────────────────────────────────────────
    # 15. Save to CSV / JSON
    # ───────────────────────────────────────────────────────────────────

    def save_to_csv(self, output_dir: str = "data") -> None:
        """
        Persist all generated data to disk.

        - DataFrames → CSV files in *output_dir*.
        - Company dict → company.json in *output_dir*.
        - Columns containing dicts/lists (payload, parameters, etc.)
          are serialised as JSON strings so they survive the CSV
          round-trip.
        """
        os.makedirs(output_dir, exist_ok=True)

        data = self.generate_all() if not self.company else {
            "company": self.company,
            "customers": self.customers_df,
            "suppliers": self.suppliers_df,
            "financing_options": self.financing_options_df,
            "invoices": self.invoices_df,
            "receivables": self.receivables_df,
            "obligations": self.obligations_df,
            "transactions": self.transactions_df,
            "cash_accounts": self.cash_accounts_df,
            "events": self.events_df,
            "decisions": self.decisions_df,
            "decision_items": self.decision_items_df,
            "scenarios": self.scenarios_df,
        }

        # --- Company (dict → JSON) ---
        company_path = os.path.join(output_dir, "company.json")
        with open(company_path, "w") as f:
            json.dump(data["company"], f, indent=2, default=str)
        print(f"  💾  Saved company       → {company_path}")

        # --- DataFrames (→ CSV) ---
        # Some columns hold dicts / lists; convert them to JSON strings.
        dict_columns = {
            "events": ["payload"],
            "decisions": ["alternatives", "weights", "scores", "assumptions"],
            "scenarios": ["parameters", "result"],
        }

        for name, df in data.items():
            if name == "company":
                continue
            out = df.copy()
            # Serialise dict/list columns
            for col in dict_columns.get(name, []):
                if col in out.columns:
                    out[col] = out[col].apply(
                        lambda v: json.dumps(v, default=str) if isinstance(v, (dict, list)) else v
                    )
            csv_path = os.path.join(output_dir, f"{name}.csv")
            out.to_csv(csv_path, index=False)
            print(f"  💾  Saved {name:25s} → {csv_path}  ({len(out):,} rows)")

        print(f"\n✅  All data saved to '{output_dir}/' directory.")

    # ───────────────────────────────────────────────────────────────────
    # 16. Load from CSV / JSON
    # ───────────────────────────────────────────────────────────────────

    @staticmethod
    def load_from_csv(input_dir: str = "data") -> Dict[str, Any]:
        """
        Reload previously saved data from *input_dir*.

        Returns the same dict structure as ``generate_all()``.
        Dict/list columns are deserialised from their JSON strings.
        """
        # --- Company ---
        company_path = os.path.join(input_dir, "company.json")
        with open(company_path, "r") as f:
            company = json.load(f)

        # --- DataFrames ---
        csv_names = [
            "customers", "suppliers", "financing_options",
            "invoices", "receivables", "obligations",
            "transactions", "cash_accounts", "events",
            "decisions", "decision_items", "scenarios",
        ]

        dict_columns = {
            "events": ["payload"],
            "decisions": ["alternatives", "weights", "scores", "assumptions"],
            "scenarios": ["parameters", "result"],
        }

        date_columns = {
            "invoices": ["invoice_date", "due_date", "discount_deadline", "actual_payment_date"],
            "receivables": ["expected_date"],
            "obligations": ["issue_date", "due_date"],
            "transactions": ["date"],
            "cash_accounts": ["date"],
            "events": ["timestamp"],
            "decisions": ["decision_date"],
        }

        result: Dict[str, Any] = {"company": company}

        for name in csv_names:
            csv_path = os.path.join(input_dir, f"{name}.csv")
            df = pd.read_csv(csv_path)

            # Parse date columns
            for col in date_columns.get(name, []):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            # Deserialise JSON columns
            for col in dict_columns.get(name, []):
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda v: json.loads(v) if isinstance(v, str) else v
                    )

            result[name] = df

        print(f"✅  Loaded all data from '{input_dir}/' directory.")
        return result


# ═══════════════════════════════════════════════════════════════════════════
# Quick-run entry point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    gen = FinancialDataGenerator()
    data = gen.generate_all()
    for key, val in data.items():
        if isinstance(val, dict):
            print(f"\n{'='*60}")
            print(f"  {key.upper()} (dict)")
            print(f"{'='*60}")
            for k, v in val.items():
                print(f"  {k}: {v}")
        else:
            print(f"\n{'='*60}")
            print(f"  {key.upper()}  –  {len(val)} records")
            print(f"{'='*60}")
            print(val.head(3).to_string(index=False))

    # Save everything to data/ folder
    print(f"\n{'='*60}")
    print("  SAVING TO DISK")
    print(f"{'='*60}")
    gen.save_to_csv("data")

    print("\n✅  All data generated and saved successfully.")
