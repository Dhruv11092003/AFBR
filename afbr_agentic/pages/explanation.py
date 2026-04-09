"""
pages/explanation.py
────────────────────
AFBR Agentic – Explanation Page (Page 2)
Describes the system, agents, concepts, and diagrams for academic evaluation.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="AFBR – System Explanation",
    page_icon="📖",
    layout="wide",
)

st.title("📖 AFBR – System Explanation & Architecture")
st.caption("A deep-dive into the system design, concepts, and agentic AI architecture.")

# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏛️ Overview",
    "🤖 Agents",
    "📐 LCPI",
    "🔀 Diagrams",
    "🔄 Feedback Loop",
    "📚 Glossary",
])

# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.header("Project Overview")
    st.markdown("""
## Problem Statement

Traditional banking apps approve or reject transactions **after** the user confirms them.
By then, the psychological commitment is already made — behavioural economics research
shows that post-transaction regret rarely changes future behaviour.

**The gap:** No system currently *intervenes before confirmation* using predictive
behavioural intelligence combined with personalised negotiation.

---

## AFBR Inspiration

> This system is **inspired by** the *Autonomous Financial Behavioral Regulator (AFBR)* patent concept.

The AFBR patent proposes a system that:
- **Predicts** impulsive financial behaviour before transaction confirmation
- **Intervenes** using predictive negotiation and strategic friction
- **Maintains** human-in-the-loop (never blocks)
- **Adapts** its thresholds using closed-loop behavioral feedback

Our prototype implements a **simplified version** of this architecture using:
- Python-based autonomous agents
- MongoDB for behavioral logging
- Anthropic Claude API for LLM-powered negotiation
- Streamlit for the interactive UI

---

## What Is Agentic AI?

**Agentic AI** refers to AI systems where multiple specialised agents:
- Act **autonomously** toward a goal
- **Communicate** structured outputs to each other
- **Reason** about context before acting
- **Adapt** behaviour based on feedback

This is distinct from a single LLM chatbot — each agent has a defined role,
inputs, and outputs. Together they form an **intelligent pipeline**.

---

## Why This System Is Agentic AI

| Property | How AFBR implements it |
|----------|----------------------|
| **Autonomy** | Each agent operates independently with typed inputs/outputs |
| **Goal-directed** | System goal: prevent impulsive overspending |
| **Multi-agent** | 7 specialised agents, each with a unique responsibility |
| **Adaptive** | AdaptiveThresholdAgent adjusts based on real user history |
| **Closed-loop** | Logged outcomes feed back into decision thresholds |
| **Human-in-loop** | User always makes final decision; agents only advise |

---

## System Novelty

1. **Pre-confirmation intervention** — acts before the user confirms
2. **LLM-powered negotiation** — personalised, not generic warnings
3. **Closed-loop adaptation** — thresholds shift based on your behaviour
4. **Personality-aware messaging** — tone adapts (Impulsive / Planned / Goal-Oriented)
5. **Strategic friction** — tiered delays and justification requirements
    """)

# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.header("Agent Descriptions")
    agents_info = [
        {
            "num": "01",
            "name": "Transaction Agent",
            "file": "agents/transaction_agent.py",
            "role": "Entry point of the pipeline. Receives raw user input, validates it, and produces a normalised `TransactionInput` dataclass.",
            "inputs": "amount, category, remaining_budget, timestamp",
            "outputs": "TransactionInput",
            "key_logic": "Clamps negatives, normalises category, defaults timestamp to now().",
        },
        {
            "num": "02",
            "name": "Behavior Analysis Agent",
            "file": "agents/behavior_agent.py",
            "role": "Computes behavioural features from transaction history and calculates the LCPI risk score.",
            "inputs": "TransactionInput, transactions_today (MongoDB), category_spending_ratio (MongoDB)",
            "outputs": "BehaviorFeatures (includes lcpi_score)",
            "key_logic": "Applies the LCPI formula: 0.4×budget_pressure + 0.2×frequency + 0.2×category_ratio + 0.2×late_night.",
        },
        {
            "num": "03",
            "name": "Decision Agent",
            "file": "agents/decision_agent.py",
            "role": "Compares LCPI against the adaptive threshold and decides whether to trigger intervention.",
            "inputs": "lcpi_score (float), threshold (float)",
            "outputs": "RiskDecision (trigger_intervention, margin, risk_label)",
            "key_logic": "trigger = lcpi_score >= threshold. Never blocks — only signals downstream agents.",
        },
        {
            "num": "04",
            "name": "Negotiation Agent",
            "file": "agents/negotiation_agent.py",
            "role": "Generates a personalised negotiation message using Anthropic Claude API or a deterministic fallback.",
            "inputs": "personality, amount, category, BehaviorFeatures",
            "outputs": "Negotiation message string (4 bullet points)",
            "key_logic": "Adapts tone per personality type. Falls back gracefully if API is unavailable.",
        },
        {
            "num": "05",
            "name": "Strategic Friction Agent",
            "file": "agents/friction_agent.py",
            "role": "Determines friction level (Low/Medium/High) and enforces mandatory pause and justification requirements.",
            "inputs": "risk_score, threshold, amount, remaining_budget",
            "outputs": "FrictionPolicy (level, delay_seconds, reason_required, budget_warning)",
            "key_logic": "Friction ∝ (risk_score − threshold). Never blocks transaction.",
        },
        {
            "num": "06",
            "name": "Logging Agent",
            "file": "agents/logging_agent.py",
            "role": "Persists all behavioral outcomes to MongoDB `behavior_logs` collection for closed-loop feedback.",
            "inputs": "LogEntry dataclass",
            "outputs": "MongoDB document insert",
            "key_logic": "Records lcpi_score, decision, override status, friction_level, reason, personality.",
        },
        {
            "num": "07",
            "name": "Adaptive Threshold Agent",
            "file": "agents/threshold_agent.py",
            "role": "Reads historical logs from MongoDB and dynamically adjusts the intervention threshold.",
            "inputs": "compliance_rate, override_rate, avg_risk (from MongoDB)",
            "outputs": "ThresholdUpdate (new_threshold)",
            "key_logic": "High overrides → raise threshold (reduce alert fatigue). Low overrides → lower threshold. Clamped to [0.35, 0.85].",
        },
    ]

    for a in agents_info:
        with st.expander(f"Agent {a['num']} – {a['name']}  (`{a['file']}`)"):
            st.markdown(f"**Role:** {a['role']}")
            st.markdown(f"**Inputs:** `{a['inputs']}`")
            st.markdown(f"**Outputs:** `{a['outputs']}`")
            st.markdown(f"**Key Logic:** {a['key_logic']}")

# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.header("LCPI – Liquidity-Calibrated Predictive Index")
    st.markdown(r"""
## Formula

$$\text{LCPI} = 0.4 \times \frac{\text{amount}}{\text{remaining\_budget}} + 0.2 \times \frac{\text{txns\_today}}{10} + 0.2 \times \text{category\_ratio} + 0.2 \times \text{late\_night\_flag}$$

**Clamped to $[0.0,\ 1.0]$**

---

## Component Explanation

| Component | Weight | Rationale |
|-----------|--------|-----------|
| `amount / remaining_budget` | **0.4** | Largest weight — how much of budget this single purchase uses |
| `transactions_today / 10` | **0.2** | High frequency today → impulsive behaviour pattern |
| `category_spending_ratio` | **0.2** | Over-concentrating spend in one category is a risk signal |
| `late_night_flag` | **0.2** | Purchases between 23:00–05:00 are associated with impulsivity |

---

## Risk Thresholds

| LCPI Range | Label | Action |
|------------|-------|--------|
| 0.00 – 0.35 | 🟢 Low Risk | Normal confirmation |
| 0.35 – 0.55 | 🟡 Moderate Risk | Warning (approaching threshold) |
| 0.55 – 0.75 | 🔴 High Risk | Negotiation + Medium friction |
| 0.75 – 1.00 | 🚨 Critical Risk | Negotiation + High friction + justification |

---

## Strategic Friction Levels

| Friction Level | Condition | Measures |
|---------------|-----------|---------|
| **Low** | LCPI just above threshold (margin < 0.15) | Warning banner only |
| **Medium** | Moderate excess (margin 0.15–0.30) | Warning + 10-second forced delay |
| **High** | Severe excess (margin > 0.30) | Warning + 10s delay + mandatory written justification |

*Friction never blocks transactions — it introduces reflective pause points.*

---

## Adaptive Threshold

The threshold starts at **0.55** and shifts based on logged behavior:

- **High override rate (>45%)** → threshold rises by 0.03 (reduce alert fatigue)
- **Low override rate (<20%)** → threshold falls by 0.02 (user is compliant; be stricter)
- **High compliance (>75%)** → threshold rises by 0.015 (reward good behaviour)
- **High avg risk (>0.70)** → threshold falls by 0.01 (user is genuinely risky)

Clamped to **[0.35, 0.85]** to prevent extremes.
    """)

# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.header("System Diagrams (Mermaid)")
    st.info("Copy these diagrams into any Mermaid-compatible renderer (e.g. mermaid.live, GitHub markdown, Notion).")

    st.subheader("1. System Architecture")
    st.code("""
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
    """, language="mermaid")

    st.subheader("2. Agent Workflow")
    st.code("""
sequenceDiagram
    participant U as User
    participant TA as TransactionAgent
    participant BA as BehaviorAgent
    participant DA as DecisionAgent
    participant NA as NegotiationAgent
    participant FA as FrictionAgent
    participant LA as LoggingAgent
    participant DB as MongoDB
    participant THA as ThresholdAgent

    U->>TA: Enter transaction details
    TA->>BA: TransactionInput
    DB-->>BA: Historical stats (txns_today, category_ratio)
    BA->>DA: BehaviorFeatures + LCPI score
    DB-->>THA: Logged behavior history
    THA-->>DA: Adaptive threshold
    DA->>NA: Trigger intervention (if LCPI >= threshold)
    NA->>FA: Negotiation message
    FA->>U: Friction UI (delay, reason)
    U->>LA: User decision (proceed/modify/defer)
    LA->>DB: Store behavior_log
    DB-->>THA: Update threshold
    """, language="mermaid")

    st.subheader("3. Closed-Loop Feedback")
    st.code("""
graph LR
    A[Transaction] --> B[LCPI Computed]
    B --> C{Intervention?}
    C -->|Yes| D[Negotiation + Friction]
    D --> E[User Decision]
    C -->|No| E
    E --> F[Logging Agent]
    F --> G[(MongoDB behavior_logs)]
    G --> H[Adaptive Threshold Agent]
    H -->|Adjusts threshold| C
    style H fill:#f39c12,color:#fff
    style G fill:#2ecc71,color:#fff
    """, language="mermaid")

    st.subheader("4. Decision Flowchart")
    st.code("""
flowchart TD
    A[User submits transaction] --> B[TransactionAgent normalises input]
    B --> C[BehaviorAgent computes LCPI]
    C --> D{LCPI >= threshold?}
    D -->|No| E[✅ Normal confirmation]
    E --> F[Log as compliant]
    D -->|Yes| G[DecisionAgent triggers intervention]
    G --> H[NegotiationAgent generates message]
    H --> I{Friction level?}
    I -->|Low| J[Show warning only]
    I -->|Medium| K[Warning + 10s delay]
    I -->|High| L[Warning + delay + reason required]
    J & K & L --> M[User sees options]
    M -->|Proceed| N[Log as override]
    M -->|Modify| O[Log as modify]
    M -->|Defer| P[Log as defer]
    N & O & P --> Q[AdaptiveThresholdAgent recalculates]
    Q --> R[Update threshold for next transaction]
    F --> R
    """, language="mermaid")

# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.header("Closed-Loop Feedback System")
    st.markdown("""
## What is a Closed-Loop System?

A **closed-loop** (feedback) system uses its own outputs as inputs to improve future decisions.

In AFBR:

```
Transaction → LCPI → Decision → User Action → Log → Threshold Update → Next Decision
     ↑_______________________________________________________________|
```

### How the Loop Closes

1. **Every transaction** is processed through the 7-agent pipeline
2. **Every user decision** (proceed/modify/defer + override flag) is stored in MongoDB
3. **AdaptiveThresholdAgent** reads the full history and computes:
   - Average LCPI (true risk level of this user)
   - Override rate (how often user ignores warnings)
   - Compliance rate (how often user follows advice)
4. **Threshold is adjusted** to match the user's actual behavior pattern
5. **Next transaction** uses the updated threshold → more relevant interventions

### Why This Matters

Without feedback, a fixed threshold treats all users the same.
With feedback:
- A **habitual ignorer** gets a higher threshold (fewer false alarms)
- A **compliant user** gets a lower threshold (catches more risky txns)
- A **genuinely risky user** is monitored more tightly

This is **personalised, adaptive financial intelligence** — not a one-size-fits-all rule engine.

---

## MongoDB Schema

### `transactions` collection
```json
{
  "amount": 3000.0,
  "category": "shopping",
  "timestamp": "2024-01-15T14:32:00Z",
  "remaining_budget": 8000.0
}
```

### `behavior_logs` collection
```json
{
  "transaction_id": "ObjectId(...)",
  "lcpi_score": 0.712,
  "decision": "proceed_override",
  "override": true,
  "friction_level": "High",
  "reason": "One-time offer, won't happen again",
  "personality": "Impulsive",
  "threshold": 0.582,
  "timestamp": "2024-01-15T14:33:12Z"
}
```
    """)

# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.header("Glossary")
    terms = {
        "AFBR": "Autonomous Financial Behavioral Regulator – the patent concept this project is inspired by.",
        "LCPI": "Liquidity-Calibrated Predictive Index – the risk score computed per transaction [0–1].",
        "Agentic AI": "AI architecture with multiple autonomous agents each having defined goals, inputs, and outputs.",
        "Strategic Friction": "Intentional cognitive pause (delay, warning, justification) before a high-risk action.",
        "Adaptive Threshold": "The LCPI cutoff for intervention, dynamically adjusted based on user behavior history.",
        "Closed-Loop Feedback": "System uses its own past outputs (logs) to improve future decisions (threshold).",
        "Override": "User proceeds with a high-risk transaction despite intervention. Logged for threshold adjustment.",
        "Compliance": "User modifies or defers a high-risk transaction following intervention advice.",
        "Human-in-the-Loop": "Design principle: AI advises, human always decides. System never blocks autonomously.",
        "Negotiation Agent": "LLM-powered agent that generates personalised persuasion before transaction confirmation.",
        "Personality Type": "Behavioral classification (Impulsive/Risky/Planned/Goal-Oriented) used to tune negotiation tone.",
    }
    for term, definition in terms.items():
        st.markdown(f"**{term}:** {definition}")

st.markdown("---")
st.caption("AFBR Prototype | Explanation Page | Inspired by the AFBR patent concept")
