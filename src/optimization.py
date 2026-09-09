import random
from pathlib import Path

import pandas as pd

from .experiments import run_trials_for_strategy
from .plotting import generate_optimization_plots, generate_regime_optimization_plots


def run_parameter_optimization():
    """
    Runs a grid search over market-making strategy parameters.

    The goal is to find parameter combinations that maximize average
    risk-adjusted score under a fixed market environment.
    """

    random.seed(456)

    # Fixed market environment
    num_steps = 1000
    num_trials = 200
    risk_penalty = 2.0

    price_process = "brownian"
    random_walk_step_size = 0.01
    brownian_drift = 0.0
    brownian_volatility = 0.02
    dt = 1.0

    observation_noise_std = 0.03
    volatility_window = 50

    # Parameter grid
    base_spread_values = [0.05, 0.10, 0.15, 0.20]
    inventory_skew_values = [0.0, 0.001, 0.002, 0.004]
    uncertainty_sensitivity_values = [0.0, 1.0, 2.0, 3.0, 5.0]

    rows = []

    print()
    print("Parameter Optimization Experiment")
    print("---------------------------------")
    print(f"Steps per simulation: {num_steps}")
    print(f"Trials per parameter set: {num_trials}")
    print(f"Risk penalty: {risk_penalty}")
    print(f"Price process: {price_process}")
    print(f"Brownian drift: {brownian_drift}")
    print(f"Brownian volatility: {brownian_volatility}")
    print(f"Observation noise std: {observation_noise_std}")
    print(f"Volatility window: {volatility_window}")
    print()

    total_combinations = (
        len(base_spread_values)
        * len(inventory_skew_values)
        * len(uncertainty_sensitivity_values)
    )

    combination_number = 0

    for base_spread in base_spread_values:
        for inventory_skew in inventory_skew_values:
            for uncertainty_sensitivity in uncertainty_sensitivity_values:
                combination_number += 1

                print(
                    f"Running {combination_number}/{total_combinations}: "
                    f"spread={base_spread}, "
                    f"skew={inventory_skew}, "
                    f"uncertainty_sensitivity={uncertainty_sensitivity}"
                )

                summary = run_trials_for_strategy(
                    base_spread=base_spread,
                    num_steps=num_steps,
                    num_trials=num_trials,
                    strategy="inventory_and_uncertainty_aware",
                    inventory_skew=inventory_skew,
                    observation_noise_std=observation_noise_std,
                    risk_penalty=risk_penalty,
                    uncertainty_sensitivity=uncertainty_sensitivity,
                    volatility_window=volatility_window,
                    price_process=price_process,
                    random_walk_step_size=random_walk_step_size,
                    brownian_drift=brownian_drift,
                    brownian_volatility=brownian_volatility,
                    dt=dt,
                )

                row = {
                    "base_spread": base_spread,
                    "inventory_skew": inventory_skew,
                    "uncertainty_sensitivity": uncertainty_sensitivity,
                    "strategy": "inventory_and_uncertainty_aware",
                    "num_steps": num_steps,
                    "num_trials": num_trials,
                    "risk_penalty": risk_penalty,
                    "price_process": price_process,
                    "random_walk_step_size": random_walk_step_size,
                    "brownian_drift": brownian_drift,
                    "brownian_volatility": brownian_volatility,
                    "dt": dt,
                    "observation_noise_std": observation_noise_std,
                    "volatility_window": volatility_window,
                    **summary,
                }

                rows.append(row)

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by="avg_risk_adjusted_score",
        ascending=False,
    )

    Path("results").mkdir(exist_ok=True)

    output_path = "results/parameter_optimization_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print(f"Saved optimization results to: {output_path}")
    print()
    print("Top 10 Parameter Sets")
    print("---------------------")

    columns_to_show = [
        "base_spread",
        "inventory_skew",
        "uncertainty_sensitivity",
        "avg_pnl",
        "std_pnl",
        "avg_risk_adjusted_score",
        "avg_abs_inventory",
        "avg_total_fills",
        "avg_effective_spread",
    ]

    print(df[columns_to_show].head(10).to_string(index=False))

    generate_optimization_plots(df)

    return df


def run_regime_parameter_optimization():
    """
    Runs parameter optimization separately across multiple market regimes.

    This tests whether the best market-making parameters depend on the
    underlying market environment.
    """

    random.seed(789)

    # Simulation settings
    num_steps = 1000
    num_trials = 100
    risk_penalty = 2.0

    price_process = "brownian"
    random_walk_step_size = 0.01
    brownian_drift = 0.0
    dt = 1.0

    volatility_window = 50

    # Parameter grid
    base_spread_values = [0.05, 0.10, 0.15, 0.20]
    inventory_skew_values = [0.0, 0.001, 0.002, 0.004]
    uncertainty_sensitivity_values = [0.0, 1.0, 2.0, 3.0, 5.0]

    regimes = [
        {
            "regime": "calm_clean",
            "brownian_volatility": 0.01,
            "observation_noise_std": 0.01,
        },
        {
            "regime": "volatile_clean",
            "brownian_volatility": 0.05,
            "observation_noise_std": 0.01,
        },
        {
            "regime": "calm_noisy",
            "brownian_volatility": 0.01,
            "observation_noise_std": 0.10,
        },
        {
            "regime": "volatile_noisy",
            "brownian_volatility": 0.05,
            "observation_noise_std": 0.10,
        },
    ]

    total_combinations_per_regime = (
        len(base_spread_values)
        * len(inventory_skew_values)
        * len(uncertainty_sensitivity_values)
    )

    total_runs = total_combinations_per_regime * len(regimes)

    rows = []
    run_number = 0

    print()
    print("Regime-Specific Parameter Optimization")
    print("--------------------------------------")
    print(f"Steps per simulation: {num_steps}")
    print(f"Trials per parameter set: {num_trials}")
    print(f"Total parameter sets per regime: {total_combinations_per_regime}")
    print(f"Total optimization runs: {total_runs}")
    print(f"Risk penalty: {risk_penalty}")
    print(f"Price process: {price_process}")
    print(f"Brownian drift: {brownian_drift}")
    print(f"Volatility window: {volatility_window}")
    print()

    for regime_config in regimes:
        regime_name = regime_config["regime"]
        brownian_volatility = regime_config["brownian_volatility"]
        observation_noise_std = regime_config["observation_noise_std"]

        print()
        print(f"Optimizing regime: {regime_name}")
        print(f"Brownian volatility: {brownian_volatility}")
        print(f"Observation noise std: {observation_noise_std}")
        print("-" * 60)

        for base_spread in base_spread_values:
            for inventory_skew in inventory_skew_values:
                for uncertainty_sensitivity in uncertainty_sensitivity_values:
                    run_number += 1

                    print(
                        f"Running {run_number}/{total_runs}: "
                        f"regime={regime_name}, "
                        f"spread={base_spread}, "
                        f"skew={inventory_skew}, "
                        f"sens={uncertainty_sensitivity}"
                    )

                    summary = run_trials_for_strategy(
                        base_spread=base_spread,
                        num_steps=num_steps,
                        num_trials=num_trials,
                        strategy="inventory_and_uncertainty_aware",
                        inventory_skew=inventory_skew,
                        observation_noise_std=observation_noise_std,
                        risk_penalty=risk_penalty,
                        uncertainty_sensitivity=uncertainty_sensitivity,
                        volatility_window=volatility_window,
                        price_process=price_process,
                        random_walk_step_size=random_walk_step_size,
                        brownian_drift=brownian_drift,
                        brownian_volatility=brownian_volatility,
                        dt=dt,
                    )

                    row = {
                        "regime": regime_name,
                        "base_spread": base_spread,
                        "inventory_skew": inventory_skew,
                        "uncertainty_sensitivity": uncertainty_sensitivity,
                        "strategy": "inventory_and_uncertainty_aware",
                        "num_steps": num_steps,
                        "num_trials": num_trials,
                        "risk_penalty": risk_penalty,
                        "price_process": price_process,
                        "random_walk_step_size": random_walk_step_size,
                        "brownian_drift": brownian_drift,
                        "brownian_volatility": brownian_volatility,
                        "dt": dt,
                        "observation_noise_std": observation_noise_std,
                        "volatility_window": volatility_window,
                        **summary,
                    }

                    rows.append(row)

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by=["regime", "avg_risk_adjusted_score"],
        ascending=[True, False],
    )

    Path("results").mkdir(exist_ok=True)

    output_path = "results/regime_parameter_optimization_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print(f"Saved regime optimization results to: {output_path}")

    columns_to_show = [
        "base_spread",
        "inventory_skew",
        "uncertainty_sensitivity",
        "avg_pnl",
        "std_pnl",
        "avg_risk_adjusted_score",
        "avg_abs_inventory",
        "avg_total_fills",
        "avg_effective_spread",
    ]

    for regime_config in regimes:
        regime_name = regime_config["regime"]

        print()
        print(f"Top 5 Parameter Sets for {regime_name}")
        print("-" * 50)

        regime_df = df[df["regime"] == regime_name]
        regime_df = regime_df.sort_values(
            by="avg_risk_adjusted_score",
            ascending=False,
        )

        print(regime_df[columns_to_show].head(5).to_string(index=False))

    generate_regime_optimization_plots(df)

    return df