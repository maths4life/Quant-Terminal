import streamlit as st
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def render_navbar(market_open, market_status, icon_clock, icon_bell, icon_gear, active_page="home"):
    """Top brand bar. Rendered with st.markdown (not components.html) so it
    shares the page's stylesheet and CSS variables, and so its height can
    flex naturally instead of clipping/overlapping on smaller screens.

    The AI Insights entry is a plain <a href="?page=insights"> rather than
    a Streamlit widget — real st.button/st.* widgets can't be embedded
    inside a raw HTML block, which is also why the bell/gear icons above
    are inert. An anchor tag updates st.query_params on click and triggers
    a normal rerun, which app.py reads to decide which page to render.
    """
    ist_now = datetime.now(IST)
    dot_class = "live" if market_open else "closed"
    insights_active = "active" if active_page == "insights" else ""

    st.markdown(
        f"""
<div class="qt-header">
    <div class="qt-brand">
        <div class="qt-logo">Q</div>
        <div>
            <div class="qt-title">Quant Terminal</div>
            <div class="qt-subtitle">Institutional Research Platform</div>
        </div>
        <a href="?page=insights" target="_self" class="qt-nav-btn {insights_active}">
            <span>🧠</span>AI Insights
        </a>
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