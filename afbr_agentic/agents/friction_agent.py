from dataclasses import dataclass


@dataclass
class FrictionPolicy:
    level: str
    instruction: str
    delay_seconds: int
    reason_required: bool


class StrategicFrictionAgent:
    """Applies strategic friction based on risk severity."""

    def apply(self, risk_score: float, threshold: float) -> FrictionPolicy:
        severity = risk_score - threshold

        if severity < 0.15:
            return FrictionPolicy(
                level="Low",
                instruction="Warning: this transaction may reduce your near-term financial flexibility.",
                delay_seconds=0,
                reason_required=False,
            )
        if severity < 0.30:
            return FrictionPolicy(
                level="Medium",
                instruction="Pause for a short delay before confirming. Use this time to review goals.",
                delay_seconds=8,
                reason_required=False,
            )
        return FrictionPolicy(
            level="High",
            instruction="High-risk transaction. You must provide a justification before override.",
            delay_seconds=12,
            reason_required=True,
        )
