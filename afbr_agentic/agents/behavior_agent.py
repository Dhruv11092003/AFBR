from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .transaction_agent import TransactionPayload
from afbr_agentic.utils.lcpi_calculator import calculate_lcpi


@dataclass
class BehaviorOutput:
    transactions_today: int
    category_spending_ratio: float
    late_night_flag: int
    spend_velocity: float
    budget_deviation: float
    lcpi_score: float


class BehaviorAnalysisAgent:
    """Builds behavioral features from MongoDB transaction history and computes LCPI."""

    def analyze(self, tx: TransactionPayload, transactions_collection) -> BehaviorOutput:
        ts_utc = tx.timestamp.astimezone(timezone.utc)
        day_start = datetime(ts_utc.year, ts_utc.month, ts_utc.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        today_cursor = transactions_collection.find(
            {"timestamp": {"$gte": day_start, "$lt": day_end}}
        )
        today_transactions = list(today_cursor)
        transactions_today = len(today_transactions)

        total_today = sum(float(t.get("amount", 0.0)) for t in today_transactions)
        category_total = sum(
            float(t.get("amount", 0.0))
            for t in today_transactions
            if t.get("category", "").lower() == tx.category
        )

        category_ratio = (category_total / total_today) if total_today > 0 else 0.0
        late_night_flag = 1 if tx.timestamp.hour >= 23 or tx.timestamp.hour < 5 else 0

        spend_velocity = transactions_today / max(tx.timestamp.hour + 1, 1)
        budget_deviation = tx.amount / max(tx.remaining_budget, 1.0)
        lcpi_score = calculate_lcpi(
            amount=tx.amount,
            remaining_budget=tx.remaining_budget,
            transactions_today=transactions_today,
            category_spending_ratio=category_ratio,
            late_night_flag=late_night_flag,
        )

        return BehaviorOutput(
            transactions_today=transactions_today,
            category_spending_ratio=float(min(max(category_ratio, 0.0), 1.0)),
            late_night_flag=late_night_flag,
            spend_velocity=float(spend_velocity),
            budget_deviation=float(budget_deviation),
            lcpi_score=lcpi_score,
        )
