"""
agents/logging_agent.py
───────────────────────
Agent 6 – Logging Agent
Responsibility: Persist all behavioral outcomes to MongoDB.
This data feeds the closed-loop feedback system via AdaptiveThresholdAgent.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    transaction_id: str
    risk_score: float
    threshold: float
    decision: str           # "proceed" | "modify" | "defer"
    friction_level: str     # "None" | "Low" | "Medium" | "High"
    user_action: str        # final action taken
    override: bool          # True if user overrode a high-risk flag
    personality: str        # user personality label
    negotiation_message: str
    reason: str             # user-provided reason (for high friction)
    timestamp: datetime


class LoggingAgent:
    """
    Persists transaction outcomes to MongoDB behavior_logs collection.

    The log entries form the closed-loop dataset consumed by
    AdaptiveThresholdAgent to dynamically adjust intervention thresholds.
    """

    def log(self, entry: LogEntry) -> bool:
        """
        Write a LogEntry to MongoDB.

        Parameters
        ----------
        entry : Fully populated LogEntry dataclass.

        Returns
        -------
        True on success, False on error.
        """
        try:
            from database.mongo_client import insert_behavior_log

            insert_behavior_log(
                lcpi_score=entry.risk_score,
                decision=entry.decision,
                override=entry.override,
                friction_level=entry.friction_level,
                timestamp=entry.timestamp,
                transaction_id=entry.transaction_id,
                reason=entry.reason,
                personality=entry.personality,
                threshold=entry.threshold,
            )
            return True
        except Exception as exc:
            print(f"[LoggingAgent] Failed to write log: {exc}")
            return False
