import streamlit as st


def render_sidebar(
    market_status,
    dot_class,
    ICON_TIME,
    ICON_LAYERS,
    ICON_CANDLE,
    ICON_GEAR,
):
    with st.sidebar:

        st.markdown("""
        <div style="display:flex;align-items:center;gap:.6rem;padding:.25rem .25rem 1rem .25rem;">
            <div class="qt-logo" style="width:32px;height:32px;">Q</div>

            <div>
                <div style="font-size:.82rem;font-weight:700;letter-spacing:.16em;color:#fff;text-transform:uppercase;">
                    Controls
                </div>

                <div style="font-size:.62rem;letter-spacing:.16em;color:var(--text-tertiary);text-transform:uppercase;">
                    Workspace
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- TIMEFRAME ----------------

        st.markdown(
            f'<div class="qt-side-section"><div class="qt-side-head">{ICON_TIME}<span>Time Frame</span></div>',
            unsafe_allow_html=True,
        )

        period = st.radio(
            "Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
            index=3,
            label_visibility="collapsed",
        )

        interval_map = {
            "Daily": "1d",
            "Weekly": "1wk",
            "Monthly": "1mo",
        }

        interval_label = st.radio(
            "Interval",
            list(interval_map.keys()),
            index=0,
            label_visibility="collapsed",
        )

        interval = interval_map[interval_label]

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- INDICATORS ----------------

        st.markdown(
            f'<div class="qt-side-section"><div class="qt-side-head">{ICON_LAYERS}<span>Indicators</span></div>',
            unsafe_allow_html=True,
        )

        show_ma20 = st.checkbox("MA 20", True)
        show_ma50 = st.checkbox("MA 50", True)
        show_vwap = st.checkbox("VWAP", False)
        show_prevc = st.checkbox("Previous Close", True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- SUB PANELS ----------------

        st.markdown(
            f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CANDLE}<span>Sub Panels</span></div>',
            unsafe_allow_html=True,
        )

        show_volume = st.checkbox("Volume", True)
        show_rsi = st.checkbox("RSI (14)", True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- ACTIONS ----------------

        st.markdown(
            f'<div class="qt-side-section"><div class="qt-side-head">{ICON_GEAR}<span>Actions</span></div>',
            unsafe_allow_html=True,
        )

        if st.button("↺ Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.toast("Market data refreshed")
            st.rerun()

        st.markdown(
            f"""
            <div style="margin-top:.8rem">
                <div class="qt-chip" style="justify-content:center;width:100%;">
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