import streamlit as st
import yfinance as yf
import pandas as pd

from utils.helpers import compute_rsi


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

    # Technical Indicators
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = compute_rsi(df["Close"])

    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()

    # Latest candle
    latest = df.iloc[-1]

    # Use the last 252 trading sessions for 52-week statistics
    yearly = df.tail(252)

    stats = {
        "day_high": float(latest["High"]),
        "day_low": float(latest["Low"]),
        "day_open": float(latest["Open"]),
        "day_close": float(latest["Close"]),
        "volume": int(latest["Volume"]),
        "avg_volume_20": int(yearly["Volume"].tail(20).mean()),
        "high_52w": float(yearly["High"].max()),
        "low_52w": float(yearly["Low"].min()),
    }

    # Return only the requested period for plotting
    if history_period != period:
        if period == "1mo":
            plot_df = df.tail(22)
        elif period == "3mo":
            plot_df = df.tail(66)
        elif period == "6mo":
            plot_df = df.tail(132)
        elif period == "1y":
            plot_df = df.tail(252)
        else:
            plot_df = df.copy()
    else:
        plot_df = df

    return plot_df, stats