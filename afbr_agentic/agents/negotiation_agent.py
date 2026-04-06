import os

from openai import OpenAI

from .behavior_agent import BehaviorFeatures


class NegotiationAgent:
    """Generates negotiation prompts using LLM (or deterministic fallback)."""

    STYLE_MAP = {
        "Impulsive": "firm, concise, consequence-focused",
        "Risky": "analytical, risk-aware, direct",
        "Planned": "supportive, planning-oriented",
        "Goal-Oriented": "motivational, goal-protection-focused",
    }

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate(self, personality: str, amount: float, category: str, features: BehaviorFeatures) -> str:
        style = self.STYLE_MAP.get(personality, "balanced")

        fallback_message = (
            f"Before you confirm this ${amount:.2f} {category} transaction: "
            "consider a 24-hour goal delay, review liquidity impact on weekly essentials, "
            "shift part of this spend into a safer category budget, and compare one cheaper alternative."
        )

        if not self.client:
            return fallback_message

        prompt = (
            "You are a negotiation agent in an agentic AI spending regulator. "
            f"User personality: {personality}. Tone: {style}. "
            f"Transaction: ${amount:.2f} in {category}. LCPI risk score: {features.lcpi_score:.2f}. "
            "Create a short negotiation with exactly four bullets covering: goal delay, liquidity impact, "
            "budget redistribution, and alternative suggestion."
        )

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                max_output_tokens=180,
            )
            return response.output_text.strip() or fallback_message
        except Exception:
            return fallback_message
