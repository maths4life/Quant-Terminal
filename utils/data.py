import streamlit as st
import yfinance as yf
import pandas as pd

from utils.helpers import compute_rsi


@st.cache_data(ttl=3600)
def fetch_company_info(ticker):
    """
    Pulls fundamental / descriptive fields for the company-profile strip
    and key-statistics panel. Indices (e.g. ^NSEI) won't have most of
    these fields, so every lookup is defensive and falls back to None.
    """
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
        "name":            g("longName", "shortName") or ticker,
        "sector":          g("sector"),
        "industry":        g("industry"),
        "exchange":        g("exchange", "fullExchangeName"),
        "currency":        g("currency"),
        "market_cap":      g("marketCap"),
        "pe":              g("trailingPE"),
        "forward_pe":      g("forwardPE"),
        "pb":              g("priceToBook"),
        "eps":             g("trailingEps"),
        "beta":            g("beta"),
        "dividend_yield":  g("dividendYield"),
        "book_value":      g("bookValue"),
        "fifty_two_high":  g("fiftyTwoWeekHigh"),
        "fifty_two_low":   g("fiftyTwoWeekLow"),
    }


@st.cache_data(ttl=3600)
def fetch_data(ticker, period="1y", interval="1d"):
    """
    Downloads market data and computes all indicators/statistics
    needed by the application.
    """

    # Download enough history for indicators and 52-week stats
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

    # Technical Indicators (computed on full history for accuracy)
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"]  = compute_rsi(df["Close"])

    # Latest candle
    latest = df.iloc[-1]

    # Use the last 252 trading sessions for 52-week statistics
    yearly = df.tail(252)

    stats = {
        "day_high":      float(latest["High"]),
        "day_low":       float(latest["Low"]),
        "day_open":      float(latest["Open"]),
        "day_close":     float(latest["Close"]),
        "volume":        int(latest["Volume"]),
        "avg_volume_20": int(yearly["Volume"].tail(20).mean()),
        "high_52w":      float(yearly["High"].max()),
        "low_52w":       float(yearly["Low"].min()),
    }

    # Slice to the requested plot window
    if history_period != period:
        if period == "1mo":
            plot_df = df.tail(22).copy()
        elif period == "3mo":
            plot_df = df.tail(66).copy()
        elif period == "6mo":
            plot_df = df.tail(132).copy()
        elif period == "1y":
            plot_df = df.tail(252).copy()
        else:
            plot_df = df.copy()
    else:
        plot_df = df.copy()

    # BUG 5 FIX: compute VWAP on the plot window only, not the full history.
    # Cumulative VWAP on 2y data shown over a 1mo window produces nonsense values.
    plot_df = plot_df.reset_index(drop=True)
    tp = (plot_df["High"] + plot_df["Low"] + plot_df["Close"]) / 3
    plot_df["VWAP"] = (tp * plot_df["Volume"]).cumsum() / plot_df["Volume"].cumsum()

    return plot_df, stats
