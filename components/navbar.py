import streamlit as st
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def render_navbar(market_open, market_status, icon_clock, icon_bell, icon_gear):
    """Top brand bar. Rendered with st.markdown (not components.html) so it
    shares the page's stylesheet and CSS variables, and so its height can
    flex naturally instead of clipping/overlapping on smaller screens."""
    ist_now = datetime.now(IST)
    dot_class = "live" if market_open else "closed"

    st.markdown(
        f"""
<div class="qt-header">
    <div class="qt-brand">
        <div class="qt-logo">Q</div>
        <div>
            <div class="qt-title">Quant Terminal</div>
            <div class="qt-subtitle">Institutional Research Platform</div>
        </div>
    </div>
    <div class="qt-header-right">
        <div class="qt-chip"><span class="qt-dot {dot_class}"></span>NSE · {market_status}</div>
        <div class="qt-chip">{icon_clock}&nbsp;{ist_now.strftime("%H:%M:%S")} IST</div>
        <div class="qt-icon-btn" title="Notifications">{icon_bell}</div>
        <div class="qt-icon-btn" title="Settings">{icon_gear}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
