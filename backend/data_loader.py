import os
import json
import pandas as pd
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "historical_data_cashpilot", "data", "historical")

class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = os.path.abspath(data_dir)

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
        return 4820000.0

    def load_suppliers(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "suppliers.csv")
        default_suppliers = [
            {
                "id": "SUP-01",
                "name": "Tata Steel Processing",
                "category": "Raw Materials",
                "strategicImportance": 5,
                "isCritical": True,
                "liquidityRisk": "LOW",
                "outstandingInvoices": 2,
                "outstandingAmount": 1450000.0,
                "onTimePaymentPct": 98.0,
                "capturedDiscountTotal": 142000.0
            },
            {
                "id": "SUP-02",
                "name": "Apex Electronics Logistics",
                "category": "Supply Chain",
                "strategicImportance": 4,
                "isCritical": True,
                "liquidityRisk": "LOW",
                "outstandingInvoices": 1,
                "outstandingAmount": 580000.0,
                "onTimePaymentPct": 94.0,
                "capturedDiscountTotal": 54000.0
            },
            {
                "id": "SUP-03",
                "name": "Zenith Packaging Corp",
                "category": "Packaging",
                "strategicImportance": 3,
                "isCritical": False,
                "liquidityRisk": "MEDIUM",
                "outstandingInvoices": 1,
                "outstandingAmount": 1250000.0,
                "onTimePaymentPct": 88.0,
                "capturedDiscountTotal": 37500.0
            },
            {
                "id": "SUP-04",
                "name": "Reliance Polymers",
                "category": "Raw Materials",
                "strategicImportance": 2,
                "isCritical": False,
                "liquidityRisk": "HIGH",
                "outstandingInvoices": 1,
                "outstandingAmount": 850000.0,
                "onTimePaymentPct": 81.0,
                "capturedDiscountTotal": 12000.0
            }
        ]

        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                suppliers = []
                for _, row in df.head(6).iterrows():
                    imp_val = str(row.get("strategic_importance", "MEDIUM")).upper()
                    imp_score = 5 if "CRITICAL" in imp_val else 3 if "MEDIUM" in imp_val else 2
                    is_critical = "CRITICAL" in imp_val
                    risk_val = str(row.get("liquidity_risk", "LOW")).upper()

                    suppliers.append({
                        "id": str(row.get("supplier_id", row.get("id", "SUP-01"))),
                        "name": str(row.get("name", "Tata Steel Processing")),
                        "category": str(row.get("category", "Raw Materials")),
                        "strategicImportance": imp_score,
                        "isCritical": is_critical,
                        "liquidityRisk": risk_val if risk_val in ["LOW", "MEDIUM", "HIGH"] else "LOW",
                        "outstandingInvoices": 2,
                        "outstandingAmount": 1450000.0,
                        "onTimePaymentPct": 94.0,
                        "capturedDiscountTotal": 125000.0
                    })
                return suppliers if suppliers else default_suppliers
            except Exception as e:
                print(f"Error loading suppliers CSV: {e}")
        return default_suppliers

    def load_invoices(self) -> List[Dict[str, Any]]:
        default_invoices = [
            {
                "id": "INV-2026-081",
                "supplierName": "Tata Steel Processing",
                "supplierCategory": "Raw Materials",
                "amount": 920000.0,
                "dueDate": "2026-09-05",
                "discountPct": 2.5,
                "discountDeadline": "2026-08-30",
                "priorityScore": 96,
                "aiAction": "Pay Now",
                "strategicImportance": 5,
                "reasoning": "Strategic Tier-1 supplier. Captures ₹23,000 discount (32.4% annualized return). Buffer exceeds ₹15L safety floor."
            },
            {
                "id": "INV-2026-084",
                "supplierName": "Apex Electronics Logistics",
                "supplierCategory": "Supply Chain",
                "amount": 580000.0,
                "dueDate": "2026-09-02",
                "discountPct": 1.8,
                "discountDeadline": "2026-08-31",
                "priorityScore": 89,
                "aiAction": "Pay Now",
                "strategicImportance": 4,
                "reasoning": "Prevents freight dispatch hold for upcoming Q3 delivery. 1.8% early payment discount captures ₹10,440."
            },
            {
                "id": "INV-2026-089",
                "supplierName": "Infosys Cloud Operations",
                "supplierCategory": "IT Infrastructure",
                "amount": 340000.0,
                "dueDate": "2026-09-20",
                "discountPct": 0.0,
                "discountDeadline": "-",
                "priorityScore": 42,
                "aiAction": "Pay at Maturity",
                "strategicImportance": 3,
                "reasoning": "No early settlement discount offered. Net 30 terms allow liquidity preservation until day 28."
            },
            {
                "id": "INV-2026-092",
                "supplierName": "Zenith Packaging Corp",
                "supplierCategory": "Packaging",
                "amount": 1250000.0,
                "dueDate": "2026-09-10",
                "discountPct": 3.0,
                "discountDeadline": "2026-08-29",
                "priorityScore": 78,
                "aiAction": "Finance",
                "strategicImportance": 3,
                "reasoning": "Preserves internal cash while securing 3.0% discount via Dynamic Supplier Discounting at 8.5% APR."
            },
            {
                "id": "INV-2026-095",
                "supplierName": "Reliance Polymers",
                "supplierCategory": "Raw Materials",
                "amount": 850000.0,
                "dueDate": "2026-09-15",
                "discountPct": 0.0,
                "discountDeadline": "-",
                "priorityScore": 31,
                "aiAction": "Delay",
                "strategicImportance": 2,
                "reasoning": "Receivable delay from Client Beta risks temporary liquidity dip on Sept 8th. Payment scheduled for Sept 18th."
            }
        ]
        return default_invoices

    def load_receivables(self) -> List[Dict[str, Any]]:
        default_receivables = [
            {
                "id": "REC-901",
                "customerName": "Mahindra Logistics",
                "amount": 2450000.0,
                "expectedDate": "2026-08-30",
                "collectionProbability": 95.0,
                "expectedDelayDays": 0,
                "status": "On Time"
            },
            {
                "id": "REC-904",
                "customerName": "Flipkart Fulfillment",
                "amount": 1800000.0,
                "expectedDate": "2026-09-04",
                "collectionProbability": 82.0,
                "expectedDelayDays": 3,
                "status": "Slight Delay"
            },
            {
                "id": "REC-908",
                "customerName": "Bajaj Auto Ancillaries",
                "amount": 1200000.0,
                "expectedDate": "2026-09-12",
                "collectionProbability": 64.0,
                "expectedDelayDays": 9,
                "status": "At Risk"
            }
        ]
        return default_receivables
