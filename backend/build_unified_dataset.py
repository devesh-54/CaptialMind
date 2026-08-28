import os
import json
import pandas as pd
import sqlite3
from typing import Dict, Any, List

HISTORICAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "historical_data_cashpilot", "data", "historical"))
FUTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data"))
OUTPUT_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "cashpilot_unified_relational_dataset.json"))
OUTPUT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "cashpilot_relational.db"))

def read_csv_if_exists(path: str) -> List[Dict[str, Any]]:
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # Replace NaNs with None/empty string for JSON serialization
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"Warning reading {path}: {e}")
    return []

def build_unified_dataset():
    print("Building unified relational dataset from historical and future streaming data sources...")

    # 1. Company Profile (Root Entity)
    company_data = {
        "company_id": "TATA001",
        "name": "Tata Consumer Products",
        "currency": "INR",
        "minimum_cash_reserve": 970000.0,
        "operating_reserve_floor": 1500000.0,
        "treasury_bank": "HDFC Bank",
        "credit_line_limit": 1250000.0,
        "credit_line_apr": 8.5
    }

    # 2. Cash Accounts
    cash_accounts_hist = read_csv_if_exists(os.path.join(HISTORICAL_DIR, "cash_accounts.csv"))
    cash_accounts_fut = read_csv_if_exists(os.path.join(FUTURE_DIR, "cash_accounts.csv"))

    cash_accounts = []
    seen_cash = set()
    for row in cash_accounts_fut + cash_accounts_hist:
        cid = str(row.get("cash_account_id", "CASH001"))
        if cid not in seen_cash:
            seen_cash.add(cid)
            cash_accounts.append({
                "cash_account_id": cid,
                "company_id": "TATA001",
                "account_name": "Main HDFC Treasury Account",
                "account_type": "OPERATING_TREASURY",
                "opening_balance": float(row.get("opening_balance", 4204079.97)),
                "current_balance": float(row.get("balance", 2554079.97)),
                "available_balance": float(row.get("available_balance", 1954079.97)),
                "reserved_balance": float(row.get("reserved_balance", 970000.0)),
                "deployable_cash": float(row.get("deployable_cash", 984079.97))
            })

    # 3. Customers Entity (Preprocessed Beta-Binomial Priors)
    customers = [
        {
            "customer_id": "CUST011",
            "company_id": "TATA001",
            "name": "Mahindra Logistics",
            "category": "Enterprise Logistics",
            "alpha_prior": 10,
            "beta_prior": 2,
            "observations_count": 12,
            "on_time_probability": 87.0,
            "average_delay_days": 1,
            "risk_rating": "LOW"
        },
        {
            "customer_id": "CUST001",
            "company_id": "TATA001",
            "name": "Flipkart Fulfillment",
            "category": "E-Commerce Retail",
            "alpha_prior": 8,
            "beta_prior": 4,
            "observations_count": 12,
            "on_time_probability": 66.0,
            "average_delay_days": 6,
            "risk_rating": "MEDIUM"
        },
        {
            "customer_id": "CUST009",
            "company_id": "TATA001",
            "name": "Bajaj Auto Ancillaries",
            "category": "Automotive Tier-1",
            "alpha_prior": 7,
            "beta_prior": 5,
            "observations_count": 12,
            "on_time_probability": 78.0,
            "average_delay_days": 5,
            "risk_rating": "MEDIUM"
        },
        {
            "customer_id": "CUST005",
            "company_id": "TATA001",
            "name": "Reliance Retail Distribution",
            "category": "Retail Chain",
            "alpha_prior": 4,
            "beta_prior": 8,
            "observations_count": 12,
            "on_time_probability": 38.0,
            "average_delay_days": 21,
            "risk_rating": "HIGH"
        }
    ]

    # 4. Suppliers Entity
    suppliers_hist = read_csv_if_exists(os.path.join(HISTORICAL_DIR, "suppliers.csv"))
    suppliers = []
    seen_sup = set()
    for row in suppliers_hist:
        sup_id = str(row.get("supplier_id", ""))
        if sup_id and sup_id not in seen_sup:
            seen_sup.add(sup_id)
            imp_val = str(row.get("strategic_importance", "MEDIUM")).upper()
            imp_score = 5 if "CRITICAL" in imp_val else 3 if "MEDIUM" in imp_val else 2
            suppliers.append({
                "supplier_id": sup_id,
                "company_id": "TATA001",
                "name": str(row.get("name", f"Supplier {sup_id}")),
                "category": str(row.get("category", "Raw Materials")),
                "strategic_importance_rating": imp_score,
                "is_critical": "CRITICAL" in imp_val,
                "liquidity_risk": str(row.get("liquidity_risk", "LOW")).upper(),
                "payment_terms": "Net 30 / 2% 10",
                "captured_discount_total": 142000.0
            })

    # Fallback default suppliers if historical CSV had different columns
    if not suppliers:
        suppliers = [
            {"supplier_id": "SUP001", "company_id": "TATA001", "name": "Tata Steel Ltd", "category": "Raw Materials", "strategic_importance_rating": 5, "is_critical": True, "liquidity_risk": "LOW", "captured_discount_total": 142000.0},
            {"supplier_id": "SUP002", "company_id": "TATA001", "name": "JSW Steel Ltd", "category": "Raw Materials", "strategic_importance_rating": 4, "is_critical": True, "liquidity_risk": "LOW", "captured_discount_total": 85000.0},
            {"supplier_id": "SUP003", "company_id": "TATA001", "name": "Bosch Ltd", "category": "Components", "strategic_importance_rating": 5, "is_critical": True, "liquidity_risk": "LOW", "captured_discount_total": 194000.0},
            {"supplier_id": "SUP004", "company_id": "TATA001", "name": "Denso India Pvt Ltd", "category": "Electronics", "strategic_importance_rating": 3, "is_critical": False, "liquidity_risk": "MEDIUM", "captured_discount_total": 42000.0}
        ]

    # 5. Invoices (Merged Historical & Future Open Invoices with Relational Foreign Keys)
    invoices_hist = read_csv_if_exists(os.path.join(HISTORICAL_DIR, "invoices.csv"))
    invoices_fut = read_csv_if_exists(os.path.join(FUTURE_DIR, "invoices.csv"))

    invoices = []
    seen_inv = set()

    for row in invoices_fut:
        inv_id = str(row.get("invoice_id", ""))
        if inv_id and inv_id not in seen_inv:
            seen_inv.add(inv_id)
            sup_id = str(row.get("supplier_id", "SUP003"))
            amount = float(row.get("amount", 68902.88))
            disc_pct = float(row.get("discount_percentage", 0.0))
            invoices.append({
                "invoice_id": inv_id,
                "company_id": "TATA001",
                "supplier_id": sup_id,
                "data_stream_type": "FUTURE_STREAMING",
                "amount": amount,
                "currency": str(row.get("currency", "INR")),
                "issue_date": str(row.get("issue_date", "2026-08-28")),
                "due_date": str(row.get("issue_date", "2026-08-28")),
                "discount_percentage": disc_pct,
                "discount_deadline": str(row.get("discount_deadline", "")),
                "discount_savings_amount": round(amount * disc_pct / 100.0, 2),
                "status": str(row.get("status", "OPEN")),
                "ai_priority_score": 95 if disc_pct > 0 else 82,
                "recommended_action": "Pay Now" if disc_pct > 0 or amount > 100000 else "Pay at Maturity"
            })

    for row in invoices_hist:
        inv_id = str(row.get("invoice_id", ""))
        if inv_id and inv_id not in seen_inv:
            seen_inv.add(inv_id)
            sup_id = str(row.get("supplier_id", "SUP001"))
            amount = float(row.get("amount", 100000.0))
            disc_pct = float(row.get("discount_percentage", 0.0))
            invoices.append({
                "invoice_id": inv_id,
                "company_id": "TATA001",
                "supplier_id": sup_id,
                "data_stream_type": "HISTORICAL",
                "amount": amount,
                "currency": str(row.get("currency", "INR")),
                "issue_date": str(row.get("issue_date", "2026-07-01")),
                "due_date": str(row.get("due_date", "2026-08-01")),
                "discount_percentage": disc_pct,
                "discount_deadline": str(row.get("discount_deadline", "")),
                "discount_savings_amount": round(amount * disc_pct / 100.0, 2),
                "status": str(row.get("status", "PAID")),
                "ai_priority_score": 75,
                "recommended_action": "PAID"
            })

    # 6. Receivables (Merged Historical & Future Open Receivables with Foreign Keys)
    receivables_hist = read_csv_if_exists(os.path.join(HISTORICAL_DIR, "receivables.csv"))
    receivables_fut = read_csv_if_exists(os.path.join(FUTURE_DIR, "receivables.csv"))

    receivables = []
    seen_rec = set()

    for row in receivables_fut:
        rec_id = str(row.get("receivable_id", ""))
        if rec_id and rec_id not in seen_rec:
            seen_rec.add(rec_id)
            cust_id = str(row.get("customer_id", "CUST011"))
            amount = float(row.get("amount", 31760.96))
            prob_raw = float(row.get("collection_probability", 0.87))
            prob = (prob_raw * 100.0) if prob_raw <= 1.0 else prob_raw
            delay = int(row.get("expected_delay_days", 1))

            receivables.append({
                "receivable_id": rec_id,
                "company_id": "TATA001",
                "customer_id": cust_id,
                "data_stream_type": "FUTURE_STREAMING",
                "amount": amount,
                "invoice_date": str(row.get("invoice_date", "2026-08-28")),
                "expected_date": str(row.get("expected_date", "2026-09-28")),
                "collection_probability": round(prob, 1),
                "expected_delay_days": delay,
                "status": "On Time" if delay == 0 else "Slight Delay" if delay <= 5 else "At Risk",
                "actual_payment_date": row.get("actual_payment_date")
            })

    for row in receivables_hist:
        rec_id = str(row.get("receivable_id", ""))
        if rec_id and rec_id not in seen_rec:
            seen_rec.add(rec_id)
            cust_id = str(row.get("customer_id", "CUST001"))
            amount = float(row.get("amount", 500000.0))
            prob_raw = float(row.get("collection_probability", 0.9))
            prob = (prob_raw * 100.0) if prob_raw <= 1.0 else prob_raw

            receivables.append({
                "receivable_id": rec_id,
                "company_id": "TATA001",
                "customer_id": cust_id,
                "data_stream_type": "HISTORICAL",
                "amount": amount,
                "invoice_date": str(row.get("invoice_date", "2026-06-01")),
                "expected_date": str(row.get("expected_date", "2026-07-01")),
                "collection_probability": round(prob, 1),
                "expected_delay_days": int(row.get("expected_delay_days", 0)),
                "status": "PAID",
                "actual_payment_date": row.get("actual_payment_date")
            })

    # 7. Obligations Entity
    obligations = [
        {
            "obligation_id": "OBL-FUT-001",
            "company_id": "TATA001",
            "supplier_id": "INTERNAL_PAYROLL",
            "description": "Operating Expense & Monthly Salaries",
            "amount": 1650000.0,
            "due_date": "2026-08-28",
            "priority": "CRITICAL",
            "ai_action": "Must Pay"
        },
        {
            "obligation_id": "OBL-FUT-002",
            "company_id": "TATA001",
            "supplier_id": "SUP003",
            "description": "Bosch Ltd Component Invoice (INV_FUT_0260)",
            "amount": 68902.88,
            "due_date": "2026-08-28",
            "priority": "HIGH",
            "ai_action": "Pay Now"
        },
        {
            "obligation_id": "OBL-FUT-003",
            "company_id": "TATA001",
            "supplier_id": "SUP003",
            "description": "Bosch Ltd Component Invoice (INV_FUT_0261)",
            "amount": 140555.66,
            "due_date": "2026-08-29",
            "priority": "HIGH",
            "ai_action": "Pay Now"
        }
    ]

    # 8. Transactions Entity (Historical Raw Transactions)
    transactions = read_csv_if_exists(os.path.join(HISTORICAL_DIR, "transactions.csv"))
    if not transactions:
        transactions = read_csv_if_exists(os.path.join(FUTURE_DIR, "transactions.csv"))

    # 9. Future Daily Sequence (128 daily simulation steps)
    future_daily_sequence = read_csv_if_exists(os.path.join(FUTURE_DIR, "future_daily_consolidated.csv"))

    # 10. Autonomous Decision History Lineage
    decisions = [
        {
            "decision_id": "DEC-8801",
            "company_id": "TATA001",
            "timestamp": "2026-08-28 14:45",
            "trigger_event": "Daily Working Capital Run & Future Dataset Sync",
            "title": "Reserve ₹16.5L Opex + Early Settlement for Bosch Ltd (Pay Now)",
            "allocated_amount": 68902.88,
            "confidence_score": 96,
            "status": "SUPERSEDED",
            "version": "v1.2",
            "valid_until": "2026-08-28 17:51",
            "reasons": [
                "Operating Expense & Payroll (₹16.5L) prioritized as CRITICAL due today.",
                "Pay Now candidate scored 96/100 (runner-up Bank Finance scored 74/100).",
                "Customer CUST011 inflow of ₹31.76k on Sep 28 guarantees safety buffer above ₹9.70L floor."
            ]
        },
        {
            "decision_id": "DEC-9700",
            "company_id": "TATA001",
            "timestamp": "2026-08-28 17:51",
            "trigger_event": "Material Change: Customer CUST011 delayed +10 days",
            "title": "Reserve ₹16.5L Opex + Pay Invoices INV_FUT_0260 & 0261 today",
            "allocated_amount": 209458.54,
            "confidence_score": 96,
            "status": "ACTIVE",
            "version": "v2.2",
            "valid_until": None,
            "reasons": [
                "Material Change Detected: Receivable expected payment delayed by +10 days.",
                "Bayesian Customer CUST011 Probability shifted to 76.9%.",
                "Evaluated candidates. 0/1 Knapsack allocation re-optimized, keeping reserve floor above ₹9.70L."
            ]
        }
    ]

    # Combine into single Master Relational Dataset Structure
    unified_dataset = {
        "metadata": {
            "title": "CashPilot AI Unified Relational Master Dataset",
            "version": "2.0.0",
            "schema_architecture": "Relational Foreign Key Linkages",
            "data_sources": [
                "historical_data_cashpilot/data/historical",
                "futureStreaming_data_cashpilot/cashpilot_ai/data"
            ],
            "total_records": {
                "company": 1,
                "cash_accounts": len(cash_accounts),
                "customers": len(customers),
                "suppliers": len(suppliers),
                "invoices": len(invoices),
                "receivables": len(receivables),
                "obligations": len(obligations),
                "transactions": len(transactions),
                "future_daily_sequence": len(future_daily_sequence),
                "decisions": len(decisions)
            }
        },
        "company": company_data,
        "cash_accounts": cash_accounts,
        "customers": customers,
        "suppliers": suppliers,
        "invoices": invoices,
        "receivables": receivables,
        "obligations": obligations,
        "transactions": transactions,
        "future_daily_sequence": future_daily_sequence,
        "decisions": decisions
    }

    # Save to JSON
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(unified_dataset, f, indent=2)

    print(f"Successfully created unified relational JSON dataset at: {OUTPUT_JSON_PATH}")

    # Also build SQLite relational database for SQL queries
    build_sqlite_database(unified_dataset)

    return unified_dataset


def build_sqlite_database(dataset: Dict[str, Any]):
    try:
        conn = sqlite3.connect(OUTPUT_DB_PATH)
        cursor = conn.cursor()

        # 1. Company
        cursor.execute("DROP TABLE IF EXISTS company;")
        cursor.execute("""
            CREATE TABLE company (
                company_id TEXT PRIMARY KEY,
                name TEXT,
                currency TEXT,
                minimum_cash_reserve REAL,
                operating_reserve_floor REAL,
                treasury_bank TEXT,
                credit_line_limit REAL,
                credit_line_apr REAL
            );
        """)
        c = dataset["company"]
        cursor.execute("INSERT INTO company VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (
            c["company_id"], c["name"], c["currency"], c["minimum_cash_reserve"],
            c["operating_reserve_floor"], c["treasury_bank"], c["credit_line_limit"], c["credit_line_apr"]
        ))

        # 2. Customers
        cursor.execute("DROP TABLE IF EXISTS customers;")
        cursor.execute("""
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                company_id TEXT,
                name TEXT,
                category TEXT,
                alpha_prior INTEGER,
                beta_prior INTEGER,
                observations_count INTEGER,
                on_time_probability REAL,
                average_delay_days INTEGER,
                risk_rating TEXT,
                FOREIGN KEY (company_id) REFERENCES company(company_id)
            );
        """)
        for cust in dataset["customers"]:
            cursor.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
                cust["customer_id"], cust["company_id"], cust["name"], cust["category"],
                cust["alpha_prior"], cust["beta_prior"], cust["observations_count"],
                cust["on_time_probability"], cust["average_delay_days"], cust["risk_rating"]
            ))

        # 3. Suppliers
        cursor.execute("DROP TABLE IF EXISTS suppliers;")
        cursor.execute("""
            CREATE TABLE suppliers (
                supplier_id TEXT PRIMARY KEY,
                company_id TEXT,
                name TEXT,
                category TEXT,
                strategic_importance_rating INTEGER,
                is_critical INTEGER,
                liquidity_risk TEXT,
                captured_discount_total REAL,
                FOREIGN KEY (company_id) REFERENCES company(company_id)
            );
        """)
        for sup in dataset["suppliers"]:
            cursor.execute("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (
                sup["supplier_id"], sup["company_id"], sup["name"], sup["category"],
                sup["strategic_importance_rating"], 1 if sup.get("is_critical") else 0,
                sup["liquidity_risk"], sup.get("captured_discount_total", 0.0)
            ))

        # 4. Invoices
        cursor.execute("DROP TABLE IF EXISTS invoices;")
        cursor.execute("""
            CREATE TABLE invoices (
                invoice_id TEXT PRIMARY KEY,
                company_id TEXT,
                supplier_id TEXT,
                data_stream_type TEXT,
                amount REAL,
                currency TEXT,
                issue_date TEXT,
                due_date TEXT,
                discount_percentage REAL,
                discount_savings_amount REAL,
                status TEXT,
                ai_priority_score INTEGER,
                recommended_action TEXT,
                FOREIGN KEY (company_id) REFERENCES company(company_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            );
        """)
        for inv in dataset["invoices"]:
            cursor.execute("INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
                inv["invoice_id"], inv["company_id"], inv["supplier_id"], inv["data_stream_type"],
                inv["amount"], inv["currency"], inv["issue_date"], inv["due_date"],
                inv["discount_percentage"], inv["discount_savings_amount"], inv["status"],
                inv["ai_priority_score"], inv["recommended_action"]
            ))

        # 5. Receivables
        cursor.execute("DROP TABLE IF EXISTS receivables;")
        cursor.execute("""
            CREATE TABLE receivables (
                receivable_id TEXT PRIMARY KEY,
                company_id TEXT,
                customer_id TEXT,
                data_stream_type TEXT,
                amount REAL,
                invoice_date TEXT,
                expected_date TEXT,
                collection_probability REAL,
                expected_delay_days INTEGER,
                status TEXT,
                FOREIGN KEY (company_id) REFERENCES company(company_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
        """)
        for rec in dataset["receivables"]:
            cursor.execute("INSERT INTO receivables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
                rec["receivable_id"], rec["company_id"], rec["customer_id"], rec["data_stream_type"],
                rec["amount"], rec["invoice_date"], rec["expected_date"], rec["collection_probability"],
                rec["expected_delay_days"], rec["status"]
            ))

        # 6. Decisions
        cursor.execute("DROP TABLE IF EXISTS decisions;")
        cursor.execute("""
            CREATE TABLE decisions (
                decision_id TEXT PRIMARY KEY,
                company_id TEXT,
                timestamp TEXT,
                trigger_event TEXT,
                title TEXT,
                allocated_amount REAL,
                confidence_score INTEGER,
                status TEXT,
                version TEXT,
                valid_until TEXT,
                FOREIGN KEY (company_id) REFERENCES company(company_id)
            );
        """)
        for dec in dataset["decisions"]:
            cursor.execute("INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (
                dec["decision_id"], dec["company_id"], dec["timestamp"], dec["trigger_event"],
                dec["title"], dec["allocated_amount"], dec["confidence_score"], dec["status"],
                dec["version"], dec["valid_until"]
            ))

        conn.commit()
        conn.close()
        print(f"Successfully created relational SQLite database at: {OUTPUT_DB_PATH}")
    except Exception as e:
        print(f"Error creating SQLite database: {e}")

if __name__ == "__main__":
    build_unified_dataset()
