import pytest

from src.fill_model import fill_probability


def test_fill_probability_is_between_zero_and_one():
    probability = fill_probability(0.05)

    assert probability >= 0
    assert probability <= 1


def test_fill_probability_decreases_as_distance_increases():
    close_probability = fill_probability(0.01)
    medium_probability = fill_probability(0.05)
    far_probability = fill_probability(0.10)

    assert close_probability > medium_probability
    assert medium_probability > far_probability


def test_negative_distance_is_treated_like_zero_distance():
    negative_distance_probability = fill_probability(-0.05)
    zero_distance_probability = fill_probability(0.0)

    assert negative_distance_probability == pytest.approx(zero_distance_probability)