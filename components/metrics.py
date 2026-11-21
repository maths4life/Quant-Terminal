import streamlit as st
from utils.helpers import render_html


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
    """UI/UX Pro Max high-density KPI grid for market snapshot & technical indicators."""
    
    # ── MARKET SNAPSHOT ───────────────────────────────────────────────
    render_html('<h2 class="qt-section-head">Market Snapshot</h2>')

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Last Price", f"₹{close:,.2f}", f"{change:+.2f}%")
    c2.metric("Day High", f"₹{stats['day_high']:,.2f}")
    c3.metric("Day Low", f"₹{stats['day_low']:,.2f}")
    c4.metric(
        "Trading Volume",
        fmt_indian(stats["volume"]) if "Volume" in df.columns else "—",
    )
    c5.metric(
        "52-Week High",
        f"₹{w52_h:,.2f}",
        f"{abs(pct_from_high):.1f}% below high",
    )
    c6.metric(
        "52-Week Low",
        f"₹{w52_l:,.2f}",
        f"{pct_from_low:.1f}% above low",
    )

    # ── TECHNICAL INDICATORS ──────────────────────────────────────────
    render_html('<h2 class="qt-section-head">Technical Indicators</h2>')

    m1, m2, m3, m4 = st.columns(4)

    if last_ma20:
        above20 = close > last_ma20
        delta_ma20 = ((close - last_ma20) / last_ma20) * 100
        m1.metric(
            "20-Day Moving Average",
            f"₹{last_ma20:,.2f}",
            f"{delta_ma20:+.2f}% vs Price",
        )
    else:
        m1.metric("20-Day Moving Average", "—")

    if last_ma50:
        above50 = close > last_ma50
        delta_ma50 = ((close - last_ma50) / last_ma50) * 100
        m2.metric(
            "50-Day Moving Average",
            f"₹{last_ma50:,.2f}",
            f"{delta_ma50:+.2f}% vs Price",
        )
    else:
        m2.metric("50-Day Moving Average", "—")

    if last_rsi:
        if last_rsi >= 70:
            rsi_tone = "Overbought (>=70)"
        elif last_rsi <= 30:
            rsi_tone = "Oversold (<=30)"
        else:
            rsi_tone = "Neutral Range (30-70)"
        m3.metric("RSI (14 Period)", f"{last_rsi:.1f}", rsi_tone)
    else:
        m3.metric("RSI (14 Period)", "—")

    if avg_vol20 and "Volume" in df.columns:
        last_vol = float(df["Volume"].dropna().iloc[-1])
        vol_ratio = (last_vol / avg_vol20) * 100 if avg_vol20 else 0
        m4.metric(
            "20-Day Avg Volume",
            fmt_indian(avg_vol20),
            f"{vol_ratio:.0f}% of 20D Avg",
        )
    else:
        m4.metric("20-Day Avg Volume", "—")
