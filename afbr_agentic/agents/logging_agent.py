from __future__ import annotations

from datetime import datetime, timezone


class LoggingAgent:
    """Writes transactions and behavioral outcomes into MongoDB collections."""

    def log_transaction(self, transactions_collection, payload: dict) -> str:
        doc = {
            "amount": float(payload["amount"]),
            "category": payload["category"],
            "timestamp": payload["timestamp"],
            "remaining_budget": float(payload["remaining_budget"]),
        }
        result = transactions_collection.insert_one(doc)
        return str(result.inserted_id)

    def log_behavior(
        self,
        behavior_collection,
        transaction_id: str,
        lcpi_score: float,
        decision: str,
        override: bool,
        friction_level: str,
        threshold: float,
        reason: str,
    ) -> str:
        doc = {
            "transaction_id": transaction_id,
            "lcpi_score": float(lcpi_score),
            "decision": decision,
            "override": bool(override),
            "friction_level": friction_level,
            "threshold": float(threshold),
            "reason": reason,
            "timestamp": datetime.now(timezone.utc),
        }
        result = behavior_collection.insert_one(doc)
        return str(result.inserted_id)
