"""
agents/negotiation_agent.py
───────────────────────────
Agent 4 – Negotiation Agent
Generates a personalised negotiation message via Anthropic Claude API,
with a deterministic fallback if the key is absent or the call fails.

Fix: API key is read fresh from env at call time (not only at __init__),
so it works correctly when agents are cached via @st.cache_resource.
"""

import os

from .behavior_agent import BehaviorFeatures

_STYLE_MAP = {
    "Impulsive":     "firm, concise, consequence-focused. Use short punchy sentences.",
    "Risky":         "analytical, risk-aware, cite numbers directly.",
    "Planned":       "supportive and planning-oriented. Acknowledge their discipline.",
    "Goal-Oriented": "motivational and goal-protection-focused. Tie spending to long-term goals.",
}


class NegotiationAgent:
    """
    Generates a negotiation message using the Anthropic API.
    Falls back to a deterministic message if the API key is absent or the call fails.
    """

    def generate(
        self,
        personality: str,
        amount: float,
        category: str,
        features: BehaviorFeatures,
    ) -> str:
        # Read key fresh every call (agents are cached; .env may load after cache)
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        fallback = self._fallback(personality, amount, category, features)

        if not api_key:
            return fallback

        try:
            return self._call_anthropic(api_key, personality, amount, category, features) or fallback
        except Exception:
            return fallback

    def _call_anthropic(
        self,
        api_key: str,
        personality: str,
        amount: float,
        category: str,
        features: BehaviorFeatures,
    ) -> str:
        import anthropic  # lazy import

        style = _STYLE_MAP.get(personality, "balanced and empathetic")
        client = anthropic.Anthropic(api_key=api_key)

        prompt = (
            f"You are a behavioural finance negotiation agent in an Agentic AI spending regulator.\n"
            f"User personality type: {personality}. Communication style: {style}.\n"
            f"Transaction: \u20b9{amount:.2f} in '{category}' category.\n"
            f"LCPI risk score: {features.lcpi_score:.2f}/1.00 | "
            f"Budget used: {features.budget_deviation:.1%} | "
            f"Category ratio today: {features.category_spending_ratio:.1%} | "
            f"Transactions today: {features.transactions_today} | "
            f"Late night: {'Yes' if features.late_night_flag else 'No'}.\n\n"
            "Generate a short negotiation message with exactly 4 bullet points:\n"
            "\u2022 Goal Delay: what financial goal this might delay\n"
            "\u2022 Liquidity Impact: immediate impact on cash flow\n"
            "\u2022 Smarter Alternative: a concrete lower-cost suggestion\n"
            "\u2022 Motivation: a personalised closing nudge\n"
            "Keep the entire message under 120 words. No preamble."
        )

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()

    def _fallback(
        self,
        personality: str,
        amount: float,
        category: str,
        features: BehaviorFeatures,
    ) -> str:
        budget_pct = min(features.budget_deviation * 100, 100)
        return (
            f"\u26a0\ufe0f  **Before you confirm this \u20b9{amount:.2f} {category} transaction:**\n\n"
            f"\u2022 **Goal Delay:** This spend uses {budget_pct:.0f}% of your remaining budget "
            f"and may delay near-term savings goals by days or weeks.\n"
            f"\u2022 **Liquidity Impact:** With {features.transactions_today} transactions already today, "
            f"your liquidity cushion is thinning \u2014 unexpected expenses may become harder to cover.\n"
            f"\u2022 **Smarter Alternative:** Consider deferring by 24 hours or splitting this purchase "
            f"across two budget periods to reduce the impact.\n"
            f"\u2022 **Motivation:** Small pauses compound into big wins. "
            f"{'Your track record shows discipline \u2014 protect it.' if personality == 'Goal-Oriented' else 'You have the power to choose differently right now.'}"
        )
