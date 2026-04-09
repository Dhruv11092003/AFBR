from dataclasses import dataclass
from datetime import datetime


@dataclass
class TransactionPayload:
    amount: float
    category: str
    remaining_budget: float
    timestamp: datetime


class TransactionAgent:
    """Collects transaction details and normalizes values for downstream agents."""

    def collect(self, amount: float, category: str, remaining_budget: float, timestamp: datetime) -> TransactionPayload:
        return TransactionPayload(
            amount=max(0.0, float(amount)),
            category=category.strip().lower(),
            remaining_budget=max(1.0, float(remaining_budget)),
            timestamp=timestamp,
        )
