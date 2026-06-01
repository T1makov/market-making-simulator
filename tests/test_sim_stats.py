import pytest

from src.sim_stats import average, standard_deviation, estimate_uncertainty


def test_average():
    assert average([1, 2, 3, 4]) == pytest.approx(2.5)


def test_standard_deviation():
    values = [1, 2, 3]

    # Population standard deviation:
    # mean = 2
    # variance = ((1-2)^2 + (2-2)^2 + (3-2)^2) / 3 = 2/3
    # std = sqrt(2/3)
    assert standard_deviation(values) == pytest.approx((2 / 3) ** 0.5)


def test_standard_deviation_of_empty_list_is_zero():
    assert standard_deviation([]) == pytest.approx(0.0)


def test_estimate_uncertainty_is_zero_with_too_little_data():
    assert estimate_uncertainty([]) == pytest.approx(0.0)
    assert estimate_uncertainty([0.01]) == pytest.approx(0.0)


def test_estimate_uncertainty_is_higher_for_jumpier_price_changes():
    stable_changes = [0.01, 0.01, 0.01, 0.01]
    jumpy_changes = [0.10, -0.10, 0.15, -0.15]

    stable_uncertainty = estimate_uncertainty(stable_changes)
    jumpy_uncertainty = estimate_uncertainty(jumpy_changes)

    assert jumpy_uncertainty > stable_uncertainty