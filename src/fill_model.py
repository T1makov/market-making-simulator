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


def orderbook_fill(bot_bid_price, bot_ask_price, market_bid, market_ask):
    """
    Returns (bot_buys, bot_sells) as booleans for this step.

    bot_buys: the bot's bid crosses or meets the simulated public ask, so the
    bot buys.

    bot_sells: the bot's ask crosses or meets the simulated public bid, so
    the bot sells.

    Unlike fill_probability(), this is a deterministic "would this actually
    trade" crossing check against a simulated public bid/ask market rather
    than a hand-tuned probability curve. It has no randomness of its own.
    """

    bot_buys = bot_bid_price >= market_ask
    bot_sells = bot_ask_price <= market_bid

    return bot_buys, bot_sells