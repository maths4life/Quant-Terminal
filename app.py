import streamlit as st

from assets.theme import load_css

from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.hero import render_hero
from components.chart import render_chart
from components.metrics import render_metrics
from components.footer import render_footer
from datetime import datetime
import pytz

from utils.data import fetch_data
from utils.helpers import (
    fmt_indian,
    is_nse_open,
    rsi_label,
)
from utils.icons import (
    ICON_SEARCH,
    ICON_CLOCK,
    ICON_GEAR,
    ICON_BELL,
    ICON_CANDLE,
    ICON_MARKET,
    ICON_LAYERS,
    ICON_TIME,
    ICON_STAR,
    ICON_REFRESH,
    ICON_TOOL,
)

# ───────────────────────────────────────────────────────────────
# PAGE CONFIG
# ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Quant Terminal",
    page_icon="💹",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────────────────────
# LOAD THEME
# ───────────────────────────────────────────────────────────────
load_css()

# ───────────────────────────────────────────────────────────────
# SESSION STATE
# ───────────────────────────────────────────────────────────────
if "recent" not in st.session_state:
    st.session_state.recent = []


def add_recent(ticker):
    if ticker not in st.session_state.recent:
        st.session_state.recent.insert(0, ticker)
        st.session_state.recent = st.session_state.recent[:5]

# ── TOP HEADER ────────────────────────────────────────────────────────────────
market_open, market_status = is_nse_open()

ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
dot_class = "live" if market_open else "closed"

render_navbar(
    market_open=market_open,
    market_status=market_status,
    icon_search=ICON_SEARCH,
    icon_clock=ICON_CLOCK,
    icon_bell=ICON_BELL,
    icon_gear=ICON_GEAR,
)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

sidebar = render_sidebar(
    recent=st.session_state.recent,
    market_status=market_status,
    dot_class=dot_class,
    ICON_SEARCH=ICON_SEARCH,
    ICON_STAR=ICON_STAR,
    ICON_CLOCK=ICON_CLOCK,
    ICON_TIME=ICON_TIME,
    ICON_LAYERS=ICON_LAYERS,
    ICON_CANDLE=ICON_CANDLE,
    ICON_GEAR=ICON_GEAR,
)
ticker = sidebar["ticker"]
period = sidebar["period"]
interval = sidebar["interval"]
interval_label = sidebar["interval_label"]

show_ma20 = sidebar["show_ma20"]
show_ma50 = sidebar["show_ma50"]
show_vwap = sidebar["show_vwap"]
show_prevc = sidebar["show_prevc"]

show_volume = sidebar["show_volume"]
show_rsi = sidebar["show_rsi"]


# ── FETCH DATA ────────────────────────────────────────────────────────────────
with st.spinner(f"Loading {ticker}  ·  {period}  ·  {interval_label}…"):
    result = fetch_data(ticker, period, interval)

if result is None:
    st.error(f"No data found for '{ticker}'")
    st.info("Try: RELIANCE.NS  ·  INFY.NS  ·  TCS.NS  ·  HDFCBANK.NS  ·  ^NSEI")
    st.stop()

df, stats = result

if len(df) < 55:
    st.warning("Limited history — MA50 / RSI readings may be inaccurate. Try a longer period.")

add_recent(ticker)

last = df.iloc[-1]
prev = df.iloc[-2]

close = float(last["Close"])
prev_close = float(prev["Close"])

change = ((close - prev_close) / prev_close) * 100
change_abs = close - prev_close

# Read values from stats dictionary
w52_h = stats["high_52w"]
w52_l = stats["low_52w"]

pct_from_high = ((close - w52_h) / w52_h) * 100
pct_from_low = ((close - w52_l) / w52_l) * 100

last_ma20 = float(df["MA20"].dropna().iloc[-1]) if not df["MA20"].dropna().empty else None
last_ma50 = float(df["MA50"].dropna().iloc[-1]) if not df["MA50"].dropna().empty else None
last_rsi = float(df["RSI"].dropna().iloc[-1]) if not df["RSI"].dropna().empty else None
last_vwap = float(df["VWAP"].dropna().iloc[-1]) if not df["VWAP"].dropna().empty else None

avg_vol20 = stats["avg_volume_20"]

rsi_txt, rsi_color = rsi_label(last_rsi)

date_str = last["Date"].strftime("%d %b %Y") if hasattr(last["Date"], "strftime") else ""
# ── HERO CARD ─────────────────────────────────────────────────────────────────
render_hero(
    ticker=ticker,
    interval_label=interval_label,
    period=period,
    close=close,
    change=change,
    change_abs=change_abs,
    rsi_txt=rsi_txt,
    date_str=date_str,
)

# ── METRIC ROW  ──────────────────────────────────────────────────────────────
render_metrics(
    df=df,
    stats=stats,
    close=close,
    change=change,
    w52_h=w52_h,
    w52_l=w52_l,
    pct_from_high=pct_from_high,
    pct_from_low=pct_from_low,
    last_ma20=last_ma20,
    last_ma50=last_ma50,
    last_rsi=last_rsi,
    avg_vol20=avg_vol20,
    fmt_indian=fmt_indian,
)

# ── CHART HELPERS ─────────────────────────────────────────────────────────────
render_chart(
    df=df,
    ticker=ticker,
    prev_close=prev_close,

    show_ma20=show_ma20,
    show_ma50=show_ma50,
    show_vwap=show_vwap,
    show_prevc=show_prevc,
    show_volume=show_volume,
    show_rsi=show_rsi,

    last_ma20=last_ma20,
    last_ma50=last_ma50,
    last_vwap=last_vwap,

    ICON_TOOL=ICON_TOOL,
    ICON_MARKET=ICON_MARKET,
    ICON_LAYERS=ICON_LAYERS,
    ICON_REFRESH=ICON_REFRESH,
)


# ── FOOTER ────────────────────────────────────────────────────────────────────
render_footer()