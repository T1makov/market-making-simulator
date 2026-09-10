import random

from .fill_model import fill_probability, orderbook_fill
from .market_quote import generate_market_quote, observed_mid_from_market_quote
from .sim_stats import estimate_uncertainty
from .strategies import choose_effective_spread, choose_quote_mid_price
from .price_process import next_price


def run_simulation(
    base_spread,
    num_steps,
    strategy,
    inventory_skew,
    observation_noise_std,
    risk_penalty,
    uncertainty_sensitivity,
    volatility_window,
    price_process="random_walk",
    random_walk_step_size=0.01,
    brownian_drift=0.0,
    brownian_volatility=0.02,
    dt=1.0,
    record_history=False,
    observation_model="gaussian_noise",
    fill_model_type="probability",
    base_market_spread=0.05,
    volatility_linked_width=0.5,
):
    """
    Runs one simulation of the market-making bot.

    observation_model:
        "gaussian_noise" (default) -- the bot observes the true midprice plus
        unbounded Gaussian noise, as before.

        "market_quote" -- the bot instead observes a point drawn uniformly
        from within a simulated public bid/ask market (see market_quote.py),
        which naturally bounds the observation error by the public spread.

    fill_model_type:
        "probability" (default) -- fills are decided by fill_probability(),
        a hand-tuned probability curve based on distance from the true
        midprice, as before.

        "orderbook" -- fills are instead decided by a deterministic crossing
        check (orderbook_fill()) against the same simulated public bid/ask
        market used by "market_quote".

    observation_model and fill_model_type are independent switches: any
    combination of the two is valid (e.g. "gaussian_noise" observation with
    "orderbook" fills).
    """

    initial_price = 100.00
    true_mid_price = initial_price

    cash = 0.0
    inventory = 0

    buy_fills = 0
    sell_fills = 0

    max_abs_inventory = 0
    sum_abs_inventory = 0.0
    sum_abs_observation_error = 0.0
    sum_effective_spread = 0.0
    sum_estimated_uncertainty = 0.0

    previous_observed_mid_price = None
    recent_observed_price_changes = []

    true_mid_price_history = []
    observed_mid_price_history = []

    for step in range(num_steps):
        # 1. The true market price moves randomly.
        true_mid_price = next_price(
            current_price=true_mid_price,
            price_process=price_process,
            random_walk_step_size=random_walk_step_size,
            brownian_drift=brownian_drift,
            brownian_volatility=brownian_volatility,
            dt=dt,
        )

        # 2. Optionally simulate a public bid/ask "market" around the true
        # midprice. This is generated whenever either the observation model
        # or the fill model needs it, using the volatility estimated from
        # observed price changes so far (i.e. not including this step's own
        # observation, which hasn't happened yet).
        market_bid = None
        market_ask = None

        if observation_model == "market_quote" or fill_model_type == "orderbook":
            recent_volatility_estimate = estimate_uncertainty(
                recent_observed_price_changes
            )

            market_bid, market_ask = generate_market_quote(
                true_mid_price=true_mid_price,
                base_market_spread=base_market_spread,
                volatility_linked_width=volatility_linked_width,
                recent_volatility_estimate=recent_volatility_estimate,
            )

        # 3. The bot observes the market.
        if observation_model == "gaussian_noise":
            observation_noise = random.gauss(0.0, observation_noise_std)
            observed_mid_price = true_mid_price + observation_noise
        elif observation_model == "market_quote":
            observed_mid_price = observed_mid_from_market_quote(
                market_bid, market_ask
            )
            observation_noise = observed_mid_price - true_mid_price
        else:
            raise ValueError(f"Unknown observation model: {observation_model}")

        if record_history:
            true_mid_price_history.append(true_mid_price)
            observed_mid_price_history.append(observed_mid_price)

        sum_abs_observation_error += abs(observation_noise)

        # 4. Update recent observed price changes.
        if previous_observed_mid_price is not None:
            observed_price_change = observed_mid_price - previous_observed_mid_price
            recent_observed_price_changes.append(observed_price_change)

            if len(recent_observed_price_changes) > volatility_window:
                recent_observed_price_changes.pop(0)

        previous_observed_mid_price = observed_mid_price

        # 5. Estimate uncertainty from recent observed price changes.
        estimated_uncertainty = estimate_uncertainty(recent_observed_price_changes)

        # 6. Choose the center of the bot's bid/ask quotes.
        quote_mid_price = choose_quote_mid_price(
            strategy=strategy,
            observed_mid_price=observed_mid_price,
            inventory=inventory,
            inventory_skew=inventory_skew,
        )

        # 7. Choose the spread.
        effective_spread = choose_effective_spread(
            strategy=strategy,
            base_spread=base_spread,
            estimated_uncertainty=estimated_uncertainty,
            uncertainty_sensitivity=uncertainty_sensitivity,
        )

        # 8. Place bid and ask around the chosen quote midpoint.
        bid_price = quote_mid_price - effective_spread / 2
        ask_price = quote_mid_price + effective_spread / 2

        # 9. Decide whether the bid and/or ask get filled.
        if fill_model_type == "probability":
            # Fills depend on the TRUE midprice, not the bot's observed price.
            bid_distance = true_mid_price - bid_price
            ask_distance = ask_price - true_mid_price

            prob_someone_sells_to_us = fill_probability(bid_distance)
            prob_someone_buys_from_us = fill_probability(ask_distance)

            bot_buys = random.random() < prob_someone_sells_to_us
            bot_sells = random.random() < prob_someone_buys_from_us
        elif fill_model_type == "orderbook":
            bot_buys, bot_sells = orderbook_fill(
                bot_bid_price=bid_price,
                bot_ask_price=ask_price,
                market_bid=market_bid,
                market_ask=market_ask,
            )
        else:
            raise ValueError(f"Unknown fill model type: {fill_model_type}")

        # 10. Someone sells to us, so we buy at our bid.
        if bot_buys:
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 11. Someone buys from us, so we sell at our ask.
        if bot_sells:
            inventory -= 1
            cash += ask_price
            sell_fills += 1

        # 12. Track risk and strategy behavior.
        max_abs_inventory = max(max_abs_inventory, abs(inventory))
        sum_abs_inventory += abs(inventory)
        sum_effective_spread += effective_spread
        sum_estimated_uncertainty += estimated_uncertainty

    final_pnl = cash + inventory * true_mid_price
    average_abs_inventory = sum_abs_inventory / num_steps
    average_abs_observation_error = sum_abs_observation_error / num_steps
    average_effective_spread = sum_effective_spread / num_steps
    average_estimated_uncertainty = sum_estimated_uncertainty / num_steps

    risk_adjusted_score = final_pnl - risk_penalty * average_abs_inventory

    result = {
        "strategy": strategy,
        "inventory_skew": inventory_skew,
        "observation_noise_std": observation_noise_std,
        "final_pnl": final_pnl,
        "risk_adjusted_score": risk_adjusted_score,
        "final_inventory": inventory,
        "abs_final_inventory": abs(inventory),
        "buy_fills": buy_fills,
        "sell_fills": sell_fills,
        "total_fills": buy_fills + sell_fills,
        "max_abs_inventory": max_abs_inventory,
        "average_abs_inventory": average_abs_inventory,
        "average_abs_observation_error": average_abs_observation_error,
        "average_effective_spread": average_effective_spread,
        "average_estimated_uncertainty": average_estimated_uncertainty,
    }

    if record_history:
        result["true_mid_price_history"] = true_mid_price_history
        result["observed_mid_price_history"] = observed_mid_price_history

    return result