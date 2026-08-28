CashPilot AI

_An autonomous AI agent that decides where limited working capital should go — before liquidity becomes a problem._

**Event** CSI ORIGIN 2026

**Problem Statement**

ID 4 — Autonomous Working-Capital Management Under Financial and Supply-Chain Constraints

**Prepared by** Ashwin

**Document type** Solution & Architecture Report

_"Traditional systems tell finance teams what happened. CashPilot AI continuously evaluates what should happen next."_

_This report consolidates the problem interpretation, system architecture, decision-making methodology, technology stack, and demo strategy developed for the hackathon prototype._

# Table of Contents

- 1\. Executive Summary
- 2\. Problem Statement (as given)
- 3\. Product Positioning
- 4\. Core Autonomous Loop
- 5\. System Architecture
- 6\. Data Model
- 7\. Forecasting & Receivable Uncertainty
- 8\. Decision-Making Methodology
- 9\. Global Capital Allocation
- 10\. Role of the LLM
- 11\. Explainability & What-If Simulation
- 12\. Technology Stack
- 13\. Competitive Landscape
- 14\. Demo Mode & Hero Scenario
- 15\. Judge-Facing Value Proposition
- 16\. Development Plan & Scope Boundaries
- 17\. Success Criteria

# Executive Summary

CashPilot AI is an autonomous working-capital decision agent built for CSI ORIGIN 2026, Problem Statement 4. Rather than displaying cash, receivable, and payable data for a human to interpret, the system continuously forecasts a business's future liquidity, evaluates every available payment and financing option for every open invoice, balances competing financial objectives, allocates limited capital across them, and explains its reasoning in plain language.

When financial or supply-chain conditions change, it automatically re-evaluates and updates its recommendations.

The one-line pitch:

_We built an autonomous working-capital agent that continuously forecasts a company's 30-day liquidity, evaluates every available payment and financing option, dynamically adjusts its priorities based on financial context, allocates limited capital globally, and automatically re-optimizes when conditions change._

# Problem Statement (as given)

**Title:** Autonomous Working-Capital Management Under Financial and Supply-Chain Constraints

Businesses continuously manage competing demands for limited working capital — paying suppliers early for discounts versus preserving liquidity, using external financing versus internal cash, all under uncertainty about when receivables will actually arrive. Existing treasury systems mostly provide visibility (dashboards, static rules, fixed schedules) but leave the actual decision-making to finance teams.

## Core challenge (verbatim intent)

Design and build an autonomous working-capital management agent capable of continuously maintaining a forward-looking financial model of a business and determining how available capital should be allocated across competing payment and financing decisions.

## Key constraints the solution must satisfy

- - Reason about current **and** projected financial states — not just current cash balances.
    - Account for uncertain receivable timing, changing cash availability, supplier requirements, financing costs, payment deadlines, discounts, penalties, and financial obligations.
    - Evaluate multiple payment and financing alternatives before allocating capital.
    - Balance cash preservation, financing cost, supplier liquidity, discounts, obligations, and financial risk — never a single metric.
    - Continuously monitor changes and re-optimize decisions as conditions evolve.
    - Provide an explainable rationale, including assumptions and trade-offs, for every decision.
    - Be an autonomous decision system — not merely a cash-flow dashboard or a financing-cost optimizer.

# Product Positioning

CashPilot AI is deliberately **not** described as a cash-flow dashboard, invoice tracker, accounting application, payment scheduler, financing-cost calculator, or generic chatbot. It is positioned as:

_An autonomous working-capital decision engine that continuously evaluates future financial states and determines how limited capital should be allocated across payment, financing, and cash-retention decisions._

## The key differentiator, in one contrast

| **Traditional system**  | **CashPilot AI**                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "You have ₹48.2L cash." | "You have ₹26.7L safely deployable capital. Pay Alpha and Gamma now, finance Delta, wait on Beta, and retain ₹3.4L because a major receivable is uncertain." |

# Core Autonomous Loop

The system's architecture visibly implements a continuous decision loop:

| **OBSERVE** | **FORECAST** | **PRIORITIZE** | **EVALUATE PAYMENT & FINANCING OPTIONS** | **ALLOCATE CAPITAL** | **EXECUTE / RECOMMEND** | **MONITOR OUTCOMES** | **RE-OPTIMIZE** |
| ----------- | ------------ | -------------- | ---------------------------------------- | -------------------- | ----------------------- | -------------------- | --------------- |

The system re-enters this loop whenever any of the following change: cash balance, receivable timing, a large approaching obligation, supplier liquidity, financing cost, available discounts, imminent penalties, or overall financial risk.

# System Architecture

End-to-end data and decision flow:

| **Layer**                      | **Responsibility**                                                                                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Data Generator                 | Produces the initial simulated company dataset: cash, suppliers, customers, invoices, receivables, obligations, financing options, historical transactions. |
| Database (PostgreSQL)          | Stores current financial state, decision history, and forecast snapshots.                                                                                   |
| Event Generator → POST /events | Simulates real-world changes (new invoice, receivable delayed, new obligation, financing rate change) that update the database and trigger re-evaluation.   |
| Forecast Engine                | Projects a day-by-day cash timeline, incorporating receivable uncertainty; detects material change.                                                         |
| Candidate Engine               | Enumerates possible actions per invoice: pay now, pay at maturity, delay, capture discount, bank financing, supplier financing, retain cash.                |
| Deterministic Scoring          | Scores each candidate on liquidity, financial cost/benefit, supplier relationship, and risk (0–1 each).                                                     |

| Dynamic Weighting                | Recomputes the importance of each objective based on current financial context (e.g. tight cash → liquidity/risk weighted higher). |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Global Allocator                 | Ranks candidates by utility-per-rupee and greedily allocates limited cash while respecting the liquidity floor.                    |
| Decision Log                     | Persists the chosen action, all alternatives considered, weights, scores, and assumptions.                                         |
| LLM (Explanation layer)          | Converts the structured decision into a natural-language rationale and answers what-if questions — never invents numbers.          |
| Execution (POST<br><br>/execute) | Commits the chosen action to the database (simulated), closing the loop back to the forecast engine.                               |

Architecture principle: business logic lives in backend services, never in the frontend. Deterministic financial calculations are kept separate from the ML prediction component and from the LLM explanation component, so every number a judge sees can be traced to actual code, not model output.

# Data Model

Core PostgreSQL entities:

| **Entity**                 | **Key fields**                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| companies                  | minimum_cash_reserve, currency                                                                  |
| cash_accounts              | balance, available_balance                                                                      |
| suppliers                  | strategic_importance, liquidity_risk, payment_terms, financing_terms                            |
| customers                  | payment_history, on_time_probability, average_delay_days                                        |
| invoices                   | amount, due_date, discount_percentage, discount_deadline, late_penalty_percentage, status       |
| receivables                | amount, expected_date, collection_probability, expected_delay_days, status                      |
| obligations                | amount, due_date, priority                                                                      |
| financing_options          | provider, type, interest_rate, credit_limit, repayment_terms                                    |
| decisions / decision_items | decision_type, chosen action, alternatives, weights, scores, assumptions, reasoning, confidence |
| scenarios                  | parameters, result (for what-if simulation)                                                     |
| events                     | event_type and payload for live simulated changes                                               |

Data realism matters: customers are generated with distinct payment behaviours (e.g. a customer with a 10% historical delay probability versus one with 45%), and suppliers are

generated with distinct strategic-importance scores (e.g. a critical steel supplier at 0.95 versus office supplies at 0.20). This is what makes the decision engine's trade-offs meaningful rather than arbitrary.

# Forecasting & Receivable Uncertainty

The forecast engine projects a 30-day day-by-day cash position rather than reading today's balance alone:

_projected_cash\[day\] = cash_today + expected_inflows(up to day) − committed_outflows(up to day)_

Receivables are never treated as guaranteed. Each customer carries an on-time-payment probability derived from payment history (predicted via a scikit-learn classifier such as RandomForest or GradientBoosting, using features like historical delay count, average delay days, invoice amount, and payment terms). Expected cash from a receivable uses an expected-value calculation:

_Expected cash = P(on-time) × on-time cash flow + P(late) × late cash flow_

Example: a customer owing ₹6L with an 80% on-time probability contributes ₹4.8L of expected cash within the relevant forecast window (0.80 × ₹6L + 0.20 × ₹0), with a pessimistic scenario also modeled for risk scoring. When an event arrives (e.g. a receivable is delayed), the forecast recalculates and checks for **material change** — a significant drop in projected cash floor, a delayed receivable, a large new invoice, an approaching critical obligation, or a financing-cost change. Only a material change triggers a full re-run of the decision engine, keeping the system responsive without recomputing on every trivial update.

# Decision-Making Methodology

The decision engine is intentionally split into a deterministic calculation layer and a natural-language explanation layer, so every recommendation is auditable.

## Step 1 — Candidate actions per invoice

- - PAY_NOW
    - PAY_AT_MATURITY
    - DELAY_PAYMENT
    - CAPTURE_DISCOUNT
    - BANK_FINANCE
    - SUPPLIER_FINANCE
    - RETAIN_CASH

All candidates are generated and scored before any action is chosen — not just a single default path — and every candidate's score is logged, not only the winner.

## Step 2 — Four normalized scores (0–1) per candidate

| **Score** | **What it answers** | **Inputs** |
| --------- | ------------------- | ---------- |

| Liquidity impact       | How does this action affect future cash?       | Current cash, 30-day forecast, expected receivables and their uncertainty, upcoming obligations                      |
| ---------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Financial cost/benefit | What does this action cost or save?            | Early-payment discount, late-payment penalty, financing interest, avoided costs                                      |
| Supplier relationship  | What does this do to a key relationship?       | Supplier strategic-importance score, supplier liquidity risk                                                         |
| Risk exposure          | Can obligations still be met safely afterward? | Forward simulation of projected cash floor under a pessimistic receivable scenario vs. the required liquidity buffer |

## Step 3 — Context-sensitive dynamic weighting

Weights are not fixed at 25% each — that would reproduce the static-rule problem the challenge explicitly warns against. Instead, weights are recalculated every decision cycle from the current financial context:

| **Situation**                             | **Liquidity** | **Financial** | **Supplier** | **Risk** |
| ----------------------------------------- | ------------- | ------------- | ------------ | -------- |
| Cash tight, large obligations approaching | 0.35          | 0.20          | 0.10         | 0.35     |
| Cash comfortable, good discount available | 0.15          | 0.40          | 0.30         | 0.15     |

Utility for each candidate is then:

_Utility = (w1 × Liquidity) + (w2 × Financial) + (w3 × Supplier) + (w4 × Risk), where w1 + w2_

_\+ w3 + w4 = 1_

**Demonstrating multi-objective reasoning:** the system must be able to show a case where the cheapest option is deliberately not chosen — for example, delaying payment to a

high-importance supplier costs ₹0 but is rejected in favour of paying at maturity (cost ₹5,000) because it protects a critical supplier relationship and keeps risk low. This single example is strong evidence against the "just a cost-optimizer" failure mode.

# Global Capital Allocation

Invoices compete for the same limited cash, so the best action per invoice cannot be chosen independently — doing so can overcommit available capital. The allocator instead:

- - Ranks every (invoice, action) candidate by **utility per rupee committed** (benefit density).
    - Greedily allocates available cash down the ranked list.
    - Skips any allocation that would breach the required liquidity floor for near-term known obligations.
    - Stops once available capital for the cycle is fully and safely allocated.

This is a simple greedy/knapsack-style allocator — deterministic, cheap to implement, and easy to explain to judges (no black-box optimization library required for the MVP; SciPy can be layered in later for a more sophisticated allocator if time allows).

# Role of the LLM

The LLM is explicitly **not** the financial calculator. All forecasting, scoring, weighting, and allocation are pure deterministic Python, verifiable by a judge. The LLM receives only the already-computed structured decision and turns it into a readable explanation:

_Input to LLM: { decision: PAY_AT_MATURITY, alternatives: \[PAY_NOW, DELAY, BANK_FINANCING\], customer_on_time_probability: 0.80, projected_cash_floor: 320000,_

_required_cash_floor: 200000, discount_available: 60000 }_

_LLM output: "Pay the invoice at maturity rather than immediately. Although early payment would capture a ₹60,000 discount, preserving liquidity is currently more valuable because the customer has only an 80% probability of paying on time. The projected cash floor remains_

_₹3.2 lakh against the required ₹2 lakh reserve."_

The style should read like a financial operations analyst, always referencing concrete numbers

— never a vague statement like "I think you should pay this invoice."

# Explainability & What-If Simulation

Every decision persists a full record: chosen action, all alternatives considered, the weights used, all candidate scores, key assumptions (e.g. "assumed 80% on-time probability based on the last 6 invoices"), and what would flip the decision (e.g. "if the cash buffer fell below ₹X, we would delay this instead"). When conditions change, a new decision version is logged with an explicit link back to the one it supersedes and the trigger that caused the change.

What-if questions ("what if this customer pays 10 days late?") are handled the same way — never by letting the LLM guess:

_User question → extract the changed assumption → re-run the deterministic engine with that change → new forecast, scores, weights, allocation → diff against the previous result → LLM explains only the difference._

# Technology Stack

| **Layer**       | **Technology**                                                  | **Purpose**                          |
| --------------- | --------------------------------------------------------------- | ------------------------------------ |
| Frontend        | React + TypeScript + Vite, Tailwind CSS, Recharts, Lucide icons | Command-center dashboard and demo UI |
| Backend         | Python + FastAPI                                                | REST APIs and orchestration          |
| Database        | PostgreSQL                                                      | Financial state and decision history |
| Data generation | Python, Faker, NumPy, Pandas                                    | Realistic simulated company dataset  |

| Forecasting        | Python, NumPy, Pandas, datetime                     | 30-day deterministic cash-flow projection        |
| ------------------ | --------------------------------------------------- | ------------------------------------------------ |
| Payment prediction | scikit-learn (RandomForest / GradientBoosting)      | Customer on-time-payment probability             |
| Decision engine    | Pure Python                                         | Candidate scoring and dynamic weighting          |
| Optimization       | Pure Python (greedy/knapsack); SciPy optional later | Global capital allocation                        |
| LLM                | LLM API (e.g. OpenAI-compatible)                    | Explanation generation and what-if orchestration |
| Charts             | Recharts / Plotly                                   | Cash forecast visualization                      |
| Deployment         | Docker                                              | Packaging backend and database for the demo      |

Explicitly out of scope for the hackathon MVP: real banking integrations, real money movement, blockchain/crypto, complex microservices, custom LLM training, and generic chatbot features. The intelligence lives in the decision engine, not in a conversational interface.

# Competitive Landscape

Enterprise treasury and working-capital platforms already provide strong forecasting and automation. Positioning against them honestly (rather than claiming novelty that doesn't hold up) is important for judge credibility.

| **Capability**                  | **CashPilot AI** | **Kyriba**        | **Tesorio**          | **HighRadiu s**     | **Coupa**       |
| ------------------------------- | ---------------- | ----------------- | -------------------- | ------------------- | --------------- |
| Cash forecasting                | ✓                | ✓                 | ✓                    | ✓                   | ✓               |
| Receivable prediction           | ✓                | ✓                 | Strong               | ✓                   | ✓               |
| Supplier / AP data              | ✓                | ✓                 | ✓                    | Strong              | Strong          |
| Invoice-level candidate actions | Core focus       | Related           | Partial              | Related             | Related         |
| Global capital allocation       | Core focus       | ✓                 | Limited              | Related             | Related         |
| Dynamic objective weighting     | Core focus       | Analytics         | Forecast-foc used    | AI-driven           | Decision intel. |
| Autonomous re-optimization      | Core demo        | Automation avail. | Continuous forecasts | Autonomou s finance | Automatio n     |
| Explainable decision log        | Core focus       | Analytics         | Analytics            | AI explanati ons    | Analytics       |
| Hackathon-sized build           | ✓                | Enterprise        | Enterprise           | Enterprise          | Enterprise      |

The defensible framing for judges:

_Existing platforms provide strong treasury visibility, forecasting, AP/AR automation, and working-capital capabilities. Our prototype focuses specifically on an autonomous decision layer that combines these signals into a continuously re-optimized capital-allocation plan._

# Demo Mode & Hero Scenario

A dedicated demo mode uses a fictional company, **NovaTech Manufacturing Pvt. Ltd.**, preloaded with realistic data so judges never need to enter records manually.

| **Item**      | **Value**                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------ |
| Starting cash | ₹48.2L                                                                                           |
| Receivables   | ₹12.5L — ABC Industries; ₹8.2L — Orion Retail; ₹6.4L — Metro Systems                             |
| Payables      | ₹9.2L — Alpha Components; ₹5.8L — Beta Logistics; ₹3.1L — Gamma Systems; ₹7.4L — Delta Packaging |
| Financing     | Bank credit line, supplier financing, internal cash                                              |

## The hero interaction (should be the centerpiece of the live demo)

- - **Initial state:** Cash = ₹48.2L. Agent recommends: pay Alpha Components now to capture a discount.
    - **Trigger:** click "Simulate: ABC Industries pays 10 days late."
    - **Reaction:** forecast recalculates → recommendation changes to "preserve ₹6L cash and finance Beta Logistics."
    - **Explanation shown:** "The expected receivable delay increases projected liquidity risk. The agent therefore preserves internal cash and shifts part of the payment obligation to financing."

This single interaction should visibly demonstrate forecasting, uncertainty handling, multi-objective optimization, financing evaluation, explainability, and autonomous re-optimization together.

## Suggested 3–5 minute judge walkthrough

- - Open the Command Center — show cash position and the AI's recommended allocation.
    - Open Invoice Intelligence — show why invoices carry different priorities.
    - Open the AI recommendation — show the detailed "Why?" explanation.
    - Open "What If?" — select "ABC Industries pays 10 days late."
    - Run the simulation — show the cash forecast changing.
    - Show the agent changing its recommendation and the reason for the change.
    - Open Agent Activity — show the "material change detected → strategy re-optimized" log entry.
    - Close with the traditional-vs-CashPilot contrast line.

# Judge-Facing Value Proposition

| **Property**    | **What it means here**                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| Autonomous      | Continuously reassesses the financial state without waiting for a human to ask.                               |
| Forward-looking | Reasons about projected future liquidity, not just today's cash balance.                                      |
| Multi-objective | Balances liquidity, financing cost, discounts, penalties, supplier liquidity, obligations, and risk together. |
| Explainable     | Every decision has a rationale grounded in stored numbers, not invented text.                                 |
| Scenario-aware  | Can answer "what if" questions by re-running the real engine, not by guessing.                                |
| Adaptive        | Changes its recommendation automatically when conditions change.                                              |

# Development Plan & Scope Boundaries

## Build order

- - Phase 1 — Project setup
    - Phase 2 — Database schema + seed data
    - Phase 3 — FastAPI backend skeleton
    - Phase 4 — Financial state engine
    - Phase 5 — Forecasting engine
    - Phase 6 — Decision & allocation engine
    - Phase 7 — Explainability (LLM layer)
    - Phase 8 — Frontend dashboard
    - Phase 9 — Scenario simulator ("What If?")
    - Phase 10 — Agent activity feed
    - Phase 11 — Polish and demo mode

## Deliberately out of scope

- - Complex ERP integrations or real banking/money movement.
    - Blockchain, cryptocurrency, or unnecessary microservices.
    - Complicated authentication systems.
    - Custom LLM training or excessive/unsupported ML models.
    - Generic chatbot features as a substitute for the decision engine.

## Safety framing

This remains a prototype decision-support system. Recommendations are clearly labeled Predicted / Estimated / Recommended / Simulated, never presented as guaranteed savings or guaranteed outcomes. Actual execution of any financial action requires human approval in the demo (AI Recommended → Human Approval → Execute), with simulated execution only.

# Success Criteria

The project succeeds if a judge can understand, within about 60 seconds of the demo, answers to all of the following:

- - What problem exists?
    - What does the agent actually do?
    - Why is it autonomous, rather than a dashboard?
    - How does it account for uncertainty in receivables?
    - How does it choose between payment and financing options?
    - Why did it make its current recommendation?
    - What happens when conditions change?

**Closing line for the pitch: "Traditional systems tell finance teams what happened. CashPilot AI continuously evaluates what should happen next."**