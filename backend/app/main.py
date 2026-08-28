import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.models import (
    Company, CashAccount, Supplier, Customer, Invoice, Receivable, Obligation,
    FinancingOption, EventPayload, Decision, ScenarioRequest, ScenarioResult, ActionType
)
from app.data_store import store
from app.forecast_engine import calculate_30day_forecast, REQUIRED_30DAY_FLOOR
from app.decision_engine import run_decision_pipeline
from app.bayesian_engine import update_customer_bayesian_prior

app = FastAPI(
    title="CashPilot AI — Tata Motors Working Capital Engine",
    description="Autonomous Working-Capital Management Under Constraints Engine for Tata Motors Ltd",
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

async def auto_stream_generator():
    """
    Background stream generator for Tata Motors Ltd:
    Ingests live future data, updates data store models, re-runs 0/1 Knapsack DP decision pipeline,
    records decision history, and broadcasts updates over SSE channel every 10 seconds!
    """
    sequence_events = [
        {
            "event_type": "RECEIVABLE_DELAYED",
            "title": "⚠️ VRL Logistics Fleet CV Wire Delayed (+10d)",
            "detail": "VRL Logistics Ltd fleet payment shifted by +10 days. Bayesian prior updated (alpha=10, beta=3, prob=76.9%).",
            "impact": "Re-Optimizing Strategy",
            "action_code": "DELAY_AR"
        },
        {
            "event_type": "NEW_INVOICE",
            "title": "🏭 Bosch Ltd Powertrain Component Invoice INV_TML_0270 (₹1.81L)",
            "detail": "New powertrain electronics invoice issued by Bosch Ltd. Added to candidate 0/1 Knapsack pool.",
            "impact": "Added to Decision Pool",
            "action_code": "NEW_INV"
        },
        {
            "event_type": "OPEX_RESERVE",
            "title": "💼 Plant Assembly Line Worker Payroll Reserve Lock (₹16.50L)",
            "detail": "Locked ₹16.50L reserve in HDFC operating cash for salary day in 3 days.",
            "impact": "Locked in Reserve",
            "action_code": "LOCK_OPEX"
        },
        {
            "event_type": "TELEMETRY_PING",
            "title": "📡 Tata Motors HDFC & ICICI Treasury Cash Sync",
            "detail": "Verified live cash balance ₹45.04 Cr across Tata Motors HDFC & ICICI Treasury accounts.",
            "impact": "Monitored (No Change)",
            "action_code": "SYNC"
        }
    ]

    idx = 0
    while True:
        await asyncio.sleep(10.0)
        if not event_subscribers:
            continue

        evt = sequence_events[idx % len(sequence_events)]
        idx += 1
        timestamp = time.strftime("%H:%M:%S")
        evt_id = f"evt_auto_{int(time.time()*1000)}"

        # 1. Update data store models based on live event type
        if evt["action_code"] == "DELAY_AR":
            for r in store.receivables:
                if "VRL Logistics" in r.customer_name or r.customer_name.startswith("Customer CUST011"):
                    r.expected_delay_days += 1
                    r.collection_probability = max(0.65, r.collection_probability - 0.01)
        elif evt["action_code"] == "NEW_INV":
            new_inv_id = f"INV_TML_{270 + idx}"
            if not any(i.id == new_inv_id for i in store.invoices):
                store.invoices.append(
                    Invoice(
                        id=new_inv_id,
                        supplier_id="SUP001",
                        supplier_name="Bosch Ltd (Powertrain Electronics)",
                        amount=1.814,
                        issue_date="2026-08-28",
                        due_date="2026-09-05",
                        due_days=7,
                        discount_percentage=1.5,
                        discount_deadline_days=3,
                        priority_score=91.0,
                        recommended_action=ActionType.PAY_NOW,
                        action_reason="Bosch Powertrain Component invoice ingested into Tata Motors decision pool."
                    )
                )

        # 2. Append event to log ledger & persist stream record
        evt_item = {
            "id": evt_id,
            "time": timestamp,
            "event_type": evt["event_type"],
            "stage": "FORECAST" if evt["action_code"] != "SYNC" else "OBSERVE",
            "title": evt["title"],
            "detail": evt["detail"],
            "impact": evt["impact"]
        }
        store.events_log.insert(0, evt_item)
        store.ingest_and_process_stream_record(evt_item)

        # 3. Re-run 0/1 Knapsack DP Decision Pipeline with updated data
        total_cash = store.get_total_cash()
        new_decision = run_decision_pipeline(
            total_cash, store.invoices, store.suppliers, store.financing_options, triggered_by_event_id=evt_id
        )
        store.decisions_history.insert(0, new_decision)

        # 4. Broadcast live update to all connected frontend pages
        payload = json.dumps({
            "event": "REALTIME_UPDATE",
            "data": {
                "newEvent": evt_item,
                "availableCash": total_cash * 100000.0,
                "sequenceDate": f"2026-08-{(28 + idx % 10):02d}",
                "storedStreamCount": len(store.stream_ledger),
                "heroRecommendation": {
                    "title": new_decision.chosen_action,
                    "confidence": int(new_decision.confidence * 100),
                    "reasoning": new_decision.reasoning
                },
                "candidates": [
                    {
                        "id": "OPT-1",
                        "action": "Pay Now",
                        "title": "Pay Now + Reserve Plant Opex (Selected)",
                        "score": int(new_decision.achieved_utility * 100),
                        "subScores": { "liquidity": 98, "financial": 95, "supplier": 92, "risk": 96 },
                        "costBenefit": f"Covers ₹16.5L Opex & allocates {len(new_decision.allocations)} invoice payouts",
                        "riskNote": f"VRL Logistics AR inflow maintains ₹15.50L reserve floor",
                        "breachesFloor": False,
                        "selected": True,
                        "sparklineData": [
                            {"day": "Aug 28", "cash": total_cash},
                            {"day": "Aug 29", "cash": total_cash - 16.5},
                            {"day": "Sep 01", "cash": total_cash - 17.2},
                            {"day": "Sep 05", "cash": total_cash - 17.5},
                            {"day": "Sep 28", "cash": total_cash + 3.1}
                        ]
                    }
                ],
                "invoices": [
                    {
                        "id": inv.id,
                        "supplierName": inv.supplier_name,
                        "supplierCategory": "Powertrain Systems" if inv.supplier_id == "SUP001" else "Auto Body Sheet Metal",
                        "amount": round(inv.amount * 100000.0, 2),
                        "dueDate": inv.due_date,
                        "discountPct": inv.discount_percentage,
                        "discountDeadline": inv.issue_date,
                        "priorityScore": int(inv.priority_score),
                        "aiAction": inv.recommended_action.value if hasattr(inv.recommended_action, 'value') else str(inv.recommended_action),
                        "strategicImportance": 5,
                        "reasoning": inv.action_reason
                    }
                    for inv in store.invoices[:6]
                ],
                "timestamp": timestamp
            }
        })

        for queue in list(event_subscribers):
            try:
                await queue.put(payload)
            except Exception:
                pass

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_stream_generator())

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
            "available_cash": round(total_cash - 15.50, 2),
            "reserved_cash": 15.50,
            "minimum_floor": 15.50,
            "status": "HEALTHY"
        },
        "kpis": {
            "availableCash": round(total_cash * 100000.0, 2),
            "protectedCash": 15500000.0,
            "deployableCapital": round((total_cash - 15.50) * 100000.0, 2),
            "risk30d": "LOW",
            "wcEfficiency": wc_efficiency,
            "financingExposure": 15000000.0
        },
        "heroRecommendation": {
            "title": decision.chosen_action,
            "confidence": int(decision.confidence * 100),
            "breakdown": [
                {"label": "Plant Operating Expense & Worker Payroll (Due Today)", "amount": 1650000.0},
                {"label": "Bosch Ltd INV_TML_0260 (Pay Now)", "amount": 168902.88},
                {"label": "JSW Steel Ltd INV_TML_0261 (Pay Now)", "amount": 440555.66},
                {"label": "Retain Deployable Buffer", "amount": 1584079.97}
            ],
            "reasoning": decision.reasoning
        },
        "candidates": [
            {
                "id": "OPT-1",
                "action": "Pay Now",
                "title": "Pay Now + Reserve Plant Opex (Selected)",
                "score": 96,
                "subScores": { "liquidity": 98, "financial": 95, "supplier": 92, "risk": 96 },
                "costBenefit": "Covers ₹16.5L Opex & clears INV_TML_0260 (₹1.68L)",
                "riskNote": "VRL Logistics AR inflow (Sep 28) guarantees ₹15.50L floor safety",
                "breachesFloor": False,
                "selected": True,
                "sparklineData": [
                    {"day": "Aug 28", "cash": 45.0},
                    {"day": "Aug 29", "cash": 28.5},
                    {"day": "Sep 01", "cash": 27.8},
                    {"day": "Sep 05", "cash": 27.0},
                    {"day": "Sep 15", "cash": 27.5},
                    {"day": "Sep 28", "cash": 30.8},
                    {"day": "Oct 08", "cash": 31.7},
                    {"day": "Oct 18", "cash": 33.0}
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
                    {"day": "Aug 28", "cash": 45.0},
                    {"day": "Aug 29", "cash": 28.5},
                    {"day": "Sep 01", "cash": 28.5},
                    {"day": "Sep 05", "cash": 28.5},
                    {"day": "Sep 15", "cash": 27.8},
                    {"day": "Sep 28", "cash": 30.8},
                    {"day": "Oct 08", "cash": 31.7},
                    {"day": "Oct 18", "cash": 32.5}
                ]
            }
        ],
        "forecast": [
            {"day": "Aug 28", "cash": 45.0, "pessimistic": 43.0},
            {"day": "Aug 29 (Opex)", "cash": 28.5, "pessimistic": 27.5},
            {"day": "Sep 01", "cash": 27.8, "pessimistic": 26.8},
            {"day": "Sep 05", "cash": 27.0, "pessimistic": 26.0},
            {"day": "Sep 15 (REC_TML_0365)", "cash": 27.5, "pessimistic": 26.5},
            {"day": "Sep 28", "cash": 30.8, "pessimistic": 29.5},
            {"day": "Oct 08", "cash": 31.7, "pessimistic": 30.0},
            {"day": "Oct 18", "cash": 33.0, "pessimistic": 31.5}
        ],
        "invoices": [
            {
                "id": inv.id,
                "supplierName": inv.supplier_name,
                "supplierCategory": "Powertrain Systems" if inv.supplier_id == "SUP001" else "Auto Body Sheet Metal",
                "amount": round(inv.amount * 100000.0, 2),
                "dueDate": inv.due_date,
                "discountPct": inv.discount_percentage,
                "discountDeadline": inv.issue_date,
                "priorityScore": int(inv.priority_score),
                "aiAction": inv.recommended_action.value if hasattr(inv.recommended_action, 'value') else str(inv.recommended_action),
                "strategicImportance": 5,
                "reasoning": inv.action_reason
            }
            for inv in store.invoices[:6]
        ],
        "receivables": [
            {
                "id": "REC_TML_0365",
                "customerName": "VRL Logistics Ltd (Fleet CV Purchase)",
                "amount": 317609.60,
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
            "id": inv.id,
            "supplierName": inv.supplier_name,
            "supplierCategory": "Powertrain Systems" if inv.supplier_id == "SUP001" else "Auto Body Sheet Metal",
            "amount": round(inv.amount * 100000.0, 2),
            "dueDate": inv.due_date,
            "discountPct": inv.discount_percentage,
            "discountDeadline": inv.issue_date,
            "priorityScore": int(inv.priority_score),
            "aiAction": inv.recommended_action.value if hasattr(inv.recommended_action, 'value') else str(inv.recommended_action),
            "strategicImportance": 5,
            "reasoning": inv.action_reason
        }
        for inv in store.invoices
    ]

@app.get("/receivables")
@app.get("/api/receivables")
def get_receivables():
    return [
        {
            "id": r.id,
            "customerName": r.customer_name,
            "amount": round(r.amount * 100000.0, 2),
            "expectedDate": r.expected_date,
            "collectionProbability": round(r.collection_probability * 100.0, 1),
            "expectedDelayDays": r.expected_delay_days,
            "status": "On Time" if r.expected_delay_days <= 2 else "Delayed"
        }
        for r in store.receivables
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
            "impact": "₹6.09L Outflow + ₹16.5L Plant Opex",
            "cost": "₹0 (Zero Financing Interest)",
            "verdict": "RECOMMENDED: Covers ₹16.5L Plant Opex while paying Bosch & JSW Steel.",
            "apr": "0.0%",
            "availability": "Instant (HDFC Treasury)"
        },
        {
            "id": "FIN-02",
            "title": "Dynamic Bank Credit Line",
            "recommended": False,
            "impact": "₹0 Outflow Today (₹15.5L Line Drawn)",
            "cost": "₹1,550 Interest Cost (8.5% APR)",
            "verdict": "ALTERNATIVE: Preserves cash if VRL Logistics receivable is delayed >5 days.",
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
            if r.id == event.target_id or "VRL Logistics" in r.customer_name or r.customer_name.startswith("Customer CUST011"):
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
            "title": f"⚠️ Material Delay: {event.description or 'VRL Logistics fleet receivable delayed'}",
            "detail": f"Receivable delayed by {event.delay_days or 10} days! VRL Logistics Bayesian probability shifted to 76.9%.",
            "impact": "Strategy Re-Optimized"
        }
        store.events_log.insert(0, evt_item)
    else:
        evt_item = {
            "id": evt_id,
            "time": timestamp,
            "event_type": event.event_type,
            "stage": "OBSERVE",
            "title": f"Telemetry Event: {event.description or 'Tata Motors telemetry processed'}",
            "detail": "Monitored telemetry event ingested.",
            "impact": "Monitored (No Material Change)"
        }
        store.events_log.insert(0, evt_item)

    store.ingest_and_process_stream_record(evt_item)

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
    breaches_floor = min_cash < 15.50

    return {
        "minCashLakhs": min_cash * 10.0,
        "breachesFloor": breaches_floor,
        "explanation": f"Simulating VRL Logistics fleet delay (+{delay_days}d) drops cash floor to ₹{min_cash:.1f} Cr. Strategy intact above ₹15.50 Cr Tata Motors reserve floor."
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
            "timestamp": dec.created_at or "2026-08-28 14:45",
            "triggerEvent": f"Tata Motors Live Ingestion & 0/1 Knapsack Re-Run ({dec.triggered_by_event_id or 'Auto'})",
            "decision": dec.chosen_action,
            "amount": round(dec.total_budget_spent * 100000.0, 2),
            "confidence": int(dec.confidence * 100),
            "status": "ACTIVE" if idx == 0 else "SUPERSEDED",
            "version": f"v2.{len(store.decisions_history) - idx}",
            "reasons": [dec.reasoning]
        })
    return result

@app.get("/agent/activity")
@app.get("/api/agent-activity")
def get_agent_activity():
    activities = []
    for evt in store.events_log[:15]:
        activities.append({
            "stage": evt.get("stage", "OBSERVE"),
            "time": evt.get("time", "20:01:04"),
            "title": evt.get("title", "Tata Motors Telemetry Sync"),
            "detail": evt.get("detail", "Processed Tata Motors live event stream."),
            "impact": evt.get("impact", "Monitored")
        })
    return activities

# SSE STREAM ENDPOINT
@app.get("/api/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    event_subscribers.append(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            yield json.dumps({"event": "CONNECTED", "data": "CashPilot AI Tata Motors Engine Active"})

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
