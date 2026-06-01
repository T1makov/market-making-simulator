import math


def fill_probability(distance_from_true_mid):
    """
    Returns the probability that our quote gets filled.

    The farther our quote is from the true midprice, the less likely someone is
    to trade with us.

    If distance is negative, our quote is aggressive:
        - bid is above true midprice, or
        - ask is below true midprice

    In that case, we treat distance as 0, meaning maximum fill probability.
    """

    base_fill_probability = 0.30
    sensitivity = 20.0

    distance_from_true_mid = max(0.0, distance_from_true_mid)

    probability = base_fill_probability * math.exp(
        -sensitivity * distance_from_true_mid
    )

    probability = min(1.0, probability)

    return probability