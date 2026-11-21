from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_navbar(market_open, market_status, icon_clock, icon_bell, icon_gear, active_page="terminal"):
    """UI/UX Pro Max Institutional Navigation Bar.
    OLED dark palette, live pulse radar, active route indicators,
    and high-contrast typography.
    """
    ist_now = datetime.now(IST)
    status_text = "NSE LIVE" if market_open else f"NSE {market_status.upper() if market_status else 'CLOSED'}"
    status_tone = "status-open" if market_open else "status-closed"

    terminal_active = "active" if active_page in ("terminal", "home", "") else ""
    insights_active = "active" if active_page == "insights" else ""

    render_html(
        f"""
<header class="qt-navbar">
    <div class="qt-brand">
        <a href="?page=terminal" target="_self" class="qt-brand-link">
            <span class="qt-mark">Q</span>
            <span class="qt-wordmark">Quant Terminal</span>
            <span class="qt-pro-badge">PRO</span>
        </a>
    </div>

    <nav class="qt-nav-group">
        <a href="?page=terminal" target="_self" class="qt-nav-link {terminal_active}">Terminal</a>
        <a href="?page=insights" target="_self" class="qt-nav-link {insights_active}">AI Insights</a>
    </nav>

    <div class="qt-meta-group">
        <span class="qt-meta-pill {status_tone}">
            <span class="qt-status-pulse"></span>
            <span>{status_text}</span>
        </span>
        <span class="qt-clock-pill">
            {icon_clock}
            <span>{ist_now.strftime("%H:%M:%S")} IST</span>
        </span>
        <button type="button" class="qt-icon-btn" title="Alerts & Notifications" aria-label="Notifications">{icon_bell}</button>
        <button type="button" class="qt-icon-btn" title="Terminal Settings" aria-label="Settings">{icon_gear}</button>
    </div>
</header>
"""
    )
