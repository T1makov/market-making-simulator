import random
import math
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

"""
Legacy one-file version of the simulator.

The current modular version should be run with:
    python3 -m src.main
"""

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"


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


def choose_quote_mid_price(strategy, observed_mid_price, inventory, inventory_skew):
    """
    Chooses the center point around which the bot places its bid and ask.

    Fixed strategy:
        Quote around the observed midprice.

    Inventory-aware strategy:
        Shift quotes depending on inventory.

    Uncertainty-aware strategies:
        Still quote around observed midprice, unless they are also inventory-aware.
    """

    if strategy == "fixed":
        return observed_mid_price

    if strategy == "inventory_aware":
        return observed_mid_price - inventory_skew * inventory

    if strategy == "uncertainty_aware":
        return observed_mid_price

    if strategy == "inventory_and_uncertainty_aware":
        return observed_mid_price - inventory_skew * inventory

    raise ValueError(f"Unknown strategy: {strategy}")


def choose_effective_spread(
    strategy,
    base_spread,
    estimated_uncertainty,
    uncertainty_sensitivity,
):
    """
    Chooses the spread the bot will quote.

    Fixed and inventory-aware strategies:
        Always use the same base spread.

    Uncertainty-aware strategies:
        Widen the spread when estimated uncertainty is high.
    """

    if strategy in ["fixed", "inventory_aware"]:
        return base_spread

    if strategy in ["uncertainty_aware", "inventory_and_uncertainty_aware"]:
        return base_spread + uncertainty_sensitivity * estimated_uncertainty

    raise ValueError(f"Unknown strategy: {strategy}")


def run_simulation(
    base_spread,
    num_steps,
    strategy,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
    uncertainty_sensitivity,
    volatility_window,
):
    """
    Runs one simulation of the market-making bot.
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
    sum_effective_spread = 0.0
    sum_estimated_uncertainty = 0.0

    previous_observed_mid_price = None
    recent_observed_price_changes = []

    for step in range(num_steps):
        # 1. The true market price moves randomly.
        price_change = random.choice([-0.01, 0.01])
        true_mid_price += price_change

        # 2. The bot observes the true price with noise.
        observation_noise = random.gauss(0.0, observation_noise_std)
        observed_mid_price = true_mid_price + observation_noise

        sum_abs_observation_error += abs(observation_noise)

        # 3. Update recent observed price changes.
        if previous_observed_mid_price is not None:
            observed_price_change = observed_mid_price - previous_observed_mid_price
            recent_observed_price_changes.append(observed_price_change)

            if len(recent_observed_price_changes) > volatility_window:
                recent_observed_price_changes.pop(0)

        previous_observed_mid_price = observed_mid_price

        # 4. Estimate uncertainty from recent observed price changes.
        estimated_uncertainty = estimate_uncertainty(recent_observed_price_changes)

        # 5. Choose the center of the bot's bid/ask quotes.
        quote_mid_price = choose_quote_mid_price(
            strategy=strategy,
            observed_mid_price=observed_mid_price,
            inventory=inventory,
            inventory_skew=inventory_skew,
        )

        # 6. Choose the spread.
        effective_spread = choose_effective_spread(
            strategy=strategy,
            base_spread=base_spread,
            estimated_uncertainty=estimated_uncertainty,
            uncertainty_sensitivity=uncertainty_sensitivity,
        )

        # 7. Place bid and ask around the chosen quote midpoint.
        bid_price = quote_mid_price - effective_spread / 2
        ask_price = quote_mid_price + effective_spread / 2

        # 8. Fills depend on the TRUE midprice, not the bot's observed price.
        bid_distance = true_mid_price - bid_price
        ask_distance = ask_price - true_mid_price

        prob_someone_sells_to_us = fill_probability(bid_distance)
        prob_someone_buys_from_us = fill_probability(ask_distance)

        # 9. Someone sells to us, so we buy at our bid.
        if random.random() < prob_someone_sells_to_us:
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 10. Someone buys from us, so we sell at our ask.
        if random.random() < prob_someone_buys_from_us:
            inventory -= 1
            cash += ask_price
            sell_fills += 1

        # 11. Track risk and strategy behavior.
        max_abs_inventory = max(max_abs_inventory, abs(inventory))
        sum_abs_inventory += abs(inventory)
        sum_effective_spread += effective_spread
        sum_estimated_uncertainty += estimated_uncertainty

    final_pnl = cash + inventory * true_mid_price
    average_abs_inventory = sum_abs_inventory / num_steps
    average_abs_observation_error = sum_abs_observation_error / num_steps
    average_effective_spread = sum_effective_spread / num_steps
    average_estimated_uncertainty = sum_estimated_uncertainty / num_steps

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
        "average_effective_spread": average_effective_spread,
        "average_estimated_uncertainty": average_estimated_uncertainty,
    }


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
        "avg_effective_spread": average(
            [result["average_effective_spread"] for result in results]
        ),
        "avg_estimated_uncertainty": average(
            [result["average_estimated_uncertainty"] for result in results]
        ),
    }


def run_trials_for_strategy(
    base_spread,
    num_steps,
    num_trials,
    strategy,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
    uncertainty_sensitivity,
    volatility_window,
):
    """
    Runs many simulations for one strategy under one noise level.
    """

    results = []

    for trial in range(num_trials):
        result = run_simulation(
            base_spread=base_spread,
            num_steps=num_steps,
            strategy=strategy,
            inventory_skew=inventory_skew,
            observation_noise_std=observation_noise_std,
            risk_penalty=risk_penalty,
            uncertainty_sensitivity=uncertainty_sensitivity,
            volatility_window=volatility_window,
        )
        results.append(result)

    return summarize_results(results)


def print_summary_row(noise_std, strategy_name, inventory_skew, summary):
    """
    Prints one row of the experiment table.
    """

    print(
        f"{noise_std:<8}"
        f"{strategy_name:<34}"
        f"{inventory_skew:<10}"
        f"{summary['avg_pnl']:<12.2f}"
        f"{summary['std_pnl']:<12.2f}"
        f"{summary['avg_risk_adjusted_score']:<16.2f}"
        f"{summary['avg_abs_inventory']:<14.2f}"
        f"{summary['avg_max_abs_inventory']:<14.2f}"
        f"{summary['avg_total_fills']:<12.2f}"
        f"{summary['avg_effective_spread']:<14.4f}"
        f"{summary['avg_estimated_uncertainty']:<14.4f}"
    )


def save_results_to_csv(rows):
    """
    Saves all experiment summary rows to a CSV file.
    """

    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    df = pd.DataFrame(rows)

    output_path = RESULTS_DIR / "experiment_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print(f"Saved experiment results to: {output_path}")

    return df


def save_metric_plot(df, metric, ylabel, title, filename):
    """
    Saves one line plot for a specific metric.

    The x-axis is observation noise.
    Each line is one strategy.
    """

    plt.figure(figsize=(10, 6))

    for strategy in df["strategy"].unique():
        strategy_df = df[df["strategy"] == strategy]

        plt.plot(
            strategy_df["observation_noise_std"],
            strategy_df[metric],
            marker="o",
            label=strategy,
        )

    plt.xlabel("Observation Noise Standard Deviation")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = PLOTS_DIR / filename
    plt.savefig(output_path)
    plt.close()

    print(f"Saved plot: {output_path}")


def generate_plots(df):
    """
    Generates and saves plots from the experiment results.
    """

    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    save_metric_plot(
        df=df,
        metric="avg_pnl",
        ylabel="Average PnL",
        title="Average PnL by Strategy and Observation Noise",
        filename="avg_pnl_by_noise.png",
    )

    save_metric_plot(
        df=df,
        metric="avg_risk_adjusted_score",
        ylabel="Average Risk-Adjusted Score",
        title="Risk-Adjusted Score by Strategy and Observation Noise",
        filename="risk_adjusted_score_by_noise.png",
    )

    save_metric_plot(
        df=df,
        metric="avg_abs_inventory",
        ylabel="Average Absolute Inventory",
        title="Average Inventory Exposure by Strategy and Observation Noise",
        filename="avg_inventory_by_noise.png",
    )

    save_metric_plot(
        df=df,
        metric="avg_max_abs_inventory",
        ylabel="Average Max Absolute Inventory",
        title="Maximum Inventory Exposure by Strategy and Observation Noise",
        filename="max_inventory_by_noise.png",
    )

    save_metric_plot(
        df=df,
        metric="avg_total_fills",
        ylabel="Average Total Fills",
        title="Average Total Fills by Strategy and Observation Noise",
        filename="fills_by_noise.png",
    )

    save_metric_plot(
        df=df,
        metric="avg_effective_spread",
        ylabel="Average Effective Spread",
        title="Average Effective Spread by Strategy and Observation Noise",
        filename="avg_spread_by_noise.png",
    )


def run_uncertainty_experiment():
    """
    Main experiment:

    For each observation-noise level, compare:
        - fixed quoting
        - inventory-aware quoting
        - uncertainty-aware quoting
        - inventory-and-uncertainty-aware quoting

    The uncertainty-aware strategies estimate uncertainty using recent observed
    price changes. They do NOT know the true observation_noise_std.
    """

    random.seed(42)

    base_spread = 0.10
    num_steps = 1000
    num_trials = 500
    risk_penalty = 2.0

    uncertainty_sensitivity = 3.0
    volatility_window = 50

    noise_levels = [0.00, 0.01, 0.03, 0.05, 0.10, 0.20]

    strategies = [
        ("fixed", 0.0),
        ("inventory_aware", 0.002),
        ("uncertainty_aware", 0.0),
        ("inventory_and_uncertainty_aware", 0.002),
    ]

    experiment_rows = []

    print("Uncertainty-Aware Market-Making Experiment")
    print("------------------------------------------")
    print(f"Base spread: {base_spread}")
    print(f"Steps per simulation: {num_steps}")
    print(f"Trials per strategy/noise level: {num_trials}")
    print(f"Risk penalty: {risk_penalty}")
    print(f"Uncertainty sensitivity: {uncertainty_sensitivity}")
    print(f"Volatility window: {volatility_window}")
    print()

    print(
        f"{'Noise':<8}"
        f"{'Strategy':<34}"
        f"{'Skew':<10}"
        f"{'Avg PnL':<12}"
        f"{'Std PnL':<12}"
        f"{'Risk Adj':<16}"
        f"{'Avg |Inv|':<14}"
        f"{'Max |Inv|':<14}"
        f"{'Fills':<12}"
        f"{'Avg Spread':<14}"
        f"{'Est Uncert':<14}"
    )
    print("-" * 160)

    for noise_std in noise_levels:
        for strategy_name, inventory_skew in strategies:
            summary = run_trials_for_strategy(
                base_spread=base_spread,
                num_steps=num_steps,
                num_trials=num_trials,
                strategy=strategy_name,
                inventory_skew=inventory_skew,
                observation_noise_std=noise_std,
                risk_penalty=risk_penalty,
                uncertainty_sensitivity=uncertainty_sensitivity,
                volatility_window=volatility_window,
            )

            print_summary_row(
                noise_std=noise_std,
                strategy_name=strategy_name,
                inventory_skew=inventory_skew,
                summary=summary,
            )

            row = {
                "observation_noise_std": noise_std,
                "strategy": strategy_name,
                "inventory_skew": inventory_skew,
                "base_spread": base_spread,
                "num_steps": num_steps,
                "num_trials": num_trials,
                "risk_penalty": risk_penalty,
                "uncertainty_sensitivity": uncertainty_sensitivity,
                "volatility_window": volatility_window,
                **summary,
            }

            experiment_rows.append(row)

        print()

    df = save_results_to_csv(experiment_rows)
    generate_plots(df)


if __name__ == "__main__":
    run_uncertainty_experiment()