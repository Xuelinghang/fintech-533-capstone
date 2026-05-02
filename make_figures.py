"""Generate static SVG figures for the site from outputs/ data.

Each function reads from outputs/ (and data/ where needed) and writes one
SVG to site/figures/. Run before build_site.py.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "site" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

ACCENT = "#0b6e4f"
ACCENT_RED = "#cc6633"
ACCENT_DARK = "#aa3333"
MUTED = "#6b6b6b"
FG = "#1a1a1a"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.edgecolor": "#cccccc",
    "axes.labelcolor": FG,
    "axes.titlecolor": FG,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
})


def equity_curve():
    ledger = pd.read_csv(OUTPUTS / "ledger.csv", parse_dates=["date"])
    pv = ledger.groupby("date")["portfolio_value"].sum().sort_index()
    cum_return = (pv / pv.iloc[0] - 1.0) * 100
    running_max = pv.cummax()
    drawdown = ((pv - running_max) / running_max) * 100

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9, 5), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.08},
    )
    ax1.plot(cum_return.index, cum_return.values, color=ACCENT, linewidth=1.8)
    ax1.axhline(0, color=MUTED, linewidth=0.6, linestyle="--", alpha=0.6)
    ax1.set_ylabel("Cumulative return (%)")
    ax1.set_title(
        "Aggregate equity curve across 3 selected pairs (PNC/TFC, COP/OXY, MU/LRCX)",
        fontsize=11, loc="left", pad=12, color=FG,
    )
    ax2.fill_between(drawdown.index, drawdown.values, 0, color=ACCENT, alpha=0.25)
    ax2.plot(drawdown.index, drawdown.values, color=ACCENT, linewidth=1.0)
    ax2.set_ylabel("Drawdown (%)")
    fig.savefig(FIGURES / "equity_curve.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/equity_curve.svg")


def screening_scatter():
    df = pd.read_csv(OUTPUTS / "screening_all_pairs.csv")
    selected = pd.read_csv(OUTPUTS / "selected_pairs.csv")
    sel_keys = set(zip(selected["stock_A"], selected["stock_B"]))
    df["selected"] = df.apply(
        lambda r: (r["stock_A"], r["stock_B"]) in sel_keys, axis=1
    )

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    others = df[~df["selected"]]
    sel = df[df["selected"]]

    ax.scatter(others["corr"], others["coint_p"],
               s=14, alpha=0.4, color=MUTED, edgecolor="none",
               label=f"Rejected ({len(others)})")
    ax.scatter(sel["corr"], sel["coint_p"],
               s=90, color=ACCENT, edgecolor="white", linewidth=1.4,
               zorder=3, label=f"Selected ({len(sel)})")
    ax.axvline(0.50, color=ACCENT_RED, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axhline(0.10, color=ACCENT_RED, linewidth=0.8, linestyle="--", alpha=0.7)

    for _, r in sel.iterrows():
        ax.annotate(f"{r['stock_A']}/{r['stock_B']}",
                    (r["corr"], r["coint_p"]),
                    xytext=(8, -2), textcoords="offset points",
                    fontsize=9, color=ACCENT, fontweight="bold")

    notable = df[(df["stock_A"] == "V") & (df["stock_B"] == "MA")]
    for _, r in notable.iterrows():
        ax.scatter(r["corr"], r["coint_p"], s=40, facecolors="none",
                   edgecolor=ACCENT_DARK, linewidth=1.2, zorder=2)
        ax.annotate(f"{r['stock_A']}/{r['stock_B']}",
                    (r["corr"], r["coint_p"]),
                    xytext=(8, 4), textcoords="offset points",
                    fontsize=8.5, color=ACCENT_DARK, style="italic")

    ax.set_yscale("log")
    ax.set_xlabel("Daily-return correlation")
    ax.set_ylabel("Engle–Granger cointegration p-value (log scale)")
    ax.set_title(f"Pair screening: {len(df)} candidates, {len(sel)} selected",
                 fontsize=11, loc="left", pad=12, color=FG)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    fig.savefig(FIGURES / "screening_scatter.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/screening_scatter.svg")


def pair_panel():
    ledger = pd.read_csv(OUTPUTS / "ledger.csv", parse_dates=["date"])
    selected = pd.read_csv(OUTPUTS / "selected_pairs.csv")
    pair = selected[(selected["stock_A"] == "PNC") &
                    (selected["stock_B"] == "TFC")].iloc[0]

    pair_data = ledger[ledger["pair"] == "PNC/TFC"].set_index("date").sort_index()
    pnc = pd.read_csv(DATA / "PNC.csv", parse_dates=["timestamp"]) \
            .set_index("timestamp")["close"]
    tfc = pd.read_csv(DATA / "TFC.csv", parse_dates=["timestamp"]) \
            .set_index("timestamp")["close"]
    aligned_pnc = pnc.reindex(pair_data.index, method="ffill")
    aligned_tfc = tfc.reindex(pair_data.index, method="ffill")

    log_pnc = np.log(aligned_pnc)
    log_tfc = np.log(aligned_tfc)
    spread = log_pnc - pair["hedge_ratio"] * log_tfc - pair["alpha"]
    spread_mean = spread.rolling(60, min_periods=20).mean()
    zscore = pair_data["zscore"]

    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True,
                              gridspec_kw={"hspace": 0.18})
    axes[0].plot(log_pnc.index, log_pnc.values, color=ACCENT,
                 linewidth=1.2, label="log(PNC)")
    axes[0].plot(log_tfc.index, log_tfc.values, color=ACCENT_RED,
                 linewidth=1.2, label="log(TFC)")
    axes[0].set_ylabel("Log price")
    axes[0].legend(frameon=False, fontsize=9, loc="lower right")
    axes[0].set_title(
        "PNC / TFC: log prices, spread, and rolling Z-score",
        fontsize=11, loc="left", pad=12, color=FG,
    )

    axes[1].plot(spread.index, spread.values, color=MUTED,
                 linewidth=0.9, label="Spread")
    axes[1].plot(spread_mean.index, spread_mean.values, color=ACCENT,
                 linewidth=1.4, label="60-day rolling mean")
    axes[1].set_ylabel("Spread (log units)")
    axes[1].legend(frameon=False, fontsize=9, loc="lower right")

    axes[2].plot(zscore.index, zscore.values, color=ACCENT, linewidth=0.9)
    for level, style, color, label in [
        (2, "--", ACCENT_RED, "±2 entry"),
        (-2, "--", ACCENT_RED, None),
        (3, ":", ACCENT_DARK, "±3 stop"),
        (-3, ":", ACCENT_DARK, None),
        (0.5, "-", MUTED, "±0.5 exit"),
        (-0.5, "-", MUTED, None),
    ]:
        axes[2].axhline(level, color=color, linestyle=style,
                        linewidth=0.7, alpha=0.7, label=label)
    axes[2].axhline(0, color="black", linewidth=0.4, alpha=0.3)
    axes[2].set_ylabel("Z-score")
    axes[2].legend(frameon=False, fontsize=8.5, loc="lower right", ncol=3)
    fig.savefig(FIGURES / "pair_panel_pnc_tfc.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/pair_panel_pnc_tfc.svg")


def annotated_trade_window():
    ledger = pd.read_csv(OUTPUTS / "ledger.csv", parse_dates=["date"])
    trades = pd.read_csv(OUTPUTS / "trades.csv",
                         parse_dates=["entry_date", "exit_date"])
    pnc_trades = trades[trades["pair"] == "PNC/TFC"].copy().sort_values("entry_date")

    best_window = None
    best_score = -1
    for _, row in pnc_trades.iterrows():
        start = row["entry_date"] - pd.Timedelta(days=10)
        end = start + pd.Timedelta(days=90)
        in_window = pnc_trades[(pnc_trades["entry_date"] >= start) &
                                (pnc_trades["entry_date"] <= end)]
        fates = set(in_window["fate"])
        if "success" in fates and "stop_loss" in fates:
            score = len(fates) * 10 + len(in_window)
            if score > best_score:
                best_window = (start, end)
                best_score = score
    if best_window is None:
        # fallback: window with most trades
        best_score = -1
        for _, row in pnc_trades.iterrows():
            start = row["entry_date"] - pd.Timedelta(days=10)
            end = start + pd.Timedelta(days=90)
            in_window = pnc_trades[(pnc_trades["entry_date"] >= start) &
                                    (pnc_trades["entry_date"] <= end)]
            if len(in_window) > best_score:
                best_window = (start, end)
                best_score = len(in_window)

    start, end = best_window
    pair_data = ledger[ledger["pair"] == "PNC/TFC"].set_index("date").sort_index()
    z = pair_data.loc[start:end, "zscore"]
    window_trades = pnc_trades[(pnc_trades["entry_date"] >= start) &
                                (pnc_trades["entry_date"] <= end)]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(z.index, z.values, color=ACCENT, linewidth=1.2)
    for level, style, color in [
        (2, "--", ACCENT_RED), (-2, "--", ACCENT_RED),
        (3, ":", ACCENT_DARK), (-3, ":", ACCENT_DARK),
        (0.5, "-", MUTED), (-0.5, "-", MUTED),
    ]:
        ax.axhline(level, color=color, linestyle=style, linewidth=0.7, alpha=0.6)
    ax.axhline(0, color="black", linewidth=0.4, alpha=0.3)

    fate_markers = {
        "success": ("^", ACCENT, "Success exit"),
        "stop_loss": ("v", ACCENT_DARK, "Stop-loss exit"),
        "timeout": ("s", MUTED, "Timeout exit"),
    }
    seen = set()
    for _, t in window_trades.iterrows():
        ax.plot(t["entry_date"], t["entry_z"], marker="o", markersize=8,
                color="white", markeredgecolor=FG, markeredgewidth=1.2,
                zorder=4)
        if "Entry" not in seen:
            ax.plot([], [], marker="o", markersize=8, color="white",
                    markeredgecolor=FG, linestyle="None", label="Entry")
            seen.add("Entry")
        marker, color, label = fate_markers.get(t["fate"], ("x", FG, t["fate"]))
        ax.plot(t["exit_date"], t["exit_z"], marker=marker, markersize=10,
                color=color, markeredgecolor="white", markeredgewidth=1.0,
                zorder=5)
        if label not in seen:
            ax.plot([], [], marker=marker, markersize=10, color=color,
                    markeredgecolor="white", linestyle="None", label=label)
            seen.add(label)

    ax.set_ylabel("Z-score")
    ax.set_title(f"PNC / TFC trades: {start.date()} to {end.date()}",
                 fontsize=11, loc="left", pad=12, color=FG)
    ax.legend(frameon=False, fontsize=9, loc="lower right", ncol=2)
    fig.savefig(FIGURES / "annotated_trades.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/annotated_trades.svg")


def fate_stacked_bar():
    trades = pd.read_csv(OUTPUTS / "trades.csv")
    counts = trades.groupby(["pair", "fate"]).size().unstack(fill_value=0)
    fate_order = [f for f in ["success", "stop_loss", "timeout", "end_close"]
                  if f in counts.columns]
    counts = counts[fate_order]
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    fate_colors = {
        "success": ACCENT,
        "stop_loss": ACCENT_RED,
        "timeout": MUTED,
        "end_close": "#999999",
    }

    fig, ax = plt.subplots(figsize=(9, 3.0))
    left = pd.Series(0.0, index=pct.index)
    for fate in fate_order:
        ax.barh(pct.index, pct[fate], left=left,
                color=fate_colors[fate], label=fate.replace("_", "-"),
                edgecolor="white", linewidth=1.5, height=0.6)
        for pair in pct.index:
            val = pct.loc[pair, fate]
            if val > 6:
                ax.text(left[pair] + val / 2, pair, f"{val:.0f}%",
                        ha="center", va="center", fontsize=9.5,
                        color="white", fontweight="bold")
        left = left + pct[fate]

    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of trades (%)")
    ax.set_title("Trade fate distribution by pair",
                 fontsize=11, loc="left", pad=12, color=FG)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25),
              ncol=4, frameon=False, fontsize=9)
    fig.savefig(FIGURES / "fate_stacked_bar.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/fate_stacked_bar.svg")


def return_distribution():
    trades = pd.read_csv(OUTPUTS / "trades.csv")
    returns = trades["return_pct"] * 100

    fate_colors = {
        "success": ACCENT,
        "stop_loss": ACCENT_RED,
        "timeout": MUTED,
    }

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    bins = np.linspace(returns.min(), returns.max(), 24)
    bottoms = np.zeros(len(bins) - 1)
    for fate in ["success", "stop_loss", "timeout"]:
        sub = trades[trades["fate"] == fate]["return_pct"] * 100
        if len(sub) == 0:
            continue
        counts, _ = np.histogram(sub, bins=bins)
        ax.bar(bins[:-1], counts, width=np.diff(bins),
               bottom=bottoms, align="edge",
               color=fate_colors[fate], alpha=0.85,
               edgecolor="white", linewidth=0.4,
               label=f"{fate.replace('_', '-')} (n={len(sub)})")
        bottoms = bottoms + counts

    ax.axvline(0, color="black", linewidth=0.6, alpha=0.5)
    ax.set_xlabel("Trade return (%)")
    ax.set_ylabel("Number of trades")
    ax.set_title("Per-trade return distribution by fate",
                 fontsize=11, loc="left", pad=12, color=FG)
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(FIGURES / "return_distribution.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/return_distribution.svg")


def drawdown_underwater():
    ledger = pd.read_csv(OUTPUTS / "ledger.csv", parse_dates=["date"])
    pv = ledger.groupby("date")["portfolio_value"].sum().sort_index()
    running_max = pv.cummax()
    drawdown = ((pv - running_max) / running_max) * 100

    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.fill_between(drawdown.index, drawdown.values, 0,
                    color=ACCENT, alpha=0.3)
    ax.plot(drawdown.index, drawdown.values, color=ACCENT, linewidth=1.0)
    ax.axhline(0, color="black", linewidth=0.5, alpha=0.4)
    ax.set_ylabel("Drawdown (%)")
    ax.set_title(
        f"Underwater drawdown curve (max DD: {drawdown.min():.2f}%)",
        fontsize=11, loc="left", pad=12, color=FG,
    )
    fig.savefig(FIGURES / "drawdown_underwater.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/drawdown_underwater.svg")


def rolling_metrics():
    trades = pd.read_csv(OUTPUTS / "trades.csv",
                         parse_dates=["exit_date"]).sort_values("exit_date")
    trades = trades.reset_index(drop=True)
    span_days = (trades["exit_date"].max() - trades["exit_date"].min()).days
    trades_per_year = len(trades) * 365.25 / max(span_days, 1)

    window = 20
    r = trades["return_pct"]
    rolling_sharpe = (r.rolling(window).mean() /
                       r.rolling(window).std() *
                       np.sqrt(trades_per_year))
    is_success = (trades["fate"] == "success").astype(float)
    is_stop = (trades["fate"] == "stop_loss").astype(float)
    rolling_success = is_success.rolling(window).mean() * 100
    rolling_stop = is_stop.rolling(window).mean() * 100
    x = trades["exit_date"]

    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True,
                              gridspec_kw={"hspace": 0.2})
    axes[0].plot(x, rolling_sharpe, color=ACCENT, linewidth=1.4)
    axes[0].axhline(1.0, color=MUTED, linewidth=0.8, linestyle="--", alpha=0.6,
                     label="Watch band: Sharpe < 1")
    axes[0].set_ylabel("Trailing 20-trade Sharpe")
    axes[0].legend(frameon=False, fontsize=8.5, loc="lower left")
    axes[0].set_title(
        "Rolling strategy diagnostics (trailing 20-trade window)",
        fontsize=11, loc="left", pad=12, color=FG,
    )
    axes[1].plot(x, rolling_success, color=ACCENT, linewidth=1.4)
    axes[1].axhline(35, color=ACCENT_RED, linewidth=0.7, linestyle="--",
                     alpha=0.7, label="Watch band: success < 35%")
    axes[1].set_ylabel("Success rate (%)")
    axes[1].set_ylim(0, 100)
    axes[1].legend(frameon=False, fontsize=8.5, loc="lower left")
    axes[2].plot(x, rolling_stop, color=ACCENT_RED, linewidth=1.4)
    axes[2].axhline(50, color=ACCENT_RED, linewidth=0.7, linestyle="--",
                     alpha=0.7, label="Watch band: stop-loss > 50%")
    axes[2].set_ylabel("Stop-loss rate (%)")
    axes[2].set_ylim(0, 100)
    axes[2].legend(frameon=False, fontsize=8.5, loc="lower left")
    fig.savefig(FIGURES / "rolling_metrics.svg", format="svg")
    plt.close(fig)
    print("  wrote site/figures/rolling_metrics.svg")


if __name__ == "__main__":
    print(f"Generating figures to {FIGURES}")
    equity_curve()
    screening_scatter()
    pair_panel()
    annotated_trade_window()
    fate_stacked_bar()
    return_distribution()
    drawdown_underwater()
    rolling_metrics()
    print("Done.")
