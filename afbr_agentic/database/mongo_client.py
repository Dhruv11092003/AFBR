from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


@dataclass
class MongoStatus:
    mode: str
    message: str


class MongoConnectionManager:
    """Centralized MongoDB connection manager with optional in-memory fallback."""

    def __init__(self) -> None:
        load_dotenv()
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB", "afbr_db")
        self._status = MongoStatus("disconnected", "Not initialized")
        self._client: MongoClient | None = None
        self._db: Database | None = None

    def connect(self) -> MongoStatus:
        if self._db is not None:
            return self._status
        try:
            self._client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self._client.admin.command("ping")
            self._db = self._client[self.db_name]
            self._status = MongoStatus("mongo", f"Connected to {self.db_name}")
        except Exception as exc:
            import mongomock

            self._client = mongomock.MongoClient()
            self._db = self._client[self.db_name]
            self._status = MongoStatus("mongomock", f"MongoDB unavailable, using mongomock fallback: {exc}")

        self._ensure_indexes()
        self._seed_settings()
        return self._status

    def _ensure_indexes(self) -> None:
        if self._db is None:
            return
        self._db.transactions.create_index("timestamp")
        self._db.transactions.create_index([("category", 1), ("timestamp", 1)])
        self._db.behavior_logs.create_index("timestamp")
        self._db.settings.create_index("key", unique=True)

    def _seed_settings(self) -> None:
        if self._db is None:
            return
        initial_threshold = float(os.getenv("AFBR_INITIAL_THRESHOLD", "0.55"))
        self._db.settings.update_one(
            {"key": "risk_threshold"},
            {"$setOnInsert": {"key": "risk_threshold", "value": initial_threshold}},
            upsert=True,
        )

    def db(self) -> Database:
        if self._db is None:
            self.connect()
        if self._db is None:
            raise RuntimeError("MongoDB connection could not be created")
        return self._db

    def collection(self, name: str) -> Collection:
        return self.db()[name]

    @property
    def status(self) -> MongoStatus:
        return self._status


mongo_manager = MongoConnectionManager()
