from dataclasses import dataclass


@dataclass
class ThresholdUpdate:
    old_threshold: float
    new_threshold: float
    compliance_rate: float
    override_rate: float


class AdaptiveThresholdAgent:
    """Adjusts threshold from compliance/override behavior."""

    def update(self, old_threshold: float, compliance_rate: float, override_rate: float, avg_risk: float) -> ThresholdUpdate:
        adjustment = 0.0

        if override_rate > 0.45:
            adjustment += 0.03
        elif override_rate < 0.20:
            adjustment -= 0.02

        if compliance_rate > 0.75:
            adjustment += 0.015
        elif compliance_rate < 0.45:
            adjustment -= 0.015

        if avg_risk > 0.70:
            adjustment -= 0.01

        new_threshold = min(max(old_threshold + adjustment, 0.35), 0.85)
        return ThresholdUpdate(
            old_threshold=old_threshold,
            new_threshold=new_threshold,
            compliance_rate=compliance_rate,
            override_rate=override_rate,
        )
