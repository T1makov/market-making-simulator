from pathlib import Path

from matplotlib import pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

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