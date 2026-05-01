# 10. Blotter and Ledger

The backtest writes two CSVs that together fully reconstruct the strategy's
behavior over the test window.

## 10.1 `trades.csv` — the blotter (one row per closed trade)

| Column          | Type       | Meaning |
|-----------------|------------|---------|
| `trade_id`      | int        | Sequential trade identifier across the run |
| `pair`          | string     | e.g. `PNC/TFC` |
| `industry`      | string     | Industry tag |
| `entry_date`    | date       | Day the position was opened |
| `exit_date`     | date       | Day the position was closed |
| `direction`     | string     | `long_spread` or `short_spread` |
| `entry_z`       | float      | Z-score at entry |
| `exit_z`        | float      | Z-score at exit |
| `hedge_ratio`   | float      | Hedge ratio used at entry |
| `entry_price_A` | float      | Stock A close on entry day |
| `entry_price_B` | float      | Stock B close on entry day |
| `exit_price_A`  | float      | Stock A close on exit day |
| `exit_price_B`  | float      | Stock B close on exit day |
| `shares_A`      | int        | Signed share count for stock A (>0 long, <0 short) |
| `shares_B`      | int        | Signed share count for stock B |
| `pnl`           | float      | Realized dollar P&L on the trade |
| `return_pct`    | float      | P&L divided by gross entry cost |
| `holding_days`  | int        | Days the trade was open |
| `fate`          | string     | `success`, `stop_loss`, `timeout`, or `end_close` |

## 10.2 `ledger.csv` — the daily ledger (one row per pair per day)

| Column            | Type   | Meaning |
|-------------------|--------|---------|
| `date`            | date   | Trading day |
| `pair`            | string | Pair this row belongs to |
| `industry`        | string | Industry tag |
| `position_A`      | int    | Current signed shares of A (0 if flat) |
| `position_B`      | int    | Current signed shares of B (0 if flat) |
| `price_A`         | float  | Daily close of A |
| `price_B`         | float  | Daily close of B |
| `cash`            | float  | Pair's cash balance after entries/exits |
| `portfolio_value` | float  | `cash + position_A * price_A + position_B * price_B` |
| `daily_pnl`       | float  | Day-over-day change in `portfolio_value` |
| `daily_return`    | float  | `daily_pnl / prev portfolio_value` |
| `zscore`          | float  | Spread Z-score on this day (NaN until 60-day window fills) |
| `open_trade_id`   | int    | `trade_id` if a position is open, else NaN |

## 10.3 Reconciliation

A trade row in `trades.csv` and the daily ledger rows in `ledger.csv` are
linked by `trade_id` / `open_trade_id`. Specifically:

- The set of ledger rows where `open_trade_id == k` covers exactly the days
  from `entry_date` through `exit_date - 1` for trade `k` (the exit-day P&L
  is realized into cash on the exit day itself).
- Summing `daily_pnl` over those rows reproduces the trade's `pnl` up to
  rounding.

## 10.4 Sample record (illustrative)

A successful entry-and-exit on PNC / TFC might appear in the blotter as:

| Field | Value | Note |
|---|---|---|
| `trade_id` | 12 | |
| `pair` | PNC/TFC | |
| `industry` | Banks | |
| `entry_date` | 2024-08-19 | |
| `exit_date` | 2024-08-26 | |
| `direction` | short_spread | |
| `entry_z` | +2.41 | |
| `exit_z` | +0.31 | |
| `hedge_ratio` | 1.121 | |
| `entry_price_A` | 162.34 | |
| `entry_price_B` | 39.20 | |
| `exit_price_A` | 159.12 | |
| `exit_price_B` | 39.81 | |
| `shares_A` | −61 | short ~$10k of PNC |
| `shares_B` | +286 | long ~$10k × 1.121 of TFC |
| `pnl` | +371.21 | |
| `return_pct` | +0.0186 | |
| `holding_days` | 5 | |
| `fate` | success | |

Numbers are illustrative — see `outputs/trades.csv` for the actual blotter.
