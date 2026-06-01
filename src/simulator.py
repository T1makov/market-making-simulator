import random

from .fill_model import fill_probability
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
):
    """
    Runs one simulation of the market-making bot.
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
        # 2. The bot observes the true price with noise.
        observation_noise = random.gauss(0.0, observation_noise_std)
        observed_mid_price = true_mid_price + observation_noise

        if record_history:
            true_mid_price_history.append(true_mid_price)
            observed_mid_price_history.append(observed_mid_price)

        sum_abs_observation_error += abs(observation_noise)

        # 3. Update recent observed price changes.
        if previous_observed_mid_price is not None:
            observed_price_change = observed_mid_price - previous_observed_mid_price
            recent_observed_price_changes.append(observed_price_change)

            if len(recent_observed_price_changes) > volatility_window:
                recent_observed_price_changes.pop(0)

        previous_observed_mid_price = observed_mid_price

        # 4. Estimate uncertainty from recent observed price changes.
        estimated_uncertainty = estimate_uncertainty(recent_observed_price_changes)

        # 5. Choose the center of the bot's bid/ask quotes.
        quote_mid_price = choose_quote_mid_price(
            strategy=strategy,
            observed_mid_price=observed_mid_price,
            inventory=inventory,
            inventory_skew=inventory_skew,
        )

        # 6. Choose the spread.
        effective_spread = choose_effective_spread(
            strategy=strategy,
            base_spread=base_spread,
            estimated_uncertainty=estimated_uncertainty,
            uncertainty_sensitivity=uncertainty_sensitivity,
        )

        # 7. Place bid and ask around the chosen quote midpoint.
        bid_price = quote_mid_price - effective_spread / 2
        ask_price = quote_mid_price + effective_spread / 2

        # 8. Fills depend on the TRUE midprice, not the bot's observed price.
        bid_distance = true_mid_price - bid_price
        ask_distance = ask_price - true_mid_price

        prob_someone_sells_to_us = fill_probability(bid_distance)
        prob_someone_buys_from_us = fill_probability(ask_distance)

        # 9. Someone sells to us, so we buy at our bid.
        if random.random() < prob_someone_sells_to_us:
            inventory += 1
            cash -= bid_price
            buy_fills += 1

        # 10. Someone buys from us, so we sell at our ask.
        if random.random() < prob_someone_buys_from_us:
            inventory -= 1
            cash += ask_price
            sell_fills += 1

        # 11. Track risk and strategy behavior.
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