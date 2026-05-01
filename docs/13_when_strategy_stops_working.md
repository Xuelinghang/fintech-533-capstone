# 13. When the Strategy Stops Working

A pair-trading strategy stops working when the **statistical relationship
between the two stocks breaks down**. This can happen for many reasons:
M&A activity, a major change in business mix, divergent management decisions,
a regulatory shock that hits one firm but not the other, or simply a structural
break in market regime. We do not need to identify the cause to react — we
need a clear rule for stepping back.

## 13.1 Per-pair stop-trading conditions

We **suspend new entries** on a pair if any one of the following is true:

1. Trailing 12-month return correlation falls below 0.30 for two consecutive
   monthly checks.
2. Trailing 12-month Engle-Granger cointegration p-value stays above 0.10
   for two consecutive monthly checks.
3. ADF p-value on the spread stays above 0.10 for two consecutive monthly
   checks.
4. Rolling 20-trade success rate drops below 23% (50% of the backtest 45.6%).
5. Rolling 20-trade stop-loss rate exceeds 55%.
6. Three or more stop-losses occur within any 10 consecutive trading days.

When suspended, we hold any existing open position to its natural exit (or to
its stop-loss), then close the pair until the screening evidence recovers.

## 13.2 Portfolio-level stop conditions

We pause **all new entries** across all pairs if:

1. Live drawdown exceeds -1.3% (1.5x the backtest max drawdown of -0.85%).
2. Two consecutive monthly Sharpe ratios fall below 0.5.
3. Aggregate stop-loss rate over the trailing 60 trades exceeds 55%.

This is a circuit breaker, not a kill switch. Open positions still exit
according to the standing rules; we simply do not put on new exposure until
the underlying signals look healthy again.

## 13.3 Resumption rule

A suspended pair is **eligible for re-screening** in the next monthly cycle.
To resume trading the pair, the same statistical thresholds must be met on
the trailing 12-month window: correlation of at least 0.50, cointegration
p-value of at most 0.10, and ADF p-value of at most 0.10 on the spread.

If a pair fails to re-qualify for two consecutive months, it is removed from
the trading roster and the corresponding industry returns to the candidate
pool for fresh selection.

## 13.4 What is NOT a stop signal

To avoid over-reacting, we deliberately do **not** treat any of the following
as automatic stop signals:

- A single losing trade, even a large one.
- A single month of negative P&L.
- An unusually wide Z-score on entry (this is the signal, not the failure).
- A change in the absolute price level of either leg.

Pair trading is a tail-heavy strategy: the success-trade payoff distribution
includes some that recover from very wide spreads. We need enough patience to
let those resolve, while still cutting genuinely broken pairs quickly. The
two-consecutive-month rule on statistical thresholds plus the trade-fate
circuit breakers are calibrated to that tradeoff.
