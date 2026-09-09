import random
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
BEST_PARAMETERS_PATH = RESULTS_DIR / "best_parameters_by_regime.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.experiments import run_trials_for_strategy
from src.simulator import run_simulation


st.set_page_config(
    page_title="Market-Making Simulator",
    page_icon="📈",
    layout="wide",
)


STRATEGIES = [
    "fixed",
    "inventory_aware",
    "uncertainty_aware",
    "inventory_and_uncertainty_aware",
]

STRATEGY_LABELS = {
    "fixed": "Fixed Spread",
    "inventory_aware": "Inventory-Aware",
    "uncertainty_aware": "Uncertainty-Aware",
    "inventory_and_uncertainty_aware": "Inventory + Uncertainty-Aware",
}


STRATEGY_DESCRIPTIONS = {
    "fixed": """
    Quotes a fixed bid/ask spread around the observed midprice.

    This is the simplest strategy. It can perform well when the observed
    midprice is accurate, but it does not actively manage inventory risk or
    uncertainty.
    """,
    "inventory_aware": """
    Shifts quotes based on current inventory.

    When inventory is positive, the strategy shifts quotes downward to
    encourage selling. When inventory is negative, it shifts quotes upward to
    encourage buying back.
    """,
    "uncertainty_aware": """
    Widens the spread when recent observed price changes become more volatile.

    This helps the strategy avoid trading too aggressively when the fair-value
    signal is unreliable.
    """,
    "inventory_and_uncertainty_aware": """
    Combines inventory-aware quote shifting with uncertainty-aware spread
    widening.

    This strategy manages both inventory risk and noisy fair-value estimation.
    """,
}


def strategy_label(strategy_name):
    """
    Converts internal strategy names into readable dashboard labels.
    """

    return STRATEGY_LABELS.get(strategy_name, strategy_name)


DEFAULT_SETTINGS = {
    "seed": 42,
    "price_process": "brownian",
    "num_steps": 1000,
    "base_spread": 0.10,
    "inventory_skew": 0.002,
    "observation_noise_std": 0.03,
    "risk_penalty": 2.0,
    "uncertainty_sensitivity": 3.0,
    "volatility_window": 50,
    "random_walk_step_size": 0.01,
    "brownian_drift": 0.0,
    "brownian_volatility": 0.02,
    "dt": 1.0,
}


for key, value in DEFAULT_SETTINGS.items():
    st.session_state.setdefault(key, value)

# Counts how many times each "Run" button has been pressed, so repeated
# presses advance the random seed instead of replaying the exact same
# simulation every time.
for run_count_key in [
    "single_simulation_run_count",
    "strategy_comparison_run_count",
    "preset_evaluation_run_count",
]:
    st.session_state.setdefault(run_count_key, 0)


@st.cache_data
def load_best_parameters_by_regime():
    """
    Loads optimized parameter presets if the regime optimization summary exists.
    """

    if not BEST_PARAMETERS_PATH.exists():
        return None

    return pd.read_csv(BEST_PARAMETERS_PATH)


def apply_regime_preset(row):
    """
    Applies one optimized regime preset to the dashboard controls.
    """

    st.session_state["price_process"] = "brownian"
    st.session_state["base_spread"] = float(row["base_spread"])
    st.session_state["inventory_skew"] = float(row["inventory_skew"])
    st.session_state["uncertainty_sensitivity"] = float(
        row["uncertainty_sensitivity"]
    )
    st.session_state["brownian_volatility"] = float(
        row["brownian_volatility"]
    )
    st.session_state["observation_noise_std"] = float(
        row["observation_noise_std"]
    )


def run_sample_simulation(
    strategy,
    base_spread,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
    uncertainty_sensitivity,
    volatility_window,
    price_process,
    random_walk_step_size,
    brownian_drift,
    brownian_volatility,
    dt,
    num_steps,
    seed,
):
    """
    Runs one simulation and records the true and observed midprice paths.
    """

    random.seed(seed)

    return run_simulation(
        base_spread=base_spread,
        num_steps=num_steps,
        strategy=strategy,
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
        record_history=True,
    )


def run_strategy_comparison(
    base_spread,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
    uncertainty_sensitivity,
    volatility_window,
    price_process,
    random_walk_step_size,
    brownian_drift,
    brownian_volatility,
    dt,
    num_steps,
    num_trials,
    seed,
):
    """
    Runs a multi-trial comparison across all strategies.
    """

    random.seed(seed)

    rows = []

    strategy_configs = [
        ("fixed", 0.0),
        ("inventory_aware", inventory_skew),
        ("uncertainty_aware", 0.0),
        ("inventory_and_uncertainty_aware", inventory_skew),
    ]

    for strategy_name, strategy_inventory_skew in strategy_configs:
        summary = run_trials_for_strategy(
            base_spread=base_spread,
            num_steps=num_steps,
            num_trials=num_trials,
            strategy=strategy_name,
            inventory_skew=strategy_inventory_skew,
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
            "strategy": strategy_name,
            "inventory_skew": strategy_inventory_skew,
            **summary,
        }

        rows.append(row)

    return pd.DataFrame(rows)


def run_preset_evaluation(
    preset_df,
    risk_penalty,
    volatility_window,
    random_walk_step_size,
    brownian_drift,
    dt,
    num_steps,
    num_trials,
    seed,
):
    """
    Evaluates each optimized regime preset on fresh simulations.
    """

    random.seed(seed)

    rows = []

    for _, row in preset_df.iterrows():
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
            price_process="brownian",
            random_walk_step_size=random_walk_step_size,
            brownian_drift=brownian_drift,
            brownian_volatility=float(row["brownian_volatility"]),
            dt=dt,
        )

        row_result = {
            "regime": row["regime"],
            "base_spread": float(row["base_spread"]),
            "inventory_skew": float(row["inventory_skew"]),
            "uncertainty_sensitivity": float(row["uncertainty_sensitivity"]),
            "brownian_volatility": float(row["brownian_volatility"]),
            "observation_noise_std": float(row["observation_noise_std"]),
            **summary,
        }

        rows.append(row_result)

    return pd.DataFrame(rows)


def create_price_path_chart(result):
    """
    Creates a price path chart with a zoomed y-axis and readable legend.

    The true midprice is shown as a solid dark blue line.
    The observed midprice is shown as a solid orange, partially transparent line.
    """

    true_prices = result["true_mid_price_history"]
    observed_prices = result["observed_mid_price_history"]

    path_df = pd.DataFrame(
        {
            "time_step": list(range(len(true_prices))),
            "True midprice": true_prices,
            "Observed midprice": observed_prices,
        }
    )

    long_df = path_df.melt(
        id_vars="time_step",
        value_vars=["True midprice", "Observed midprice"],
        var_name="series",
        value_name="midprice",
    )

    min_price = long_df["midprice"].min()
    max_price = long_df["midprice"].max()

    price_range = max_price - min_price
    padding = max(price_range * 0.10, 0.01)

    y_min = min_price - padding
    y_max = max_price + padding

    chart = (
        alt.Chart(long_df)
        .mark_line()
        .encode(
            x=alt.X(
                "time_step:Q",
                title="Time Step",
            ),
            y=alt.Y(
                "midprice:Q",
                title="Midprice",
                scale=alt.Scale(domain=[y_min, y_max], zero=False),
            ),
            color=alt.Color(
                "series:N",
                title="Line",
                scale=alt.Scale(
                    domain=["True midprice", "Observed midprice"],
                    range=["#003B73", "#F28E2B"],
                ),
                legend=alt.Legend(
                    orient="top",
                    title="Line",
                ),
            ),
            opacity=alt.Opacity(
                "series:N",
                scale=alt.Scale(
                    domain=["True midprice", "Observed midprice"],
                    range=[1.0, 0.55],
                ),
                legend=None,
            ),
            strokeWidth=alt.StrokeWidth(
                "series:N",
                scale=alt.Scale(
                    domain=["True midprice", "Observed midprice"],
                    range=[2.75, 2.25],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("time_step:Q", title="Time Step"),
                alt.Tooltip("series:N", title="Line"),
                alt.Tooltip("midprice:Q", title="Midprice", format=".4f"),
            ],
        )
        .properties(
            height=420,
            title="True vs Observed Midprice Path",
        )
        .interactive()
    )

    return chart

def display_saved_plot(filename, caption):
    """
    Displays a saved plot from results/plots if it exists.
    """

    plot_path = RESULTS_DIR / "plots" / filename

    if plot_path.exists():
        st.image(
            str(plot_path),
            caption=caption,
            use_container_width=True,
        )
    else:
        st.warning(f"Missing plot: {plot_path}")


def load_results_csv(filename):
    """
    Loads a CSV from the results directory.
    """

    csv_path = RESULTS_DIR / filename

    if not csv_path.exists():
        return None

    return pd.read_csv(csv_path)
st.title("Stochastic Market-Making Simulator")

st.write(
    """
    Interactive dashboard for testing market-making strategies under stochastic
    price dynamics, noisy observations, inventory risk, and uncertainty-aware
    spread adjustment.
    """
)


with st.sidebar:
    st.header("Optimized Presets")

    preset_df = load_best_parameters_by_regime()

    if preset_df is None:
        st.info(
            "No optimized preset file found. Run "
            "`python3 -m src.analyze_regime_results` first."
        )
    else:
        selected_regime = st.selectbox(
            "Regime preset",
            options=list(preset_df["regime"]),
        )

        selected_row = preset_df[
            preset_df["regime"] == selected_regime
        ].iloc[0]

        st.caption(
            f"Best preset for `{selected_regime}` based on "
            "risk-adjusted score."
        )

        st.dataframe(
            selected_row[
                [
                    "base_spread",
                    "inventory_skew",
                    "uncertainty_sensitivity",
                    "brownian_volatility",
                    "observation_noise_std",
                    "avg_risk_adjusted_score",
                    "avg_total_fills",
                ]
            ].to_frame("value"),
            use_container_width=True,
        )

        if st.button("Apply Optimized Preset"):
            apply_regime_preset(selected_row)
            st.success(f"Applied preset: {selected_regime}")

    st.divider()

    st.header("Simulation Settings")

    with st.expander("What do these settings mean?"):
        st.markdown(
            """
            **Base spread** controls the default width between the bid and ask
            quotes.

            **Inventory skew** controls how strongly the strategy shifts quotes to
            reduce inventory exposure.

            **Observation noise std** controls how inaccurate the bot's observed
            midprice is relative to the true midprice.

            **Risk penalty** controls how much the risk-adjusted score penalizes
            holding inventory.

            **Uncertainty sensitivity** controls how aggressively the strategy
            widens its spread when recent observed price changes become volatile.

            **Volatility window** controls how many recent observed price changes
            are used to estimate uncertainty.

            **Brownian volatility** controls how much the true simulated market
            midprice moves each step.
            """
        )

    seed = st.number_input(
        "Random seed",
        min_value=0,
        max_value=100000,
        step=1,
        key="seed",
    )

    price_process = st.selectbox(
        "Price process",
        options=["brownian", "random_walk"],
        key="price_process",
    )

    num_steps = st.slider(
        "Steps per simulation",
        min_value=100,
        max_value=5000,
        step=100,
        key="num_steps",
    )

    base_spread = st.slider(
        "Base spread",
        min_value=0.01,
        max_value=0.50,
        step=0.01,
        key="base_spread",
    )

    inventory_skew = st.slider(
        "Inventory skew",
        min_value=0.0,
        max_value=0.010,
        step=0.001,
        format="%.3f",
        key="inventory_skew",
    )

    observation_noise_std = st.slider(
        "Observation noise std",
        min_value=0.00,
        max_value=0.30,
        step=0.01,
        key="observation_noise_std",
    )

    risk_penalty = st.slider(
        "Risk penalty",
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        key="risk_penalty",
    )

    uncertainty_sensitivity = st.slider(
        "Uncertainty sensitivity",
        min_value=0.0,
        max_value=10.0,
        step=0.5,
        key="uncertainty_sensitivity",
    )

    volatility_window = st.slider(
        "Volatility window",
        min_value=5,
        max_value=200,
        step=5,
        key="volatility_window",
    )

    st.header("Price Process Parameters")

    random_walk_step_size = st.slider(
        "Random walk step size",
        min_value=0.001,
        max_value=0.10,
        step=0.001,
        format="%.3f",
        key="random_walk_step_size",
    )

    brownian_drift = st.slider(
        "Brownian drift",
        min_value=-0.05,
        max_value=0.05,
        step=0.005,
        format="%.3f",
        key="brownian_drift",
    )

    brownian_volatility = st.slider(
        "Brownian volatility",
        min_value=0.001,
        max_value=0.20,
        step=0.001,
        format="%.3f",
        key="brownian_volatility",
    )

    dt = st.slider(
        "dt",
        min_value=0.1,
        max_value=5.0,
        step=0.1,
        key="dt",
    )


tab_story, tab_sample, tab_compare, tab_presets, tab_results = st.tabs(
    [
        "Project Story",
        "Single Simulation",
        "Strategy Comparison",
        "Preset Evaluation",
        "Saved Results",
    ]
)

with tab_story:
    st.subheader("Project Story")

    st.markdown(
        """
        This project is a Python-based stochastic market-making simulator.

        The simulator studies how different quoting strategies perform when a
        market maker faces:

        - stochastic midprice movement
        - noisy fair-value observations
        - inventory risk
        - uncertain fill behavior
        - tradeoffs between liquidity provision and risk-adjusted performance

        A market maker repeatedly posts bid and ask quotes. If those quotes are
        filled, the strategy updates its cash, inventory, and mark-to-market
        PnL.
        """
    )

    st.markdown("### Core Simulation Loop")

    st.markdown(
        """
        At each time step:

        1. The true midprice moves according to a stochastic price process.
        2. The bot observes a noisy version of the true midprice.
        3. The selected strategy chooses a bid and ask quote.
        4. The simulator determines whether the bid or ask gets filled.
        5. Cash, inventory, PnL, and risk metrics are updated.

        The bot does **not** directly observe the true midprice. It quotes
        using the observed midprice, while fills and PnL are evaluated against
        the hidden true midprice.
        """
    )

    st.markdown("### Strategies")

    for strategy_name in STRATEGIES:
        st.markdown(f"**{strategy_label(strategy_name)}**")
        st.markdown(STRATEGY_DESCRIPTIONS[strategy_name])

    st.markdown("### Experiments Implemented")

    st.markdown(
        """
        The project includes several experiment types:

        - **Observation-noise experiments**: test how strategies behave as the
          bot's fair-value estimate becomes noisier.
        - **Volatility-regime experiments**: test how strategies behave as true
          Brownian market volatility changes.
        - **Parameter optimization**: grid-searches over spread, inventory
          skew, and uncertainty sensitivity.
        - **Regime-specific optimization**: finds the best parameters in
          calm/clean, volatile/clean, calm/noisy, and volatile/noisy regimes.
        - **Fill-constrained analysis**: studies what happens when the market
          maker is required to trade at least a minimum amount.
        """
    )

    st.markdown("### Main Findings So Far")

    st.markdown(
        """
        The experiments suggest several useful patterns:

        - Inventory skew is consistently important for controlling risk.
        - In clean regimes, tighter spreads and frequent trading can perform
          well.
        - In noisy regimes, uncertainty-aware spread widening becomes much more
          important.
        - Without fill constraints, the optimizer may choose to barely trade in
          noisy markets.
        - With fill constraints, the strategy must trade off liquidity provision
          against risk-adjusted performance.
        """
    )

    st.markdown("### Current Limitations")

    st.markdown(
        """
        This is still a simplified simulator. It does not yet include:

        - a real limit order book
        - queue position
        - real historical bid/ask quote data
        - exchange fees or rebates
        - latency
        - competing market makers
        - real execution constraints

        Because of this, the results should be interpreted as controlled
        simulation experiments, not as claims about live trading profitability.
        """
    )

with tab_sample:
    st.subheader("Single Simulation Path")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        strategy = st.selectbox(
            "Strategy",
            options=STRATEGIES,
            index=3,
            format_func=strategy_label,
        )

        st.info(STRATEGY_DESCRIPTIONS[strategy])
        
        run_button = st.button("Run Single Simulation")

    if run_button:
        st.session_state["single_simulation_run_count"] += 1
        run_seed = seed + st.session_state["single_simulation_run_count"]

        result = run_sample_simulation(
            strategy=strategy,
            base_spread=base_spread,
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
            num_steps=num_steps,
            seed=run_seed,
        )

        with col_left:
            st.metric("Final PnL", f"{result['final_pnl']:.4f}")
            st.metric(
                "Risk-adjusted score",
                f"{result['risk_adjusted_score']:.4f}",
            )
            st.metric("Final inventory", result["final_inventory"])
            st.metric("Total fills", result["total_fills"])
            st.metric(
                "Average effective spread",
                f"{result['average_effective_spread']:.4f}",
            )

        with col_right:
            price_path_chart = create_price_path_chart(result)
            st.altair_chart(price_path_chart, use_container_width=True)

            st.caption(
                "Dark blue = true hidden midprice. "
                "Transparent orange = noisy observed midprice used by the strategy."
            )

            st.info(
                "When the orange observed line moves away from the blue true line, "
                "the strategy is quoting using a noisy estimate of fair value. "
                "Large gaps can lead to worse fills or inventory risk."
            )

        st.subheader("Simulation Result")

        result_without_history = {
            key: value
            for key, value in result.items()
            if key
            not in [
                "true_mid_price_history",
                "observed_mid_price_history",
            ]
        }

        st.dataframe(
            pd.DataFrame([result_without_history]),
            use_container_width=True,
        )
    else:
        with col_right:
            st.info("Click **Run Single Simulation** to generate a price path.")


with tab_compare:
    st.subheader("Strategy Comparison")

    st.write(
        """
        This runs multiple trials for each strategy and compares average
        performance metrics.
        """
    )

    num_trials = st.slider(
        "Trials per strategy",
        min_value=10,
        max_value=1000,
        value=200,
        step=10,
    )

    compare_button = st.button("Run Strategy Comparison")

    if compare_button:
        st.session_state["strategy_comparison_run_count"] += 1
        run_seed = seed + st.session_state["strategy_comparison_run_count"]

        comparison_df = run_strategy_comparison(
            base_spread=base_spread,
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
            num_steps=num_steps,
            num_trials=num_trials,
            seed=run_seed,
        )

        display_comparison_df = comparison_df.copy()
        display_comparison_df.insert(
            0,
            "strategy_label",
            display_comparison_df["strategy"].map(strategy_label),
        )

        st.dataframe(
            display_comparison_df,
            use_container_width=True,
        )
        csv_data = comparison_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download comparison results as CSV",
            data=csv_data,
            file_name="strategy_comparison_results.csv",
            mime="text/csv",
        )

        chart_df = comparison_df.copy()
        chart_df["strategy"] = chart_df["strategy"].map(strategy_label)
        chart_df = chart_df.set_index("strategy")

        st.subheader("Average Risk-Adjusted Score")
        st.bar_chart(chart_df["avg_risk_adjusted_score"])

        st.subheader("Average PnL")
        st.bar_chart(chart_df["avg_pnl"])

        st.subheader("Average Absolute Inventory")
        st.bar_chart(chart_df["avg_abs_inventory"])

        st.subheader("Average Total Fills")
        st.bar_chart(chart_df["avg_total_fills"])

        st.subheader("Average Effective Spread")
        st.bar_chart(chart_df["avg_effective_spread"])

with tab_presets:
    st.subheader("Optimized Preset Evaluation")

    st.write(
        """
        This evaluates the optimized regime presets on fresh simulations.
        Each preset uses the best parameters found for its market regime.
        """
    )

    preset_df = load_best_parameters_by_regime()

    if preset_df is None:
        st.info(
            "No optimized preset file found. Run "
            "`python3 -m src.analyze_regime_results` first."
        )
    else:
        st.dataframe(
            preset_df[
                [
                    "regime",
                    "base_spread",
                    "inventory_skew",
                    "uncertainty_sensitivity",
                    "brownian_volatility",
                    "observation_noise_std",
                    "avg_risk_adjusted_score",
                    "avg_total_fills",
                ]
            ],
            use_container_width=True,
        )

        preset_num_trials = st.slider(
            "Trials per preset",
            min_value=10,
            max_value=1000,
            value=200,
            step=10,
        )

        preset_eval_button = st.button("Evaluate Optimized Presets")

        if preset_eval_button:
            st.session_state["preset_evaluation_run_count"] += 1
            run_seed = seed + st.session_state["preset_evaluation_run_count"]

            preset_eval_df = run_preset_evaluation(
                preset_df=preset_df,
                risk_penalty=risk_penalty,
                volatility_window=volatility_window,
                random_walk_step_size=random_walk_step_size,
                brownian_drift=brownian_drift,
                dt=dt,
                num_steps=num_steps,
                num_trials=preset_num_trials,
                seed=run_seed,
            )

            st.subheader("Fresh Evaluation Results")

            st.dataframe(
                preset_eval_df,
                use_container_width=True,
            )

            chart_df = preset_eval_df.set_index("regime")

            st.subheader("Risk-Adjusted Score by Preset")
            st.bar_chart(chart_df["avg_risk_adjusted_score"])

            st.subheader("Average PnL by Preset")
            st.bar_chart(chart_df["avg_pnl"])

            st.subheader("Average Inventory by Preset")
            st.bar_chart(chart_df["avg_abs_inventory"])

            st.subheader("Average Fills by Preset")
            st.bar_chart(chart_df["avg_total_fills"])

            csv_data = preset_eval_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download preset evaluation as CSV",
                data=csv_data,
                file_name="preset_evaluation_results.csv",
                mime="text/csv",
            )

with tab_results:
    st.subheader("Saved Results and Analysis")

    st.write(
        """
        This tab shows the saved outputs from the larger experiment scripts.
        Use it to inspect generated CSVs, plots, and the analysis summary
        without leaving the dashboard.
        """
    )

    analysis_path = RESULTS_DIR / "analysis_summary.md"

    st.markdown("### Analysis Summary")

    if analysis_path.exists():
        with st.expander("Open generated analysis summary", expanded=False):
            st.markdown(analysis_path.read_text())
    else:
        st.info(
            "No analysis summary found. Run "
            "`python3 -m src.analysis_report` first."
        )

    st.markdown("### Saved Plots")

    plot_options = {
        "Sample true vs observed midprice": (
            "sample_true_vs_observed_midprice.png",
            "Sample True vs Observed Midprice Path",
        ),
        "Average PnL by observation noise": (
            "avg_pnl_by_noise.png",
            "Average PnL by Observation Noise",
        ),
        "Risk-adjusted score by observation noise": (
            "risk_adjusted_score_by_noise.png",
            "Risk-Adjusted Score by Observation Noise",
        ),
        "Average PnL by volatility": (
            "avg_pnl_by_volatility.png",
            "Average PnL by Brownian Volatility",
        ),
        "Risk-adjusted score by volatility": (
            "risk_adjusted_score_by_volatility.png",
            "Risk-Adjusted Score by Brownian Volatility",
        ),
        "Estimated uncertainty by volatility": (
            "estimated_uncertainty_by_volatility.png",
            "Estimated Uncertainty by Brownian Volatility",
        ),
        "Top parameter sets": (
            "top_parameter_sets.png",
            "Top Parameter Sets by Risk-Adjusted Score",
        ),
        "Best score by regime": (
            "best_score_by_regime.png",
            "Best Risk-Adjusted Score by Regime",
        ),
        "Best uncertainty sensitivity by regime": (
            "best_uncertainty_sensitivity_by_regime.png",
            "Best Uncertainty Sensitivity by Regime",
        ),
        "Fill constraint tradeoff": (
            "fill_constraint_tradeoff.png",
            "Liquidity Constraint vs Risk-Adjusted Performance",
        ),
    }

    selected_plots = st.multiselect(
        "Choose plots to display",
        options=list(plot_options.keys()),
        default=[
            "Sample true vs observed midprice",
            "Risk-adjusted score by volatility",
            "Top parameter sets",
            "Fill constraint tradeoff",
        ],
    )

    for plot_name in selected_plots:
        filename, caption = plot_options[plot_name]
        display_saved_plot(filename, caption)

    st.markdown("### Saved CSV Results")

    csv_options = {
        "Observation-noise experiment": "experiment_results.csv",
        "Volatility-regime experiment": "volatility_experiment_results.csv",
        "Parameter optimization": "parameter_optimization_results.csv",
        "Regime parameter optimization": "regime_parameter_optimization_results.csv",
        "Best parameters by regime": "best_parameters_by_regime.csv",
        "Fill-constrained best parameters": "fill_constrained_best_parameters.csv",
        "Out-of-sample optimized parameter evaluation": "optimized_parameter_evaluation.csv",
    }

    selected_csv_label = st.selectbox(
        "Choose a results CSV",
        options=list(csv_options.keys()),
    )

    selected_csv_filename = csv_options[selected_csv_label]
    selected_csv_df = load_results_csv(selected_csv_filename)

    if selected_csv_df is None:
        st.info(f"No file found: `results/{selected_csv_filename}`")
    else:
        st.dataframe(
            selected_csv_df,
            use_container_width=True,
        )

        csv_data = selected_csv_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download selected CSV",
            data=csv_data,
            file_name=selected_csv_filename,
            mime="text/csv",
        )