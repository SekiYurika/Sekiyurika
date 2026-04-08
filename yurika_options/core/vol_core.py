"""
Core volatility calculation functions.
"""
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Consistent history fetch — auto_adjust=True everywhere."""
    df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No price data for {ticker!r}.")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def calc_hv(prices: pd.Series, window: int) -> float:
    """Close-to-close log-return HV, annualised, as a DECIMAL."""
    lr = np.log(prices / prices.shift(1)).dropna()
    if len(lr) < window:
        return np.nan
    return float(lr.rolling(window).std().iloc[-1] * np.sqrt(252))


def get_atm_iv(ticker: str) -> dict:
    """Single closest-strike ATM IV from the nearest valid expiry."""
    t = yf.Ticker(ticker)
    exps = t.options
    if not exps:
        raise ValueError(f"No options listed for {ticker!r}.")

    spot = float(t.history(period="2d", auto_adjust=True)["Close"].iloc[-1])

    for exp in exps:
        dte = (pd.to_datetime(exp) - pd.Timestamp.now()).days
        if dte < 7:
            continue
        try:
            chain = t.option_chain(exp)
        except Exception:
            continue

        for side in [chain.puts, chain.calls]:
            df = side.dropna(subset=["impliedVolatility", "strike"])
            df = df[df["impliedVolatility"] > 0.005]
            if df.empty:
                continue
            idx = (df["strike"] - spot).abs().argsort().iloc[0]
            atm_row = df.iloc[idx]
            iv = float(atm_row["impliedVolatility"])
            if iv > 0:
                return {"iv": iv, "expiry": exp, "dte": dte, "spot": spot}

    raise ValueError(f"No valid ATM IV found for {ticker!r}.")


def full_scan(ticker: str) -> dict:
    """One call → everything both tools need."""
    sym = ticker.strip().upper()
    df = fetch_history(sym)
    prices = df["Close"]

    hv20 = calc_hv(prices, 20)
    hv30 = calc_hv(prices, 30)
    
    atm = get_atm_iv(sym)
    iv = atm["iv"]

    return {
        "ticker": sym,
        "spot": atm["spot"],
        "iv": iv,
        "iv_pct_display": iv * 100,
        "hv20": hv20,
        "hv30": hv30,
        "hv20_pct": hv20 * 100 if hv20 else None,
        "near_exp": atm["expiry"],
        "near_dte": atm["dte"],
    }
