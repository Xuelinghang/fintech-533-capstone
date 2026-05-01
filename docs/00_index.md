# Pair Trading — Website Content Index

The 13 sections below are the website content. They can be rendered as
standalone pages, a single long-form report, or a GitHub Pages site without
any modification.

| # | Section | File |
|---|---------|------|
| 1 | Strategy Overview                  | [01_strategy_overview.md](01_strategy_overview.md) |
| 2 | Market Phenomenon                  | [02_market_phenomenon.md](02_market_phenomenon.md) |
| 3 | Industry Universe and Pair Selection | [03_industry_universe.md](03_industry_universe.md) |
| 4 | Statistical Tests                  | [04_statistical_tests.md](04_statistical_tests.md) |
| 5 | Hedge Ratio and Spread Construction | [05_hedge_ratio_and_spread.md](05_hedge_ratio_and_spread.md) |
| 6 | Entry Rules                        | [06_entry_rules.md](06_entry_rules.md) |
| 7 | Exit Rules                         | [07_exit_rules.md](07_exit_rules.md) |
| 8 | Trade Fates                        | [08_trade_fates.md](08_trade_fates.md) |
| 9 | Backtest Design                    | [09_backtest_design.md](09_backtest_design.md) |
| 10 | Blotter and Ledger                | [10_blotter_and_ledger.md](10_blotter_and_ledger.md) |
| 11 | Performance Metrics               | [11_performance_metrics.md](11_performance_metrics.md) |
| 12 | Strategy Monitoring Going Forward | [12_strategy_monitoring.md](12_strategy_monitoring.md) |
| 13 | When the Strategy Stops Working   | [13_when_strategy_stops_working.md](13_when_strategy_stops_working.md) |

## Backtest summary at a glance

- **Window:** 2023-05-02 → 2026-04-30 (752 trading days)
- **Universe:** 96 candidate stocks across 10 industries (92 with valid IBKR data)
- **Pairs screened:** 386
- **Pairs selected:** 3 (PNC/TFC, COP/OXY, MU/LRCX)
- **Trades:** 68 — Sharpe 1.45, total return 3.92%, max drawdown -0.85%
- **Fate mix:** 45.6% success, 38.2% stop-loss, 16.2% timeout
