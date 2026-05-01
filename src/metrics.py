"""Performance metrics for trades and the aggregate portfolio."""
import numpy as np
import pandas as pd


def trade_summary(trades_df):
    if len(trades_df) == 0:
        return {
            "n_trades": 0, "expected_return": 0.0, "avg_holding_days": 0.0,
            "success_rate": 0.0, "stop_loss_rate": 0.0, "timeout_rate": 0.0,
            "end_close_rate": 0.0,
        }
    fates = trades_df["fate"].value_counts(normalize=True)
    return {
        "n_trades": int(len(trades_df)),
        "expected_return": float(trades_df["return_pct"].mean()),
        "avg_holding_days": float(trades_df["holding_days"].mean()),
        "success_rate": float(fates.get("success", 0.0)),
        "stop_loss_rate": float(fates.get("stop_loss", 0.0)),
        "timeout_rate": float(fates.get("timeout", 0.0)),
        "end_close_rate": float(fates.get("end_close", 0.0)),
    }


def portfolio_summary(ledger_df, periods_per_year=252, rf=0.0):
    """Aggregate per-day portfolio across pairs, then compute Sharpe / DD / total return."""
    if len(ledger_df) == 0:
        return {"sharpe": 0.0, "total_return": 0.0, "max_drawdown": 0.0,
                "annualized_return": 0.0, "annualized_vol": 0.0}

    daily = (ledger_df.groupby("date")["portfolio_value"].sum().sort_index())
    rets = daily.pct_change().dropna()
    if len(rets) == 0 or rets.std() == 0:
        sharpe = 0.0
    else:
        sharpe = float((rets.mean() - rf / periods_per_year) / rets.std() * np.sqrt(periods_per_year))

    total_return = float(daily.iloc[-1] / daily.iloc[0] - 1.0)
    annualized_return = float((1 + rets.mean()) ** periods_per_year - 1)
    annualized_vol = float(rets.std() * np.sqrt(periods_per_year))

    cum_max = daily.cummax()
    dd = (daily - cum_max) / cum_max
    max_dd = float(dd.min())

    return {
        "sharpe": sharpe,
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_vol": annualized_vol,
        "max_drawdown": max_dd,
    }


def full_summary(trades_df, ledger_df):
    return {**trade_summary(trades_df), **portfolio_summary(ledger_df)}
