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
    """UI/UX Pro Max Instrument Telemetry Banner.
    High-density layout, precise tabular numbers, and dynamic delta badges.
    """
    is_gain = change >= 0
    change_tone = "gain" if is_gain else "loss"
    sign_str = "+" if is_gain else ""
    ist_now = datetime.now(IST)

    # Format RSI badge tone
    rsi_tag_class = "highlight"
    if "Overbought" in rsi_txt:
        rsi_tag_class = "gain"
    elif "Oversold" in rsi_txt:
        rsi_tag_class = "loss"

    render_html(
        f"""
<section class="qt-hero-card">
    <div class="qt-hero-grid">
        <div class="qt-hero-primary">
            <div class="qt-ticker-row">
                <h1 class="qt-symbol">{ticker}</h1>
                <span class="qt-asset-pill">NSE: EQUITIES</span>
            </div>

            {f'<div class="qt-company-title">{company_name}</div>' if company_name else ''}
            
            {profile_html}

            <div class="qt-tags-row">
                <span class="qt-tag highlight">{interval_label} Interval</span>
                <span class="qt-tag">{period.upper()} Window</span>
                <span class="qt-tag {rsi_tag_class}">RSI {rsi_txt}</span>
                <span class="qt-tag">Updated {date_str}</span>
            </div>
        </div>

        <div class="qt-hero-secondary">
            <div class="qt-price-display">₹{close:,.2f}</div>
            <div class="qt-delta-pill {change_tone}">
                <span>{sign_str}{change:.2f}%</span>
                <span>({sign_str}₹{abs(change_abs):,.2f})</span>
            </div>
            <div class="qt-time-stamp">Live Feed · {ist_now.strftime('%H:%M:%S')} IST</div>
        </div>
    </div>
</section>
"""
    )
