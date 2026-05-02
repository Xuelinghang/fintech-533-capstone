# 1. Strategy Overview

This project implements a statistical pair-trading strategy across 10 GICS-style
US equity industries. The strategy looks for two stocks in the same industry whose
prices have moved together historically, identifies them with formal statistical
tests, and then trades the **spread** between them whenever it deviates far from
its historical mean.

The trading hypothesis is simple: when two economically similar stocks share a
**stable long-run relationship** (cointegration), short-term dislocations in
their relative price tend to revert. We enter when the spread is unusually wide,
exit when it reverts toward the mean, and stop out if the relationship appears
to break.

## Pipeline

The end-to-end workflow proceeds in seven stages:

1. Define ten industries and assemble a candidate stock pool of roughly ten
   stocks each, for a total of 96 tickers.
2. Pull three years of historical daily bars for each ticker from Interactive
   Brokers.
3. For every pair within an industry, compute four statistics: daily-return
   correlation, Engle-Granger cointegration p-value on log prices, OLS hedge
   ratio, and an ADF p-value on the constructed spread.
4. Rank the pairs and select the best one per industry, subject to the
   statistical thresholds.
5. Run the Z-score backtest (entry at ±2, success exit at |Z| < 0.5, stop-loss
   at |Z| > 3, timeout at 20 trading days).
6. Produce the blotter (`trades.csv`) and the daily ledger (`ledger.csv`).
7. Compute the performance metrics that drive the dashboards in the later
   sections.

## Backtest Window

- Start: 2023-05-02
- End: 2026-04-30
- Bars per stock: 752 daily bars
- Data source: Interactive Brokers (TWS API via `shinybroker`)

## High-Level Result

Out of 386 candidate pairs across 10 industries, **3 pairs** met the strict
selection thresholds (correlation ≥ 0.50, cointegration p ≤ 0.10, ADF p ≤ 0.10):

| Industry       | Selected Pair |
|----------------|---------------|
| Banks          | PNC / TFC     |
| Energy         | COP / OXY     |
| Semiconductors | MU / LRCX     |

The remaining 7 industries did not contain any pair that satisfied all three
statistical thresholds during this backtest window.

Aggregate backtest performance (3 selected pairs, equal-notional):

- 68 round-trip trades
- Sharpe ratio: 1.45
- Total return: 3.92%
- Max drawdown: -0.85%
- Success rate: 45.6%, stop-loss rate: 38.2%, timeout rate: 16.2%

![Aggregate equity curve and drawdown for the three selected pairs over the 2023–2026 backtest window](figures/equity_curve.svg)
