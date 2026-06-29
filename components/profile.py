import streamlit as st


def render_profile_strip(info):
    """Sector / industry / exchange chips shown under the ticker in the hero."""
    chips = []
    if info.get("sector"):
        chips.append(f'<span class="qt-profile-chip">{info["sector"]}</span>')
    if info.get("industry"):
        chips.append(f'<span class="qt-profile-chip">{info["industry"]}</span>')
    if info.get("exchange"):
        chips.append(f'<span class="qt-profile-chip">{info["exchange"]}</span>')

    if not chips:
        return ""

    return f'<div class="qt-profile-row">{"".join(chips)}</div>'


def render_key_stats(info, close, w52_h, w52_l, fmt_mcap, fmt_ratio, fmt_pct_val):
    """Fundamentals row — Market Cap / P/E / P/B / EPS / Beta / Div Yield —
    plus a 52-week range bar showing where price sits today."""

    has_fundamentals = any(
        info.get(k) is not None
        for k in ("market_cap", "pe", "pb", "eps", "beta", "dividend_yield")
    )

    if has_fundamentals:
        st.markdown(
            '<div class="qt-section-title">Key Statistics</div>',
            unsafe_allow_html=True,
        )
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Market Cap", fmt_mcap(info.get("market_cap")))
        k2.metric("P/E (TTM)", fmt_ratio(info.get("pe")))
        k3.metric("P/B", fmt_ratio(info.get("pb")))
        k4.metric("EPS", fmt_ratio(info.get("eps")))
        k5.metric("Beta", fmt_ratio(info.get("beta")))
        k6.metric("Dividend Yield", fmt_pct_val(info.get("dividend_yield")))

    # ── 52-WEEK RANGE BAR ──────────────────────────────────────────────
    lo = w52_l if w52_l is not None else info.get("fifty_two_low")
    hi = w52_h if w52_h is not None else info.get("fifty_two_high")

    if lo is not None and hi is not None and hi > lo:
        pct = max(0.0, min(1.0, (close - lo) / (hi - lo))) * 100
        st.markdown(
            f"""
<div class="qt-range-wrap">
    <div class="qt-range-label">
        <span>52W Low · ₹{lo:,.2f}</span>
        <span>52W High · ₹{hi:,.2f}</span>
    </div>
    <div class="qt-range-track">
        <div class="qt-range-fill" style="width:{pct:.2f}%;"></div>
        <div class="qt-range-marker" style="left:{pct:.2f}%;" title="Current price"></div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
