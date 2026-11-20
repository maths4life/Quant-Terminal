import streamlit as st
from utils.helpers import render_html

PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]

PERIOD_LABELS = {
    "1mo": "1M", "3mo": "3M", "6mo": "6M", "1y": "1Y",
    "2y": "2Y", "5y": "5Y", "max": "Max",
}

INTERVALS = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo",
}


def _section_open(label):
    render_html(f'<div class="qt-side-section"><div class="qt-side-head">{label}</div>')


def _section_close():
    render_html("</div>")


def _sublabel(text):
    render_html(f'<div class="qt-side-sublabel">{text}</div>')


def render_sidebar(market_status, dot_class, ICON_TIME, ICON_LAYERS, ICON_CANDLE, ICON_GEAR):
    with st.sidebar:
        # ── TIMEFRAME ───────────────────────────────────────────────
        _section_open("Timeframe")

        _sublabel("Period")
        with st.container(key="qt_period_wrap"):
            period = st.radio(
                "Period", PERIODS, horizontal=True, index=3,
                format_func=lambda p: PERIOD_LABELS.get(p, p),
                label_visibility="collapsed", key="qt_period",
            )

        _sublabel("Interval")
        with st.container(key="qt_interval_wrap"):
            interval_label = st.radio(
                "Interval", list(INTERVALS.keys()), horizontal=True, index=0,
                label_visibility="collapsed", key="qt_interval",
            )
        interval = INTERVALS[interval_label]

        _section_close()

        # ── TECHNICAL OVERLAYS (No emojis, clean labels) ────────────
        _section_open("Overlays")

        show_ma20 = st.checkbox("20-day moving average", value=True, key="qt_ma20")
        show_ma50 = st.checkbox("50-day moving average", value=True, key="qt_ma50")
        show_vwap = st.checkbox("Volume weighted average", value=False, key="qt_vwap")
        show_prevc = st.checkbox("Previous close line", value=True, key="qt_prevc")

        _section_close()

        # ── SUB PANELS ──────────────────────────────────────────────
        _section_open("Sub panels")

        show_volume = st.checkbox("Volume histogram", value=True, key="qt_volume")
        show_rsi = st.checkbox("Relative strength index (14)", value=True, key="qt_rsi")

        _section_close()

        # ── ACTIONS & STATUS ────────────────────────────────────────
        _section_open("Data feed")

        if st.button("Refresh market data", use_container_width=True, key="qt_refresh"):
            with st.spinner("Updating prices…"):
                st.cache_data.clear()
            st.toast("Data refreshed")
            st.rerun()

        status_class = "status-open" if "open" in market_status.lower() else "status-closed"
        render_html(
            f"""
            <div class="hm-side-feed">
                <span class="hm-meta-item {status_class}">NSE {market_status.lower()}</span>
                <span class="hm-feed-note">sub-second local cache</span>
            </div>
            """
        )

        _section_close()

    return {
        "timeframe": {"period": period, "interval": interval, "label": interval_label},
        "indicators": {
            "ma20": show_ma20,
            "ma50": show_ma50,
            "vwap": show_vwap,
            "prev_close": show_prevc,
        },
        "panels": {"volume": show_volume, "rsi": show_rsi},
    }
