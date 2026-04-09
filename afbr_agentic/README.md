# 🧠 AFBR – Autonomous Financial Behavioral Regulator
### Simplified Agentic AI Prototype

> **Inspired by** the *Autonomous Financial Behavioral Regulator (AFBR)* patent concept.  
> This is a simplified prototype for academic evaluation — not a full patent implementation.

---

## 1. Project Overview

AFBR is a **multi-agent AI system** that predicts impulsive financial behaviour **before** a transaction is confirmed. When a high-risk transaction is detected, the system:

- Computes a risk score (LCPI)
- Engages an LLM-powered **Negotiation Agent** that generates a personalised persuasion message
- Applies **Strategic Friction** (delays, mandatory justifications)
- Logs the outcome to **MongoDB**
- Adapts its intervention threshold based on your behavioral history

The user **always retains full control** — the system advises, never blocks.

---

## 2. Problem Statement

Traditional banking apps approve transactions reactively — after the user has already committed. By that point, the psychological impulse has already been satisfied, and regret rarely changes future behaviour.

**The gap:** No existing consumer system intervenes **before** confirmation using adaptive, personalised AI negotiation.

---

## 3. AFBR Inspiration

This project is **inspired by** the *Autonomous Financial Behavioral Regulator (AFBR)* patent concept, which proposes:

| AFBR Patent Concept | Our Implementation |
|---------------------|--------------------|
| Predict impulsive behaviour before confirmation | LCPI risk score computed before UI confirmation |
| Predictive negotiation | Anthropic Claude API generates personalised messages |
| Strategic friction | Tiered delays + mandatory justification |
| Human-in-the-loop | User always chooses: Proceed / Modify / Defer |
| Closed-loop behavioral feedback | MongoDB logs → AdaptiveThresholdAgent → updated threshold |

---

## 4. Why This Is Agentic AI

| Agentic Property | How AFBR Implements It |
|-----------------|------------------------|
| **Autonomy** | Each agent runs independently with typed inputs/outputs |
| **Goal-directed** | System goal: prevent impulsive overspending |
| **Specialised roles** | 7 agents with distinct responsibilities |
| **Agent-to-agent communication** | Typed Python dataclasses passed between agents |
| **Closed-loop feedback** | LoggingAgent → MongoDB → AdaptiveThresholdAgent → DecisionAgent |
| **LLM reasoning** | NegotiationAgent uses Claude to reason about personalised advice |
| **Adaptive behaviour** | System changes strategy based on user history |

---

## 5. Architecture

```
[Streamlit UI]
      |
[1] Transaction Agent  →  normalise + validate
      |
[2] Behavior Analysis Agent  ←── MongoDB (history)
      |  LCPI score
[3] Decision Agent  ←── [7] Adaptive Threshold Agent
      |
  ┌───┴────────────────┐
 Low Risk          High Risk
  |                    |
Confirm      [4] Negotiation Agent  ←── Anthropic Claude API
                        |
             [5] Friction Agent
                        |
                User: Proceed / Modify / Defer
                        |
             [6] Logging Agent  →  MongoDB behavior_logs
                        |
             [7] Adaptive Threshold Agent  (closed loop)
```

---

## 6. Agent Descriptions

| # | Agent | File | Role |
|---|-------|------|------|
| 1 | Transaction Agent | `agents/transaction_agent.py` | Validate + normalise input |
| 2 | Behavior Analysis Agent | `agents/behavior_agent.py` | Compute LCPI risk score |
| 3 | Decision Agent | `agents/decision_agent.py` | Threshold-based intervention |
| 4 | Negotiation Agent | `agents/negotiation_agent.py` | LLM-generated persuasion |
| 5 | Friction Agent | `agents/friction_agent.py` | Strategic friction policy |
| 6 | Logging Agent | `agents/logging_agent.py` | Persist outcomes to MongoDB |
| 7 | Adaptive Threshold Agent | `agents/threshold_agent.py` | Dynamic threshold from feedback |

---

## 7. MongoDB Schema

**Database:** `afbr_db`

**Collection: `transactions`**
```json
{
  "amount": 3500.0,
  "category": "shopping",
  "timestamp": "2024-01-15T14:32:00Z",
  "remaining_budget": 8000.0
}
```

**Collection: `behavior_logs`**
```json
{
  "transaction_id": "65a4f...",
  "lcpi_score": 0.712,
  "decision": "proceed_override",
  "override": true,
  "friction_level": "High",
  "reason": "One-time offer",
  "personality": "Impulsive",
  "threshold": 0.582,
  "timestamp": "2024-01-15T14:33:12Z"
}
```

---

## 8. LCPI Formula

```
LCPI = 0.4 × (amount / remaining_budget)
     + 0.2 × (transactions_today / 10)
     + 0.2 × (category_spending_ratio)
     + 0.2 × (late_night_flag)

Clamped to [0.0, 1.0]
```

| LCPI | Risk Level |
|------|-----------|
| < 0.35 | Low |
| 0.35–0.55 | Moderate |
| 0.55–0.75 | High |
| > 0.75 | Critical |

---

## 9. Strategic Friction

| Level | Condition | Actions |
|-------|-----------|---------|
| Low | margin < 0.15 | Warning banner |
| Medium | margin 0.15–0.30 | Warning + 10s forced delay |
| High | margin > 0.30 | Warning + 10s delay + mandatory justification |

`margin = lcpi_score − threshold`

---

## 10. Adaptive Threshold

Default threshold: **0.55**. Adjustments:

```
override_rate > 0.45  →  +0.030  (reduce alert fatigue)
override_rate < 0.20  →  -0.020  (be stricter)
compliance_rate > 0.75 → +0.015  (reward compliance)
compliance_rate < 0.45 → -0.015  (increase vigilance)
avg_risk > 0.70       →  -0.010  (high-risk user)
```
Clamped to **[0.35, 0.85]**.

---

## 11. Setup Instructions

### A. MongoDB Atlas

1. Create free account at https://cloud.mongodb.com
2. Create free M0 cluster
3. Add database user
4. Allow your IP in Network Access
5. Copy connection string

### B. .env Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGO_URI=mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=afbr_db
ANTHROPIC_API_KEY=sk-ant-...
```

> If `ANTHROPIC_API_KEY` is omitted, NegotiationAgent uses deterministic fallback — app still works fully.

### C. Install

```bash
pip install -r requirements.txt
```

---

## 12. How to Run

```bash
cd afbr_agentic
streamlit run app.py
```

Opens at http://localhost:8501 — use the sidebar to navigate to the Explanation page.

---

## 13. Test Scenarios

### Low Risk
```
Amount: ₹500 | Category: food | Budget: ₹15,000 | Time: 2 PM
Expected: LCPI ≈ 0.033 → No intervention
```

### High Risk
```
Amount: ₹7,500 | Category: entertainment | Budget: ₹8,000 | Time: 1:30 AM
Expected: LCPI ≈ 0.88 → High friction + LLM negotiation
```

### Override / Adaptive Threshold
```
Submit high-risk transaction 5 times, click Proceed each time.
Expected: Override rate rises → threshold increases toward 0.58
```

---

## 14. Mermaid Diagrams

### System Architecture
```mermaid
graph TD
    UI[Streamlit UI] --> TA[Transaction Agent]
    TA --> BA[Behavior Analysis Agent]
    BA --> DA[Decision Agent]
    DA -->|Low Risk| CONF[Normal Confirmation]
    DA -->|High Risk| NA[Negotiation Agent]
    NA --> FA[Friction Agent]
    FA --> USER[User Decision]
    USER --> LA[Logging Agent]
    LA --> DB[(MongoDB)]
    DB --> THA[Adaptive Threshold Agent]
    THA --> DA
```

### Closed-Loop Feedback
```mermaid
graph LR
    A[Transaction] --> B[LCPI Computed]
    B --> C{Intervention?}
    C -->|Yes| D[Negotiation + Friction]
    D --> E[User Decision]
    C -->|No| E
    E --> F[Logging Agent]
    F --> G[(MongoDB)]
    G --> H[Adaptive Threshold Agent]
    H -->|Adjusts threshold| C
```

### Decision Flowchart
```mermaid
flowchart TD
    A[User submits transaction] --> B[TransactionAgent]
    B --> C[BehaviorAgent computes LCPI]
    C --> D{LCPI >= threshold?}
    D -->|No| E[Normal confirmation + log]
    D -->|Yes| G[DecisionAgent triggers intervention]
    G --> H[NegotiationAgent message]
    H --> I{Friction level?}
    I -->|Low| J[Warning only]
    I -->|Medium| K[Warning + 10s delay]
    I -->|High| L[Warning + delay + reason]
    J & K & L --> M[User decision]
    M --> N[LoggingAgent → MongoDB]
    N --> O[AdaptiveThresholdAgent updates]
    E --> O
```

---

## 15. Folder Structure

```
afbr_agentic/
├── app.py                    # Main Streamlit app (Transaction UI)
├── pages/
│   └── explanation.py        # System explanation, diagrams, glossary
├── agents/
│   ├── transaction_agent.py  # Agent 1
│   ├── behavior_agent.py     # Agent 2
│   ├── decision_agent.py     # Agent 3
│   ├── negotiation_agent.py  # Agent 4
│   ├── friction_agent.py     # Agent 5
│   ├── logging_agent.py      # Agent 6
│   └── threshold_agent.py    # Agent 7
├── database/
│   └── mongo_client.py       # MongoDB connection + helpers
├── utils/
│   └── lcpi_calculator.py    # LCPI formula utility
├── .env.example
├── requirements.txt
└── README.md
```

---

*Built with: Python · Streamlit · MongoDB · Anthropic Claude API · Matplotlib · Pandas*  
*Inspired by the AFBR patent concept — academic prototype only*
