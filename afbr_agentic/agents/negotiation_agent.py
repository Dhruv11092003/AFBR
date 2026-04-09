import os

from openai import OpenAI


class NegotiationAgent:
    """Generates negotiation prompts before confirmation using LLM/fallback."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def generate_message(self, category: str, amount: float, remaining_budget: float, lcpi_score: float) -> str:
        fallback = (
            f"This ${amount:.2f} {category} purchase has risk score {lcpi_score:.2f}. "
            "Try a 24-hour delay, check liquidity impact on upcoming essentials, "
            "and consider a lower-cost alternative before final confirmation."
        )
        if self.client is None:
            return fallback

        prompt = (
            "You are AFBR's Negotiation Agent. Give concise, human-centered pre-confirmation guidance. "
            "Return 3 bullet points only: (1) goal delay idea, (2) liquidity impact note, (3) practical alternative. "
            f"Transaction category={category}, amount={amount:.2f}, remaining_budget={remaining_budget:.2f}, lcpi={lcpi_score:.2f}."
        )
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=160,
            )
            return (response.output_text or fallback).strip()
        except Exception:
            return fallback
