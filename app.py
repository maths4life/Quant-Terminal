import streamlit as st
from datetime import datetime, time as dtime
import pytz
from pathlib import Path
from streamlit_lightweight_charts import renderLightweightCharts
from utils.helpers import (
    fmt_indian,
    is_nse_open,
    rsi_label,
)
from utils.data import fetch_data

def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )
    else:
        st.error("❌ assets/style.css not found.")

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Quant Terminal",
    page_icon="💹",
    initial_sidebar_state="expanded",
)

load_css()


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "recent" not in st.session_state:
    st.session_state.recent = []


def add_recent(t):
    if t not in st.session_state.recent:
        st.session_state.recent.insert(0, t)
        st.session_state.recent = st.session_state.recent[:5]


# ── ICONS (inline SVG) ────────────────────────────────────────────────────────
ICON_SEARCH  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
ICON_CLOCK   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></svg>'
ICON_GEAR    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82c.16.39.5.7.93.84H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
ICON_BELL    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>'
ICON_CANDLE  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3M8 18v3"/><rect x="6" y="6" width="4" height="12" rx="1"/><path d="M16 3v5M16 16v5"/><rect x="14" y="8" width="4" height="8" rx="1"/></svg>'
ICON_MARKET  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m7 14 4-4 4 4 5-6"/></svg>'
ICON_LAYERS  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 2 9 5-9 5-9-5 9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/></svg>'
ICON_TIME    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
ICON_STAR    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15 9 22 9.3 17 14 18.5 21 12 17.3 5.5 21 7 14 2 9.3 9 9 12 2"/></svg>'
ICON_REFRESH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg>'
ICON_TOOL    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19 7-7 3 3-7 7-3-3z"/><path d="m18 13-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/></svg>'

# ── TOP HEADER ────────────────────────────────────────────────────────────────
market_open, market_status = is_nse_open()
ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
dot_class = "live" if market_open else "closed"

st.markdown(f"""
<div class="qt-header">
  <div class="qt-brand">
    <div class="qt-logo">Q</div>
    <div>
      <div class="qt-title">Quant Terminal</div>
      <div class="qt-subtitle">Institutional · Equity Research</div>
    </div>
  </div>
  <div class="qt-header-search">
    <span style="width:14px;height:14px;display:inline-block;">{ICON_SEARCH}</span>
    <span>Search symbols, indices, sectors…</span>
    <kbd>⌘ K</kbd>
  </div>
  <div class="qt-header-right">
    <div class="qt-chip"><span class="qt-dot {dot_class}"></span> NSE · {market_status}</div>
    <div class="qt-chip"><span style="width:12px;height:12px;display:inline-block;color:var(--text-tertiary)">{ICON_CLOCK}</span> {ist_now.strftime('%H:%M:%S')} IST</div>
    <div class="qt-icon-btn" title="Alerts">{ICON_BELL}</div>
    <div class="qt-icon-btn" title="Settings">{ICON_GEAR}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
POPULAR = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS","ICICIBANK.NS","^NSEI","^NSEBANK"]

with st.sidebar:
    # Brand block
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.6rem;padding:.25rem .25rem 1rem .25rem;">
      <div class="qt-logo" style="width:30px;height:30px;font-size:.85rem;">Q</div>
      <div>
        <div style="font-size:.78rem;font-weight:700;letter-spacing:.16em;color:#fff;text-transform:uppercase;">Controls</div>
        <div style="font-size:.6rem;letter-spacing:.16em;color:var(--text-tertiary);text-transform:uppercase;">Workspace</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SEARCH SECTION
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_SEARCH}<span>Search Symbol</span></div>', unsafe_allow_html=True)
    ticker_raw = st.text_input("Symbol", "RELIANCE.NS", label_visibility="collapsed",
                               help="NSE: .NS  |  BSE: .BO")
    ticker = ticker_raw.strip().upper()
    st.markdown('<div style="font-size:.65rem;color:var(--text-tertiary);margin-top:.45rem;letter-spacing:.04em;">e.g. INFY.NS · TCS.NS · HDFCBANK.NS · ^NSEI</div></div>', unsafe_allow_html=True)

    # POPULAR
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_STAR}<span>Popular · NSE</span></div>', unsafe_allow_html=True)
    pop_cols = st.columns(2)
    for i, sym in enumerate(POPULAR):
        if pop_cols[i % 2].button(sym.replace("^NSEI","NIFTY50").replace("^NSEBANK","BANKNIFTY").replace(".NS",""),
                                  key=f"pop_{sym}", use_container_width=True):
            st.session_state["_jump"] = sym
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # RECENTS
    if st.session_state.recent:
        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CLOCK}<span>Recent Searches</span></div>', unsafe_allow_html=True)
        cols = st.columns(min(len(st.session_state.recent), 3))
        for i, sym in enumerate(st.session_state.recent):
            if cols[i % len(cols)].button(sym.replace(".NS",""), key=f"rec_{sym}", use_container_width=True):
                st.session_state["_jump"] = sym
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "_jump" in st.session_state:
        ticker = st.session_state.pop("_jump")

    # MARKET / TIMEFRAME
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_TIME}<span>Time Frame</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.62rem;color:var(--text-tertiary);letter-spacing:.14em;text-transform:uppercase;margin-bottom:.3rem;">Period</div>', unsafe_allow_html=True)
    period = st.radio("Period", ["1mo","3mo","6mo","1y","2y","5y","max"], index=3, label_visibility="collapsed")
    st.markdown('<div style="font-size:.62rem;color:var(--text-tertiary);letter-spacing:.14em;text-transform:uppercase;margin:.55rem 0 .3rem 0;">Interval</div>', unsafe_allow_html=True)
    interval_map = {"Daily":"1d","Weekly":"1wk","Monthly":"1mo"}
    interval_label = st.radio("Interval", list(interval_map.keys()), index=0, label_visibility="collapsed")
    interval = interval_map[interval_label]
    st.markdown('</div>', unsafe_allow_html=True)

    # CHART SETTINGS / INDICATORS
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_LAYERS}<span>Indicators · Overlays</span></div>', unsafe_allow_html=True)
    show_ma20  = st.checkbox("MA 20",  True)
    show_ma50  = st.checkbox("MA 50",  True)
    show_vwap  = st.checkbox("VWAP",   False)
    show_prevc = st.checkbox("Previous Close", True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CANDLE}<span>Sub-Panels</span></div>', unsafe_allow_html=True)
    show_volume = st.checkbox("Volume",   True)
    show_rsi    = st.checkbox("RSI (14)", True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ACTIONS / MARKET STATUS
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_GEAR}<span>Actions</span></div>', unsafe_allow_html=True)
    if st.button("↺  Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"""
    <div style="margin-top:.7rem;display:flex;flex-direction:column;gap:.4rem;">
      <div class="qt-chip" style="justify-content:center;width:100%;">
        <span class="qt-dot {dot_class}"></span> NSE · {market_status}
      </div>
      <div style="font-size:.62rem;color:var(--text-tertiary);text-align:center;letter-spacing:.1em;text-transform:uppercase;">
        Data · Yahoo Finance · Delayed 15m
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)


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
change_class = "up" if change >= 0 else "down"
arrow = "▲" if change >= 0 else "▼"
exchange = "NSE" if ticker.endswith(".NS") else ("BSE" if ticker.endswith(".BO") else "INDEX")

st.markdown(f"""
<div class="qt-hero">
  <div class="qt-hero-grid">
    <div class="qt-hero-left">
      <div class="qt-hero-tags">
        <span class="qt-tag accent">● {exchange}</span>
        <span class="qt-tag">{interval_label} · {period}</span>
        <span class="qt-tag">RSI {rsi_txt}</span>
        <span class="qt-tag">Updated {date_str}</span>
      </div>
      <div class="qt-ticker">{ticker}<span class="sep">/</span><span style="color:var(--text-secondary);font-size:1.1rem;">EQUITY</span></div>
      <div class="qt-meta">Live institutional view · Yahoo Finance feed · IST {ist_now.strftime('%H:%M')}</div>
    </div>
    <div class="qt-hero-right">
      <div class="qt-price">₹{close:,.2f}</div>
      <div class="qt-change {change_class}">{arrow} {abs(change):.2f}%  ·  {'+' if change_abs>=0 else ''}{change_abs:,.2f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── METRIC ROW 1 ──────────────────────────────────────────────────────────────
st.markdown('<div class="qt-section-title">Market Snapshot</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Last Price", f"₹{close:,.2f}", f"{change:+.2f}%")
c2.metric("Day High", f"₹{stats['day_high']:,.2f}")
c3.metric("Day Low", f"₹{stats['day_low']:,.2f}")
c4.metric("Volume", fmt_indian(stats["volume"]) if "Volume" in df.columns else "—")
c5.metric("52W High", f"₹{w52_h:,.2f}", f"{abs(pct_from_high):.1f}% below ATH")
c6.metric("52W Low", f"₹{w52_l:,.2f}", f"{pct_from_low:.1f}% above")

# ── METRIC ROW 2 ──────────────────────────────────────────────────────────────
st.markdown('<div class="qt-section-title">Technical Indicators</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

if last_ma20:
    above20 = close > last_ma20
    m1.metric("MA 20", f"₹{last_ma20:,.2f}", "▲ Above" if above20 else "▼ Below")
else:
    m1.metric("MA 20", "—")

if last_ma50:
    above50 = close > last_ma50
    m2.metric("MA 50", f"₹{last_ma50:,.2f}", "▲ Above" if above50 else "▼ Below")
else:
    m2.metric("MA 50", "—")

m3.metric("RSI 14",      f"{last_rsi:.1f}" if last_rsi else "—")
m4.metric("Avg Vol 20d", fmt_indian(avg_vol20))


# ── CHART HELPERS ─────────────────────────────────────────────────────────────
def base_opts(show_time=True):
    return {
        "layout": {
            "background": {"type": "solid", "color": "#171C26"},
            "textColor": "#9BA3AF", "fontSize": 11,
            "fontFamily": "'JetBrains Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(255,255,255,0.03)"},
            "horzLines": {"color": "rgba(255,255,255,0.03)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(0,229,180,0.4)", "labelBackgroundColor": "#00E5B4"},
            "horzLine": {"color": "rgba(0,229,180,0.4)", "labelBackgroundColor": "#00E5B4"},
        },
        "rightPriceScale": {
            "borderColor": "rgba(255,255,255,0.06)", "textColor": "#9BA3AF",
            "autoScale": True, "minValue": 0,
        },
        "timeScale": {
            "borderColor": "rgba(255,255,255,0.06)", "timeVisible": show_time,
            "secondsVisible": False, "visible": show_time,
        },
    }


# ── CANDLE DATA ───────────────────────────────────────────────────────────────
candles = (
    df[["time","Open","High","Low","Close"]]
    .rename(columns={"Open":"open","High":"high","Low":"low","Close":"close"})
    .to_dict("records")
)
for r in candles:
    r["open"]  = float(r["open"])
    r["high"]  = float(r["high"])
    r["low"]   = float(r["low"])
    r["close"] = float(r["close"])

price_series = [{
    "type": "Candlestick", "data": candles,
    "options": {
        "upColor": "#00C853", "downColor": "#FF5252",
        "borderVisible": False,
        "wickUpColor": "#00C853", "wickDownColor": "#FF5252",
    }
}]

if show_ma20 and last_ma20:
    ma20d = df[["time","MA20"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
        "options": {"color": "#F5A623", "lineWidth": 1}
    })

if show_ma50 and last_ma50:
    ma50d = df[["time","MA50"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
        "options": {"color": "#4D9FFF", "lineWidth": 1}
    })

if show_vwap and last_vwap:
    vwapd = df[["time","VWAP"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
        "options": {"color": "#E879F9", "lineWidth": 1, "lineStyle": 2}
    })

if show_prevc:
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": prev_close} for r in candles],
        "options": {"color": "rgba(200,208,220,0.25)", "lineWidth": 1, "lineStyle": 2}
    })

price_opts = base_opts(show_time=not (show_volume or show_rsi))
price_opts["watermark"] = {
    "visible": True, "fontSize": 60,
    "horzAlign": "center", "vertAlign": "center",
    "color": "rgba(255,255,255,0.022)", "text": ticker,
}

charts_to_render = [{"chart": price_opts, "series": price_series}]

if show_volume and "Volume" in df.columns:
    vol_data = []
    for _, row in df.iterrows():
        c = "#00C853" if float(row["Close"]) >= float(row["Open"]) else "#FF5252"
        vol_data.append({"time": row["time"], "value": float(row["Volume"]), "color": c + "77"})
    vol_opts = base_opts(show_time=not show_rsi)
    vol_opts["rightPriceScale"]["minValue"] = 0
    charts_to_render.append({
        "chart": vol_opts,
        "series": [{"type": "Histogram", "data": vol_data,
                    "options": {"priceFormat": {"type": "volume"}, "priceScaleId": ""}}]
    })

if show_rsi:
    rsi_df   = df[["time","RSI"]].dropna()
    rsi_data = [{"time": r["time"], "value": float(r["RSI"])} for _, r in rsi_df.iterrows()]
    ob_line  = [{"time": r["time"], "value": 70.0} for _, r in rsi_df.iterrows()]
    os_line  = [{"time": r["time"], "value": 30.0} for _, r in rsi_df.iterrows()]
    rsi_opts = base_opts(show_time=True)
    rsi_opts["rightPriceScale"]["autoScale"] = False
    rsi_opts["rightPriceScale"]["minValue"]  = 0
    rsi_opts["rightPriceScale"]["maxValue"]  = 100
    charts_to_render.append({
        "chart": rsi_opts,
        "series": [
            {"type": "Line", "data": rsi_data, "options": {"color": "#A78BFA", "lineWidth": 1}},
            {"type": "Line", "data": ob_line,  "options": {"color": "rgba(255,82,82,0.45)",  "lineWidth": 1, "lineStyle": 2}},
            {"type": "Line", "data": os_line,  "options": {"color": "rgba(0,229,180,0.45)",  "lineWidth": 1, "lineStyle": 2}},
        ]
    })

total_h = 620
num_panels = len(charts_to_render)
if num_panels == 1:
    heights = [total_h]
elif num_panels == 2:
    heights = [int(total_h * 0.65), int(total_h * 0.35)]
else:
    heights = [int(total_h * 0.55), int(total_h * 0.22), int(total_h * 0.23)]

for i, h in enumerate(heights):
    charts_to_render[i]["chart"]["height"] = h


# ── CHART SHELL + TOOLBAR ─────────────────────────────────────────────────────
def pill(on, label, swatch=None):
    cls = "qt-pill on" if on else "qt-pill off"
    sw = f'<span class="swatch" style="background:{swatch};"></span>' if swatch else ''
    return f'<span class="{cls}">{sw}{label}</span>'

pills_html = "".join([
    pill(True,  "Candles", "#00C853"),
    pill(show_ma20,  "MA 20",  "#F5A623"),
    pill(show_ma50,  "MA 50",  "#4D9FFF"),
    pill(show_vwap,  "VWAP",   "#E879F9"),
    pill(show_prevc, "Prev Close", "rgba(200,208,220,.5)"),
    pill(show_volume,"Volume", "#9BA3AF"),
    pill(show_rsi,   "RSI 14", "#A78BFA"),
])

tools_html = "".join([
    f'<div class="qt-tool" title="Draw (coming soon)">{ICON_TOOL}</div>',
    f'<div class="qt-tool" title="Compare (coming soon)">{ICON_MARKET}</div>',
    f'<div class="qt-tool" title="Indicators (coming soon)">{ICON_LAYERS}</div>',
    f'<div class="qt-tool" title="Screenshot (coming soon)">{ICON_REFRESH}</div>',
])

st.markdown(f"""
<div class="qt-chart-shell">
  <div class="qt-chart-toolbar">
    <div class="qt-toolbar-group">{pills_html}</div>
    <div class="qt-toolbar-group">{tools_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── RENDER ────────────────────────────────────────────────────────────────────
try:
    renderLightweightCharts(charts_to_render, key="quant_charts")
except Exception:
    renderLightweightCharts(charts_to_render)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qt-footer">
  <div>QUANT TERMINAL · v1.0 · Institutional Build</div>
  <div>Powered by Yahoo Finance · Updated {ist_now.strftime('%d %b %Y · %H:%M:%S')} IST</div>
</div>
""", unsafe_allow_html=True)
