import streamlit as st
import yfinance as yf
import pandas as pd

from utils.indicators import compute_rsi, compute_moving_averages, compute_vwap


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_company_info(ticker: str) -> dict:
    """Fundamental / descriptive fields for the profile strip and key-stats
    panel. Indices (e.g. ^NSEI) won't have most of these fields, so every
    lookup is defensive and falls back to None."""
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        info = {}

    def g(*keys):
        for k in keys:
            v = info.get(k)
            if v not in (None, "", "N/A"):
                return v
        return None

    return {
        "name": g("longName", "shortName") or ticker,
        "sector": g("sector"),
        "industry": g("industry"),
        "exchange": g("exchange", "fullExchangeName"),
        "currency": g("currency"),
        "market_cap": g("marketCap"),
        "pe": g("trailingPE"),
        "forward_pe": g("forwardPE"),
        "pb": g("priceToBook"),
        "eps": g("trailingEps"),
        "beta": g("beta"),
        "dividend_yield": g("dividendYield"),
        "book_value": g("bookValue"),
        "fifty_two_high": g("fiftyTwoWeekHigh"),
        "fifty_two_low": g("fiftyTwoWeekLow"),
    }


def _slice_to_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    windows = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252}
    if period in windows:
        return df.tail(windows[period]).copy()
    return df.copy()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(ticker: str, period: str = "1y", interval: str = "1d"):
    """Downloads market data and computes all indicators/statistics needed
    by the app. Returns (plot_df, stats) or None if the ticker has no data."""

    # Daily interval always pulls 2y of history so MA50/52w stats stay
    # accurate even when the user is viewing a shorter window.
    history_period = "2y" if interval == "1d" else period

    df = yf.download(
        ticker,
        period=history_period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        return None

    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()

    date_col = "Datetime" if "Datetime" in df.columns else "Date"
    df.rename(columns={date_col: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["time"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Indicators computed on the full fetched history for accuracy.
    df = compute_moving_averages(df)
    df["RSI"] = compute_rsi(df["Close"])

    # BUG FIX: don't blindly trust df.iloc[-1]. Yahoo Finance regularly
    # returns a trailing row with NaN OHLCV for an in-progress/incomplete
    # period (e.g. weekly/monthly bars, or a session that just opened).
    # Using that row directly propagated NaN into every "latest price"
    # figure downstream (hero price, day high/low, volume).
    valid_rows = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    if valid_rows.empty:
        return None

    latest = valid_rows.iloc[-1]
    yearly = df.tail(252)

    stats = {
        "day_high": float(latest["High"]),
        "day_low": float(latest["Low"]),
        "day_open": float(latest["Open"]),
        "day_close": float(latest["Close"]),
        "volume": int(latest["Volume"]),
        "avg_volume_20": int(yearly["Volume"].dropna().tail(20).mean()),
        "high_52w": float(yearly["High"].max()),
        "low_52w": float(yearly["Low"].min()),
    }

    plot_df = _slice_to_period(df, period) if history_period != period else df.copy()
    plot_df = plot_df.reset_index(drop=True)
    plot_df = compute_vwap(plot_df)  # windowed VWAP — see utils.indicators

    return plot_df, stats
