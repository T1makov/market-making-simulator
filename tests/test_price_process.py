import random

import pytest

from src.price_process import (
    random_walk_step,
    brownian_motion_step,
    next_price,
)


def test_random_walk_step_moves_by_exact_step_size():
    random.seed(42)

    current_price = 100.0
    step_size = 0.01

    new_price = random_walk_step(
        current_price=current_price,
        step_size=step_size,
    )

    price_change = new_price - current_price

    assert abs(price_change) == pytest.approx(step_size)


def test_random_walk_step_moves_either_up_or_down():
    random.seed(42)

    current_price = 100.0
    step_size = 0.01

    new_price = random_walk_step(
        current_price=current_price,
        step_size=step_size,
    )

    possible_prices = {
        current_price - step_size,
        current_price + step_size,
    }

    assert new_price in possible_prices


def test_brownian_motion_with_zero_volatility_and_zero_drift_stays_constant():
    random.seed(42)

    current_price = 100.0

    new_price = brownian_motion_step(
        current_price=current_price,
        drift=0.0,
        volatility=0.0,
        dt=1.0,
    )

    assert new_price == pytest.approx(current_price)


def test_brownian_motion_with_positive_drift_moves_by_drift_when_volatility_is_zero():
    random.seed(42)

    current_price = 100.0

    new_price = brownian_motion_step(
        current_price=current_price,
        drift=0.05,
        volatility=0.0,
        dt=1.0,
    )

    assert new_price == pytest.approx(100.05)


def test_brownian_motion_price_remains_positive():
    random.seed(42)

    new_price = brownian_motion_step(
        current_price=0.02,
        drift=-10.0,
        volatility=0.0,
        dt=1.0,
    )

    assert new_price > 0


def test_next_price_uses_random_walk():
    random.seed(42)

    current_price = 100.0
    step_size = 0.01

    new_price = next_price(
        current_price=current_price,
        price_process="random_walk",
        random_walk_step_size=step_size,
    )

    price_change = new_price - current_price

    assert abs(price_change) == pytest.approx(step_size)


def test_next_price_uses_brownian_motion():
    random.seed(42)

    current_price = 100.0

    new_price = next_price(
        current_price=current_price,
        price_process="brownian",
        brownian_drift=0.05,
        brownian_volatility=0.0,
        dt=1.0,
    )

    assert new_price == pytest.approx(100.05)


def test_unknown_price_process_raises_error():
    with pytest.raises(ValueError):
        next_price(
            current_price=100.0,
            price_process="bad_price_process",
        )