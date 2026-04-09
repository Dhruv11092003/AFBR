"""
utils/lcpi_calculator.py
────────────────────────
Standalone LCPI (Liquidity-Calibrated Predictive Index) formula.

LCPI = 0.4*(amount / remaining_budget)
     + 0.2*(transactions_today / 10)
     + 0.2*(category_spending_ratio)
     + 0.2*(late_night_flag)

Clamped to [0.0, 1.0].
"""


def compute_lcpi(
    amount: float,
    remaining_budget: float,
    transactions_today: int,
    category_spending_ratio: float,
    late_night_flag: int,
) -> float:
    """
    Compute LCPI risk score.

    Parameters
    ----------
    amount                  : transaction amount (₹ / $)
    remaining_budget        : user's remaining budget for the period
    transactions_today      : number of transactions made today
    category_spending_ratio : fraction of today's spending in this category (0-1)
    late_night_flag         : 1 if between 23:00–05:00, else 0

    Returns
    -------
    float in [0.0, 1.0]
    """
    budget_ratio = amount / max(remaining_budget, 1e-6)

    lcpi = (
        0.4 * min(budget_ratio, 1.0)         # budget pressure
        + 0.2 * min(transactions_today / 10, 1.0)  # frequency pressure
        + 0.2 * min(category_spending_ratio, 1.0)   # category concentration
        + 0.2 * late_night_flag                     # late-night impulsivity
    )
    return round(min(max(lcpi, 0.0), 1.0), 4)


def lcpi_label(score: float) -> str:
    if score < 0.35:
        return "Low Risk"
    if score < 0.55:
        return "Moderate Risk"
    if score < 0.75:
        return "High Risk"
    return "Critical Risk"


def lcpi_color(score: float) -> str:
    if score < 0.35:
        return "green"
    if score < 0.55:
        return "orange"
    if score < 0.75:
        return "red"
    return "darkred"
