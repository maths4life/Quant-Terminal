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
    # ── MARKET SNAPSHOT ───────────────────────────────────────────────
    render_html('<h2 class="hm-section-head">Market snapshot</h2>')

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Last price", f"₹{close:,.2f}", f"{change:+.2f}%")
    c2.metric("Day high", f"₹{stats['day_high']:,.2f}")
    c3.metric("Day low", f"₹{stats['day_low']:,.2f}")
    c4.metric(
        "Volume",
        fmt_indian(stats["volume"]) if "Volume" in df.columns else "—",
    )
    c5.metric(
        "52-week high",
        f"₹{w52_h:,.2f}",
        f"{abs(pct_from_high):.1f}% below high",
    )
    c6.metric(
        "52-week low",
        f"₹{w52_l:,.2f}",
        f"{pct_from_low:.1f}% above low",
    )

    # ── TECHNICAL INDICATORS ──────────────────────────────────────────
    render_html('<h2 class="hm-section-head">Technical indicators</h2>')

    m1, m2, m3, m4 = st.columns(4)

    if last_ma20:
        above20 = close > last_ma20
        m1.metric(
            "20-day moving average",
            f"₹{last_ma20:,.2f}",
            "Price above average" if above20 else "Price below average",
        )
    else:
        m1.metric("20-day moving average", "—")

    if last_ma50:
        above50 = close > last_ma50
        m2.metric(
            "50-day moving average",
            f"₹{last_ma50:,.2f}",
            "Price above average" if above50 else "Price below average",
        )
    else:
        m2.metric("50-day moving average", "—")

    if last_rsi:
        if last_rsi >= 70:
            rsi_tone = "Overbought"
        elif last_rsi <= 30:
            rsi_tone = "Oversold"
        else:
            rsi_tone = "Neutral band"
        m3.metric("Relative strength index", f"{last_rsi:.1f}", rsi_tone)
    else:
        m3.metric("Relative strength index", "—")

    if avg_vol20 and "Volume" in df.columns:
        last_vol = float(df["Volume"].dropna().iloc[-1])
        vol_ratio = (last_vol / avg_vol20) * 100 if avg_vol20 else 0
        m4.metric(
            "20-day average volume",
            fmt_indian(avg_vol20),
            f"{vol_ratio:.0f}% of average",
        )
    else:
        m4.metric("20-day average volume", "—")
