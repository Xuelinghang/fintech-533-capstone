# 8. Trade Fates

Every closed trade in `trades.csv` is tagged with exactly one of four fates.
This makes downstream attribution and live monitoring straightforward.

| Fate         | Trigger                                                          | Interpretation |
|--------------|------------------------------------------------------------------|----------------|
| `success`    | abs(Z) drops below 0.5                                           | Spread reverted as predicted - the strategy worked. |
| `stop_loss`  | abs(Z) exceeds 3.0                                               | Spread continued in the wrong direction - relationship may have broken. |
| `timeout`    | Position held 20 trading days without success or stop-loss       | Spread drifted sideways - signal expired without resolving. |
| `end_close`  | Backtest ended while position was still open                     | Bookkeeping. Not a real fate in live trading. |

## Realized counts (3 selected pairs, 2023-05 to 2026-04)

| Industry       | Pair       | n_trades | success | stop_loss | timeout | end_close |
|----------------|------------|---------:|--------:|----------:|--------:|----------:|
| Banks          | PNC / TFC  | 20       | 10      | 6         | 4       | 0         |
| Energy         | COP / OXY  | 22       | 11      | 6         | 5       | 0         |
| Semiconductors | MU / LRCX  | 26       | 10      | 14        | 2       | 0         |
| **Total**      |            | **68**   | **31**  | **26**    | **11**  | **0**     |

`MU / LRCX` shows the highest stop-loss share (54%) - the spread had a few
strong directional moves during the semiconductor cycle that were not absorbed
by the rolling Z-score window. Its overall contribution to portfolio P&L is
still positive thanks to the favorable success-trade payoff distribution, but
this pair is the one most likely to be re-screened first under the live
monitoring rules in section 16.

See `outputs/trades.csv` for the full per-trade record.

## Why we report fate distribution explicitly

Two strategies with the same Sharpe ratio can have very different fate
distributions, and they age very differently in production:

- A strategy with high success rate and low stop-loss rate is "comfortable"
  and tends to be stable.
- A strategy with comparable returns achieved through frequent stop-losses is
  taking on path risk - the realized P&L distribution has fatter tails and the
  strategy is more sensitive to slippage and transaction costs.
- A strategy dominated by timeouts is generating signals the market is not
  resolving - this typically means the spread has lost its mean-reverting
  character and the strategy may need to be re-screened.

We therefore monitor success / stop-loss / timeout shares as primary live
diagnostics, alongside Sharpe and drawdown.
