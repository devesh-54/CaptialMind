import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class CashData:
    current_cash: float = 0.0
    opening_balance: float = 0.0
    available_balance: float = 0.0
    reserved_balance: float = 970000.0
    deployable_cash: float = 0.0
    daily_inflow: float = 0.0
    daily_outflow: float = 0.0

@dataclass
class ForecastData:
    raw_projected_cash: float = 0.0
    display_projected_cash: float = 0.0
    liquidity_deficit: float = 0.0
    minimum_raw_projected_cash: float = 0.0
    minimum_display_projected_cash: float = 0.0
    selected_strategy: str = "NAIVE_BASELINE"
    confidence_score: float = 0.70
    mae: Any = "NOT AVAILABLE"
    rmse: Any = "NOT AVAILABLE"
    mape: Any = "NOT AVAILABLE"
    r2: Any = "NOT AVAILABLE"
    projected_points: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ReceivableItem:
    id: str
    customer_id: str
    customer_name: str
    amount: float
    expected_payment_date: str
    collection_probability: float  # Scale 0.0 to 1.0 (e.g. 0.87)
    expected_delay_days: int = 0
    payment_status: str = "PENDING"
    
    @property
    def expected_cash_contribution(self) -> float:
        """Phase 9: Expected contribution = Amount x Collection Probability"""
        return max(0.0, self.amount * max(0.0, min(1.0, self.collection_probability)))

@dataclass
class PayableItem:
    id: str
    supplier_id: str
    supplier_name: str
    amount: float
    due_date: str
    discount_percentage: float = 0.0
    discount_deadline: str = "-"
    late_penalty_percentage: float = 0.0
    payment_status: str = "UNPAID"
    strategic_importance: int = 3  # 1-5 scale
    is_critical: bool = False

@dataclass
class ObligationItem:
    id: str
    description: str
    amount: float
    due_date: str
    priority: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    is_critical: bool = False

@dataclass
class OtherFinancials:
    operating_expenses: float = 0.0
    unexpected_expenses: float = 0.0
    loan_draws: float = 0.0
    loan_repayments: float = 0.0
    interest_payments: float = 0.0

class FinancialState:
    """
    Unified representation of the enterprise financial state.
    Preserves raw negative cash values and liquidity deficit.
    Sanitizes float inputs to guard against NaN / Inf.
    """
    def __init__(
        self,
        cash: CashData,
        forecast: ForecastData,
        receivables: List[ReceivableItem] = None,
        payables: List[PayableItem] = None,
        obligations: List[ObligationItem] = None,
        other_financials: OtherFinancials = None,
        configured_min_reserve: float = 970000.0
    ):
        self.cash = cash
        self.forecast = forecast
        self.receivables = receivables if receivables is not None else []
        self.payables = payables if payables is not None else []
        self.obligations = obligations if obligations is not None else []
        self.other_financials = other_financials if other_financials is not None else OtherFinancials()
        self.configured_min_reserve = configured_min_reserve
        
        self._sanitize_state()

    def _sanitize_val(self, val: Any, default: float = 0.0) -> float:
        try:
            f_val = float(val)
            if math.isnan(f_val) or math.isinf(f_val):
                return default
            return f_val
        except (ValueError, TypeError):
            return default

    def _sanitize_state(self):
        self.cash.current_cash = max(0.0, self._sanitize_val(self.cash.current_cash))
        self.cash.opening_balance = max(0.0, self._sanitize_val(self.cash.opening_balance))
        self.cash.available_balance = max(0.0, self._sanitize_val(self.cash.available_balance))
        self.cash.reserved_balance = max(0.0, self._sanitize_val(self.cash.reserved_balance, 970000.0))
        self.cash.deployable_cash = max(0.0, self._sanitize_val(self.cash.deployable_cash))
        self.cash.daily_inflow = max(0.0, self._sanitize_val(self.cash.daily_inflow))
        self.cash.daily_outflow = max(0.0, self._sanitize_val(self.cash.daily_outflow))

        self.forecast.raw_projected_cash = self._sanitize_val(self.forecast.raw_projected_cash)
        self.forecast.display_projected_cash = max(0.0, self.forecast.raw_projected_cash)
        self.forecast.liquidity_deficit = max(0.0, -self.forecast.raw_projected_cash)
        self.forecast.minimum_raw_projected_cash = self._sanitize_val(self.forecast.minimum_raw_projected_cash)
        self.forecast.minimum_display_projected_cash = max(0.0, self.forecast.minimum_raw_projected_cash)
        self.forecast.confidence_score = max(0.0, min(1.0, self._sanitize_val(self.forecast.confidence_score, 0.70)))

        for r in self.receivables:
            r.amount = max(0.0, self._sanitize_val(r.amount))
            r.collection_probability = max(0.0, min(1.0, self._sanitize_val(r.collection_probability, 0.87)))
            r.expected_delay_days = max(0, int(self._sanitize_val(r.expected_delay_days, 0)))

        for p in self.payables:
            p.amount = max(0.0, self._sanitize_val(p.amount))
            p.discount_percentage = max(0.0, min(100.0, self._sanitize_val(p.discount_percentage)))
            p.late_penalty_percentage = max(0.0, min(100.0, self._sanitize_val(p.late_penalty_percentage)))

        for o in self.obligations:
            o.amount = max(0.0, self._sanitize_val(o.amount))

    @property
    def total_expected_receivables(self) -> float:
        return sum([r.expected_cash_contribution for r in self.receivables])

    @property
    def total_critical_obligations(self) -> float:
        crit_ob = sum([o.amount for o in self.obligations if o.priority == "CRITICAL" or o.is_critical])
        crit_pay = sum([p.amount for p in self.payables if p.is_critical])
        return crit_ob + crit_pay + self.other_financials.operating_expenses
