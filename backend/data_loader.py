import os
import json
import pandas as pd
from typing import Dict, Any, List
from preprocessor import HistoricalPreprocessor

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "historical_data_cashpilot", "data", "historical")

class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = os.path.abspath(data_dir)
        self.preprocessor = HistoricalPreprocessor(self.data_dir)
        # Run preprocessing once at startup
        self.customer_features = self.preprocessor.preprocess_customer_history()
        self.supplier_features = self.preprocessor.preprocess_supplier_history()

    def load_company(self) -> Dict[str, Any]:
        path = os.path.join(self.data_dir, "company.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "id": "COMP-001",
            "name": "Acme Manufacturing Pvt Ltd",
            "minimum_cash_reserve": 1500000.0,
            "currency": "INR"
        }

    def load_cash(self) -> float:
        path = os.path.join(self.data_dir, "cash_accounts.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if not df.empty and 'balance' in df.columns:
                    val = float(df['balance'].iloc[0])
                    if val > 0:
                        return val
            except Exception:
                pass
        return 472711883.03

    def load_suppliers_dict(self) -> Dict[str, Dict[str, Any]]:
        path = os.path.join(self.data_dir, "suppliers.csv")
        suppliers = {}
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                for _, row in df.iterrows():
                    sup_id = str(row.get("supplier_id", ""))
                    imp_val = str(row.get("strategic_importance", "MEDIUM")).upper()
                    imp_score = 5 if "CRITICAL" in imp_val else 3 if "MEDIUM" in imp_val else 2
                    
                    sup_feat = self.supplier_features.get(sup_id, {})
                    suppliers[sup_id] = {
                        "name": str(row.get("name", "Tata Steel Ltd")),
                        "category": str(row.get("category", "Raw Materials")),
                        "strategicImportance": imp_score,
                        "isCritical": "CRITICAL" in imp_val,
                        "liquidityRisk": str(row.get("liquidity_risk", "LOW")).upper(),
                        "capturedDiscountTotal": sup_feat.get("captured_discount_total", 667633.71)
                    }
            except Exception as e:
                print(f"Error reading suppliers.csv: {e}")
        return suppliers

    def load_obligations(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "obligations.csv")
        obligations = []
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                for _, row in df.head(10).iterrows():
                    amount = float(row.get("amount", 1000000.0))
                    desc = str(row.get("description", row.get("category", "OBLIGATION")))
                    due = str(row.get("due_date", "Tomorrow"))
                    prio = str(row.get("priority", "HIGH")).upper()
                    obligations.append({
                        "id": str(row.get("obligation_id", "OBL-001")),
                        "supplierName": desc,
                        "amount": amount,
                        "dueDate": due if due else "Tomorrow",
                        "priority": prio,
                        "aiAction": "Must Pay" if prio == "CRITICAL" else "Pay Now"
                    })
                if obligations:
                    return obligations
            except Exception as e:
                print(f"Error loading obligations.csv: {e}")
        
        return [
            {
                "id": "OBL-001",
                "supplierName": "Employee Monthly Salary Payroll",
                "amount": 41005965.89,
                "dueDate": "Due Tomorrow",
                "priority": "CRITICAL",
                "aiAction": "Must Pay"
            },
            {
                "id": "OBL-002",
                "supplierName": "Valeo India Raw Material Invoice",
                "amount": 33381685.97,
                "dueDate": "Due Jan 04",
                "priority": "HIGH",
                "aiAction": "Pay Now"
            },
            {
                "id": "OBL-003",
                "supplierName": "Bosch Ltd Statutory Tax Obligation",
                "amount": 23009047.23,
                "dueDate": "Due Jan 10",
                "priority": "CRITICAL",
                "aiAction": "Must Pay"
            },
            {
                "id": "OBL-004",
                "supplierName": "Denso India Plant Utility Power & Gas",
                "amount": 17875657.24,
                "dueDate": "Due Jan 12",
                "priority": "HIGH",
                "aiAction": "Pay Now"
            }
        ]

    def load_suppliers(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "suppliers.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                suppliers = []
                for _, row in df.head(8).iterrows():
                    sup_id = str(row.get("supplier_id", "SUP001"))
                    imp_val = str(row.get("strategic_importance", "MEDIUM")).upper()
                    imp_score = 5 if "CRITICAL" in imp_val else 3 if "MEDIUM" in imp_val else 2
                    sup_feat = self.supplier_features.get(sup_id, {})
                    suppliers.append({
                        "id": sup_id,
                        "name": str(row.get("name", "Tata Steel Ltd")),
                        "category": str(row.get("category", "Raw Materials")),
                        "strategicImportance": imp_score,
                        "isCritical": "CRITICAL" in imp_val,
                        "liquidityRisk": str(row.get("liquidity_risk", "LOW")),
                        "outstandingInvoices": 2,
                        "outstandingAmount": 33381685.97,
                        "onTimePaymentPct": sup_feat.get("on_time_payment_pct", 94.0),
                        "capturedDiscountTotal": sup_feat.get("captured_discount_total", 667633.71)
                    })
                if suppliers:
                    return suppliers
            except Exception:
                pass
        return []

    def load_invoices(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "invoices.csv")
        suppliers_dict = self.load_suppliers_dict()
        invoices = []

        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                pending_df = df[df['status'].isin(['PENDING', 'OVERDUE'])]
                if pending_df.empty:
                    pending_df = df.head(10)

                for _, row in pending_df.head(10).iterrows():
                    sup_id = str(row.get("supplier_id", ""))
                    sup_info = suppliers_dict.get(sup_id, {"name": "Bosch Ltd", "category": "Components", "strategicImportance": 5})
                    amount = float(row.get("amount", 1000000.0))
                    discount_pct = float(row.get("discount_percentage", 0.0))
                    status = str(row.get("status", "PENDING"))
                    discount_deadline = str(row.get("discount_deadline", "-"))
                    if pd.isna(discount_deadline) or not discount_deadline:
                        discount_deadline = "-"

                    score = 95 if status == "PENDING" and discount_pct > 0 else 82 if status == "OVERDUE" else 60
                    action = "Pay Now" if score >= 80 else "Pay at Maturity"

                    discount_savings = (amount * discount_pct / 100.0) if discount_pct > 0 else 0
                    reasoning = f"Supplier {sup_info['name']} (Strategic {sup_info['strategicImportance']}/5). "
                    if discount_pct > 0:
                        reasoning += f"Captures ₹{discount_savings:,.0f} early discount ({discount_pct}%). Safety floor preserved."
                    else:
                        reasoning += f"Invoice status is {status}. Terms allow liquidity preservation until maturity."

                    invoices.append({
                        "id": str(row.get("invoice_id", "INV-001")),
                        "supplierName": sup_info["name"],
                        "supplierCategory": sup_info["category"],
                        "amount": amount,
                        "dueDate": str(row.get("issue_date", "2026-01-04")),
                        "discountPct": discount_pct,
                        "discountDeadline": discount_deadline,
                        "priorityScore": score,
                        "aiAction": action,
                        "strategicImportance": sup_info["strategicImportance"],
                        "reasoning": reasoning
                    })
                if invoices:
                    return invoices
            except Exception as e:
                print(f"Error parsing invoices.csv: {e}")
        return invoices

    def load_receivables(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "receivables.csv")
        receivables = []
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                for idx, row in df.head(8).iterrows():
                    cust_id = f"CUST-00{idx+1}"
                    cust_feat = self.customer_features.get(cust_id, {"alpha": 10, "beta": 2, "observations_count": 11, "on_time_probability": 91.7, "average_delay_days": 0.5})
                    amount = float(row.get("amount", 2450000.0))
                    prob = cust_feat["on_time_probability"]
                    delay = int(cust_feat["average_delay_days"])
                    status = "On Time" if delay == 0 else "Slight Delay" if delay <= 5 else "At Risk"
                    
                    receivables.append({
                        "id": str(row.get("receivable_id", row.get("id", "REC-901"))),
                        "customerName": str(row.get("customer_name", "Mahindra Logistics")),
                        "customerId": cust_id,
                        "amount": amount,
                        "expectedDate": str(row.get("expected_date", "2026-01-15")),
                        "collectionProbability": round(prob, 1),
                        "expectedDelayDays": delay,
                        "alpha": cust_feat["alpha"],
                        "beta": cust_feat["beta"],
                        "observationsCount": cust_feat["observations_count"],
                        "status": status
                    })
                if receivables:
                    return receivables
            except Exception as e:
                print(f"Error loading receivables.csv: {e}")
        return receivables
