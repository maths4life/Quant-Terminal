import streamlit as st
from utils.helpers import render_html


def render_profile_strip(info):
    """Sector, industry, and exchange indicators."""
    chips = []
    if info.get("sector"):
        chips.append(f'<span class="hm-profile-chip">{info["sector"]}</span>')
    if info.get("industry"):
        chips.append(f'<span class="hm-profile-chip">{info["industry"]}</span>')
    if info.get("exchange"):
        chips.append(f'<span class="hm-profile-chip">{info["exchange"]}</span>')

    if not chips:
        return ""

    return f'<div class="hm-profile-row">{"".join(chips)}</div>'


def render_key_stats(info, close, w52_h, w52_l, fmt_mcap, fmt_ratio, fmt_pct_val):
    """Valuation fundamentals row plus 52-week position range."""

    has_fundamentals = any(
        info.get(k) is not None
        for k in ("market_cap", "pe", "pb", "eps", "beta", "dividend_yield")
    )

    if has_fundamentals:
        render_html('<h2 class="hm-section-head">Valuation metrics</h2>')
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Market cap", fmt_mcap(info.get("market_cap")))
        k2.metric("P/E ratio", fmt_ratio(info.get("pe")))
        k3.metric("Price to book", fmt_ratio(info.get("pb")))
        k4.metric("Earnings per share", fmt_ratio(info.get("eps")))
        k5.metric("Beta coefficient", fmt_ratio(info.get("beta")))
        k6.metric("Dividend yield", fmt_pct_val(info.get("dividend_yield")))

    # ── 52-WEEK RANGE BAR ──────────────────────────────────────────────
    lo = w52_l if w52_l is not None else info.get("fifty_two_low")
    hi = w52_h if w52_h is not None else info.get("fifty_two_high")

    if lo is not None and hi is not None and hi > lo:
        pct = max(0.0, min(1.0, (close - lo) / (hi - lo))) * 100
        render_html(
            f"""
<div class="hm-range-card">
    <div class="hm-range-header">
        <span class="hm-range-edge">52-week low ₹{lo:,.2f}</span>
        <span class="hm-range-current">Position within annual range ({pct:.0f}%)</span>
        <span class="hm-range-edge">52-week high ₹{hi:,.2f}</span>
    </div>
    <div class="hm-range-track">
        <div class="hm-range-fill" style="width:{pct:.2f}%;"></div>
        <div class="hm-range-thumb" style="left:{pct:.2f}%;"></div>
    </div>
</div>
"""
        )
