from dataclasses import dataclass


@dataclass
class FrictionOutput:
    level: str
    delay_seconds: int
    reason_required: bool
    warning: str
    budget_impact: str


class FrictionAgent:
    """Applies strategic friction while preserving human final control."""

    def apply(self, lcpi_score: float, threshold: float, amount: float, remaining_budget: float) -> FrictionOutput:
        severity = lcpi_score - threshold
        remaining_after = remaining_budget - amount
        budget_impact = f"If approved, projected remaining budget: ${remaining_after:.2f}"

        if severity < 0.10:
            return FrictionOutput(
                level="warning",
                delay_seconds=0,
                reason_required=False,
                warning="Low friction: review this transaction once before proceeding.",
                budget_impact=budget_impact,
            )
        if severity < 0.25:
            return FrictionOutput(
                level="delay",
                delay_seconds=10,
                reason_required=False,
                warning="Medium friction: enforced 10-second pause for reflection.",
                budget_impact=budget_impact,
            )
        return FrictionOutput(
            level="reason",
            delay_seconds=10,
            reason_required=True,
            warning="High friction: pause + reason capture before override/proceed.",
            budget_impact=budget_impact,
        )
