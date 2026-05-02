# 5. Hedge Ratio and Spread Construction

## 5.1 Hedge ratio via OLS on log prices

For each pair (A, B), the hedge ratio is the slope of an ordinary least squares
regression of `log(price_A)` on `log(price_B)`, i.e.
`log(price_A) = α + β · log(price_B) + ε`.

`β` is the **hedge ratio**: how many units of stock B are needed to hedge
one unit of stock A in the constructed spread.

We use **log prices**, not raw prices, for two reasons:

1. Log returns are roughly symmetric and approximately constant in magnitude,
   so the regression is less sensitive to absolute price levels (KO at $80 vs.
   PEP at $145 in this sample).
2. Cointegration in log space corresponds to a stable price ratio, which is
   the economically meaningful relationship for two similar firms.

## 5.2 Spread definition

The spread on day *t* is defined as
`spread_t = log(price_A_t) − hedge_ratio · log(price_B_t)`.

If A and B are cointegrated, this spread is approximately stationary. The
backtest then standardizes it via a rolling Z-score (section 6).

## 5.3 Hedge ratios estimated for the 3 selected pairs

| Industry       | Pair       | Hedge Ratio (β) | Interpretation |
|----------------|------------|-----------------|----------------|
| Banks          | PNC / TFC  | 1.121 | 1 unit of log(PNC) hedged by 1.12 units of log(TFC) |
| Energy         | COP / OXY  | 0.634 | 1 unit of log(COP) hedged by 0.63 units of log(OXY) |
| Semiconductors | MU / LRCX  | 1.343 | 1 unit of log(MU) hedged by 1.34 units of log(LRCX) |

## 5.4 Hedge ratio in the trading book

When sizing positions, the hedge ratio determines the relative dollar exposure
on the two legs. We commit $10,000 of notional to stock A, which means
`shares_A = 10000 / price_A`. The opposite leg uses $10,000 scaled by
`|beta|`, so `shares_B = (10000 * |beta|) / price_B`.

This keeps the spread position approximately neutral with respect to the common
factor that drives both stocks. Both legs round to the nearest whole share; any
small remaining residual exposure is recorded in the ledger and absorbed into
the cash account.

![Three-panel chart for the PNC/TFC pair: log prices of both legs, the constructed spread with its 60-day rolling mean, and the rolling Z-score with horizontal threshold lines at ±0.5, ±2, and ±3](figures/pair_panel_pnc_tfc.svg)
