import random
import math


def fill_probability(distance_from_true_mid):
    """
    Returns the probability that our quote gets filled.

    The farther our quote is from the true midprice, the less likely someone is
    to trade with us.

    If the distance is negative, our quote is extremely aggressive.
    For example, selling below true value or buying above true value.
    We treat that as distance 0, meaning maximum fill probability.
    """

    base_fill_probability = 0.30
    sensitivity = 20.0

    distance_from_true_mid = max(0.0, distance_from_true_mid)

    probability = base_fill_probability * math.exp(
        -sensitivity * distance_from_true_mid
    )

    probability = min(1.0, probability)

    return probability


def run_simulation(
    spread,
    num_steps,
    strategy,
    inventory_skew=0.0,
    observation_noise_std=0.03,
):
    """
    Runs one market-making simulation.

    spread:
        Difference between ask and bid.

    num_steps:
        Number of time steps in the simulation.

    strategy:
        Either "fixed" or "inventory_aware".

    inventory_skew:
        How strongly inventory-aware quoting adjusts prices.

    observation_noise_std:
        Standard deviation of the bot's observation error.

        Bigger value = bot has a less accurate estimate of the true midprice.
    """

    initial_price = 100.00
    true_mid_price = initial_price

    cash = 0.0
    inventory = 0

    buy_fills = 0
    sell_fills = 0

    max_abs_inventory = 0
    sum_abs_inventory = 0
    sum_abs_observation_error = 0

    for step in range(num_steps):
        # 1. The true market price moves randomly.
        price_change = random.choice([-0.01, 0.01])
        true_mid_price += price_change

        # 2. The bot does NOT perfectly observe the true price anymore.
        observation_noise = random.gauss(0.0, observation_noise_std)
        observed_mid_price = true_mid_price + observation_noise

        sum_abs_observation_error += abs(observation_noise)

        # 3. Choose the center of our bid/ask quotes.
        if strategy == "fixed":
            quote_mid_price = observed_mid_price

        elif strategy == "inventory_aware":
            quote_mid_price = observed_mid_price - inventory_skew * inventory

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # 4. Place bid and ask around our chosen quote midpoint.
        bid_price = quote_mid_price - spread / 2
        ask_price = quote_mid_price + spread / 2

        # 5. IMPORTANT:
        # Fill probability is based on distance from the TRUE midprice,
        # not the observed midprice.
        #
        # If our bid is close to true_mid_price, sellers are more likely
        # to sell to us.
        #
        # If our ask is close to true_mid_price, buyers are more likely
        # to buy from us.
        bid_distance = true_mid_price - bid_price
        ask_distance = ask_price - true_mid_price

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

        # 8. Track inventory risk.
        max_abs_inventory = max(max_abs_inventory, abs(inventory))
        sum_abs_inventory += abs(inventory)

    final_pnl = cash + inventory * true_mid_price
    average_abs_inventory = sum_abs_inventory / num_steps
    average_abs_observation_error = sum_abs_observation_error / num_steps

    risk_penalty = 2.0
    risk_adjusted_score = final_pnl - risk_penalty * average_abs_inventory

    return {
        "strategy": strategy,
        "spread": spread,
        "inventory_skew": inventory_skew,
        "observation_noise_std": observation_noise_std,
        "final_pnl": final_pnl,
        "risk_adjusted_score": risk_adjusted_score,
        "final_inventory": inventory,
        "abs_final_inventory": abs(inventory),
        "buy_fills": buy_fills,
        "sell_fills": sell_fills,
        "total_fills": buy_fills + sell_fills,
        "max_abs_inventory": max_abs_inventory,
        "average_abs_inventory": average_abs_inventory,
        "average_abs_observation_error": average_abs_observation_error,
    }


def average(values):
    """
    Returns the average of a list of numbers.
    """

    return sum(values) / len(values)


def run_experiment():
    """
    Compares fixed quoting and inventory-aware quoting when the bot observes
    the midprice with noise.
    """

    random.seed(42)

    spread = 0.10
    num_steps = 1000
    num_trials = 500
    observation_noise_std = 0.03

    strategies = [
        ("fixed", 0.0),
        ("inventory_aware", 0.001),
        ("inventory_aware", 0.002),
        ("inventory_aware", 0.005),
    ]

    print("Noisy Observation Market-Making Experiment")
    print("------------------------------------------")
    print(f"Spread: {spread}")
    print(f"Observation noise std: {observation_noise_std}")
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
                observation_noise_std=observation_noise_std,
            )
            results.append(result)

        avg_pnl = average([result["final_pnl"] for result in results])
        avg_risk_adjusted_score = average(
            [result["risk_adjusted_score"] for result in results]
        )
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
        avg_abs_observation_error = average(
            [result["average_abs_observation_error"] for result in results]
        )

        print(f"Strategy: {strategy}")
        print(f"Inventory skew: {inventory_skew}")
        print(f"  Average PnL: {round(avg_pnl, 2)}")
        print(f"  Average risk-adjusted score: {round(avg_risk_adjusted_score, 2)}")
        print(f"  Average total fills: {round(avg_total_fills, 2)}")
        print(f"  Average absolute final inventory: {round(avg_abs_final_inventory, 2)}")
        print(f"  Average max absolute inventory: {round(avg_max_abs_inventory, 2)}")
        print(f"  Average absolute inventory over time: {round(avg_abs_inventory, 2)}")
        print(f"  Average absolute observation error: {round(avg_abs_observation_error, 4)}")
        print()


if __name__ == "__main__":
    run_experiment()