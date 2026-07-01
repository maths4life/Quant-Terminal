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


def _select_ticker(symbol: str):
    st.session_state.ticker = symbol.upper().strip()
    st.rerun()


def render_search(current_ticker, recent):
    """Renders the search card. Ticker selection is committed straight to
    st.session_state.ticker and triggers a rerun, so the caller can simply
    read st.session_state.ticker afterwards — no return-value plumbing."""

    st.markdown(
        """
<div class="qt-search-card">
<div class="qt-search-title">🔍 Search &amp; Analyze</div>
<div class="qt-search-subtitle">Search any NSE/BSE stock or market index</div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([6, 1])
    with col1:
        typed = st.text_input(
            "Ticker",
            value=current_ticker,
            placeholder="Example: RELIANCE.NS, TCS.NS, ^NSEI",
            label_visibility="collapsed",
            key="search_box",
        )
    with col2:
        if st.button("Analyze", key="search_analyze_btn", use_container_width=True):
            if typed.strip():
                _select_ticker(typed)

    st.markdown('<div class="qt-search-small-title">Popular</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, sym in enumerate(POPULAR):
        label = sym.replace(".NS", "").replace("^NSEI", "NIFTY50").replace("^NSEBANK", "BANKNIFTY")
        with cols[i % 4]:
            st.markdown('<div class="qt-secondary-btn">', unsafe_allow_html=True)
            if st.button(label, key=f"popular_{sym}", use_container_width=True):
                _select_ticker(sym)
            st.markdown("</div>", unsafe_allow_html=True)

    if recent:
        st.markdown('<div class="qt-search-small-title">Recent Searches</div>', unsafe_allow_html=True)
        cols = st.columns(min(4, len(recent)))
        for i, sym in enumerate(recent):
            with cols[i % len(cols)]:
                st.markdown('<div class="qt-secondary-btn">', unsafe_allow_html=True)
                if st.button(sym.replace(".NS", ""), key=f"recent_{sym}", use_container_width=True):
                    _select_ticker(sym)
                st.markdown("</div>", unsafe_allow_html=True)
