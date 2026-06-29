import streamlit as st

from assets.theme import load_css

from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.hero import render_hero
from components.chart import render_chart
from components.metrics import render_metrics
from components.footer import render_footer
from components.search import render_search
from components.profile import render_profile_strip, render_key_stats
from datetime import datetime
import pytz

from utils.data import fetch_data, fetch_company_info
from utils.helpers import (
    fmt_indian,
    fmt_mcap,
    fmt_ratio,
    fmt_pct_val,
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

if "ticker" not in st.session_state:
    st.session_state.ticker = "RELIANCE.NS"

# ── TOP HEADER ────────────────────────────────────────────────────────────────
market_open, market_status = is_nse_open()
dot_class = "live" if market_open else "closed"

render_navbar(
    current_ticker=st.session_state.ticker,
    market_open=market_open,
    market_status=market_status,
    icon_clock=ICON_CLOCK,
    icon_bell=ICON_BELL,
    icon_gear=ICON_GEAR,
)

new_ticker, analyze = render_search(
    current_ticker=st.session_state.ticker,
    recent=st.session_state.recent,
)
if analyze:
    st.session_state.ticker = new_ticker.upper().strip()

# BUG 2 FIX: always read ticker from session_state AFTER render_search
# so the current run uses the just-updated value, not the stale pre-render value.
ticker = st.session_state.ticker

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

sidebar = render_sidebar(
    market_status,
    dot_class,
    ICON_TIME,
    ICON_LAYERS,
    ICON_CANDLE,
    ICON_GEAR,
)

timeframe = sidebar["timeframe"]
indicators = sidebar["indicators"]
panels = sidebar["panels"]

period = timeframe["period"]
interval = timeframe["interval"]
interval_label = timeframe["label"]

show_ma20 = indicators["ma20"]
show_ma50 = indicators["ma50"]
show_vwap = indicators["vwap"]
show_prevc = indicators["prev_close"]

show_volume = panels["volume"]
show_rsi = panels["rsi"]


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

# ── COMPANY INFO (sector / industry / fundamentals) ───────────────────────────
info = fetch_company_info(ticker)
profile_html = render_profile_strip(info)
company_name = info.get("name") or ""
if company_name.upper() == ticker.upper():
    company_name = ""

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
    company_name=company_name,
    profile_html=profile_html,
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

# ── KEY STATISTICS + 52W RANGE ────────────────────────────────────────────────
render_key_stats(
    info=info,
    close=close,
    w52_h=w52_h,
    w52_l=w52_l,
    fmt_mcap=fmt_mcap,
    fmt_ratio=fmt_ratio,
    fmt_pct_val=fmt_pct_val,
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
