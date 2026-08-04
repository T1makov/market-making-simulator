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
def save_price_path_plot(
    simulation_result,
    filename="sample_true_vs_observed_midprice.png",
):
    """
    Saves a plot of the true midprice and observed midprice from one simulation.

    This is useful for visualizing the simulated market path and the noisy
    price signal observed by the bot.
    """

    PLOTS_DIR.mkdir(exist_ok=True)

    true_prices = simulation_result["true_mid_price_history"]
    observed_prices = simulation_result["observed_mid_price_history"]

    steps = list(range(len(true_prices)))

    plt.figure(figsize=(10, 6))

    plt.plot(
    steps,
    observed_prices,
    label="Observed midprice",
    linewidth=1.0,
    alpha=0.45,
    )

    plt.plot(
        steps,
        true_prices,
        label="True midprice",
        linewidth=2.5,
    )

    plt.xlabel("Time Step")
    plt.ylabel("Midprice")
    plt.title("Sample True vs Observed Midprice Path")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = PLOTS_DIR / filename
    plt.savefig(output_path)
    plt.close()

    print(f"Saved plot: {output_path}")
def save_volatility_metric_plot(df, metric, ylabel, title, filename):
    """
    Saves one line plot for a specific metric.

    The x-axis is Brownian volatility.
    Each line is one strategy.
    """

    plt.figure(figsize=(10, 6))

    for strategy in df["strategy"].unique():
        strategy_df = df[df["strategy"] == strategy]

        plt.plot(
            strategy_df["brownian_volatility"],
            strategy_df[metric],
            marker="o",
            label=strategy,
        )

    plt.xlabel("Brownian Volatility")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = PLOTS_DIR / filename
    plt.savefig(output_path)
    plt.close()

    print(f"Saved plot: {output_path}")


def generate_volatility_plots(df):
    """
    Generates and saves plots from the volatility-regime experiment.
    """

    RESULTS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    save_volatility_metric_plot(
        df=df,
        metric="avg_pnl",
        ylabel="Average PnL",
        title="Average PnL by Strategy and Brownian Volatility",
        filename="avg_pnl_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_risk_adjusted_score",
        ylabel="Average Risk-Adjusted Score",
        title="Risk-Adjusted Score by Strategy and Brownian Volatility",
        filename="risk_adjusted_score_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_abs_inventory",
        ylabel="Average Absolute Inventory",
        title="Average Inventory Exposure by Strategy and Brownian Volatility",
        filename="avg_inventory_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_max_abs_inventory",
        ylabel="Average Max Absolute Inventory",
        title="Maximum Inventory Exposure by Strategy and Brownian Volatility",
        filename="max_inventory_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_total_fills",
        ylabel="Average Total Fills",
        title="Average Total Fills by Strategy and Brownian Volatility",
        filename="fills_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_effective_spread",
        ylabel="Average Effective Spread",
        title="Average Effective Spread by Strategy and Brownian Volatility",
        filename="avg_spread_by_volatility.png",
    )

    save_volatility_metric_plot(
        df=df,
        metric="avg_estimated_uncertainty",
        ylabel="Average Estimated Uncertainty",
        title="Estimated Uncertainty by Strategy and Brownian Volatility",
        filename="estimated_uncertainty_by_volatility.png",
    )