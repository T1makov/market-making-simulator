import random

import pytest

from src.market_quote import generate_market_quote, observed_mid_from_market_quote


def test_generate_market_quote_is_symmetric_around_true_mid_price():
    market_bid, market_ask = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.0,
    )

    assert market_bid == pytest.approx(99.95)
    assert market_ask == pytest.approx(100.05)


def test_generate_market_quote_with_zero_volatility_uses_base_spread():
    market_bid, market_ask = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.0,
    )

    assert (market_ask - market_bid) == pytest.approx(0.10)


def test_generate_market_quote_widens_with_volatility():
    calm_bid, calm_ask = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.0,
    )

    volatile_bid, volatile_ask = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.02,
    )

    calm_spread = calm_ask - calm_bid
    volatile_spread = volatile_ask - volatile_bid

    assert volatile_spread > calm_spread


def test_generate_market_quote_is_deterministic_given_same_inputs():
    quote_a = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.01,
    )
    quote_b = generate_market_quote(
        true_mid_price=100.0,
        base_market_spread=0.10,
        volatility_linked_width=5.0,
        recent_volatility_estimate=0.01,
    )

    assert quote_a == quote_b


def test_observed_mid_from_market_quote_is_within_bounds():
    random.seed(42)

    market_bid = 99.90
    market_ask = 100.10

    for _ in range(200):
        observed_mid_price = observed_mid_from_market_quote(market_bid, market_ask)

        assert market_bid <= observed_mid_price <= market_ask


def test_observed_mid_from_market_quote_with_zero_width_returns_that_price():
    random.seed(42)

    observed_mid_price = observed_mid_from_market_quote(100.0, 100.0)

    assert observed_mid_price == pytest.approx(100.0)
