"""
AI Insights — Stock Research Dashboard
---------------------------------------
Deterministic, rule-based research report built entirely from yfinance data
and the technical indicators computed in this module. No LLM / external AI
API is used anywhere on this page — every label, badge, and observation
below is produced by explicit if/else logic over real numbers.

Drop this file in as `components/insights.py` (replaces the Step-1 shell).
Only entry point used elsewhere: render_insights_page(ticker).
"""

import re

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

from components.search import render_search


def _md(html: str):
    """Render trusted HTML via st.markdown.

    The HTML fragments below are written as indented, multi-line
    f-strings purely for source readability. Standard Markdown treats
    any line indented 4+ spaces as a preformatted code block, so
    rendering them as-is causes chunks of markup to show up as literal
    text instead of being parsed as HTML. Collapsing every newline +
    run of following whitespace onto a single line sidesteps that
    entirely without changing the rendered layout (which is controlled
    by the CSS, not by whitespace in the source).
    """
    st.markdown(re.sub(r"\n\s*", "", html), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# STYLE — additive only. Reuses the existing design tokens defined in
# assets/theme.py's global stylesheet (--bg-card, --border, --accent,
# --bullish, --bearish, --radius, --shadow-sm, font families, etc).
# Nothing here redefines or overrides those tokens.
# ════════════════════════════════════════════════════════════════════
_INSIGHTS_CSS = """
<style>
.qt-ins-card{
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:16px; padding:1.3rem 1.5rem; margin-bottom:1rem;
    box-shadow:var(--shadow-sm);
}
.qt-ins-card.tight{ padding:1.1rem 1.3rem; }

/* At-a-glance grid */
.qt-glance-grid{
    display:grid; grid-template-columns:repeat(5,1fr); gap:.85rem;
    margin-bottom:1.1rem;
}
.qt-glance-tile{
    background:var(--bg-elev); border:1px solid var(--border);
    border-radius:12px; padding:.9rem 1rem; text-align:center;
}
.qt-glance-label{
    font-family:'Geist',sans-serif; font-size:.64rem; font-weight:700;
    letter-spacing:.07em; text-transform:uppercase; color:var(--text-tertiary);
    margin-bottom:.5rem;
}
.qt-glance-value{
    font-family:'Geist Mono',monospace; font-size:1.05rem; font-weight:700;
    color:var(--text-primary);
}
.qt-glance-value.stars{ letter-spacing:.1em; color:#D97706; font-size:1.15rem; }
.qt-glance-value.bullish{ color:var(--bullish); }
.qt-glance-value.bearish{ color:var(--bearish); }
.qt-glance-value.neutral{ color:var(--text-secondary); }
.qt-glance-value.warn{ color:#D97706; }

.qt-strength-risk{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
@media (max-width:900px){
    .qt-glance-grid{ grid-template-columns:repeat(2,1fr); }
    .qt-strength-risk{ grid-template-columns:1fr; }
}
.qt-sr-block{
    background:var(--bg-elev); border:1px solid var(--border);
    border-radius:12px; padding:.9rem 1.05rem;
}
.qt-sr-head{
    font-family:'Geist',sans-serif; font-size:.68rem; font-weight:700;
    letter-spacing:.06em; text-transform:uppercase; margin-bottom:.55rem;
}
.qt-sr-block.strength .qt-sr-head{ color:var(--bullish); }
.qt-sr-block.risk .qt-sr-head{ color:#D97706; }
.qt-sr-list{ list-style:none; margin:0; padding:0; }
.qt-sr-list li{
    font-family:'Geist',sans-serif; font-size:.8rem; color:var(--text-primary);
    padding:.3rem 0; display:flex; gap:.5rem; align-items:flex-start;
    border-bottom:1px dashed var(--border);
}
.qt-sr-list li:last-child{ border-bottom:none; }

/* Section headers use the existing qt-section-title look already in
   the base stylesheet — no redefinition needed. */

/* Tables */
.qt-ins-table{ width:100%; border-collapse:collapse; margin-top:.4rem; }
.qt-ins-table th{
    font-family:'Geist',sans-serif; font-size:.66rem; font-weight:700;
    letter-spacing:.05em; text-transform:uppercase; color:var(--text-tertiary);
    text-align:right; padding:.55rem .7rem; border-bottom:1px solid var(--border-strong);
    background:var(--bg-elev);
}
.qt-ins-table th:first-child{ text-align:left; }
.qt-ins-table td{
    font-family:'Geist Mono',monospace; font-size:.8rem; color:var(--text-primary);
    text-align:right; padding:.55rem .7rem; border-bottom:1px solid var(--border);
}
.qt-ins-table td:first-child{
    text-align:left; font-family:'Geist',sans-serif; font-weight:600; font-size:.8rem;
    color:var(--text-secondary);
}
.qt-ins-table tr:last-child td{ border-bottom:none; }
.qt-ins-table td.up{ color:var(--bullish); }
.qt-ins-table td.down{ color:var(--bearish); }

/* Badges */
.qt-badge{
    display:inline-flex; align-items:center; gap:.3rem;
    font-family:'Geist',sans-serif; font-size:.68rem; font-weight:700;
    padding:.22rem .6rem; border-radius:999px; white-space:nowrap;
}
.qt-badge.bullish{ color:var(--bullish); background:var(--bullish-dim); }
.qt-badge.bearish{ color:var(--bearish); background:var(--bearish-dim); }
.qt-badge.neutral{ color:var(--text-secondary); background:var(--bg-elev); border:1px solid var(--border); }
.qt-badge.warn{ color:#D97706; background:rgba(217,119,6,0.10); }

/* Observation list */
.qt-obs-list{ list-style:none; margin:0; padding:0; }
.qt-obs-list li{
    font-family:'Geist',sans-serif; font-size:.85rem; color:var(--text-primary);
    padding:.55rem 0; border-bottom:1px solid var(--border);
    display:flex; gap:.6rem; align-items:flex-start; line-height:1.45;
}
.qt-obs-list li:last-child{ border-bottom:none; }
.qt-obs-icon{ flex-shrink:0; font-size:.95rem; margin-top:.05rem; }

/* Valuation metric rows */
.qt-val-row{
    display:grid; grid-template-columns:140px 100px 1fr; gap:1rem;
    align-items:start; padding:.7rem 0; border-bottom:1px solid var(--border);
}
.qt-val-row:last-child{ border-bottom:none; }
.qt-val-label{ font-family:'Geist',sans-serif; font-weight:700; font-size:.78rem; color:var(--text-primary); }
.qt-val-num{ font-family:'Geist Mono',monospace; font-weight:700; font-size:.88rem; color:var(--text-primary); }
.qt-val-note{ font-family:'Geist',sans-serif; font-size:.78rem; color:var(--text-secondary); line-height:1.45; }

/* Checklist */
.qt-checklist{ display:grid; grid-template-columns:1fr 1fr; gap:.6rem .1rem; }
@media (max-width:900px){ .qt-checklist{ grid-template-columns:1fr; } }
.qt-check-row{
    display:flex; align-items:center; justify-content:space-between;
    background:var(--bg-elev); border:1px solid var(--border);
    border-radius:9px; padding:.55rem .85rem;
}
.qt-check-label{ font-family:'Geist',sans-serif; font-size:.8rem; font-weight:600; color:var(--text-primary); }

/* Snapshot strip */
.qt-snapshot-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:.85rem; }
@media (max-width:900px){ .qt-snapshot-grid{ grid-template-columns:repeat(2,1fr); } }
.qt-snapshot-tile{
    background:var(--bg-elev); border:1px solid var(--border);
    border-radius:12px; padding:1rem; text-align:center;
}
.qt-snapshot-kicker{
    font-family:'Geist',sans-serif; font-size:.64rem; font-weight:700;
    letter-spacing:.07em; text-transform:uppercase; color:var(--text-tertiary);
    margin-bottom:.5rem;
}
.qt-snapshot-value{ font-family:'Geist Mono',monospace; font-weight:700; font-size:1.1rem; }

.qt-ins-caption{
    font-family:'Geist Mono',monospace; font-size:.68rem; color:var(--text-tertiary);
    margin-top:.6rem;
}
</style>
"""


def _inject_css():
    st.markdown(_INSIGHTS_CSS, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# DATA FETCHING (yfinance only — no external AI API)
# ════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def _fetch_bundle(ticker: str):
    t = yf.Ticker(ticker)
    info = {}
    try:
        info = t.info or {}
    except Exception:
        info = {}

    hist = pd.DataFrame()
    try:
        hist = t.history(period="2y", interval="1d", auto_adjust=False)
    except Exception:
        hist = pd.DataFrame()

    def _safe(getter):
        try:
            df = getter()
            return df if df is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    q_fin = _safe(lambda: t.quarterly_financials)
    q_bs = _safe(lambda: t.quarterly_balance_sheet)
    a_fin = _safe(lambda: t.financials)
    a_bs = _safe(lambda: t.balance_sheet)
    a_cf = _safe(lambda: t.cashflow)

    return {
        "info": info, "hist": hist,
        "q_fin": q_fin, "q_bs": q_bs,
        "a_fin": a_fin, "a_bs": a_bs, "a_cf": a_cf,
    }


def _row(df: pd.DataFrame, candidates):
    """Return the first matching row (as a Series) from a yfinance
    financial statement, trying several possible label spellings."""
    if df is None or df.empty:
        return None
    for name in candidates:
        if name in df.index:
            return df.loc[name]
    # case-insensitive fallback
    lower_map = {str(i).lower(): i for i in df.index}
    for name in candidates:
        key = name.lower()
        if key in lower_map:
            return df.loc[lower_map[key]]
    return None


def _val_at(series, pos):
    if series is None or len(series) <= pos:
        return None
    v = series.iloc[pos]
    if pd.isna(v):
        return None
    return float(v)


# ════════════════════════════════════════════════════════════════════
# TECHNICAL INDICATORS (computed locally — deterministic math only)
# ════════════════════════════════════════════════════════════════════
def _compute_technicals(hist: pd.DataFrame) -> pd.DataFrame:
    df = hist.copy()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    df["VOL_AVG20"] = df["Volume"].rolling(20).mean()
    df["DAILY_RET"] = df["Close"].pct_change()
    return df


def _support_resistance(df: pd.DataFrame, lookback=60):
    window = df.tail(lookback)
    resistance = float(window["High"].max())
    support = float(window["Low"].min())
    return support, resistance


def _detect_candlestick(df: pd.DataFrame):
    """Simple deterministic candlestick pattern detection on the last
    1-3 completed candles. Returns (pattern_name, direction) or
    (None, None) if nothing reliable is found."""
    d = df.tail(3)
    if len(d) < 1:
        return None, None

    def body(row):
        return abs(row["Close"] - row["Open"])

    def rng(row):
        return max(row["High"] - row["Low"], 1e-9)

    def is_green(row):
        return row["Close"] > row["Open"]

    c0 = d.iloc[-1]  # most recent
    if len(d) >= 3:
        c1, c2 = d.iloc[-2], d.iloc[-3]

        # Morning Star: down candle, small-body star, up candle closing
        # above the midpoint of the first candle
        if (not is_green(c2) and body(c2) / rng(c2) > 0.5
                and body(c1) / rng(c1) < 0.35
                and is_green(c0) and c0["Close"] > (c2["Open"] + c2["Close"]) / 2):
            return "Morning Star", "bullish"

        # Evening Star: mirror of the above
        if (is_green(c2) and body(c2) / rng(c2) > 0.5
                and body(c1) / rng(c1) < 0.35
                and not is_green(c0) and c0["Close"] < (c2["Open"] + c2["Close"]) / 2):
            return "Evening Star", "bearish"

        # Three White Soldiers
        if (is_green(c2) and is_green(c1) and is_green(c0)
                and c1["Close"] > c2["Close"] and c0["Close"] > c1["Close"]
                and c1["Open"] > c2["Open"] and c0["Open"] > c1["Open"]):
            return "Three White Soldiers", "bullish"

        # Three Black Crows
        if (not is_green(c2) and not is_green(c1) and not is_green(c0)
                and c1["Close"] < c2["Close"] and c0["Close"] < c1["Close"]
                and c1["Open"] < c2["Open"] and c0["Open"] < c1["Open"]):
            return "Three Black Crows", "bearish"

    if len(d) >= 2:
        c1, c0 = d.iloc[-2], d.iloc[-1]

        # Bullish Engulfing
        if (not is_green(c1) and is_green(c0)
                and c0["Open"] <= c1["Close"] and c0["Close"] >= c1["Open"]):
            return "Bullish Engulfing", "bullish"

        # Bearish Engulfing
        if (is_green(c1) and not is_green(c0)
                and c0["Open"] >= c1["Close"] and c0["Close"] <= c1["Open"]):
            return "Bearish Engulfing", "bearish"

        # Harami (current body inside previous body, opposite colours)
        if (is_green(c1) != is_green(c0)
                and body(c0) < body(c1)
                and max(c0["Open"], c0["Close"]) <= max(c1["Open"], c1["Close"])
                and min(c0["Open"], c0["Close"]) >= min(c1["Open"], c1["Close"])):
            direction = "bullish" if is_green(c0) else "bearish"
            return "Harami", direction

    # Single-candle patterns on the most recent candle
    upper_wick = c0["High"] - max(c0["Open"], c0["Close"])
    lower_wick = min(c0["Open"], c0["Close"]) - c0["Low"]
    b = body(c0)
    r = rng(c0)

    if b / r < 0.1:
        return "Doji", "neutral"
    if lower_wick > 2 * b and upper_wick < 0.3 * b + 1e-9:
        return "Hammer", "bullish"
    if upper_wick > 2 * b and lower_wick < 0.3 * b + 1e-9:
        return "Shooting Star", "bearish"

    return None, None


# ════════════════════════════════════════════════════════════════════
# FORMATTING HELPERS
# ════════════════════════════════════════════════════════════════════
def _fmt_amount(v, currency="₹"):
    if v is None:
        return "—"
    av = abs(v)
    if av >= 1e7:
        return f"{currency}{v / 1e7:,.1f} Cr"
    if av >= 1e5:
        return f"{currency}{v / 1e5:,.1f} L"
    return f"{currency}{v:,.0f}"


def _fmt_num(v, suffix="", decimals=2):
    if v is None:
        return "—"
    return f"{v:,.{decimals}f}{suffix}"


def _fmt_pct(v, decimals=1):
    if v is None:
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.{decimals}f}%"


def _pct_change(cur, prev):
    if cur is None or prev is None or prev == 0:
        return None
    return (cur - prev) / abs(prev) * 100


def _diff(cur, prev):
    if cur is None or prev is None:
        return None
    return cur - prev


def _delta_class(v):
    if v is None:
        return ""
    return "up" if v >= 0 else "down"


def _table_row(label, cur, prev, fmt=_fmt_amount, pct_decimals=1):
    d = _diff(cur, prev)
    p = _pct_change(cur, prev)
    return (
        f'<tr><td>{label}</td>'
        f'<td>{fmt(cur)}</td>'
        f'<td>{fmt(prev)}</td>'
        f'<td class="{_delta_class(d)}">{fmt(d) if d is not None else "—"}</td>'
        f'<td class="{_delta_class(p)}">{_fmt_pct(p, pct_decimals) if p is not None else "—"}</td>'
        f'</tr>'
    )


# ════════════════════════════════════════════════════════════════════
# RULE-BASED INTERPRETATION LAYER (deterministic, no AI)
# ════════════════════════════════════════════════════════════════════
def _trend_label(price, ema20, ema50, ema200):
    have = [x for x in (ema20, ema50, ema200) if x is not None]
    if price is None or not have:
        return "Neutral"
    above = sum(1 for x in have if price > x)
    if above == len(have) and len(have) >= 2:
        return "Bullish"
    if above == 0 and len(have) >= 2:
        return "Bearish"
    return "Neutral"


def _momentum_label(rsi, macd_hist, vol_ratio):
    score = 0
    if rsi is not None:
        if rsi >= 55:
            score += 1
        elif rsi <= 45:
            score -= 1
    if macd_hist is not None:
        score += 1 if macd_hist > 0 else -1
    if vol_ratio is not None:
        if vol_ratio >= 1.15:
            score += 1
        elif vol_ratio <= 0.85:
            score -= 1
    if score >= 2:
        return "Strong"
    if score <= -2:
        return "Weak"
    return "Moderate"


def _valuation_label(pe, pb, peg):
    """Rough, transparent heuristic thresholds — not a sector-adjusted
    model, since no external benchmark data is used on this page."""
    signals = []
    if pe is not None:
        signals.append(1 if pe > 30 else (-1 if pe < 15 else 0))
    if pb is not None:
        signals.append(1 if pb > 6 else (-1 if pb < 2 else 0))
    if peg is not None:
        signals.append(1 if peg > 2 else (-1 if peg < 1 else 0))
    if not signals:
        return "Fair"
    avg = sum(signals) / len(signals)
    if avg > 0.3:
        return "Premium"
    if avg < -0.3:
        return "Discounted"
    return "Fair"


def _risk_label(beta, volatility_ann, debt_to_equity):
    score = 0
    if beta is not None:
        score += 1 if beta > 1.3 else (-1 if beta < 0.8 else 0)
    if volatility_ann is not None:
        score += 1 if volatility_ann > 35 else (-1 if volatility_ann < 20 else 0)
    if debt_to_equity is not None:
        score += 1 if debt_to_equity > 100 else (-1 if debt_to_equity < 40 else 0)
    if score >= 2:
        return "High"
    if score <= -1:
        return "Low"
    return "Medium"


def _business_quality(rev_growth, profit_growth, op_margin, debt_trend_down, positive_cash):
    stars = 2  # baseline
    if rev_growth is not None and rev_growth > 0:
        stars += 1
    if profit_growth is not None and profit_growth > 0:
        stars += 1
    if op_margin is not None and op_margin > 15:
        stars += 0.5
    if debt_trend_down:
        stars += 0.5
    if positive_cash:
        stars += 0.0  # already reflected via cash checklist, avoid double count
    stars = max(1, min(5, round(stars)))
    label = {1: "Weak", 2: "Weak", 3: "Moderate", 4: "Strong", 5: "Strong"}[stars]
    return stars, label


def _stars_html(n):
    return "★" * n + "☆" * (5 - n)


def _badge(text, kind):
    return f'<span class="qt-badge {kind}">{text}</span>'


# ════════════════════════════════════════════════════════════════════
# SECTION RENDERERS
# ════════════════════════════════════════════════════════════════════
def _section_title(text):
    st.markdown(f'<div class="qt-section-title">{text}</div>', unsafe_allow_html=True)


def _render_top_summary(ctx):
    stars_html = _stars_html(ctx["quality_stars"])
    trend_cls = {"Bullish": "bullish", "Bearish": "bearish", "Neutral": "neutral"}[ctx["trend"]]
    val_cls = {"Discounted": "bullish", "Premium": "warn", "Fair": "neutral"}[ctx["valuation"]]
    risk_cls = {"Low": "bullish", "High": "bearish", "Medium": "warn"}[ctx["risk"]]
    mom_cls = {"Strong": "bullish", "Weak": "bearish", "Moderate": "neutral"}[ctx["momentum"]]

    tiles = f"""
    <div class="qt-glance-grid">
        <div class="qt-glance-tile">
            <div class="qt-glance-label">Business Quality</div>
            <div class="qt-glance-value stars">{stars_html}</div>
        </div>
        <div class="qt-glance-tile">
            <div class="qt-glance-label">Technical Trend</div>
            <div class="qt-glance-value {trend_cls}">{ctx["trend"]}</div>
        </div>
        <div class="qt-glance-tile">
            <div class="qt-glance-label">Valuation</div>
            <div class="qt-glance-value {val_cls}">{ctx["valuation"]}</div>
        </div>
        <div class="qt-glance-tile">
            <div class="qt-glance-label">Risk</div>
            <div class="qt-glance-value {risk_cls}">{ctx["risk"]}</div>
        </div>
        <div class="qt-glance-tile">
            <div class="qt-glance-label">Momentum</div>
            <div class="qt-glance-value {mom_cls}">{ctx["momentum"]}</div>
        </div>
    </div>
    """

    strengths = "".join(f"<li>✓ {s}</li>" for s in ctx["strengths"]) or "<li>No standout strengths detected.</li>"
    risks = "".join(f"<li>⚠ {r}</li>" for r in ctx["risks"]) or "<li>No notable risk flags detected.</li>"

    sr = f"""
    <div class="qt-strength-risk">
        <div class="qt-sr-block strength">
            <div class="qt-sr-head">Top Strengths</div>
            <ul class="qt-sr-list">{strengths}</ul>
        </div>
        <div class="qt-sr-block risk">
            <div class="qt-sr-head">Things to Watch</div>
            <ul class="qt-sr-list">{risks}</ul>
        </div>
    </div>
    """

    _md(
        f'<div class="qt-ins-card">'
        f'<div class="qt-tag" style="display:inline-flex;margin-bottom:.9rem;">🧭 At a Glance</div>'
        f'{tiles}{sr}'
        f'<div class="qt-ins-caption">All labels below are generated by deterministic rules over yfinance data — no AI model or recommendation engine is involved.</div>'
        f'</div>'
    )


def _render_company_overview(info, close, change_abs, change_pct, w52_h, w52_l):
    name = info.get("longName") or info.get("shortName") or "—"
    sector = info.get("sector", "—")
    industry = info.get("industry", "—")
    mcap = info.get("marketCap")
    beta = info.get("beta")
    summary = info.get("longBusinessSummary", "No business summary available.")

    _section_title("Company Overview")
    change_cls = "up" if change_pct is not None and change_pct >= 0 else "down"
    _md(
        f"""
        <div class="qt-ins-card tight">
            <div class="qt-hero-grid">
                <div class="qt-hero-left">
                    <div class="qt-ticker" style="font-size:1.3rem;">{name}</div>
                    <div class="qt-profile-row">
                        <span class="qt-profile-chip">Sector · {sector}</span>
                        <span class="qt-profile-chip">Industry · {industry}</span>
                        <span class="qt-profile-chip">Beta · {_fmt_num(beta)}</span>
                        <span class="qt-profile-chip">Mkt Cap · {_fmt_amount(mcap)}</span>
                    </div>
                </div>
                <div class="qt-hero-right">
                    <div class="qt-price">{_fmt_num(close)}</div>
                    <div class="qt-change {change_cls}">
                        {_fmt_num(change_abs)} ({_fmt_pct(change_pct)})
                    </div>
                </div>
            </div>
        </div>
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("52 Week High", _fmt_num(w52_h))
    c2.metric("52 Week Low", _fmt_num(w52_l))
    c3.metric("Market Cap", _fmt_amount(mcap))
    c4.metric("Beta", _fmt_num(beta))

    with st.expander("Business Summary — Read More"):
        st.write(summary)


def _render_financial_health(q_fin, q_bs, info):
    _section_title("Financial Health — Quarterly")

    revenue = _row(q_fin, ["Total Revenue", "TotalRevenue"])
    net_income = _row(q_fin, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
    op_income = _row(q_fin, ["Operating Income", "OperatingIncome"])
    ebitda = _row(q_fin, ["EBITDA", "Ebitda"])
    diluted_eps = _row(q_fin, ["Diluted EPS", "DilutedEPS"])

    cash = _row(q_bs, ["Cash And Cash Equivalents", "CashAndCashEquivalents",
                        "Cash Cash Equivalents And Short Term Investments"])
    total_debt = _row(q_bs, ["Total Debt", "TotalDebt"])
    equity = _row(q_bs, ["Stockholders Equity", "StockholdersEquity", "Total Stockholder Equity"])

    cur_rev, prev_rev = _val_at(revenue, 0), _val_at(revenue, 1)
    cur_ni, prev_ni = _val_at(net_income, 0), _val_at(net_income, 1)
    cur_op, prev_op = _val_at(op_income, 0), _val_at(op_income, 1)
    cur_ebitda, prev_ebitda = _val_at(ebitda, 0), _val_at(ebitda, 1)
    cur_eps, prev_eps = _val_at(diluted_eps, 0), _val_at(diluted_eps, 1)
    cur_cash, prev_cash = _val_at(cash, 0), _val_at(cash, 1)
    cur_debt, prev_debt = _val_at(total_debt, 0), _val_at(total_debt, 1)
    cur_eq, prev_eq = _val_at(equity, 0), _val_at(equity, 1)

    cur_opm = (cur_op / cur_rev * 100) if cur_op is not None and cur_rev else None
    prev_opm = (prev_op / prev_rev * 100) if prev_op is not None and prev_rev else None

    cur_de = (cur_debt / cur_eq * 100) if cur_debt is not None and cur_eq else None
    prev_de = (prev_debt / prev_eq * 100) if prev_debt is not None and prev_eq else None

    rows = "".join([
        _table_row("Revenue", cur_rev, prev_rev),
        _table_row("Net Profit", cur_ni, prev_ni),
        _table_row("EPS", cur_eps, prev_eps, fmt=lambda v: _fmt_num(v, decimals=2)),
        _table_row("EBITDA", cur_ebitda, prev_ebitda),
        _table_row("Operating Margin", cur_opm, prev_opm, fmt=lambda v: _fmt_num(v, "%", 1)),
        _table_row("Cash", cur_cash, prev_cash),
        _table_row("Debt", cur_debt, prev_debt),
        _table_row("Debt to Equity", cur_de, prev_de, fmt=lambda v: _fmt_num(v, "%", 1)),
    ])

    _md(
        f"""
        <div class="qt-ins-card tight">
            <table class="qt-ins-table">
                <tr><th>Metric</th><th>Current Q</th><th>Previous Q</th><th>Change</th><th>% Change</th></tr>
                {rows}
            </table>
        </div>
        """
    )

    obs = []
    rev_g = _pct_change(cur_rev, prev_rev)
    ni_g = _pct_change(cur_ni, prev_ni)
    if rev_g is not None:
        obs.append(f"Revenue {'increased' if rev_g >= 0 else 'declined'} by {abs(rev_g):.1f}% QoQ.")
    if rev_g is not None and ni_g is not None:
        if ni_g > rev_g:
            obs.append("Profit grew faster than revenue, pointing to improving efficiency.")
        elif ni_g < rev_g:
            obs.append("Profit growth lagged revenue growth this quarter.")
    if cur_debt is not None and prev_debt is not None:
        obs.append(f"Debt {'reduced' if cur_debt < prev_debt else 'increased'} compared to the prior quarter.")
    if cur_opm is not None and prev_opm is not None:
        obs.append(f"Operating margin {'expanded' if cur_opm > prev_opm else 'contracted'} quarter-over-quarter.")
    if obs:
        st.markdown("".join(f"<div class='qt-meta' style='margin:.25rem 0;'>• {o}</div>" for o in obs),
                     unsafe_allow_html=True)
    else:
        st.info("Not enough quarterly statement data was returned by yfinance to generate observations.")

    return {
        "rev_growth": rev_g, "profit_growth": ni_g,
        "cur_opm": cur_opm, "debt_down": (cur_debt is not None and prev_debt is not None and cur_debt < prev_debt),
        "cur_debt": cur_debt, "cur_eq": equity is not None,
        "positive_cash": (cur_cash is not None and cur_cash > 0),
    }


def _render_annual_performance(a_fin, a_bs, a_cf, info):
    _section_title("Annual Performance")

    revenue = _row(a_fin, ["Total Revenue", "TotalRevenue"])
    net_income = _row(a_fin, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
    diluted_eps = _row(a_fin, ["Diluted EPS", "DilutedEPS"])
    op_income = _row(a_fin, ["Operating Income", "OperatingIncome"])
    equity = _row(a_bs, ["Stockholders Equity", "StockholdersEquity", "Total Stockholder Equity"])
    total_debt = _row(a_bs, ["Total Debt", "TotalDebt"])
    op_cf = _row(a_cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    dividends = _row(a_cf, ["Cash Dividends Paid", "Common Stock Dividend Paid"])

    cur_rev, prev_rev = _val_at(revenue, 0), _val_at(revenue, 1)
    cur_ni, prev_ni = _val_at(net_income, 0), _val_at(net_income, 1)
    cur_eps, prev_eps = _val_at(diluted_eps, 0), _val_at(diluted_eps, 1)
    cur_op, prev_op = _val_at(op_income, 0), _val_at(op_income, 1)
    cur_eq, prev_eq = _val_at(equity, 0), _val_at(equity, 1)
    cur_debt, prev_debt = _val_at(total_debt, 0), _val_at(total_debt, 1)
    cur_cf, prev_cf = _val_at(op_cf, 0), _val_at(op_cf, 1)
    cur_div, prev_div = _val_at(dividends, 0), _val_at(dividends, 1)

    cur_roe = (cur_ni / cur_eq * 100) if cur_ni is not None and cur_eq else None
    prev_roe = (prev_ni / prev_eq * 100) if prev_ni is not None and prev_eq else None
    cur_opm = (cur_op / cur_rev * 100) if cur_op is not None and cur_rev else None
    prev_opm = (prev_op / prev_rev * 100) if prev_op is not None and prev_rev else None

    rows = "".join([
        _table_row("Revenue", cur_rev, prev_rev),
        _table_row("Net Profit", cur_ni, prev_ni),
        _table_row("EPS", cur_eps, prev_eps, fmt=lambda v: _fmt_num(v, decimals=2)),
        _table_row("ROE", cur_roe, prev_roe, fmt=lambda v: _fmt_num(v, "%", 1)),
        _table_row("Operating Margin", cur_opm, prev_opm, fmt=lambda v: _fmt_num(v, "%", 1)),
        _table_row("Operating Cash Flow", cur_cf, prev_cf),
        _table_row("Debt", cur_debt, prev_debt),
        _table_row("Dividends Paid", cur_div, prev_div),
    ])

    _md(
        f"""
        <div class="qt-ins-card tight">
            <table class="qt-ins-table">
                <tr><th>Metric</th><th>Current FY</th><th>Previous FY</th><th>Difference</th><th>% Difference</th></tr>
                {rows}
            </table>
        </div>
        """
    )

    rev_g = _pct_change(cur_rev, prev_rev)
    ni_g = _pct_change(cur_ni, prev_ni)
    parts = []
    if rev_g is not None:
        parts.append(f"revenue {'grew' if rev_g >= 0 else 'fell'} {abs(rev_g):.1f}% YoY")
    if ni_g is not None:
        parts.append(f"net profit {'grew' if ni_g >= 0 else 'fell'} {abs(ni_g):.1f}% YoY")
    if cur_roe is not None and prev_roe is not None:
        parts.append(f"ROE moved from {prev_roe:.1f}% to {cur_roe:.1f}%")
    if parts:
        st.markdown(f"<div class='qt-meta'>Year-over-year, {'; '.join(parts)}.</div>", unsafe_allow_html=True)
    else:
        st.info("Not enough annual statement data was returned by yfinance to generate a summary.")

    return {"rev_growth": rev_g, "profit_growth": ni_g}


def _render_valuation(info):
    _section_title("Valuation")

    pe = info.get("trailingPE")
    fpe = info.get("forwardPE")
    pb = info.get("priceToBook")
    peg = info.get("pegRatio") or info.get("trailingPegRatio")
    div_yield = info.get("dividendYield")
    ev = info.get("enterpriseValue")
    ps = info.get("priceToSalesTrailing12Months")

    def note(metric, val):
        if val is None:
            return "Not reported by the data source for this stock."
        if metric == "pe":
            if val > 30:
                return f"PE of {val:.1f} indicates investors are paying a premium for expected future earnings. A high PE alone does not imply the stock is overvalued."
            if val < 15:
                return f"PE of {val:.1f} is on the lower side, suggesting the market is pricing in modest growth expectations."
            return f"PE of {val:.1f} sits in a fairly typical range relative to broad market norms."
        if metric == "fpe":
            return f"Forward PE of {val:.1f} reflects the price relative to analysts' next-year earnings estimate."
        if metric == "pb":
            if val > 6:
                return f"Price-to-Book of {val:.1f} is high, implying the market values the business well above its net asset base."
            if val < 2:
                return f"Price-to-Book of {val:.1f} is modest relative to the company's net assets."
            return f"Price-to-Book of {val:.1f} is within a moderate range."
        if metric == "peg":
            if val > 2:
                return f"PEG of {val:.1f} suggests the stock is priced richly relative to its earnings growth rate."
            if val < 1:
                return f"PEG of {val:.1f} suggests earnings growth may be undervalued relative to the price paid."
            return f"PEG of {val:.1f} suggests price and earnings growth are roughly in balance."
        if metric == "div":
            return f"Dividend yield of {val:.2f}% is the cash return paid to shareholders at the current price."
        if metric == "ev":
            return f"Enterprise Value of {_fmt_amount(val)} captures market cap plus net debt — the theoretical takeover cost."
        if metric == "ps":
            return f"Price-to-Sales of {val:.1f} shows how much investors are paying per unit of revenue."
        return ""

    div_pct = div_yield * 100 if div_yield is not None and div_yield < 1 else div_yield

    rows_data = [
        ("PE (Trailing)", _fmt_num(pe), note("pe", pe)),
        ("Forward PE", _fmt_num(fpe), note("fpe", fpe)),
        ("Price to Book", _fmt_num(pb), note("pb", pb)),
        ("PEG Ratio", _fmt_num(peg), note("peg", peg)),
        ("Dividend Yield", _fmt_num(div_pct, "%") if div_pct is not None else "—", note("div", div_pct)),
        ("Enterprise Value", _fmt_amount(ev), note("ev", ev)),
        ("Price to Sales", _fmt_num(ps), note("ps", ps)),
    ]
    rows_html = "".join(
        f'<div class="qt-val-row"><div class="qt-val-label">{label}</div>'
        f'<div class="qt-val-num">{value}</div><div class="qt-val-note">{n}</div></div>'
        for label, value, n in rows_data
    )

    valuation_label = _valuation_label(pe, pb, peg)
    _md(
        f'<div class="qt-ins-card tight">'
        f'<div style="margin-bottom:.8rem;">{_badge(valuation_label, {"Discounted":"bullish","Premium":"warn","Fair":"neutral"}[valuation_label])}</div>'
        f'{rows_html}</div>'
    )
    return valuation_label


def _render_technical(df, close):
    _section_title("Technical Analysis")

    ema20 = _val_at(df["EMA20"], -1) if len(df) else None
    ema50 = _val_at(df["EMA50"], -1) if len(df) else None
    ema200 = _val_at(df["EMA200"], -1) if len(df) else None
    rsi = _val_at(df["RSI"], -1) if len(df) else None
    macd = _val_at(df["MACD"], -1) if len(df) else None
    signal = _val_at(df["MACD_SIGNAL"], -1) if len(df) else None
    hist_v = _val_at(df["MACD_HIST"], -1) if len(df) else None
    vol = _val_at(df["Volume"], -1) if len(df) else None
    vol_avg = _val_at(df["VOL_AVG20"], -1) if len(df) else None
    vol_ratio = (vol / vol_avg) if vol and vol_avg else None

    support, resistance = _support_resistance(df) if len(df) else (None, None)
    pattern, direction = _detect_candlestick(df) if len(df) >= 1 else (None, None)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
        st.markdown("**Trend**")
        st.metric("Price", _fmt_num(close))
        st.metric("EMA20", _fmt_num(ema20))
        st.metric("EMA50", _fmt_num(ema50))
        st.metric("EMA200", _fmt_num(ema200))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
        st.markdown("**RSI (14)**")
        st.metric("Value", _fmt_num(rsi, decimals=1))
        if rsi is not None:
            if rsi >= 70:
                rsi_status, rsi_note = "Overbought", "Momentum is stretched to the upside; pullbacks become more likely."
            elif rsi <= 30:
                rsi_status, rsi_note = "Oversold", "Selling pressure looks extended; a bounce becomes more likely."
            else:
                rsi_status, rsi_note = "Neutral", "RSI is in a balanced range with no extreme reading."
        else:
            rsi_status, rsi_note = "—", "Not enough history to compute RSI."
        st.markdown(f"Status: **{rsi_status}**")
        st.caption(rsi_note)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
        st.markdown("**MACD**")
        st.metric("MACD", _fmt_num(macd, decimals=2))
        st.metric("Signal", _fmt_num(signal, decimals=2))
        st.metric("Histogram", _fmt_num(hist_v, decimals=2))
        cross = "Bullish crossover" if (macd is not None and signal is not None and macd > signal) else "Bearish crossover" if (macd is not None and signal is not None) else "—"
        st.markdown(f"{cross}")
        st.markdown('</div>', unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
        st.markdown("**Volume**")
        vc1, vc2, vc3 = st.columns(3)
        vc1.metric("Current", f"{vol:,.0f}" if vol else "—")
        vc2.metric("20D Avg", f"{vol_avg:,.0f}" if vol_avg else "—")
        vc3.metric("Vs Avg", _fmt_pct((vol_ratio - 1) * 100) if vol_ratio else "—")
        st.markdown('</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
        st.markdown("**Support & Resistance** (60-day range)")
        sc1, sc2 = st.columns(2)
        sc1.metric("Support", _fmt_num(support))
        sc2.metric("Resistance", _fmt_num(resistance))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="qt-ins-card tight">', unsafe_allow_html=True)
    st.markdown("**Candlestick Pattern**")
    if pattern:
        kind = {"bullish": "bullish", "bearish": "bearish", "neutral": "neutral"}[direction]
        st.markdown(_badge(pattern, kind), unsafe_allow_html=True)
    else:
        st.markdown(_badge("No reliable pattern detected", "neutral"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    trend = _trend_label(close, ema20, ema50, ema200)
    momentum = _momentum_label(rsi, hist_v, vol_ratio)

    near_resistance = resistance is not None and close is not None and (resistance - close) / resistance < 0.03
    near_support = support is not None and close is not None and (close - support) / max(support, 1e-9) < 0.03

    return {
        "trend": trend, "momentum": momentum,
        "ema20": ema20, "ema50": ema50, "ema200": ema200,
        "rsi": rsi, "macd_hist": hist_v, "vol_ratio": vol_ratio,
        "near_resistance": near_resistance, "near_support": near_support,
        "pattern": pattern, "pattern_dir": direction,
        "macd_bullish": (macd is not None and signal is not None and macd > signal),
    }


def _render_key_observations(obs_list):
    _section_title("Key Observations")
    if not obs_list:
        st.info("Not enough data was available to generate automated observations for this stock.")
        return
    items = "".join(
        f'<li><span class="qt-obs-icon">{"✓" if kind == "good" else "⚠"}</span><span>{text}</span></li>'
        for text, kind in obs_list
    )
    st.markdown(f'<div class="qt-ins-card tight"><ul class="qt-obs-list">{items}</ul></div>',
                unsafe_allow_html=True)


def _render_checklist(checklist):
    _section_title("Investment Checklist")
    rows = "".join(
        f'<div class="qt-check-row"><span class="qt-check-label">{label}</span>{_badge("✅" if ok else "⚠", "bullish" if ok else "warn")}</div>'
        for label, ok in checklist
    )
    st.markdown(f'<div class="qt-ins-card tight"><div class="qt-checklist">{rows}</div></div>',
                unsafe_allow_html=True)


def _render_snapshot(ctx):
    _section_title("Overall Snapshot")
    trend_cls = {"Bullish": "bullish", "Bearish": "bearish", "Neutral": "neutral"}[ctx["trend"]]
    val_cls = {"Discounted": "bullish", "Premium": "warn", "Fair": "neutral"}[ctx["valuation"]]
    risk_cls = {"Low": "bullish", "High": "bearish", "Medium": "warn"}[ctx["risk"]]
    quality_cls = {"Strong": "bullish", "Weak": "bearish", "Moderate": "neutral"}[ctx["quality_label"]]

    _md(
        f"""
        <div class="qt-ins-card tight">
            <div class="qt-snapshot-grid">
                <div class="qt-snapshot-tile">
                    <div class="qt-snapshot-kicker">Business Quality</div>
                    <div class="qt-snapshot-value {quality_cls}">{ctx["quality_label"]}</div>
                </div>
                <div class="qt-snapshot-tile">
                    <div class="qt-snapshot-kicker">Technical Trend</div>
                    <div class="qt-snapshot-value {trend_cls}">{ctx["trend"]}</div>
                </div>
                <div class="qt-snapshot-tile">
                    <div class="qt-snapshot-kicker">Valuation</div>
                    <div class="qt-snapshot-value {val_cls}">{ctx["valuation"]}</div>
                </div>
                <div class="qt-snapshot-tile">
                    <div class="qt-snapshot-kicker">Risk Level</div>
                    <div class="qt-snapshot-value {risk_cls}">{ctx["risk"]}</div>
                </div>
            </div>
            <div class="qt-ins-caption" style="margin-top:.9rem;">
                This report describes the current condition of the company and stock only.
                It is not a Buy/Sell recommendation and does not predict future returns.
            </div>
        </div>
        """
    )


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════
def render_insights_page(ticker: str):
    _inject_css()

    # Same search bar as the home page — it commits directly to
    # st.session_state.ticker and reruns on selection, so switching
    # stocks here updates this page immediately without a trip back
    # to the terminal.
    st.markdown('<div class="qt-search-mount">', unsafe_allow_html=True)
    render_search(current_ticker=st.session_state.ticker)
    st.markdown('</div>', unsafe_allow_html=True)
    ticker = st.session_state.ticker

    _md(
        f"""
        <div class="qt-hero" style="padding: 1.4rem 1.6rem; margin-bottom: 1rem;">
            <div class="qt-hero-grid">
                <div class="qt-hero-left">
                    <div class="qt-tag" style="display:inline-flex;">📊 AI Insights · Research Dashboard</div>
                    <div class="qt-ticker">{ticker}</div>
                    <div class="qt-meta">Deterministic, rule-based research — no LLM or external AI API is used on this page.</div>
                </div>
                <div class="qt-hero-right">
                    <a href="?page=home" target="_self" class="qt-nav-btn">
                        <span>←</span>Back to Terminal
                    </a>
                </div>
            </div>
        </div>
        """
    )

    with st.spinner(f"Building research report for {ticker}…"):
        bundle = _fetch_bundle(ticker)

    info = bundle["info"]
    hist = bundle["hist"]

    if hist is None or hist.empty:
        st.error(f"No price data found for '{ticker}'.")
        st.info("Try: RELIANCE.NS  ·  INFY.NS  ·  TCS.NS  ·  HDFCBANK.NS")
        return

    df = _compute_technicals(hist)
    valid = df.dropna(subset=["Close"])
    last = valid.iloc[-1]
    prev = valid.iloc[-2] if len(valid) >= 2 else last
    close = float(last["Close"])
    prev_close = float(prev["Close"])
    change_abs = close - prev_close
    change_pct = (change_abs / prev_close) * 100 if prev_close else None

    w52_h = float(valid["High"].tail(252).max())
    w52_l = float(valid["Low"].tail(252).min())

    # ---- Fundamentals ----
    _render_company_overview(info, close, change_abs, change_pct, w52_h, w52_l)
    fh_ctx = _render_financial_health(bundle["q_fin"], bundle["q_bs"], info)
    ap_ctx = _render_annual_performance(bundle["a_fin"], bundle["a_bs"], bundle["a_cf"], info)
    valuation_label = _render_valuation(info)

    # ---- Technicals ----
    tech_ctx = _render_technical(df, close)

    # ---- Risk & quality ----
    daily_returns = df["DAILY_RET"].dropna().tail(252)
    volatility_ann = float(daily_returns.std() * (252 ** 0.5) * 100) if len(daily_returns) > 20 else None
    beta = info.get("beta")

    q_debt = fh_ctx.get("cur_debt")
    eq_flag = fh_ctx.get("cur_eq")
    de_ratio = None  # already used inside table; derive rough one for risk model
    total_debt_row = _row(bundle["q_bs"], ["Total Debt", "TotalDebt"])
    equity_row = _row(bundle["q_bs"], ["Stockholders Equity", "StockholdersEquity", "Total Stockholder Equity"])
    cur_debt_v, cur_eq_v = _val_at(total_debt_row, 0), _val_at(equity_row, 0)
    if cur_debt_v is not None and cur_eq_v:
        de_ratio = cur_debt_v / cur_eq_v * 100

    risk = _risk_label(beta, volatility_ann, de_ratio)

    rev_growth = fh_ctx.get("rev_growth") if fh_ctx.get("rev_growth") is not None else ap_ctx.get("rev_growth")
    profit_growth = fh_ctx.get("profit_growth") if fh_ctx.get("profit_growth") is not None else ap_ctx.get("profit_growth")
    quality_stars, quality_label = _business_quality(
        rev_growth, profit_growth, fh_ctx.get("cur_opm"),
        fh_ctx.get("debt_down"), fh_ctx.get("positive_cash"),
    )

    # ---- Build strengths / risks for the top summary card ----
    strengths, risks = [], []
    if rev_growth is not None and rev_growth > 0:
        strengths.append("Revenue growing quarter-over-quarter")
    if profit_growth is not None and profit_growth > 0:
        strengths.append("Profit growth outpacing prior period")
    if tech_ctx["trend"] == "Bullish":
        strengths.append("Trading above major moving averages")
    if fh_ctx.get("positive_cash"):
        strengths.append("Positive cash position on the balance sheet")
    if fh_ctx.get("debt_down"):
        strengths.append("Debt reduced versus the prior quarter")
    if tech_ctx.get("macd_bullish"):
        strengths.append("MACD signals bullish momentum")

    if tech_ctx.get("near_resistance"):
        risks.append("Trading near short-term resistance")
    if valuation_label == "Premium":
        risks.append("Valuation looks premium on current multiples")
    if fh_ctx.get("cur_opm") is not None and fh_ctx["cur_opm"] < 10:
        risks.append("Operating margin is relatively thin")
    if volatility_ann is not None and volatility_ann > 35:
        risks.append("Higher-than-average price volatility")
    if tech_ctx["rsi"] is not None and tech_ctx["rsi"] >= 70:
        risks.append("RSI is in overbought territory")
    if de_ratio is not None and de_ratio > 100:
        risks.append("Debt levels are elevated relative to equity")

    ctx = {
        "quality_stars": quality_stars,
        "quality_label": quality_label,
        "trend": tech_ctx["trend"],
        "valuation": valuation_label,
        "risk": risk,
        "momentum": tech_ctx["momentum"],
        "strengths": strengths[:4] if strengths else [],
        "risks": risks[:4] if risks else [],
    }
    _render_top_summary(ctx)

    # ---- Key observations (5-8, deterministic) ----
    observations = []
    if rev_growth is not None:
        observations.append((f"Revenue {'increased' if rev_growth >= 0 else 'decreased'} {abs(rev_growth):.1f}% versus the prior period.",
                              "good" if rev_growth >= 0 else "warn"))
    if profit_growth is not None and rev_growth is not None:
        if profit_growth > rev_growth:
            observations.append(("Net profit is growing faster than revenue.", "good"))
        elif profit_growth < 0:
            observations.append(("Net profit declined versus the prior period.", "warn"))
    if fh_ctx.get("debt_down"):
        observations.append(("Debt has reduced compared to the prior quarter.", "good"))
    if tech_ctx["ema20"] and tech_ctx["ema50"] and tech_ctx["ema200"] and close > tech_ctx["ema20"] > tech_ctx["ema50"] > tech_ctx["ema200"]:
        observations.append(("Price remains above EMA20, EMA50 and EMA200.", "good"))
    elif tech_ctx["ema20"] and tech_ctx["ema50"] and tech_ctx["ema200"] and close < tech_ctx["ema20"] < tech_ctx["ema50"] < tech_ctx["ema200"]:
        observations.append(("Price remains below EMA20, EMA50 and EMA200.", "warn"))
    if tech_ctx.get("macd_bullish"):
        observations.append(("MACD remains in bullish territory relative to its signal line.", "good"))
    else:
        observations.append(("MACD is below its signal line, a bearish technical signal.", "warn"))
    if tech_ctx["rsi"] is not None:
        if tech_ctx["rsi"] >= 65:
            observations.append(("RSI is approaching overbought territory.", "warn"))
        elif tech_ctx["rsi"] <= 35:
            observations.append(("RSI is approaching oversold territory.", "warn"))
    if tech_ctx.get("near_resistance"):
        observations.append(("Stock is trading near a major resistance level.", "warn"))
    if tech_ctx.get("near_support"):
        observations.append(("Stock is trading near a major support level.", "good"))
    if valuation_label == "Premium":
        observations.append(("Valuation multiples remain on the higher side versus general thresholds.", "warn"))
    elif valuation_label == "Discounted":
        observations.append(("Valuation multiples are on the lower side versus general thresholds.", "good"))
    if tech_ctx.get("pattern"):
        observations.append((f"Recent candles show a {tech_ctx['pattern']} formation.",
                              "good" if tech_ctx["pattern_dir"] == "bullish" else "warn"))

    _render_key_observations(observations[:8])

    # ---- Investment checklist ----
    checklist = [
        ("Revenue Growth", bool(rev_growth is not None and rev_growth > 0)),
        ("Profit Growth", bool(profit_growth is not None and profit_growth > 0)),
        ("Healthy Margins", bool(fh_ctx.get("cur_opm") is not None and fh_ctx["cur_opm"] > 15)),
        ("Positive Cash Flow", bool(fh_ctx.get("positive_cash"))),
        ("Debt Under Control", bool(de_ratio is not None and de_ratio < 100)),
        ("Bullish Trend", tech_ctx["trend"] == "Bullish"),
        ("Positive Momentum", tech_ctx["momentum"] in ("Strong", "Moderate")),
        ("Away From Resistance", not tech_ctx.get("near_resistance")),
        ("Reasonable Valuation", valuation_label != "Premium"),
    ]
    _render_checklist(checklist)

    # ---- Overall snapshot ----
    _render_snapshot(ctx)

    _md(
        '<div class="qt-ins-caption">Source: Yahoo Finance via yfinance. '
        'All labels are produced by fixed, transparent rules — this page does not use any AI model, '
        'and nothing here is investment advice.</div>'
    )
