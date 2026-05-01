# fintech-533-capstone

A pair-trading strategy across 10 GICS-style US equity industries, with all
data fetched from Interactive Brokers via the `shinybroker` library.

**Authors:** Peiyuan Shan, Linghang Xue, Supawich Puengdang

## Layout

```
fintech-533-capstone/
  src/
    universe.py       industry candidate stock universe (full + smoke)
    fetch_data.py     IBKR fetcher with on-disk CSV cache
    screen_pairs.py   correlation, Engle-Granger, OLS hedge ratio, ADF, ranking
    backtest.py       event-driven Z-score backtest (entry, exit, stop, timeout)
    metrics.py        Sharpe, drawdown, fate distribution, etc.
  data/               cached daily-bar CSVs (one per ticker)
  outputs/            screening_*.csv, selected_pairs.csv, trades.csv,
                      ledger.csv, summary.json
  docs/               13-section website source content (markdown)
  site/               publish-ready static HTML site (open site/index.html)
  build_site.py       converts docs/*.md -> site/*.html with shared styling
  run_pipeline.py     one-shot orchestrator
```

## Website

The `site/` directory is a self-contained static site. Open
`site/index.html` directly in a browser, or host it on any static host
(GitHub Pages, Netlify, S3, etc.). No build server, no JS framework, no
external dependencies.

```bash
python3 build_site.py        # rebuilds site/ from docs/*.md
open site/index.html         # macOS: open in default browser
# or:
python3 -m http.server -d site 8000   # serve locally at http://localhost:8000
```

To deploy on GitHub Pages: in repo Settings -> Pages, set the source to
`main` branch and folder `/site`.

## Run

Prerequisite: TWS or IB Gateway running on `127.0.0.1:7497`.

```bash
python3 run_pipeline.py --mode smoke   # 30 tickers, fast smoke test
python3 run_pipeline.py --mode full    # 96 tickers, full universe
```

The fetcher caches each ticker as `data/<TICKER>.csv`, so reruns are fast.

## Latest run

- Window: 2023-05-02 → 2026-04-30 (3 years, 752 daily bars)
- Universe: 96 candidates, 92 with valid IBKR data
- Pairs screened: 386
- Pairs selected: 3 — PNC/TFC (Banks), COP/OXY (Energy), MU/LRCX (Semiconductors)
- Backtest: 68 trades, Sharpe 1.45, total return 3.92%, max drawdown -0.85%

See [docs/00_index.md](docs/00_index.md) for the full website content.
