import os
import pandas as pd
from typing import Dict, List

HISTORICAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "historical_data_cashpilot", "data", "historical"))
FUTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data"))
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))

def merge_csv_files():
    print("Merging small CSV files across historical and future dataset directories...")

    csv_tables = [
        "invoices.csv",
        "receivables.csv",
        "cash_accounts.csv",
        "suppliers.csv",
        "obligations.csv",
        "transactions.csv",
        "decisions.csv"
    ]

    all_master_rows = []

    # 1. Merge each individual CSV table across historical and future folders
    for table_name in csv_tables:
        hist_path = os.path.join(HISTORICAL_DIR, table_name)
        fut_path = os.path.join(FUTURE_DIR, table_name)

        dfs = []
        if os.path.exists(hist_path):
            try:
                df_hist = pd.read_csv(hist_path)
                df_hist["data_source"] = "HISTORICAL"
                dfs.append(df_hist)
            except Exception as e:
                print(f"Error reading {hist_path}: {e}")

        if os.path.exists(fut_path):
            try:
                df_fut = pd.read_csv(fut_path)
                df_fut["data_source"] = "FUTURE_STREAMING"
                dfs.append(df_fut)
            except Exception as e:
                print(f"Error reading {fut_path}: {e}")

        if dfs:
            merged_table_df = pd.concat(dfs, ignore_index=True)
            out_table_path = os.path.join(BACKEND_DIR, f"merged_{table_name}")
            merged_table_df.to_csv(out_table_path, index=False)
            print(f"Saved merged entity table: merged_{table_name} ({len(merged_table_df)} rows)")

            # Add to master unified CSV rows
            for _, row in merged_table_df.iterrows():
                row_dict = row.to_dict()
                
                # Normalize key fields for single master CSV
                entity_id = row_dict.get("invoice_id") or row_dict.get("receivable_id") or row_dict.get("supplier_id") or row_dict.get("cash_account_id") or row_dict.get("decision_id") or row_dict.get("obligation_id") or "N/A"
                date_val = row_dict.get("issue_date") or row_dict.get("expected_date") or row_dict.get("date") or row_dict.get("due_date") or row_dict.get("timestamp") or "N/A"
                amount_val = row_dict.get("amount") or row_dict.get("balance") or row_dict.get("allocated_amount") or 0.0

                master_entry = {
                    "record_type": table_name.replace(".csv", "").upper(),
                    "entity_id": entity_id,
                    "company_id": row_dict.get("company_id", "TATA001"),
                    "supplier_id": row_dict.get("supplier_id", ""),
                    "customer_id": row_dict.get("customer_id", ""),
                    "date": date_val,
                    "amount": amount_val,
                    "status": row_dict.get("status", "ACTIVE"),
                    "data_source": row_dict.get("data_source", "MERGED"),
                    "details": str(row_dict)
                }
                all_master_rows.append(master_entry)

    # 2. Add future_daily_consolidated.csv to master
    fut_daily_path = os.path.join(FUTURE_DIR, "future_daily_consolidated.csv")
    if os.path.exists(fut_daily_path):
        df_daily = pd.read_csv(fut_daily_path)
        df_daily["data_source"] = "FUTURE_STREAMING"
        df_daily.to_csv(os.path.join(BACKEND_DIR, "merged_future_daily_consolidated.csv"), index=False)
        print(f"Saved merged_future_daily_consolidated.csv ({len(df_daily)} rows)")

        for _, row in df_daily.iterrows():
            row_dict = row.to_dict()
            all_master_rows.append({
                "record_type": "FUTURE_DAILY_CONSOLIDATED",
                "entity_id": f"DAILY-{row_dict.get('date')}",
                "company_id": row_dict.get("company_id", "TATA001"),
                "supplier_id": "",
                "customer_id": "",
                "date": row_dict.get("date"),
                "amount": row_dict.get("balance"),
                "status": "SIMULATED",
                "data_source": "FUTURE_STREAMING",
                "details": str(row_dict)
            })

    # 3. Create SINGLE UNIFIED MASTER CSV FILE
    master_df = pd.DataFrame(all_master_rows)
    master_csv_path = os.path.join(BACKEND_DIR, "cashpilot_merged_master_dataset.csv")
    master_df.to_csv(master_csv_path, index=False)
    print(f"\nSUCCESS! Created Single Master Merged CSV File at: {master_csv_path} ({len(master_df)} total records)")

if __name__ == "__main__":
    merge_csv_files()
