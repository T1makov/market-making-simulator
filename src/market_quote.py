import random


def generate_market_quote(
    true_mid_price,
    base_market_spread,
    volatility_linked_width,
    recent_volatility_estimate,
):
    """
    Returns (market_bid, market_ask) for the current step.

    market_spread = base_market_spread + volatility_linked_width * recent_volatility_estimate
    market_bid = true_mid_price - market_spread / 2
    market_ask = true_mid_price + market_spread / 2

    This is deterministic given its inputs -- it has no randomness of its
    own -- so callers control reproducibility entirely through the values
    they pass in (in particular, through recent_volatility_estimate).
    """

    market_spread = base_market_spread + volatility_linked_width * recent_volatility_estimate

    market_bid = true_mid_price - market_spread / 2
    market_ask = true_mid_price + market_spread / 2

    return market_bid, market_ask


def observed_mid_from_market_quote(market_bid, market_ask):
    """
    Returns a simulated observed mid price drawn uniformly within
    [market_bid, market_ask], representing observation noise that is
    naturally bounded by the public spread rather than unbounded.
    """

    return random.uniform(market_bid, market_ask)
