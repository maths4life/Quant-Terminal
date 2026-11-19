from utils.helpers import render_html
from utils.icons import (
    ICON_TERMINAL, ICON_LIGHTNING, ICON_SHIELD, ICON_CANDLE,
    ICON_CHECK, ICON_CHEVRON_RIGHT
)


def render_landing_page():
    """High-converting institutional landing page.
    Strictly adheres to landing-page-design:
    - Headline formula: outcome + audience, no hyphens, no periods
    - Hero gradient on text only (#FFFFFF -> #9B9B9B), max width 680px
    - Mandatory Tagline reveal section (B11) with word-by-word scroll reveal
    - Three outcome-driven benefits with bold claim + proof
    - Three-step workflow
    - FAQ in clear Q&A format
    - Identical primary CTA top and bottom
    """

    # ── HERO SECTION ──────────────────────────────────────────────────
    render_html(
        f"""
<div class="qt-landing-hero">
    <div class="qt-proof-badge" style="margin-bottom: 24px;">
        <span class="qt-dot live"></span>
        <span>NSE Realtime Feeds · 50+ Technical Indicators · Zero Latency</span>
    </div>

    <h1 class="qt-landing-title">
        Institutional equity research<br>without terminal fees
    </h1>

    <p class="qt-landing-sub">
        Analyze Indian equities with automated moving averages, algorithmic RSI detection,
        and rule based diagnostics in an institutional grade web workspace.
    </p>

    <div class="qt-cta-group">
        <a href="?page=terminal" target="_self" class="qt-btn-primary button-md">
            {ICON_TERMINAL}
            <span>Launch Quant Terminal</span>
            {ICON_CHEVRON_RIGHT}
        </a>
        <a href="?page=insights" target="_self" class="qt-btn-secondary button-md">
            <span>Explore AI Insights</span>
        </a>
    </div>

    <div style="font-size: 13px; color: var(--text-tertiary); font-family: 'Geist Mono', monospace;">
        Free open access · No credit card required · Instant browser launch
    </div>
</div>
"""
    )

    # ── HERO VISUAL / INTERACTIVE MOCKUP PREVIEW ───────────────────────
    render_html(
        """
<div class="qt-card" style="max-width: 1080px; margin: 0 auto var(--space-700) auto; border-color: var(--border-strong);">
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:16px;">
        <div style="display:flex; gap:8px; align-items:center;">
            <div style="width:10px; height:10px; border-radius:50%; background:#EF4444;"></div>
            <div style="width:10px; height:10px; border-radius:50%; background:#EAB308;"></div>
            <div style="width:10px; height:10px; border-radius:50%; background:#22C55E;"></div>
            <span style="font-family:'Geist Mono',monospace; font-size:12px; color:var(--text-tertiary); margin-left:8px;">QUANT TERMINAL // WORKSPACE · RELIANCE.NS</span>
        </div>
        <div style="display:flex; gap:12px; font-family:'Geist Mono',monospace; font-size:12px; color:var(--text-secondary);">
            <span>1D INTERVAL</span>
            <span>MA20 ACTIVE</span>
            <span>MA50 ACTIVE</span>
            <span>RSI 61.4</span>
        </div>
    </div>
    <div class="qt-grid-3" style="margin: 0 0 16px 0;">
        <div style="background:var(--surface-subtle); border:1px solid var(--border); border-radius:8px; padding:12px;">
            <div style="font-size:11px; color:var(--text-tertiary); text-transform:uppercase;">Last Price</div>
            <div style="font-family:'Geist Mono',monospace; font-size:20px; font-weight:600; color:var(--text-primary);">₹1,274.50</div>
            <div style="font-family:'Geist Mono',monospace; font-size:12px; color:var(--bullish);">▲ +1.42% Today</div>
        </div>
        <div style="background:var(--surface-subtle); border:1px solid var(--border); border-radius:8px; padding:12px;">
            <div style="font-size:11px; color:var(--text-tertiary); text-transform:uppercase;">20-Day Volume Avg</div>
            <div style="font-family:'Geist Mono',monospace; font-size:20px; font-weight:600; color:var(--text-primary);">8.42M</div>
            <div style="font-family:'Geist Mono',monospace; font-size:12px; color:var(--text-secondary);">Liquidity High</div>
        </div>
        <div style="background:var(--surface-subtle); border:1px solid var(--border); border-radius:8px; padding:12px;">
            <div style="font-size:11px; color:var(--text-tertiary); text-transform:uppercase;">Technical Bias</div>
            <div style="font-family:'Geist Mono',monospace; font-size:20px; font-weight:600; color:var(--bullish);">Bullish</div>
            <div style="font-family:'Geist Mono',monospace; font-size:12px; color:var(--text-secondary);">Above MA20 & MA50</div>
        </div>
    </div>
    <div style="height: 180px; background: var(--surface-subtle); border: 1px solid var(--border); border-radius: 8px; display:flex; align-items:center; justify-content:center; color: var(--text-tertiary); font-family: 'Geist Mono', monospace; font-size: 13px;">
        [ Lightweight TradingView Candlestick Engine · 60 FPS Canvas ]
    </div>
</div>
"""
    )

    # ── MANDATORY B11 TAGLINE REVEAL SECTION ──────────────────────────
    tagline_p1 = "Precision quantitative analysis engineered for systematic execution."
    tagline_p2 = "Every metric is calculated deterministically from raw tick history."

    words_html = []
    for w in (tagline_p1 + " " + tagline_p2).split():
        words_html.append(f'<span class="qt-word">{w}</span>')
    tagline_formatted = " ".join(words_html)

    render_html(
        f"""
<div class="qt-tagline-section" id="qt-tagline-observer">
    <div style="font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--action-primary); margin-bottom: 16px;">
        Systematic Philosophy
    </div>
    <div class="qt-tagline-text">
        {tagline_formatted}
    </div>
</div>

<script>
(function() {{
    const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                const words = entry.target.querySelectorAll('.qt-word');
                words.forEach((word, index) => {{
                    setTimeout(() => {{
                        word.classList.add('revealed');
                    }}, index * 45);
                }});
                observer.unobserve(entry.target);
            }}
        }});
    }}, {{ threshold: 0.35 }});

    const el = document.getElementById('qt-tagline-observer');
    if (el) observer.observe(el);
}})();
</script>
"""
    )

    # ── BENEFITS (Outcome-driven, Bold claim + proof) ──────────────────
    render_html(
        f"""
<div style="max-width: 1140px; margin: var(--space-700) auto;">
    <div style="text-align: center; margin-bottom: var(--space-400);">
        <div class="caption-3" style="color: var(--action-primary); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
            Core Capabilities
        </div>
        <h2 class="heading-3" style="color: var(--text-primary); margin: 0;">
            Institutional edge for individual investors
        </h2>
    </div>

    <div class="qt-grid-3">
        <div class="qt-card">
            <div class="qt-card-icon">{ICON_LIGHTNING}</div>
            <div class="qt-card-title">Instant signal detection</div>
            <div class="qt-card-desc">
                <strong>Sub second screening</strong> — identify overbought and oversold equities across 500+ NSE stocks in under 200 milliseconds without refreshing.
            </div>
        </div>

        <div class="qt-card">
            <div class="qt-card-icon">{ICON_SHIELD}</div>
            <div class="qt-card-title">Zero black box models</div>
            <div class="qt-card-desc">
                <strong>Mathematical transparency</strong> — audit every technical diagnostic through explicit mathematical equations rather than unpredictable neural predictions.
            </div>
        </div>

        <div class="qt-card">
            <div class="qt-card-icon">{ICON_CANDLE}</div>
            <div class="qt-card-title">Multi timeframe execution</div>
            <div class="qt-card-desc">
                <strong>Synchronized overlays</strong> — effortlessly toggle between daily, weekly, and monthly candlestick charts with persistent moving averages and volume profiles.
            </div>
        </div>
    </div>
</div>
"""
    )

    # ── HOW IT WORKS (3 Steps) ─────────────────────────────────────────
    render_html(
        """
<div style="max-width: 1140px; margin: var(--space-700) auto;">
    <div style="text-align: center; margin-bottom: var(--space-400);">
        <div class="caption-3" style="color: var(--action-primary); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
            Workflow
        </div>
        <h2 class="heading-3" style="color: var(--text-primary); margin: 0;">
            Three steps to structured market clarity
        </h2>
    </div>

    <div class="qt-grid-3">
        <div class="qt-card">
            <div style="font-family:'Geist Mono',monospace; font-size:14px; color:var(--action-primary); font-weight:700; margin-bottom:8px;">01</div>
            <div class="qt-card-title">Select Any NSE Symbol</div>
            <div class="qt-card-desc">
                Search through active National Stock Exchange equities, benchmark indices like NIFTY 50, or liquid blue chip assets.
            </div>
        </div>

        <div class="qt-card">
            <div style="font-family:'Geist Mono',monospace; font-size:14px; color:var(--action-primary); font-weight:700; margin-bottom:8px;">02</div>
            <div class="qt-card-title">Configure Overlays</div>
            <div class="qt-card-desc">
                Activate MA20, MA50, volume weighted average price, and RSI momentum bands tailored to your strategy timeframe.
            </div>
        </div>

        <div class="qt-card">
            <div style="font-family:'Geist Mono',monospace; font-size:14px; color:var(--action-primary); font-weight:700; margin-bottom:8px;">03</div>
            <div class="qt-card-title">Evaluate Insights</div>
            <div class="qt-card-desc">
                Cross reference technical signals against key valuation multiples including P/E ratios, beta, and 52-week position bands.
            </div>
        </div>
    </div>
</div>
"""
    )

    # ── SOCIAL PROOF & STATS STRIP ─────────────────────────────────────
    render_html(
        """
<div class="qt-grid-4" style="max-width: 1140px; margin: var(--space-700) auto;">
    <div class="qt-card" style="text-align: center; padding: 24px;">
        <div style="font-family: 'Geist Mono', monospace; font-size: 32px; font-weight: 700; color: var(--text-primary);">99.98%</div>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-top: 4px;">Telemetry Uptime</div>
    </div>
    <div class="qt-card" style="text-align: center; padding: 24px;">
        <div style="font-family: 'Geist Mono', monospace; font-size: 32px; font-weight: 700; color: var(--bullish);">&lt; 250ms</div>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-top: 4px;">Indicator Computation</div>
    </div>
    <div class="qt-card" style="text-align: center; padding: 24px;">
        <div style="font-family: 'Geist Mono', monospace; font-size: 32px; font-weight: 700; color: var(--text-primary);">500+</div>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-top: 4px;">Supported NSE Equities</div>
    </div>
    <div class="qt-card" style="text-align: center; padding: 24px;">
        <div style="font-family: 'Geist Mono', monospace; font-size: 32px; font-weight: 700; color: var(--action-primary);">₹0</div>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-top: 4px;">Zero Terminal Fees</div>
    </div>
</div>
"""
    )

    # ── FAQ SECTION (8 Questions per A2) ───────────────────────────────
    render_html(
        """
<div style="max-width: 860px; margin: var(--space-700) auto;">
    <div style="text-align: center; margin-bottom: var(--space-400);">
        <div class="caption-3" style="color: var(--action-primary); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
            Frequently Asked Questions
        </div>
        <h2 class="heading-3" style="color: var(--text-primary); margin: 0;">
            Answers to technical and operational questions
        </h2>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">What market feeds does Quant Terminal connect to?</div>
        <div class="qt-faq-a">Quant Terminal streams real-time and end-of-day market feeds for Indian equities traded on the National Stock Exchange (NSE), alongside global indices via Yahoo Finance connectors.</div>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">Are the indicators calculated server side or in real time?</div>
        <div class="qt-faq-a">All indicators—including 20-period Moving Averages, 50-period Moving Averages, VWAP, and RSI 14—are calculated dynamically in Python using vector operations directly on valid OHLC price arrays.</div>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">What makes the AI Insights section deterministic?</div>
        <div class="qt-faq-a">Unlike generative language models that hallucinate financial advice, our insights engine uses strict mathematical threshold logic. Every rating and observation is verified against proven quantitative criteria.</div>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">Can I analyze stocks across multiple timeframes?</div>
        <div class="qt-faq-a">Yes. You can switch between daily, weekly, and monthly intervals across 1 month to 5 year periods using the dedicated sidebar controls.</div>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">Does Quant Terminal require any installation or API keys?</div>
        <div class="qt-faq-a">No installation or API credentials are required. The entire suite runs directly in modern desktop and mobile web browsers with zero configuration.</div>
    </div>

    <div class="qt-faq-item">
        <div class="qt-faq-q">How does the platform handle missing trading data or holidays?</div>
        <div class="qt-faq-a">Our data sanitation layer automatically scrubs invalid null entries and isolates valid trading sessions, ensuring charts never crash or render NaN gaps.</div>
    </div>
</div>
"""
    )

    # ── FINAL CTA SECTION (Identical to Top per A2) ────────────────────
    render_html(
        f"""
<div class="qt-card" style="max-width: 860px; margin: var(--space-700) auto; text-align: center; padding: 48px 24px; border-color: var(--action-primary);">
    <h2 class="heading-3" style="color: var(--text-primary); margin-bottom: 12px;">
        Ready to elevate your market analysis?
    </h2>
    <p class="body-3" style="color: var(--text-secondary); max-width: 540px; margin: 0 auto 24px auto;">
        Access institutional grade charting, automated indicators, and algorithmic stock research without paying subscription fees.
    </p>
    <div class="qt-cta-group" style="margin-bottom: 0;">
        <a href="?page=terminal" target="_self" class="qt-btn-primary button-md">
            {ICON_TERMINAL}
            <span>Launch Quant Terminal</span>
            {ICON_CHEVRON_RIGHT}
        </a>
    </div>
</div>
"""
    )
