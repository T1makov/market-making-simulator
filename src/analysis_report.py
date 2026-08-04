from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

OBSERVATION_RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"
VOLATILITY_RESULTS_PATH = RESULTS_DIR / "volatility_experiment_results.csv"
PARAMETER_OPTIMIZATION_PATH = RESULTS_DIR / "parameter_optimization_results.csv"
REGIME_OPTIMIZATION_PATH = RESULTS_DIR / "regime_parameter_optimization_results.csv"
FILL_CONSTRAINT_PATH = RESULTS_DIR / "fill_constrained_best_parameters.csv"

OUTPUT_PATH = RESULTS_DIR / "analysis_summary.md"


def require_file(path):
    """
    Raises a clear error if a required results file does not exist.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run the relevant experiment first."
        )


def best_rows_by_group(df, group_column, score_column="avg_risk_adjusted_score"):
    """
    Returns the best row within each group according to the score column.
    """

    best_indices = df.groupby(group_column)[score_column].idxmax()
    return df.loc[best_indices].sort_values(group_column)


def format_float(value, digits=4):
    """
    Formats floats nicely for the markdown report.
    """

    if pd.isna(value):
        return ""

    return f"{value:.{digits}f}"


def dataframe_to_markdown(df, columns, float_digits=4):
    """
    Converts selected dataframe columns into a markdown table.
    """

    table_df = df[columns].copy()

    for column in table_df.columns:
        if pd.api.types.is_float_dtype(table_df[column]):
            table_df[column] = table_df[column].apply(
                lambda value: format_float(value, float_digits)
            )

    return table_df.to_markdown(index=False)


def write_observation_noise_section(lines):
    """
    Adds a section summarizing the observation-noise experiment.
    """

    require_file(OBSERVATION_RESULTS_PATH)

    df = pd.read_csv(OBSERVATION_RESULTS_PATH)

    best_df = best_rows_by_group(
        df=df,
        group_column="observation_noise_std",
    )

    lines.append("## Observation-Noise Experiment")
    lines.append("")
    lines.append(
        "This experiment varies the noise in the bot's observed midprice while "
        "keeping the market model fixed. It tests how strategies behave when "
        "fair-value observations become less reliable."
    )
    lines.append("")
    lines.append("Best strategy by observation-noise level:")
    lines.append("")
    lines.append(
        dataframe_to_markdown(
            best_df,
            columns=[
                "observation_noise_std",
                "strategy",
                "avg_pnl",
                "avg_risk_adjusted_score",
                "avg_abs_inventory",
                "avg_total_fills",
                "avg_effective_spread",
            ],
        )
    )
    lines.append("")

    low_noise_row = best_df.iloc[0]
    high_noise_row = best_df.iloc[-1]

    lines.append("Key observation:")
    lines.append("")
    lines.append(
        f"- At low observation noise, the best strategy is "
        f"`{low_noise_row['strategy']}`."
    )
    lines.append(
        f"- At high observation noise, the best strategy is "
        f"`{high_noise_row['strategy']}`."
    )
    lines.append(
        "- This shows how noisy fair-value estimates can change the preferred "
        "quoting strategy."
    )
    lines.append("")


def write_volatility_section(lines):
    """
    Adds a section summarizing the volatility-regime experiment.
    """

    require_file(VOLATILITY_RESULTS_PATH)

    df = pd.read_csv(VOLATILITY_RESULTS_PATH)

    best_df = best_rows_by_group(
        df=df,
        group_column="brownian_volatility",
    )

    lines.append("## Volatility-Regime Experiment")
    lines.append("")
    lines.append(
        "This experiment varies the true Brownian volatility of the market "
        "while keeping observation noise fixed. It tests whether strategies "
        "are robust when the actual midprice moves more aggressively."
    )
    lines.append("")
    lines.append("Best strategy by Brownian volatility level:")
    lines.append("")
    lines.append(
        dataframe_to_markdown(
            best_df,
            columns=[
                "brownian_volatility",
                "strategy",
                "avg_pnl",
                "avg_risk_adjusted_score",
                "avg_abs_inventory",
                "avg_total_fills",
                "avg_effective_spread",
                "avg_estimated_uncertainty",
            ],
        )
    )
    lines.append("")
    lines.append("Key observation:")
    lines.append("")
    lines.append(
        "- The volatility experiment checks whether the uncertainty estimator "
        "responds as true market volatility increases."
    )
    lines.append(
        "- Comparing this with the observation-noise experiment helps separate "
        "true market movement from noisy fair-value estimation."
    )
    lines.append("")


def write_parameter_optimization_section(lines):
    """
    Adds a section summarizing the single-regime parameter optimization.
    """

    require_file(PARAMETER_OPTIMIZATION_PATH)

    df = pd.read_csv(PARAMETER_OPTIMIZATION_PATH)
    top_df = df.sort_values(
        by="avg_risk_adjusted_score",
        ascending=False,
    ).head(10)

    lines.append("## Parameter Optimization")
    lines.append("")
    lines.append(
        "This experiment grid-searches over base spread, inventory skew, and "
        "uncertainty sensitivity for the combined strategy."
    )
    lines.append("")
    lines.append("Top 10 parameter sets:")
    lines.append("")
    lines.append(
        dataframe_to_markdown(
            top_df,
            columns=[
                "base_spread",
                "inventory_skew",
                "uncertainty_sensitivity",
                "avg_pnl",
                "std_pnl",
                "avg_risk_adjusted_score",
                "avg_abs_inventory",
                "avg_total_fills",
                "avg_effective_spread",
            ],
        )
    )
    lines.append("")

    best_row = top_df.iloc[0]

    lines.append("Best parameter set:")
    lines.append("")
    lines.append(f"- `base_spread = {best_row['base_spread']}`")
    lines.append(f"- `inventory_skew = {best_row['inventory_skew']}`")
    lines.append(
        f"- `uncertainty_sensitivity = "
        f"{best_row['uncertainty_sensitivity']}`"
    )
    lines.append(
        f"- average risk-adjusted score: "
        f"`{best_row['avg_risk_adjusted_score']:.4f}`"
    )
    lines.append("")


def write_regime_optimization_section(lines):
    """
    Adds a section summarizing regime-specific parameter optimization.
    """

    require_file(REGIME_OPTIMIZATION_PATH)

    df = pd.read_csv(REGIME_OPTIMIZATION_PATH)

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

    lines.append("## Regime-Specific Parameter Optimization")
    lines.append("")
    lines.append(
        "This experiment optimizes parameters separately across four market "
        "regimes: calm/clean, volatile/clean, calm/noisy, and volatile/noisy."
    )
    lines.append("")
    lines.append("Best parameter set by regime:")
    lines.append("")
    lines.append(
        dataframe_to_markdown(
            best_df,
            columns=[
                "regime",
                "brownian_volatility",
                "observation_noise_std",
                "base_spread",
                "inventory_skew",
                "uncertainty_sensitivity",
                "avg_pnl",
                "avg_risk_adjusted_score",
                "avg_abs_inventory",
                "avg_total_fills",
                "avg_effective_spread",
            ],
        )
    )
    lines.append("")
    lines.append("Key observation:")
    lines.append("")
    lines.append(
        "- Clean regimes tend to support tighter spreads and frequent trading."
    )
    lines.append(
        "- Noisy regimes tend to favor wider spreads and larger uncertainty "
        "sensitivity."
    )
    lines.append(
        "- This suggests that uncertainty-aware spread widening is most useful "
        "when fair-value observations are unreliable."
    )
    lines.append("")


def write_fill_constraint_section(lines):
    """
    Adds a section summarizing fill-constrained optimization.
    """

    require_file(FILL_CONSTRAINT_PATH)

    df = pd.read_csv(FILL_CONSTRAINT_PATH)

    lines.append("## Fill-Constrained Optimization")
    lines.append("")
    lines.append(
        "The unconstrained optimizer can choose very wide spreads in noisy "
        "regimes, causing the strategy to barely trade. This analysis adds "
        "minimum average fill requirements to study the tradeoff between "
        "liquidity provision and risk-adjusted performance."
    )
    lines.append("")
    lines.append("Best feasible parameter sets under fill constraints:")
    lines.append("")
    lines.append(
        dataframe_to_markdown(
            df,
            columns=[
                "regime",
                "minimum_avg_fills",
                "feasible",
                "base_spread",
                "inventory_skew",
                "uncertainty_sensitivity",
                "avg_pnl",
                "avg_risk_adjusted_score",
                "avg_abs_inventory",
                "avg_total_fills",
                "avg_effective_spread",
            ],
        )
    )
    lines.append("")
    lines.append("Key observation:")
    lines.append("")
    lines.append(
        "- In clean regimes, the fill constraint has little effect because the "
        "best strategies already trade frequently."
    )
    lines.append(
        "- In noisy regimes, requiring more fills forces the strategy to quote "
        "more aggressively, which usually lowers risk-adjusted performance."
    )
    lines.append(
        "- This exposes a liquidity-versus-risk tradeoff: market makers may "
        "need to accept worse risk-adjusted performance if they are required "
        "to provide liquidity."
    )
    lines.append("")


def generate_analysis_report():
    """
    Generates a markdown report summarizing the main experimental findings.
    """

    RESULTS_DIR.mkdir(exist_ok=True)

    lines = []

    lines.append("# Market-Making Simulator Analysis Summary")
    lines.append("")
    lines.append(
        "This report is automatically generated from the simulator's result "
        "CSVs. It summarizes the main findings from the observation-noise, "
        "volatility-regime, parameter-optimization, regime-optimization, and "
        "fill-constrained optimization experiments."
    )
    lines.append("")

    write_observation_noise_section(lines)
    write_volatility_section(lines)
    write_parameter_optimization_section(lines)
    write_regime_optimization_section(lines)
    write_fill_constraint_section(lines)

    lines.append("## Overall Project Takeaway")
    lines.append("")
    lines.append(
        "The simulator shows that market-making performance depends strongly "
        "on the quality of the fair-value signal and the market regime. In "
        "clean regimes, the strategy can trade frequently while controlling "
        "inventory with inventory-aware skew. In noisy regimes, uncertainty-"
        "aware spread widening becomes much more important, but it can also "
        "reduce fill frequency sharply. When minimum fill constraints are "
        "introduced, the strategy must trade off liquidity provision against "
        "risk-adjusted performance."
    )
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines))

    print()
    print(f"Saved analysis report to: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_analysis_report()