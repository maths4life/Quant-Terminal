from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_footer():
    """UI/UX Pro Max Institutional Footer."""
    ist_now = datetime.now(IST)

    render_html(
        f"""
<footer class="qt-footer">
    <div class="qt-footer-brand">
        <span>Quant Terminal PRO</span>
        <span style="color: var(--color-text-dim); margin-left: 8px;">Institutional Equity Intelligence</span>
    </div>
    <div class="qt-footer-links">
        <a href="#terms" onclick="return false;">Platform Terms</a>
        <a href="#privacy" onclick="return false;">Privacy Policy</a>
        <a href="#disclaimer" onclick="return false;">NSE Market Disclaimer</a>
    </div>
    <div style="font-family: var(--font-mono); font-size: 10px;">
        Data synced via Yahoo Finance · {ist_now.strftime('%d %b %Y, %H:%M:%S')} IST
    </div>
</footer>
"""
    )
