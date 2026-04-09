from dataclasses import dataclass


@dataclass
class RiskDecision:
    trigger_intervention: bool
    threshold: float
    margin: float


class RiskDecisionAgent:
    """Decides intervention based on adaptive threshold."""

    def decide(self, risk_score: float, threshold: float) -> RiskDecision:
        margin = risk_score - threshold
        return RiskDecision(
            trigger_intervention=risk_score >= threshold,
            threshold=threshold,
            margin=margin,
        )
