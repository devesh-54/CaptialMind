"""
CashPilot AI – Data Generator Tests
=====================================
Generates all data, prints summaries, and validates integrity constraints.
Run with:  python test_data_generator.py
"""

import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from historical_data_generator import HistoricalDataGenerator


def main():
    print("=" * 70)
    print("  CashPilot AI – Historical Data Generator Validation")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Generate all data
    # ------------------------------------------------------------------
    gen = HistoricalDataGenerator()
    data = gen.generate_all()
    gen.save("data/historical")
    success = gen.validate_and_plot("data/historical")
    if not success:
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Print record counts
    # ------------------------------------------------------------------
    print("\n📊  Record counts:")
    print("-" * 40)
    for key, val in data.items():
        if isinstance(val, dict):
            print(f"  {key:25s}  →  1 (dict)")
        else:
            print(f"  {key:25s}  →  {len(val):,} rows")

    # ------------------------------------------------------------------
    # 3. Print sample rows for each DataFrame
    # ------------------------------------------------------------------
    for key, val in data.items():
        if isinstance(val, pd.DataFrame) and len(val) > 0:
            print(f"\n{'─' * 70}")
            print(f"  Sample: {key.upper()}")
            print(f"{'─' * 70}")
            print(val.head(3).to_string(index=False))

    # ------------------------------------------------------------------
    # 4. Validations
    # ------------------------------------------------------------------
    errors: list[str] = []

    # ---- 4a. Exactly 365 daily cash records ----
    n_cash = len(data["cash_accounts"])
    if n_cash != 365:
        errors.append(f"Expected 365 cash-account rows, got {n_cash}")
    else:
        print("\n✅  365 daily cash-account rows present.")

    # ---- 4b. No negative cash balance ----
    neg_balance = data["cash_accounts"][data["cash_accounts"]["balance"] < 0]
    if len(neg_balance) > 0:
        # We warn but don't fail – some liquidity crises may dip below 0
        print(f"\n⚠️   {len(neg_balance)} day(s) with negative balance detected "
              f"(allowed under extreme liquidity pressure).")
    else:
        print("✅  No negative cash balances.")

    # ---- 4c. All invoice supplier_ids exist in suppliers ----
    valid_sups = set(data["suppliers"]["supplier_id"])
    inv_sups = set(data["invoices"]["supplier_id"])
    orphan_inv = inv_sups - valid_sups
    if orphan_inv:
        errors.append(f"Invoices reference unknown suppliers: {orphan_inv}")
    else:
        print("✅  All invoice supplier IDs are valid.")

    # ---- 4d. All receivables reference valid customers ----
    valid_custs = set(data["customers"]["customer_id"])
    recv_custs = set(data["receivables"]["customer_id"])
    orphan_recv = recv_custs - valid_custs
    if orphan_recv:
        errors.append(f"Receivables reference unknown customers: {orphan_recv}")
    else:
        print("✅  All receivable customer IDs are valid.")

    # ---- 4e. All obligation supplier_ids exist in suppliers ----
    valid_sups = set(data["suppliers"]["supplier_id"])
    obl_sups = set(data["obligations"]["supplier_id"])
    orphan_obl = obl_sups - valid_sups
    if orphan_obl:
        errors.append(f"Obligations reference unknown suppliers: {orphan_obl}")
    else:
        print("✅  All obligation supplier IDs are valid.")

    # ---- 4f. Cash balance consistency ----
    ca = data["cash_accounts"]
    ca_check = ca.copy()
    ca_check["computed_balance"] = (
        ca_check["opening_balance"]
        + ca_check["daily_inflow"]
        - ca_check["daily_outflow"]
    ).round(2)
    mismatch = ca_check[
        (ca_check["computed_balance"] - ca_check["balance"]).abs() > 0.02
    ]
    if len(mismatch) > 0:
        errors.append(
            f"Cash balance mismatch on {len(mismatch)} day(s). "
            f"First mismatch: {mismatch.iloc[0]['date']}"
        )
    else:
        print("✅  Cash balances are consistent (opening + inflow − outflow = balance).")

    # ---- 4g. Opening balance continuity ----
    for i in range(1, len(ca)):
        prev_close = round(ca.iloc[i - 1]["balance"], 2)
        curr_open = round(ca.iloc[i]["opening_balance"], 2)
        if abs(prev_close - curr_open) > 0.02:
            errors.append(
                f"Opening-balance discontinuity on {ca.iloc[i]['date']}: "
                f"prev close={prev_close}, curr open={curr_open}"
            )
            break
    else:
        print("✅  Opening balance equals previous day's closing balance for all days.")

    # ---- 4h. Decision items reference valid decisions ----
    if len(data["decision_items"]) > 0:
        valid_decs = set(data["decisions"]["decision_id"])
        di_decs = set(data["decision_items"]["decision_id"])
        orphan_di = di_decs - valid_decs
        if orphan_di:
            errors.append(f"Decision items reference unknown decisions: {orphan_di}")
        else:
            print("✅  All decision-item decision IDs are valid.")

    # ---- 4i. Receivables have valid status ----
    if len(data["receivables"]) > 0:
        recv_statuses = set(data["receivables"]["status"])
        invalid_statuses = recv_statuses - {"PENDING", "OVERDUE", "PAID"}
        if invalid_statuses:
            errors.append(f"Receivables have unexpected statuses: {invalid_statuses}")
        else:
            print("✅  All receivables have valid statuses (PAID, PENDING, OVERDUE).")

    # ------------------------------------------------------------------
    # 5. Summary statistics for ARIMA
    # ------------------------------------------------------------------
    print(f"\n{'─' * 70}")
    print("  Cash Account Summary (for ARIMA readiness)")
    print(f"{'─' * 70}")
    print(f"  Date range   : {ca['date'].min().date()} → {ca['date'].max().date()}")
    print(f"  Mean balance  : ₹{ca['balance'].mean():,.0f}")
    print(f"  Std balance   : ₹{ca['balance'].std():,.0f}")
    print(f"  Min balance   : ₹{ca['balance'].min():,.0f}")
    print(f"  Max balance   : ₹{ca['balance'].max():,.0f}")

    # ------------------------------------------------------------------
    # 6. Final verdict
    # ------------------------------------------------------------------
    print()
    if errors:
        print("❌  VALIDATION FAILED")
        for e in errors:
            print(f"    • {e}")
        sys.exit(1)
    else:
        print("=" * 70)
        print("  DATA GENERATION SUCCESSFUL")
        print("=" * 70)


if __name__ == "__main__":
    main()
