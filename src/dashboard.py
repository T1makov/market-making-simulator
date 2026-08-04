import random
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

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
        ("inventory_aware", 0.002),
        ("uncertainty_aware", 0.0),
        ("inventory_and_uncertainty_aware", 0.002),
    ]

    for strategy_name, inventory_skew in strategy_configs:
        summary = run_trials_for_strategy(
            base_spread=base_spread,
            num_steps=num_steps,
            num_trials=num_trials,
            strategy=strategy_name,
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
            "strategy": strategy_name,
            "inventory_skew": inventory_skew,
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
    st.header("Simulation Settings")

    seed = st.number_input(
        "Random seed",
        min_value=0,
        max_value=100000,
        value=42,
        step=1,
    )

    price_process = st.selectbox(
        "Price process",
        options=["brownian", "random_walk"],
        index=0,
    )

    num_steps = st.slider(
        "Steps per simulation",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
    )

    base_spread = st.slider(
        "Base spread",
        min_value=0.01,
        max_value=0.50,
        value=0.10,
        step=0.01,
    )

    observation_noise_std = st.slider(
        "Observation noise std",
        min_value=0.00,
        max_value=0.30,
        value=0.03,
        step=0.01,
    )

    risk_penalty = st.slider(
        "Risk penalty",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
    )

    uncertainty_sensitivity = st.slider(
        "Uncertainty sensitivity",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.5,
    )

    volatility_window = st.slider(
        "Volatility window",
        min_value=5,
        max_value=200,
        value=50,
        step=5,
    )

    st.header("Price Process Parameters")

    random_walk_step_size = st.slider(
        "Random walk step size",
        min_value=0.001,
        max_value=0.10,
        value=0.01,
        step=0.001,
        format="%.3f",
    )

    brownian_drift = st.slider(
        "Brownian drift",
        min_value=-0.05,
        max_value=0.05,
        value=0.0,
        step=0.005,
        format="%.3f",
    )

    brownian_volatility = st.slider(
        "Brownian volatility",
        min_value=0.001,
        max_value=0.20,
        value=0.02,
        step=0.001,
        format="%.3f",
    )

    dt = st.slider(
        "dt",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
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

        inventory_skew = st.slider(
            "Inventory skew",
            min_value=0.0,
            max_value=0.010,
            value=0.002,
            step=0.001,
            format="%.3f",
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