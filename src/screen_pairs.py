"""Pair screening: correlation, Engle-Granger cointegration, OLS hedge ratio, ADF.

Inputs are date-aligned close-price panels (output of fetch_data.aligned_close_panel).
"""
from itertools import combinations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller


def hedge_ratio_ols(log_a, log_b):
    """OLS: log_a = alpha + beta * log_b. Returns (alpha, beta)."""
    X = sm.add_constant(log_b.values)
    res = sm.OLS(log_a.values, X).fit()
    return float(res.params[0]), float(res.params[1])


def pair_stats(close_a, close_b):
    """Compute all per-pair statistics. Returns dict."""
    df = pd.concat([close_a, close_b], axis=1).dropna()
    df.columns = ["A", "B"]
    if len(df) < 60:
        return None

    ret = df.pct_change().dropna()
    corr = float(ret["A"].corr(ret["B"]))

    log_a, log_b = np.log(df["A"]), np.log(df["B"])
    alpha, beta = hedge_ratio_ols(log_a, log_b)
    spread = log_a - beta * log_b

    try:
        _, coint_p, _ = coint(log_a, log_b)
        coint_p = float(coint_p)
    except Exception:
        coint_p = np.nan

    try:
        adf_p = float(adfuller(spread.dropna(), autolag="AIC")[1])
    except Exception:
        adf_p = np.nan

    return {
        "corr": corr,
        "coint_p": coint_p,
        "adf_p": adf_p,
        "alpha": alpha,
        "hedge_ratio": beta,
        "spread_std": float(spread.std()),
        "n_obs": int(len(df)),
    }


def screen_industry(industry, tickers, panel):
    """All pairwise stats for one industry. Returns DataFrame."""
    available = [t for t in tickers if t in panel.columns]
    rows = []
    for a, b in combinations(available, 2):
        s = pair_stats(panel[a], panel[b])
        if s is None:
            continue
        rows.append({"industry": industry, "stock_A": a, "stock_B": b, **s})
    return pd.DataFrame(rows)


def screen_all(universe, panel):
    """Run pairwise screening across all industries. Returns concatenated DataFrame."""
    parts = [screen_industry(ind, syms, panel) for ind, syms in universe.items()]
    parts = [p for p in parts if len(p) > 0]
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def rank_and_pick(screen_df, corr_min=0.50, coint_max=0.10, adf_max=0.10):
    """Rank pairs and pick the best one per industry.

    Score = z(corr) - z(coint_p) - z(adf_p).
    Returns (ranked_all, best_per_industry, selected_for_backtest).
      best_per_industry: top-scored pair per industry with a 'decision' column.
      selected_for_backtest: subset where passes_filter is True.
    """
    if len(screen_df) == 0:
        empty = screen_df.copy()
        return empty, empty, empty

    df = screen_df.copy()
    df["passes_filter"] = (
        (df["corr"] >= corr_min)
        & (df["coint_p"] <= coint_max)
        & (df["adf_p"] <= adf_max)
    )

    def _z(s):
        s = s.astype(float)
        if s.std() == 0 or s.isna().all():
            return pd.Series(np.zeros(len(s)), index=s.index)
        return (s - s.mean()) / s.std()

    df["score"] = _z(df["corr"]) - _z(df["coint_p"]) - _z(df["adf_p"])

    best = (df.sort_values(["industry", "score"], ascending=[True, False])
              .groupby("industry", as_index=False)
              .head(1)
              .reset_index(drop=True))
    best["decision"] = best["passes_filter"].map({True: "selected", False: "rejected"})

    selected = best[best["passes_filter"]].copy().reset_index(drop=True)
    ranked = df.sort_values("score", ascending=False).reset_index(drop=True)
    return ranked, best, selected
