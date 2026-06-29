import streamlit as st


def render_metrics(
    df,
    stats,
    close,
    change,
    w52_h,
    w52_l,
    pct_from_high,
    pct_from_low,
    last_ma20,
    last_ma50,
    last_rsi,
    avg_vol20,
    fmt_indian,
):
    # ── MARKET SNAPSHOT ───────────────────────────────────────────────
    st.markdown(
        '<div class="qt-section-title">Market Snapshot</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Last Price", f"₹{close:,.2f}", f"{change:+.2f}%")
    c2.metric("Day High", f"₹{stats['day_high']:,.2f}")
    c3.metric("Day Low", f"₹{stats['day_low']:,.2f}")
    c4.metric(
        "Volume",
        fmt_indian(stats["volume"]) if "Volume" in df.columns else "—",
    )
    c5.metric(
        "52W High",
        f"₹{w52_h:,.2f}",
        f"{abs(pct_from_high):.1f}% below ATH",
    )
    c6.metric(
        "52W Low",
        f"₹{w52_l:,.2f}",
        f"{pct_from_low:.1f}% above",
    )

    # ── TECHNICAL INDICATORS ──────────────────────────────────────────
    st.markdown(
        '<div class="qt-section-title">Technical Indicators</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    if last_ma20:
        above20 = close > last_ma20
        m1.metric(
            "MA 20",
            f"₹{last_ma20:,.2f}",
            "▲ Above" if above20 else "▼ Below",
        )
    else:
        m1.metric("MA 20", "—")

    if last_ma50:
        above50 = close > last_ma50
        m2.metric(
            "MA 50",
            f"₹{last_ma50:,.2f}",
            "▲ Above" if above50 else "▼ Below",
        )
    else:
        m2.metric("MA 50", "—")

    m3.metric(
        "RSI 14",
        f"{last_rsi:.1f}" if last_rsi else "—",
    )

    m4.metric(
        "Avg Vol 20d",
        fmt_indian(avg_vol20),
    )