from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_footer():
    """Hallmark v2.0.0 quiet footer.
    No middle-dot joined meta strings, no tracked uppercase, quiet muted text.
    """
    ist_now = datetime.now(IST)

    render_html(
        f"""
<footer class="hm-footer">
    <div class="hm-footer-info">
        <span>Quant Terminal</span>
        <span class="hm-footer-sub">Systematic equity telemetry</span>
    </div>
    <div class="hm-footer-links">
        <a href="#terms" onclick="return false;">Terms</a>
        <a href="#privacy" onclick="return false;">Privacy</a>
        <a href="#disclaimer" onclick="return false;">Risk disclosure</a>
    </div>
    <div class="hm-footer-stamp">
        Market data via Yahoo Finance · Refreshed {ist_now.strftime('%d %b %Y, %H:%M:%S')} IST
    </div>
</footer>
"""
    )
