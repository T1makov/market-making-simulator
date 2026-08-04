# Market-Making Simulator Analysis Summary

This report is automatically generated from the simulator's result CSVs. It summarizes the main findings from the observation-noise, volatility-regime, parameter-optimization, regime-optimization, and fill-constrained optimization experiments.

## Observation-Noise Experiment

This experiment varies the noise in the bot's observed midprice while keeping the market model fixed. It tests how strategies behave when fair-value observations become less reliable.

Best strategy by observation-noise level:

|   observation_noise_std | strategy                        |   avg_pnl |   avg_risk_adjusted_score |   avg_abs_inventory |   avg_total_fills |   avg_effective_spread |
|------------------------:|:--------------------------------|----------:|--------------------------:|--------------------:|------------------:|-----------------------:|
|                    0    | inventory_aware                 |   11.0686 |                    5.99   |              2.5393 |           223.382 |                 0.1    |
|                    0.01 | inventory_aware                 |   10.8364 |                    5.7704 |              2.533  |           227.91  |                 0.1    |
|                    0.03 | inventory_aware                 |    8.4019 |                    2.9183 |              2.7418 |           256.58  |                 0.1    |
|                    0.05 | inventory_and_uncertainty_aware |    4.5182 |                   -0.2066 |              2.3624 |            42.576 |                 0.3179 |
|                    0.1  | inventory_and_uncertainty_aware |    1.8034 |                   -2.5942 |              2.1988 |            21.57  |                 0.5235 |
|                    0.2  | inventory_and_uncertainty_aware |    0.1276 |                   -3.6499 |              1.8888 |            14.512 |                 0.9416 |

Key observation:

- At low observation noise, the best strategy is `inventory_aware`.
- At high observation noise, the best strategy is `inventory_and_uncertainty_aware`.
- This shows how noisy fair-value estimates can change the preferred quoting strategy.

## Volatility-Regime Experiment

This experiment varies the true Brownian volatility of the market while keeping observation noise fixed. It tests whether strategies are robust when the actual midprice moves more aggressively.

Best strategy by Brownian volatility level:

|   brownian_volatility | strategy        |   avg_pnl |   avg_risk_adjusted_score |   avg_abs_inventory |   avg_total_fills |   avg_effective_spread |   avg_estimated_uncertainty |
|----------------------:|:----------------|----------:|--------------------------:|--------------------:|------------------:|-----------------------:|----------------------------:|
|                 0.005 | inventory_aware |    8.5554 |                    3.0736 |              2.7409 |           255.864 |                    0.1 |                      0.0423 |
|                 0.01  | inventory_aware |    8.5473 |                    2.9317 |              2.8078 |           256.526 |                    0.1 |                      0.0431 |
|                 0.02  | inventory_aware |    8.5766 |                    3.0104 |              2.7831 |           256.372 |                    0.1 |                      0.0464 |
|                 0.05  | inventory_aware |    8.9549 |                    3.442  |              2.7564 |           255.072 |                    0.1 |                      0.0646 |
|                 0.1   | inventory_aware |    9.0453 |                    3.5125 |              2.7664 |           256.328 |                    0.1 |                      0.1068 |

Key observation:

- The volatility experiment checks whether the uncertainty estimator responds as true market volatility increases.
- Comparing this with the observation-noise experiment helps separate true market movement from noisy fair-value estimation.

## Parameter Optimization

This experiment grid-searches over base spread, inventory skew, and uncertainty sensitivity for the combined strategy.

Top 10 parameter sets:

|   base_spread |   inventory_skew |   uncertainty_sensitivity |   avg_pnl |   std_pnl |   avg_risk_adjusted_score |   avg_abs_inventory |   avg_total_fills |   avg_effective_spread |
|--------------:|-----------------:|--------------------------:|----------:|----------:|--------------------------:|--------------------:|------------------:|-----------------------:|
|          0.15 |            0.004 |                         0 |    8.9078 |    1.6636 |                    5.0879 |              1.9099 |           162.89  |                 0.15   |
|          0.05 |            0.004 |                         2 |    8.9845 |    1.8981 |                    5.0513 |              1.9666 |           174.6   |                 0.1429 |
|          0.1  |            0.004 |                         1 |    8.8924 |    1.7988 |                    5.0283 |              1.9321 |           165.875 |                 0.1465 |
|          0.1  |            0.004 |                         2 |    8.1866 |    1.6938 |                    4.4608 |              1.8629 |           106.26  |                 0.1928 |
|          0.1  |            0.004 |                         0 |    8.3967 |    1.8292 |                    4.4426 |              1.9771 |           259.64  |                 0.1    |
|          0.15 |            0.004 |                         1 |    8.0716 |    1.6934 |                    4.3408 |              1.8654 |           103.165 |                 0.1963 |
|          0.05 |            0.004 |                         3 |    8.0705 |    1.8283 |                    4.3139 |              1.8783 |           112.305 |                 0.1888 |
|          0.2  |            0.004 |                         0 |    7.9108 |    1.7401 |                    4.2583 |              1.8263 |            99.7   |                 0.2    |
|          0.05 |            0.004 |                         1 |    8.2206 |    1.7196 |                    4.2461 |              1.9872 |           264.37  |                 0.0963 |
|          0.1  |            0.002 |                         1 |    9.2235 |    2.1815 |                    3.9294 |              2.647  |           166.405 |                 0.1463 |

Best parameter set:

- `base_spread = 0.15`
- `inventory_skew = 0.004`
- `uncertainty_sensitivity = 0.0`
- average risk-adjusted score: `5.0879`

## Regime-Specific Parameter Optimization

This experiment optimizes parameters separately across four market regimes: calm/clean, volatile/clean, calm/noisy, and volatile/noisy.

Best parameter set by regime:

| regime         |   brownian_volatility |   observation_noise_std |   base_spread |   inventory_skew |   uncertainty_sensitivity |   avg_pnl |   avg_risk_adjusted_score |   avg_abs_inventory |   avg_total_fills |   avg_effective_spread |
|:---------------|----------------------:|------------------------:|--------------:|-----------------:|--------------------------:|----------:|--------------------------:|--------------------:|------------------:|-----------------------:|
| calm_clean     |                  0.01 |                    0.01 |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| volatile_clean |                  0.05 |                    0.01 |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| calm_noisy     |                  0.01 |                    0.1  |          0.2  |            0.004 |                         5 |    0.1162 |                   -0.7576 |              0.4369 |              0.96 |                 0.9004 |
| volatile_noisy |                  0.05 |                    0.1  |          0.2  |            0.004 |                         5 |    0.1747 |                   -0.7643 |              0.4695 |              0.78 |                 0.9412 |

Key observation:

- Clean regimes tend to support tighter spreads and frequent trading.
- Noisy regimes tend to favor wider spreads and larger uncertainty sensitivity.
- This suggests that uncertainty-aware spread widening is most useful when fair-value observations are unreliable.

## Fill-Constrained Optimization

The unconstrained optimizer can choose very wide spreads in noisy regimes, causing the strategy to barely trade. This analysis adds minimum average fill requirements to study the tradeoff between liquidity provision and risk-adjusted performance.

Best feasible parameter sets under fill constraints:

| regime         |   minimum_avg_fills | feasible   |   base_spread |   inventory_skew |   uncertainty_sensitivity |   avg_pnl |   avg_risk_adjusted_score |   avg_abs_inventory |   avg_total_fills |   avg_effective_spread |
|:---------------|--------------------:|:-----------|--------------:|-----------------:|--------------------------:|----------:|--------------------------:|--------------------:|------------------:|-----------------------:|
| calm_clean     |                   1 | True       |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| calm_clean     |                  10 | True       |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| calm_clean     |                  25 | True       |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| calm_clean     |                  50 | True       |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| calm_clean     |                 100 | True       |          0.1  |            0.004 |                         0 |   10.7237 |                    7.0893 |              1.8172 |            230.81 |                 0.1    |
| volatile_clean |                   1 | True       |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| volatile_clean |                  10 | True       |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| volatile_clean |                  25 | True       |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| volatile_clean |                  50 | True       |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| volatile_clean |                 100 | True       |          0.05 |            0.004 |                         1 |   10.9396 |                    7.3233 |              1.8081 |            228.39 |                 0.101  |
| calm_noisy     |                   1 | True       |          0.2  |            0.002 |                         5 |    0.165  |                   -0.9732 |              0.5691 |              1.06 |                 0.9021 |
| calm_noisy     |                  10 | True       |          0.1  |            0.004 |                         3 |    1.7846 |                   -1.4083 |              1.5964 |             22.26 |                 0.5213 |
| calm_noisy     |                  25 | True       |          0.15 |            0.004 |                         2 |    2.4564 |                   -1.5685 |              2.0125 |             44.04 |                 0.4294 |
| calm_noisy     |                  50 | True       |          0.2  |            0.004 |                         1 |    2.7612 |                   -1.6587 |              2.21   |             84.06 |                 0.34   |
| calm_noisy     |                 100 | True       |          0.15 |            0.004 |                         1 |    2.4482 |                   -2.1609 |              2.3046 |            116.36 |                 0.2903 |
| volatile_noisy |                   1 | True       |          0.15 |            0     |                         5 |    0.3855 |                   -0.9315 |              0.6585 |              1.54 |                 0.8884 |
| volatile_noisy |                  10 | True       |          0.1  |            0.004 |                         2 |    3.0623 |                   -1.0959 |              2.0791 |             57.56 |                 0.3975 |
| volatile_noisy |                  25 | True       |          0.1  |            0.004 |                         2 |    3.0623 |                   -1.0959 |              2.0791 |             57.56 |                 0.3975 |
| volatile_noisy |                  50 | True       |          0.1  |            0.004 |                         2 |    3.0623 |                   -1.0959 |              2.0791 |             57.56 |                 0.3975 |
| volatile_noisy |                 100 | True       |          0.15 |            0.004 |                         1 |    3.1566 |                   -1.5079 |              2.3323 |            108.45 |                 0.2985 |

Key observation:

- In clean regimes, the fill constraint has little effect because the best strategies already trade frequently.
- In noisy regimes, requiring more fills forces the strategy to quote more aggressively, which usually lowers risk-adjusted performance.
- This exposes a liquidity-versus-risk tradeoff: market makers may need to accept worse risk-adjusted performance if they are required to provide liquidity.

## Overall Project Takeaway

The simulator shows that market-making performance depends strongly on the quality of the fair-value signal and the market regime. In clean regimes, the strategy can trade frequently while controlling inventory with inventory-aware skew. In noisy regimes, uncertainty-aware spread widening becomes much more important, but it can also reduce fill frequency sharply. When minimum fill constraints are introduced, the strategy must trade off liquidity provision against risk-adjusted performance.
