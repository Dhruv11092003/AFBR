from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    transaction_id: int
    risk_score: float
    threshold: float
    decision: str
    friction_level: str
    user_action: str
    override: int
    personality: str
    negotiation_message: str
    reason: str
    timestamp: datetime


class LoggingAgent:
    """Persists outcomes for closed-loop learning and auditability."""

    def log(self, conn, entry: LogEntry) -> None:
        conn.execute(
            """
            INSERT INTO decisions (
                transaction_id, risk_score, threshold, decision, friction_level,
                user_action, override, personality, negotiation_message, reason, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.transaction_id,
                entry.risk_score,
                entry.threshold,
                entry.decision,
                entry.friction_level,
                entry.user_action,
                entry.override,
                entry.personality,
                entry.negotiation_message,
                entry.reason,
                entry.timestamp.isoformat(),
            ),
        )
