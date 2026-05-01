# 7. Exit Rules

A trade can exit through one of four channels. Each is checked once per day
in this order: success, stop-loss, timeout, end-of-data.

## 7.1 Success exit (mean reversion)

When the absolute Z-score drops below **0.5**, the position is closed and
tagged with the fate `success`.

We exit when the spread mostly reverts toward its mean. We use 0.5 instead of
exactly 0 because waiting for the spread to return to *exactly* zero often
means giving back already-realized profit. 0.5 captures most of the reversion
while leaving a small buffer.

## 7.2 Stop-loss exit

When the absolute Z-score exceeds **3.0**, the position is closed and tagged
with the fate `stop_loss`.

A stop-loss is triggered when the spread has continued moving against the
trade beyond 3 standard deviations. At this point the historical spread
distribution no longer supports the trade, and the more likely explanation is
that the underlying relationship has shifted.

## 7.3 Timeout exit

If a position has been open for **20 trading days** without hitting either of
the two exits above, it is closed and tagged with the fate `timeout`.

Pair trading is a short- to medium-term mean-reversion strategy. If the spread
has not reverted within roughly one trading month, it is more likely to be
trending than reverting, and the original statistical edge has expired. Closing
the position frees capital for a fresher signal.

## 7.4 End-of-data close

If a trade is still open on the last day of the backtest, it is closed at that
day's price and tagged with the fate `end_close`. This is a bookkeeping rule
for the backtest, not a live trading rule — in production the position would
simply remain open into the next session.

## 7.5 Realized fate distribution (3 selected pairs, full backtest)

| Fate       | Trades | Share |
|------------|--------|-------|
| success    | 31     | 45.6% |
| stop_loss  | 26     | 38.2% |
| timeout    | 11     | 16.2% |
| end_close  | 0      | 0.0%  |
| **Total**  | **68** | 100%  |

Roughly half of trades exit cleanly via mean reversion; about 38% are stopped
out. Stop-loss frequency is something we monitor closely - a sustained rise in
that rate is one of the early warning signals described in section 16.
