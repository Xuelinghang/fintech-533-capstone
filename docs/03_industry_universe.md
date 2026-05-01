# 3. Industry Universe and Pair Selection

## 3.1 Why these 10 industries

The 10 industries are chosen to cover a broad cross-section of the US equity
market based on the GICS sector framework (S&P/MSCI). Within each industry the
candidate pool is filled with large-cap, liquid names that share business model
and demand drivers, which is the precondition that makes a stable long-run
spread plausible.

## 3.2 Candidate stock universe (96 tickers)

| Industry       | Candidate stocks |
|----------------|------------------|
| Beverages      | KO, PEP, MNST, KDP, STZ, TAP, CELH, FIZZ |
| Payments       | V, MA, AXP, PYPL, FIS, FI, GPN, DFS |
| Energy         | XOM, CVX, COP, EOG, SLB, OXY, PSX, MPC, VLO, HAL |
| Semiconductors | NVDA, AMD, INTC, AVGO, QCOM, TXN, MU, AMAT, LRCX, KLAC |
| Airlines       | DAL, UAL, AAL, LUV, ALK, JBLU, CPA, RYAAY, SAVE, HA |
| Banks          | JPM, BAC, C, WFC, GS, MS, USB, PNC, TFC, BK |
| Retail         | WMT, TGT, COST, DG, DLTR, KR, HD, LOW, TJX, ROST |
| Autos          | TSLA, F, GM, RIVN, LCID, TM, HMC, STLA, NIO, XPEV |
| Health Care    | JNJ, PFE, MRK, ABBV, LLY, BMY, GILD, AMGN, REGN, BIIB |
| Communication  | GOOGL, META, NFLX, DIS, CMCSA, T, VZ, TMUS, SNAP, PINS |

Of these 96 candidates, **92** returned valid 3-year daily bars from IBKR.
4 tickers were excluded because the contract did not resolve on TWS during the
fetch window (`FI`, `DFS`, `SAVE`, `HA`).

## 3.3 Selection process

For every distinct pair within each industry, we compute four statistics:

1. Daily return correlation
2. Engle-Granger cointegration p-value (on log prices)
3. OLS hedge ratio (slope of `log(A) ~ log(B)`)
4. Augmented Dickey-Fuller p-value on the spread

We then rank candidates within each industry using a composite score and pick
the top pair. A pair is **selected** for trading only if it passes all three
statistical thresholds simultaneously: correlation of at least 0.50,
cointegration p-value of at most 0.10, and ADF p-value of at most 0.10 on
the constructed spread.

If a top-ranked pair fails the threshold, it is **rejected** and that industry
contributes no pair to the live strategy. This is intentional: we would rather
trade fewer pairs with strong statistical support than force a pair from every
industry.
