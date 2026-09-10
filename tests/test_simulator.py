import random

import pytest

from src.simulator import run_simulation


def test_run_simulation_returns_expected_keys():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="fixed",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
    )

    expected_keys = {
        "strategy",
        "inventory_skew",
        "observation_noise_std",
        "final_pnl",
        "risk_adjusted_score",
        "final_inventory",
        "abs_final_inventory",
        "buy_fills",
        "sell_fills",
        "total_fills",
        "max_abs_inventory",
        "average_abs_inventory",
        "average_abs_observation_error",
        "average_effective_spread",
        "average_estimated_uncertainty",
    }

    assert set(result.keys()) == expected_keys


def test_total_fills_equals_buy_fills_plus_sell_fills():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="fixed",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
    )

    assert result["total_fills"] == result["buy_fills"] + result["sell_fills"]


def test_abs_final_inventory_matches_final_inventory():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="inventory_aware",
        inventory_skew=0.002,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
    )

    assert result["abs_final_inventory"] == abs(result["final_inventory"])


def test_inventory_metrics_are_nonnegative():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="inventory_and_uncertainty_aware",
        inventory_skew=0.002,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
    )

    assert result["abs_final_inventory"] >= 0
    assert result["max_abs_inventory"] >= 0
    assert result["average_abs_inventory"] >= 0


def test_uncertainty_aware_strategy_has_effective_spread_at_least_base_spread():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="uncertainty_aware",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
    )

    assert result["average_effective_spread"] >= 0.10


def test_run_simulation_with_market_quote_and_orderbook_models_runs():
    random.seed(42)

    result = run_simulation(
        base_spread=0.10,
        num_steps=100,
        strategy="fixed",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
        observation_model="market_quote",
        fill_model_type="orderbook",
    )

    expected_keys = {
        "strategy",
        "inventory_skew",
        "observation_noise_std",
        "final_pnl",
        "risk_adjusted_score",
        "final_inventory",
        "abs_final_inventory",
        "buy_fills",
        "sell_fills",
        "total_fills",
        "max_abs_inventory",
        "average_abs_inventory",
        "average_abs_observation_error",
        "average_effective_spread",
        "average_estimated_uncertainty",
    }

    assert set(result.keys()) == expected_keys


def test_run_simulation_observation_model_and_fill_model_type_are_independent():
    random.seed(42)

    # gaussian_noise observation with orderbook fills.
    result_a = run_simulation(
        base_spread=0.10,
        num_steps=50,
        strategy="fixed",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
        observation_model="gaussian_noise",
        fill_model_type="orderbook",
    )

    # market_quote observation with probability fills.
    result_b = run_simulation(
        base_spread=0.10,
        num_steps=50,
        strategy="fixed",
        inventory_skew=0.0,
        observation_noise_std=0.03,
        risk_penalty=2.0,
        uncertainty_sensitivity=3.0,
        volatility_window=50,
        observation_model="market_quote",
        fill_model_type="probability",
    )

    assert result_a["total_fills"] >= 0
    assert result_b["total_fills"] >= 0


def test_run_simulation_raises_for_unknown_observation_model():
    with pytest.raises(ValueError):
        run_simulation(
            base_spread=0.10,
            num_steps=10,
            strategy="fixed",
            inventory_skew=0.0,
            observation_noise_std=0.03,
            risk_penalty=2.0,
            uncertainty_sensitivity=3.0,
            volatility_window=50,
            observation_model="bad_observation_model",
        )


def test_run_simulation_raises_for_unknown_fill_model_type():
    with pytest.raises(ValueError):
        run_simulation(
            base_spread=0.10,
            num_steps=10,
            strategy="fixed",
            inventory_skew=0.0,
            observation_noise_std=0.03,
            risk_penalty=2.0,
            uncertainty_sensitivity=3.0,
            volatility_window=50,
            fill_model_type="bad_fill_model",
        )