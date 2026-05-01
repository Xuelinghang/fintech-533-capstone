# 9. Backtest Design

## 9.1 Architecture

The backtest is **event-driven** and runs day by day. For each pair and each
day, the engine performs three steps in order:

1. **Manage any open trade.** Read the current Z-score and close the position
   if it has reverted (success), gone too far against us (stop-loss), or aged
   out (timeout). On the final day of the backtest, any still-open trade is
   closed at that day's price.
2. **Check for an entry.** If no trade is open and the Z-score is beyond ±2.0,
   open a long-spread or short-spread position accordingly.
3. **Record a ledger row** capturing the date, prices, positions, cash,
   portfolio value, current Z-score, and any open trade identifier.

Exits are evaluated before entries on the same day, so a trade can only be
opened on a day when no other position is active for that pair.

## 9.2 Inputs

- Daily close prices for the 92 successfully-fetched tickers.
- Date-aligned price panel via inner-join on dates.
- Hedge ratio per pair from OLS on log prices.
- The 3 selected pairs from the screening step.

## 9.3 Capital and sizing

- Starting cash per pair: **$100,000** (each pair has an independent ledger
  account in this implementation).
- Notional per leg per trade: **$10,000**, scaled by hedge ratio on stock B.
- Cash account: tracks proceeds and outlays, and pays the residual P&L on
  close.
- No margin, no commissions, no slippage are modelled. These are conservative
  simplifications - in production they would be added at the trade level.

## 9.4 Outputs

The backtest produces three artifacts in `outputs/`:

1. `trades.csv` - one row per closed trade (the **blotter**).
2. `ledger.csv` - one row per trading day per pair (the **daily ledger**).
3. `summary.json` - aggregate trade and portfolio metrics.

The screening step also produces:

4. `screening_all_pairs.csv` - all pairwise statistics, all industries.
5. `screening_ranked.csv` - same data, ranked by composite score.
6. `best_per_industry.csv` - the top-scored pair per industry with the
   selected/rejected decision (10 rows).
7. `selected_pairs.csv` - the subset of `best_per_industry` that actually
   entered the backtest.

## 9.5 What is intentionally NOT modelled

- Intraday execution (we use daily closes only).
- Borrow cost on the short leg.
- Dividends, splits, and other corporate actions (the IBKR `TRADES` series
  used here is unadjusted; the impact on a 3-year window with all listed
  large caps is small but non-zero).
- Slippage and bid-ask spread.
- Capital constraints across pairs (each pair is treated as an independent
  $100k book).

These omissions make the reported Sharpe a slight overstatement relative to
what a live deployment would realize. The relative ranking of pairs and the
qualitative shape of the equity curve are unaffected.
