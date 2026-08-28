import os
import math
import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

class TimeSeriesForecaster:
    """
    Time-Series Forecasting & Validation Engine for Working-Capital Management.
    Performs strict chronological train/test splits (80% train, 20% test),
    dynamically evaluates Naive, Moving Average, Ridge ML, Weighted Ensemble, and
    ARIMA_SARIMA models, selects the strategy with the lowest MAE on the held-out
    test period, and returns 30-day cash projections preserving raw negative cash
    values and deficits.
    """

    MODEL_FILE = os.path.join(os.path.dirname(__file__), "arima_netflow_model.pkl")

    def __init__(self, data_path: str = None):
        if data_path is None:
            base_dir = os.path.dirname(__file__)
            candidates = [
                os.path.join(base_dir, "merged_future_daily_consolidated.csv"),
                os.path.join(base_dir, "..", "historical_data_cashpilot", "data", "historical", "future_daily_consolidated.csv"),
                os.path.join(base_dir, "..", "futureStreaming_data_cashpilot", "cashpilot_ai", "data", "future_daily_consolidated.csv"),
            ]
            for candidate in candidates:
                if os.path.exists(candidate):
                    data_path = os.path.abspath(candidate)
                    break

        self.data_path = data_path
        self.df = self._load_data()
        self.selected_strategy = "NOT AVAILABLE"
        self.selected_reason = ""
        self.metrics = {}
        self.all_model_metrics = {}
        self.is_validated = False
        self.train_samples_count = 0
        self.test_samples_count = 0
        self.test_date_range = "NOT AVAILABLE"
        # CI fields (populated when ARIMA wins selection)
        self.ci_upper_bound: float = 0.0
        self.ci_lower_bound: float = 0.0
        self._arima_model = None  # loaded lazily
        self._arima_forecast_result = None  # 30-step get_forecast() result

    def _load_data(self) -> pd.DataFrame:
        if self.data_path and os.path.exists(self.data_path):
            try:
                df = pd.read_csv(self.data_path)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date').reset_index(drop=True)
                return df
            except Exception as e:
                print(f"Warning: Failed to load dataset from {self.data_path}: {e}")
        return pd.DataFrame()

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)

        if len(y_true) == 0:
            return {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"}

        mae = float(np.mean(np.abs(y_true - y_pred)))
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

        # Safe MAPE calculation avoiding division by zero
        denom = np.where(np.abs(y_true) < 1e-5, 1.0, np.abs(y_true))
        mape = float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)

        # R^2 Score
        ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
        ss_res = float(np.sum((y_true - y_pred) ** 2))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-5 else 0.0

        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "r2": round(r2, 4)
        }

    def _load_arima_model(self) -> Optional[Any]:
        """Load the SARIMA model via joblib. Returns None on any failure."""
        if self._arima_model is not None:
            return self._arima_model
        if not os.path.exists(self.MODEL_FILE):
            return None
        try:
            import joblib
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._arima_model = joblib.load(self.MODEL_FILE)
            return self._arima_model
        except Exception as e:
            print(f"Warning: Could not load ARIMA model from {self.MODEL_FILE}: {e}")
            return None

    def _evaluate_arima(
        self,
        clean_df: pd.DataFrame,
        split_idx: int,
        y_balance: np.ndarray
    ) -> Tuple[Optional[Dict[str, Any]], Optional[np.ndarray]]:
        """
        Evaluate ARIMA(2,1,3)(1,0,1,7) on the same chronological test split
        used by the other 4 models. Converts net-flow forecasts → balance by
        integrating from the last training balance.

        Returns (metrics_dict, y_test_arima) or (None, None) on failure.
        """
        model = self._load_arima_model()
        if model is None:
            return None, None

        if 'daily_inflow' not in clean_df.columns or 'daily_outflow' not in clean_df.columns:
            print("Warning: ARIMA skipped — no daily_inflow/daily_outflow columns in dataset.")
            return None, None

        try:
            import statsmodels.api as sm
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                net_flow = (clean_df['daily_inflow'] - clean_df['daily_outflow']).values
                train_net = net_flow[:split_idx]
                test_net_actual = net_flow[split_idx:]
                n_test = len(test_net_actual)

                if n_test < 2:
                    return None, None

                # Re-apply model to training portion so forecasts are on-distribution
                fitted = model.apply(train_net)
                fc = fitted.get_forecast(steps=n_test)
                # predicted_mean may be a pandas Series or numpy array depending on input
                pm = fc.predicted_mean
                pred_net = pm.values if hasattr(pm, 'values') else np.asarray(pm)

                # Convert net-flow forecasts → balance by integrating from last train balance
                last_train_balance = float(y_balance[split_idx - 1])
                y_test_arima = np.zeros(n_test)
                running = last_train_balance
                for i, nf in enumerate(pred_net):
                    running = running + float(nf)
                    y_test_arima[i] = running

                # Store 90% CI for the last step (represents end-of-horizon uncertainty)
                ci = fc.conf_int(alpha=0.10)
                # conf_int may be a DataFrame or ndarray
                ci_arr = ci.values if hasattr(ci, 'values') else np.asarray(ci)  # shape (n_test, 2)
                # Convert CI to balance CI at end of horizon
                balance_lower = last_train_balance + float(np.cumsum(ci_arr[:, 0])[-1])
                balance_upper = last_train_balance + float(np.cumsum(ci_arr[:, 1])[-1])
                self.ci_lower_bound = balance_lower
                self.ci_upper_bound = balance_upper

                # Store 30-step forecast result for use in predict_30d when ARIMA wins
                self._arima_train_balance = last_train_balance
                self._arima_fitted = fitted

                y_test_balance = y_balance[split_idx:]
                arima_metrics = self.calculate_metrics(y_test_balance, y_test_arima)
                return arima_metrics, y_test_arima

        except Exception as e:
            print(f"Warning: ARIMA evaluation failed: {e}")
            return None, None

    def train_and_evaluate(self) -> Dict[str, Any]:
        """
        Chronological Train/Test Evaluation & Dynamic Model Selection.
        Evaluates up to 5 candidates (NAIVE, MA7D, RIDGE_ML, WEIGHTED_ENSEMBLE,
        ARIMA_SARIMA) and selects the one with the lowest held-out test MAE.
        Returns 'NOT AVAILABLE' if data is insufficient.
        """
        np.random.seed(42)  # Reproducibility seed

        df = self.df.copy()
        if 'balance' not in df.columns or len(df) < 15:
            self.selected_strategy = "NOT AVAILABLE"
            self.selected_reason = "Dataset contains fewer than 15 historical records or missing 'balance' column."
            self.is_validated = False
            return {
                "selected_forecast_strategy": "NOT AVAILABLE",
                "reason": self.selected_reason,
                "ml_metrics": {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"},
                "naive_metrics": {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"},
                "ma_metrics": {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"},
                "ensemble_metrics": {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"},
                "arima_metrics": {"mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"},
                "model_outperforms_baseline": False,
                "confidence_score": 0.10
            }

        # Feature Engineering (strictly backwards-looking)
        df['lag_1'] = df['balance'].shift(1)
        df['lag_3'] = df['balance'].shift(3)
        df['lag_7'] = df['balance'].shift(7)
        df['roll_mean_7'] = df['balance'].shift(1).rolling(7).mean()
        df['roll_std_7'] = df['balance'].shift(1).rolling(7).std().fillna(0)

        if 'daily_inflow' in df.columns and 'daily_outflow' in df.columns:
            df['net_flow_lag1'] = (df['daily_inflow'] - df['daily_outflow']).shift(1)
        else:
            df['net_flow_lag1'] = 0.0

        clean_df = df.dropna().reset_index(drop=True)
        feature_cols = ['lag_1', 'lag_3', 'lag_7', 'roll_mean_7', 'roll_std_7', 'net_flow_lag1']
        X = clean_df[feature_cols].values
        y = clean_df['balance'].values

        # Strict Chronological Train/Test Split (80% Train, 20% Test)
        split_idx = int(len(clean_df) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        self.train_samples_count = len(X_train)
        self.test_samples_count = len(X_test)
        if 'date' in clean_df.columns:
            test_dates = clean_df['date'].iloc[split_idx:]
            self.test_date_range = f"{test_dates.iloc[0].strftime('%Y-%m-%d')} to {test_dates.iloc[-1].strftime('%Y-%m-%d')}"

        # 1. Naive Baseline (prediction[t] = actual[t-1])
        y_test_naive = np.zeros(len(y_test))
        for i in range(len(y_test)):
            y_test_naive[i] = y[split_idx - 1 + i] if (split_idx - 1 + i) >= 0 else y_train[-1]
        naive_metrics = self.calculate_metrics(y_test, y_test_naive)

        # 2. 7-Day Moving Average Baseline
        y_test_ma = clean_df['roll_mean_7'].values[split_idx:]
        ma_metrics = self.calculate_metrics(y_test, y_test_ma)

        # 3. Ridge ML Regressor
        try:
            from sklearn.linear_model import Ridge
            model_ridge = Ridge(alpha=1.0)
            model_ridge.fit(X_train, y_train)
            y_test_ml = model_ridge.predict(X_test)
        except Exception:
            X_b = np.hstack([np.ones((len(X_train), 1)), X_train])
            weights = np.linalg.pinv(X_b.T @ X_b + 1e-3 * np.eye(X_b.shape[1])) @ X_b.T @ y_train
            X_test_b = np.hstack([np.ones((len(X_test), 1)), X_test])
            y_test_ml = X_test_b @ weights
            model_ridge = None

        ml_metrics = self.calculate_metrics(y_test, y_test_ml)

        # 4. Weighted Ensemble Model (Weights determined strictly on train split)
        y_train_pred_naive = clean_df['lag_1'].values[:split_idx]
        y_train_pred_ml = model_ridge.predict(X_train) if model_ridge is not None else y_train_pred_naive

        best_w_ml = 0.5
        best_train_mae = float('inf')
        for w in np.linspace(0.0, 1.0, 21):
            train_ens = (w * y_train_pred_ml) + ((1.0 - w) * y_train_pred_naive)
            m_mae = float(np.mean(np.abs(y_train - train_ens)))
            if m_mae < best_train_mae:
                best_train_mae = m_mae
                best_w_ml = w

        y_test_ensemble = (best_w_ml * y_test_ml) + ((1.0 - best_w_ml) * y_test_naive)
        ensemble_metrics = self.calculate_metrics(y_test, y_test_ensemble)

        # 5. ARIMA_SARIMA — evaluated on the same test window (graceful fallback)
        arima_metrics, y_test_arima = self._evaluate_arima(clean_df, split_idx, y)

        # Candidate Model Comparison
        all_models: Dict[str, Tuple[Dict, np.ndarray]] = {
            "NAIVE_BASELINE": (naive_metrics, y_test_naive),
            "MOVING_AVERAGE_7D": (ma_metrics, y_test_ma),
            "RIDGE_ML": (ml_metrics, y_test_ml),
            "WEIGHTED_ENSEMBLE": (ensemble_metrics, y_test_ensemble),
        }
        if arima_metrics is not None and y_test_arima is not None:
            all_models["ARIMA_SARIMA"] = (arima_metrics, y_test_arima)

        # Select Strategy with Lowest Test MAE
        def _safe_mae(key: str) -> float:
            mae = all_models[key][0].get("mae", float('inf'))
            return mae if isinstance(mae, (int, float)) else float('inf')

        best_strategy = min(all_models.keys(), key=_safe_mae)
        selected_metrics = all_models[best_strategy][0]

        # Build selection reason
        if best_strategy == "NAIVE_BASELINE":
            reason = f"Naive baseline achieved lowest MAE (₹{naive_metrics['mae']:,.2f}) on held-out test split (Ridge ML MAE: ₹{ml_metrics['mae']:,.2f})."
        elif best_strategy == "WEIGHTED_ENSEMBLE":
            reason = f"Weighted Ensemble ({best_w_ml:.2f} ML + {1-best_w_ml:.2f} Naive) achieved lowest MAE (₹{ensemble_metrics['mae']:,.2f}) on held-out test split."
        elif best_strategy == "RIDGE_ML":
            reason = f"Ridge ML model achieved lowest MAE (₹{ml_metrics['mae']:,.2f}) on held-out test split (Naive MAE: ₹{naive_metrics['mae']:,.2f})."
        elif best_strategy == "ARIMA_SARIMA":
            reason = (
                f"ARIMA SARIMA(2,1,3)(1,0,1,7) achieved lowest MAE (₹{arima_metrics['mae']:,.2f}) "
                f"on held-out test split (Naive MAE: ₹{naive_metrics['mae']:,.2f}, "
                f"Ridge ML MAE: ₹{ml_metrics['mae']:,.2f})."
            )
        else:
            reason = f"7-Day Moving Average achieved lowest MAE (₹{ma_metrics['mae']:,.2f}) on held-out test split."

        # If ARIMA did NOT win, clear CI bounds (no CI available from other models)
        if best_strategy != "ARIMA_SARIMA":
            self.ci_upper_bound = 0.0
            self.ci_lower_bound = 0.0

        self.selected_strategy = best_strategy
        self.selected_reason = reason
        self.metrics = selected_metrics
        self.all_model_metrics = {
            "ml_metrics": ml_metrics,
            "naive_metrics": naive_metrics,
            "ma_metrics": ma_metrics,
            "ensemble_metrics": ensemble_metrics,
            "arima_metrics": arima_metrics if arima_metrics is not None else {
                "mae": "NOT AVAILABLE", "rmse": "NOT AVAILABLE", "mape": "NOT AVAILABLE", "r2": "NOT AVAILABLE"
            },
        }
        self.is_validated = True

        model_outperforms = (ml_metrics["mae"] < naive_metrics["mae"])

        # Confidence Score Calculation Formula (model-agnostic):
        # confidence_score = 0.4*(1 - MAE/σ_y) + 0.3*max(0, R²) + 0.3*max(0, 1 - MAPE/20)
        y_std = float(np.std(y_test)) if len(y_test) > 1 else 1.0
        mae_ratio_score = max(0.0, min(1.0, 1.0 - (selected_metrics["mae"] / max(1.0, y_std))))
        r2_val = selected_metrics["r2"] if isinstance(selected_metrics["r2"], float) else 0.0
        r2_score = max(0.0, min(1.0, r2_val))
        mape_val = selected_metrics["mape"] if isinstance(selected_metrics["mape"], float) else 10.0
        mape_score = max(0.0, min(1.0, 1.0 - (mape_val / 20.0)))

        raw_conf = (0.4 * mae_ratio_score) + (0.3 * r2_score) + (0.3 * mape_score)
        if not model_outperforms and best_strategy != "NAIVE_BASELINE":
            raw_conf *= 0.85

        confidence_score = round(max(0.10, min(1.0, raw_conf)), 2)

        return {
            "selected_forecast_strategy": best_strategy,
            "reason": reason,
            "selected_metrics": selected_metrics,
            "ml_metrics": ml_metrics,
            "naive_metrics": naive_metrics,
            "ma_metrics": ma_metrics,
            "ensemble_metrics": ensemble_metrics,
            "arima_metrics": self.all_model_metrics["arima_metrics"],
            "model_outperforms_baseline": model_outperforms,
            "confidence_score": confidence_score,
            "train_samples_count": self.train_samples_count,
            "test_samples_count": self.test_samples_count,
            "test_date_range": self.test_date_range
        }

    def predict_30d(
        self,
        current_cash: float,
        receivable_delay_days: int = 0,
        extra_outflow: float = 0.0,
        expected_inflows: float = 0.0,
        expected_inflow_prob: float = 0.87
    ) -> Dict[str, Any]:
        """
        Produces 30-day cash projections.
        When ARIMA_SARIMA is the selected strategy, uses ARIMA net-flow forecasts
        to build projected_points. All other strategies use the existing 8-checkpoint
        schedule. In all cases, raw_projected_cash, display_projected_cash, and
        liquidity_deficit are preserved with the same contract shape.
        """
        if not self.is_validated:
            self.train_and_evaluate()

        if 'daily_outflow' in self.df.columns and len(self.df) > 0:
            avg_daily_outflow = float(self.df['daily_outflow'].mean())
            if avg_daily_outflow <= 0:
                avg_daily_outflow = 165000.0
        else:
            avg_daily_outflow = 165000.0

        # --- ARIMA path: use 30-step model forecast ---
        if self.selected_strategy == "ARIMA_SARIMA" and hasattr(self, '_arima_fitted') and self._arima_fitted is not None:
            projected_points = self._predict_30d_arima(
                current_cash=current_cash,
                extra_outflow=extra_outflow,
                expected_inflows=expected_inflows,
                expected_inflow_prob=expected_inflow_prob,
                receivable_delay_days=receivable_delay_days,
                avg_daily_outflow=avg_daily_outflow
            )
        else:
            projected_points = self._predict_30d_heuristic(
                current_cash=current_cash,
                extra_outflow=extra_outflow,
                expected_inflows=expected_inflows,
                expected_inflow_prob=expected_inflow_prob,
                receivable_delay_days=receivable_delay_days,
                avg_daily_outflow=avg_daily_outflow
            )

        min_raw_cash = min([p["raw_cash"] for p in projected_points])
        raw_projected_cash = projected_points[1]["raw_cash"] if len(projected_points) > 1 else (current_cash - extra_outflow - 1650000.0)

        display_projected_cash = max(0.0, raw_projected_cash)
        liquidity_deficit = max(0.0, -raw_projected_cash)

        return {
            "projected_points": projected_points,
            "raw_projected_cash": raw_projected_cash,
            "display_projected_cash": display_projected_cash,
            "liquidity_deficit": liquidity_deficit,
            "minimum_raw_projected_cash": min_raw_cash,
            "minimum_display_projected_cash": max(0.0, min_raw_cash),
            "forecast_metrics": self.metrics,
            "selected_strategy": self.selected_strategy,
            "confidence_score": self.metrics.get("r2", 0.70) if isinstance(self.metrics.get("r2"), float) else 0.50,
            "avg_daily_outflow": avg_daily_outflow,
            # CI bounds (non-zero only when ARIMA won selection)
            "ci_upper_bound": self.ci_upper_bound,
            "ci_lower_bound": self.ci_lower_bound,
        }

    def _predict_30d_arima(
        self,
        current_cash: float,
        extra_outflow: float,
        expected_inflows: float,
        expected_inflow_prob: float,
        receivable_delay_days: int,
        avg_daily_outflow: float
    ) -> List[Dict[str, Any]]:
        """Build projected_points using ARIMA 30-step net-flow forecast."""
        import warnings
        days_labels = [
            'Aug 28', 'Aug 29 (Opex)', 'Sep 01', 'Sep 05',
            'Sep 15', 'Sep 28 (Inflow)', 'Oct 08', 'Oct 18'
        ]
        n_steps = 30
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fc = self._arima_fitted.get_forecast(steps=n_steps)
                pm = fc.predicted_mean
                pred_net = pm.values if hasattr(pm, 'values') else np.asarray(pm)
                ci_raw = fc.conf_int(alpha=0.10)
                ci = ci_raw.values if hasattr(ci_raw, 'values') else np.asarray(ci_raw)  # (30, 2)

            running_cash = current_cash - extra_outflow
            all_30_points = []
            for i in range(n_steps):
                nf = float(pred_net[i])
                running_cash = running_cash + nf
                raw_cash = float(running_cash)
                display_cash = max(0.0, raw_cash)
                deficit = max(0.0, -raw_cash)
                cash_lakhs = round(raw_cash / 100000.0, 2)
                display_lakhs = round(display_cash / 100000.0, 2)
                all_30_points.append({
                    "day": f"Day {i+1}",
                    "raw_cash": raw_cash,
                    "display_cash": display_cash,
                    "liquidity_deficit": deficit,
                    "cash": display_lakhs,
                    "raw_cash_lakhs": cash_lakhs,
                    "pessimistic": round(max(0.0, display_lakhs - 1.5), 2)
                })

            # Update CI bounds from the final 30-step forecast
            last_train_bal = current_cash - extra_outflow
            self.ci_lower_bound = last_train_bal + float(np.cumsum(ci[:, 0])[-1])
            self.ci_upper_bound = last_train_bal + float(np.cumsum(ci[:, 1])[-1])

            # Return 8 representative checkpoints (matching heuristic path contract)
            checkpoint_indices = [0, 1, 2, 4, 14, 27, 29, 29]
            projected_points = []
            for idx, ci_idx in enumerate(checkpoint_indices):
                pt = dict(all_30_points[ci_idx])
                pt["day"] = days_labels[idx]
                projected_points.append(pt)
            return projected_points

        except Exception as e:
            print(f"Warning: ARIMA predict_30d failed, falling back to heuristic: {e}")
            return self._predict_30d_heuristic(
                current_cash=current_cash,
                extra_outflow=extra_outflow,
                expected_inflows=expected_inflows,
                expected_inflow_prob=expected_inflow_prob,
                receivable_delay_days=receivable_delay_days,
                avg_daily_outflow=avg_daily_outflow
            )

    def _predict_30d_heuristic(
        self,
        current_cash: float,
        extra_outflow: float,
        expected_inflows: float,
        expected_inflow_prob: float,
        receivable_delay_days: int,
        avg_daily_outflow: float
    ) -> List[Dict[str, Any]]:
        """Original 8-checkpoint heuristic projection (Naive/MA/Ridge/Ensemble path)."""
        days = ['Aug 28', 'Aug 29 (Opex)', 'Sep 01', 'Sep 05', 'Sep 15', 'Sep 28 (Inflow)', 'Oct 08', 'Oct 18']
        projected_points = []
        running_cash = current_cash - extra_outflow

        for idx, day in enumerate(days):
            if idx == 0:
                cash_val = running_cash
            elif idx == 1:
                cash_val = running_cash - 1650000.0
            elif idx == 5:
                inflow_factor = max(0.1, expected_inflow_prob - (receivable_delay_days * 0.08))
                net_inflow = (expected_inflows if expected_inflows > 0 else 31760.96) * inflow_factor
                cash_val = projected_points[-1]["raw_cash"] + net_inflow - (avg_daily_outflow * 0.5)
            else:
                cash_val = projected_points[-1]["raw_cash"] - (avg_daily_outflow * 0.4)

            raw_cash = float(cash_val)
            display_cash = max(0.0, raw_cash)
            deficit = max(0.0, -raw_cash)
            cash_lakhs = round(raw_cash / 100000.0, 2)
            display_lakhs = round(display_cash / 100000.0, 2)

            projected_points.append({
                "day": day,
                "raw_cash": raw_cash,
                "display_cash": display_cash,
                "liquidity_deficit": deficit,
                "cash": display_lakhs,
                "raw_cash_lakhs": cash_lakhs,
                "pessimistic": round(max(0.0, display_lakhs - 1.5), 2)
            })

        return projected_points
