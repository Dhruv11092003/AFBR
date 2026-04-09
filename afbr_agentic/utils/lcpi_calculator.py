def calculate_lcpi(
    amount: float,
    remaining_budget: float,
    transactions_today: int,
    category_spending_ratio: float,
    late_night_flag: int,
) -> float:
    """Rule-based LCPI score as specified by project formula."""
    remaining_budget = max(remaining_budget, 1e-6)
    lcpi = (
        0.4 * (amount / remaining_budget)
        + 0.2 * (transactions_today / 10)
        + 0.2 * category_spending_ratio
        + 0.2 * late_night_flag
    )
    return float(min(max(lcpi, 0.0), 1.0))
