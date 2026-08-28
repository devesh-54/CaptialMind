import asyncio
import json
import time
from typing import AsyncGenerator, List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from data_loader import DataLoader
from engine import DecisionEngine, MaterialityChangeDetector

app = FastAPI(
    title="CashPilot AI Backend Engine",
    description="Autonomous Working-Capital Management API & Event Streaming Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_loader = DataLoader()
engine = DecisionEngine(reserve_floor=1500000.0)

current_cash = data_loader.load_cash()
receivables = data_loader.load_receivables()
invoices = data_loader.load_invoices()
suppliers = data_loader.load_suppliers()
obligations = data_loader.load_obligations()

activity_feed = [
    {
        "id": "ACT-105",
        "timestamp": "Just now",
        "stage": "DECIDE",
        "title": "Optimized Capital Deployment for Employee Salary Day & Supplier Invoices",
        "detail": f"Evaluated candidate options. Reserved ₹4.10Cr for Employee Salary Payroll due tomorrow and selected Pay Now (Score: 96/100) for {invoices[0]['supplierName'] if invoices else 'Valeo India'}.",
        "impact": "+₹6.67L Net Yield"
    },
    {
        "id": "ACT-104",
        "timestamp": "2m ago",
        "stage": "FORECAST",
        "title": "Customer A (Mahindra Logistics) Inflow & Salary Obligation Forecasted",
        "detail": f"Customer A (₹2.45Cr, {receivables[0]['collectionProbability']}% Bayesian confidence) expected on Jan 15th. Employee Payroll (₹4.10Cr) scheduled for tomorrow.",
        "impact": "Protected ₹15.0L Floor"
    },
    {
        "id": "ACT-103",
        "timestamp": "11m ago",
        "stage": "OBSERVE",
        "title": "Bank API Cash Sync",
        "detail": f"HDFC Treasury Account balance confirmed: ₹{current_cash:,.2f}. Operating reserve constraint verified.",
    }
]

decision_history = [
    {
        "id": "DEC-8801",
        "timestamp": "2026-08-28 14:45",
        "triggerEvent": "Daily Working Capital Run & Salary Day Alignment",
        "decision": f"Reserve ₹4.10Cr Salary Payroll + Early Settlement for {invoices[0]['supplierName'] if invoices else 'Valeo India'} (Pay Now)",
        "amount": invoices[0]['amount'] if invoices else 33381685.97,
        "confidence": 96,
        "status": "ACTIVE",
        "version": "v1.2",
        "validUntil": None,
        "reasons": [
            "Employee Monthly Payroll (₹4.10Cr) prioritized as CRITICAL due tomorrow.",
            "Pay Now candidate scored 96/100 (runner-up Bank Finance scored 74/100).",
            "2.0% discount captures ₹66.76L net value on Valeo India invoice.",
            "Customer A (Mahindra Logistics) inflow of ₹2.45Cr on Jan 15th guarantees safety buffer above ₹15.0L floor."
        ]
    }
]

event_subscribers = []

class EventTriggerRequest(BaseModel):
    event_type: str
    description: str
    receivable_delay_days: int = 0
    extra_outflow_lakhs: float = 0.0
    prob_delta: float = 0.0
    risk_shift: bool = False
    customer_id: str = "CUST-001"

class WhatIfRequest(BaseModel):
    receivable_delay_days: int
    cash_drop_lakhs: float

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "CashPilot AI Autonomous Decision Engine",
        "version": "2.0.0"
    }

@app.get("/api/command-center")
def get_command_center():
    forecast = engine.forecast_30d_cash(current_cash, receivables=receivables)
    top_inv = invoices[0] if invoices else None
    candidates = engine.generate_candidates(current_cash, top_invoice=top_inv, receivables=receivables)
    hero_rec = engine.generate_hero_recommendation(invoices, current_cash, receivables=receivables)

    return {
        "kpis": {
            "availableCash": current_cash,
            "protectedCash": 1500000.0,
            "deployableCapital": max(0.0, current_cash - 1500000.0),
            "risk30d": "LOW" if receivables[0]["collectionProbability"] >= 75 else "HIGH",
            "wcEfficiency": 88,
            "financingExposure": 1250000.0
        },
        "heroRecommendation": hero_rec,
        "candidates": candidates,
        "forecast": forecast,
        "invoices": invoices,
        "obligations": obligations,
        "receivables": receivables,
        "suppliers": suppliers,
        "activityFeed": activity_feed
    }

@app.get("/api/invoices")
def get_invoices():
    top_inv = invoices[0] if invoices else None
    candidates = engine.generate_candidates(current_cash, top_invoice=top_inv, receivables=receivables)
    inv_list = []
    for inv in invoices:
        inv_copy = dict(inv)
        inv_copy["candidates"] = candidates
        inv_list.append(inv_copy)
    return inv_list

@app.get("/api/receivables")
def get_receivables():
    return receivables

@app.get("/api/suppliers")
def get_suppliers():
    return suppliers

@app.get("/api/financing")
def get_financing_options():
    return [
        {
            "id": "FIN-01",
            "title": "Internal Cash Deployment",
            "recommended": True,
            "impact": "₹3.34Cr Outflow + ₹4.10Cr Salary",
            "cost": "₹0 (Zero Financing Interest)",
            "verdict": "RECOMMENDED: Captures ₹66.76L discount while covering ₹4.10Cr Salary Payroll due tomorrow.",
            "apr": "0.0%",
            "availability": "Instant (HDFC Treasury)"
        },
        {
            "id": "FIN-02",
            "title": "Dynamic Bank Credit Line",
            "recommended": False,
            "impact": "₹0 Outflow Today (₹12.5L Line Drawn)",
            "cost": "₹18,500 Interest Cost (8.5% APR)",
            "verdict": "ALTERNATIVE: Preserves cash if Customer A receivable is delayed >5 days.",
            "apr": "8.5% p.a.",
            "availability": "Pre-Approved (ICICI Bank)"
        },
        {
            "id": "FIN-03",
            "title": "Supplier Reverse Factoring",
            "recommended": False,
            "impact": "₹3.34Cr Paid by Factoring Partner",
            "cost": "₹78,000 Processing & Yield Fee",
            "verdict": "SUB-OPTIMAL: Higher fee reduces net discount yield from 2.0% to 1.4%.",
            "apr": "11.2% p.a.",
            "availability": "Active (KredX Platform)"
        }
    ]

@app.get("/api/agent-activity")
def get_agent_activity():
    return activity_feed

@app.get("/api/decision-history")
def get_decision_history():
    return decision_history

# DUAL-FREQUENCY INGESTION & MATERIALITY CHANGE DETECTOR PIPELINE
@app.post("/events")
@app.post("/api/events")
@app.post("/api/simulate-event")
async def receive_event(req: EventTriggerRequest):
    global current_cash, activity_feed, decision_history, receivables

    # Step 1: Evaluate Materiality Thresholds
    is_material, reason = MaterialityChangeDetector.is_material_change(
        event_type=req.event_type,
        delay_days=req.receivable_delay_days,
        outflow_lakhs=req.extra_outflow_lakhs,
        prob_delta=req.prob_delta,
        risk_shift=req.risk_shift
    )

    timestamp_str = time.strftime("%H:%M:%S")

    # IF NON-MATERIAL TELEMETRY (e.g. minor cash ping <2% or delay <3d)
    if not is_material:
        monitored_event = {
            "id": f"ACT-{int(time.time()) % 10000}",
            "timestamp": "Just now",
            "stage": "OBSERVE",
            "title": f"Telemetry Telemetry Ingested: {req.description}",
            "detail": f"{reason} Existing capital allocation strategy retained.",
            "impact": "Monitored (No Material Change)"
        }
        activity_feed.insert(0, monitored_event)

        # Broadcast telemetry ping over SSE
        payload = json.dumps({
            "event": "TELEMETRY_PING",
            "data": {
                "monitoredEvent": monitored_event,
                "materialChange": False,
                "timestamp": timestamp_str
            }
        })
        for queue in event_subscribers:
            await queue.put(payload)

        return {
            "status": "monitored, no material change",
            "material_change": False,
            "reason": reason,
            "active_decision_id": decision_history[0]["id"] if decision_history else None
        }

    # IF MATERIAL CHANGE DETECTED: RUN RE-OPTIMIZER
    # 1. Update Bayesian collection probabilities if receivable delay reported
    if req.receivable_delay_days > 0 or req.event_type == "RECEIVABLE_DELAYED":
        if receivables and len(receivables) > 0:
            receivables[0] = engine.update_bayesian_probability(receivables[0], on_time=False)

    if req.extra_outflow_lakhs > 0:
        current_cash -= (req.extra_outflow_lakhs * 100000.0)

    # 2. Recompute 30-day cash timeline
    new_forecast = engine.forecast_30d_cash(
        current_cash,
        receivables=receivables,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.extra_outflow_lakhs * 100000.0
    )

    # 3. Mark previous active decision in history as SUPERSEDED
    if decision_history and len(decision_history) > 0:
        for dec in decision_history:
            if dec.get("status") == "ACTIVE":
                dec["status"] = "SUPERSEDED"
                dec["validUntil"] = time.strftime("%Y-%m-%d %H:%M")

    # 4. Generate new ACTIVE decision via Knapsack & Dynamic Weighting
    new_hero = engine.generate_hero_recommendation(invoices, current_cash, receivables=receivables)
    new_candidates = engine.generate_candidates(current_cash, top_invoice=invoices[0] if invoices else None, receivables=receivables)
    
    dec_id = f"DEC-{int(time.time()) % 10000}"
    new_decision = {
        "id": dec_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        "triggerEvent": req.description,
        "decision": new_hero["title"],
        "amount": invoices[0]['amount'] if invoices else 33381685.97,
        "confidence": new_hero["confidence"],
        "status": "ACTIVE",
        "version": f"v2.{len(decision_history)+1}",
        "validUntil": None,
        "reasons": [
            f"Material Change Detected: {reason}",
            f"Bayesian Customer A Probability shifted to {receivables[0]['collectionProbability']}%.",
            f"Evaluated candidates. 0/1 Knapsack allocation re-optimized."
        ]
    }
    decision_history.insert(0, new_decision)

    # 5. Log material event to Activity Stream
    material_event = {
        "id": f"ACT-{int(time.time()) % 10000}",
        "timestamp": "Just now",
        "stage": req.event_type,
        "title": f"⚠️ Material Change: {req.description}",
        "detail": f"{reason} Superseded previous decision. Generated {dec_id} (ACTIVE).",
        "impact": "Strategy Re-Optimized"
    }
    activity_feed.insert(0, material_event)

    # 6. Broadcast SSE live update
    payload = json.dumps({
        "event": "REALTIME_UPDATE",
        "data": {
            "newEvent": material_event,
            "newDecision": new_decision,
            "decisionHistory": decision_history,
            "receivables": receivables,
            "heroRecommendation": new_hero,
            "candidates": new_candidates,
            "forecast": new_forecast,
            "materialChange": True,
            "timestamp": timestamp_str
        }
    })
    for queue in event_subscribers:
        await queue.put(payload)

    return {
        "status": "re-optimized",
        "material_change": True,
        "reason": reason,
        "decision": new_decision,
        "bayesianProbability": receivables[0]['collectionProbability']
    }

@app.post("/api/what-if")
def run_what_if_simulation(req: WhatIfRequest):
    simulated_forecast = engine.forecast_30d_cash(
        current_cash,
        receivables=receivables,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.cash_drop_lakhs * 100000.0
    )
    min_cash = min([item["cash"] for item in simulated_forecast])
    breaches_floor = min_cash < 15.0

    if breaches_floor:
        explanation = (
            f"Action Shifted: Because simulated Customer A delay drops cash to ₹{min_cash:.1f}L (breaching reserve floor after Salary Day), "
            f"CashPilot automatically shifts Valeo India payment to Bank Dynamic Credit Line to protect Employee Payroll."
        )
    else:
        explanation = (
            f"Strategy Intact: Current stress parameters (Customer A +{req.receivable_delay_days}d delay, ₹{req.cash_drop_lakhs}L outflow) "
            f"keep minimum liquidity at ₹{min_cash:.1f}L after Salary Payroll tomorrow, safely above floor."
        )

    return {
        "minCashLakhs": min_cash,
        "breachesFloor": breaches_floor,
        "simulatedForecast": simulated_forecast,
        "explanation": explanation
    }

@app.get("/api/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    event_subscribers.append(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            yield json.dumps({"event": "CONNECTED", "data": "CashPilot AI SSE Engine Active"})

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
