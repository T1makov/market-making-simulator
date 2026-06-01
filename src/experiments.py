from pathlib import Path

import random

import pandas as pd

from .plotting import generate_plots
from .simulator import run_simulation
from .toy_simulator import summarize_results

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

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