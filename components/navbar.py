import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz


def render_navbar(
    current_ticker,
    market_open,
    market_status,
    icon_clock,
    icon_bell,
    icon_gear,
):
    ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
    dot_class = "live" if market_open else "closed"

    # Build HTML string first, then pass to components.html.
    # st.markdown with unsafe_allow_html=True escapes the block as plain text
    # in newer Streamlit versions when SVG tags are present in the f-string.
    # components.v1.html always renders raw HTML, bypassing the sanitizer.
    html = (
        '<div class="qt-header">'
        '<div class="qt-brand">'
        '<div class="qt-logo">Q</div>'
        '<div class="qt-brand-text">'
        '<div class="qt-title">Quant Terminal</div>'
        '<div class="qt-subtitle">Institutional Research Platform</div>'
        '</div>'
        '</div>'
        '<div class="qt-header-right">'
        f'<div class="qt-chip"><span class="qt-dot {dot_class}"></span>NSE · {market_status}</div>'
        f'<div class="qt-chip">{icon_clock}{ist_now.strftime("%H:%M:%S")} IST</div>'
        f'<div class="qt-icon-btn">{icon_bell}</div>'
        f'<div class="qt-icon-btn">{icon_gear}</div>'
        '</div>'
        '</div>'
    )

    components.html(html, height=70, scrolling=False)
