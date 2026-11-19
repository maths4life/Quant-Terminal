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
    """Hallmark v2.0.0 instrument telemetry banner.
    Solid high-contrast typography (no gradient text), no middle-dot meta strings,
    no decorative status dots, and quiet hairline frame.
    """
    change_tone = "delta-positive" if change >= 0 else "delta-negative"
    sign_str = "+" if change >= 0 else ""
    ist_now = datetime.now(IST)

    render_html(
        f"""
<section class="hm-hero-card">
    <div class="hm-hero-grid">
        <div class="hm-hero-primary">
            <div class="hm-tag-row">
                <span class="hm-tag">{interval_label}</span>
                <span class="hm-tag">{period} window</span>
                <span class="hm-tag">RSI {rsi_txt}</span>
                <span class="hm-tag">Updated {date_str}</span>
            </div>

            <div class="hm-ticker-title">
                <h1 class="hm-symbol">{ticker}</h1>
                <span class="hm-asset-class">equity</span>
            </div>

            {f'<div class="hm-company-name">{company_name}</div>' if company_name else ''}
            {profile_html}
        </div>

        <div class="hm-hero-secondary">
            <div class="hm-price-display">₹{close:,.2f}</div>
            <div class="hm-delta-badge {change_tone}">
                <span>{sign_str}{change:.2f}%</span>
                <span class="hm-delta-abs">{sign_str}{change_abs:,.2f}</span>
            </div>
            <div class="hm-time-label">{ist_now.strftime('%H:%M')} IST timestamp</div>
        </div>
    </div>
</section>
"""
    )
