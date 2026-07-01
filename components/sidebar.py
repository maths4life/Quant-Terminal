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
        st.write("Controls")

        st.write("Time Frame")
        period = st.radio(
            "Period",
            PERIODS,
            horizontal=True,
            index=3,
            label_visibility="collapsed",
        )

        interval_label = st.radio(
            "Interval",
            list(INTERVALS.keys()),
            horizontal=True,
            index=0,
            label_visibility="collapsed",
        )
        interval = INTERVALS[interval_label]

        st.write("Indicators")
        show_ma20 = st.checkbox("MA 20", value=True)
        show_ma50 = st.checkbox("MA 50", value=True)
        show_vwap = st.checkbox("VWAP", value=False)
        show_prevc = st.checkbox("Previous Close", value=True)

        st.write("Sub Panels")
        show_volume = st.checkbox("Volume", value=True)
        show_rsi = st.checkbox("RSI (14)", value=True)

        st.write("Actions")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.write(f"NSE · {market_status}")

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
