from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="AFBR - Explanation", layout="wide")
st.title("AFBR Explanation Page")
st.caption("Autonomous Financial Behavioral Regulator (AFBR) – simplified prototype inspired by AFBR concepts.")


def render_mermaid(diagram: str, height: int = 380) -> None:
    components.html(
        f"""
        <div class="mermaid">{diagram}</div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=height,
        scrolling=True,
    )


st.header("Project Overview")
st.write(
    "This project predicts impulsive spending before final confirmation and intervenes via "
    "negotiation + strategic friction while preserving human final control."
)

st.header("Problem Statement")
st.write(
    "Users often make high-risk, emotionally-driven purchases. Traditional apps track spending but rarely "
    "intervene at decision time. AFBR adds decision-time behavioral safeguards."
)

st.header("AFBR Inspiration")
st.write(
    "This system is **inspired by AFBR concepts** (predictive intervention, strategic friction, and feedback adaptation) "
    "but implemented as a simplified educational prototype."
)

st.header("What is Agentic AI?")
st.write(
    "Agentic AI uses autonomous specialized agents that communicate sequentially, make scoped decisions, "
    "and adapt from outcomes."
)

st.header("Why this system is Agentic AI")
st.markdown(
    """
- Separate agents with unique responsibilities.
- Explicit agent-to-agent handoff pipeline.
- Conditional intervention decisioning.
- Human-in-the-loop final decision.
- Closed-loop threshold adaptation from logged outcomes.
"""
)

st.header("Agent Explanations")
st.markdown(
    """
1. **Transaction Agent** – normalizes transaction data.
2. **Behavior Analysis Agent** – computes historical features and LCPI.
3. **Decision Agent** – applies adaptive threshold intervention logic.
4. **Negotiation Agent** – generates pre-confirmation guidance.
5. **Friction Agent** – warning / delay / reason friction.
6. **Logging Agent** – stores transaction and behavior decisions.
7. **Adaptive Threshold Agent** – updates future threshold sensitivity.
"""
)

st.header("LCPI Formula")
st.latex(r"LCPI = 0.4(\frac{amount}{remaining\_budget}) + 0.2(\frac{transactions\_today}{10}) + 0.2(category\_spending\_ratio) + 0.2(late\_night\_flag)")
st.write("LCPI is clamped between 0 and 1.")

st.header("Strategic Friction")
st.markdown(
    """
- **Warning**: lightweight prompt.
- **Delay**: mandatory 10-second pause.
- **Reason**: captures rationale before proceeding on high-risk actions.
"""
)

st.header("Adaptive Threshold")
st.write(
    "Threshold is updated from behavior logs (override patterns, defer rate, and average risk), "
    "producing a closed-loop regulator."
)

st.header("Closed-loop Feedback")
st.write("Logged outcomes influence future intervention thresholds, shaping subsequent decisions.")

st.header("Mermaid Diagrams")

st.subheader("1) System Architecture")
render_mermaid(
    """
flowchart LR
    T[Transaction Agent] --> B[Behavior Analysis Agent]
    B --> D[Decision Agent]
    D --> N[Negotiation Agent]
    N --> F[Friction Agent]
    F --> H[Human Decision]
    H --> L[Logging Agent]
    L --> A[Adaptive Threshold Agent]
    A --> D
"""
)

st.subheader("2) Agent Workflow")
render_mermaid(
    """
flowchart TD
    I[Input Transaction] --> TA[Transaction Agent]
    TA --> BA[Behavior Agent]
    BA --> DA[Decision Agent]
    DA -->|Low risk| P[Proceed normally]
    DA -->|High risk| NA[Negotiation Agent]
    NA --> FA[Friction Agent]
    FA --> U[User action: Proceed/Modify/Defer]
    U --> LA[Logging Agent]
    LA --> AT[Adaptive Threshold Agent]
"""
)

st.subheader("3) Closed-loop Feedback")
render_mermaid(
    """
flowchart LR
    E[Decision Event] --> LG[Log Behavior]
    LG --> M[Compute rates + avg risk]
    M --> UP[Update Threshold]
    UP --> E
"""
)

st.subheader("4) Decision Flowchart")
render_mermaid(
    """
flowchart TD
    S([Start]) --> R{LCPI >= Threshold?}
    R -->|No| PRO[Proceed]
    R -->|Yes| NEG[Negotiate]
    NEG --> FRC[Friction]
    FRC --> DEC{User choice}
    DEC -->|Proceed| OVR[Override]
    DEC -->|Modify| MOD[Modify]
    DEC -->|Defer| DEF[Defer]
    PRO --> LOG[Log]
    OVR --> LOG
    MOD --> LOG
    DEF --> LOG
    LOG --> END([End])
"""
)
