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

    bot_buys: the bot's bid is at least as competitive as the simulated
    public bid (bot_bid_price >= market_bid), so it sits at the front of the
    book and receives the next incoming public sell order.

    bot_sells: the bot's ask is at least as competitive as the simulated
    public ask (bot_ask_price <= market_ask), so it receives the next
    incoming public buy order.

    Unlike fill_probability(), this is a deterministic "would this actually
    trade" check against a simulated public bid/ask market rather than a
    hand-tuned probability curve. It has no randomness of its own.

    Note this compares each side of the bot's quote to the *same* side of
    the public quote (bid-to-bid, ask-to-ask), not to the opposite side.
    Since the bot and the public market are both centered near the same
    fair-value price, requiring the bot's bid to reach all the way to the
    public *ask* (or the ask to reach the public *bid*) would mean the bot
    has to quote outside the public spread entirely -- something none of
    this project's market-making strategies do, so it would never fire.
    Comparing same-side-to-same-side instead models a resting limit order
    that gets filled whenever it is priced at or better than the public
    touch, which is what "the bot's quote crosses/meets the market" means
    for a passive maker.
    """

    bot_buys = bot_bid_price >= market_bid
    bot_sells = bot_ask_price <= market_ask

    return bot_buys, bot_sells