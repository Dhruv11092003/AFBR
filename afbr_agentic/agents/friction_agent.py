"""
agents/friction_agent.py
────────────────────────
Agent 5 – Strategic Friction Agent
Responsibility: Determine the appropriate friction level and policy
based on how far the LCPI exceeds the adaptive threshold.

Friction levels:
  Low    → Warning banner only
  Medium → Warning + 10-second forced delay
  High   → Warning + 10-second delay + mandatory reason input
"""

from dataclasses import dataclass


@dataclass
class FrictionPolicy:
    level: str              # "Low" | "Medium" | "High"
    instruction: str        # Human-readable guidance
    delay_seconds: int      # Forced countdown before user can proceed
    reason_required: bool   # Must user type a reason to override?
    budget_warning: str     # Budget impact message


class StrategicFrictionAgent:
    """
    Applies strategic friction proportional to risk severity.

    The friction agent NEVER blocks a transaction; it introduces
    cognitive pause points that encourage reflective decision-making.
    This implements the 'strategic friction' concept from the AFBR patent.
    """

    def apply(self, risk_score: float, threshold: float, amount: float, remaining_budget: float) -> FrictionPolicy:
        """
        Compute friction policy.

        Parameters
        ----------
        risk_score       : LCPI score [0, 1].
        threshold        : Current adaptive threshold.
        amount           : Transaction amount.
        remaining_budget : User's remaining budget.

        Returns
        -------
        FrictionPolicy dataclass.
        """
        severity = risk_score - threshold
        budget_after = max(remaining_budget - amount, 0)
        pct_used = min((amount / max(remaining_budget, 1e-6)) * 100, 100)
        budget_msg = (
            f"This transaction uses {pct_used:.0f}% of your remaining budget "
            f"(₹{budget_after:.2f} will remain)."
        )

        if severity < 0.15:
            return FrictionPolicy(
                level="Low",
                instruction=(
                    "⚠️  This transaction may reduce your near-term financial flexibility. "
                    "Take a moment to consider your budget goals."
                ),
                delay_seconds=0,
                reason_required=False,
                budget_warning=budget_msg,
            )

        if severity < 0.30:
            return FrictionPolicy(
                level="Medium",
                instruction=(
                    "🛑  Medium-risk transaction detected. A short pause has been applied. "
                    "Use this time to review your financial goals before confirming."
                ),
                delay_seconds=10,
                reason_required=False,
                budget_warning=budget_msg,
            )

        return FrictionPolicy(
            level="High",
            instruction=(
                "🚨  High-risk transaction. This significantly impacts your budget. "
                "You must provide a justification before proceeding."
            ),
            delay_seconds=10,
            reason_required=True,
            budget_warning=budget_msg,
        )
