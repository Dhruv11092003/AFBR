from dataclasses import dataclass


@dataclass
class DecisionOutput:
    intervention_required: bool
    threshold: float
    risk_margin: float


class DecisionAgent:
    """Threshold-based intervention decision agent."""

    def decide(self, lcpi_score: float, threshold: float) -> DecisionOutput:
        return DecisionOutput(
            intervention_required=lcpi_score >= threshold,
            threshold=float(threshold),
            risk_margin=float(lcpi_score - threshold),
        )
