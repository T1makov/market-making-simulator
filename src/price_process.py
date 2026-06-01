import math
import random


def random_walk_step(current_price, step_size=0.01):
    """
    Moves the price up or down by a fixed amount.

    This is the original simple price process we used.

    Example:
        current_price = 100
        step_size = 0.01

        next price is either 99.99 or 100.01
    """

    price_change = random.choice([-step_size, step_size])
    return current_price + price_change


def brownian_motion_step(current_price, drift=0.0, volatility=0.02, dt=1.0):
    """
    Updates the price using arithmetic Brownian motion.

    Formula:
        S_{t+dt} = S_t + drift * dt + volatility * sqrt(dt) * Z

    where:
        Z ~ Normal(0, 1)

    current_price:
        Current true midprice.

    drift:
        Average directional movement per unit time.

    volatility:
        Controls the size of random price movements.

    dt:
        Length of one simulation time step.
    """

    z = random.gauss(0.0, 1.0)

    price_change = drift * dt + volatility * math.sqrt(dt) * z

    new_price = current_price + price_change

    # Safety check: prices should not become negative.
    # With reasonable parameters near price 100, this should almost never matter.
    return max(0.01, new_price)


def next_price(
    current_price,
    price_process,
    random_walk_step_size=0.01,
    brownian_drift=0.0,
    brownian_volatility=0.02,
    dt=1.0,
):
    """
    Chooses which price process to use.

    price_process options:
        "random_walk"
        "brownian"
    """

    if price_process == "random_walk":
        return random_walk_step(
            current_price=current_price,
            step_size=random_walk_step_size,
        )

    if price_process == "brownian":
        return brownian_motion_step(
            current_price=current_price,
            drift=brownian_drift,
            volatility=brownian_volatility,
            dt=dt,
        )

    raise ValueError(f"Unknown price process: {price_process}")