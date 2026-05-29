import random
import math


def fill_probability(distance_from_mid):
    """
    Returns the probability that our quote gets filled.

    The farther our quote is from the midprice, the less likely someone is
    to trade with us.

    Example:
    - If our ask is very close to the midprice, buyers are more likely to buy.
    - If our ask is very far above the midprice, buyers are less likely to buy.
    """

    base_fill_probability = 0.30
    sensitivity = 20.0

    probability = base_fill_probability * math.exp(-sensitivity * distance_from_mid)

    return probability


def run_simulation():
    # The market starts at this price.
    initial_price = 100.00

    # This is the market's actual current reference price.
    true_mid_price = initial_price

    # Our bot's state.
    cash = 0.0
    inventory = 0

    # Strategy settings.
    spread = 0.1
    num_steps = 1000

    # Useful statistics.
    buy_fills = 0    # number of times someone sold to us, so we bought
    sell_fills = 0   # number of times someone bought from us, so we sold

    for step in range(num_steps):
        # 1. The market price moves randomly.
        price_change = random.choice([-0.01, 0.01])
        true_mid_price += price_change

        # 2. For now, assume our bot perfectly observes the current market price.
        observed_mid_price = true_mid_price

        # 3. Our bot places quotes around the observed price.
        bid_price = observed_mid_price - spread / 2
        ask_price = observed_mid_price + spread / 2

        # 4. Calculate how far our quotes are from the midprice.
        bid_distance = observed_mid_price - bid_price
        ask_distance = ask_price - observed_mid_price

        # 5. Convert those distances into fill probabilities.
        prob_someone_sells_to_us = fill_probability(bid_distance)
        prob_someone_buys_from_us = fill_probability(ask_distance)

        # 6. Check whether someone sells to us.
        if random.random() < prob_someone_sells_to_us:
            # Someone sells to us, so we buy from them at our bid.
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 7. Check whether someone buys from us.
        if random.random() < prob_someone_buys_from_us:
            # Someone buys from us, so we sell to them at our ask.
            inventory -= 1
            cash += ask_price
            sell_fills += 1

    # Final PnL = cash + value of our remaining inventory.
    final_pnl = cash + inventory * true_mid_price

    print("Initial price:", round(initial_price, 2))
    print("Final true mid price:", round(true_mid_price, 2))
    print("Final cash:", round(cash, 2))
    print("Final inventory:", inventory)
    print("Buy fills:", buy_fills)
    print("Sell fills:", sell_fills)
    print("Total fills:", buy_fills + sell_fills)
    print("Final PnL:", round(final_pnl, 2))


if __name__ == "__main__":
    run_simulation()