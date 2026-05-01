"""End-to-end pipeline: fetch -> screen -> select -> backtest -> metrics -> outputs.

Usage:
    python run_pipeline.py --mode smoke
    python run_pipeline.py --mode full
"""
import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from src.universe import SMOKE_UNIVERSE, FULL_UNIVERSE, all_tickers
from src.fetch_data import fetch_universe, aligned_close_panel
from src.screen_pairs import screen_all, rank_and_pick
from src.backtest import backtest_portfolio
from src.metrics import trade_summary, portfolio_summary

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def run(universe, duration="3 Y"):
    tickers = all_tickers(universe)
    print(f"Universe: {len(tickers)} tickers across {len(universe)} industries")

    print("\n[1/5] Fetching historical data via IBKR...")
    prices = fetch_universe(tickers, durationStr=duration)
    print(f"  Got data for {len(prices)} / {len(tickers)} tickers")

    print("\n[2/5] Aligning close-price panel...")
    panel = aligned_close_panel(prices)
    print(f"  Panel shape: {panel.shape}, dates {panel.index.min().date()} to {panel.index.max().date()}")

    print("\n[3/5] Screening pairs (correlation, cointegration, ADF)...")
    screen_df = screen_all(universe, panel)
    screen_df.to_csv(os.path.join(OUT_DIR, "screening_all_pairs.csv"), index=False)
    print(f"  Screened {len(screen_df)} pairs")

    ranked, best, selected = rank_and_pick(screen_df, corr_min=0.50, coint_max=0.10, adf_max=0.10)
    ranked.to_csv(os.path.join(OUT_DIR, "screening_ranked.csv"), index=False)
    best.to_csv(os.path.join(OUT_DIR, "best_per_industry.csv"), index=False)
    selected.to_csv(os.path.join(OUT_DIR, "selected_pairs.csv"), index=False)
    print(f"  Best pair per industry (10 rows expected):")
    print(best[["industry", "stock_A", "stock_B", "corr", "coint_p", "adf_p", "hedge_ratio", "decision"]].to_string(index=False))
    print(f"  -> {len(selected)} pairs selected for backtest")

    print("\n[4/5] Running backtest...")
    trades_df, ledger_df = backtest_portfolio(
        panel.set_index(panel.index),
        selected,
        entry_z=2.0, exit_z=0.5, stop_z=3.0, timeout=20,
        zscore_window=60, notional_per_leg=10000.0,
        starting_cash=100000.0,
    )
    trades_df.to_csv(os.path.join(OUT_DIR, "trades.csv"), index=False)
    ledger_df.to_csv(os.path.join(OUT_DIR, "ledger.csv"), index=False)
    print(f"  Trades: {len(trades_df)}, Ledger rows: {len(ledger_df)}")

    print("\n[5/5] Computing performance metrics...")
    summary = {
        "trade_summary": trade_summary(trades_df),
        "portfolio_summary": portfolio_summary(ledger_df),
    }
    with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    p.add_argument("--duration", default="3 Y")
    args = p.parse_args()
    universe = SMOKE_UNIVERSE if args.mode == "smoke" else FULL_UNIVERSE
    run(universe, duration=args.duration)
