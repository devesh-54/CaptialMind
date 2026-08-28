import asyncio
import json
import time
from typing import AsyncGenerator, List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from data_loader import DataLoader
from engine import DecisionEngine

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

activity_feed = [
    {
        "id": "ACT-105",
        "timestamp": "14s ago",
        "stage": "DECIDE",
        "title": "Optimized Day 1 Capital Deployment",
        "detail": "Evaluated 5 candidates. Selected Pay Now (Score: 96/100) over Bank Finance (74/100).",
        "impact": "+₹33.4k Net Yield"
    },
    {
        "id": "ACT-104",
        "timestamp": "2m ago",
        "stage": "FORECAST",
        "title": "Receivable Risk Updated",
        "detail": "Probability shift on Bajaj Auto (82% → 64%). Simulated floor breach under Delay scenario.",
        "impact": "Protected ₹15.0L Floor"
    },
    {
        "id": "ACT-103",
        "timestamp": "11m ago",
        "stage": "OBSERVE",
        "title": "Bank API Cash Sync",
        "detail": "HDFC Treasury Account balance confirmed: ₹48,20,000. Reserve floor verified.",
    }
]

decision_history = [
    {
        "id": "DEC-8801",
        "timestamp": "2026-08-28 14:45",
        "triggerEvent": "Daily Working Capital Run",
        "decision": "Early Settlement - Tata Steel (Pay Now)",
        "amount": 920000.0,
        "confidence": 96,
        "status": "Pending Approval",
        "version": "v1.2",
        "reasons": [
            "Pay Now candidate scored 96/100 (runner-up Bank Finance scored 74/100).",
            "2.5% discount captures ₹23,000 net value (32.4% annualized return).",
            "Post-payment cash remains at ₹33.2L, well above ₹15.0L safety reserve floor.",
            "Tata Steel priority rating (5/5) critical for Q3 delivery guarantees."
        ]
    },
    {
        "id": "DEC-8794",
        "timestamp": "2026-08-27 10:15",
        "triggerEvent": "Flipkart Payment Delay (+4d)",
        "decision": "Switch Zenith Packaging to Credit Line",
        "amount": 1250000.0,
        "confidence": 88,
        "status": "Executed",
        "version": "v2.0",
        "supersededBy": "DEC-8801",
        "reasons": [
            "Flipkart expected payment shifted from Aug 29 to Sept 2.",
            "Prevents cash floor dip below ₹15L threshold on Sept 1st."
        ]
    }
]

event_subscribers = []

class EventTriggerRequest(BaseModel):
    event_type: str
    description: str
    receivable_delay_days: int = 0
    extra_outflow_lakhs: float = 0.0

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
    forecast = engine.forecast_30d_cash(current_cash)
    candidates = engine.generate_candidates(current_cash)
    return {
        "kpis": {
            "availableCash": current_cash,
            "protectedCash": 1500000.0,
            "deployableCapital": current_cash - 1500000.0,
            "risk30d": "LOW",
            "wcEfficiency": 88,
            "financingExposure": 1250000.0
        },
        "heroRecommendation": {
            "title": "Allocate ₹18.4L today to capture ₹33,440 early discounts",
            "confidence": 94,
            "breakdown": [
                {"label": "Tata Steel (Pay Now)", "amount": 920000.0},
                {"label": "Apex Logistics (Pay Now)", "amount": 580000.0},
                {"label": "Retain Safety Buffer", "amount": 340000.0}
            ],
            "reasoning": "Executing these payments today captures a 2.5% discount on Tata Steel (32.4% annualized return) and protects Q3 freight dispatch with Apex Logistics while preserving ₹33.2L deployable cash."
        },
        "candidates": candidates,
        "forecast": forecast,
        "invoices": invoices,
        "receivables": receivables,
        "suppliers": suppliers,
        "activityFeed": activity_feed
    }

@app.get("/api/invoices")
def get_invoices():
    candidates = engine.generate_candidates(current_cash)
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
            "impact": "₹18.4L Immediate Outflow",
            "cost": "₹0 (Zero Financing Interest)",
            "verdict": "RECOMMENDED: Captures ₹33,440 discount while preserving ₹15L safety reserve floor.",
            "apr": "0.0%",
            "availability": "Instant (HDFC Treasury)"
        },
        {
            "id": "FIN-02",
            "title": "Dynamic Bank Credit Line",
            "recommended": False,
            "impact": "₹0 Outflow Today (₹12.5L Line Drawn)",
            "cost": "₹4,100 Interest Cost (8.5% APR)",
            "verdict": "ALTERNATIVE: Preserves cash if Flipkart receivable is delayed >5 days.",
            "apr": "8.5% p.a.",
            "availability": "Pre-Approved (ICICI Bank)"
        },
        {
            "id": "FIN-03",
            "title": "Supplier Reverse Factoring",
            "recommended": False,
            "impact": "₹9.2L Paid by Factoring Partner",
            "cost": "₹7,800 Processing & Yield Fee",
            "verdict": "SUB-OPTIMAL: Higher fee reduces net discount yield from 2.5% to 1.6%.",
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

@app.post("/api/simulate-event")
async def trigger_simulated_event(req: EventTriggerRequest):
    global current_cash, activity_feed

    new_event = {
        "id": f"ACT-{int(time.time()) % 10000}",
        "timestamp": "Just now",
        "stage": req.event_type,
        "title": req.description,
        "detail": f"Triggered real-time scenario: Delay +{req.receivable_delay_days}d, Outflow ₹{req.extra_outflow_lakhs}L.",
        "impact": "Re-optimized Plan"
    }
    activity_feed.insert(0, new_event)

    payload = json.dumps({
        "event": "REALTIME_UPDATE",
        "data": {
            "newEvent": new_event,
            "activityFeed": activity_feed,
            "timestamp": time.strftime("%H:%M:%S")
        }
    })
    for queue in event_subscribers:
        await queue.put(payload)

    return {"status": "success", "event": new_event}

@app.post("/api/what-if")
def run_what_if_simulation(req: WhatIfRequest):
    simulated_forecast = engine.forecast_30d_cash(
        current_cash,
        receivable_delay_days=req.receivable_delay_days,
        extra_outflow=req.cash_drop_lakhs * 100000.0
    )
    min_cash = min([item["cash"] for item in simulated_forecast])
    breaches_floor = min_cash < 15.0

    if breaches_floor:
        explanation = (
            f"Action Shifted: Because simulated cash drops to ₹{min_cash:.1f}L (breaching the ₹15.0L reserve floor), "
            f"CashPilot automatically shifts Zenith Packaging from Pay Now to Bank Dynamic Credit Line to preserve ₹12.5L internal cash buffer."
        )
    else:
        explanation = (
            f"Strategy Intact: Current stress parameters (+{req.receivable_delay_days}d delay, ₹{req.cash_drop_lakhs}L outflow) "
            f"keep minimum liquidity at ₹{min_cash:.1f}L, safely above the policy floor."
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
