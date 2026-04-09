class AdaptiveThresholdAgent:
    """Updates risk threshold from logged behavior (closed-loop feedback)."""

    @staticmethod
    def get_current_threshold(settings_collection) -> float:
        doc = settings_collection.find_one({"key": "risk_threshold"})
        if not doc:
            settings_collection.update_one(
                {"key": "risk_threshold"},
                {"$set": {"key": "risk_threshold", "value": 0.55}},
                upsert=True,
            )
            return 0.55
        return float(doc.get("value", 0.55))

    def adapt_threshold(self, behavior_logs_collection, settings_collection) -> float:
        logs = list(behavior_logs_collection.find().sort("timestamp", -1).limit(50))
        if not logs:
            return self.get_current_threshold(settings_collection)

        override_rate = sum(1 for l in logs if l.get("override")) / len(logs)
        defer_rate = sum(1 for l in logs if l.get("decision") == "defer") / len(logs)
        avg_lcpi = sum(float(l.get("lcpi_score", 0.0)) for l in logs) / len(logs)

        current = self.get_current_threshold(settings_collection)
        updated = current

        if override_rate > 0.5:
            updated += 0.03
        elif override_rate < 0.2:
            updated -= 0.02

        if defer_rate > 0.35:
            updated += 0.01
        if avg_lcpi > 0.75:
            updated -= 0.01

        updated = float(min(max(updated, 0.35), 0.85))
        settings_collection.update_one(
            {"key": "risk_threshold"},
            {"$set": {"key": "risk_threshold", "value": updated}},
            upsert=True,
        )
        return updated
