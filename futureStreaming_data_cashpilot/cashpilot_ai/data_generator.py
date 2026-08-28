import random
import datetime
import json
import uuid
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Generator

# Import configurations
import cashpilot_ai.config as config

class FinancialDataGenerator:
    def __init__(self, seed: int = None):
        """
        Initializes the financial data generator with a fixed random seed.
        """
        self.seed = seed if seed is not None else config.RANDOM_SEED
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Internal placeholders for generated raw structures before DataFrame conversion
        self.company_data = {}
        self.customers_raw = []
        self.suppliers_raw = []
        self.financing_options_raw = []
        self.invoices_raw = []       # Supplier invoices (Accounts Payable)
        self.receivables_raw = []     # Customer invoices (Accounts Receivable)
        self.obligations_raw = []     # General operating/recurring obligations
        self.transactions_raw = []    # General ledger
        self.events_raw = []
        self.decisions_raw = []
        self.decision_items_raw = []
        self.decision_alternatives_raw = []
        self.forecast_snapshots_raw = []
        self.scenarios_raw = []
        
        # Predefined names for realistic entities
        self.customer_names = [
            "Maruti Suzuki India", "Mahindra & Mahindra Ltd", "Tata Motors Dealership North",
            "Ashok Leyland Logistics", "VRL Logistics Ltd", "Safexpress Corporate",
            "Force Motors Ltd", "Ola Electric Mobility", "Ather Energy Corp",
            "Eicher Motors Corporate", "TVS Motor Corporate", "Bajaj Auto Distribution",
            "Honda Cars India Pvt Ltd", "Hyundai Motors Corporate", "Toyota Kirloskar Commercial"
        ]
        
        self.supplier_names = [
            "Alpha Auto Components", "Dynamic Precision Tools",
            "Apex Logistics Pvt Ltd", "National Power Grid Corp",
            "Pioneer Steel Casting", "Matrix Packaging Solutions",
            "Sterling Forge & Metals", "Prism Glass & Ceramics",
            "Intellect Software Systems", "Standard Utilities & Water",
            "Kalyani Engine Alloys", "Bharat Electronics Ltd"
        ]

    def generate_company(self) -> Dict[str, Any]:
        """
        Generates a single fictional company record (Tata Motors Ltd).
        """
        self.company_data = {
            "company_id": "TATA001",
            "company_name": "Tata Motors Ltd",
            "currency": "INR",
            "minimum_cash_reserve": float(config.MINIMUM_CASH_RESERVE),
            "industry": "automotive_manufacturing"
        }
        return self.company_data

    def generate_customers(self) -> pd.DataFrame:
        """
        Generates baseline customer profiles with distinct underlying archetypes.
        Empirical columns (on_time_probability, average_delay_days, payment_history)
        will be populated later after historical transactions are generated.
        """
        num_customers = len(self.customer_names)
        self.customers_raw = []
        
        archetypes = ["reliable", "average", "risky"]
        weights = [0.4, 0.4, 0.2]
        
        categories = ["Dealership Network", "Fleet Operator", "OEM Partner", "Government Contract"]
        
        for i, name in enumerate(self.customer_names):
            cust_id = f"CUST{i+1:03d}"
            archetype = random.choices(archetypes, weights=weights)[0]
            category = random.choice(categories)
            
            # Setup hidden parameters
            if archetype == "reliable":
                payment_terms = random.choice([15, 30])
                true_on_time = random.uniform(0.85, 0.98)
                true_avg_delay = random.uniform(0.0, 5.0)
            elif archetype == "average":
                payment_terms = random.choice([30, 45])
                true_on_time = random.uniform(0.60, 0.85)
                true_avg_delay = random.uniform(5.0, 15.0)
            else:
                payment_terms = random.choice([45, 60, 90])
                true_on_time = random.uniform(0.30, 0.60)
                true_avg_delay = random.uniform(15.0, 45.0)
                
            self.customers_raw.append({
                "customer_id": cust_id,
                "company_id": "TATA001",
                "customer_name": name,
                "category": category,
                "archetype": archetype,
                "true_on_time_probability": true_on_time,
                "true_average_delay_days": true_avg_delay,
                "payment_terms": f"NET_{payment_terms}",
                "payment_terms_days": payment_terms,
                "on_time_probability": 0.0,
                "average_delay_days": 0.0,
                "historical_delay_count": 0,
                "payment_history": "No history",
                "risk_category": "UNKNOWN"
            })
            
        return pd.DataFrame(self.customers_raw)

    def generate_suppliers(self) -> pd.DataFrame:
        """
        Generates suppliers with strategic importance, categories, and financing parameters.
        """
        num_suppliers = len(self.supplier_names)
        self.suppliers_raw = []
        
        categories = ["Engine Components", "Body Panels", "Electrical Systems", "Tires", "Logistics", "Casting & Forging"]
        
        for i, name in enumerate(self.supplier_names):
            sup_id = f"SUP{i+1:03d}"
            category = categories[i % len(categories)]
            
            # Determine strategic importance archetype
            rand_val = random.random()
            if rand_val < 0.30:
                strategic_importance = 0.90 + random.uniform(0.0, 0.10) # CRITICAL
                liq_risk = random.choice(["LOW", "MEDIUM"])
                payment_terms = random.choice([15, 30])
                financing_available = True
                financing_rate = 0.115 # 11.5%
            elif rand_val < 0.80:
                strategic_importance = 0.40 + random.uniform(0.0, 0.40) # MEDIUM
                liq_risk = random.choice(["LOW", "MEDIUM", "HIGH"])
                payment_terms = random.choice([30, 45])
                financing_available = random.random() < 0.5
                financing_rate = 0.125 if financing_available else 0.0
            else:
                strategic_importance = 0.10 + random.uniform(0.0, 0.30) # LOW
                liq_risk = random.choice(["MEDIUM", "HIGH"])
                payment_terms = random.choice([45, 60])
                financing_available = False
                financing_rate = 0.0
                
            self.suppliers_raw.append({
                "supplier_id": sup_id,
                "company_id": "TATA001",
                "name": name,
                "category": category,
                "strategic_importance": round(strategic_importance, 2),
                "liquidity_risk": liq_risk,
                "payment_terms_days": payment_terms,
                "financing_available": financing_available,
                "financing_rate": f"{financing_rate*100:.1f}%" if financing_available else "N/A"
            })
            
        return pd.DataFrame(self.suppliers_raw)

    def generate_financing_options(self) -> pd.DataFrame:
        """
        Generates financing options with different structures and minimum limits.
        """
        self.financing_options_raw = [
            {
                "facility_id": "FIN001",
                "company_id": "TATA001",
                "provider": "State Bank of India",
                "type": "BANK_LOAN",
                "interest_rate": 0.095,  # 9.5% p.a.
                "credit_limit": 5000000.0,
                "available_amount": 5000000.0,
                "minimum_amount": 500000.0,
                "processing_fee": 15000.0,
                "repayment_terms": "Monthly EMI over 24 months"
            },
            {
                "facility_id": "FIN002",
                "company_id": "TATA001",
                "provider": "HDFC Bank",
                "type": "LINE_OF_CREDIT",
                "interest_rate": 0.115,  # 11.5% p.a.
                "credit_limit": 3000000.0,
                "available_amount": 3000000.0,
                "minimum_amount": 100000.0,
                "processing_fee": 5000.0,
                "repayment_terms": "Revolving, interest paid monthly"
            },
            {
                "facility_id": "FIN003",
                "company_id": "TATA001",
                "provider": "ICICI Bank",
                "type": "WORKING_CAPITAL_LOAN",
                "interest_rate": 0.108,  # 10.8% p.a.
                "credit_limit": 4000000.0,
                "available_amount": 4000000.0,
                "minimum_amount": 250000.0,
                "processing_fee": 10000.0,
                "repayment_terms": "Bullet repayment in 180 days"
            },
            {
                "facility_id": "FIN004",
                "company_id": "TATA001",
                "provider": "KredX Factoring",
                "type": "INVOICE_FINANCING",
                "interest_rate": 0.135,  # 13.5% p.a.
                "credit_limit": 2500000.0,
                "available_amount": 2500000.0,
                "minimum_amount": 50000.0,
                "processing_fee": 2500.0,
                "repayment_terms": "Repaid upon customer payment"
            },
            {
                "facility_id": "FIN005",
                "company_id": "TATA001",
                "provider": "Tata Capital Solutions",
                "type": "SUPPLIER_FINANCING",
                "interest_rate": 0.085,  # 8.5% p.a.
                "credit_limit": 2000000.0,
                "available_amount": 2000000.0,
                "minimum_amount": 100000.0,
                "processing_fee": 5000.0,
                "repayment_terms": "Net 90 extensions"
            }
        ]
        return pd.DataFrame(self.financing_options_raw)

    def generate_receivables(self) -> pd.DataFrame:
        """
        Generates customer invoices (AR) across 365 days.
        Simulates payment dates based on true customer behavior profiles.
        """
        num_receivables = random.randint(350, 420)
        self.receivables_raw = []
        
        start_date = config.START_DATE
        num_days = config.NUM_DAYS
        cutoff_date = start_date + datetime.timedelta(days=num_days)
        
        for i in range(num_receivables):
            rec_id = f"REC{i+1:04d}"
            
            customer = random.choice(self.customers_raw)
            cust_id = customer["customer_id"]
            
            # Select invoice issue date
            invoice_day_offset = random.randint(0, num_days - 5)
            invoice_date = start_date + datetime.timedelta(days=invoice_day_offset)
            
            # Invoice amount (realistic distribution for automotive parts, e.g. ₹50,000 to ₹1,500,000)
            amount = round(float(np.random.lognormal(mean=11.6, sigma=0.7)), 2)
            amount = min(max(amount, 30000.0), 3000000.0)
            amount = round(amount, 2)
            
            due_date = invoice_date + datetime.timedelta(days=customer["payment_terms_days"])
            
            # Simulate payment date using customer true parameters
            p_on_time = customer["true_on_time_probability"]
            avg_delay = customer["true_average_delay_days"]
            
            is_on_time = random.random() < p_on_time
            if is_on_time:
                delay = random.randint(-5, 0)
            else:
                delay = int(np.random.exponential(scale=avg_delay)) + 1
                
            actual_payment_date = due_date + datetime.timedelta(days=delay)
            
            if actual_payment_date <= cutoff_date:
                status = "PAID"
            else:
                status = "OVERDUE" if due_date <= cutoff_date else "PENDING"
                
            self.receivables_raw.append({
                "receivable_id": rec_id,
                "customer_id": cust_id,
                "company_id": "TATA001",
                "amount": amount,
                "invoice_date": invoice_date,
                "due_date": due_date, # Helper
                "expected_date": due_date + datetime.timedelta(days=int(avg_delay)), # Placeholder to be updated with derived
                "collection_probability": round(float(p_on_time), 2), # Placeholder to be updated
                "expected_delay_days": int(avg_delay), # Placeholder to be updated
                "status": status,
                "actual_payment_date": actual_payment_date if status == "PAID" else pd.NaT,
                "simulated_delay": delay  # Helper field for statistics calculation
            })
            
        return pd.DataFrame(self.receivables_raw)

    def generate_invoices(self) -> pd.DataFrame:
        """
        Generates supplier invoices (AP) across 365 days.
        """
        num_invoices = random.randint(220, 260)
        self.invoices_raw = []
        
        start_date = config.START_DATE
        num_days = config.NUM_DAYS
        cutoff_date = start_date + datetime.timedelta(days=num_days)
        
        sup_map = {s["supplier_id"]: s for s in self.suppliers_raw}
        supplier_ids = list(sup_map.keys())
        
        for i in range(num_invoices):
            inv_id = f"INV{i+1:04d}"
            sup_id = random.choice(supplier_ids)
            supplier = sup_map[sup_id]
            
            # Select invoice issue date
            issue_day_offset = random.randint(0, num_days - 5)
            issue_date = start_date + datetime.timedelta(days=issue_day_offset)
            due_date = issue_date + datetime.timedelta(days=supplier["payment_terms_days"])
            
            # Invoice amount (₹20,000 to ₹2,000,000)
            amount = round(float(np.random.lognormal(mean=11.2, sigma=0.8)), 2)
            amount = min(max(amount, 15000.0), 2000000.0)
            amount = round(amount, 2)
            
            # Early payment discount terms
            discount_percentage = 0.0
            discount_deadline = pd.NaT
            if supplier["financing_available"] and random.random() < 0.4:
                discount_percentage = random.choice([1.0, 2.0])
                discount_deadline = issue_date + datetime.timedelta(days=10)
                
            late_penalty_percentage = random.choice([1.5, 2.0])
            payment_method = random.choice(["NEFT", "RTGS", "NACH"])
            
            # Determine payment date (normally due date, early if discount is captured, late if cash crunch)
            # Cash crunch periods
            crunch_dates = [
                start_date + datetime.timedelta(days=120),
                start_date + datetime.timedelta(days=210),
                start_date + datetime.timedelta(days=300)
            ]
            
            is_crunch = False
            for cd in crunch_dates:
                if cd <= due_date <= cd + datetime.timedelta(days=10):
                    is_crunch = True
                    break
                    
            if is_crunch and supplier["strategic_importance"] < 0.5:
                # Delay payment during cash crunches
                delay = random.randint(15, 30)
            elif discount_percentage > 0 and random.random() < 0.5:
                # Capture discount
                delay = - (supplier["payment_terms_days"] - 10)
            else:
                delay = random.randint(-2, 0)
                
            actual_payment_date = due_date + datetime.timedelta(days=delay)
            
            if actual_payment_date <= cutoff_date:
                status = "PAID"
            else:
                status = "PENDING"
                
            self.invoices_raw.append({
                "invoice_id": inv_id,
                "supplier_id": sup_id,
                "company_id": "TATA001",
                "amount": amount,
                "issue_date": issue_date,
                "due_date": due_date,
                "discount_percentage": discount_percentage,
                "discount_deadline": discount_deadline if discount_percentage > 0 else pd.NaT,
                "late_penalty_percentage": late_penalty_percentage,
                "currency": "INR",
                "payment_method": payment_method,
                "status": status,
                "actual_payment_date": actual_payment_date if status == "PAID" else pd.NaT
            })
            
        return pd.DataFrame(self.invoices_raw)

    def generate_obligations(self) -> pd.DataFrame:
        """
        Generates general operating payables (salaries, rent, utilities, EMI, taxes, regulatory fees).
        """
        self.obligations_raw = []
        start_date = config.START_DATE
        num_days = config.NUM_DAYS
        cutoff_date = start_date + datetime.timedelta(days=num_days)
        
        # Monthly operating items
        for month in range(12):
            # 1. Rent (Day 1)
            rent_date = start_date + datetime.timedelta(days=month * 30 + 1)
            if rent_date < cutoff_date:
                self.obligations_raw.append({
                    "obligation_id": f"OBL_RENT_{month+1:02d}",
                    "company_id": "TATA001",
                    "description": f"Corporate Facility Rent - Month {month+1}",
                    "category": "RENT",
                    "amount": 120000.0,
                    "due_date": rent_date,
                    "priority": "HIGH",
                    "status": "PAID",
                    "actual_payment_date": rent_date
                })
                
            # 2. Payroll (Day 28)
            payroll_date = start_date + datetime.timedelta(days=month * 30 + 28)
            if payroll_date < cutoff_date:
                self.obligations_raw.append({
                    "obligation_id": f"OBL_PAY_{month+1:02d}",
                    "company_id": "TATA001",
                    "description": f"Factory & HQ Employee Salaries - Month {month+1}",
                    "category": "SALARY",
                    "amount": 1650000.0,
                    "due_date": payroll_date,
                    "priority": "CRITICAL",
                    "status": "PAID",
                    "actual_payment_date": payroll_date
                })
                
            # 3. Utilities (Day 10)
            util_date = start_date + datetime.timedelta(days=month * 30 + 10)
            if util_date < cutoff_date:
                self.obligations_raw.append({
                    "obligation_id": f"OBL_UTIL_{month+1:02d}",
                    "company_id": "TATA001",
                    "description": f"Power & Water Utility Charges - Month {month+1}",
                    "category": "UTILITY",
                    "amount": 45000.0,
                    "due_date": util_date,
                    "priority": "MEDIUM",
                    "status": "PAID",
                    "actual_payment_date": util_date
                })
                
            # 4. Bank Loan EMI (Day 5)
            emi_date = start_date + datetime.timedelta(days=month * 30 + 5)
            if emi_date < cutoff_date:
                self.obligations_raw.append({
                    "obligation_id": f"OBL_EMI_{month+1:02d}",
                    "company_id": "TATA001",
                    "description": f"HDFC Capital Expansion Loan EMI - Month {month+1}",
                    "category": "EMI",
                    "amount": 185000.0,
                    "due_date": emi_date,
                    "priority": "HIGH",
                    "status": "PAID",
                    "actual_payment_date": emi_date
                })
                
        # 5. GST & TDS Tax Obligations (Quarterly - Day 20)
        for q in range(4):
            tax_date = start_date + datetime.timedelta(days=(q+1) * 90 + 20)
            if tax_date < cutoff_date:
                self.obligations_raw.append({
                    "obligation_id": f"OBL_TAX_{q+1:02d}",
                    "company_id": "TATA001",
                    "description": f"Quarterly GST & TDS Filing Compliance",
                    "category": "TAX",
                    "amount": 420000.0,
                    "due_date": tax_date,
                    "priority": "CRITICAL",
                    "status": "PAID",
                    "actual_payment_date": tax_date
                })
                
        return pd.DataFrame(self.obligations_raw)

    def generate_transactions(self) -> pd.DataFrame:
        """
        Creates historical cash transaction ledger entries that represent cleared payments.
        """
        self.transactions_raw = []
        
        # 1. Add CUSTOMER_PAYMENT transactions from PAID receivables (AR)
        for rec in self.receivables_raw:
            if rec["status"] == "PAID":
                tx_id = f"TX_IN_{len(self.transactions_raw)+1:05d}"
                self.transactions_raw.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "CUSTOMER_PAYMENT",
                    "amount": rec["amount"],
                    "date": rec["actual_payment_date"],
                    "category": "CUSTOMER_COLLECTION",
                    "description": f"Payment received for receivable invoice {rec['receivable_id']}",
                    "reference_type": "RECEIVABLE",
                    "reference_id": rec["receivable_id"],
                    "status": "CLEARED"
                })
                
        # 2. Add SUPPLIER_PAYMENT transactions from PAID invoices (AP)
        for inv in self.invoices_raw:
            if inv["status"] == "PAID":
                tx_id = f"TX_OUT_{len(self.transactions_raw)+1:05d}"
                self.transactions_raw.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "SUPPLIER_PAYMENT",
                    "amount": inv["amount"],
                    "date": inv["actual_payment_date"],
                    "category": "RAW_MATERIAL",
                    "description": f"Payment cleared for supplier invoice {inv['invoice_id']}",
                    "reference_type": "INVOICE",
                    "reference_id": inv["invoice_id"],
                    "status": "CLEARED"
                })
                
        # 3. Add OPERATING_EXPENSE transactions from PAID obligations
        for obl in self.obligations_raw:
            if obl["status"] == "PAID":
                tx_id = f"TX_OPS_{len(self.transactions_raw)+1:05d}"
                self.transactions_raw.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "OPERATING_EXPENSE",
                    "amount": obl["amount"],
                    "date": obl["actual_payment_date"],
                    "category": obl["category"],
                    "description": obl["description"],
                    "reference_type": "OBLIGATION",
                    "reference_id": obl["obligation_id"],
                    "status": "CLEARED"
                })
                
        # 4. Inject unexpected expenses and LOC financing interactions
        crunch_events = [
            {"date": config.START_DATE + datetime.timedelta(days=120), "amount": 800000.0, "desc": "Emergency stamping tool replacement"},
            {"date": config.START_DATE + datetime.timedelta(days=210), "amount": 600000.0, "desc": "Environmental compliance safety audit"},
            {"date": config.START_DATE + datetime.timedelta(days=300), "amount": 900000.0, "desc": "Tax audit reconciliation settlement"}
        ]
        
        for i, crunch in enumerate(crunch_events):
            tx_id = f"TX_UNEXP_{i+1:02d}"
            self.transactions_raw.append({
                "transaction_id": tx_id,
                "company_id": "TATA001",
                "type": "UNEXPECTED_EXPENSE",
                "amount": crunch["amount"],
                "date": crunch["date"],
                "category": "OTHER",
                "description": crunch["desc"],
                "reference_type": "NONE",
                "reference_id": np.nan,
                "status": "CLEARED"
            })
            
            # LOC draws
            draw_date = crunch["date"]
            self.transactions_raw.append({
                "transaction_id": f"TX_DRAW_{i+1:02d}",
                "company_id": "TATA001",
                "type": "LOAN_DRAW",
                "amount": 1000000.0,
                "date": draw_date,
                "category": "EMI",
                "description": "LOC drawdown to cover working capital crunch",
                "reference_type": "NONE",
                "reference_id": np.nan,
                "status": "CLEARED"
            })
            
            # Monthly Interest
            self.transactions_raw.append({
                "transaction_id": f"TX_INT_{i+1:02d}",
                "company_id": "TATA001",
                "type": "INTEREST_PAYMENT",
                "amount": 9583.33,
                "date": draw_date + datetime.timedelta(days=30),
                "category": "EMI",
                "description": "LOC drawdown monthly interest payment",
                "reference_type": "NONE",
                "reference_id": np.nan,
                "status": "CLEARED"
            })
            
            # Repay LOC
            self.transactions_raw.append({
                "transaction_id": f"TX_REPAY_{i+1:02d}",
                "company_id": "TATA001",
                "type": "LOAN_REPAYMENT",
                "amount": 1000000.0,
                "date": draw_date + datetime.timedelta(days=60),
                "category": "EMI",
                "description": "LOC drawdown principal repayment",
                "reference_type": "NONE",
                "reference_id": np.nan,
                "status": "CLEARED"
            })
            
        return pd.DataFrame(self.transactions_raw)

    def generate_cash_accounts(self) -> pd.DataFrame:
        """
        Generates daily cash balance accounting logs.
        Includes calculations for reserved_balance and deployable_cash.
        """
        daily_cash_raw = []
        
        start_date = config.START_DATE
        num_days = config.NUM_DAYS
        
        current_cash = float(config.STARTING_CASH)
        
        # Convert ledger lists to DataFrames for faster querying
        tx_df = pd.DataFrame(self.transactions_raw)
        tx_df["date"] = pd.to_datetime(tx_df["date"]).dt.date
        
        obl_df = pd.DataFrame(self.obligations_raw)
        obl_df["due_date"] = pd.to_datetime(obl_df["due_date"]).dt.date
        if "actual_payment_date" in obl_df.columns:
            obl_df["actual_payment_date"] = pd.to_datetime(obl_df["actual_payment_date"]).dt.date
            
        for day in range(num_days):
            current_date = start_date + datetime.timedelta(days=day)
            
            # Opening balance
            opening_balance = current_cash
            
            # Get cleared transactions on this date
            day_txs = tx_df[tx_df["date"] == current_date]
            
            inflow = day_txs[day_txs["type"].isin(["CUSTOMER_PAYMENT", "LOAN_DRAW"])]["amount"].sum()
            outflow = day_txs[~day_txs["type"].isin(["CUSTOMER_PAYMENT", "LOAN_DRAW"])]["amount"].sum()
            
            closing_balance = opening_balance + inflow - outflow
            current_cash = closing_balance
            
            # Safety reserves
            available_balance = max(closing_balance - config.MINIMUM_CASH_RESERVE, 0.0)
            
            # Earmarked cash reserved for upcoming operating obligations (rent, payroll, utilities) due in the next 7 days
            upcoming_obs = obl_df[
                (obl_df["due_date"] >= current_date) & 
                (obl_df["due_date"] <= current_date + datetime.timedelta(days=7)) &
                ((obl_df["actual_payment_date"].isna()) | (obl_df["actual_payment_date"] > current_date))
            ]
            reserved_balance = float(upcoming_obs["amount"].sum())
            
            deployable_cash = max(available_balance - reserved_balance, 0.0)
            
            daily_cash_raw.append({
                "date": current_date,
                "company_id": "TATA001",
                "cash_account_id": "CASH001",
                "opening_balance": round(opening_balance, 2),
                "daily_inflow": round(inflow, 2),
                "daily_outflow": round(outflow, 2),
                "balance": round(closing_balance, 2),
                "available_balance": round(available_balance, 2),
                "reserved_balance": round(reserved_balance, 2),
                "deployable_cash": round(deployable_cash, 2)
            })
            
        return pd.DataFrame(daily_cash_raw)

    def update_derived_customer_statistics(self) -> pd.DataFrame:
        """
        Calculates empirical customer metrics from historical paid receivables.
        """
        cust_df = pd.DataFrame(self.customers_raw)
        rec_df = pd.DataFrame(self.receivables_raw)
        
        for idx, row in cust_df.iterrows():
            cust_id = row["customer_id"]
            cust_recs = rec_df[rec_df["customer_id"] == cust_id]
            
            if len(cust_recs) > 0:
                paid_recs = cust_recs[cust_recs["status"] == "PAID"]
                total_count = len(cust_recs)
                paid_count = len(paid_recs)
                
                # Check delay
                on_time_count = len(paid_recs[paid_recs["simulated_delay"] <= 0])
                on_time_prob = on_time_count / paid_count if paid_count > 0 else row["true_on_time_probability"]
                
                # Average delay calculated ONLY from late payments
                late_recs = paid_recs[paid_recs["simulated_delay"] > 0]
                avg_delay = late_recs["simulated_delay"].mean() if len(late_recs) > 0 else 0.0
                
                delay_count = len(late_recs)
                
                if on_time_prob >= 0.85:
                    risk_cat = "LOW"
                elif on_time_prob >= 0.60:
                    risk_cat = "MEDIUM"
                else:
                    risk_cat = "HIGH"
                    
                summary = f"Total: {total_count}, Paid: {paid_count}, Delayed: {delay_count}"
                
                cust_df.at[idx, "on_time_probability"] = round(float(on_time_prob), 2)
                cust_df.at[idx, "average_delay_days"] = round(float(avg_delay), 2)
                cust_df.at[idx, "historical_delay_count"] = int(delay_count)
                cust_df.at[idx, "payment_history"] = summary
                cust_df.at[idx, "risk_category"] = risk_cat
            else:
                cust_df.at[idx, "on_time_probability"] = round(row["true_on_time_probability"], 2)
                cust_df.at[idx, "average_delay_days"] = round(row["true_average_delay_days"], 2)
                cust_df.at[idx, "historical_delay_count"] = 0
                cust_df.at[idx, "payment_history"] = "No payments generated"
                cust_df.at[idx, "risk_category"] = "MEDIUM"
                
        # Set derived properties on receivables
        cust_lookup = cust_df.set_index("customer_id")
        for i, rec in enumerate(self.receivables_raw):
            c_id = rec["customer_id"]
            stats = cust_lookup.loc[c_id]
            
            # Expected date is due date + derived delay
            derived_delay = int(stats["average_delay_days"])
            self.receivables_raw[i]["expected_date"] = rec["due_date"] + datetime.timedelta(days=derived_delay)
            self.receivables_raw[i]["collection_probability"] = float(stats["on_time_probability"])
            self.receivables_raw[i]["expected_delay_days"] = derived_delay
            
        cust_df = cust_df.drop(columns=["true_on_time_probability", "true_average_delay_days", "archetype", "payment_terms_days"])
        return cust_df

    def generate_events(self) -> pd.DataFrame:
        """
        Generates event logs with JSON payloads and processing statuses.
        """
        self.events_raw = []
        tx_df = pd.DataFrame(self.transactions_raw).sort_values("date")
        
        for idx, tx in tx_df.iterrows():
            event_id = f"EV_{len(self.events_raw)+1:05d}"
            tx_type = tx["type"]
            
            if tx_type == "CUSTOMER_PAYMENT":
                event_type = "RECEIVABLE_COLLECTED"
                payload = {"receivable_id": tx["reference_id"], "customer_id": tx["entity_id"] if "entity_id" in tx else "CUST001", "amount": tx["amount"]}
            elif tx_type == "SUPPLIER_PAYMENT":
                event_type = "SUPPLIER_INVOICE_PAID"
                payload = {"invoice_id": tx["reference_id"], "amount": tx["amount"]}
            elif tx_type == "UNEXPECTED_EXPENSE":
                event_type = "RECEIVABLE_DELAYED"
                payload = {"original_expected_date": tx["date"].strftime("%Y-%m-%d"), "delay_days": 10, "amount": tx["amount"]}
            elif tx_type == "LOAN_DRAW":
                event_type = "LIQUIDITY_CRUNCH_WARNING"
                payload = {"funding_facility": "FIN002", "amount": tx["amount"]}
            else:
                continue
                
            self.events_raw.append({
                "event_id": event_id,
                "company_id": "TATA001",
                "event_type": event_type,
                "payload": json.dumps(payload),
                "created_at": datetime.datetime.combine(tx["date"], datetime.time(10, 0, 0)),
                "processed_at": datetime.datetime.combine(tx["date"], datetime.time(10, 5, 0)),
                "status": "PROCESSED"
            })
            
        # Interest rate change event
        interest_change_date = config.START_DATE + datetime.timedelta(days=180)
        self.events_raw.append({
            "event_id": f"EV_{len(self.events_raw)+1:05d}",
            "company_id": "TATA001",
            "event_type": "INTEREST_RATE_CHANGED",
            "payload": json.dumps({"provider_id": "FIN002", "old_rate": 0.115, "new_rate": 0.125}),
            "created_at": datetime.datetime.combine(interest_change_date, datetime.time(9, 0, 0)),
            "processed_at": datetime.datetime.combine(interest_change_date, datetime.time(9, 1, 0)),
            "status": "PROCESSED"
        })
        
        return pd.DataFrame(self.events_raw)

    def generate_decisions(self) -> pd.DataFrame:
        """
        Generates historical decisions.
        """
        self.decisions_raw = []
        # We find dates where cash was low or critical expenses occurred
        daily_cash_df = self.generate_cash_accounts()
        low_cash_days = daily_cash_df[daily_cash_df["balance"] < 4500000.0]
        
        sample_low_days = low_cash_days["date"].values
        if len(sample_low_days) > 15:
            sample_low_days = sorted(random.sample(list(sample_low_days), 15))
            
        for i, d_date in enumerate(sample_low_days):
            if isinstance(d_date, np.datetime64):
                d_date = pd.to_datetime(d_date).date()
                
            self.decisions_raw.append({
                "decision_id": f"DEC_LOW_{i+1:03d}",
                "company_id": "TATA001",
                "created_at": d_date,
                "decision_type": "LIQUIDITY_MANAGEMENT",
                "chosen_action": "BANK_FINANCE",
                "confidence": 0.90,
                "reasoning": "Working capital reserve falls below safety margins. Earmarked LOC drawn to maintain supplier operations.",
                "status": "EXECUTED"
            })
            
        return pd.DataFrame(self.decisions_raw)

    def generate_decision_items(self) -> pd.DataFrame:
        """
        Creates mapping child records linked to specific decision entities.
        """
        self.decision_items_raw = []
        for dec in self.decisions_raw:
            dec_id = dec["decision_id"]
            self.decision_items_raw.append({
                "item_id": f"DITEM_{len(self.decision_items_raw)+1:04d}",
                "decision_id": dec_id,
                "invoice_id": "INV0001",
                "action": "FINANCE",
                "amount": 500000.0,
                "score": 85.0,
                "expected_cost": 4500.0,
                "expected_benefit": 15000.0,
                "risk_score": 12.0
            })
        return pd.DataFrame(self.decision_items_raw)

    def generate_decision_alternatives(self) -> pd.DataFrame:
        """
        Creates decision alternatives matrix for each decision log.
        """
        self.decision_alternatives_raw = []
        for dec in self.decisions_raw:
            dec_id = dec["decision_id"]
            options = ["Pay Now", "Pay at Maturity", "Bank Financing", "Supplier Financing", "Retain Cash"]
            for i, opt in enumerate(options):
                self.decision_alternatives_raw.append({
                    "alternative_id": f"ALT_{dec_id}_{i+1}",
                    "decision_id": dec_id,
                    "action": opt,
                    "score": round(random.uniform(0.60, 0.95), 2),
                    "cost": round(random.uniform(1000.0, 20000.0), 2),
                    "benefit": round(random.uniform(5000.0, 50000.0), 2),
                    "liquidity_impact": round(random.uniform(-100000.0, 100000.0), 2),
                    "risk": round(random.uniform(0.1, 0.5), 2)
                })
        return pd.DataFrame(self.decision_alternatives_raw)

    def generate_forecast_snapshots(self) -> pd.DataFrame:
        """
        Generates sample rolling forecast snapshots across the timeline.
        """
        self.forecast_snapshots_raw = []
        start_date = config.START_DATE
        num_days = config.NUM_DAYS
        
        # Create a snapshot every 15 days
        for i in range(0, num_days, 15):
            snap_date = start_date + datetime.timedelta(days=i)
            snap_id = f"SNAP_{i//15+1:03d}"
            
            # Draw realistic values
            projected_cash = float(np.random.normal(loc=12000000.0, scale=3000000.0))
            projected_cash = round(max(projected_cash, 2000000.0), 2)
            
            inflows = float(np.random.normal(loc=4000000.0, scale=1000000.0))
            outflows = float(np.random.normal(loc=3500000.0, scale=1000000.0))
            
            liq_risk = "LOW"
            if projected_cash < 5000000.0:
                liq_risk = "HIGH"
            elif projected_cash < 8000000.0:
                liq_risk = "MEDIUM"
                
            self.forecast_snapshots_raw.append({
                "snapshot_id": snap_id,
                "company_id": self.company_data.get("company_id", "TATA001"),
                "created_at": snap_date,
                "forecast_horizon_days": 30,
                "projected_cash": projected_cash,
                "minimum_projected_cash": round(projected_cash * 0.8, 2),
                "liquidity_risk": liq_risk,
                "expected_inflows": round(max(inflows, 500000.0), 2),
                "expected_outflows": round(max(outflows, 500000.0), 2),
                "reserve_requirement": config.MINIMUM_CASH_RESERVE,
                "risk_probability": round(0.15 if liq_risk == "LOW" else (0.45 if liq_risk == "MEDIUM" else 0.85), 2)
            })
            
        return pd.DataFrame(self.forecast_snapshots_raw)

    def generate_scenarios(self) -> pd.DataFrame:
        """
        Generates what-if scenarios mapping parameters to simulated outputs.
        """
        self.scenarios_raw = [
            {
                "scenario_id": "SCEN001",
                "company_id": "TATA001",
                "name": "Key Customer Payment Delay",
                "parameters": json.dumps({"customer_id": "CUST001", "delay_days": 15}),
                "result": json.dumps({
                    "liquidity_risk_before": "LOW",
                    "liquidity_risk_after": "HIGH",
                    "original_strategy": "Direct payment on due dates",
                    "new_strategy": "Draw ₹12.5L from LOC facility",
                    "capital_reallocation": 620000.0
                }),
                "created_at": config.START_DATE + datetime.timedelta(days=100)
            },
            {
                "scenario_id": "SCEN002",
                "company_id": "TATA001",
                "name": "LOC Financing Rate Spike",
                "parameters": json.dumps({"rate_increase": 0.02}),
                "result": json.dumps({
                    "liquidity_risk_before": "LOW",
                    "liquidity_risk_after": "LOW",
                    "original_strategy": "Maintain LOC term limits",
                    "new_strategy": "Shift early pay discount triggers",
                    "capital_reallocation": 0.0
                }),
                "created_at": config.START_DATE + datetime.timedelta(days=150)
            }
        ]
        return pd.DataFrame(self.scenarios_raw)

    def generate_all(self) -> Dict[str, Any]:
        """
        Executes the entire financial data generation workflow in proper dependency order.
        """
        company = self.generate_company()
        self.generate_customers()
        self.generate_suppliers()
        self.generate_financing_options()
        self.generate_receivables()
        self.generate_invoices()
        self.generate_obligations()
        
        # Populate history ledger
        self.generate_transactions()
        
        # Populate derived parameters
        customers_df = self.update_derived_customer_statistics()
        
        # Calculate daily cash account updates
        cash_df = self.generate_cash_accounts()
        
        # Other runtime metrics
        events_df = self.generate_events()
        decisions_df = self.generate_decisions()
        decision_items_df = self.generate_decision_items()
        decision_alts_df = self.generate_decision_alternatives()
        forecasts_df = self.generate_forecast_snapshots()
        scenarios_df = self.generate_scenarios()
        
        # Remove helper fields to matches pure schema outputs
        clean_receivables_df = pd.DataFrame(self.receivables_raw).drop(columns=["due_date", "simulated_delay"])
        clean_invoices_df = pd.DataFrame(self.invoices_raw).drop(columns=["due_date"])
        
        return {
            "company": company,
            "customers": customers_df,
            "suppliers": pd.DataFrame(self.suppliers_raw),
            "financing_options": pd.DataFrame(self.financing_options_raw),
            "receivables": clean_receivables_df,
            "invoices": clean_invoices_df,
            "obligations": pd.DataFrame(self.obligations_raw),
            "transactions": pd.DataFrame(self.transactions_raw),
            "cash_accounts": cash_df,
            "events": events_df,
            "decisions": decisions_df,
            "decision_items": decision_items_df,
            "decision_alternatives": decision_alts_df,
            "forecast_snapshots": forecasts_df,
            "scenarios": scenarios_df
        }

    def generate_future_data(self, num_days: int = 35) -> Dict[str, Any]:
        """
        Generates consistent future streaming financial data.
        """
        if not self.company_data:
            self.generate_all()
            
        start_future_date = config.START_DATE + datetime.timedelta(days=365)
        
        # Get last historical values
        last_cash = self.generate_cash_accounts().iloc[-1]["balance"]
        
        future_cash_accounts = []
        future_invoices = []
        future_receivables = []
        future_obligations = []
        future_transactions = []
        future_events = []
        future_decisions = []
        future_decision_items = []
        future_decision_alternatives = []
        future_forecast_snapshots = []
        
        cust_map = {c["customer_id"]: c for c in self.customers_raw}
        sup_map = {s["supplier_id"]: s for s in self.suppliers_raw}
        
        current_cash = last_cash
        
        for day in range(num_days):
            current_date = start_future_date + datetime.timedelta(days=day)
            
            day_inflow = 0.0
            day_outflow = 0.0
            day_txs = []
            day_events = []
            
            # 1. Collections from historical pending receivables due/paid today
            for rec in self.receivables_raw:
                if rec["status"] in ["PENDING", "OVERDUE"]:
                    if rec["actual_payment_date"] == current_date:
                        tx_id = f"TX_FUT_IN_HIST_{len(future_transactions)+len(day_txs)+1:05d}"
                        day_txs.append({
                            "transaction_id": tx_id,
                            "company_id": "TATA001",
                            "type": "CUSTOMER_PAYMENT",
                            "amount": rec["amount"],
                            "date": current_date,
                            "category": "CUSTOMER_COLLECTION",
                            "description": f"Collection of historical receivable {rec['receivable_id']}",
                            "reference_type": "RECEIVABLE",
                            "reference_id": rec["receivable_id"],
                            "status": "CLEARED"
                        })
                        day_inflow += rec["amount"]
                        
            # 2. Payments of historical pending supplier invoices paid today
            for inv in self.invoices_raw:
                if inv["status"] == "PENDING":
                    if inv["actual_payment_date"] == current_date:
                        tx_id = f"TX_FUT_OUT_HIST_{len(future_transactions)+len(day_txs)+1:05d}"
                        day_txs.append({
                            "transaction_id": tx_id,
                            "company_id": "TATA001",
                            "type": "SUPPLIER_PAYMENT",
                            "amount": inv["amount"],
                            "date": current_date,
                            "category": "RAW_MATERIAL",
                            "description": f"Payment of historical invoice {inv['invoice_id']}",
                            "reference_type": "INVOICE",
                            "reference_id": inv["invoice_id"],
                            "status": "CLEARED"
                        })
                        day_outflow += inv["amount"]

            # 3. Payments of historical pending obligations due today
            for obl in self.obligations_raw:
                if obl["status"] == "PENDING":
                    if obl["due_date"] == current_date:
                        tx_id = f"TX_FUT_OUT_HIST_{len(future_transactions)+len(day_txs)+1:05d}"
                        day_txs.append({
                            "transaction_id": tx_id,
                            "company_id": "TATA001",
                            "type": "OPERATING_EXPENSE",
                            "amount": obl["amount"],
                            "date": current_date,
                            "category": obl["category"],
                            "description": f"Payment of historical obligation {obl['obligation_id']}",
                            "reference_type": "OBLIGATION",
                            "reference_id": obl["obligation_id"],
                            "status": "CLEARED"
                        })
                        day_outflow += obl["amount"]

            # 4. Generate new future Customer Receivables (0 to 3 daily)
            new_rec_count = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]
            for _ in range(new_rec_count):
                rec_idx = len(self.receivables_raw) + len(future_receivables) + 1
                rec_id = f"REC_FUT_{rec_idx:04d}"
                customer = random.choice(self.customers_raw)
                
                amount = round(float(np.random.lognormal(mean=11.6, sigma=0.7)), 2)
                amount = min(max(amount, 30000.0), 3000000.0)
                
                due_date = current_date + datetime.timedelta(days=customer["payment_terms_days"])
                
                p_on_time = customer["true_on_time_probability"]
                avg_delay = customer["true_average_delay_days"]
                is_on_time = random.random() < p_on_time
                delay = random.randint(-5, 0) if is_on_time else int(np.random.exponential(scale=avg_delay)) + 1
                actual_payment_date = due_date + datetime.timedelta(days=delay)
                
                status = "PAID" if actual_payment_date <= (start_future_date + datetime.timedelta(days=num_days)) else "PENDING"
                
                new_rec = {
                    "receivable_id": rec_id,
                    "customer_id": customer["customer_id"],
                    "company_id": "TATA001",
                    "amount": amount,
                    "invoice_date": current_date,
                    "due_date": due_date,
                    "expected_date": due_date + datetime.timedelta(days=int(avg_delay)),
                    "collection_probability": round(float(p_on_time), 2),
                    "expected_delay_days": int(avg_delay),
                    "status": status,
                    "actual_payment_date": actual_payment_date if status == "PAID" else pd.NaT,
                    "simulated_delay": delay
                }
                future_receivables.append(new_rec)
                
                if status == "PAID" and actual_payment_date == current_date:
                    tx_id = f"TX_FUT_IN_{len(future_transactions)+len(day_txs)+1:05d}"
                    day_txs.append({
                        "transaction_id": tx_id,
                        "company_id": "TATA001",
                        "type": "CUSTOMER_PAYMENT",
                        "amount": amount,
                        "date": current_date,
                        "category": "CUSTOMER_COLLECTION",
                        "description": f"Payment received for future receivable {rec_id}",
                        "reference_type": "RECEIVABLE",
                        "reference_id": rec_id,
                        "status": "CLEARED"
                    })
                    day_inflow += amount

            # 5. Collect payments from previously created future receivables paid today
            for rec in future_receivables[:-new_rec_count if new_rec_count else None]:
                if rec["actual_payment_date"] == current_date:
                    tx_id = f"TX_FUT_IN_{len(future_transactions)+len(day_txs)+1:05d}"
                    day_txs.append({
                        "transaction_id": tx_id,
                        "company_id": "TATA001",
                        "type": "CUSTOMER_PAYMENT",
                        "amount": rec["amount"],
                        "date": current_date,
                        "category": "CUSTOMER_COLLECTION",
                        "description": f"Collection of future receivable {rec['receivable_id']}",
                        "reference_type": "RECEIVABLE",
                        "reference_id": rec["receivable_id"],
                        "status": "CLEARED"
                    })
                    day_inflow += rec["amount"]

            # 6. Generate new future Supplier Invoices (0 to 2 daily)
            new_inv_count = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
            for _ in range(new_inv_count):
                inv_idx = len(self.invoices_raw) + len(future_invoices) + 1
                inv_id = f"INV_FUT_{inv_idx:04d}"
                sup_id = random.choice(list(sup_map.keys()))
                supplier = sup_map[sup_id]
                
                amount = round(float(np.random.lognormal(mean=11.2, sigma=0.8)), 2)
                amount = min(max(amount, 15000.0), 2000000.0)
                
                due_date = current_date + datetime.timedelta(days=supplier["payment_terms_days"])
                
                discount_percentage = 0.0
                discount_deadline = pd.NaT
                if supplier["financing_available"] and random.random() < 0.4:
                    discount_percentage = random.choice([1.0, 2.0])
                    discount_deadline = current_date + datetime.timedelta(days=10)
                    
                actual_payment_date = due_date
                status = "PAID" if actual_payment_date <= (start_future_date + datetime.timedelta(days=num_days)) else "PENDING"
                
                new_inv = {
                    "invoice_id": inv_id,
                    "supplier_id": sup_id,
                    "company_id": "TATA001",
                    "amount": amount,
                    "issue_date": current_date,
                    "due_date": due_date,
                    "discount_percentage": discount_percentage,
                    "discount_deadline": discount_deadline if discount_percentage > 0 else pd.NaT,
                    "late_penalty_percentage": 2.0,
                    "currency": "INR",
                    "payment_method": "NEFT",
                    "status": status,
                    "actual_payment_date": actual_payment_date if status == "PAID" else pd.NaT
                }
                future_invoices.append(new_inv)
                
                if status == "PAID" and actual_payment_date == current_date:
                    tx_id = f"TX_FUT_OUT_{len(future_transactions)+len(day_txs)+1:05d}"
                    day_txs.append({
                        "transaction_id": tx_id,
                        "company_id": "TATA001",
                        "type": "SUPPLIER_PAYMENT",
                        "amount": amount,
                        "date": current_date,
                        "category": "RAW_MATERIAL",
                        "description": f"Payment made for future invoice {inv_id}",
                        "reference_type": "INVOICE",
                        "reference_id": inv_id,
                        "status": "CLEARED"
                    })
                    day_outflow += amount

            # 7. Collect payments from previously created future supplier invoices paid today
            for inv in future_invoices[:-new_inv_count if new_inv_count else None]:
                if inv["actual_payment_date"] == current_date:
                    tx_id = f"TX_FUT_OUT_{len(future_transactions)+len(day_txs)+1:05d}"
                    day_txs.append({
                        "transaction_id": tx_id,
                        "company_id": "TATA001",
                        "type": "SUPPLIER_PAYMENT",
                        "amount": inv["amount"],
                        "date": current_date,
                        "category": "RAW_MATERIAL",
                        "description": f"Payment cleared for future invoice {inv['invoice_id']}",
                        "reference_type": "INVOICE",
                        "reference_id": inv["invoice_id"],
                        "status": "CLEARED"
                    })
                    day_outflow += inv["amount"]

            # 8. Add recurring operating payments
            # Day 28: Payroll
            if current_date.day == 28:
                payroll_amount = 1650000.0
                tx_id = f"TX_FUT_OPS_{len(future_transactions)+len(day_txs)+1:05d}"
                day_txs.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "OPERATING_EXPENSE",
                    "amount": payroll_amount,
                    "date": current_date,
                    "category": "SALARY",
                    "description": "Corporate Employee Payroll",
                    "reference_type": "NONE",
                    "reference_id": np.nan,
                    "status": "CLEARED"
                })
                day_outflow += payroll_amount
                
            # Day 1: Rent
            if current_date.day == 1:
                rent_amount = 120000.0
                tx_id = f"TX_FUT_OPS_{len(future_transactions)+len(day_txs)+1:05d}"
                day_txs.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "OPERATING_EXPENSE",
                    "amount": rent_amount,
                    "date": current_date,
                    "category": "RENT",
                    "description": "Facility Rental Charge",
                    "reference_type": "NONE",
                    "reference_id": np.nan,
                    "status": "CLEARED"
                })
                day_outflow += rent_amount

            # 9. Liquidity buffer LOC support
            opening_balance = current_cash
            closing_balance = opening_balance + day_inflow - day_outflow
            
            if closing_balance < config.MINIMUM_CASH_RESERVE:
                draw_amount = max(config.MINIMUM_CASH_RESERVE - closing_balance + 500000.0, 500000.0)
                tx_id = f"TX_FUT_LOC_{len(future_transactions)+len(day_txs)+1:05d}"
                day_txs.append({
                    "transaction_id": tx_id,
                    "company_id": "TATA001",
                    "type": "LOAN_DRAW",
                    "amount": draw_amount,
                    "date": current_date,
                    "category": "EMI",
                    "description": "LOC drawdown to prevent safety reserve breach",
                    "reference_type": "NONE",
                    "reference_id": np.nan,
                    "status": "CLEARED"
                })
                day_inflow += draw_amount
                closing_balance += draw_amount
                
                day_events.append({
                    "event_id": f"EV_FUT_{len(future_events)+len(day_events)+1:05d}",
                    "company_id": "TATA001",
                    "event_type": "LIQUIDITY_CRUNCH_WARNING",
                    "payload": json.dumps({"funding_facility": "FIN002", "amount": draw_amount}),
                    "created_at": datetime.datetime.combine(current_date, datetime.time(16, 0, 0)),
                    "processed_at": datetime.datetime.combine(current_date, datetime.time(16, 1, 0)),
                    "status": "PROCESSED"
                })
                
            # Available balance
            available_balance = max(closing_balance - config.MINIMUM_CASH_RESERVE, 0.0)
            
            # Dynamically calculate future reserved balance
            # For simplicity, we check upcoming obligations in our future obligations and recurring items
            # Within next 7 days: Rent (if day is 22-30), Payroll (if day is 21-27), utilities, plus any pending AP supplier invoices
            reserved_balance = 850000.0 # Baseline future reserve buffer
            if current_date.day >= 21 and current_date.day <= 27:
                reserved_balance += 1650000.0 # Salary block
            elif current_date.day >= 25 or current_date.day <= 1:
                reserved_balance += 120000.0 # Rent block
                
            deployable_cash = max(available_balance - reserved_balance, 0.0)
            
            # Commit daily record
            cash_rec = {
                "date": current_date,
                "company_id": "TATA001",
                "cash_account_id": "CASH001",
                "opening_balance": round(opening_balance, 2),
                "daily_inflow": round(day_inflow, 2),
                "daily_outflow": round(day_outflow, 2),
                "balance": round(closing_balance, 2),
                "available_balance": round(available_balance, 2),
                "reserved_balance": round(reserved_balance, 2),
                "deployable_cash": round(deployable_cash, 2)
            }
            future_cash_accounts.append(cash_rec)
            current_cash = closing_balance
            future_transactions.extend(day_txs)
            future_events.extend(day_events)
            
            # Create a forecast snapshot every 15 days
            if day % 15 == 0:
                snap_id = f"SNAP_FUT_{day//15+1:03d}"
                projected = float(closing_balance)
                inflow_exp = float(np.random.normal(loc=1500000.0, scale=300000.0))
                outflow_exp = float(np.random.normal(loc=1200000.0, scale=300000.0))
                liq_risk = "LOW" if projected >= 8000000.0 else ("MEDIUM" if projected >= 5000000.0 else "HIGH")
                future_forecast_snapshots.append({
                    "snapshot_id": snap_id,
                    "company_id": "TATA001",
                    "created_at": current_date,
                    "forecast_horizon_days": 30,
                    "projected_cash": round(projected, 2),
                    "minimum_projected_cash": round(projected * 0.8, 2),
                    "liquidity_risk": liq_risk,
                    "expected_inflows": round(max(inflow_exp, 500000.0), 2),
                    "expected_outflows": round(max(outflow_exp, 500000.0), 2),
                    "reserve_requirement": config.MINIMUM_CASH_RESERVE,
                    "risk_probability": round(0.15 if liq_risk == "LOW" else (0.45 if liq_risk == "MEDIUM" else 0.85), 2)
                })

            # Create a sample decision when cash is low
            if closing_balance < 4500000.0 and random.random() < 0.2:
                dec_id = f"DEC_FUT_{len(future_decisions)+1:03d}"
                future_decisions.append({
                    "decision_id": dec_id,
                    "company_id": "TATA001",
                    "created_at": current_date,
                    "decision_type": "LIQUIDITY_MANAGEMENT",
                    "chosen_action": "BANK_FINANCE",
                    "confidence": 0.92,
                    "reasoning": "Future working capital tight. LOC drawn to maintain buffer.",
                    "status": "EXECUTED"
                })
                future_decision_items.append({
                    "item_id": f"DITEM_FUT_{len(future_decision_items)+1:04d}",
                    "decision_id": dec_id,
                    "invoice_id": "INV_FUT_0001",
                    "action": "FINANCE",
                    "amount": 500000.0,
                    "score": 88.0,
                    "expected_cost": 4500.0,
                    "expected_benefit": 15000.0,
                    "risk_score": 10.0
                })
                options = ["Pay Now", "Pay at Maturity", "Bank Financing", "Supplier Financing", "Retain Cash"]
                for i, opt in enumerate(options):
                    future_decision_alternatives.append({
                        "alternative_id": f"ALT_FUT_{dec_id}_{i+1}",
                        "decision_id": dec_id,
                        "action": opt,
                        "score": round(random.uniform(0.60, 0.95), 2),
                        "cost": round(random.uniform(1000.0, 20000.0), 2),
                        "benefit": round(random.uniform(5000.0, 50000.0), 2),
                        "liquidity_impact": round(random.uniform(-100000.0, 100000.0), 2),
                        "risk": round(random.uniform(0.1, 0.5), 2)
                    })
            
        future_receivables_clean = pd.DataFrame(future_receivables).drop(columns=["due_date", "simulated_delay"])
        future_invoices_clean = pd.DataFrame(future_invoices).drop(columns=["due_date"])
        
        return {
            "cash_accounts": pd.DataFrame(future_cash_accounts),
            "invoices": future_invoices_clean,
            "receivables": future_receivables_clean,
            "obligations": pd.DataFrame(future_obligations),
            "transactions": pd.DataFrame(future_transactions),
            "events": pd.DataFrame(future_events),
            "decisions": pd.DataFrame(future_decisions),
            "decision_items": pd.DataFrame(future_decision_items),
            "decision_alternatives": pd.DataFrame(future_decision_alternatives),
            "forecast_snapshots": pd.DataFrame(future_forecast_snapshots)
        }

    def stream_future_data(self, num_days: int = 35) -> Generator[Dict[str, Any], None, None]:
        """
        Yields future financial snapshots daily.
        """
        future_data = self.generate_future_data(num_days=num_days)
        
        cash_accounts = future_data["cash_accounts"]
        invoices = future_data["invoices"]
        receivables = future_data["receivables"]
        obligations = future_data["obligations"]
        transactions = future_data["transactions"]
        events = future_data["events"]
        
        for idx in range(num_days):
            current_row = cash_accounts.iloc[idx]
            current_date = current_row["date"]
            
            day_invoices = invoices[invoices["issue_date"] == current_date]
            day_obligations = obligations[obligations["issue_date"] == current_date] if len(obligations) > 0 else pd.DataFrame()
            day_transactions = transactions[transactions["date"] == current_date]
            if not events.empty and "created_at" in events.columns:
                day_events = events[events["created_at"].apply(lambda t: pd.to_datetime(t).date() == current_date)]
            else:
                day_events = pd.DataFrame(columns=["event_id", "company_id", "event_type", "payload", "created_at", "processed_at", "status"])
            
            active_recs = receivables[
                (receivables["invoice_date"] <= current_date) & 
                (receivables["actual_payment_date"].apply(
                    lambda val: (val.date() if hasattr(val, "date") else val) > current_date if pd.notna(val) else True
                ))
            ]
            
            yield {
                "date": current_date,
                "cash_account": current_row.to_dict(),
                "new_invoices": day_invoices.to_dict(orient="records"),
                "new_obligations": day_obligations.to_dict(orient="records") if not day_obligations.empty else [],
                "transactions": day_transactions.to_dict(orient="records"),
                "receivables": active_recs.to_dict(orient="records"),
                "events": day_events.to_dict(orient="records")
            }

    def save_to_csv(self, data: Dict[str, Any], output_dir: str = "data"):
        """
        Saves all generated DataFrames to CSV files.
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save company config as JSON
        if "company" in data:
            company_path = os.path.join(output_dir, "company.json")
            with open(company_path, "w", encoding="utf-8") as f:
                json.dump(data["company"], f, indent=4)
            print(f"Saved company configuration to: {company_path}")
            
        for key, value in data.items():
            if key == "company":
                continue
            if isinstance(value, pd.DataFrame):
                csv_path = os.path.join(output_dir, f"{key}.csv")
                value.to_csv(csv_path, index=False, encoding="utf-8")
                print(f"Saved {key} DataFrame to: {csv_path}")

    def compile_daily_consolidated(self, cash_accounts: pd.DataFrame, invoices: pd.DataFrame, 
                                 obligations: pd.DataFrame, transactions: pd.DataFrame, 
                                 events: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates transaction ledger, invoice registry, obligations, and events 
        into a single, consolidated daily time-series DataFrame.
        """
        cash_df = cash_accounts.copy()
        cash_df["date"] = pd.to_datetime(cash_df["date"]).dt.date
        
        # 1. Aggregate Invoices (AP Bills Created)
        inv_df = invoices.copy()
        inv_df["issue_date"] = pd.to_datetime(inv_df["issue_date"]).dt.date
        inv_agg = inv_df.groupby("issue_date").agg(
            invoices_created_count=("invoice_id", "count"),
            invoices_created_amount=("amount", "sum")
        ).reset_index().rename(columns={"issue_date": "date"})
        
        # 2. Aggregate Obligations (Earmarked Payables Issued)
        obl_agg = pd.DataFrame(columns=["date", "obligations_created_count", "obligations_created_amount"])
        if len(obligations) > 0:
            obl_df = obligations.copy()
            obl_df["due_date"] = pd.to_datetime(obl_df["due_date"]).dt.date
            obl_agg = obl_df.groupby("due_date").agg(
                obligations_created_count=("obligation_id", "count"),
                obligations_created_amount=("amount", "sum")
            ).reset_index().rename(columns={"due_date": "date"})
        
        # 3. Aggregate Transactions from Ledger
        tx_df = transactions.copy()
        tx_df["date"] = pd.to_datetime(tx_df["date"]).dt.date
        
        tx_pivot = pd.DataFrame()
        if len(tx_df) > 0:
            tx_pivot = tx_df.groupby(["date", "type"]).agg(
                amount=("amount", "sum"),
                count=("transaction_id", "count")
            ).unstack(fill_value=0.0)
            
            # Flatten column index
            tx_pivot.columns = [f"{col[1].lower()}_{col[0]}" for col in tx_pivot.columns]
            tx_pivot = tx_pivot.reset_index()
            
        expected_cols = []
        for t in ["CUSTOMER_PAYMENT", "SUPPLIER_PAYMENT", "OPERATING_EXPENSE", 
                  "UNEXPECTED_EXPENSE", "LOAN_DRAW", "LOAN_REPAYMENT", "INTEREST_PAYMENT"]:
            expected_cols.append(f"{t.lower()}_amount")
            expected_cols.append(f"{t.lower()}_count")
            
        for col in expected_cols:
            if tx_pivot.empty or col not in tx_pivot.columns:
                tx_pivot[col] = 0.0
                
        if tx_pivot.empty:
            tx_pivot["date"] = cash_df["date"]
        
        # 4. Aggregate Events
        ev_agg = pd.DataFrame(columns=["date", "events_logged_count"])
        if len(events) > 0:
            ev_df = events.copy()
            ev_df["date"] = pd.to_datetime(ev_df["created_at"]).dt.date
            ev_agg = ev_df.groupby("date").agg(
                events_logged_count=("event_id", "count")
            ).reset_index()
        
        # Merge all
        consolidated = cash_df.merge(inv_agg, on="date", how="left")
        consolidated = consolidated.merge(obl_agg, on="date", how="left")
        consolidated = consolidated.merge(tx_pivot, on="date", how="left")
        consolidated = consolidated.merge(ev_agg, on="date", how="left")
        
        fill_cols = [c for c in consolidated.columns if c not in ["date", "company_id", "cash_account_id"]]
        consolidated[fill_cols] = consolidated[fill_cols].fillna(0.0)
        
        return consolidated
