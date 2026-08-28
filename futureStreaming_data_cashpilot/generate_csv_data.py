import os
import sys
import datetime
import shutil
import json

# Ensure cashpilot_ai is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cashpilot_ai.data_generator import FinancialDataGenerator

def main():
    print("Initializing Financial Data Generator for Tata Motors (fixed seed=42)...")
    generator = FinancialDataGenerator(seed=42)
    
    # 1. Generate Historical Data in memory (to establish initial state and ensure continuity)
    print("\nGenerating historical data in memory (will not be saved)...")
    hist_data = generator.generate_all()
    
    # 2. Generate Future streaming dataset (from August 28, 2026 to December 31, 2026)
    start_future = datetime.date(2026, 8, 28)
    end_future = datetime.date(2026, 12, 31)
    num_days = (end_future - start_future).days + 1
    print(f"\nGenerating future streaming data from {start_future} to {end_future} ({num_days} days)...")
    future_data = generator.generate_future_data(num_days=num_days)
    
    # 3. Setup output directory and delete any old past files
    output_dir = "cashpilot_ai/data"
    print(f"\nCleaning output directory '{output_dir}' to remove all past/historical data files...")
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.chmod(file_path, 0o777)
                    os.remove(file_path)
                except Exception:
                    pass
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.chmod(dir_path, 0o777)
                    os.rmdir(dir_path)
                except Exception:
                    pass
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
        except Exception:
            pass
            
    os.makedirs(output_dir, exist_ok=True)
    
    # Save company configuration as JSON
    company_path = os.path.join(output_dir, "company.json")
    with open(company_path, "w", encoding="utf-8") as f:
        json.dump(hist_data["company"], f, indent=4)
    print(f"Saved company configuration to: {company_path}")
    
    # Save each Future DataFrame to CSV directly in output_dir
    for name, df in future_data.items():
        csv_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Saved future streaming {name} DataFrame to: {csv_path}")
        
    # Compile future consolidated daily dataset
    future_cons = generator.compile_daily_consolidated(
        cash_accounts=future_data["cash_accounts"],
        invoices=future_data["invoices"],
        obligations=future_data["obligations"],
        transactions=future_data["transactions"],
        events=future_data["events"]
    )
    future_cons_path = os.path.join(output_dir, "future_daily_consolidated.csv")
    future_cons.to_csv(future_cons_path, index=False, encoding="utf-8")
    print(f"Saved consolidated future daily data ({future_cons.shape[0]} days) to: {future_cons_path}")
    
    print("\n==================================================")
    print("      DATASET EXPORT TO CSV COMPLETED SUCCESSFULLY ")
    print("==================================================")
    print(f"Future streaming files for Tata Motors are located in: {os.path.abspath(output_dir)}")
    print(f"Consolidated file: {os.path.abspath(future_cons_path)}")

if __name__ == "__main__":
    main()
