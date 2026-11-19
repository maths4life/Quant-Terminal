from datetime import datetime
import pytz
from utils.helpers import render_html

IST = pytz.timezone("Asia/Kolkata")


def render_footer():
    """Institutional terminal footer.
    Adheres strictly to landing-page-design B10 (ship requirements:
    privacy policy and terms links, semantic info, live status).
    """
    ist_now = datetime.now(IST)

    render_html(
        f"""
<div class="qt-footer">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="qt-dot live"></span>
        <span>QUANT TERMINAL // v2.0 · INSTITUTIONAL BUILD</span>
    </div>
    <div class="qt-footer-links">
        <a href="#terms" onclick="return false;">Terms of Service</a>
        <a href="#privacy" onclick="return false;">Privacy Policy</a>
        <a href="#disclaimer" onclick="return false;">Risk Disclosure</a>
        <a href="https://github.com" target="_blank">Documentation</a>
    </div>
    <div>
        Telemetry: Yahoo Finance Live Feed · {ist_now.strftime('%d %b %Y · %H:%M:%S')} IST
    </div>
</div>
"""
    )
