def choose_quote_mid_price(strategy, observed_mid_price, inventory, inventory_skew):
    """
    Chooses the center point around which the bot places its bid and ask.

    Fixed strategy:
        Quote around the observed midprice.

    Inventory-aware strategy:
        Shift quotes depending on inventory.

    Uncertainty-aware strategies:
        Still quote around observed midprice, unless they are also inventory-aware.
    """

    if strategy == "fixed":
        return observed_mid_price

    if strategy == "inventory_aware":
        return observed_mid_price - inventory_skew * inventory

    if strategy == "uncertainty_aware":
        return observed_mid_price

    if strategy == "inventory_and_uncertainty_aware":
        return observed_mid_price - inventory_skew * inventory

    raise ValueError(f"Unknown strategy: {strategy}")


def choose_effective_spread(
    strategy,
    base_spread,
    estimated_uncertainty,
    uncertainty_sensitivity,
):
    """
    Chooses the spread the bot will quote.

    Fixed and inventory-aware strategies:
        Always use the same base spread.

    Uncertainty-aware strategies:
        Widen the spread when estimated uncertainty is high.
    """

    if strategy in ["fixed", "inventory_aware"]:
        return base_spread

    if strategy in ["uncertainty_aware", "inventory_and_uncertainty_aware"]:
        return base_spread + uncertainty_sensitivity * estimated_uncertainty

    raise ValueError(f"Unknown strategy: {strategy}")