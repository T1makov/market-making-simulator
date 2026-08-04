import math


def average(values):
    """
    Returns the average of a list of numbers.
    """

    if len(values) == 0:
        return 0.0

    return sum(values) / len(values)


def standard_deviation(values):
    """
    Returns the population standard deviation of a list of numbers.
    """

    if len(values) == 0:
        return 0.0

    mean = average(values)
    variance = average([(value - mean) ** 2 for value in values])

    return math.sqrt(variance)


def estimate_uncertainty(recent_observed_price_changes):
    """
    Estimates uncertainty using the standard deviation of recent observed
    price changes.
    """

    if len(recent_observed_price_changes) < 2:
        return 0.0

    return standard_deviation(recent_observed_price_changes)


def summarize_results(results):
    """
    Takes many simulation results and summarizes them.
    """

    pnls = [result["final_pnl"] for result in results]
    risk_adjusted_scores = [result["risk_adjusted_score"] for result in results]

    return {
        "avg_pnl": average(pnls),
        "std_pnl": standard_deviation(pnls),
        "avg_risk_adjusted_score": average(risk_adjusted_scores),
        "avg_total_fills": average([result["total_fills"] for result in results]),
        "avg_abs_final_inventory": average(
            [result["abs_final_inventory"] for result in results]
        ),
        "avg_max_abs_inventory": average(
            [result["max_abs_inventory"] for result in results]
        ),
        "avg_abs_inventory": average(
            [result["average_abs_inventory"] for result in results]
        ),
        "avg_abs_observation_error": average(
            [result["average_abs_observation_error"] for result in results]
        ),
        "avg_effective_spread": average(
            [result["average_effective_spread"] for result in results]
        ),
        "avg_estimated_uncertainty": average(
            [result["average_estimated_uncertainty"] for result in results]
        ),
    }