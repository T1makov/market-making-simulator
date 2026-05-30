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

    # If distance is negative, it means our quote is extremely aggressive.
    # For now, we treat that as distance 0 so the probability does not explode.
    distance_from_mid = max(0.0, distance_from_mid)

    probability = base_fill_probability * math.exp(-sensitivity * distance_from_mid)

    # A probability should never be greater than 1.
    probability = min(1.0, probability)

    return probability


def run_simulation(spread, num_steps, strategy, inventory_skew=0.0):
    """
    Runs one market-making simulation.

    spread:
        Difference between our ask and bid.

    num_steps:
        Number of time steps in the simulation.

    strategy:
        Which quoting strategy the bot uses.
        Options:
            "fixed"
            "inventory_aware"

    inventory_skew:
        How strongly the bot adjusts its quotes based on inventory.
        Only used for the inventory-aware strategy.
    """

    initial_price = 100.00
    true_mid_price = initial_price

    cash = 0.0
    inventory = 0

    buy_fills = 0
    sell_fills = 0

    max_abs_inventory = 0
    sum_abs_inventory = 0

    for step in range(num_steps):
        # 1. The market price moves randomly.
        price_change = random.choice([-0.01, 0.01])
        true_mid_price += price_change

        # 2. For now, assume the bot perfectly observes the current midprice.
        observed_mid_price = true_mid_price

        # 3. Choose where the bot wants to center its bid/ask quotes.
        if strategy == "fixed":
            quote_mid_price = observed_mid_price

        elif strategy == "inventory_aware":
            # If inventory is positive, lower quote_mid_price.
            # If inventory is negative, raise quote_mid_price.
            quote_mid_price = observed_mid_price - inventory_skew * inventory

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # 4. Place bid and ask around the quote_mid_price.
        bid_price = quote_mid_price - spread / 2
        ask_price = quote_mid_price + spread / 2

        # 5. Calculate distances from the actual observed midprice.
        bid_distance = observed_mid_price - bid_price
        ask_distance = ask_price - observed_mid_price

        # 6. Convert distances into fill probabilities.
        prob_someone_sells_to_us = fill_probability(bid_distance)
        prob_someone_buys_from_us = fill_probability(ask_distance)

        # 7. Someone sells to us, so we buy at our bid.
        if random.random() < prob_someone_sells_to_us:
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 8. Someone buys from us, so we sell at our ask.
        if random.random() < prob_someone_buys_from_us:
            inventory -= 1
            cash += ask_price
            sell_fills += 1

        # 9. Track inventory risk.
        max_abs_inventory = max(max_abs_inventory, abs(inventory))
        sum_abs_inventory += abs(inventory)

    final_pnl = cash + inventory * true_mid_price
    average_abs_inventory = sum_abs_inventory / num_steps

    return {
        "strategy": strategy,
        "spread": spread,
        "inventory_skew": inventory_skew,
        "final_pnl": final_pnl,
        "final_inventory": inventory,
        "abs_final_inventory": abs(inventory),
        "buy_fills": buy_fills,
        "sell_fills": sell_fills,
        "total_fills": buy_fills + sell_fills,
        "max_abs_inventory": max_abs_inventory,
        "average_abs_inventory": average_abs_inventory,
    }


def average(values):
    """
    Returns the average of a list of numbers.
    """

    return sum(values) / len(values)


def run_experiment():
    """
    Compares fixed quoting against inventory-aware quoting.
    """

    random.seed(42)

    spread = 0.10
    num_steps = 1000
    num_trials = 500

    strategies = [
        ("fixed", 0.0),
        ("inventory_aware", 0.001),
        ("inventory_aware", 0.002),
        ("inventory_aware", 0.005),
    ]

    print("Inventory-Aware Quoting Experiment")
    print("----------------------------------")
    print(f"Spread: {spread}")
    print(f"Number of steps per simulation: {num_steps}")
    print(f"Number of trials per strategy: {num_trials}")
    print()

    for strategy, inventory_skew in strategies:
        results = []

        for trial in range(num_trials):
            result = run_simulation(
                spread=spread,
                num_steps=num_steps,
                strategy=strategy,
                inventory_skew=inventory_skew,
            )
            results.append(result)

        avg_pnl = average([result["final_pnl"] for result in results])
        avg_total_fills = average([result["total_fills"] for result in results])
        avg_abs_final_inventory = average(
            [result["abs_final_inventory"] for result in results]
        )
        avg_max_abs_inventory = average(
            [result["max_abs_inventory"] for result in results]
        )
        avg_abs_inventory = average(
            [result["average_abs_inventory"] for result in results]
        )

        print(f"Strategy: {strategy}")
        print(f"Inventory skew: {inventory_skew}")
        print(f"  Average PnL: {round(avg_pnl, 2)}")
        print(f"  Average total fills: {round(avg_total_fills, 2)}")
        print(f"  Average absolute final inventory: {round(avg_abs_final_inventory, 2)}")
        print(f"  Average max absolute inventory: {round(avg_max_abs_inventory, 2)}")
        print(f"  Average absolute inventory over time: {round(avg_abs_inventory, 2)}")
        print()


if __name__ == "__main__":
    run_experiment()