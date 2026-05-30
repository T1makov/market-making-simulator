import random
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


def choose_quote_mid_price(strategy, observed_mid_price, inventory, inventory_skew):
    """
    Chooses the center point around which the bot places its bid and ask.

    Fixed strategy:
        Quote around the observed midprice.

    Inventory-aware strategy:
        Shift quotes depending on inventory.

        If inventory > 0:
            We are long.
            Shift quotes down to encourage selling and discourage buying.

        If inventory < 0:
            We are short.
            Shift quotes up to encourage buying and discourage selling.
    """

    if strategy == "fixed":
        return observed_mid_price

    if strategy == "inventory_aware":
        return observed_mid_price - inventory_skew * inventory

    raise ValueError(f"Unknown strategy: {strategy}")


def run_simulation(
    spread,
    num_steps,
    strategy,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
):
    """
    Runs one simulation of the market-making bot.

    spread:
        Difference between ask and bid.

    num_steps:
        Number of time steps in the simulation.

    strategy:
        "fixed" or "inventory_aware"

    inventory_skew:
        How strongly the inventory-aware strategy adjusts quotes.

    observation_noise_std:
        Standard deviation of the bot's observation error.

        If this is 0, the bot perfectly observes the true midprice.
        If this is larger, the bot has a noisier estimate.

    risk_penalty:
        How much we penalize average inventory exposure in the risk-adjusted score.
    """

    initial_price = 100.00
    true_mid_price = initial_price

    cash = 0.0
    inventory = 0

    buy_fills = 0
    sell_fills = 0

    max_abs_inventory = 0
    sum_abs_inventory = 0.0
    sum_abs_observation_error = 0.0

    for step in range(num_steps):
        # 1. The true market price moves randomly.
        price_change = random.choice([-0.01, 0.01])
        true_mid_price += price_change

        # 2. The bot observes the true price with noise.
        observation_noise = random.gauss(0.0, observation_noise_std)
        observed_mid_price = true_mid_price + observation_noise

        sum_abs_observation_error += abs(observation_noise)

        # 3. The bot chooses the center of its bid/ask quotes.
        quote_mid_price = choose_quote_mid_price(
            strategy=strategy,
            observed_mid_price=observed_mid_price,
            inventory=inventory,
            inventory_skew=inventory_skew,
        )

        # 4. The bot places bid and ask around its chosen quote midpoint.
        bid_price = quote_mid_price - spread / 2
        ask_price = quote_mid_price + spread / 2

        # 5. Fills depend on the TRUE midprice, not the bot's observed price.
        #
        # This is important:
        # If the bot has a bad estimate, it may quote bad prices.
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

    risk_adjusted_score = final_pnl - risk_penalty * average_abs_inventory

    return {
        "strategy": strategy,
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


def standard_deviation(values):
    """
    Returns the standard deviation of a list of numbers.

    This helps us measure how unstable the PnL is across trials.
    """

    mean = average(values)
    variance = average([(value - mean) ** 2 for value in values])
    return math.sqrt(variance)


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
    }


def run_trials_for_strategy(
    spread,
    num_steps,
    num_trials,
    strategy,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
):
    """
    Runs many simulations for one strategy under one noise level.
    """

    results = []

    for trial in range(num_trials):
        result = run_simulation(
            spread=spread,
            num_steps=num_steps,
            strategy=strategy,
            inventory_skew=inventory_skew,
            observation_noise_std=observation_noise_std,
            risk_penalty=risk_penalty,
        )
        results.append(result)

    return summarize_results(results)


def print_summary_row(noise_std, strategy_name, inventory_skew, summary):
    """
    Prints one row of the experiment table.
    """

    print(
        f"{noise_std:<8}"
        f"{strategy_name:<22}"
        f"{inventory_skew:<10}"
        f"{summary['avg_pnl']:<12.2f}"
        f"{summary['std_pnl']:<12.2f}"
        f"{summary['avg_risk_adjusted_score']:<16.2f}"
        f"{summary['avg_abs_inventory']:<14.2f}"
        f"{summary['avg_max_abs_inventory']:<14.2f}"
        f"{summary['avg_total_fills']:<12.2f}"
    )


def run_noise_experiment():
    """
    Main experiment:

    For each observation-noise level, compare:
        - fixed quoting
        - inventory-aware quoting with different inventory skew values

    We compare:
        - average PnL
        - PnL standard deviation
        - risk-adjusted score
        - average inventory exposure
        - max inventory exposure
        - total fills
    """

    random.seed(42)

    spread = 0.10
    num_steps = 1000
    num_trials = 500
    risk_penalty = 2.0

    noise_levels = [0.00, 0.01, 0.03, 0.05, 0.10, 0.20]

    strategies = [
        ("fixed", 0.0),
        ("inventory_aware", 0.001),
        ("inventory_aware", 0.002),
        ("inventory_aware", 0.005),
        ("inventory_aware", 0.010),
    ]

    print("Noisy Observation Market-Making Experiment")
    print("------------------------------------------")
    print(f"Spread: {spread}")
    print(f"Steps per simulation: {num_steps}")
    print(f"Trials per strategy/noise level: {num_trials}")
    print(f"Risk penalty: {risk_penalty}")
    print()

    print(
        f"{'Noise':<8}"
        f"{'Strategy':<22}"
        f"{'Skew':<10}"
        f"{'Avg PnL':<12}"
        f"{'Std PnL':<12}"
        f"{'Risk Adj':<16}"
        f"{'Avg |Inv|':<14}"
        f"{'Max |Inv|':<14}"
        f"{'Fills':<12}"
    )
    print("-" * 120)

    for noise_std in noise_levels:
        for strategy_name, inventory_skew in strategies:
            summary = run_trials_for_strategy(
                spread=spread,
                num_steps=num_steps,
                num_trials=num_trials,
                strategy=strategy_name,
                inventory_skew=inventory_skew,
                observation_noise_std=noise_std,
                risk_penalty=risk_penalty,
            )

            print_summary_row(
                noise_std=noise_std,
                strategy_name=strategy_name,
                inventory_skew=inventory_skew,
                summary=summary,
            )

        print()


if __name__ == "__main__":
    run_noise_experiment()