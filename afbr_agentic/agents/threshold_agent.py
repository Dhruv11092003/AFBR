"""
agents/threshold_agent.py
─────────────────────────
Agent 7 – Adaptive Threshold Agent
Responsibility: Adjust the intervention threshold dynamically based on
closed-loop behavioral feedback from MongoDB behavior_logs.

This closes the feedback loop:
  User behavior → LoggingAgent → MongoDB
  → AdaptiveThresholdAgent reads stats → updates threshold
  → DecisionAgent uses updated threshold next time
"""

from dataclasses import dataclass


@dataclass
class ThresholdUpdate:
    old_threshold: float
    new_threshold: float
    compliance_rate: float
    override_rate: float
    avg_risk: float
    adjustment_applied: float


_DEFAULT_THRESHOLD = 0.55
_MIN_THRESHOLD = 0.35
_MAX_THRESHOLD = 0.85


class AdaptiveThresholdAgent:
    """
    Dynamically adjusts the LCPI intervention threshold.

    Logic
    -----
    - High override rate  → raise threshold (user resists intervention; avoid fatigue)
    - Low override rate   → lower threshold (user compliant; catch more risky tx)
    - High compliance     → raise slightly  (reward good behaviour)
    - Low compliance      → lower slightly  (increase vigilance)
    - High avg risk       → lower slightly  (user is genuinely high-risk)
    """

    def update(
        self,
        old_threshold: float,
        compliance_rate: float,
        override_rate: float,
        avg_risk: float,
    ) -> ThresholdUpdate:
        """
        Compute the new threshold.

        Parameters
        ----------
        old_threshold   : Previous threshold value.
        compliance_rate : Fraction of interventions that were NOT overridden.
        override_rate   : Fraction of interventions that were overridden.
        avg_risk        : Mean LCPI score across all logged transactions.

        Returns
        -------
        ThresholdUpdate dataclass.
        """
        adjustment = 0.0

        # Override behaviour
        if override_rate > 0.45:
            adjustment += 0.03   # user ignores warnings → reduce alert fatigue
        elif override_rate < 0.20:
            adjustment -= 0.02   # user rarely overrides → can afford stricter threshold

        # Compliance behaviour
        if compliance_rate > 0.75:
            adjustment += 0.015  # strong compliance → reward with slightly easier threshold
        elif compliance_rate < 0.45:
            adjustment -= 0.015  # poor compliance → tighten threshold

        # Absolute risk level
        if avg_risk > 0.70:
            adjustment -= 0.01   # user is genuinely high-risk → be more proactive

        new_threshold = round(
            min(max(old_threshold + adjustment, _MIN_THRESHOLD), _MAX_THRESHOLD),
            4,
        )

        return ThresholdUpdate(
            old_threshold=old_threshold,
            new_threshold=new_threshold,
            compliance_rate=compliance_rate,
            override_rate=override_rate,
            avg_risk=avg_risk,
            adjustment_applied=round(adjustment, 4),
        )

    def get_current_threshold(self, default: float = _DEFAULT_THRESHOLD) -> float:
        """
        Read the latest adaptive threshold from MongoDB behavior_logs.
        Falls back to `default` if no logs exist.
        """
        try:
            from database.mongo_client import get_adaptive_stats, get_behavior_logs_collection
            col = get_behavior_logs_collection()
            # Use the most recently stored threshold as the base
            last = col.find_one({}, {"threshold": 1}, sort=[("timestamp", -1)])
            base = last["threshold"] if last and "threshold" in last else default

            stats = get_adaptive_stats()
            update = self.update(
                old_threshold=base,
                compliance_rate=stats["compliance_rate"],
                override_rate=stats["override_rate"],
                avg_risk=stats["avg_risk"],
            )
            return update.new_threshold
        except Exception:
            return default
