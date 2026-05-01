# 2. Market Phenomenon

## What we are trying to capture

This strategy attempts to profit from temporary relative mispricing between two
economically similar stocks in the same industry. If two stocks have historically
moved together and the spread between their prices is statistically stationary,
then large deviations from the historical average represent **temporary
dislocations** rather than a permanent change in fundamentals. The strategy
enters when the spread becomes unusually wide and exits when the spread reverts
toward its mean.

## Why this happens

Stocks within the same industry are exposed to the same macro factors:
sector-wide demand shocks, regulation, commodity inputs, the broader market.
When investors react to firm-specific news (an earnings surprise, an analyst
upgrade, an executive change), the relative prices of two otherwise similar
companies can drift apart even though their long-run cash flows remain coupled.
That short-term divergence is what creates the trading opportunity.

## What the strategy does NOT assume

- It does not assume the two stocks have the same price level.
- It does not assume the two stocks have the same volatility.
- It does not assume markets are inefficient on average.
- It only assumes that, conditional on having passed the cointegration test,
  the spread has a tendency to revert during the backtest horizon.

## Risk: when the assumption fails

A pair can stop being cointegrated. M&A activity, a major change in business
mix, a regulatory shock that hits one firm but not the other, or simply a
structural break in the relationship can make the spread non-stationary. When
that happens, the strategy will keep entering trades that no longer revert,
which is what the stop-loss and the live monitoring rules in section 16 are
designed to detect.
