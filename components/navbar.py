from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_navbar(market_open, market_status, icon_clock, icon_bell, icon_gear, active_page="landing"):
    """Floating top brand navigation bar.
    Adheres strictly to landing-page-design B7:
    Translucent surface over background blur, compact, centered,
    with clear indicated state for the current active page.
    """
    ist_now = datetime.now(IST)
    dot_class = "live" if market_open else "closed"

    landing_active = "active" if active_page in ("landing", "overview") else ""
    terminal_active = "active" if active_page in ("terminal", "home", "") else ""
    insights_active = "active" if active_page == "insights" else ""

    render_html(
        f"""
<div class="qt-header">
    <div class="qt-brand">
        <a href="?page=landing" target="_self" style="text-decoration:none; display:flex; align-items:center; gap:10px;">
            <div class="qt-logo">Q</div>
            <div>
                <div class="qt-title">Quant Terminal</div>
                <div class="qt-subtitle">Institutional Research</div>
            </div>
        </a>
    </div>

    <div class="qt-nav-links">
        <a href="?page=landing" target="_self" class="qt-nav-link {landing_active}">Overview</a>
        <a href="?page=terminal" target="_self" class="qt-nav-link {terminal_active}">Live Terminal</a>
        <a href="?page=insights" target="_self" class="qt-nav-link {insights_active}">AI Insights</a>
    </div>

    <div class="qt-header-right">
        <div class="qt-chip">
            <span class="qt-dot {dot_class}"></span>NSE · {market_status}
        </div>
        <div class="qt-chip">
            {icon_clock}&nbsp;{ist_now.strftime("%H:%M:%S")} IST
        </div>
        <div class="qt-icon-btn" title="System Notifications">{icon_bell}</div>
        <div class="qt-icon-btn" title="Terminal Settings">{icon_gear}</div>
    </div>
</div>
"""
    )
