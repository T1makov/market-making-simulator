import random
import math


def fill_probability(distance_from_mid):
    """
    Returns the probability that our quote gets filled.

    The farther our quote is from the midprice, the less likely someone is
    to trade with us.
    """

    base_fill_probability = 0.30
    sensitivity = 20.0

    probability = base_fill_probability * math.exp(-sensitivity * distance_from_mid)

    return probability


def run_simulation(spread, num_steps):
    """
    Runs one market-making simulation.

    spread:
        Difference between our ask and bid.

        Example:
        if spread = 0.10 and midprice = 100,
        then bid = 99.95 and ask = 100.05.

    num_steps:
        Number of time steps in the simulation.
    """

    initial_price = 100.00
    true_mid_price = initial_price

    cash = 0.0
    inventory = 0

    buy_fills = 0
    sell_fills = 0
    max_abs_inventory = 0

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

        # 5. Convert quote distances into fill probabilities.
        prob_someone_sells_to_us = fill_probability(bid_distance)
        prob_someone_buys_from_us = fill_probability(ask_distance)

        # 6. Someone sells to us, so we buy at our bid.
        if random.random() < prob_someone_sells_to_us:
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 7. Someone buys from us, so we sell at our ask.
        if random.random() < prob_someone_buys_from_us:
            inventory -= 1
            cash += ask_price
            sell_fills += 1

        # 8. Track our largest inventory exposure.
        max_abs_inventory = max(max_abs_inventory, abs(inventory))

    final_pnl = cash + inventory * true_mid_price

    return {
        "spread": spread,
        "final_pnl": final_pnl,
        "final_inventory": inventory,
        "buy_fills": buy_fills,
        "sell_fills": sell_fills,
        "total_fills": buy_fills + sell_fills,
        "max_abs_inventory": max_abs_inventory,
    }


def average(values):
    """
    Returns the average of a list of numbers.
    """

    return sum(values) / len(values)


def run_experiment():
    """
    Runs many simulations for different spreads and compares them.
    """

    random.seed(42)

    spreads = [0.02, 0.05, 0.10, 0.20, 0.50]
    num_steps = 1000
    num_trials = 200

    print("Spread Experiment")
    print("-----------------")
    print(f"Number of steps per simulation: {num_steps}")
    print(f"Number of trials per spread: {num_trials}")
    print()

    for spread in spreads:
        results = []

        for trial in range(num_trials):
            result = run_simulation(spread=spread, num_steps=num_steps)
            results.append(result)

        avg_pnl = average([result["final_pnl"] for result in results])
        avg_total_fills = average([result["total_fills"] for result in results])
        avg_final_inventory = average([result["final_inventory"] for result in results])
        avg_max_abs_inventory = average([result["max_abs_inventory"] for result in results])

        print(f"Spread: {spread}")
        print(f"  Average PnL: {round(avg_pnl, 2)}")
        print(f"  Average total fills: {round(avg_total_fills, 2)}")
        print(f"  Average final inventory: {round(avg_final_inventory, 2)}")
        print(f"  Average max absolute inventory: {round(avg_max_abs_inventory, 2)}")
        print()


if __name__ == "__main__":
    run_experiment()