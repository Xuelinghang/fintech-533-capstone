"""Event-driven pair-trading backtest.

Entry: Z(spread) > +entry_z -> short spread; < -entry_z -> long spread.
Exit:  |Z| < exit_z (success), |Z| > stop_z (stop-loss), holding > timeout (timeout),
       end-of-data (end_close).
Spread: log(A) - hedge_ratio * log(B).

Position sizing: dollar-neutral. notional_per_leg dollars on each leg of the spread,
shares rounded to int. Cash accounts for both legs and final P&L.
"""
import numpy as np
import pandas as pd


def rolling_zscore(spread, window):
    mu = spread.rolling(window).mean()
    sd = spread.rolling(window).std(ddof=0)
    return (spread - mu) / sd


def _build_spread(panel_a, panel_b, hedge_ratio):
    return np.log(panel_a) - hedge_ratio * np.log(panel_b)


def backtest_pair(panel, stock_a, stock_b, hedge_ratio, industry,
                  entry_z=2.0, exit_z=0.5, stop_z=3.0, timeout=20,
                  zscore_window=60, notional_per_leg=10000.0,
                  starting_cash=100000.0, trade_id_offset=0):
    """Backtest a single pair. Returns (trades_df, ledger_df)."""
    df = panel[[stock_a, stock_b]].dropna().copy()
    df.columns = ["A", "B"]
    df["spread"] = _build_spread(df["A"], df["B"], hedge_ratio)
    df["zscore"] = rolling_zscore(df["spread"], zscore_window)

    cash = starting_cash
    pos_a = 0
    pos_b = 0
    open_trade = None
    next_trade_id = trade_id_offset + 1

    trades = []
    ledger = []

    dates = df.index.tolist()
    for i, date in enumerate(dates):
        z = df["zscore"].iat[i]
        pa = df["A"].iat[i]
        pb = df["B"].iat[i]

        # ---- manage open trade ----
        if open_trade is not None:
            held = i - open_trade["entry_idx"]
            fate = None
            if not np.isnan(z) and abs(z) < exit_z:
                fate = "success"
            elif not np.isnan(z) and abs(z) > stop_z:
                fate = "stop_loss"
            elif held >= timeout:
                fate = "timeout"
            elif i == len(dates) - 1:
                fate = "end_close"

            if fate is not None:
                # close: cash += pos_a * pa + pos_b * pb (sign already in pos)
                cash += pos_a * pa + pos_b * pb
                exit_val_a = pos_a * pa
                exit_val_b = pos_b * pb
                pnl = (
                    pos_a * (pa - open_trade["entry_price_A"])
                    + pos_b * (pb - open_trade["entry_price_B"])
                )
                gross_entry_cost = (
                    abs(open_trade["shares_A"]) * open_trade["entry_price_A"]
                    + abs(open_trade["shares_B"]) * open_trade["entry_price_B"]
                )
                ret_pct = pnl / gross_entry_cost if gross_entry_cost > 0 else 0.0

                trades.append({
                    "trade_id": open_trade["trade_id"],
                    "pair": f"{stock_a}/{stock_b}",
                    "industry": industry,
                    "entry_date": open_trade["entry_date"],
                    "exit_date": date,
                    "direction": open_trade["direction"],
                    "entry_z": open_trade["entry_z"],
                    "exit_z": float(z) if not np.isnan(z) else np.nan,
                    "hedge_ratio": hedge_ratio,
                    "entry_price_A": open_trade["entry_price_A"],
                    "entry_price_B": open_trade["entry_price_B"],
                    "exit_price_A": float(pa),
                    "exit_price_B": float(pb),
                    "shares_A": open_trade["shares_A"],
                    "shares_B": open_trade["shares_B"],
                    "pnl": float(pnl),
                    "return_pct": float(ret_pct),
                    "holding_days": int(held),
                    "fate": fate,
                })
                pos_a = 0
                pos_b = 0
                open_trade = None

        # ---- check entry ----
        if open_trade is None and not np.isnan(z):
            direction = None
            if z > entry_z:
                direction = "short_spread"  # short A, long B
            elif z < -entry_z:
                direction = "long_spread"   # long A, short B

            if direction is not None:
                shares_a_abs = int(notional_per_leg / pa) if pa > 0 else 0
                shares_b_abs = int((notional_per_leg * abs(hedge_ratio)) / pb) if pb > 0 else 0
                if shares_a_abs > 0 and shares_b_abs > 0:
                    if direction == "long_spread":
                        sh_a = +shares_a_abs
                        sh_b = -shares_b_abs
                    else:
                        sh_a = -shares_a_abs
                        sh_b = +shares_b_abs
                    cash -= sh_a * pa + sh_b * pb
                    pos_a = sh_a
                    pos_b = sh_b
                    open_trade = {
                        "trade_id": next_trade_id,
                        "entry_idx": i,
                        "entry_date": date,
                        "direction": direction,
                        "entry_z": float(z),
                        "entry_price_A": float(pa),
                        "entry_price_B": float(pb),
                        "shares_A": sh_a,
                        "shares_B": sh_b,
                    }
                    next_trade_id += 1

        # ---- ledger row ----
        portfolio_value = cash + pos_a * pa + pos_b * pb
        ledger.append({
            "date": date,
            "pair": f"{stock_a}/{stock_b}",
            "industry": industry,
            "position_A": pos_a,
            "position_B": pos_b,
            "price_A": float(pa),
            "price_B": float(pb),
            "cash": float(cash),
            "portfolio_value": float(portfolio_value),
            "zscore": float(z) if not np.isnan(z) else np.nan,
            "open_trade_id": open_trade["trade_id"] if open_trade else np.nan,
        })

    trades_df = pd.DataFrame(trades)
    ledger_df = pd.DataFrame(ledger)
    if len(ledger_df) > 0:
        ledger_df["daily_pnl"] = ledger_df["portfolio_value"].diff().fillna(0.0)
        ledger_df["daily_return"] = ledger_df["portfolio_value"].pct_change().fillna(0.0)
    return trades_df, ledger_df


def backtest_portfolio(panel, selected_pairs, **kwargs):
    """Run backtest_pair over the selected_pairs DataFrame. Returns (trades, ledgers).

    selected_pairs columns: industry, stock_A, stock_B, hedge_ratio
    """
    all_trades = []
    all_ledgers = []
    offset = 0
    for _, row in selected_pairs.iterrows():
        t, l = backtest_pair(
            panel,
            stock_a=row["stock_A"],
            stock_b=row["stock_B"],
            hedge_ratio=row["hedge_ratio"],
            industry=row["industry"],
            trade_id_offset=offset,
            **kwargs,
        )
        offset += len(t)
        all_trades.append(t)
        all_ledgers.append(l)

    trades_df = (pd.concat(all_trades, ignore_index=True)
                 if any(len(t) for t in all_trades) else pd.DataFrame())
    ledgers_df = (pd.concat(all_ledgers, ignore_index=True)
                  if any(len(l) for l in all_ledgers) else pd.DataFrame())
    return trades_df, ledgers_df
