import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_DIR = Path(__file__).resolve().parents[1] / "database"
DB_PATH = DB_DIR / "afbr.db"


def init_db() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            remaining_budget REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            risk_score REAL,
            threshold REAL,
            decision TEXT,
            friction_level TEXT,
            user_action TEXT,
            override INTEGER,
            personality TEXT,
            negotiation_message TEXT,
            reason TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(transaction_id) REFERENCES transactions(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    cur.execute(
        "INSERT OR IGNORE INTO settings(key, value) VALUES ('risk_threshold', '0.55')"
    )

    conn.commit()
    conn.close()


@contextmanager
def get_conn():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def get_setting(key: str, default: str) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
