"""
agents/transaction_agent.py
────────────────────────────
Agent 1 – Transaction Agent
Responsibility: Receive, validate, and normalise raw transaction input.
Outputs a TransactionInput dataclass consumed by downstream agents.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TransactionInput:
    amount: float
    category: str
    remaining_budget: float
    timestamp: datetime
    transaction_id: str = ""   # populated after MongoDB insert


class TransactionAgent:
    """
    Collects and normalises transaction details.

    This is the ENTRY POINT of the agentic pipeline.
    It sanitises user input and produces a clean TransactionInput
    that all subsequent agents can rely on.
    """

    VALID_CATEGORIES = [
        "food", "entertainment", "shopping", "travel",
        "healthcare", "education", "utilities", "other",
    ]

    def collect(
        self,
        amount: float,
        category: str,
        remaining_budget: float,
        timestamp: datetime | None = None,
    ) -> TransactionInput:
        """
        Validate and normalise a raw transaction.

        Parameters
        ----------
        amount           : Positive transaction amount.
        category         : Spending category string.
        remaining_budget : User's remaining budget.
        timestamp        : Defaults to now() if not provided.

        Returns
        -------
        TransactionInput dataclass.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        amount = max(float(amount), 0.01)
        remaining_budget = max(float(remaining_budget), 0.01)
        category = category.strip().lower()
        if category not in self.VALID_CATEGORIES:
            category = "other"

        return TransactionInput(
            amount=amount,
            category=category,
            remaining_budget=remaining_budget,
            timestamp=timestamp,
        )
