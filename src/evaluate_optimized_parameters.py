import random
from pathlib import Path

import pandas as pd

from .experiments import run_trials_for_strategy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_PATH = RESULTS_DIR / "best_parameters_by_regime.csv"
OUTPUT_PATH = RESULTS_DIR / "optimized_parameter_evaluation.csv"


def evaluate_optimized_parameters():
    """
    Evaluates optimized regime parameters on fresh simulations.

    The optimization step selected the best parameters using one set of random
    simulations. This script reruns those selected parameters using a different
    random seed and more trials to check whether the optimized settings remain
    strong out of sample.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_PATH}. Run "
            "`python3 -m src.analyze_regime_results` first."
        )

    random.seed(999)

    optimized_df = pd.read_csv(INPUT_PATH)

    num_steps = 1000
    num_trials = 500
    risk_penalty = 2.0

    price_process = "brownian"
    random_walk_step_size = 0.01
    brownian_drift = 0.0
    dt = 1.0
    volatility_window = 50

    rows = []

    print()
    print("Out-of-Sample Optimized Parameter Evaluation")
    print("--------------------------------------------")
    print(f"Steps per simulation: {num_steps}")
    print(f"Trials per regime: {num_trials}")
    print("Random seed: 999")
    print()

    for _, row in optimized_df.iterrows():
        regime = row["regime"]

        print(f"Evaluating regime: {regime}")

        summary = run_trials_for_strategy(
            base_spread=float(row["base_spread"]),
            num_steps=num_steps,
            num_trials=num_trials,
            strategy="inventory_and_uncertainty_aware",
            inventory_skew=float(row["inventory_skew"]),
            observation_noise_std=float(row["observation_noise_std"]),
            risk_penalty=risk_penalty,
            uncertainty_sensitivity=float(row["uncertainty_sensitivity"]),
            volatility_window=volatility_window,
            price_process=price_process,
            random_walk_step_size=random_walk_step_size,
            brownian_drift=brownian_drift,
            brownian_volatility=float(row["brownian_volatility"]),
            dt=dt,
        )

        evaluation_row = {
            "regime": regime,
            "base_spread": float(row["base_spread"]),
            "inventory_skew": float(row["inventory_skew"]),
            "uncertainty_sensitivity": float(
                row["uncertainty_sensitivity"]
            ),
            "brownian_volatility": float(row["brownian_volatility"]),
            "observation_noise_std": float(row["observation_noise_std"]),
            "optimization_avg_risk_adjusted_score": float(
                row["avg_risk_adjusted_score"]
            ),
            "evaluation_avg_risk_adjusted_score": summary[
                "avg_risk_adjusted_score"
            ],
            "score_difference": summary["avg_risk_adjusted_score"]
            - float(row["avg_risk_adjusted_score"]),
            **summary,
        }

        rows.append(evaluation_row)

    evaluation_df = pd.DataFrame(rows)

    RESULTS_DIR.mkdir(exist_ok=True)
    evaluation_df.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved evaluation results to: {OUTPUT_PATH}")
    print()
    print("Out-of-Sample Evaluation Results")
    print("--------------------------------")
    print(
        evaluation_df[
            [
                "regime",
                "base_spread",
                "inventory_skew",
                "uncertainty_sensitivity",
                "optimization_avg_risk_adjusted_score",
                "evaluation_avg_risk_adjusted_score",
                "score_difference",
                "avg_pnl",
                "avg_abs_inventory",
                "avg_total_fills",
            ]
        ].to_string(index=False)
    )

    return evaluation_df


if __name__ == "__main__":
    evaluate_optimized_parameters()