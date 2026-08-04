from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_PATH = RESULTS_DIR / "regime_parameter_optimization_results.csv"
OUTPUT_PATH = RESULTS_DIR / "fill_constrained_best_parameters.csv"


def analyze_fill_constrained_parameters():
    """
    Finds the best parameter set in each regime subject to minimum fill
    requirements.

    This prevents the optimizer from choosing strategies that look good only
    because they almost never trade.
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

    minimum_fill_requirements = [1, 10, 25, 50, 100]

    rows = []

    for regime in regime_order:
        regime_df = df[df["regime"] == regime]

        for min_fills in minimum_fill_requirements:
            feasible_df = regime_df[
                regime_df["avg_total_fills"] >= min_fills
            ]

            if feasible_df.empty:
                row = {
                    "regime": regime,
                    "minimum_avg_fills": min_fills,
                    "feasible": False,
                    "brownian_volatility": None,
                    "observation_noise_std": None,
                    "base_spread": None,
                    "inventory_skew": None,
                    "uncertainty_sensitivity": None,
                    "avg_pnl": None,
                    "std_pnl": None,
                    "avg_risk_adjusted_score": None,
                    "avg_abs_inventory": None,
                    "avg_total_fills": None,
                    "avg_effective_spread": None,
                }
            else:
                best_row = feasible_df.sort_values(
                    by="avg_risk_adjusted_score",
                    ascending=False,
                ).iloc[0]

                row = {
                    "regime": regime,
                    "minimum_avg_fills": min_fills,
                    "feasible": True,
                    "brownian_volatility": best_row["brownian_volatility"],
                    "observation_noise_std": best_row["observation_noise_std"],
                    "base_spread": best_row["base_spread"],
                    "inventory_skew": best_row["inventory_skew"],
                    "uncertainty_sensitivity": best_row[
                        "uncertainty_sensitivity"
                    ],
                    "avg_pnl": best_row["avg_pnl"],
                    "std_pnl": best_row["std_pnl"],
                    "avg_risk_adjusted_score": best_row[
                        "avg_risk_adjusted_score"
                    ],
                    "avg_abs_inventory": best_row["avg_abs_inventory"],
                    "avg_total_fills": best_row["avg_total_fills"],
                    "avg_effective_spread": best_row["avg_effective_spread"],
                }

            rows.append(row)

    summary_df = pd.DataFrame(rows)

    summary_df.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved fill-constrained optimization summary to: {OUTPUT_PATH}")
    print()
    print("Fill-Constrained Best Parameters")
    print("--------------------------------")
    print(summary_df.to_string(index=False))

    return summary_df


if __name__ == "__main__":
    analyze_fill_constrained_parameters()