from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_navbar(market_open, market_status, icon_clock, icon_bell, icon_gear, active_page="terminal"):
    """Hallmark v2.0.0 navigation bar.
    Quiet chrome: no decorative status dots, no middle-dot meta strings,
    no tracked small caps. Plain sentence-case labels and instant focus rings.
    """
    ist_now = datetime.now(IST)
    status_text = "NSE open" if market_open else "NSE closed"
    status_tone = "status-open" if market_open else "status-closed"

    terminal_active = "active" if active_page in ("terminal", "home", "") else ""
    insights_active = "active" if active_page == "insights" else ""

    render_html(
        f"""
<header class="hm-navbar">
    <div class="hm-brand">
        <a href="?page=terminal" target="_self" class="hm-brand-link">
            <span class="hm-mark">Q</span>
            <span class="hm-wordmark">Quant Terminal</span>
        </a>
    </div>

    <nav class="hm-nav-group">
        <a href="?page=terminal" target="_self" class="hm-nav-link {terminal_active}">Terminal</a>
        <a href="?page=insights" target="_self" class="hm-nav-link {insights_active}">Research insights</a>
    </nav>

    <div class="hm-meta-group">
        <span class="hm-meta-item {status_tone}">{status_text}</span>
        <span class="hm-meta-item">{ist_now.strftime("%H:%M:%S")} IST</span>
        <button type="button" class="hm-icon-control" title="Notifications" aria-label="Notifications">{icon_bell}</button>
        <button type="button" class="hm-icon-control" title="Settings" aria-label="Settings">{icon_gear}</button>
    </div>
</header>
"""
    )
