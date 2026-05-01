"""Fetch historical daily bars via IBKR (shinybroker) with on-disk cache.

Each ticker is cached as a CSV in data/<TICKER>.csv. Re-running skips already
cached symbols unless force=True.
"""
import os
import time
import pandas as pd
import shinybroker as sb

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _cache_path(symbol):
    return os.path.join(DATA_DIR, f"{symbol}.csv")


def fetch_one(symbol, durationStr="3 Y", barSizeSetting="1 day",
              host="127.0.0.1", port=7497, client_id=10000):
    """Fetch one symbol's historical bars. Returns DataFrame or None."""
    contract = sb.Contract({
        "symbol": symbol,
        "secType": "STK",
        "exchange": "SMART",
        "currency": "USD",
    })
    res = sb.fetch_historical_data(
        contract=contract,
        durationStr=durationStr,
        barSizeSetting=barSizeSetting,
        whatToShow="TRADES",
        host=host, port=port, client_id=client_id,
    )
    if res is None or "hst_dta" not in res:
        return None
    df = res["hst_dta"].copy()
    if df is None or len(df) == 0:
        return None
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def fetch_universe(tickers, durationStr="3 Y", force=False, sleep_between=0.4,
                   host="127.0.0.1", port=7497, base_client_id=11000):
    """Fetch all tickers and cache to data/. Returns dict[symbol -> DataFrame]."""
    os.makedirs(DATA_DIR, exist_ok=True)
    out, failed = {}, []
    for i, sym in enumerate(tickers):
        path = _cache_path(sym)
        if os.path.exists(path) and not force:
            df = pd.read_csv(path, parse_dates=["timestamp"])
            out[sym] = df
            continue
        cid = base_client_id + i
        try:
            df = fetch_one(sym, durationStr=durationStr, host=host, port=port, client_id=cid)
        except Exception as e:
            print(f"[FAIL] {sym}: {e}")
            failed.append(sym)
            continue
        if df is None:
            print(f"[EMPTY] {sym}")
            failed.append(sym)
            continue
        df.to_csv(path, index=False)
        out[sym] = df
        print(f"[OK] {sym}: {len(df)} bars")
        time.sleep(sleep_between)
    if failed:
        print(f"Failed/empty: {failed}")
    return out


def aligned_close_panel(price_dict):
    """Build a date-aligned wide DataFrame of close prices, inner-joined on dates."""
    series = {sym: df.set_index("timestamp")["close"] for sym, df in price_dict.items()}
    panel = pd.DataFrame(series).dropna()
    return panel
