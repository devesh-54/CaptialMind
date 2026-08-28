from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class EntityArchetype(str, Enum):
    RELIABLE = "reliable"
    AVERAGE = "average"
    RISKY = "risky"

class SupplierArchetype(str, Enum):
    CRITICAL = "critical"
    STANDARD = "standard"
    LOW_STAKES = "low-stakes"

class ActionType(str, Enum):
    PAY_NOW = "PAY_NOW"
    PAY_AT_MATURITY = "PAY_AT_MATURITY"
    DELAY = "DELAY"
    CAPTURE_DISCOUNT = "CAPTURE_DISCOUNT"
    BANK_FINANCE = "BANK_FINANCE"
    SUPPLIER_FINANCE = "SUPPLIER_FINANCE"
    RETAIN_CASH = "RETAIN_CASH"

class DecisionStatus(str, Enum):
    RECOMMENDED = "Recommended"
    PENDING_APPROVAL = "Pending Approval"
    EXECUTED = "Executed"
    SUPERSEDED = "Superseded"

class Company(BaseModel):
    id: str = "comp_novatech"
    name: str = "NovaTech Manufacturing Pvt. Ltd."
    currency: str = "₹ Cr"
    minimum_cash_reserve: float = 18.5  # ₹18.5 Cr floor

class CashAccount(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    name: str
    account_type: str
    balance: float
    available_balance: float
    yield_rate: float = 0.0

class Supplier(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    name: str
    strategic_importance: float  # 0.1 to 1.0
    liquidity_risk: str         # Low, Moderate, High
    payment_terms: str          # Net-30, 2/10 Net-30, etc.
    archetype: SupplierArchetype = SupplierArchetype.STANDARD

class Customer(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    name: str
    archetype: EntityArchetype = EntityArchetype.AVERAGE
    alpha: int = 1               # Beta prior success count
    beta: int = 1                # Beta prior failure count
    on_time_probability: float = 0.80
    average_delay_days: float = 5.0

class Invoice(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    amount: float
    issue_date: str
    due_date: str
    due_days: int
    discount_percentage: float = 0.0
    discount_deadline_days: int = 0
    late_penalty_percentage: float = 0.0
    priority_score: float = 0.0
    status: str = "PENDING"
    recommended_action: Optional[ActionType] = ActionType.PAY_NOW
    action_reason: Optional[str] = None

class Receivable(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    amount: float
    expected_date: str
    due_days: int
    collection_probability: float
    expected_delay_days: float
    status: str = "PENDING"
    probability_history: List[float] = Field(default_factory=list)

class Obligation(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    description: str
    amount: float
    due_days: int
    priority: str
    status: str = "PENDING"

class FinancingOption(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    provider: str
    type: str  # Revolving Credit, Invoice Factoring, Supply Chain Finance
    interest_rate_annual: float
    credit_limit: float
    available_amount: float
    processing_fee: float = 0.0
    recommended: bool = False

class EventPayload(BaseModel):
    event_type: str  # NEW_INVOICE, PAYMENT_RECEIVED, RECEIVABLE_DELAYED, NEW_OBLIGATION, FINANCING_RATE_CHANGED, SUPPLIER_RISK_CHANGED
    target_id: Optional[str] = None
    delay_days: Optional[int] = 0
    amount: Optional[float] = 0.0
    description: Optional[str] = None

class CandidateActionScore(BaseModel):
    action: ActionType
    invoice_id: str
    invoice_name: str
    raw_liquidity: float
    raw_financial: float
    raw_supplier: float
    raw_risk: float
    norm_liquidity: float
    norm_financial: float
    norm_supplier: float
    norm_risk: float
    utility_score: float
    cost_cash: float
    cost_financing: float
    sparkline_cash_trajectory: List[float] = Field(default_factory=list)
    reasoning: str

class DecisionItem(BaseModel):
    id: str
    invoice_id: str
    invoice_name: str
    action: ActionType
    amount: float
    expected_cost: float
    expected_benefit: float
    risk_score: float
    utility_score: float

class Decision(BaseModel):
    id: str
    company_id: str = "comp_novatech"
    created_at: str
    chosen_action: str
    allocations: List[DecisionItem]
    alternatives: List[CandidateActionScore]
    weights: Dict[str, float]
    cash_buffer_ratio: float
    total_budget_spent: float
    achieved_utility: float
    next_best_gap: float
    confidence: float
    status: DecisionStatus = DecisionStatus.RECOMMENDED
    triggered_by_event_id: Optional[str] = None
    reasoning: str

class ScenarioRequest(BaseModel):
    name: str = "Custom Scenario"
    ar_delay_days: int = 10
    revenue_shock_percent: float = 0.0
    emergency_expense: float = 0.0

class ScenarioResult(BaseModel):
    scenario_name: str
    before_status: str
    after_status: str
    before_cash_floor: float
    after_cash_floor: float
    strategy_before: str
    strategy_after: str
    reallocated_amount: float
    diff_reasoning: str
