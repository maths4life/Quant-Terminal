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


def render_search(current_ticker, recent):

    st.markdown(
        """
<div class="qt-search-card">

<div class="qt-search-title">
🔍 Search & Analyze
</div>

<div class="qt-search-subtitle">
Search any NSE/BSE stock or market index
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([6, 1])

    with col1:

        ticker = st.text_input(
            "",
            value=current_ticker,
            placeholder="Example: RELIANCE.NS, TCS.NS, ^NSEI",
            label_visibility="collapsed",
            key="search_box",
        )

    with col2:

        analyze = st.button(
            "Analyze",
            key="search_analyze_btn",
            use_container_width=True,
        )

    st.markdown(
        '<div class="qt-search-small-title">Popular</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    for i, sym in enumerate(POPULAR):

        label = (
            sym.replace(".NS", "")
            .replace("^NSEI", "NIFTY50")
            .replace("^NSEBANK", "BANKNIFTY")
        )

        if cols[i % 4].button(
            label,
            key=f"popular_{sym}",
            use_container_width=True,
        ):
            ticker = sym
            analyze = True

    if recent:

        st.markdown(
            '<div class="qt-search-small-title">Recent Searches</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(min(4, len(recent)))

        for i, sym in enumerate(recent):

            if cols[i % len(cols)].button(
                sym.replace(".NS", ""),
                key=f"recent_{sym}",
                use_container_width=True,
            ):
                ticker = sym
                analyze = True

    return ticker.upper().strip(), analyze