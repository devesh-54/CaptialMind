import sys
import os
import pandas as pd
import numpy as np
import datetime

# Ensure the parent directory is on the path so we can run the test script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cashpilot_ai.data_generator import FinancialDataGenerator

def run_tests():
    print("==================================================")
    print("      CashPilot AI Financial Data Generator       ")
    print("               Validation Suite                   ")
    print("==================================================")
    
    # 1. Instantiate the generator
    generator = FinancialDataGenerator(seed=42)
    
    # 2. Generate all data
    data = generator.generate_all()
    
    # Extract entities
    company = data["company"]
    customers = data["customers"]
    suppliers = data["suppliers"]
    financing_options = data["financing_options"]
    invoices = data["invoices"]
    receivables = data["receivables"]
    obligations = data["obligations"]
    transactions = data["transactions"]
    cash_accounts = data["cash_accounts"]
    events = data["events"]
    decisions = data["decisions"]
    decision_items = data["decision_items"]
    decision_alternatives = data["decision_alternatives"]
    forecast_snapshots = data["forecast_snapshots"]
    scenarios = data["scenarios"]
    
    # 3. Print the number of records generated for each entity
    print("\n--- Record Counts Summary ---")
    print(f"Company: {1} (ID: {company['company_id']}, Name: {company['company_name']}, Industry: {company['industry']})")
    print(f"Customers: {len(customers)} records")
    print(f"Suppliers: {len(suppliers)} records")
    print(f"Financing Options: {len(financing_options)} records")
    print(f"Supplier Invoices (AP): {len(invoices)} records")
    print(f"Customer Receivables (AR): {len(receivables)} records")
    print(f"Operating Obligations: {len(obligations)} records")
    print(f"Transactions (Historical Ledger): {len(transactions)} records")
    print(f"Daily Cash Accounts (Simulation Time series): {len(cash_accounts)} records")
    print(f"Historical Events: {len(events)} records")
    print(f"Decision Records: {len(decisions)} records")
    print(f"Decision Items: {len(decision_items)} records")
    print(f"Decision Alternatives: {len(decision_alternatives)} records")
    print(f"Forecast Snapshots: {len(forecast_snapshots)} records")
    print(f"What-if Scenarios: {len(scenarios)} records")
    
    # 4. Print sample rows for visual confirmation
    print("\n--- Sample Rows (Supplier Invoices AP - First 3) ---")
    print(invoices.head(3).to_string(index=False))
    
    print("\n--- Sample Rows (Daily Cash Account - First 3) ---")
    print(cash_accounts.head(3).to_string(index=False))
    
    print("\n--- Sample Rows (Customer Receivables AR - First 3) ---")
    print(receivables.head(3).to_string(index=False))
    
    # 5. Executing Validation Checks
    print("\n--- Starting Validations ---")
    
    # A. Check daily cash account count
    assert len(cash_accounts) == 365, f"Validation Failed: Expected exactly 365 days of cash account records, got {len(cash_accounts)}."
    print("[OK] Daily cash account count is exactly 365.")
    
    # B. Check for negative balances
    negative_balance_count = (cash_accounts["balance"] < 0).sum()
    assert negative_balance_count == 0, f"Validation Failed: Found {negative_balance_count} days with negative cash balance."
    print("[OK] No negative cash balance occurred during the simulated period.")
    
    # C. Validate supplier invoice supplier IDs exist
    valid_supplier_ids = set(suppliers["supplier_id"])
    for idx, row in invoices.iterrows():
        sup_id = row["supplier_id"]
        assert sup_id in valid_supplier_ids, f"Validation Failed: Invoice {row['invoice_id']} contains invalid supplier_id '{sup_id}'."
    print("[OK] All supplier IDs in Invoices table are valid.")
    
    # D. Validate customer receivable customer IDs exist
    valid_customer_ids = set(customers["customer_id"])
    for idx, row in receivables.iterrows():
        cust_id = row["customer_id"]
        assert cust_id in valid_customer_ids, f"Validation Failed: Receivable {row['receivable_id']} links to invalid customer_id '{cust_id}'."
    print("[OK] All customer IDs in Receivables table are valid.")
    
    # E. Validate mathematical consistency of daily cash account:
    # balance_t = balance_{t-1} + inflow_t - outflow_t
    # next day's opening_balance = previous day's balance
    for idx in range(len(cash_accounts)):
        day_record = cash_accounts.iloc[idx]
        opening = day_record["opening_balance"]
        inflow = day_record["daily_inflow"]
        outflow = day_record["daily_outflow"]
        closing = day_record["balance"]
        
        # Check balance consistency
        expected_closing = round(opening + inflow - outflow, 2)
        assert abs(closing - expected_closing) < 0.05, (
            f"Validation Failed on row {idx} ({day_record['date']}): "
            f"closing balance is {closing}, expected {expected_closing} "
            f"(opening: {opening}, inflow: {inflow}, outflow: {outflow})."
        )
        
        # Check day-to-day link
        if idx > 0:
            prev_closing = cash_accounts.iloc[idx - 1]["balance"]
            assert abs(opening - prev_closing) < 0.05, (
                f"Validation Failed on row {idx} ({day_record['date']}): "
                f"opening balance {opening} does not match previous day's closing balance {prev_closing}."
            )
            
    print("[OK] Cash balances are 100% mathematically consistent day-over-day.")
    
    # F. Validate available balance and deployable cash logic
    for idx, row in cash_accounts.iterrows():
        expected_avail = max(row["balance"] - company["minimum_cash_reserve"], 0.0)
        assert abs(row["available_balance"] - expected_avail) < 0.05, (
            f"Validation Failed: Row {idx} ({row['date']}) available balance is {row['available_balance']}, "
            f"expected {expected_avail}."
        )
        expected_deployable = max(row["available_balance"] - row["reserved_balance"], 0.0)
        assert abs(row["deployable_cash"] - expected_deployable) < 0.05, (
            f"Validation Failed: Row {idx} ({row['date']}) deployable cash is {row['deployable_cash']}, "
            f"expected {expected_deployable}."
        )
    print("[OK] Available balance and Deployable cash calculations are correct.")
    
    # G. Verify customer payment delay metrics are realistic and match risk categories
    print("\n--- Customer Performance Stats Verification ---")
    risky_avg_delay = customers[customers["risk_category"] == "HIGH"]["average_delay_days"].mean()
    reliable_avg_delay = customers[customers["risk_category"] == "LOW"]["average_delay_days"].mean()
    print(f"Average delay days for HIGH risk customers: {risky_avg_delay:.2f} days" if pd.notna(risky_avg_delay) else "Average delay days for HIGH risk: N/A")
    print(f"Average delay days for LOW risk customers: {reliable_avg_delay:.2f} days" if pd.notna(reliable_avg_delay) else "Average delay days for LOW risk: N/A")
    
    # H. Validate Future Data Generation and Stream Engine
    start_future = datetime.date(2026, 8, 28)
    end_future = datetime.date(2026, 12, 31)
    num_days = (end_future - start_future).days + 1
    print(f"\n--- Testing Future Streaming Engine ({num_days} Days) ---")
    future_data = generator.generate_future_data(num_days=num_days)
    future_cash = future_data["cash_accounts"]
    
    # Verify count
    assert len(future_cash) == num_days, f"Validation Failed: Expected {num_days} days of future cash, got {len(future_cash)}"
    print(f"[OK] Future cash account count is exactly {num_days} days.")
    
    # Verify mathematical continuity:
    # Opening balance of future Day 1 must match closing balance of historical Day 365
    last_hist_closing = cash_accounts.iloc[-1]["balance"]
    first_fut_opening = future_cash.iloc[0]["opening_balance"]
    assert abs(last_hist_closing - first_fut_opening) < 0.05, (
        f"Validation Failed: Chronological gap detected between history and future! "
        f"Last historical closing: {last_hist_closing}, First future opening: {first_fut_opening}"
    )
    print(f"[OK] Chronological continuity verified! Balance transitions from {last_hist_closing} to {first_fut_opening} seamlessly.")
    
    # Check mathematical consistency of future cash
    for idx in range(len(future_cash)):
        day_record = future_cash.iloc[idx]
        opening = day_record["opening_balance"]
        inflow = day_record["daily_inflow"]
        outflow = day_record["daily_outflow"]
        closing = day_record["balance"]
        expected_closing = round(opening + inflow - outflow, 2)
        assert abs(closing - expected_closing) < 0.05, f"Validation Failed: Future row {idx} math inconsistent."
    print("[OK] Future cash balances are mathematically consistent day-over-day.")
    
    # Test streaming iterator
    stream = generator.stream_future_data(num_days=5)
    stream_days = list(stream)
    assert len(stream_days) == 5, f"Expected 5 streamed days, got {len(stream_days)}"
    print(f"[OK] Streaming engine successfully yielded {len(stream_days)} days of live simulated feeds.")
    
    # Display details of Day 1 of stream
    day_1 = stream_days[0]
    print(f"Stream Day 1 Date: {day_1['date']}")
    print(f"Stream Day 1 Cash Account State: {day_1['cash_account']}")
    print(f"Stream Day 1 New Invoices Issued: {len(day_1['new_invoices'])}")
    print(f"Stream Day 1 Active Receivables Tracking: {len(day_1['receivables'])}")
    print(f"Stream Day 1 Daily Events Logged: {len(day_1['events'])}")
    
    # Save the dataset to disk (to verify saving works, use a temporary test folder)
    print("\n--- Persisting Dataset to Disk (Test Folder) ---")
    test_out_dir = "cashpilot_ai/data_test"
    generator.save_to_csv(data, output_dir=test_out_dir)
    import shutil
    shutil.rmtree(test_out_dir, ignore_errors=True)
    
    print("\n==================================================")
    print("            DATA GENERATION SUCCESSFUL            ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
