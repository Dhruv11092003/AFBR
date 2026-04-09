from __future__ import annotations

import time
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from afbr_agentic.agents.behavior_agent import BehaviorAnalysisAgent
from afbr_agentic.agents.decision_agent import DecisionAgent
from afbr_agentic.agents.friction_agent import FrictionAgent
from afbr_agentic.agents.logging_agent import LoggingAgent
from afbr_agentic.agents.negotiation_agent import NegotiationAgent
from afbr_agentic.agents.threshold_agent import AdaptiveThresholdAgent
from afbr_agentic.agents.transaction_agent import TransactionAgent
from afbr_agentic.database.mongo_client import mongo_manager


st.set_page_config(page_title="AFBR - Main App", layout="wide")

status = mongo_manager.connect()
db = mongo_manager.db()
transactions_col = db.transactions
behavior_col = db.behavior_logs
settings_col = db.settings

transaction_agent = TransactionAgent()
behavior_agent = BehaviorAnalysisAgent()
decision_agent = DecisionAgent()
negotiation_agent = NegotiationAgent()
friction_agent = FrictionAgent()
logging_agent = LoggingAgent()
threshold_agent = AdaptiveThresholdAgent()


st.title("Autonomous Financial Behavioral Regulator (AFBR)")
st.caption("Simplified Agentic AI prototype inspired by AFBR behavioral intervention concepts.")

if status.mode != "mongo":
    st.warning(status.message)
else:
    st.success(status.message)

st.markdown("### Step 1: Transaction Input")
with st.form("transaction_form"):
    amount = st.number_input("Amount ($)", min_value=0.0, value=120.0, step=5.0)
    category = st.selectbox("Category", ["food", "shopping", "transport", "entertainment", "health", "other"])
    remaining_budget = st.number_input("Remaining Budget ($)", min_value=1.0, value=500.0, step=10.0)
    tx_time = st.time_input("Transaction Time", value=datetime.now().time())
    submitted = st.form_submit_button("Run Agentic Pipeline")

if submitted:
    ts = datetime.now(timezone.utc).replace(
        hour=tx_time.hour,
        minute=tx_time.minute,
        second=0,
        microsecond=0,
    )
    tx = transaction_agent.collect(amount, category, remaining_budget, ts)

    transaction_id = logging_agent.log_transaction(
        transactions_col,
        {
            "amount": tx.amount,
            "category": tx.category,
            "timestamp": tx.timestamp,
            "remaining_budget": tx.remaining_budget,
        },
    )

    behavior = behavior_agent.analyze(tx, transactions_col)
    threshold = threshold_agent.get_current_threshold(settings_col)
    decision = decision_agent.decide(behavior.lcpi_score, threshold)

    st.markdown("### Step 2: Behavior Analysis Agent")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LCPI", f"{behavior.lcpi_score:.2f}")
    c2.metric("Transactions Today", behavior.transactions_today)
    c3.metric("Category Ratio", f"{behavior.category_spending_ratio:.2f}")
    c4.metric("Late Night", behavior.late_night_flag)

    st.markdown("### Step 3: Decision Agent")
    st.info(
        f"Intervention Required: **{decision.intervention_required}** | "
        f"Threshold: **{decision.threshold:.2f}** | Margin: **{decision.risk_margin:.2f}**"
    )

    negotiation_message = "Low risk detected. You may proceed normally."
    friction_level = "none"
    reason = ""

    st.markdown("### Step 4/5: Negotiation + Strategic Friction")
    if decision.intervention_required:
        negotiation_message = negotiation_agent.generate_message(
            category=tx.category,
            amount=tx.amount,
            remaining_budget=tx.remaining_budget,
            lcpi_score=behavior.lcpi_score,
        )
        st.warning("Negotiation Agent Message")
        st.write(negotiation_message)

        friction = friction_agent.apply(
            lcpi_score=behavior.lcpi_score,
            threshold=threshold,
            amount=tx.amount,
            remaining_budget=tx.remaining_budget,
        )
        friction_level = friction.level
        st.error(f"Friction Level: {friction.level}")
        st.write(friction.warning)
        st.write(friction.budget_impact)

        if friction.delay_seconds:
            with st.spinner(f"Applying strategic delay ({friction.delay_seconds}s)..."):
                time.sleep(friction.delay_seconds)

        if friction.reason_required:
            reason = st.text_input("Reason (required for high friction)")
    else:
        st.success("No intervention required. Proceeding with normal confirmation.")

    st.markdown("### Step 6: Human-in-the-loop Decision")
    user_decision = st.radio("Select final action", ["proceed", "modify", "defer"], horizontal=True)
    override = bool(decision.intervention_required and user_decision == "proceed")

    logging_agent.log_behavior(
        behavior_col,
        transaction_id=transaction_id,
        lcpi_score=behavior.lcpi_score,
        decision=user_decision,
        override=override,
        friction_level=friction_level,
        threshold=threshold,
        reason=reason,
    )

    new_threshold = threshold_agent.adapt_threshold(behavior_col, settings_col)
    st.markdown("### Step 7: Adaptive Threshold Update")
    st.metric("Updated Threshold", f"{new_threshold:.2f}")

st.markdown("---")
st.subheader("Behavior History (MongoDB)")

history_docs = list(behavior_col.find({}, {"_id": 0}).sort("timestamp", 1))
if not history_docs:
    st.info("No behavior logs yet. Submit a transaction to populate history.")
else:
    history_df = pd.DataFrame(history_docs)
    history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
    st.dataframe(history_df.tail(50), use_container_width=True)

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(history_df["timestamp"], history_df["lcpi_score"], marker="o", label="LCPI")
    ax.plot(history_df["timestamp"], history_df["threshold"], marker="x", label="Threshold")
    ax.set_title("Risk Trend vs Adaptive Threshold")
    ax.set_ylabel("Score")
    ax.legend()
    st.pyplot(fig)
