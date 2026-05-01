# 4. Statistical Tests

Three statistical tests are run on every candidate pair. The tests are
deliberately layered so that a passing pair shows evidence of (a) a contemporaneous
relationship, (b) a stable long-run relationship, and (c) mean-reverting
short-term deviations.

## 4.1 Daily return correlation (quick screen)

Pairs trading requires both stocks to respond to similar shocks; otherwise the
spread is just two unrelated random walks. A simple Pearson correlation on
daily returns is fast and gives us a first cut. We require a correlation of at
least **0.50**.

Correlation alone is **not sufficient**: two stocks can be highly correlated in
returns while having a non-stationary spread (a permanently widening or
narrowing relationship). That is why the next two tests matter more.

## 4.2 Engle-Granger cointegration test

We run `statsmodels.tsa.stattools.coint` on the **log prices** of each pair.
The null hypothesis is "no cointegration." A small p-value indicates that the
two log-price series share a stable long-run relationship - the residual from
their linear combination is stationary.

Selection rule: cointegration p-value of at most **0.10**.

The plan ideally wants p < 0.05. We loosen to 0.10 because 0.05 leaves too few
qualifying pairs in this 3-year window; 0.10 gives a slightly noisier but still
defensible signal.

## 4.3 ADF test on the spread

After computing the spread (section 5), we run an Augmented Dickey-Fuller test
on the spread itself. The null is "spread has a unit root" (non-stationary,
random walk). A small p-value means the spread is stationary - exactly the
condition the strategy needs.

Selection rule: ADF p-value of at most **0.10**.

In practice, ADF and cointegration tend to agree. The combined test acts as a
cross-check.

## 4.4 Combined ranking score

For pairs that pass all three filters, we compute a composite score
`score = z(correlation) − z(cointegration_p) − z(ADF_p)`, where `z(·)`
standardizes each statistic across all candidate pairs. Higher
correlation pushes the score up, lower p-values push the score up. The top-
scoring pair within each industry is the one we report.

## 4.5 Why we do not use only correlation

A pair like `V / MA` has a daily-return correlation of 0.85 - extremely high -
but its cointegration p-value is 0.24, so it does not pass the cointegration
test. The two stocks move together day-to-day, but their long-run spread is
not stationary in the test window. Trading the spread of such a pair would be
exposed to permanent drift, which is exactly what the cointegration test is
designed to filter out.
