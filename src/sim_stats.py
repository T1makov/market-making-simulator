import math


def average(values):
    """
    Returns the average of a list of numbers.
    """

    return sum(values) / len(values)


def standard_deviation(values):
    """
    Returns the standard deviation of a list of numbers.
    """

    if len(values) == 0:
        return 0.0

    mean = average(values)
    variance = average([(value - mean) ** 2 for value in values])
    return math.sqrt(variance)


def estimate_uncertainty(recent_observed_price_changes):
    """
    Estimates market uncertainty using recent observed price changes.

    The bot does NOT know the true observation noise.

    Instead, it looks at how much the observed price has been moving recently.

    If observed prices are stable:
        estimated uncertainty is low.

    If observed prices are jumping around:
        estimated uncertainty is high.
    """

    if len(recent_observed_price_changes) < 2:
        return 0.0

    return standard_deviation(recent_observed_price_changes)