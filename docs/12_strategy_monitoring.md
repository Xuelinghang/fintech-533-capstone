# 12. Strategy Monitoring Going Forward

The backtest gives us a distribution of expected outcomes. In live trading, we
compare realized behavior against that distribution and ask: **is the strategy
still doing what the backtest said it would do?**

## 12.1 What we monitor (and how often)

Monthly cadence, computed from the production blotter:

| Metric                 | Backtest value | Watch band               |
|------------------------|---------------:|--------------------------|
| Sharpe (ann., trailing 6 months) | 1.45 | flag if < 0.5 for 2 consecutive months |
| Average return per trade | 0.85% | flag if rolling 20-trade mean < 0 |
| Success rate           | 45.6%         | flag if rolling 20-trade rate < 30% |
| Stop-loss rate         | 38.2%         | flag if rolling 20-trade rate > 55% |
| Timeout rate           | 16.2%         | flag if rolling 20-trade rate > 35% |
| Average holding days   | 9.07          | flag if rolling 20-trade mean > 18 days |
| Max drawdown           | -0.85%        | flag if live drawdown < -1.3% (1.5x) |

Daily cadence, computed from the production ledger:

- Live drawdown vs. running peak.
- Open-position count vs. expected (one per pair).
- Spread Z-score per pair (so we can see entries forming).

## 12.2 Per-pair sanity checks

Every weekend (or on the last day of each month), we re-run the screening
calculations on the trailing 12 months of data **for each pair currently in
production**:

- The rolling daily-return correlation, with a warning if it falls below 0.30.
- The rolling Engle-Granger cointegration p-value, with a warning if it stays
  above 0.10 for two consecutive monthly checks.
- The ADF p-value on the spread, with a warning if it stays above 0.10 for two
  consecutive monthly checks.

These are the same tests used at selection time, applied to the most recent
window. If a pair's underlying statistical evidence has deteriorated, the live
trade behavior may not have caught up yet — but the next few trades almost
certainly will, so we want the early signal.

## 12.3 Reporting

A weekly status note records:

1. Current open positions (pair, direction, days held, current Z-score, MTM
   P&L).
2. Trades closed since the previous report and their fates.
3. Trailing-month Sharpe, success rate, stop-loss rate, timeout rate.
4. Drawdown vs. peak.
5. Per-pair trailing 12-month correlation, cointegration p-value, ADF p-value.
6. Any flags raised by the watch bands above.

This is the input that feeds the section 16 stop-trading decision.

![Rolling 20-trade diagnostics over the backtest: trailing Sharpe, success rate, and stop-loss rate, each annotated with the watch-band threshold from the monitoring framework](figures/rolling_metrics.svg)
