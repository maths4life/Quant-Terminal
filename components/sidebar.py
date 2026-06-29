import streamlit as st

POPULAR = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "SBIN.NS",
    "ICICIBANK.NS",
    "^NSEI",
    "^NSEBANK",
]


def render_sidebar(
    recent,
    market_status,
    dot_class,
    ICON_SEARCH,
    ICON_STAR,
    ICON_CLOCK,
    ICON_TIME,
    ICON_LAYERS,
    ICON_CANDLE,
    ICON_GEAR,
):
    with st.sidebar:

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:.6rem;padding:.25rem .25rem 1rem .25rem;">
          <div class="qt-logo" style="width:30px;height:30px;font-size:.85rem;">Q</div>
          <div>
            <div style="font-size:.78rem;font-weight:700;letter-spacing:.16em;color:#fff;text-transform:uppercase;">Controls</div>
            <div style="font-size:.6rem;letter-spacing:.16em;color:var(--text-tertiary);text-transform:uppercase;">Workspace</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_SEARCH}<span>Search Symbol</span></div>', unsafe_allow_html=True)

            # Initialize only once
        if "ticker" not in st.session_state:
            st.session_state["ticker"] = "RELIANCE.NS"

        ticker = st.text_input(
            "Symbol",
            key="ticker",
            label_visibility="collapsed",
            help="NSE: .NS | BSE: .BO",
        ).strip().upper()

        st.markdown(
            '<div style="font-size:.65rem;color:var(--text-tertiary);margin-top:.45rem;letter-spacing:.04em;">'
            'e.g. INFY.NS · TCS.NS · HDFCBANK.NS · ^NSEI'
            '</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_STAR}<span>Popular · NSE</span></div>', unsafe_allow_html=True)

        pop_cols = st.columns(2)

        for i, sym in enumerate(POPULAR):
            if pop_cols[i % 2].button(
                sym.replace("^NSEI", "NIFTY50")
                   .replace("^NSEBANK", "BANKNIFTY")
                   .replace(".NS", ""),
                key=f"pop_{sym}",
                use_container_width=True,
            ):
                st.session_state["ticker"] = sym
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        if recent:
            st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CLOCK}<span>Recent Searches</span></div>', unsafe_allow_html=True)

            cols = st.columns(min(len(recent), 3))

            for i, sym in enumerate(recent):
                if cols[i % len(cols)].button(
                    sym.replace(".NS", ""),
                    key=f"rec_{sym}",
                    use_container_width=True,
                ):
                    st.session_state["ticker"] = sym
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_TIME}<span>Time Frame</span></div>', unsafe_allow_html=True)

        period = st.radio(
            "Period",
            ["1mo","3mo","6mo","1y","2y","5y","max"],
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

        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_LAYERS}<span>Indicators · Overlays</span></div>', unsafe_allow_html=True)

        show_ma20 = st.checkbox("MA 20", True)
        show_ma50 = st.checkbox("MA 50", True)
        show_vwap = st.checkbox("VWAP", False)
        show_prevc = st.checkbox("Previous Close", True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CANDLE}<span>Sub-Panels</span></div>', unsafe_allow_html=True)

        show_volume = st.checkbox("Volume", True)
        show_rsi = st.checkbox("RSI (14)", True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_GEAR}<span>Actions</span></div>', unsafe_allow_html=True)

        if st.button("↺ Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown(f"""
        <div style="margin-top:.7rem;display:flex;flex-direction:column;gap:.4rem;">
          <div class="qt-chip" style="justify-content:center;width:100%;">
            <span class="qt-dot {dot_class}"></span>
            NSE · {market_status}
          </div>
        </div>
        """, unsafe_allow_html=True)

    return {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "interval_label": interval_label,
        "show_ma20": show_ma20,
        "show_ma50": show_ma50,
        "show_vwap": show_vwap,
        "show_prevc": show_prevc,
        "show_volume": show_volume,
        "show_rsi": show_rsi,
    }