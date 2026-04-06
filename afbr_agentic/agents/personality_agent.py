from dataclasses import dataclass


@dataclass
class PersonalityProfile:
    personality_type: str
    rationale: str


class PersonalityAgent:
    """Classifies user behavioral personality for adaptive negotiation tone."""

    def classify(self, avg_risk: float, override_rate: float, savings_focus: float) -> PersonalityProfile:
        if avg_risk > 0.72 and override_rate > 0.45:
            return PersonalityProfile("Impulsive", "Frequent high-risk actions with many overrides.")
        if avg_risk > 0.62 and override_rate > 0.3:
            return PersonalityProfile("Risky", "Repeated acceptance of elevated financial risk.")
        if savings_focus > 0.55 and avg_risk < 0.45:
            return PersonalityProfile("Goal-Oriented", "Mostly aligned with savings and low-risk purchases.")
        return PersonalityProfile("Planned", "Moderate-risk behavior with controlled overrides.")
