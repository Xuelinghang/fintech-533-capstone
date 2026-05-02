"""Generate static SVG figures for the site from outputs/ data.

Each function reads from outputs/ and writes one SVG to site/figures/.
Run before build_site.py.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "site" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

ACCENT = "#0b6e4f"
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


if __name__ == "__main__":
    print(f"Generating figures to {FIGURES}")
    equity_curve()
    print("Done.")
