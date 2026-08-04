from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_PATH = RESULTS_DIR / "regime_parameter_optimization_results.csv"
OUTPUT_PATH = RESULTS_DIR / "best_parameters_by_regime.csv"


def analyze_best_parameters_by_regime():
    """
    Extracts the best parameter set for each market regime from the
    regime-specific optimization results.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_PATH}. "
            "Run `python3 -m src.optimize_regimes` first."
        )

    df = pd.read_csv(INPUT_PATH)

    regime_order = [
        "calm_clean",
        "volatile_clean",
        "calm_noisy",
        "volatile_noisy",
    ]

    best_df = (
        df.sort_values(
            by="avg_risk_adjusted_score",
            ascending=False,
        )
        .drop_duplicates(subset=["regime"], keep="first")
        .copy()
    )

    best_df["regime"] = pd.Categorical(
        best_df["regime"],
        categories=regime_order,
        ordered=True,
    )

    best_df = best_df.sort_values("regime")

    columns_to_keep = [
        "regime",
        "brownian_volatility",
        "observation_noise_std",
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

    best_summary = best_df[columns_to_keep]

    best_summary.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved best parameters by regime to: {OUTPUT_PATH}")
    print()
    print("Best Parameters by Regime")
    print("-------------------------")
    print(best_summary.to_string(index=False))

    return best_summary


if __name__ == "__main__":
    analyze_best_parameters_by_regime()