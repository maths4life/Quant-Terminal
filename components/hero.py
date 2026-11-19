from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_hero(
    ticker,
    interval_label,
    period,
    close,
    change,
    change_abs,
    rsi_txt,
    date_str,
    company_name="",
    profile_html="",
):
    """Institutional terminal hero section.
    Adheres to Part B5:
    - Left-to-right gradient on heading text (#FFFFFF -> #9B9B9B in dark theme)
    - Max width 680px for heading group
    - Nested radius formula: 16px outer - 8px gap = 8px inner tag radius
    - Real numeric precision with Geist Mono typography
    """
    change_class = "up" if change >= 0 else "down"
    arrow = "▲" if change >= 0 else "▼"
    ist_now = datetime.now(IST)

    render_html(
        f"""
<div class="qt-hero">
<div class="qt-hero-grid">
    <div class="qt-hero-left">
        <div class="qt-hero-tags">
            <span class="qt-tag">{interval_label} · {period}</span>
            <span class="qt-tag">RSI {rsi_txt}</span>
            <span class="qt-tag">Updated {date_str}</span>
        </div>
        <div class="qt-ticker">
            <span class="qt-hero-headline">{ticker}</span>
            <span class="sep">/</span>
            <span style="color:var(--text-secondary);font-size:16px;font-weight:500;">EQUITY</span>
        </div>
        {f'<div class="qt-company-name">{company_name}</div>' if company_name else ''}
        {profile_html}
        <div class="qt-meta">Institutional telemetry · Feed latency &lt; 250ms · IST {ist_now.strftime('%H:%M')}</div>
    </div>
    <div class="qt-hero-right">
        <div class="qt-price">₹{close:,.2f}</div>
        <div class="qt-change {change_class}">
            {arrow} {abs(change):.2f}% &nbsp;·&nbsp; {'+' if change_abs >= 0 else ''}{change_abs:,.2f}
        </div>
    </div>
</div>
</div>
"""
    )
