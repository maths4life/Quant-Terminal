import streamlit as st


PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]

INTERVALS = {
    "Daily": "1d",
    "Weekly": "1wk",
    "Monthly": "1mo",
}


def render_sidebar(
    market_status,
    dot_class,
    ICON_TIME,
    ICON_LAYERS,
    ICON_CANDLE,
    ICON_GEAR,
):
    with st.sidebar:

        # -------------------------------------------------------
        # HEADER
        # -------------------------------------------------------

        st.markdown("""
        <div style="
            display:flex;
            align-items:center;
            gap:.75rem;
            padding:.4rem .25rem 1rem .25rem;
            border-bottom:1px solid var(--border);
            margin-bottom:1rem;
        ">
            <div class="qt-logo">Q</div>

            <div>
                <div class="qt-title" style="font-size:.84rem;">
                    Controls
                </div>

                <div class="qt-subtitle">
                    Workspace
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # =======================================================
        # TIME FRAME
        # =======================================================

        st.markdown(
            f"""
            <div class="qt-side-section">
            <div class="qt-side-head">
            {ICON_TIME}
            <span>Time Frame</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        period = st.radio(
            "",
            PERIODS,
            horizontal=True,
            index=3,
            label_visibility="collapsed",
        )

        interval_label = st.radio(
            "",
            list(INTERVALS.keys()),
            horizontal=True,
            index=0,
            label_visibility="collapsed",
        )

        interval = INTERVALS[interval_label]

        st.markdown("</div>", unsafe_allow_html=True)

        # Divider
        st.divider()

        # =======================================================
        # INDICATORS
        # =======================================================

        st.markdown(
            f"""
            <div class="qt-side-section">
            <div class="qt-side-head">
            {ICON_LAYERS}
            <span>Indicators</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        show_ma20 = st.checkbox("📈 MA 20", value=True)
        show_ma50 = st.checkbox("📈 MA 50", value=True)
        show_vwap = st.checkbox("〰️ VWAP", value=False)
        show_prevc = st.checkbox("📊 Previous Close", value=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # =======================================================
        # SUB PANELS
        # =======================================================

        st.markdown(
            f"""
            <div class="qt-side-section">
            <div class="qt-side-head">
            {ICON_CANDLE}
            <span>Sub Panels</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        show_volume = st.checkbox("📊 Volume", value=True)
        show_rsi = st.checkbox("📉 RSI (14)", value=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # =======================================================
        # ACTIONS
        # =======================================================

        st.markdown(
            f"""
            <div class="qt-side-section">
            <div class="qt-side-head">
            {ICON_GEAR}
            <span>Actions</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "↻ Refresh Data",
            use_container_width=True,
            type="secondary",
        ):
            st.cache_data.clear()
            st.toast("Market data refreshed")
            st.rerun()

        st.markdown(
            f"""
            <div style="margin-top:1rem">

                <div class="qt-chip"
                     style="justify-content:center;width:100%;">

                    <span class="qt-dot {dot_class}"></span>

                    NSE · {market_status}

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "timeframe": {
            "period": period,
            "interval": interval,
            "label": interval_label,
        },
        "indicators": {
            "ma20": show_ma20,
            "ma50": show_ma50,
            "vwap": show_vwap,
            "prev_close": show_prevc,
        },
        "panels": {
            "volume": show_volume,
            "rsi": show_rsi,
        },
    }