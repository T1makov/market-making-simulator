import random

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