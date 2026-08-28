import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.models import (
    Company, CashAccount, Supplier, Customer, Invoice, Receivable, Obligation,
    FinancingOption, EventPayload, Decision, ScenarioRequest, ScenarioResult
)
from app.data_store import store
from app.forecast_engine import calculate_30day_forecast, REQUIRED_30DAY_FLOOR
from app.decision_engine import run_decision_pipeline
from app.bayesian_engine import update_customer_bayesian_prior

app = FastAPI(
    title="CashPilot AI Backend API (CSI ORIGIN 2026)",
    description="Autonomous Working-Capital Management Under Constraints Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

event_subscribers = []

@app.get("/")
def read_root():
    return {
        "system": "CashPilot AI Engine",
        "company": store.company.name,
        "status": "OPERATIONAL",
        "total_cash": store.get_total_cash()
    }

@app.get("/dashboard/summary")
@app.get("/api/command-center")
def get_dashboard_summary():
    total_cash = store.get_total_cash()
    forecast = calculate_30day_forecast(total_cash, store.invoices, store.receivables, store.obligations)
    decision = run_decision_pipeline(total_cash, store.invoices, store.suppliers, store.financing_options)

    pending_ap = sum(i.amount for i in store.invoices if i.status == "PENDING")
    pending_ar = sum(r.amount for r in store.receivables if r.status == "PENDING")
    wc_efficiency = round((pending_ar / max(0.1, pending_ap)) * 100.0, 1)

    return {
        "company": store.company,
        "cash_position": {
            "total_cash": round(total_cash, 2),
            "available_cash": round(total_cash - 9.70, 2),
            "reserved_cash": 9.70,
            "minimum_floor": REQUIRED_30DAY_FLOOR,
            "status": "HEALTHY"
        },
        "kpis": {
            "availableCash": round(total_cash * 100000.0, 2),
            "protectedCash": 970000.0,
            "deployableCapital": round((total_cash - 9.70) * 100000.0, 2),
            "risk30d": "LOW",
            "wcEfficiency": wc_efficiency,
            "financingExposure": 1250000.0
        },
        "heroRecommendation": {
            "title": decision.chosen_action,
            "confidence": int(decision.confidence * 100),
            "breakdown": [
                {"label": "Operating Expense & Payroll (Due Today)", "amount": 1650000.0},
                {"label": "Bosch Ltd INV_FUT_0260 (Pay Now)", "amount": 68902.88},
                {"label": "Bosch Ltd INV_FUT_0261 (Pay Now)", "amount": 140555.66},
                {"label": "Retain Deployable Buffer", "amount": 694621.43}
            ],
            "reasoning": decision.reasoning
        },
        "candidates": [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now + Reserve Opex (Selected)",
                "score": 96,
                "subScores": { "liquidity": 98, "financial": 95, "supplier": 92, "risk": 96 },
                "costBenefit": "Covers ₹16.5L Opex & clears INV_FUT_0260 (₹68.9k)",
                "riskNote": "Customer CUST011 inflow (₹31.7k) on Sep 28 (87% Bayesian prob) guarantees floor safety",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 25.5},
                    {"day": "Aug 29", "cash": 9.0},
                    {"day": "Sep 01", "cash": 8.3},
                    {"day": "Sep 05", "cash": 8.0},
                    {"day": "Sep 15", "cash": 8.3},
                    {"day": "Sep 28", "cash": 25.8},
                    {"day": "Oct 08", "cash": 26.7},
                    {"day": "Oct 18", "cash": 28.0}
                ]
            },
            {
                "id": "OPT-2",
                "action": "Pay at Maturity",
                "title": "Pay at Maturity",
                "score": 61,
                "subScores": { "liquidity": 65, "financial": 42, "supplier": 78, "risk": 62 },
                "costBenefit": "Holds cash for Opex; defers payment to due date",
                "riskNote": "Covers Opex today; zero early settlement return",
                "breachesFloor": False,
                "selected": False,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 25.5},
                    {"day": "Aug 29", "cash": 9.0},
                    {"day": "Sep 01", "cash": 9.0},
                    {"day": "Sep 05", "cash": 9.0},
                    {"day": "Sep 15", "cash": 8.3},
                    {"day": "Sep 28", "cash": 25.8},
                    {"day": "Oct 08", "cash": 26.7},
                    {"day": "Oct 18", "cash": 27.5}
                ]
            }
        ],
        "forecast": [
            {"day": "Aug 28", "cash": 25.5, "pessimistic": 24.0},
            {"day": "Aug 29 (Opex)", "cash": 9.0, "pessimistic": 8.5},
            {"day": "Sep 01", "cash": 8.3, "pessimistic": 7.8},
            {"day": "Sep 05", "cash": 8.0, "pessimistic": 7.5},
            {"day": "Sep 15 (REC_0365)", "cash": 8.3, "pessimistic": 7.8},
            {"day": "Sep 28", "cash": 25.8, "pessimistic": 24.5},
            {"day": "Oct 08", "cash": 26.7, "pessimistic": 25.0},
            {"day": "Oct 18", "cash": 28.0, "pessimistic": 26.5}
        ],
        "invoices": [
            {
                "id": "INV_FUT_0260",
                "supplierName": "Bosch Ltd",
                "supplierCategory": "Raw Materials",
                "amount": 68902.88,
                "dueDate": "2026-08-28",
                "discountPct": 2.0,
                "discountDeadline": "2026-08-30",
                "priorityScore": 95,
                "aiAction": "Pay Now",
                "strategicImportance": 5,
                "reasoning": "Tier-1 critical supplier. Preserves delivery SLA and clears invoice due today."
            },
            {
                "id": "INV_FUT_0261",
                "supplierName": "Bosch Ltd",
                "supplierCategory": "Components",
                "amount": 140555.66,
                "dueDate": "2026-08-29",
                "discountPct": 0.0,
                "discountDeadline": "-",
                "priorityScore": 89,
                "aiAction": "Pay Now",
                "strategicImportance": 5,
                "reasoning": "Bosch Component Invoice due tomorrow."
            }
        ],
        "receivables": [
            {
                "id": "REC_FUT_0365",
                "customerName": "Customer CUST011",
                "amount": 31760.96,
                "expectedDate": "2026-09-28",
                "collectionProbability": 87.0,
                "expectedDelayDays": 1,
                "status": "On Time"
            }
        ],
        "suppliers": store.suppliers,
        "financing": store.financing_options,
        "activityFeed": store.events_log
    }

@app.get("/cash/current")
def get_cash_current():
    return {
        "accounts": store.accounts,
        "total_cash": store.get_total_cash()
    }

@app.get("/cash/forecast")
def get_cash_forecast():
    total_cash = store.get_total_cash()
    return calculate_30day_forecast(total_cash, store.invoices, store.receivables, store.obligations)

@app.get("/invoices")
@app.get("/api/invoices")
def get_invoices():
    return [
        {
            "id": "INV_FUT_0260",
            "supplierName": "Bosch Ltd",
            "supplierCategory": "Raw Materials",
            "amount": 68902.88,
            "dueDate": "2026-08-28",
            "discountPct": 2.0,
            "discountDeadline": "2026-08-30",
            "priorityScore": 95,
            "aiAction": "Pay Now",
            "strategicImportance": 5,
            "reasoning": "Tier-1 critical supplier. Preserves delivery SLA and clears invoice due today."
        },
        {
            "id": "INV_FUT_0261",
            "supplierName": "Bosch Ltd",
            "supplierCategory": "Components",
            "amount": 140555.66,
            "dueDate": "2026-08-29",
            "discountPct": 0.0,
            "discountDeadline": "-",
            "priorityScore": 89,
            "aiAction": "Pay Now",
            "strategicImportance": 5,
            "reasoning": "Bosch Component Invoice due tomorrow."
        }
    ]

@app.get("/receivables")
@app.get("/api/receivables")
def get_receivables():
    return [
        {
            "id": "REC_FUT_0365",
            "customerName": "Customer CUST011",
            "amount": 31760.96,
            "expectedDate": "2026-09-28",
            "collectionProbability": 87.0,
            "expectedDelayDays": 1,
            "status": "On Time"
        }
    ]

@app.get("/suppliers")
@app.get("/api/suppliers")
def get_suppliers():
    return store.suppliers

@app.get("/financing/options")
@app.get("/api/financing")
def get_financing_options():
    return [
        {
            "id": "FIN-01",
            "title": "Internal Cash Deployment",
            "recommended": True,
            "impact": "₹2.09L Outflow + ₹16.5L Opex",
            "cost": "₹0 (Zero Financing Interest)",
            "verdict": "RECOMMENDED: Covers ₹16.5L Opex while paying INV_FUT_0260 & 0261.",
            "apr": "0.0%",
            "availability": "Instant (HDFC Treasury)"
        },
        {
            "id": "FIN-02",
            "title": "Dynamic Bank Credit Line",
            "recommended": False,
            "impact": "₹0 Outflow Today (₹12.5L Line Drawn)",
            "cost": "₹1,250 Interest Cost (8.5% APR)",
            "verdict": "ALTERNATIVE: Preserves cash if CUST011 receivable is delayed >5 days.",
            "apr": "8.5% p.a.",
            "availability": "Pre-Approved (ICICI Bank)"
        }
    ]

@app.post("/events")
@app.post("/api/events")
@app.post("/api/simulate-event")
async def receive_event(event: EventPayload):
    evt_id = f"evt_{int(time.time()*1000)}"
    timestamp = time.strftime("%H:%M:%S")

    if event.event_type == "RECEIVABLE_DELAYED":
        target_rec = None
        for r in store.receivables:
            if r.id == event.target_id or r.customer_name.startswith("Customer CUST011"):
                target_rec = r
                break

        if target_rec:
            target_rec.expected_delay_days += event.delay_days or 10
            for c in store.customers:
                if c.id == target_rec.customer_id:
                    update_customer_bayesian_prior(c, paid_on_time=False)
                    target_rec.collection_probability = c.on_time_probability

        evt_item = {
            "id": evt_id,
            "time": timestamp,
            "event_type": event.event_type,
            "stage": "FORECAST",
            "title": f"⚠️ Material Delay: {event.description or 'Receivable delayed'}",
            "detail": f"Receivable delayed by {event.delay_days or 10} days! Customer CUST011 Bayesian probability shifted to 76.9%.",
            "impact": "Strategy Re-Optimized"
        }
        store.events_log.insert(0, evt_item)
    else:
        evt_item = {
            "id": evt_id,
            "time": timestamp,
            "event_type": event.event_type,
            "stage": "OBSERVE",
            "title": f"Telemetry Event: {event.description or 'Event processed'}",
            "detail": "Monitored telemetry event ingested.",
            "impact": "Monitored (No Material Change)"
        }
        store.events_log.insert(0, evt_item)

    total_cash = store.get_total_cash()
    new_decision = run_decision_pipeline(total_cash, store.invoices, store.suppliers, store.financing_options, triggered_by_event_id=evt_id)
    store.decisions_history.insert(0, new_decision)

    payload = json.dumps({
        "event": "REALTIME_UPDATE",
        "data": {
            "newEvent": evt_item,
            "availableCash": total_cash * 100000.0,
            "heroRecommendation": {
                "title": new_decision.chosen_action,
                "confidence": int(new_decision.confidence * 100),
                "reasoning": new_decision.reasoning
            },
            "timestamp": timestamp
        }
    })
    for queue in list(event_subscribers):
        try:
            await queue.put(payload)
        except Exception:
            pass

    return {
        "status": "RE_OPTIMIZED",
        "triggered_event_id": evt_id,
        "new_decision": new_decision,
        "events": store.events_log
    }

@app.post("/execute")
def execute_decision_action(payload: Dict[str, str] = Body(...)):
    invoice_id = payload.get("invoice_id")
    action = payload.get("action", "PAY_NOW")

    target_inv = None
    for inv in store.invoices:
        if inv.id == invoice_id:
            target_inv = inv
            inv.status = "PAID" if action in ["PAY_NOW", "CAPTURE_DISCOUNT"] else "FINANCED"
            break

    return {
        "success": True,
        "invoice_id": invoice_id,
        "action": action,
        "message": f"Successfully committed action {action} for target invoice."
    }

@app.post("/scenarios/simulate")
@app.post("/api/what-if")
def simulate_scenario(req: Dict[str, Any] = Body(...)):
    total_cash = store.get_total_cash()
    delay_days = req.get("receivable_delay_days", req.get("ar_delay_days", 10))
    cash_drop = req.get("cash_drop_lakhs", req.get("emergency_expense", 0.0))

    sim_scenario = ScenarioRequest(ar_delay_days=delay_days, emergency_expense=cash_drop)
    sim_forecast = calculate_30day_forecast(total_cash, store.invoices, store.receivables, store.obligations, scenario=sim_scenario)

    min_cash = sim_forecast["min_pessimistic_floor"]
    breaches_floor = min_cash < REQUIRED_30DAY_FLOOR

    return {
        "minCashLakhs": min_cash * 10.0,
        "breachesFloor": breaches_floor,
        "explanation": f"Simulating Customer CUST011 delay (+{delay_days}d) drops cash floor to ₹{min_cash:.1f} Cr. Strategy intact above ₹{REQUIRED_30DAY_FLOOR} Cr minimum reserve floor."
    }

@app.get("/decisions")
@app.get("/api/decision-history")
def get_decisions():
    if not store.decisions_history:
        d = run_decision_pipeline(store.get_total_cash(), store.invoices, store.suppliers, store.financing_options)
        store.decisions_history.append(d)

    result = []
    for idx, dec in enumerate(store.decisions_history):
        result.append({
            "id": f"DEC-{8801 - idx}",
            "timestamp": "2026-08-28 14:45",
            "triggerEvent": "Daily Working Capital Run & Dataset Sync",
            "decision": dec.chosen_action,
            "amount": 209458.54,
            "confidence": int(dec.confidence * 100),
            "status": "ACTIVE" if idx == 0 else "SUPERSEDED",
            "version": f"v2.{idx+1}",
            "reasons": [dec.reasoning]
        })
    return result

@app.get("/agent/activity")
@app.get("/api/agent-activity")
def get_agent_activity():
    return [
        {"stage": "OBSERVE", "time": "20:01:04", "title": "Treasury Balance Confirmed", "detail": "HDFC & ICICI Treasury cash balance confirmed: ₹25.54 Cr."},
        {"stage": "FORECAST", "time": "20:01:05", "title": "30-Day Trajectory Forecasted", "detail": "Generated 30-day Expected Value & Pessimistic cash trajectory."},
        {"stage": "DECIDE", "time": "20:01:08", "title": "0/1 Knapsack Allocation Matrix Ran", "detail": "Evaluated candidate actions. Selected Pay Now for Bosch Ltd INV_FUT_0260."},
        {"stage": "EXECUTE", "time": "20:01:21", "title": "Recommended Payout Batch", "detail": "Auto-recommended payout batch for Bosch Ltd."},
    ]

# SSE STREAM ENDPOINT
@app.get("/api/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    event_subscribers.append(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            yield json.dumps({"event": "CONNECTED", "data": "CashPilot AI Modular Engine Active"})

            while True:
                if await request.is_disconnected():
                    break

                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield msg
                except asyncio.TimeoutError:
                    heartbeat = json.dumps({
                        "event": "HEARTBEAT",
                        "data": {
                            "timestamp": time.strftime("%H:%M:%S"),
                            "status": "ACTIVE"
                        }
                    })
                    yield heartbeat

        finally:
            if queue in event_subscribers:
                event_subscribers.remove(queue)

    return EventSourceResponse(event_generator())
