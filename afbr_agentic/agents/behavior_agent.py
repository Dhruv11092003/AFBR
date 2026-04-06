from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .transaction_agent import TransactionInput


@dataclass
class BehaviorFeatures:
    transactions_today: int
    category_spending_ratio: float
    late_night_flag: int
    spend_velocity: float
    category_overspending: float
    budget_deviation: float
    lcpi_score: float


class BehaviorAnalysisAgent:
    """Computes behavioral features and LCPI-like risk score."""

    def analyze(self, tx: TransactionInput, transactions_today: int, category_spending_ratio: float) -> BehaviorFeatures:
        late_night_flag = 1 if tx.timestamp.hour >= 23 or tx.timestamp.hour < 5 else 0

        spend_velocity = transactions_today / max(tx.timestamp.hour + 1, 1)
        category_overspending = max(category_spending_ratio - 0.30, 0.0)
        budget_deviation = min(tx.amount / max(tx.remaining_budget, 1e-6), 3.0)

        lcpi = (
            0.4 * (tx.amount / max(tx.remaining_budget, 1e-6))
            + 0.2 * (transactions_today / 10)
            + 0.2 * category_spending_ratio
            + 0.2 * late_night_flag
        )
        lcpi = min(max(lcpi, 0.0), 1.0)

        return BehaviorFeatures(
            transactions_today=transactions_today,
            category_spending_ratio=category_spending_ratio,
            late_night_flag=late_night_flag,
            spend_velocity=spend_velocity,
            category_overspending=category_overspending,
            budget_deviation=budget_deviation,
            lcpi_score=lcpi,
        )
