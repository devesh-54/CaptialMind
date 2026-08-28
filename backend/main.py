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
engine = DecisionEngine(reserve_floor=970000.0)

current_cash = data_loader.load_cash()
receivables = data_loader.load_receivables()
invoices = data_loader.load_invoices()
suppliers = data_loader.load_suppliers()
obligations = data_loader.load_obligations()
future_sequence = data_loader.load_future_daily_sequence()

activity_feed = [
    {
        "id": "ACT-105",
        "timestamp": "Just now",
        "stage": "DECIDE",
        "title": "Optimized Capital Deployment for Opex & Supplier Invoices",
        "detail": f"Evaluated candidate options. Reserved ₹16.5L for Opex due today and selected Pay Now (Score: 96/100) for {invoices[0]['supplierName'] if invoices else 'Bosch Ltd'}.",
        "impact": "+₹1.41L Net Yield"
    },
    {
        "id": "ACT-104",
        "timestamp": "2m ago",
        "stage": "FORECAST",
        "title": "Customer CUST011 Inflow & Opex Obligation Forecasted",
        "detail": f"Customer CUST011 (₹31.76k, {receivables[0]['collectionProbability']}% Bayesian confidence) expected on Sep 28. Opex (₹16.5L) scheduled for today.",
        "impact": "Protected ₹9.70L Floor"
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
        "triggerEvent": "Daily Working Capital Run & Future Dataset Sync",
        "decision": f"Reserve ₹16.5L Opex + Early Settlement for {invoices[0]['supplierName'] if invoices else 'Bosch Ltd'} (Pay Now)",
        "amount": invoices[0]['amount'] if invoices else 68902.88,
        "confidence": 96,
        "status": "ACTIVE",
        "version": "v1.2",
        "validUntil": None,
        "reasons": [
            "Operating Expense & Payroll (₹16.5L) prioritized as CRITICAL due today.",
            "Pay Now candidate scored 96/100 (runner-up Bank Finance scored 74/100).",
            "Customer CUST011 inflow of ₹31.76k on Sep 28 guarantees safety buffer above ₹9.70L floor."
        ]
    }
]

event_subscribers = []
current_sequence_index = 0

class EventTriggerRequest(BaseModel):
    event_type: str
    description: str
    receivable_delay_days: int = 0
    extra_outflow_lakhs: float = 0.0
    prob_delta: float = 0.0
    risk_shift: bool = False
    customer_id: str = "CUST011"

class WhatIfRequest(BaseModel):
    receivable_delay_days: int
    cash_drop_lakhs: float

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "CashPilot AI Autonomous Decision Engine",
        "version": "2.0.0",
        "data_source": "futureStreaming_data_cashpilot & historical_data_cashpilot"
    }

@app.get("/api/decision-intelligence")
def get_decision_intelligence():
    """Returns Phase 13 Output Contract for Working-Capital Decision Intelligence."""
    contract = engine.evaluate_full_pipeline(
        current_cash=current_cash,
        receivables=receivables,
        invoices=invoices,
        obligations=obligations
    )
    return contract

@app.get("/api/command-center")
def get_command_center():
    forecast = engine.forecast_30d_cash(current_cash, receivables=receivables)
    top_inv = invoices[0] if invoices else None
    candidates = engine.generate_candidates(current_cash, top_invoice=top_inv, receivables=receivables)
    hero_rec = engine.generate_hero_recommendation(invoices, current_cash, receivables=receivables)
    
    # Phase 13 full output contract
    decision_contract = engine.evaluate_full_pipeline(
        current_cash=current_cash,
        receivables=receivables,
        invoices=invoices,
        obligations=obligations
    )

    rec_prob = receivables[0]["collectionProbability"] if receivables else 87.0
    risk_level = decision_contract["financial_health"]["risk_level"]

    return {
        "kpis": {
            "availableCash": current_cash,
            "protectedCash": decision_contract["financial_health"]["recommended_reserve"],
            "deployableCapital": max(0.0, current_cash - decision_contract["financial_health"]["recommended_reserve"]),
            "risk30d": risk_level,
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
        "activityFeed": activity_feed,
        "decisionContract": decision_contract
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

    is_material, reason = MaterialityChangeDetector.is_material_change(
        event_type=req.event_type,
        delay_days=req.receivable_delay_days,
        outflow_lakhs=req.extra_outflow_lakhs,
        prob_delta=req.prob_delta,
        risk_shift=req.risk_shift
    )

    timestamp_str = time.strftime("%H:%M:%S")

    if not is_material:
        monitored_event = {
            "id": f"ACT-{int(time.time()) % 10000}",
            "timestamp": "Just now",
            "stage": "OBSERVE",
            "title": f"Telemetry Ingested: {req.description}",
            "detail": f"{reason} Existing capital allocation strategy retained.",
            "impact": "Monitored (No Material Change)"
        }
        activity_feed.insert(0, monitored_event)

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
    if req.receivable_delay_days > 0 or req.event_type == "RECEIVABLE_DELAYED":
        if receivables and len(receivables) > 0:
            receivables[0] = engine.update_bayesian_probability(receivables[0], on_time=False)

    if req.extra_outflow_lakhs > 0:
        current_cash -= (req.extra_outflow_lakhs * 100000.0)

    decision_contract = engine.evaluate_full_pipeline(
        current_cash=current_cash,
        receivables=receivables,
        invoices=invoices,
        obligations=obligations,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.extra_outflow_lakhs * 100000.0
    )

    new_forecast = decision_contract["forecast_quality"].get("projected_points", engine.forecast_30d_cash(
        current_cash,
        receivables=receivables,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.extra_outflow_lakhs * 100000.0
    ))

    if decision_history and len(decision_history) > 0:
        for dec in decision_history:
            if dec.get("status") == "ACTIVE":
                dec["status"] = "SUPERSEDED"
                dec["validUntil"] = time.strftime("%Y-%m-%d %H:%M")

    new_hero = engine.generate_hero_recommendation(invoices, current_cash, receivables=receivables)
    new_candidates = engine.generate_candidates(current_cash, top_invoice=invoices[0] if invoices else None, receivables=receivables)
    
    dec_id = f"DEC-{int(time.time()) % 10000}"
    new_decision = {
        "id": dec_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        "triggerEvent": req.description,
        "decision": new_hero["title"],
        "amount": invoices[0]['amount'] if invoices else 68902.88,
        "confidence": new_hero["confidence"],
        "status": "ACTIVE",
        "version": f"v2.{len(decision_history)+1}",
        "validUntil": None,
        "reasons": [
            f"Material Change Detected: {reason}",
            f"Bayesian Customer CUST011 Probability shifted to {receivables[0]['collectionProbability']}%.",
            f"Evaluated candidates. Dynamic Reserve: ₹{decision_contract['financial_health']['recommended_reserve']:,.2f}."
        ]
    }
    decision_history.insert(0, new_decision)

    material_event = {
        "id": f"ACT-{int(time.time()) % 10000}",
        "timestamp": "Just now",
        "stage": req.event_type,
        "title": f"⚠️ Material Change: {req.description}",
        "detail": f"{reason} Superseded previous decision. Generated {dec_id} (ACTIVE).",
        "impact": "Strategy Re-Optimized"
    }
    activity_feed.insert(0, material_event)

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
            "availableCash": current_cash,
            "materialChange": True,
            "timestamp": timestamp_str,
            "decisionContract": decision_contract
        }
    })
    for queue in event_subscribers:
        await queue.put(payload)

    return {
        "status": "re-optimized",
        "material_change": True,
        "reason": reason,
        "decision": new_decision,
        "bayesianProbability": receivables[0]['collectionProbability'],
        "decisionContract": decision_contract
    }

@app.post("/api/what-if")
def run_what_if_simulation(req: WhatIfRequest):
    decision_contract = engine.evaluate_full_pipeline(
        current_cash=current_cash,
        receivables=receivables,
        invoices=invoices,
        obligations=obligations,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.cash_drop_lakhs * 100000.0
    )

    simulated_forecast = engine.forecast_30d_cash(
        current_cash,
        receivables=receivables,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.cash_drop_lakhs * 100000.0
    )
    min_cash = min([item["cash"] for item in simulated_forecast])
    breaches_floor = min_cash < 9.7

    if breaches_floor:
        explanation = (
            f"Action Shifted: Because simulated CUST011 delay drops cash to ₹{min_cash:.1f}L (breaching ₹9.70L reserve floor), "
            f"CashPilot automatically shifts invoice payment to Bank Dynamic Credit Line to protect Opex & Payroll."
        )
    else:
        explanation = (
            f"Strategy Intact: Current stress parameters (CUST011 +{req.receivable_delay_days}d delay, ₹{req.cash_drop_lakhs}L outflow) "
            f"keep minimum liquidity at ₹{min_cash:.1f}L after Opex today, safely above floor."
        )

    return {
        "minCashLakhs": min_cash,
        "breachesFloor": breaches_floor,
        "simulatedForecast": simulated_forecast,
        "explanation": explanation,
        "decisionContract": decision_contract
    }

# BACKGROUND SSE LIVE AUTOMATED STREAM GENERATOR
async def auto_stream_generator():
    global current_cash, current_sequence_index
    while True:
        await asyncio.sleep(5.0)
        if future_sequence and len(future_sequence) > 0:
            current_sequence_index = (current_sequence_index + 1) % len(future_sequence)
            row = future_sequence[current_sequence_index]

            date_str = row.get("date", "2026-08-28")
            new_bal = row.get("balance", 2554079.97)
            inflow = row.get("inflow", 0.0)
            outflow = row.get("outflow", 0.0)

            # Update cash balance from future sequence row
            current_cash = new_bal

            timestamp_str = time.strftime("%H:%M:%S")

            # Evaluate materiality
            is_material = outflow > 150000.0 or inflow > 200000.0

            if is_material:
                event_type = "FORECAST"
                desc = f"Future Sequence Date {date_str}: Daily Outflow ₹{(outflow/100000.0):.2f}L / Inflow ₹{(inflow/100000.0):.2f}L Ingested"
                new_event = {
                    "id": f"ACT-FUT-{current_sequence_index}",
                    "timestamp": "Just now",
                    "stage": event_type,
                    "title": f"⚡ Future Streaming Sequence Event ({date_str})",
                    "detail": desc,
                    "impact": f"Cash Balance: ₹{(new_bal/100000.0):.2f}L"
                }
                activity_feed.insert(0, new_event)

                new_forecast = engine.forecast_30d_cash(current_cash, receivables=receivables)
                new_hero = engine.generate_hero_recommendation(invoices, current_cash, receivables=receivables)
                new_candidates = engine.generate_candidates(current_cash, top_invoice=invoices[0] if invoices else None, receivables=receivables)

                payload = json.dumps({
                    "event": "REALTIME_UPDATE",
                    "data": {
                        "newEvent": new_event,
                        "availableCash": current_cash,
                        "heroRecommendation": new_hero,
                        "candidates": new_candidates,
                        "forecast": new_forecast,
                        "receivables": receivables,
                        "timestamp": timestamp_str,
                        "sequenceDate": date_str
                    }
                })
            else:
                payload = json.dumps({
                    "event": "TELEMETRY_PING",
                    "data": {
                        "sequenceDate": date_str,
                        "availableCash": current_cash,
                        "status": f"Monitored Date {date_str} - Balance ₹{(new_bal/100000.0):.2f}L",
                        "timestamp": timestamp_str
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

@app.get("/api/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    event_subscribers.append(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            yield json.dumps({"event": "CONNECTED", "data": "CashPilot AI Continuous Automated Streaming Engine Active"})

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
                            "status": "ACTIVE_AUTOMATED_STREAM"
                        }
                    })
                    yield heartbeat

        finally:
            if queue in event_subscribers:
                event_subscribers.remove(queue)

    return EventSourceResponse(event_generator())
