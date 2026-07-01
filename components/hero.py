import streamlit as st
from datetime import datetime
import pytz

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
    change_class = "up" if change >= 0 else "down"
    arrow = "▲" if change >= 0 else "▼"
    ist_now = datetime.now(IST)

    st.markdown(
        f"""
    <div class="qt-hero">
    <div class="qt-hero-grid">
        <div class="qt-hero-left">
        <div class="qt-hero-tags">
            <span class="qt-tag">{interval_label} · {period}</span>
            <span class="qt-tag">RSI {rsi_txt}</span>
            <span class="qt-tag">Updated {date_str}</span>
        </div>
        <div class="qt-ticker">{ticker}<span class="sep">/</span><span style="color:var(--text-secondary);font-size:1.05rem;">EQUITY</span></div>
        {f'<div class="qt-company-name">{company_name}</div>' if company_name else ''}
        {profile_html}
        <div class="qt-meta">Live institutional view · Yahoo Finance feed · IST {ist_now.strftime('%H:%M')}</div>
        </div>
        <div class="qt-hero-right">
        <div class="qt-price">₹{close:,.2f}</div>
        <div class="qt-change {change_class}">{arrow} {abs(change):.2f}%  ·  {'+' if change_abs >= 0 else ''}{change_abs:,.2f}</div>
        </div>
    </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
