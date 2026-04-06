from datetime import datetime
import time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from agents.behavior_agent import BehaviorAnalysisAgent
from agents.friction_agent import StrategicFrictionAgent
from agents.logging_agent import LogEntry, LoggingAgent
from agents.negotiation_agent import NegotiationAgent
from agents.personality_agent import PersonalityAgent
from agents.risk_agent import RiskDecisionAgent
from agents.threshold_agent import AdaptiveThresholdAgent
from agents.transaction_agent import TransactionAgent
from utils.db import get_conn, get_setting, init_db, set_setting


st.set_page_config(page_title="Simplified AFBR", layout="wide")
init_db()

transaction_agent = TransactionAgent()
behavior_agent = BehaviorAnalysisAgent()
risk_agent = RiskDecisionAgent()
negotiation_agent = NegotiationAgent()
friction_agent = StrategicFrictionAgent()
personality_agent = PersonalityAgent()
logging_agent = LoggingAgent()
adaptive_agent = AdaptiveThresholdAgent()


def fetch_behavior_context(conn, tx_timestamp: datetime, category: str):
    day_start = tx_timestamp.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    today_count = conn.execute(
        "SELECT COUNT(*) AS c FROM transactions WHERE timestamp >= ?",
        (day_start,),
    ).fetchone()["c"]

    day_total = conn.execute(
        "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE timestamp >= ?",
        (day_start,),
    ).fetchone()["s"]

    category_total = conn.execute(
        "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE timestamp >= ? AND category = ?",
        (day_start, category),
    ).fetchone()["s"]

    category_ratio = float(category_total / day_total) if day_total > 0 else 0.0
    return int(today_count), min(max(category_ratio, 0.0), 1.0)


def fetch_learning_metrics(conn):
    row = conn.execute(
        """
        SELECT
            COALESCE(AVG(risk_score), 0.0) AS avg_risk,
            COALESCE(AVG(CASE WHEN override = 1 THEN 1.0 ELSE 0.0 END), 0.0) AS override_rate,
            COALESCE(AVG(CASE WHEN user_action = 'cancel' THEN 1.0 ELSE 0.0 END), 0.0) AS compliance_rate
        FROM decisions
        """
    ).fetchone()
    return float(row["avg_risk"]), float(row["override_rate"]), float(row["compliance_rate"])


st.title("Agentic AI Financial Decision Regulator (Simplified AFBR)")
st.caption("Multi-agent system for impulsive spending prediction, negotiation, and strategic friction.")

left, right = st.columns([1.2, 1])

with left:
    st.subheader("1) Transaction Input (Transaction Agent)")
    with st.form("tx_form"):
        amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, value=120.0)
        category = st.selectbox("Category", ["food", "shopping", "transport", "entertainment", "health", "other"])
        remaining_budget = st.number_input("Remaining monthly budget ($)", min_value=1.0, step=10.0, value=500.0)
        tx_time = st.time_input("Transaction time", value=datetime.now().time())
        submitted = st.form_submit_button("Run Agentic Workflow")

with right:
    st.subheader("Current Adaptive Threshold")
    current_threshold = float(get_setting("risk_threshold", "0.55"))
    st.metric("Risk threshold", f"{current_threshold:.2f}")

if submitted:
    tx_timestamp = datetime.now().replace(hour=tx_time.hour, minute=tx_time.minute, second=0, microsecond=0)

    tx = transaction_agent.collect(amount, category, remaining_budget, tx_timestamp)

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transactions (amount, category, remaining_budget, timestamp) VALUES (?, ?, ?, ?)",
            (tx.amount, tx.category, tx.remaining_budget, tx.timestamp.isoformat()),
        )
        tx_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

        transactions_today, category_ratio = fetch_behavior_context(conn, tx.timestamp, tx.category)

        behavior = behavior_agent.analyze(
            tx,
            transactions_today=transactions_today,
            category_spending_ratio=category_ratio,
        )

        threshold = float(get_setting("risk_threshold", "0.55"))
        risk_decision = risk_agent.decide(behavior.lcpi_score, threshold)

        avg_risk, override_rate, compliance_rate = fetch_learning_metrics(conn)
        personality = personality_agent.classify(avg_risk, override_rate, compliance_rate)

        st.markdown("---")
        st.subheader("2) Behavior + Risk Output")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("LCPI Risk Score", f"{behavior.lcpi_score:.2f}")
        c2.metric("Transactions Today", behavior.transactions_today)
        c3.metric("Category Ratio", f"{behavior.category_spending_ratio:.2f}")
        c4.metric("Late Night Flag", behavior.late_night_flag)

        st.info(f"Risk Decision Agent: intervention = **{risk_decision.trigger_intervention}** (threshold {threshold:.2f})")

        negotiation_message = "No intervention needed. Transaction can proceed normally."
        friction_level = "None"
        reason_text = ""
        user_action = "approved"
        override = 0

        if risk_decision.trigger_intervention:
            st.subheader("3) Intervention Pipeline")
            st.write(f"**Personality Agent**: {personality.personality_type} — {personality.rationale}")

            negotiation_message = negotiation_agent.generate(
                personality.personality_type, tx.amount, tx.category, behavior
            )
            st.warning("Negotiation Agent Message")
            st.write(negotiation_message)

            friction = friction_agent.apply(behavior.lcpi_score, threshold)
            friction_level = friction.level
            st.error(f"Strategic Friction Level: **{friction.level}**")
            st.write(friction.instruction)

            if friction.delay_seconds > 0:
                with st.spinner(f"Applying delay friction for {friction.delay_seconds} seconds..."):
                    time.sleep(friction.delay_seconds)

            if friction.reason_required:
                reason_text = st.text_area("Required: Why should this transaction proceed?")

            user_choice = st.radio(
                "User Decision (Human-in-the-loop)",
                ["cancel", "override_and_continue"],
                horizontal=True,
            )

            if user_choice == "cancel":
                user_action = "cancel"
                override = 0
                st.success("Great choice. Transaction cancelled.")
            else:
                user_action = "override"
                override = 1
                if friction.reason_required and not reason_text.strip():
                    st.error("High friction requires a reason. Logging placeholder reason for demonstration.")
                    reason_text = "No reason provided"
                st.warning("Transaction overridden and allowed to continue.")

        log_entry = LogEntry(
            transaction_id=tx_id,
            risk_score=behavior.lcpi_score,
            threshold=threshold,
            decision="intervene" if risk_decision.trigger_intervention else "allow",
            friction_level=friction_level,
            user_action=user_action,
            override=override,
            personality=personality.personality_type,
            negotiation_message=negotiation_message,
            reason=reason_text,
            timestamp=datetime.now(),
        )
        logging_agent.log(conn, log_entry)

        avg_risk, override_rate, compliance_rate = fetch_learning_metrics(conn)
        update = adaptive_agent.update(threshold, compliance_rate, override_rate, avg_risk)
        set_setting("risk_threshold", f"{update.new_threshold:.4f}")

        st.subheader("4) Adaptive Threshold Update")
        st.write(
            f"Threshold updated from **{update.old_threshold:.2f}** to **{update.new_threshold:.2f}** "
            f"(compliance={update.compliance_rate:.2f}, override={update.override_rate:.2f})"
        )

st.markdown("---")
st.subheader("Historical Closed-Loop Feedback Dashboard")

with get_conn() as conn:
    history = pd.read_sql_query(
        "SELECT risk_score, threshold, override, user_action, timestamp FROM decisions ORDER BY id ASC",
        conn,
    )

if history.empty:
    st.info("No transactions yet. Submit one to view analytics and feedback loops.")
else:
    history["timestamp"] = pd.to_datetime(history["timestamp"])

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(history["timestamp"], history["risk_score"], marker="o", label="Risk Score")
    ax.plot(history["timestamp"], history["threshold"], marker="x", label="Adaptive Threshold")
    ax.set_title("Risk vs Threshold over Time")
    ax.set_ylabel("Score")
    ax.legend()
    st.pyplot(fig)

    override_pct = 100 * history["override"].mean()
    cancel_pct = 100 * (history["user_action"] == "cancel").mean()

    m1, m2 = st.columns(2)
    m1.metric("Override Rate", f"{override_pct:.1f}%")
    m2.metric("Cancel / Compliance Rate", f"{cancel_pct:.1f}%")

    st.dataframe(history.tail(20), use_container_width=True)
