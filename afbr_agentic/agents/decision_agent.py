"""
agents/decision_agent.py
────────────────────────
Agent 3 – Decision Agent
Responsibility: Compare LCPI against adaptive threshold and emit a
structured RiskDecision that drives downstream intervention routing.
"""

from dataclasses import dataclass


@dataclass
class RiskDecision:
    trigger_intervention: bool   # True → engage negotiation + friction
    threshold: float             # current adaptive threshold
    margin: float                # lcpi - threshold (negative = safe)
    risk_label: str              # Low / Moderate / High / Critical


class DecisionAgent:
    """
    Threshold-based decision agent.

    Compares the LCPI score produced by BehaviorAnalysisAgent
    against the adaptive threshold maintained by AdaptiveThresholdAgent.

    This agent NEVER blocks a transaction — it only signals intervention.
    """

    def decide(self, risk_score: float, threshold: float) -> RiskDecision:
        """
        Emit an intervention decision.

        Parameters
        ----------
        risk_score : LCPI score from BehaviorAnalysisAgent [0, 1].
        threshold  : Current adaptive threshold from AdaptiveThresholdAgent.

        Returns
        -------
        RiskDecision dataclass.
        """
        margin = round(risk_score - threshold, 4)
        trigger = risk_score >= threshold

        if risk_score < 0.35:
            label = "Low"
        elif risk_score < 0.55:
            label = "Moderate"
        elif risk_score < 0.75:
            label = "High"
        else:
            label = "Critical"

        return RiskDecision(
            trigger_intervention=trigger,
            threshold=threshold,
            margin=margin,
            risk_label=label,
        )
