"""
agents/behavior_agent.py
────────────────────────
Agent 2 – Behavior Analysis Agent
Responsibility: Compute behavioral features and the LCPI risk score.
Reads historical data from MongoDB; outputs BehaviorFeatures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .transaction_agent import TransactionInput
from utils.lcpi_calculator import compute_lcpi


@dataclass
class BehaviorFeatures:
    transactions_today: int
    category_spending_ratio: float
    late_night_flag: int
    spend_velocity: float          # txns per hour
    category_overspending: float   # ratio above 30 % baseline
    budget_deviation: float        # amount / budget (capped at 3)
    lcpi_score: float              # main risk metric [0, 1]


class BehaviorAnalysisAgent:
    """
    Computes behavioral features and the LCPI risk score.

    Receives TransactionInput + MongoDB-derived historical features.
    Applies the official LCPI formula from utils/lcpi_calculator.py.
    """

    def analyze(
        self,
        tx: TransactionInput,
        transactions_today: int,
        category_spending_ratio: float,
    ) -> BehaviorFeatures:
        """
        Derive behavioral features and compute LCPI.

        Parameters
        ----------
        tx                       : Normalised TransactionInput from TransactionAgent.
        transactions_today       : Count of transactions already made today (from MongoDB).
        category_spending_ratio  : Fraction of today's spend in this category (from MongoDB).

        Returns
        -------
        BehaviorFeatures dataclass with lcpi_score in [0, 1].
        """
        # ── Late-night detection ──────────────────────────────────────────────
        hour = tx.timestamp.hour
        late_night_flag = 1 if (hour >= 23 or hour < 5) else 0

        # ── Derived features ──────────────────────────────────────────────────
        spend_velocity = transactions_today / max(hour + 1, 1)
        category_overspending = max(category_spending_ratio - 0.30, 0.0)
        budget_deviation = min(tx.amount / max(tx.remaining_budget, 1e-6), 3.0)

        # ── Core LCPI calculation (delegated to utility) ──────────────────────
        lcpi = compute_lcpi(
            amount=tx.amount,
            remaining_budget=tx.remaining_budget,
            transactions_today=transactions_today,
            category_spending_ratio=category_spending_ratio,
            late_night_flag=late_night_flag,
        )

        return BehaviorFeatures(
            transactions_today=transactions_today,
            category_spending_ratio=category_spending_ratio,
            late_night_flag=late_night_flag,
            spend_velocity=spend_velocity,
            category_overspending=category_overspending,
            budget_deviation=budget_deviation,
            lcpi_score=lcpi,
        )
