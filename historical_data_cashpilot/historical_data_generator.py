"""
CashPilot AI – Historical Data Generator (Previous Year)
=========================================================
Generates full-year 2025 (Jan 1 – Dec 31) financial data for Tata Motors
with all 15 enriched tables matching the new column schema.

Tables produced (saved to data/historical/):
  1.  companies.csv / company.json
  2.  cash_accounts.csv
  3.  suppliers.csv
  4.  customers.csv
  5.  invoices.csv          (accounts payable – supplier invoices)
  6.  receivables.csv       (accounts receivable – customer invoices)
  7.  obligations.csv
  8.  financing_options.csv
  9.  transactions.csv
 10.  events.csv
 11.  decisions.csv
 12.  decision_items.csv
 13.  decision_alternatives.csv
 14.  forecast_snapshots.csv
 15.  scenarios.csv
 16.  future_daily_consolidated.csv  (daily flat file)
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

# ─── Config ──────────────────────────────────────────────────────────────────
RANDOM_SEED = 99
START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime(2025, 12, 31)
NUM_DAYS   = (END_DATE - START_DATE).days + 1        # 365

CURRENCY             = "INR"
STARTING_CASH        = 480_000_000   # ₹48 Crore
MINIMUM_CASH_RESERVE =  50_000_000   # ₹5 Crore
COMPANY_ID           = "COMP001"

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def _rdate(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start if delta <= 0 else start + timedelta(days=random.randint(0, delta))


# ═════════════════════════════════════════════════════════════════════════════
class HistoricalDataGenerator:
# ═════════════════════════════════════════════════════════════════════════════

    def __init__(self):
        self.company: Dict[str, Any] = {}
        self.customers_df            = pd.DataFrame()
        self.suppliers_df            = pd.DataFrame()
        self.financing_options_df    = pd.DataFrame()
        self.invoices_df             = pd.DataFrame()
        self.receivables_df          = pd.DataFrame()
        self.obligations_df          = pd.DataFrame()
        self.transactions_df         = pd.DataFrame()
        self.cash_accounts_df        = pd.DataFrame()
        self.events_df               = pd.DataFrame()
        self.decisions_df            = pd.DataFrame()
        self.decision_items_df       = pd.DataFrame()
        self.decision_alternatives_df= pd.DataFrame()
        self.forecast_snapshots_df   = pd.DataFrame()
        self.scenarios_df            = pd.DataFrame()
        self.consolidated_df         = pd.DataFrame()

    # ── 1. Company ────────────────────────────────────────────────────────────
    def generate_company(self) -> Dict[str, Any]:
        self.company = {
            "id": COMPANY_ID,
            "name": "Tata Motors Ltd",
            "industry": "automotive_manufacturing",
            "currency": CURRENCY,
            "minimum_cash_reserve": MINIMUM_CASH_RESERVE,
            "starting_cash": STARTING_CASH,
        }
        return self.company

    # ── 2. Customers (derive behavior from simulated history) ─────────────────
    def generate_customers(self) -> pd.DataFrame:
        names = [
            "Concorde Motors","Pinnacle Motors","Jayem Automotives",
            "Ganganagar Motors","Bimal Auto Agency","Kiran Motors",
            "Prabhu Motors","Prerana Motors","Sai Service Pvt Ltd",
            "Shivam Autozone","Tirupati Motors","Vinayak Motors",
            "BlueDart Express Ltd","Rivigo Services Pvt Ltd",
            "TCI Express Ltd","VRL Logistics Ltd","Gati Ltd",
            "Eicher Trucks & Buses (Fleet Div)",
            "Indian Army (DGOF)","ONGC Ltd","NTPC Ltd",
            "Tata Steel Ltd (Internal)","Indian Railways",
            "Ashok Leyland (Cross-supply)","Mahindra & Mahindra",
            "State Road Transport Corporations","Delhi Transport Corporation",
            "BEST Undertaking Mumbai","Ola Fleet Technologies",
            "Lithium Urban Technologies",
        ]
        tier_weights = ["reliable"]*3 + ["average"]*5 + ["risky"]*2
        rows: List[Dict] = []
        n = random.randint(22, 28)

        for i in range(n):
            tier = tier_weights[i % len(tier_weights)]
            cid  = f"CUST{i+1:03d}"

            # Simulate historical payment records to *derive* probabilities
            total_payments = random.randint(12, 36)
            if tier == "reliable":
                on_time = int(total_payments * random.uniform(0.85, 0.98))
                terms   = random.choice([15, 30])
                risk    = "LOW"
            elif tier == "average":
                on_time = int(total_payments * random.uniform(0.60, 0.85))
                terms   = random.choice([30, 45])
                risk    = "MEDIUM"
            else:
                on_time = int(total_payments * random.uniform(0.30, 0.60))
                terms   = random.choice([45, 60])
                risk    = "HIGH"

            late_payments = total_payments - on_time
            otp = round(on_time / total_payments, 2)
            late_delays  = [random.randint(3, 45) for _ in range(late_payments)] if late_payments else [0]
            avg_delay    = round(sum(late_delays) / len(late_delays), 1)

            rows.append({
                "customer_id":            cid,
                "customer_name":          names[i] if i < len(names) else fake.company(),
                "company_id":             COMPANY_ID,
                "industry":               "automotive_manufacturing",
                "payment_terms":          terms,
                "risk_category":          risk,
                "total_historical_payments": total_payments,
                "on_time_payments":       on_time,
                "late_payments":          late_payments,
                "on_time_probability":    otp,
                "average_delay_days":     avg_delay,
                "payment_history_tier":   tier,
            })

        self.customers_df = pd.DataFrame(rows)
        return self.customers_df

    # ── 3. Suppliers ──────────────────────────────────────────────────────────
    def generate_suppliers(self) -> pd.DataFrame:
        supplier_defs = [
            ("Tata Steel Ltd",                   "Raw Materials",     "critical", 0.93, 0.12, 30,  True,  11.5),
            ("JSW Steel Ltd",                    "Raw Materials",     "critical", 0.88, 0.15, 30,  True,  12.0),
            ("Bosch Ltd",                        "Engine Components", "critical", 0.91, 0.10, 15,  True,  10.5),
            ("Denso India Pvt Ltd",              "Engine Components", "critical", 0.87, 0.18, 30,  True,  11.0),
            ("MRF Ltd",                          "Tyres",             "medium",   0.72, 0.35, 45,  True,  13.0),
            ("Apollo Tyres Ltd",                 "Tyres",             "medium",   0.65, 0.40, 45,  False,  0.0),
            ("Motherson Sumi Systems Ltd",       "Electrical",        "medium",   0.70, 0.38, 30,  True,  12.5),
            ("Bharat Forge Ltd",                 "Forged Components", "medium",   0.68, 0.42, 45,  False,  0.0),
            ("Sundaram-Clayton Ltd",             "Aluminium Castings","medium",   0.60, 0.45, 45,  True,  13.5),
            ("Valeo India Pvt Ltd",              "Lighting Systems",  "medium",   0.55, 0.50, 60,  False,  0.0),
            ("ZF Commercial Vehicle Control",    "Brakes",            "medium",   0.62, 0.44, 60,  True,  14.0),
            ("Saint-Gobain India",               "Glass",             "low",      0.30, 0.65, 60,  False,  0.0),
            ("3M India Ltd",                     "Consumables",       "low",      0.28, 0.68, 60,  False,  0.0),
            ("Asian Paints Industrial",          "Paints",            "low",      0.25, 0.70, 45,  False,  0.0),
            ("Castrol India Ltd",                "Lubricants",        "low",      0.22, 0.72, 45,  False,  0.0),
        ]
        rows = []
        for i, (name, cat, tier, si, lr, terms, fin_avail, fin_rate) in enumerate(supplier_defs):
            liq_risk = "HIGH" if lr > 0.5 else ("MEDIUM" if lr > 0.25 else "LOW")
            rows.append({
                "supplier_id":               f"SUP{i+1:03d}",
                "company_id":                COMPANY_ID,
                "name":                      name,
                "category":                  cat,
                "strategic_importance":      tier.upper(),
                "strategic_importance_score":si,
                "liquidity_risk":            liq_risk,
                "liquidity_risk_score":      lr,
                "payment_terms_days":        terms,
                "financing_available":       fin_avail,
                "financing_rate":            fin_rate,
            })
        self.suppliers_df = pd.DataFrame(rows)
        return self.suppliers_df

    # ── 4. Financing Options ──────────────────────────────────────────────────
    def generate_financing_options(self) -> pd.DataFrame:
        options = [
            {"id":"FIN001","provider":"State Bank of India",         "type":"BANK_LOAN",            "interest_rate":0.095,"credit_limit":500_000_000,"available_amount":500_000_000,"minimum_amount":5_000_000, "processing_fee":0.005,"repayment_terms":"12 monthly instalments"},
            {"id":"FIN002","provider":"HDFC Bank",                   "type":"LINE_OF_CREDIT",        "interest_rate":0.105,"credit_limit":300_000_000,"available_amount":250_000_000,"minimum_amount":2_000_000, "processing_fee":0.003,"repayment_terms":"Revolving – min 5% monthly"},
            {"id":"FIN003","provider":"ICICI Bank",                  "type":"WORKING_CAPITAL_LOAN",  "interest_rate":0.100,"credit_limit":400_000_000,"available_amount":400_000_000,"minimum_amount":10_000_000,"processing_fee":0.004,"repayment_terms":"6 monthly instalments"},
            {"id":"FIN004","provider":"Kotak Mahindra Bank",         "type":"INVOICE_FINANCING",     "interest_rate":0.120,"credit_limit":200_000_000,"available_amount":180_000_000,"minimum_amount":1_000_000, "processing_fee":0.006,"repayment_terms":"Against invoice settlement"},
            {"id":"FIN005","provider":"Tata Capital Financial Svc",  "type":"SUPPLIER_FINANCING",    "interest_rate":0.085,"credit_limit":150_000_000,"available_amount":120_000_000,"minimum_amount":500_000,  "processing_fee":0.002,"repayment_terms":"90 days from drawdown"},
        ]
        df = pd.DataFrame(options)
        df.rename(columns={"id": "financing_option_id"}, inplace=True)
        self.financing_options_df = df
        return df

    # ── 5. Invoices (Accounts Payable – supplier invoices) ────────────────────
    def generate_invoices(self) -> pd.DataFrame:
        """Supplier invoices that Tata Motors receives and must pay."""
        n = random.randint(350, 600)
        sup_list = self.suppliers_df.to_dict("records")
        rows = []
        for i in range(n):
            sup      = random.choice(sup_list)
            inv_id   = f"INV{i+1:05d}"
            issue    = _rdate(START_DATE, END_DATE - timedelta(days=10))
            terms    = sup["payment_terms_days"]
            due      = issue + timedelta(days=terms)
            amount   = round(random.uniform(3_000_000, 60_000_000), 2)
            disc_pct = round(random.choice([0,0,0,1.0,1.5,2.0,2.5]), 2)
            disc_dl  = issue + timedelta(days=max(terms//3,7)) if disc_pct > 0 else None
            late_pen = round(random.choice([0,0,1.0,1.5,2.0]), 2)
            methods  = ["NEFT","RTGS","IMPS","CHEQUE"]
            method   = random.choice(methods)

            roll = random.random()
            if due > END_DATE:
                status, apd = "PENDING", None
            elif roll < 0.65:
                status = "PAID"
                apd    = due - timedelta(days=random.randint(0,3))
            elif roll < 0.85:
                status = "PAID"
                apd    = due + timedelta(days=random.randint(1, terms//2))
            else:
                status = "OVERDUE" if due < END_DATE - timedelta(days=5) else "PENDING"
                apd    = None

            rows.append({
                "invoice_id":              inv_id,
                "supplier_id":             sup["supplier_id"],
                "company_id":              COMPANY_ID,
                "amount":                  amount,
                "issue_date":              issue.date(),
                "discount_percentage":     disc_pct,
                "discount_deadline":       disc_dl.date() if disc_dl else None,
                "late_penalty_percentage": late_pen,
                "currency":                CURRENCY,
                "payment_method":          method,
                "status":                  status,
                "actual_payment_date":     apd.date() if apd else None,
            })

        self.invoices_df = pd.DataFrame(rows)
        return self.invoices_df

    # ── 6. Receivables (Accounts Receivable – customer invoices) ─────────────
    def generate_receivables(self) -> pd.DataFrame:
        n = random.randint(300, 500)
        cust_list = self.customers_df.to_dict("records")
        rows = []
        for i in range(n):
            cust       = random.choice(cust_list)
            rcv_id     = f"RCV{i+1:05d}"
            inv_date   = _rdate(START_DATE, END_DATE - timedelta(days=15))
            terms      = cust["payment_terms"]
            exp_date   = inv_date + timedelta(days=terms)
            amount     = round(random.uniform(2_000_000, 80_000_000), 2)
            otp        = cust["on_time_probability"]
            avg_delay  = cust["average_delay_days"]

            # Derive collection probability from on_time_probability w/ noise
            cp         = round(min(max(otp + random.uniform(-0.05,0.05), 0.10), 1.0), 2)
            exp_delay  = 0 if random.random() < otp else random.randint(1, int(avg_delay)+10)

            roll = random.random()
            if exp_date > END_DATE:
                status, apd = "PENDING", None
            elif roll < otp:
                status = "PAID"
                apd    = exp_date - timedelta(days=random.randint(0,3))
            elif roll < otp + (1-otp)*0.5:
                status = "PAID"
                apd    = exp_date + timedelta(days=random.randint(1,int(avg_delay)+5))
            else:
                status = "OVERDUE" if exp_date < END_DATE - timedelta(days=5) else "PENDING"
                apd    = None

            rows.append({
                "receivable_id":            rcv_id,
                "customer_id":              cust["customer_id"],
                "company_id":               COMPANY_ID,
                "amount":                   amount,
                "invoice_date":             inv_date.date(),
                "expected_date":            exp_date.date(),
                "collection_probability":   cp,
                "expected_delay_days":      exp_delay,
                "status":                   status,
                "actual_payment_date":      apd.date() if apd else None,
            })

        self.receivables_df = pd.DataFrame(rows)
        return self.receivables_df

    # ── 7. Obligations ────────────────────────────────────────────────────────
    def generate_obligations(self) -> pd.DataFrame:
        categories = ["SALARY","RENT","TAX","EMI","UTILITY","RAW_MATERIAL","REGULATORY","OTHER"]
        sup_list   = self.suppliers_df.to_dict("records")
        n          = random.randint(180, 300)
        rows       = []
        for i in range(n):
            sup      = random.choice(sup_list)
            obl_id   = f"OBL{i+1:05d}"
            cat      = random.choice(categories)
            issue    = _rdate(START_DATE, END_DATE - timedelta(days=15))
            terms    = sup["payment_terms_days"]
            due      = issue + timedelta(days=terms)
            amount   = round(random.uniform(3_000_000, 60_000_000), 2)

            si      = sup["strategic_importance_score"]
            urgency = max(0, 1-(due-END_DATE).days/60) if due >= END_DATE else 1.0
            score   = 0.4*si + 0.3*(amount/60_000_000) + 0.3*urgency
            priority = ("CRITICAL" if score>0.75 else ("HIGH" if score>0.55 else ("MEDIUM" if score>0.35 else "LOW")))

            if due > END_DATE:
                status = "PENDING"
            elif random.random() < 0.65:
                status = "PAID"
            else:
                status = "OVERDUE" if due < END_DATE - timedelta(days=5) else "PENDING"

            rows.append({
                "obligation_id": obl_id,
                "company_id":    COMPANY_ID,
                "supplier_id":   sup["supplier_id"],
                "description":   f"{cat} obligation – {sup['name']}",
                "category":      cat,
                "amount":        amount,
                "issue_date":    issue.date(),
                "due_date":      due.date(),
                "priority":      priority,
                "status":        status,
            })

        self.obligations_df = pd.DataFrame(rows)
        return self.obligations_df

    # ── 8. Transactions ───────────────────────────────────────────────────────
    def generate_transactions(self) -> pd.DataFrame:
        txns: List[Dict] = []

        # Customer receipts (from paid receivables)
        paid_rcv = self.receivables_df[self.receivables_df["status"] == "PAID"]
        for _, r in paid_rcv.iterrows():
            apd = r["actual_payment_date"]
            if apd is None: continue
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "CUSTOMER_PAYMENT",
                "amount":         r["amount"],
                "date":           apd,
                "category":       "RECEIVABLE",
                "description":    f"Collection from {r['customer_id']} – {r['receivable_id']}",
                "reference_type": "RECEIVABLE",
                "reference_id":   r["receivable_id"],
                "status":         "COMPLETED",
            })

        # Supplier payments (from paid invoices)
        paid_inv = self.invoices_df[self.invoices_df["status"] == "PAID"]
        for _, inv in paid_inv.iterrows():
            apd = inv["actual_payment_date"]
            if apd is None: continue
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "SUPPLIER_PAYMENT",
                "amount":         -inv["amount"],
                "date":           apd,
                "category":       "PAYABLE",
                "description":    f"Payment to {inv['supplier_id']} – {inv['invoice_id']}",
                "reference_type": "INVOICE",
                "reference_id":   inv["invoice_id"],
                "status":         "COMPLETED",
            })

        # Daily operating expenses
        for d in range(NUM_DAYS):
            date    = START_DATE + timedelta(days=d)
            weekend = date.weekday() >= 5
            base    = random.uniform(500_000, 2_000_000) if weekend else random.uniform(3_000_000, 12_000_000)
            if date.day >= 28:
                base *= random.uniform(1.3, 1.8)
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "OPERATING_EXPENSE",
                "amount":         -round(base, 2),
                "date":           date.date(),
                "category":       "OPEX",
                "description":    "Daily operating expenses",
                "reference_type": "COMPANY",
                "reference_id":   COMPANY_ID,
                "status":         "COMPLETED",
            })

        # Unexpected expenses / crises
        crisis_days = sorted(random.sample(range(30, 340), 4))
        for cd in crisis_days:
            date  = START_DATE + timedelta(days=cd)
            shock = round(random.uniform(30_000_000, 90_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "UNEXPECTED_EXPENSE",
                "amount":         -shock,
                "date":           date.date(),
                "category":       "EXCEPTIONAL",
                "description":    random.choice(["Equipment failure","Regulatory fine","Legal settlement","Product recall"]),
                "reference_type": "COMPANY",
                "reference_id":   COMPANY_ID,
                "status":         "COMPLETED",
            })

        # Loan draws
        for _ in range(random.randint(2, 5)):
            date = _rdate(START_DATE+timedelta(30), END_DATE-timedelta(30))
            fin  = self.financing_options_df.sample(1).iloc[0]
            draw = round(random.uniform(20_000_000, float(fin["available_amount"])*0.8), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "LOAN_DRAW",
                "amount":         draw,
                "date":           date.date(),
                "category":       "FINANCING",
                "description":    f"Loan drawdown from {fin['provider']}",
                "reference_type": "FINANCING_OPTION",
                "reference_id":   fin["financing_option_id"],
                "status":         "COMPLETED",
            })

        # Loan repayments
        for _ in range(random.randint(2, 4)):
            date  = _rdate(START_DATE+timedelta(60), END_DATE-timedelta(10))
            fin   = self.financing_options_df.sample(1).iloc[0]
            repay = round(random.uniform(10_000_000, 50_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "LOAN_REPAYMENT",
                "amount":         -repay,
                "date":           date.date(),
                "category":       "FINANCING",
                "description":    f"Repayment to {fin['provider']}",
                "reference_type": "FINANCING_OPTION",
                "reference_id":   fin["financing_option_id"],
                "status":         "COMPLETED",
            })

        # Quarterly interest payments
        for q in [90, 180, 270, 360]:
            if q >= NUM_DAYS: continue
            date     = START_DATE + timedelta(days=q)
            interest = round(random.uniform(3_000_000, 15_000_000), 2)
            txns.append({
                "transaction_id": _uid("TXN"),
                "company_id":     COMPANY_ID,
                "type":           "INTEREST_PAYMENT",
                "amount":         -interest,
                "date":           date.date(),
                "category":       "FINANCING",
                "description":    "Quarterly interest payment",
                "reference_type": "FINANCING_OPTION",
                "reference_id":   "FIN001",
                "status":         "COMPLETED",
            })

        df = pd.DataFrame(txns)
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)
        df.reset_index(drop=True, inplace=True)
        self.transactions_df = df
        return df

    # ── 9. Cash Accounts ──────────────────────────────────────────────────────
    def generate_cash_accounts(self) -> pd.DataFrame:
        dates = pd.date_range(START_DATE, periods=NUM_DAYS, freq="D")
        txn   = self.transactions_df.copy()
        txn["inflow"]  = txn["amount"].clip(lower=0)
        txn["outflow"] = (-txn["amount"]).clip(lower=0)
        daily = txn.groupby(txn["date"].dt.date).agg(
            daily_inflow=("inflow","sum"),
            daily_outflow=("outflow","sum"),
        )
        daily.index = pd.to_datetime(daily.index)

        rows = []
        balance = STARTING_CASH
        for date in dates:
            opening  = balance
            inflow   = daily.loc[date,"daily_inflow"]  if date in daily.index else 0.0
            outflow  = daily.loc[date,"daily_outflow"] if date in daily.index else 0.0
            closing  = round(opening + inflow - outflow, 2)
            reserved = round(MINIMUM_CASH_RESERVE * random.uniform(1.0,1.3), 2)
            avail    = round(max(closing - reserved, 0), 2)
            deploy   = round(max(avail - reserved*0.1, 0), 2)

            rows.append({
                "date":              date,
                "company_id":        COMPANY_ID,
                "cash_account_id":   "CASH001",
                "opening_balance":   round(opening,2),
                "daily_inflow":      round(inflow,2),
                "daily_outflow":     round(outflow,2),
                "balance":           closing,
                "available_balance": avail,
                "reserved_balance":  reserved,
                "deployable_cash":   deploy,
            })
            balance = closing

        self.cash_accounts_df = pd.DataFrame(rows)
        return self.cash_accounts_df

    # ── 10. Events ────────────────────────────────────────────────────────────
    def generate_events(self) -> pd.DataFrame:
        event_types = [
            "PAYMENT_RECEIVED","INVOICE_CREATED","RECEIVABLE_DELAYED",
            "SUPPLIER_PAYMENT","NEW_OBLIGATION","FINANCING_DRAWN",
            "INTEREST_RATE_CHANGED","UNEXPECTED_EXPENSE",
        ]
        n    = random.randint(120, 200)
        rows = []
        for _ in range(n):
            etype = random.choice(event_types)
            ts    = _rdate(START_DATE, END_DATE)

            if etype == "PAYMENT_RECEIVED":
                cust    = self.customers_df.sample(1).iloc[0]
                payload = {"amount": round(random.uniform(2e6,50e6),2), "customer_id": cust["customer_id"]}
            elif etype == "INVOICE_CREATED":
                cust    = self.customers_df.sample(1).iloc[0]
                payload = {"amount": round(random.uniform(3e6,60e6),2), "customer_id": cust["customer_id"], "payment_terms": int(cust["payment_terms"])}
            elif etype == "RECEIVABLE_DELAYED":
                cust    = self.customers_df.sample(1).iloc[0]
                delay   = random.randint(5,30)
                orig    = _rdate(START_DATE, END_DATE-timedelta(30))
                payload = {"customer_id": cust["customer_id"],"delay_days": delay,
                           "original_expected_date": str(orig.date()),
                           "new_expected_date": str((orig+timedelta(delay)).date())}
            elif etype == "SUPPLIER_PAYMENT":
                sup  = self.suppliers_df.sample(1).iloc[0]
                payload = {"supplier_id": sup["supplier_id"],"amount": round(random.uniform(3e6,50e6),2)}
            elif etype == "NEW_OBLIGATION":
                sup  = self.suppliers_df.sample(1).iloc[0]
                payload = {"supplier_id": sup["supplier_id"],"amount": round(random.uniform(5e6,60e6),2),"due_days": random.choice([15,30,45,60])}
            elif etype == "FINANCING_DRAWN":
                fin  = self.financing_options_df.sample(1).iloc[0]
                payload = {"financing_option_id": fin["financing_option_id"],"amount": round(random.uniform(10e6,100e6),2)}
            elif etype == "INTEREST_RATE_CHANGED":
                old = round(random.uniform(0.08,0.12),3)
                payload = {"old_rate": old,"new_rate": round(old + random.uniform(-0.01,0.03),3)}
            else:
                payload = {"amount": round(random.uniform(10e6,80e6),2),
                           "reason": random.choice(["Equipment failure","Regulatory fine","Emergency repair","Legal settlement","Product recall"])}

            rows.append({
                "event_id":     _uid("EVT"),
                "company_id":   COMPANY_ID,
                "event_type":   etype,
                "payload":      json.dumps(payload),
                "created_at":   ts,
                "processed_at": ts + timedelta(hours=random.randint(1,6)),
                "status":       "PROCESSED",
            })

        df = pd.DataFrame(rows)
        df.sort_values("created_at", inplace=True)
        df.reset_index(drop=True, inplace=True)
        self.events_df = df
        return df

    # ── 11-13. Decisions, Items, Alternatives ─────────────────────────────────
    def generate_decisions(self) -> pd.DataFrame:
        ALL_ACTIONS = ["PAY_NOW","PAY_AT_MATURITY","DELAY_PAYMENT","CAPTURE_DISCOUNT","BANK_FINANCE","SUPPLIER_FINANCE","RETAIN_CASH"]
        cash_map = self.cash_accounts_df.set_index("date")["available_balance"].to_dict()
        rows, di_rows, da_rows = [], [], []

        trigger_obls = self.obligations_df.sample(min(80,len(self.obligations_df)), random_state=RANDOM_SEED).to_dict("records")

        for obl in trigger_obls:
            dec_date  = pd.Timestamp(obl["due_date"]) - timedelta(days=random.randint(1,10))
            dec_date  = max(dec_date, pd.Timestamp(START_DATE))
            dec_date  = min(dec_date, pd.Timestamp(END_DATE))
            avail     = cash_map.get(dec_date, STARTING_CASH * 0.3)
            amt       = obl["amount"]
            priority  = obl["priority"]

            if avail > amt*2 and priority in ("CRITICAL","HIGH"):
                chosen, confidence = "PAY_NOW", round(random.uniform(0.80,0.95),2)
                reasoning = f"Strong liquidity (₹{avail:,.0f}); {priority} obligation – paying immediately."
            elif avail > amt*1.2 and priority == "MEDIUM":
                chosen, confidence = "PAY_AT_MATURITY", round(random.uniform(0.70,0.85),2)
                reasoning = "Adequate cash; scheduling payment at maturity."
            elif avail < amt and priority in ("CRITICAL","HIGH"):
                chosen, confidence = "BANK_FINANCE", round(random.uniform(0.60,0.80),2)
                reasoning = f"Cash (₹{avail:,.0f}) below obligation (₹{amt:,.0f}); drawing bank finance."
            elif avail < amt*0.5:
                chosen, confidence = "DELAY_PAYMENT", round(random.uniform(0.50,0.70),2)
                reasoning = "Cash very tight – deferring non-critical payment."
            elif random.random() < 0.3:
                chosen, confidence = "CAPTURE_DISCOUNT", round(random.uniform(0.75,0.90),2)
                reasoning = "Early-payment discount available and cash adequate."
            else:
                chosen, confidence = "RETAIN_CASH", round(random.uniform(0.55,0.75),2)
                reasoning = "Preserving liquidity for upcoming obligations."

            dec_id = _uid("DEC")
            rows.append({
                "decision_id":   dec_id,
                "company_id":    COMPANY_ID,
                "created_at":    dec_date,
                "decision_type": "OBLIGATION_PAYMENT",
                "chosen_action": chosen,
                "confidence":    confidence,
                "reasoning":     reasoning,
                "status":        "EXECUTED",
            })

            di_rows.append({
                "decision_item_id": _uid("DI"),
                "decision_id":      dec_id,
                "invoice_id":       obl["obligation_id"],
                "action":           chosen,
                "amount":           amt,
                "score":            confidence,
                "expected_cost":    round(amt * random.uniform(0.01,0.05),2),
                "expected_benefit": round(amt * random.uniform(0.005,0.03),2),
                "risk_score":       round(random.uniform(0.1,0.9),2),
            })

            for act in ALL_ACTIONS:
                s     = round(confidence if act==chosen else random.uniform(0.1,0.9),2)
                cost  = round(amt*random.uniform(0.01,0.08),2)
                ben   = round(amt*random.uniform(0.005,0.04),2)
                liq   = round(random.uniform(-0.3,0.3),2)
                risk  = round(random.uniform(0.1,0.9),2)
                da_rows.append({
                    "alternative_id":   _uid("DA"),
                    "decision_id":      dec_id,
                    "action":           act,
                    "score":            s,
                    "cost":             cost,
                    "benefit":          ben,
                    "liquidity_impact": liq,
                    "risk":             risk,
                })

        self.decisions_df            = pd.DataFrame(rows)
        self.decision_items_df       = pd.DataFrame(di_rows)
        self.decision_alternatives_df= pd.DataFrame(da_rows)
        self.decisions_df.sort_values("created_at", inplace=True)
        self.decisions_df.reset_index(drop=True, inplace=True)
        return self.decisions_df

    # ── 14. Forecast Snapshots ────────────────────────────────────────────────
    def generate_forecast_snapshots(self) -> pd.DataFrame:
        rows = []
        # Generate one snapshot per month
        for month in range(1, 13):
            snap_date = datetime(2025, month, random.randint(1,5))
            balance_row = self.cash_accounts_df[
                self.cash_accounts_df["date"].dt.month == month
            ]
            if balance_row.empty:
                continue
            cur_cash = float(balance_row["balance"].iloc[0])
            for horizon in [7, 14, 30]:
                proj     = round(cur_cash * random.uniform(0.7, 1.3), 2)
                min_proj = round(proj * random.uniform(0.5, 0.9), 2)
                risk     = "LOW" if min_proj > MINIMUM_CASH_RESERVE*2 else ("MEDIUM" if min_proj > MINIMUM_CASH_RESERVE else "HIGH")
                rows.append({
                    "snapshot_id":           _uid("SNAP"),
                    "company_id":            COMPANY_ID,
                    "created_at":            snap_date,
                    "forecast_horizon_days": horizon,
                    "projected_cash":        proj,
                    "minimum_projected_cash":min_proj,
                    "liquidity_risk":        risk,
                    "expected_inflows":      round(proj * random.uniform(0.3,0.6),2),
                    "expected_outflows":     round(proj * random.uniform(0.2,0.5),2),
                    "reserve_requirement":   MINIMUM_CASH_RESERVE,
                    "risk_probability":      round(random.uniform(0.05,0.45),2),
                })

        df = pd.DataFrame(rows)
        df.sort_values("created_at", inplace=True)
        df.reset_index(drop=True, inplace=True)
        self.forecast_snapshots_df = df
        return df

    # ── 15. Scenarios ─────────────────────────────────────────────────────────
    def generate_scenarios(self) -> pd.DataFrame:
        templates = [
            ("Customer payment delayed 10 days",      {"delay_days":10,"affected":"ALL"},                          "WARNING","USE_FINANCING"),
            ("Receivable probability drops 20%",       {"probability_reduction":0.20},                              "CRITICAL","DRAW_LINE_OF_CREDIT"),
            ("Unexpected expense +₹5 Cr",             {"additional_expense":50_000_000},                           "CRITICAL","DELAY_PAYMENTS_AND_FINANCE"),
            ("Supplier payments increase 15%",         {"increase_pct":15},                                         "WARNING","NEGOTIATE_TERMS"),
            ("Interest rate +2%",                     {"rate_increase":0.02},                                      "STABLE","REFINANCE"),
            ("Major customer defaults ₹10 Cr",        {"default_amount":100_000_000,"customer_id":"CUST003"},      "CRITICAL","EMERGENCY_FINANCING"),
            ("All receivables collected on time",     {"collection_probability_override":1.0},                     "HEALTHY","CAPTURE_DISCOUNTS"),
            ("OpEx rises 25%",                        {"opex_increase_pct":25},                                    "WARNING","COST_REDUCTION"),
            ("New ₹20Cr contract signed",             {"contract_value":200_000_000,"schedule":"monthly"},         "HEALTHY","INVEST_SURPLUS"),
            ("INR weakens 5%",                        {"depreciation_pct":5},                                      "WARNING","HEDGE_CURRENCY"),
            ("Credit limit cut 50%",                  {"credit_reduction_pct":50},                                 "CRITICAL","SEEK_ALTERNATIVE_FINANCING"),
            ("Two critical suppliers demand early pay",{"early_payment_days":15,"suppliers":["SUP001","SUP003"]},   "WARNING","NEGOTIATE_OR_FINANCE"),
            ("Tax liability ₹8Cr due next month",     {"tax_amount":80_000_000,"due_in_days":30},                  "CRITICAL","RESERVE_CASH"),
            ("Best-case: high collections + low opex",{"collection_boost_pct":30,"opex_reduction_pct":20},         "HEALTHY","EARLY_PAY_AND_INVEST"),
            ("Worst-case scenario",                   {"collection_reduction_pct":40,"opex_increase_pct":30},      "CRITICAL","EMERGENCY_MEASURES"),
        ]
        rows = []
        for idx, (name, params, liq_status, rec_action) in enumerate(templates):
            if liq_status == "HEALTHY":
                proj_floor = round(random.uniform(150e6,400e6),2)
            elif liq_status in ("CRITICAL","WARNING"):
                proj_floor = round(random.uniform(5e6,60e6),2)
            else:
                proj_floor = round(random.uniform(50e6,150e6),2)

            rows.append({
                "scenario_id":   f"SCN{idx+1:03d}",
                "company_id":    COMPANY_ID,
                "name":          name,
                "parameters":    json.dumps(params),
                "result":        json.dumps({
                    "projected_cash_floor": proj_floor,
                    "minimum_cash_reserve": MINIMUM_CASH_RESERVE,
                    "liquidity_status":     liq_status,
                    "recommended_action":   rec_action,
                }),
                "created_at":    _rdate(START_DATE, END_DATE),
            })

        self.scenarios_df = pd.DataFrame(rows)
        return self.scenarios_df

    # ── 16. Daily Consolidated Flat File ──────────────────────────────────────
    def generate_consolidated(self) -> pd.DataFrame:
        """Builds future_daily_consolidated style flat file for 2025."""
        ca   = self.cash_accounts_df.copy()
        txns = self.transactions_df.copy()

        def _daily_agg(type_filter, col_prefix):
            subset = txns[txns["type"] == type_filter].copy()
            subset["abs_amount"] = subset["amount"].abs()
            g = subset.groupby(subset["date"].dt.date)
            return (
                g["abs_amount"].sum().rename(f"{col_prefix}_amount"),
                g["abs_amount"].count().rename(f"{col_prefix}_count"),
            )

        cust_amt,  cust_cnt  = _daily_agg("CUSTOMER_PAYMENT",   "customer_payment")
        opex_amt,  opex_cnt  = _daily_agg("OPERATING_EXPENSE",  "operating_expense")
        supp_amt,  supp_cnt  = _daily_agg("SUPPLIER_PAYMENT",   "supplier_payment")
        unex_amt,  unex_cnt  = _daily_agg("UNEXPECTED_EXPENSE", "unexpected_expense")
        draw_amt,  draw_cnt  = _daily_agg("LOAN_DRAW",          "loan_draw")
        repay_amt, repay_cnt = _daily_agg("LOAN_REPAYMENT",     "loan_repayment")
        int_amt,   int_cnt   = _daily_agg("INTEREST_PAYMENT",   "interest_payment")

        # Invoice/Obligation counts per day
        inv_df  = self.invoices_df.copy()
        rcv_df  = self.receivables_df.copy()
        obl_df  = self.obligations_df.copy()

        inv_df["issue_date"]  = pd.to_datetime(inv_df["issue_date"])
        rcv_df["invoice_date"]= pd.to_datetime(rcv_df["invoice_date"])
        obl_df["issue_date"]  = pd.to_datetime(obl_df["issue_date"])

        inv_grp = inv_df.groupby(inv_df["issue_date"].dt.date)
        rcv_grp = rcv_df.groupby(rcv_df["invoice_date"].dt.date)
        obl_grp = obl_df.groupby(obl_df["issue_date"].dt.date)

        inv_cnt_s = inv_grp["invoice_id"].count().rename("invoices_created_count")
        inv_amt_s = inv_grp["amount"].sum().rename("invoices_created_amount")
        obl_cnt_s = obl_grp["obligation_id"].count().rename("obligations_created_count")
        obl_amt_s = obl_grp["amount"].sum().rename("obligations_created_amount")
        evt_cnt_s = self.events_df.groupby(pd.to_datetime(self.events_df["created_at"]).dt.date)["event_id"].count().rename("events_logged_count")

        rows = []
        for _, row in ca.iterrows():
            d = row["date"].date()
            rows.append({
                "date":                       row["date"],
                "company_id":                 COMPANY_ID,
                "cash_account_id":            row["cash_account_id"],
                "opening_balance":            row["opening_balance"],
                "daily_inflow":               row["daily_inflow"],
                "daily_outflow":              row["daily_outflow"],
                "balance":                    row["balance"],
                "available_balance":          row["available_balance"],
                "reserved_balance":           row["reserved_balance"],
                "deployable_cash":            row["deployable_cash"],
                "invoices_created_count":     int(inv_cnt_s.get(d, 0)),
                "invoices_created_amount":    float(inv_amt_s.get(d, 0)),
                "obligations_created_count":  int(obl_cnt_s.get(d, 0)),
                "obligations_created_amount": float(obl_amt_s.get(d, 0)),
                "customer_payment_amount":    float(cust_amt.get(d, 0)),
                "customer_payment_count":     int(cust_cnt.get(d, 0)),
                "operating_expense_amount":   float(opex_amt.get(d, 0)),
                "operating_expense_count":    int(opex_cnt.get(d, 0)),
                "supplier_payment_amount":    float(supp_amt.get(d, 0)),
                "supplier_payment_count":     int(supp_cnt.get(d, 0)),
                "unexpected_expense_amount":  float(unex_amt.get(d, 0)),
                "unexpected_expense_count":   int(unex_cnt.get(d, 0)),
                "loan_draw_amount":           float(draw_amt.get(d, 0)),
                "loan_draw_count":            int(draw_cnt.get(d, 0)),
                "loan_repayment_amount":      float(repay_amt.get(d, 0)),
                "loan_repayment_count":       int(repay_cnt.get(d, 0)),
                "interest_payment_amount":    float(int_amt.get(d, 0)),
                "interest_payment_count":     int(int_cnt.get(d, 0)),
                "events_logged_count":        int(evt_cnt_s.get(d, 0)),
            })

        self.consolidated_df = pd.DataFrame(rows)
        return self.consolidated_df

    # ── Orchestrate ───────────────────────────────────────────────────────────
    def generate_all(self) -> Dict[str, Any]:
        print("⚙️  Generating company...")
        self.generate_company()
        print("⚙️  Generating customers...")
        self.generate_customers()
        print("⚙️  Generating suppliers...")
        self.generate_suppliers()
        print("⚙️  Generating financing options...")
        self.generate_financing_options()
        print("⚙️  Generating invoices (AP)...")
        self.generate_invoices()
        print("⚙️  Generating receivables (AR)...")
        self.generate_receivables()
        print("⚙️  Generating obligations...")
        self.generate_obligations()
        print("⚙️  Generating transactions...")
        self.generate_transactions()
        print("⚙️  Generating cash accounts...")
        self.generate_cash_accounts()
        print("⚙️  Generating events...")
        self.generate_events()
        print("⚙️  Generating decisions...")
        self.generate_decisions()
        print("⚙️  Generating forecast snapshots...")
        self.generate_forecast_snapshots()
        print("⚙️  Generating scenarios...")
        self.generate_scenarios()
        print("⚙️  Generating daily consolidated...")
        self.generate_consolidated()
        return self._bundle()

    def _bundle(self) -> Dict[str, Any]:
        return {
            "company":               self.company,
            "customers":             self.customers_df,
            "suppliers":             self.suppliers_df,
            "financing_options":     self.financing_options_df,
            "invoices":              self.invoices_df,
            "receivables":           self.receivables_df,
            "obligations":           self.obligations_df,
            "transactions":          self.transactions_df,
            "cash_accounts":         self.cash_accounts_df,
            "events":                self.events_df,
            "decisions":             self.decisions_df,
            "decision_items":        self.decision_items_df,
            "decision_alternatives": self.decision_alternatives_df,
            "forecast_snapshots":    self.forecast_snapshots_df,
            "scenarios":             self.scenarios_df,
            "future_daily_consolidated": self.consolidated_df,
        }

    # ── Save ──────────────────────────────────────────────────────────────────
    def save(self, output_dir: str = "data/historical") -> None:
        os.makedirs(output_dir, exist_ok=True)

        # Company JSON
        cpath = os.path.join(output_dir, "company.json")
        with open(cpath, "w") as f:
            json.dump(self.company, f, indent=2, default=str)
        print(f"  💾  company                    → {cpath}")

        dfs = {
            "customers":                  self.customers_df,
            "suppliers":                  self.suppliers_df,
            "financing_options":          self.financing_options_df,
            "invoices":                   self.invoices_df,
            "receivables":                self.receivables_df,
            "obligations":                self.obligations_df,
            "transactions":               self.transactions_df,
            "cash_accounts":              self.cash_accounts_df,
            "events":                     self.events_df,
            "decisions":                  self.decisions_df,
            "decision_items":             self.decision_items_df,
            "decision_alternatives":      self.decision_alternatives_df,
            "forecast_snapshots":         self.forecast_snapshots_df,
            "scenarios":                  self.scenarios_df,
            "future_daily_consolidated":  self.consolidated_df,
        }

        for name, df in dfs.items():
            path = os.path.join(output_dir, f"{name}.csv")
            df.to_csv(path, index=False)
            print(f"  💾  {name:35s} → {path}  ({len(df):,} rows)")

        print(f"\n✅  All historical data saved to '{output_dir}/'")


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    gen  = HistoricalDataGenerator()
    gen.generate_all()
    gen.save("data/historical")
    print("\n✅  Done.")
