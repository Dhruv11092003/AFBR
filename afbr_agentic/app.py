"""
app.py
──────
AFBR Agentic – Main Streamlit Application (Page 1)
Autonomous Financial Behavioral Regulator – Simplified Agentic AI Prototype

Bug fixes applied (v3):
  [BUG 1] Budget never decreasing: get_transactions_today now returns
          total_spent_today. We subtract it from remaining_budget to compute
          the REAL effective remaining budget used in LCPI and friction display.

  [BUG 2] History table showing empty: get_recent_logs now pre-converts
          datetimes to strings, so pd.DataFrame() never raises a
          mixed-timezone error. Also moved history section OUTSIDE the
          `if submitted:` block so it always renders.

  [BUG 3] CryptographyDeprecationWarning: suppressed at import time in
          mongo_client.py via warnings.filterwarnings().
"""

import sys
import os
import warnings

# Suppress pymongo/pyopenssl CryptographyDeprecationWarning at process level
warnings.filterwarnings("ignore", message=".*serial number.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymongo")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Agent imports ──────────────────────────────────────────────────────────────
from agents.transaction_agent import TransactionAgent
from agents.behavior_agent import BehaviorAnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.negotiation_agent import NegotiationAgent
from agents.friction_agent import StrategicFrictionAgent
from agents.logging_agent import LoggingAgent, LogEntry
from agents.threshold_agent import AdaptiveThresholdAgent
from utils.lcpi_calculator import lcpi_label, lcpi_color

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AFBR – Agentic Financial Regulator",
    page_icon="",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title(" AFBR System")
st.sidebar.markdown("**Autonomous Financial Behavioral Regulator**")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="Main App")
st.sidebar.page_link("pages/explanation.py", label="Explanation")

# ── Instantiate agents (cached across reruns) ──────────────────────────────────
@st.cache_resource
def load_agents():
    return {
        "tx":        TransactionAgent(),
        "behavior":  BehaviorAnalysisAgent(),
        "decision":  DecisionAgent(),
        "negotiate": NegotiationAgent(),
        "friction":  StrategicFrictionAgent(),
        "logger":    LoggingAgent(),
        "threshold": AdaptiveThresholdAgent(),
    }

agents = load_agents()

# ── MongoDB connection check ───────────────────────────────────────────────────
@st.cache_resource
def check_mongo():
    try:
        from database.mongo_client import get_db
        get_db()
        return True, ""
    except Exception as exc:
        return False, str(exc)

mongo_ok, mongo_err = check_mongo()

# ── Helper: current UTC time ───────────────────────────────────────────────────
def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_mongo_history():
    try:
        from database.mongo_client import get_db

        db = get_db()
        collection = db["transactions"]

        # Fetch ALL entries (no limit, no filter)
        logs = list(collection.find().sort("timestamp", -1))

        # Convert ObjectId → string (important for pandas)
        for log in logs:
            log["_id"] = str(log["_id"])

        return logs

    except Exception as e:
        print("Mongo Fetch Error:", e)
        return []


def get_transactions_today_stats(category: str):
    """
    Returns (txns_today, cat_ratio, total_spent_today).
    FIX: now unpacks 3 values from get_transactions_today().
    """
    try:
        from database.mongo_client import get_transactions_today
        today_start = _now().replace(hour=0, minute=0, second=0, microsecond=0)
        count, ratio, spent = get_transactions_today(category, today_start)
        return count, ratio, spent
    except Exception:
        return 0, 0.0, 0.0


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("AFBR – Autonomous Financial Behavioral Regulator")
st.caption(
    "An Agentic AI prototype inspired by the AFBR patent concept. "
    "Predicts impulsive spending and negotiates before transaction confirmation."
)

if not mongo_ok:
    st.warning(
        f" MongoDB not connected: {mongo_err}\n\n"
        "The app will run in **demo mode** (no data persistence). "
        "Configure `MONGO_URI` and `MONGO_DB` in your `.env` file.",
        icon="",
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT: Form (left) + Pipeline (right)
# ══════════════════════════════════════════════════════════════════════════════
col_form, col_info = st.columns([3, 2])

with col_form:
    st.subheader("💳 Transaction Input")

    with st.form("transaction_form"):
        amount = st.number_input(
            "Transaction Amount (₹)",
            min_value=1.0, max_value=500000.0, value=3000.0, step=100.0,
        )
        category = st.selectbox(
            "Category",
            ["food", "entertainment", "shopping", "travel",
             "healthcare", "education", "utilities", "other"],
        )
        remaining_budget = st.number_input(
            "Your TOTAL Monthly Budget (₹)",
            min_value=100.0, max_value=1000000.0, value=8000.0, step=500.0,
            help="Enter your original budget. Previous transactions will be subtracted automatically.",
        )
        use_now = st.checkbox("Use current timestamp", value=True)
        if not use_now:
            txn_date = st.date_input("Date", value=_now().date())
            txn_hour = st.slider("Hour (24h)", 0, 23, _now().hour)
            txn_ts = datetime(
                txn_date.year, txn_date.month, txn_date.day, txn_hour,
                tzinfo=timezone.utc,
            )
        else:
            txn_ts = _now()

        submitted = st.form_submit_button("🔍 Analyse Transaction", use_container_width=True)

with col_info:
    st.subheader("Agentic Pipeline")
    st.markdown("""
    ```
    [1] Transaction Agent
          ↓
    [2] Behavior Analysis Agent
          ↓ (LCPI score)
    [3] Decision Agent
          ↓ (intervention?)
    [7] Threshold Agent ←──────────────┐
          ↓                            │
    [4] Negotiation Agent              │
          ↓                            │
    [5] Friction Agent                 │
          ↓                            │
    [6] Logging Agent ─────────────────┘
          ↓ (MongoDB)
    Closed-loop Feedback
    ```
    """)
    st.info(
        "Each numbered block is a **separate autonomous agent**. "
        "Agents pass typed dataclasses to each other — no shared global state.",
        
    )

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    # Stage 1: Get adaptive threshold
    current_threshold = agents["threshold"].get_current_threshold()

    # Stage 2: Transaction Agent (validate input)
    tx = agents["tx"].collect(amount, category, remaining_budget, txn_ts)

    # Stage 3: Historical stats from MongoDB
    txns_today, cat_ratio, total_spent_today = get_transactions_today_stats(tx.category)

    # ── BUG FIX 1: Compute REAL remaining budget ──────────────────────────────
    # The user entered their total budget. We subtract today's already-spent
    # amount from MongoDB so the LCPI sees the true current balance.
    real_remaining = max(tx.remaining_budget - total_spent_today, 0.01)

    # Stage 4: Persist transaction intent to MongoDB (before LCPI so it counts
    # in get_transactions_today for next run, but we already have this run's count)
    tx_id = ""
    if mongo_ok:
        try:
            from database.mongo_client import insert_transaction
            tx_id = insert_transaction(
                tx.amount, tx.category, real_remaining, tx.timestamp
            )
        except Exception:
            pass

    # Stage 5: Behavior Analysis Agent → LCPI (uses REAL remaining budget)
    from dataclasses import replace as dc_replace
    tx_for_lcpi = dc_replace(tx, remaining_budget=real_remaining)
    features = agents["behavior"].analyze(tx_for_lcpi, txns_today, cat_ratio)

    # Stage 6: Decision Agent
    decision = agents["decision"].decide(features.lcpi_score, current_threshold)

    # ── Risk Score Display ─────────────────────────────────────────────────────
    st.subheader("Risk Analysis")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("LCPI Score", f"{features.lcpi_score:.3f}")
    r2.metric("Risk Label", lcpi_label(features.lcpi_score))
    r3.metric("Threshold", f"{current_threshold:.3f}")
    r4.metric("Intervention", "YES " if decision.trigger_intervention else "NO ")
    r5.metric(
        "Real Remaining Budget",
        f"₹{real_remaining:,.0f}",
        delta=f"-₹{total_spent_today:,.0f} spent today",
        delta_color="inverse",
        help="Original budget minus today's transactions already in MongoDB",
    )

    risk_color = lcpi_color(features.lcpi_score)
    st.progress(
        features.lcpi_score,
        text=f"LCPI: {features.lcpi_score:.3f}  |  Risk: {lcpi_label(features.lcpi_score)}  [{risk_color}]",
    )

    with st.expander("LCPI Feature Breakdown"):
        budget_ratio = min(tx_for_lcpi.amount / max(real_remaining, 1e-6), 1.0)
        st.markdown(f"""
| Feature | Value | Weight | Contribution |
|---------|-------|--------|--------------|
| Budget Pressure (amount / **real** remaining) | {budget_ratio:.3f} | 0.4 | {0.4 * budget_ratio:.4f} |
| Frequency (txns today / 10) | {min(txns_today / 10, 1):.3f} | 0.2 | {0.2 * min(txns_today / 10, 1):.4f} |
| Category Spending Ratio | {cat_ratio:.3f} | 0.2 | {0.2 * cat_ratio:.4f} |
| Late-Night Flag | {features.late_night_flag} | 0.2 | {0.2 * features.late_night_flag:.4f} |
| **LCPI Total** | | | **{features.lcpi_score:.4f}** |
| Today's spend already logged | ₹{total_spent_today:,.0f} | — | — |
        """)

    st.markdown("---")

    # ── Intervention Path ──────────────────────────────────────────────────────
    if decision.trigger_intervention:
        friction = agents["friction"].apply(
            features.lcpi_score, current_threshold,
            tx_for_lcpi.amount, real_remaining,
        )

        personality = "Planned"
        try:
            from database.mongo_client import get_adaptive_stats
            stats = get_adaptive_stats()
            override_rate = stats.get("override_rate", 0)
            avg_risk = stats.get("avg_risk", 0.5)
            if avg_risk > 0.72 and override_rate > 0.45:
                personality = "Impulsive"
            elif avg_risk > 0.62 and override_rate > 0.3:
                personality = "Risky"
            elif avg_risk < 0.45:
                personality = "Goal-Oriented"
        except Exception:
            pass

        with st.spinner("Negotiation Agent generating message…"):
            neg_message = agents["negotiate"].generate(
                personality, tx_for_lcpi.amount, tx_for_lcpi.category, features
            )

        st.subheader("Intervention Active")
        st.error(friction.instruction)
        st.warning(friction.budget_warning)

        st.markdown(
            "<div style='border:1px solid #e0e0e0; border-radius:8px; padding:1rem; "
            "margin-bottom:1rem;'>"
            "<strong>Negotiation Agent Message</strong></div>",
            unsafe_allow_html=True,
        )
        with st.container():
            st.markdown(neg_message)

        if friction.delay_seconds > 0:
            st.markdown(f"**Mandatory pause: {friction.delay_seconds} seconds**")
            prog = st.progress(0)
            for i in range(friction.delay_seconds):
                time.sleep(1)
                prog.progress(
                    (i + 1) / friction.delay_seconds,
                    text=f"Please wait… {friction.delay_seconds - i - 1}s remaining",
                )
            st.success("Pause complete. You may now make your decision.")

        reason = ""
        if friction.reason_required:
            reason = st.text_area(
                "Justification required (mandatory for high-risk override)",
                placeholder="Explain why you still wish to proceed…",
                key="reason_input",
            )

        st.markdown("---")
        st.markdown("####  Your Decision")
        st.caption("You retain full control. The system will log your choice and learn from it.")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button(" Proceed", use_container_width=True, type="primary"):
                if friction.reason_required and not reason.strip():
                    st.error("Please provide a justification before proceeding.")
                else:
                    entry = LogEntry(
                        transaction_id=tx_id,
                        risk_score=features.lcpi_score,
                        threshold=current_threshold,
                        decision="proceed_override",
                        friction_level=friction.level,
                        user_action="proceed",
                        override=True,
                        personality=personality,
                        negotiation_message=neg_message,
                        reason=reason,
                        timestamp=_now(),
                    )
                    if mongo_ok:
                        agents["logger"].log(entry)
                    st.success(" Transaction logged as PROCEED (override). System has learned from this.")
                    st.balloons()

        with col_b:
            if st.button("✏️ Modify", use_container_width=True):
                entry = LogEntry(
                    transaction_id=tx_id,
                    risk_score=features.lcpi_score,
                    threshold=current_threshold,
                    decision="modify",
                    friction_level=friction.level,
                    user_action="modify",
                    override=False,
                    personality=personality,
                    negotiation_message=neg_message,
                    reason=reason,
                    timestamp=_now(),
                )
                if mongo_ok:
                    agents["logger"].log(entry)
                st.info("✏️ Modify your transaction above and re-submit.")

        with col_c:
            if st.button("Defer", use_container_width=True):
                entry = LogEntry(
                    transaction_id=tx_id,
                    risk_score=features.lcpi_score,
                    threshold=current_threshold,
                    decision="defer",
                    friction_level=friction.level,
                    user_action="defer",
                    override=False,
                    personality=personality,
                    negotiation_message=neg_message,
                    reason=reason,
                    timestamp=_now(),
                )
                if mongo_ok:
                    agents["logger"].log(entry)
                st.success("Transaction deferred. Great financial discipline!")

    else:
        # Low-risk path
        st.success(
            f"Low-risk transaction (LCPI {features.lcpi_score:.3f} < "
            f"threshold {current_threshold:.3f}). No intervention required."
        )
        if st.button(" Confirm Transaction", type="primary"):
            entry = LogEntry(
                transaction_id=tx_id,
                risk_score=features.lcpi_score,
                threshold=current_threshold,
                decision="proceed",
                friction_level="None",
                user_action="proceed",
                override=False,
                personality="Planned",
                negotiation_message="",
                reason="",
                timestamp=_now(),
            )
            if mongo_ok:
                agents["logger"].log(entry)
            st.success("Transaction confirmed and logged.")

    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY TABLE + RISK TREND  (always visible, NOT inside `if submitted`)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Transaction History (Last Entries)")

logs = get_mongo_history()

if logs:
    df = pd.DataFrame(logs)

    # Select correct columns
    display_cols = {
        "timestamp": "Timestamp",
        "amount": "Amount",
        "category": "Category",
        "remaining_budget": "Remaining Budget",
    }

    cols_present = [c for c in display_cols if c in df.columns]
    df_show = df[cols_present].rename(columns=display_cols)

    # Formatting
    if "Timestamp" in df_show.columns:
        df_show["Timestamp"] = df_show["Timestamp"].astype(str)

    if "Amount" in df_show.columns:
        df_show["Amount"] = pd.to_numeric(df_show["Amount"], errors="coerce")

    if "Remaining Budget" in df_show.columns:
        df_show["Remaining Budget"] = pd.to_numeric(df_show["Remaining Budget"], errors="coerce")

    st.dataframe(df_show, use_container_width=True, height=300)

    # ── OPTIONAL: Amount Trend ─────────────────────────────
    if "amount" in df.columns and len(df) > 1:
        st.subheader("Spending Trend")

        fig, ax = plt.subplots(figsize=(10, 3))

        amounts = pd.to_numeric(df["amount"], errors="coerce").fillna(0).tolist()[::-1]

        ax.plot(amounts, marker="o")
        ax.set_title("Spending Over Time")
        ax.set_xlabel("Transaction (oldest → newest)")
        ax.set_ylabel("Amount")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

else:
    st.warning("No transactions found in MongoDB.")

# ── Adaptive Threshold Status ──────────────────────────────────────────────────
with st.expander("🔧 Adaptive Threshold Status"):
    try:
        from database.mongo_client import get_adaptive_stats
        stats = get_adaptive_stats()
        s1, s2, s3 = st.columns(3)
        s1.metric("Override Rate", f"{stats['override_rate']:.1%}")
        s2.metric("Compliance Rate", f"{stats['compliance_rate']:.1%}")
        s3.metric("Avg LCPI", f"{stats['avg_risk']:.3f}")

        threshold_agent = agents["threshold"]
        current_base = threshold_agent.get_current_threshold()
        update = threshold_agent.update(
            old_threshold=current_base,
            compliance_rate=stats["compliance_rate"],
            override_rate=stats["override_rate"],
            avg_risk=stats["avg_risk"],
        )
        sign = "+" if update.adjustment_applied >= 0 else ""
        st.markdown(f"""
**Threshold Adjustment Logic:**
- Current base threshold: `{current_base:.4f}`
- Adjustment applied: `{sign}{update.adjustment_applied}`
- New threshold: `{update.new_threshold:.4f}`
        """)
    except Exception:
        st.info("Connect MongoDB to see adaptive threshold analytics.")

st.markdown("---")
st.caption(
    "AFBR Prototype | Inspired by the AFBR patent concept | "
    "Built with Streamlit + MongoDB + Python"
)
