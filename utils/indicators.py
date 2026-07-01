"""Technical indicator calculations, kept separate from data fetching
and from display formatting so each module has one job."""
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    return df


def compute_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """VWAP must be computed on the visible plot window only — running it
    over a longer fetch window (e.g. 2y history sliced to 1mo view) produces
    meaningless cumulative values."""
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df


def rsi_label(v):
    if v is None:
        return "—", "muted"
    if v >= 70:
        return f"{v:.1f} OVERBOUGHT", "bearish"
    if v <= 30:
        return f"{v:.1f} OVERSOLD", "bullish"
    return f"{v:.1f} NEUTRAL", "muted"
