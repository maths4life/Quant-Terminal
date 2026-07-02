import streamlit as st

from components.quant_search import quant_search

# Shown in the dropdown when the box is empty/focused, and matched against
# (symbol + name) as the user types. Add more here any time — no other code
# needs to change.
POPULAR = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "tag": "NSE"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "tag": "NSE"},
    {"symbol": "INFY.NS", "name": "Infosys", "tag": "NSE"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "tag": "NSE"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "tag": "NSE"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "tag": "NSE"},
    {"symbol": "^NSEI", "name": "Nifty 50 Index", "tag": "INDEX"},
    {"symbol": "^NSEBANK", "name": "Nifty Bank Index", "tag": "INDEX"},
]


def render_search(current_ticker):
    """Renders the primary search bar. Selecting a symbol — by click or by
    Enter, whether from the Popular list, a filtered match, or free-text —
    commits straight to st.session_state.ticker and reruns, so the caller
    can simply read st.session_state.ticker afterwards, exactly as before.
    """

    st.markdown('<div class="qt-search-mount">', unsafe_allow_html=True)
    result = quant_search(
        current_ticker=current_ticker,
        popular=POPULAR,
        key="qt_search",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # The component keeps returning the same value on every rerun until the
    # user makes a new selection, so dedupe against the last one we acted on
    # to avoid re-triggering st.rerun() in a loop.
    if result and result != st.session_state.get("_qt_search_committed"):
        st.session_state._qt_search_committed = result
        st.session_state.ticker = result.upper().strip()
        st.rerun()
