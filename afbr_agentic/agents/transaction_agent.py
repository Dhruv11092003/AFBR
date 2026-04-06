from dataclasses import dataclass
from datetime import datetime


@dataclass
class TransactionInput:
    amount: float
    category: str
    remaining_budget: float
    timestamp: datetime


class TransactionAgent:
    """Collects and normalizes transaction details."""

    def collect(self, amount: float, category: str, remaining_budget: float, timestamp: datetime) -> TransactionInput:
        return TransactionInput(
            amount=max(amount, 0.0),
            category=category.strip().lower(),
            remaining_budget=max(remaining_budget, 1e-6),
            timestamp=timestamp,
        )
