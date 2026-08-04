import random
import sys
from pathlib import Path

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


tab_sample, tab_compare = st.tabs(
    [
        "Single Simulation",
        "Strategy Comparison",
    ]
)


with tab_sample:
    st.subheader("Single Simulation Path")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        strategy = st.selectbox(
            "Strategy",
            options=STRATEGIES,
            index=3,
        )

        run_button = st.button("Run Single Simulation")

    if run_button:
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
            seed=seed,
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

        path_df = pd.DataFrame(
            {
                "True midprice": result["true_mid_price_history"],
                "Observed midprice": result["observed_mid_price_history"],
            }
        )

        with col_right:
            st.line_chart(path_df)

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
            seed=seed,
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
        )

        chart_df = comparison_df.set_index("strategy")

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