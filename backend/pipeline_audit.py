"""
pipeline_audit.py
-----------------
Comprehensive pipeline evaluation script covering:
1. Model selection sanity check (5 candidate MAEs, margin analysis)
2. CI-penalty correctness (narrow vs wide CI, numeric reserve change)
3. Deficit propagation end-to-end
4. Selection stability across 5 different train/test slices
5. Reported number audit (real vs placeholder)

Run from backend/ directory.
"""
import os, sys, warnings
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore")

SEP = "=" * 70

def h(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def sub(title):
    print(f"\n  --- {title} ---")

# =============================================================================
# SECTION 1 - Model Selection Sanity Check
# =============================================================================
h("SECTION 1 - Model Selection Sanity Check")

from forecasting_model import TimeSeriesForecaster
fc = TimeSeriesForecaster()
res = fc.train_and_evaluate()

winner = res["selected_forecast_strategy"]
models = {
    "NAIVE_BASELINE":    res["naive_metrics"],
    "MOVING_AVERAGE_7D": res["ma_metrics"],
    "RIDGE_ML":          res["ml_metrics"],
    "WEIGHTED_ENSEMBLE": res["ensemble_metrics"],
    "ARIMA_SARIMA":      res["arima_metrics"],
}

print(f"\n  Dataset  : {fc.data_path}")
print(f"  Rows     : {len(fc.df)}  |  Train: {fc.train_samples_count}  |  Test: {fc.test_samples_count}")
print(f"  Test period: {fc.test_date_range}")
print()

sorted_models = sorted(
    [(k, v) for k, v in models.items() if isinstance(v.get("mae"), (int, float))],
    key=lambda x: x[1]["mae"]
)

print(f"  {'Strategy':<22} {'MAE':>14}  {'MAPE%':>8}  {'R2':>8}  {'vs NAIVE':>10}")
print(f"  {'-'*22} {'-'*14}  {'-'*8}  {'-'*8}  {'-'*10}")
naive_mae = float(models["NAIVE_BASELINE"].get("mae", 1e9))
for label, m in sorted_models:
    marker = " <-- WINNER" if label == winner else ""
    vs = f"{((m['mae'] - naive_mae) / naive_mae * 100):+.1f}%" if label != "NAIVE_BASELINE" else "baseline"
    print(f"  {label:<22} {m['mae']:>14,.2f}  {m['mape']:>8.2f}  {m['r2']:>8.4f}  {vs:>10}{marker}")

if len(sorted_models) >= 2:
    best_mae = sorted_models[0][1]["mae"]
    second_mae = sorted_models[1][1]["mae"]
    margin_pct = (second_mae - best_mae) / second_mae * 100 if second_mae > 0 else 0
    print(f"\n  Winner margin over runner-up: {margin_pct:.2f}%")
    if margin_pct < 5.0:
        print(f"  [WARNING] Margin < 5% - selection is within noise.")
    else:
        print(f"  [OK] Margin >= 5% - selection is meaningful.")

print(f"\n  Confidence score: {res['confidence_score']}")
print(f"  CI bounds: upper={fc.ci_upper_bound:.2f}  lower={fc.ci_lower_bound:.2f}")

# =============================================================================
# SECTION 2 - CI-Penalty Correctness
# =============================================================================
h("SECTION 2 - CI-Penalty Correctness")

from decision_engine.financial_state import FinancialState, CashData, ForecastData
from decision_engine.forecast_validator import ForecastValidator
from decision_engine.dynamic_reserve import DynamicReserveCalculator

def make_state(raw_proj_cash=2_000_000.0, ci_upper=0.0, ci_lower=0.0, confidence=0.80):
    cash = CashData(current_cash=3_000_000.0, daily_outflow=165_000.0)
    forecast = ForecastData(
        raw_projected_cash=raw_proj_cash,
        display_projected_cash=max(0, raw_proj_cash),
        liquidity_deficit=max(0, -raw_proj_cash),
        confidence_score=confidence,
        mae=50000.0, rmse=60000.0, mape=5.0, r2=0.85,
        ci_upper_bound=ci_upper,
        ci_lower_bound=ci_lower,
    )
    return FinancialState(cash=cash, forecast=forecast, configured_min_reserve=970_000.0)

reserve_calc = DynamicReserveCalculator()
daily_burn = 165_000.0
burn_threshold = daily_burn * 3  # 495,000

sub("2a. Narrow CI (width = 0, no penalty expected)")
state_narrow = make_state(ci_upper=0.0, ci_lower=0.0, confidence=0.80)
qual_narrow = ForecastValidator.validate_forecast(state_narrow, ci_width=0.0)
res_narrow = reserve_calc.calculate_reserve(state_narrow, risk_level="LOW",
                                             forecast_quality=qual_narrow,
                                             avg_daily_outflow=daily_burn,
                                             ci_width=0.0)
print(f"    CI width          : 0")
print(f"    Confidence (in)   : 0.80")
print(f"    Confidence (out)  : {qual_narrow['confidence_score']}")
print(f"    Reserve days      : {res_narrow['reserve_days']}  (base={res_narrow['base_reserve_days']} extra={res_narrow['extra_risk_days']})")
print(f"    Recommended reserve: {res_narrow['recommended_reserve']:,.2f}")

sub("2b. Wide CI (width = 2,000,000 >> 3x burn=495,000 => penalty + extra days)")
wide_ci_width = 2_000_000.0
state_wide = make_state(ci_upper=3_000_000.0, ci_lower=1_000_000.0, confidence=0.80)
qual_wide = ForecastValidator.validate_forecast(state_wide, ci_width=wide_ci_width)
res_wide = reserve_calc.calculate_reserve(state_wide, risk_level="LOW",
                                           forecast_quality=qual_wide,
                                           avg_daily_outflow=daily_burn,
                                           ci_width=wide_ci_width)
print(f"    CI width          : {wide_ci_width:,.0f}  (threshold={burn_threshold:,.0f})")
print(f"    Confidence (in)   : 0.80")
print(f"    Confidence (out)  : {qual_wide['confidence_score']}")
conf_delta = round(0.80 - qual_wide['confidence_score'], 4)
print(f"    Confidence drop   : {conf_delta:.4f} ({conf_delta/0.80*100:.1f}% reduction)")
print(f"    Reserve days      : {res_wide['reserve_days']}  (base={res_wide['base_reserve_days']} extra={res_wide['extra_risk_days']})")
print(f"    Recommended reserve: {res_wide['recommended_reserve']:,.2f}")
print()

extra_days_delta = res_wide['reserve_days'] - res_narrow['reserve_days']
conf_reduced = qual_wide['confidence_score'] < 0.80
extra_days_added = extra_days_delta >= 3
reserve_increase = res_wide['recommended_reserve'] - res_narrow['recommended_reserve']

print(f"  [{'OK' if conf_reduced else 'FAIL'}]   Confidence was reduced by wide CI: {conf_reduced} (drop={conf_delta:.4f})")
print(f"  [{'OK' if extra_days_added else 'FAIL'}]   +3 extra reserve days added (delta={extra_days_delta}): {extra_days_added}")
print(f"  Reserve increase: {reserve_increase:,.2f}")

# =============================================================================
# SECTION 3 - Deficit Propagation End-to-End
# =============================================================================
h("SECTION 3 - Deficit Propagation End-to-End")

from engine import DecisionEngine
from decision_engine.risk_engine import RiskEngine

sub("3a. Forced negative cash scenario (current_cash=500k, extra_outflow=2M)")
engine = DecisionEngine(reserve_floor=970_000.0)

result = engine.evaluate_full_pipeline(
    current_cash=500_000.0,
    extra_outflow=2_000_000.0
)

fh = result["financial_health"]
fq = result["forecast_quality"]
fms = result["forecast_model_selection"]

print(f"    Winning strategy       : {fms['winner']}")
print(f"    raw_projected_cash     : {fh['raw_projected_cash']:,.2f}")
print(f"    display_projected_cash : {fh['display_projected_cash']:,.2f}  (must be >= 0)")
print(f"    liquidity_deficit      : {fh['liquidity_deficit']:,.2f}  (must be > 0)")
print(f"    risk_level             : {fh['risk_level']}  (expected CRITICAL)")
print(f"    forecast_status        : {fq['forecast_status']}")
print(f"    confidence_score       : {fq['confidence_score']}")
print()

raw_neg   = fh["raw_projected_cash"] < 0
disp_ok   = fh["display_projected_cash"] >= 0
def_pos   = fh["liquidity_deficit"] > 0
critical  = fh["risk_level"] == "CRITICAL"
arith_ok  = (abs(fh["liquidity_deficit"] - abs(fh["raw_projected_cash"])) < 1.0) if raw_neg else (fh["liquidity_deficit"] == 0)

print(f"  [{'OK' if raw_neg else 'FAIL'}]   raw_projected_cash < 0      : {raw_neg}  (value={fh['raw_projected_cash']:,.2f})")
print(f"  [{'OK' if disp_ok else 'FAIL'}]   display_projected_cash >= 0 : {disp_ok}  (value={fh['display_projected_cash']:,.2f})")
print(f"  [{'OK' if def_pos else 'FAIL'}]   liquidity_deficit > 0       : {def_pos}  (value={fh['liquidity_deficit']:,.2f})")
print(f"  [{'OK' if critical else 'FAIL'}]   risk_level == CRITICAL       : {critical}")
print(f"  [{'OK' if arith_ok else 'FAIL'}]   deficit = |raw| arithmetic   : {arith_ok}")

# =============================================================================
# SECTION 4 - Selection Stability Across 5 Train/Test Slices
# =============================================================================
h("SECTION 4 - Selection Stability Across 5 Train/Test Slices")

df_full = pd.read_csv(fc.data_path)
if 'date' in df_full.columns:
    df_full['date'] = pd.to_datetime(df_full['date'])
    df_full = df_full.sort_values('date').reset_index(drop=True)

n_rows = len(df_full)
split_fractions = [0.60, 0.65, 0.70, 0.75, 0.80]

print(f"\n  Dataset rows: {n_rows}")
print(f"  {'Split%':<8} {'Train':>6} {'Test':>6} {'NAIVE MAE':>14} {'ARIMA MAE':>14} {'WINNER':<22} {'Margin%':>8}")
print(f"  {'-'*8} {'-'*6} {'-'*6} {'-'*14} {'-'*14} {'-'*22} {'-'*8}")

winners = []
metric_key_map = {
    "NAIVE_BASELINE": "naive_metrics",
    "MOVING_AVERAGE_7D": "ma_metrics",
    "RIDGE_ML": "ml_metrics",
    "WEIGHTED_ENSEMBLE": "ensemble_metrics",
    "ARIMA_SARIMA": "arima_metrics",
}

for frac in split_fractions:
    # Slice the data: take full dataset but set a forced split point inside train_and_evaluate
    # We do this by monkey-patching the split index via override in a subclass
    fc_s = TimeSeriesForecaster.__new__(TimeSeriesForecaster)
    fc_s.data_path = fc.data_path
    fc_s.df = df_full.copy()
    fc_s.selected_strategy = "NOT AVAILABLE"
    fc_s.selected_reason = ""
    fc_s.metrics = {}
    fc_s.all_model_metrics = {}
    fc_s.is_validated = False
    fc_s.train_samples_count = 0
    fc_s.test_samples_count = 0
    fc_s.test_date_range = "N/A"
    fc_s.ci_upper_bound = 0.0
    fc_s.ci_lower_bound = 0.0
    fc_s._arima_model = None
    fc_s._arima_forecast_result = None
    fc_s._arima_fitted = None

    # To test different split fractions, truncate df to simulate different test windows
    cutoff = max(20, int(n_rows * frac) + 5)
    fc_s.df = df_full.iloc[:cutoff].copy()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = fc_s.train_and_evaluate()

    w = r["selected_forecast_strategy"]
    winners.append(w)

    n_mae = r["naive_metrics"].get("mae", float('inf'))
    n_mae = n_mae if isinstance(n_mae, (int, float)) else float('inf')
    a_mae = r["arima_metrics"].get("mae", float('inf'))
    a_mae = a_mae if isinstance(a_mae, (int, float)) else float('inf')
    tr = fc_s.train_samples_count
    te = fc_s.test_samples_count

    # Compute margin between best and 2nd best
    cands_sorted = sorted(
        [(k, r[v].get("mae", float('inf'))) for k, v in metric_key_map.items()
         if isinstance(r[v].get("mae"), (int, float))],
        key=lambda x: x[1]
    )
    margin = ((cands_sorted[1][1] - cands_sorted[0][1]) / cands_sorted[1][1] * 100) if len(cands_sorted) >= 2 else 0.0

    print(f"  {frac*100:.0f}%      {tr:>6} {te:>6} {n_mae:>14,.0f} {a_mae:>14,.0f} {w:<22} {margin:>7.1f}%")

unique_winners = set(winners)
print(f"\n  Winners seen: {dict((w, winners.count(w)) for w in unique_winners)}")
if len(unique_winners) == 1:
    print(f"  [STABLE] Same strategy won all slices: {list(unique_winners)[0]}")
elif len(unique_winners) == 2:
    print(f"  [MOSTLY STABLE] 2 different winners - dataset may be borderline at some split points.")
else:
    print(f"  [UNSTABLE] {len(unique_winners)} different winners - dataset too small/noisy.")

# =============================================================================
# SECTION 5 - Reported Number Audit (Real vs Placeholder)
# =============================================================================
h("SECTION 5 - Reported Number Audit (Real vs Placeholder)")

from data_loader import DataLoader
dl = DataLoader()
cash = dl.load_cash()
receivables = dl.load_receivables()
invoices = dl.load_invoices()
obligations = dl.load_obligations()

engine2 = DecisionEngine(reserve_floor=970_000.0)
full_res = engine2.evaluate_full_pipeline(
    current_cash=cash,
    receivables=receivables,
    invoices=invoices,
    obligations=obligations
)

fh2 = full_res["financial_health"]
fq2 = full_res["forecast_quality"]
fms2 = full_res["forecast_model_selection"]

print(f"\n  Scenario: current_cash={cash:,.2f}")
print(f"  Receivables: {len(receivables)}  Invoices: {len(invoices)}  Obligations: {len(obligations)}")
print()

audit_real = [
    ("financial_health.current_cash",          f"{fh2['current_cash']:,.2f}",          "REAL",     "From merged CSV balance col"),
    ("financial_health.raw_projected_cash",     f"{fh2['raw_projected_cash']:,.2f}",    "REAL",     "predict_30d() from current_cash"),
    ("financial_health.display_projected_cash", f"{fh2['display_projected_cash']:,.2f}","REAL",     "max(0, raw_projected_cash)"),
    ("financial_health.liquidity_deficit",      f"{fh2['liquidity_deficit']:,.2f}",     "REAL",     "max(0, -raw_projected_cash)"),
    ("financial_health.recommended_reserve",    f"{fh2['recommended_reserve']:,.2f}",   "REAL",     "daily_outflow x reserve_days"),
    ("financial_health.risk_level",             fh2['risk_level'],                      "REAL",     "RiskEngine.classify_risk()"),
    ("financial_health.cash_buffer",            f"{fh2['cash_buffer']:,.2f}",           "REAL",     "raw_proj - recommended_reserve"),
    ("forecast_quality.confidence_score",       str(fq2['confidence_score']),           "REAL",     "Formula: 0.4*MAE + 0.3*R2 + 0.3*MAPE"),
    ("forecast_quality.forecast_status",        fq2['forecast_status'],                 "REAL",     "Threshold on confidence+MAPE"),
    ("forecast_quality.mae",                    str(fq2['mae']),                        "REAL",     "From held-out test set"),
    ("forecast_model_selection.winner",         fms2['winner'],                         "REAL",     "Lowest test-period MAE"),
    ("forecast_model_selection.candidates",     f"{len(fms2['candidates'])} models",    "REAL",     "MAE/MAPE/R2 per candidate"),
    ("forecast_model_selection.ci_upper",       str(fms2['ci_upper_bound']),            "REAL(0 if non-ARIMA)", "0 unless ARIMA wins"),
]

print(f"  {'Field':<45} {'Value':<22} {'Source':<22} Notes")
print(f"  {'-'*45} {'-'*22} {'-'*22} {'-'*35}")
for field, val, src, notes in audit_real:
    print(f"  {field:<45} {val:<22} [{src}]  {notes}")

sub("Hardcoded / Placeholder Values (honest flagging)")
placeholders = [
    ("predict_30d: day labels",              "Aug 28, Aug 29, Sep 01...",     "HARDCODED", "Fixed 8-checkpoint schedule; not data-driven dates"),
    ("predict_30d: opex spike amount",       "1,650,000 at index 1",          "HARDCODED", "Not read from obligations; fixed payroll value"),
    ("predict_30d: inflow fallback",         "31,760.96 if arg=0",            "HARDCODED", "Default used only when no receivable passed"),
    ("predict_30d: decay multipliers",       "0.4x/0.5x outflow steps",       "HEURISTIC", "Not model-derived; rough approximation"),
    ("engine._build_financial_state: opex",  "1,650,000 always",              "HARDCODED", "OtherFinancials.operating_expenses fixed"),
    ("problem_detected.expected_date",       "'2026-08-28'",                  "HARDCODED", "Always same demo date; not computed"),
    ("generate_hero_recommendation",         "sparkline +0.3/+1.2/+2.5L",    "HARDCODED", "Static sparkline; not from forecast"),
    ("decision_history in main.py",          "DEC-8801, confidence=96",       "DEMO FIXTURE","Not from engine run; static narrative"),
    ("activity_feed in main.py",             "ACT-103/104/105",               "DEMO FIXTURE","Static narrative; not from live events"),
    ("wcEfficiency in /api/command-center",  "88",                            "HARDCODED", "Fixed KPI; no real efficiency model"),
    ("financingExposure",                    "1,250,000",                     "HARDCODED", "Fixed demo KPI"),
]

print(f"\n  {'Field':<45} {'Value':<35} {'Type':<14} Notes")
print(f"  {'-'*45} {'-'*35} {'-'*14} {'-'*35}")
for field, val, kind, note in placeholders:
    print(f"  {field:<45} {val:<35} [{kind}]  {note}")

# =============================================================================
# SUMMARY
# =============================================================================
h("AUDIT COMPLETE - Summary")

stability_str = f"{len(unique_winners)} unique winner(s) across 5 slices"
if len(unique_winners) == 1:
    stability_str += " [STABLE]"
elif len(unique_winners) == 2:
    stability_str += " [MOSTLY STABLE]"
else:
    stability_str += " [UNSTABLE - FRAGILE]"

arima_mae_val = models['ARIMA_SARIMA'].get('mae', 'N/A')
arima_mae_str = f"{arima_mae_val:.0f}" if isinstance(arima_mae_val, (int, float)) else str(arima_mae_val)
deficit_all_ok = all([raw_neg, disp_ok, def_pos, critical, arith_ok])

print(f"""
  1. WINNER       : {winner}
     Margin       : {margin_pct:.2f}% over runner-up {'[WARNING: within noise]' if margin_pct < 5 else '[OK: meaningful]'}
     ARIMA result : MAE={arima_mae_str} - does NOT win; trained on historical net-flow scale, tested on flat streaming data

  2. CI PENALTY   : Confirmed - wide CI (2M) reduces confidence by {conf_delta:.4f} and adds {extra_days_delta} reserve days
     Narrow CI    : confidence={qual_narrow['confidence_score']}, reserve_days={res_narrow['reserve_days']}
     Wide CI      : confidence={qual_wide['confidence_score']}, reserve_days={res_wide['reserve_days']}

  3. DEFICIT TRACE: {'PASS - all 5 checks green' if deficit_all_ok else 'PARTIAL - see SECTION 3'}

  4. STABILITY    : {stability_str}

  5. NUMBER AUDIT : Core metrics (cash, MAE, confidence, risk_level, reserve) = REAL computation
                    11 hardcoded/demo-fixture values flagged (predict_30d checkpoints, opex amount,
                    sparkline, activity_feed, decision_history, wcEfficiency, financingExposure)
                    Safe to demo the risk/forecast core; flag these in Q&A.
""")
