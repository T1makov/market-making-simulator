import pytest

from src.fill_model import fill_probability, orderbook_fill


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


def test_orderbook_fill_competitive_bid_uncompetitive_ask():
    bot_buys, bot_sells = orderbook_fill(
        bot_bid_price=100.00,
        bot_ask_price=100.10,
        market_bid=99.95,
        market_ask=100.05,
    )

    assert bot_buys is True
    assert bot_sells is False


def test_orderbook_fill_competitive_ask_uncompetitive_bid():
    bot_buys, bot_sells = orderbook_fill(
        bot_bid_price=99.90,
        bot_ask_price=100.00,
        market_bid=99.95,
        market_ask=100.05,
    )

    assert bot_buys is False
    assert bot_sells is True


def test_orderbook_fill_neither_side_is_competitive():
    # The bot quotes wider than the public market on both sides.
    bot_buys, bot_sells = orderbook_fill(
        bot_bid_price=99.90,
        bot_ask_price=100.10,
        market_bid=99.95,
        market_ask=100.05,
    )

    assert bot_buys is False
    assert bot_sells is False


def test_orderbook_fill_both_sides_are_competitive():
    # The bot quotes tighter than the public market on both sides.
    bot_buys, bot_sells = orderbook_fill(
        bot_bid_price=100.00,
        bot_ask_price=100.00,
        market_bid=99.95,
        market_ask=100.05,
    )

    assert bot_buys is True
    assert bot_sells is True


def test_orderbook_fill_exact_equality_counts_as_competitive():
    bot_buys, bot_sells = orderbook_fill(
        bot_bid_price=99.95,
        bot_ask_price=100.05,
        market_bid=99.95,
        market_ask=100.05,
    )

    assert bot_buys is True
    assert bot_sells is True