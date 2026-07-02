import streamlit as st

PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]

# Display-only labels for the period chips — the underlying values in
# PERIODS (used everywhere else, e.g. fetch_data) are unchanged.
PERIOD_LABELS = {
    "1mo": "1M", "3mo": "3M", "6mo": "6M", "1y": "1Y",
    "2y": "2Y", "5y": "5Y", "max": "MAX",
}

INTERVALS = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo",
}


def _section_open(icon, label):
    st.markdown(
        f"""<div class="qt-side-section">
        <div class="qt-side-head">{icon}<span>{label}</span></div>""",
        unsafe_allow_html=True,
    )


def _section_close():
    st.markdown("</div>", unsafe_allow_html=True)


def _sublabel(text):
    st.markdown(f'<div class="qt-side-sublabel">{text}</div>', unsafe_allow_html=True)


def render_sidebar(market_status, dot_class, ICON_TIME, ICON_LAYERS, ICON_CANDLE, ICON_GEAR):
    with st.sidebar:

        # ── HEADER ──────────────────────────────────────────────────
        st.markdown(
            """
        <div style="
            display:flex; align-items:center; gap:.75rem;
            padding:.4rem .25rem 1rem .25rem;
            border-bottom:1px solid var(--border);
            margin-bottom:1rem;
        ">
            <div class="qt-logo">Q</div>
            <div>
                <div class="qt-title" style="font-size:.84rem;">Quant Terminal</div>
                <div class="qt-subtitle">Trading Workspace</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # ── TIME FRAME ──────────────────────────────────────────────
        _section_open(ICON_TIME, "Time Frame")

        _sublabel("Period")
        with st.container(key="qt_period_wrap"):
            period = st.radio(
                "Period", PERIODS, horizontal=True, index=3,
                format_func=lambda p: PERIOD_LABELS.get(p, p.upper()),
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
        st.divider()

        # ── INDICATORS ──────────────────────────────────────────────
        _section_open(ICON_LAYERS, "Indicators")

        show_ma20 = st.checkbox("📈  MA 20", value=True, key="qt_ma20")
        show_ma50 = st.checkbox("📊  MA 50", value=True, key="qt_ma50")
        show_vwap = st.checkbox("〰️  VWAP", value=False, key="qt_vwap")
        show_prevc = st.checkbox("📍  Previous Close", value=True, key="qt_prevc")

        _section_close()
        st.divider()

        # ── SUB PANELS ──────────────────────────────────────────────
        _section_open(ICON_CANDLE, "Sub Panels")

        show_volume = st.checkbox("📶  Volume", value=True, key="qt_volume")
        show_rsi = st.checkbox("📉  RSI (14)", value=True, key="qt_rsi")

        _section_close()
        st.divider()

        # ── ACTIONS ─────────────────────────────────────────────────
        _section_open(ICON_GEAR, "Actions")

        if st.button("↻  Refresh Data", use_container_width=True, key="qt_refresh"):
            with st.spinner("Refreshing market data…"):
                st.cache_data.clear()
            st.toast("Market data refreshed", icon="✅")
            st.rerun()

        st.markdown(
            f"""
            <div class="qt-side-status">
                <div class="qt-chip" style="justify-content:center;width:100%;">
                    <span class="qt-dot {dot_class}"></span>
                    NSE &bull; {market_status}
                </div>
                <div class="qt-version-tag">Institutional Edition</div>
            </div>
            """,
            unsafe_allow_html=True,
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
