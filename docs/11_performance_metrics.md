# 11. Performance Metrics

All numbers below are computed by `src/metrics.py` from `trades.csv` and
`ledger.csv` over the full backtest window (2023-05-02 to 2026-04-30).

## 11.1 Selection results (10 rows, one per industry)

| Industry       | Pair         | Correlation | Coint p-value | ADF p-value | Hedge Ratio | Decision |
|----------------|--------------|------------:|--------------:|------------:|------------:|----------|
| Airlines       | AAL / JBLU   | 0.560       | 0.136         | 0.046       | 0.529       | rejected |
| Autos          | F / GM       | 0.671       | 0.211         | 0.080       | 0.091       | rejected |
| Banks          | PNC / TFC    | 0.821       | 0.0001        | 0.00001     | 1.121       | **selected** |
| Beverages      | PEP / STZ    | 0.428       | 0.163         | 0.057       | 0.321       | rejected |
| Communication  | META / NFLX  | 0.304       | 0.063         | 0.018       | 0.800       | rejected |
| Energy         | COP / OXY    | 0.798       | 0.018         | 0.004       | 0.634       | **selected** |
| HealthCare     | PFE / BIIB   | 0.442       | 0.065         | 0.018       | 0.436       | rejected |
| Payments       | V / MA       | 0.851       | 0.238         | 0.094       | 1.027       | rejected |
| Retail         | DG / DLTR    | 0.494       | 0.001         | 0.0002      | 0.979       | rejected |
| Semiconductors | MU / LRCX    | 0.742       | 0.012         | 0.002       | 1.343       | **selected** |

Three industries pass all three filters. Notable rejections:
- **V / MA** has the highest correlation in the table (0.85) but fails the
  cointegration test (p = 0.24). High correlation alone is not enough.
- **DG / DLTR** has very strong cointegration evidence but borderline
  correlation (0.49 < 0.50). We keep the threshold strict to avoid trading
  pairs that are statistically related but practically unstable.

## 11.2 Aggregate trade statistics (3 selected pairs)

| Metric                      | Value     |
|-----------------------------|-----------|
| Number of trades            | 68        |
| Average return per trade    | 0.85%     |
| Average holding period      | 9.07 days |
| Success rate                | 45.6%     |
| Stop-loss rate              | 38.2%     |
| Timeout rate                | 16.2%     |
| End-of-backtest close rate  | 0.0%      |

## 11.3 Aggregate portfolio statistics (3 selected pairs)

| Metric                | Value     |
|-----------------------|-----------|
| Sharpe ratio (ann.)   | 1.45      |
| Annualized return     | 1.30%     |
| Annualized volatility | 0.89%     |
| Total return          | 3.92%     |
| Max drawdown          | -0.85%    |

## 11.4 Per-pair contribution

| Industry       | Pair       | Trades | Success | Stop-loss | Timeout |
|----------------|------------|-------:|--------:|----------:|--------:|
| Banks          | PNC / TFC  | 20     | 50.0%   | 30.0%     | 20.0%   |
| Energy         | COP / OXY  | 22     | 50.0%   | 27.3%     | 22.7%   |
| Semiconductors | MU / LRCX  | 26     | 38.5%   | 53.8%     | 7.7%    |

Banks and Energy contribute clean, balanced profiles. Semiconductors is the
highest-frequency, lowest-quality pair in this run - 53.8% of MU / LRCX trades
hit the stop-loss, and this is the pair to watch most closely going forward.

## 11.5 Interpreting the numbers

- **Sharpe of 1.45** is solid for a market-neutral pair-trading strategy. The
  realized volatility (0.89% ann.) is low because each pair is dollar-neutral
  and the three pairs are largely uncorrelated.
- **Total return of 3.92%** over 3 years is modest in absolute terms, but the
  capital efficiency (low gross book size: $30k notional out of $300k cash)
  means the per-dollar-deployed return is meaningfully higher.
- **Max drawdown of -0.85%** is small. With three uncorrelated pairs, even
  simultaneous adverse moves rarely accumulate.
- The ratio of **stop-loss to success (0.84:1)** is on the higher side and is
  the main quality concern. The live monitor described in section 16 is set
  up specifically to catch a deterioration in this ratio.

![Histogram of per-trade returns stacked by fate, showing the asymmetry between winning and losing trade magnitudes](figures/return_distribution.svg)

![Underwater drawdown curve over the full 2023–2026 backtest, with maximum drawdown labeled](figures/drawdown_underwater.svg)
