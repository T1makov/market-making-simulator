import pytest

from src.strategies import choose_quote_mid_price, choose_effective_spread


def test_fixed_strategy_quotes_around_observed_midprice():
    quote_mid_price = choose_quote_mid_price(
        strategy="fixed",
        observed_mid_price=100.0,
        inventory=10,
        inventory_skew=0.002,
    )

    assert quote_mid_price == pytest.approx(100.0)


def test_positive_inventory_shifts_quote_midprice_downward():
    quote_mid_price = choose_quote_mid_price(
        strategy="inventory_aware",
        observed_mid_price=100.0,
        inventory=10,
        inventory_skew=0.002,
    )

    assert quote_mid_price == pytest.approx(99.98)


def test_negative_inventory_shifts_quote_midprice_upward():
    quote_mid_price = choose_quote_mid_price(
        strategy="inventory_aware",
        observed_mid_price=100.0,
        inventory=-10,
        inventory_skew=0.002,
    )

    assert quote_mid_price == pytest.approx(100.02)


def test_fixed_strategy_uses_base_spread():
    spread = choose_effective_spread(
        strategy="fixed",
        base_spread=0.10,
        estimated_uncertainty=0.05,
        uncertainty_sensitivity=3.0,
    )

    assert spread == pytest.approx(0.10)


def test_inventory_aware_strategy_uses_base_spread():
    spread = choose_effective_spread(
        strategy="inventory_aware",
        base_spread=0.10,
        estimated_uncertainty=0.05,
        uncertainty_sensitivity=3.0,
    )

    assert spread == pytest.approx(0.10)


def test_uncertainty_aware_strategy_widens_spread():
    spread = choose_effective_spread(
        strategy="uncertainty_aware",
        base_spread=0.10,
        estimated_uncertainty=0.05,
        uncertainty_sensitivity=3.0,
    )

    assert spread == pytest.approx(0.25)


def test_combined_strategy_widens_spread():
    spread = choose_effective_spread(
        strategy="inventory_and_uncertainty_aware",
        base_spread=0.10,
        estimated_uncertainty=0.05,
        uncertainty_sensitivity=3.0,
    )

    assert spread == pytest.approx(0.25)


def test_unknown_strategy_raises_error_for_quote_midprice():
    with pytest.raises(ValueError):
        choose_quote_mid_price(
            strategy="bad_strategy",
            observed_mid_price=100.0,
            inventory=0,
            inventory_skew=0.002,
        )


def test_unknown_strategy_raises_error_for_spread():
    with pytest.raises(ValueError):
        choose_effective_spread(
            strategy="bad_strategy",
            base_spread=0.10,
            estimated_uncertainty=0.05,
            uncertainty_sensitivity=3.0,
        )