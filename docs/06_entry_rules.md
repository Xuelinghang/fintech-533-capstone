# 6. Entry Rules

## 6.1 Z-score signal

Every trading day, we compute a rolling Z-score of the spread. Let `μ_t` be
the rolling mean of the spread over the last 60 trading days, and `σ_t` be
the rolling standard deviation over the same window. The Z-score is then
`Z_t = (spread_t − μ_t) / σ_t`.

## 6.2 Why a 60-day rolling window

A 60-day window is approximately three months of trading data. It is long
enough to give a stable estimate of the spread's local mean and standard
deviation, but short enough to adapt when market conditions change. A shorter
window (e.g. 20 days) was rejected because it produces a noisy Z-score that
generates whipsaw trades; a longer window (e.g. 252 days) was rejected because
it reacts too slowly to regime shifts.

## 6.3 Entry rule

When the Z-score exceeds **+2.0**, the spread is unusually wide and we enter a
**short spread** position: short stock A and go long stock B with a size
determined by the hedge ratio. When the Z-score falls below **−2.0**, the
spread is unusually narrow and we enter a **long spread** position: long stock
A and short stock B. Between −2.0 and +2.0 we take no new position.

Only one position per pair is open at a time. If the strategy already has an
open position on a pair, no new entry is taken for that pair until the existing
trade is closed.

## 6.4 Why ±2 standard deviations

The ±2 threshold filters out normal daily noise: under a roughly normal
distribution, only about 5% of daily Z-scores would be expected to exceed ±2,
so this is a meaningful deviation rather than an ordinary fluctuation. Trying
±1 would generate too many marginal trades; trying ±3 would generate almost
none. The 2-sigma threshold is the standard choice in academic and practitioner
references.

## 6.5 Sizing

Entries are sized to **$10,000 of notional on each leg**, scaled by the hedge
ratio. In other words, `shares_A = floor(10000 / price_A)` and
`shares_B = floor(10000 * |hedge_ratio| / price_B)`.

This produces a roughly dollar-neutral spread position. With a starting cash
of $100,000 and three concurrent pairs, peak exposure is bounded.
