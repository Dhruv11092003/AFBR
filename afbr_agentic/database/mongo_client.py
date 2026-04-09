"""
database/mongo_client.py
────────────────────────
Provides a singleton MongoDB client for afbr_db.

Fixes applied (v2):
  - Suppress CryptographyDeprecationWarning from pymongo/pyopenssl
  - get_transactions_today: now returns (count, category_ratio, total_spent_today)
    so the UI can show a REAL remaining budget (original - spent)
  - get_recent_logs: converts timezone-aware datetimes to plain strings BEFORE
    returning, so pandas never raises a mixed-timezone error
  - All datetimes stored as UTC-aware for consistent $gte queries
"""

import os
import warnings

# ── Suppress the pyopenssl CryptographyDeprecationWarning ───────────────────
warnings.filterwarnings("ignore", message=".*serial number.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymongo")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")

from datetime import datetime, timezone
from typing import Optional, Tuple, List

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

load_dotenv()

_client: Optional[MongoClient] = None
_db = None


def _reset_client():
    global _client, _db
    _client = None
    _db = None


def get_db():
    """Return the afbr_db database object (lazy singleton)."""
    global _client, _db
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB", "afbr_db")
        try:
            _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            _client.admin.command("ping")
            _db = _client[db_name]
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            _reset_client()
            raise RuntimeError(
                "Cannot connect to MongoDB. "
                "Check MONGO_URI and MONGO_DB in your .env file."
            ) from exc
    return _db


def get_transactions_collection():
    return get_db()["transactions"]


def get_behavior_logs_collection():
    return get_db()["behavior_logs"]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def insert_transaction(
    amount: float,
    category: str,
    remaining_budget: float,
    timestamp: datetime,
) -> str:
    """Insert a transaction document and return its inserted id as string."""
    col = get_transactions_collection()
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    result = col.insert_one({
        "amount": amount,
        "category": category,
        "timestamp": timestamp,
        "remaining_budget": remaining_budget,
    })
    return str(result.inserted_id)


def insert_behavior_log(
    lcpi_score: float,
    decision: str,
    override: bool,
    friction_level: str,
    timestamp: datetime,
    transaction_id: str = "",
    reason: str = "",
    personality: str = "",
    threshold: float = 0.55,
) -> None:
    col = get_behavior_logs_collection()
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    col.insert_one({
        "transaction_id": transaction_id,
        "lcpi_score": lcpi_score,
        "decision": decision,
        "override": override,
        "friction_level": friction_level,
        "reason": reason,
        "personality": personality,
        "threshold": threshold,
        "timestamp": timestamp,
    })


def get_recent_logs(limit: int = 30) -> List[dict]:
    """
    Return recent behavior logs as plain dicts.

    FIX: Convert all datetime fields to ISO strings before returning so
    pandas never raises mixed-timezone errors in the history table.
    """
    col = get_behavior_logs_collection()
    rows = list(col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    for row in rows:
        for key, val in row.items():
            if isinstance(val, datetime):
                row[key] = val.strftime("%Y-%m-%d %H:%M UTC")
    return rows


def get_transactions_today(
    category: str,
    today_start: datetime,
) -> Tuple[int, float, float]:
    """
    Return (count_all_today, category_ratio, total_spent_today).

    BUG FIX: Previously only returned 2 values and never surfaced
    total_spent_today, so the UI always showed the original remaining_budget
    without subtracting previous transactions. Now returns 3 values:
      [0] total transaction count today
      [1] fraction of today's spend that is in `category`
      [2] total amount spent today across ALL categories
    The caller subtracts [2] from the user-entered remaining_budget to
    compute the REAL current remaining budget.
    """
    col = get_transactions_collection()
    if today_start.tzinfo is None:
        today_start = today_start.replace(tzinfo=timezone.utc)

    all_today = list(col.find({"timestamp": {"$gte": today_start}}))
    total_count = len(all_today)
    total_spent = sum(t.get("amount", 0.0) for t in all_today)
    cat_spent = sum(
        t.get("amount", 0.0) for t in all_today if t.get("category") == category
    )
    ratio = cat_spent / max(total_spent, 1e-6)
    return total_count, ratio, total_spent


def get_adaptive_stats() -> dict:
    col = get_behavior_logs_collection()
    logs = list(
        col.find({}, {"_id": 0, "override": 1, "decision": 1, "lcpi_score": 1})
    )
    if not logs:
        return {"override_rate": 0.0, "compliance_rate": 0.5, "avg_risk": 0.5}
    total = len(logs)
    overrides = sum(1 for lg in logs if lg.get("override"))
    compliances = sum(
        1 for lg in logs
        if not lg.get("override") and lg.get("decision") != "proceed_high_risk"
    )
    avg_risk = sum(lg.get("lcpi_score", 0) for lg in logs) / total
    return {
        "override_rate": overrides / total,
        "compliance_rate": compliances / total,
        "avg_risk": avg_risk,
    }
