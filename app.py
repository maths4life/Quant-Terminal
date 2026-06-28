import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, time as dtime
import pytz
from streamlit_lightweight_charts import renderLightweightCharts

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Quant Terminal",
    page_icon="💹",
    initial_sidebar_state="expanded",
)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #090B10;
    --bg-secondary: #121722;
    --bg-card: #171C26;
    --bg-elev: #1C2230;
    --accent: #00E5B4;
    --accent-dim: rgba(0,229,180,0.12);
    --bullish: #00C853;
    --bearish: #FF5252;
    --text-primary: #FFFFFF;
    --text-secondary: #9BA3AF;
    --text-tertiary: #5B6473;
    --border: rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.14);
}

html, body, .stApp {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-feature-settings: 'cv11','ss01','ss03';
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

.block-container {
    padding: 1.25rem 1.75rem 2rem 1.75rem !important;
    max-width: 100% !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #232A38; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── ANIMATIONS ── */
@keyframes pulse-dot {
    0%,100% { box-shadow: 0 0 0 0 rgba(0,229,180,0.55); }
    50%     { box-shadow: 0 0 0 6px rgba(0,229,180,0); }
}
@keyframes pulse-red {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,82,82,0.55); }
    50%     { box-shadow: 0 0 0 6px rgba(255,82,82,0); }
}
@keyframes fade-up {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0% { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}

.fade-up { animation: fade-up .4s ease-out both; }

/* ── TOP HEADER ── */
.qt-header {
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem;
    background: linear-gradient(180deg, #11161F 0%, #0C1019 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: .75rem 1.1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.qt-brand { display:flex; align-items:center; gap:.7rem; }
.qt-logo {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, #00E5B4 0%, #00A884 100%);
    display:grid; place-items:center;
    color:#04121A; font-weight:800; font-family:'JetBrains Mono',monospace;
    box-shadow: 0 4px 14px rgba(0,229,180,.25), inset 0 0 0 1px rgba(255,255,255,.15);
}
.qt-title {
    font-size: .92rem; font-weight: 700; letter-spacing: .14em;
    color: #fff; text-transform: uppercase;
}
.qt-subtitle {
    font-size: .65rem; letter-spacing: .18em; color: var(--text-tertiary);
    text-transform: uppercase; margin-top: 1px;
}
.qt-header-search {
    flex: 1; max-width: 420px;
    display:flex; align-items:center; gap:.55rem;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 10px; padding: .5rem .85rem;
    color: var(--text-tertiary); font-size: .8rem;
}
.qt-header-search kbd {
    margin-left:auto; font-family:'JetBrains Mono',monospace;
    font-size:.65rem; background:#1A1F2B; border:1px solid var(--border);
    border-radius:4px; padding:1px 6px; color:var(--text-secondary);
}
.qt-header-right { display:flex; align-items:center; gap:.6rem; }
.qt-chip {
    display:inline-flex; align-items:center; gap:.45rem;
    background: var(--bg-card); border:1px solid var(--border);
    padding:.42rem .75rem; border-radius:999px;
    font-size:.72rem; color:var(--text-secondary); font-weight:500;
    font-family:'JetBrains Mono',monospace;
}
.qt-dot { width:8px; height:8px; border-radius:50%; display:inline-block; }
.qt-dot.live { background: var(--accent); animation: pulse-dot 2s infinite; }
.qt-dot.closed { background: var(--bearish); animation: pulse-red 2.4s infinite; }
.qt-icon-btn {
    width:34px; height:34px; border-radius:9px;
    background: var(--bg-card); border:1px solid var(--border);
    display:grid; place-items:center; color: var(--text-secondary);
    cursor:pointer; transition: all .15s;
}
.qt-icon-btn:hover { color: var(--accent); border-color: var(--accent-dim); }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem !important; }

.qt-side-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: .85rem .9rem;
    margin-bottom: .7rem;
}
.qt-side-section:hover { border-color: var(--border-strong); }
.qt-side-head {
    display:flex; align-items:center; gap:.5rem;
    font-size: .62rem; font-weight: 600; letter-spacing: .16em;
    text-transform: uppercase; color: var(--text-tertiary);
    margin-bottom: .65rem;
    font-family: 'Inter', sans-serif;
}
.qt-side-head svg { width: 13px; height: 13px; stroke: var(--accent); }

[data-testid="stSidebar"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: .68rem !important; font-weight: 500 !important;
    letter-spacing: .08em !important; text-transform: uppercase !important;
    color: var(--text-tertiary) !important;
}
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .92rem !important; font-weight: 600 !important;
    padding: .55rem .8rem !important;
    transition: all .15s;
}
[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,180,.12) !important;
}

/* Radio as pill stack */
[data-testid="stSidebar"] .stRadio > div {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(58px, 1fr)) !important;
    gap: .35rem !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: .42rem .5rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .7rem !important; font-weight: 600 !important;
    letter-spacing: .04em !important; color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    text-align: center !important;
    cursor: pointer !important; transition: all .15s !important;
    display:flex; align-items:center; justify-content:center;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    border-color: var(--accent-dim) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: rgba(0,229,180,.1) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent), 0 4px 12px rgba(0,229,180,.18) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* Checkboxes — toggle-pill feel */
[data-testid="stSidebar"] .stCheckbox {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: .4rem .65rem;
    margin-bottom: .3rem;
    transition: all .15s;
}
[data-testid="stSidebar"] .stCheckbox:hover { border-color: var(--accent-dim); }
[data-testid="stSidebar"] .stCheckbox label {
    font-family: 'Inter', sans-serif !important;
    font-size: .78rem !important; font-weight: 500 !important;
    letter-spacing: .02em !important; text-transform: none !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: linear-gradient(180deg, rgba(0,229,180,.16), rgba(0,229,180,.06)) !important;
    border: 1px solid rgba(0,229,180,.35) !important;
    border-radius: 9px !important;
    color: var(--accent) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .75rem !important; font-weight: 600 !important;
    letter-spacing: .06em !important; text-transform: uppercase !important;
    padding: .55rem !important; transition: all .15s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(0,229,180,.22) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 4px 18px rgba(0,229,180,.25) !important;
    transform: translateY(-1px);
}

[data-testid="stSidebar"] hr { display:none !important; }

/* Recent ticker chips (Streamlit buttons inside columns) */
[data-testid="stSidebar"] [data-testid="column"] .stButton button {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    padding: .35rem .2rem !important;
    font-size: .68rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] [data-testid="column"] .stButton button:hover {
    color: var(--accent) !important; border-color: var(--accent-dim) !important;
    background: rgba(0,229,180,.06) !important;
    box-shadow: none !important;
}

/* ── HERO ── */
.qt-hero {
    background: linear-gradient(135deg, #141A26 0%, #0E131C 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative; overflow: hidden;
    animation: fade-up .4s ease-out both;
}
.qt-hero::before {
    content:''; position:absolute; inset:0;
    background: radial-gradient(900px 200px at 0% 0%, rgba(0,229,180,.08), transparent 60%);
    pointer-events:none;
}
.qt-hero-grid {
    display:grid; grid-template-columns: 1fr auto; gap:1.5rem; align-items:center;
    position: relative;
}
.qt-hero-left { display:flex; flex-direction:column; gap:.5rem; min-width:0; }
.qt-hero-tags { display:flex; gap:.4rem; flex-wrap:wrap; }
.qt-tag {
    display:inline-flex; align-items:center; gap:.35rem;
    background: var(--bg-card); border:1px solid var(--border);
    padding:.25rem .6rem; border-radius:6px;
    font-family:'JetBrains Mono',monospace; font-size:.65rem;
    color: var(--text-secondary); letter-spacing:.06em;
}
.qt-tag.accent { color: var(--accent); border-color: var(--accent-dim); background: rgba(0,229,180,.06); }
.qt-ticker {
    font-family:'JetBrains Mono',monospace; font-weight:700;
    font-size: 1.9rem; letter-spacing:-.01em; color:#fff; line-height:1.1;
}
.qt-ticker .sep { color: var(--text-tertiary); font-weight:400; margin:0 .35rem; }
.qt-meta { color: var(--text-secondary); font-size:.78rem; }
.qt-hero-right { text-align:right; min-width: 220px; }
.qt-price {
    font-family:'JetBrains Mono',monospace; font-weight:700;
    font-size: 2.4rem; letter-spacing:-.02em; line-height:1;
    color:#fff;
}
.qt-change {
    margin-top:.45rem;
    display:inline-flex; align-items:center; gap:.45rem;
    font-family:'JetBrains Mono',monospace; font-weight:600;
    font-size: .9rem; padding:.32rem .7rem; border-radius:8px;
}
.qt-change.up   { color: var(--accent); background: rgba(0,229,180,.1); border:1px solid rgba(0,229,180,.3); }
.qt-change.down { color: var(--bearish); background: rgba(255,82,82,.1); border:1px solid rgba(255,82,82,.3); }

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: .9rem 1rem !important;
    position: relative !important; overflow: hidden !important;
    transition: all .2s ease !important;
    animation: fade-up .4s ease-out both;
}
[data-testid="stMetric"]::before {
    content:''; position:absolute; top:0; left:0;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,180,.5), transparent);
    opacity:0; transition: opacity .2s;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-strong) !important;
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0,0,0,.4), 0 0 0 1px rgba(0,229,180,.08);
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: .65rem !important; font-weight: 600 !important;
    letter-spacing: .14em !important; text-transform: uppercase !important;
    color: var(--text-tertiary) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.25rem !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important; line-height: 1.3 !important;
    letter-spacing: -.01em !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .72rem !important; font-weight: 600 !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="stMetricDelta"][data-direction="up"]   { color: var(--accent) !important; }
[data-testid="stMetricDelta"][data-direction="down"] { color: var(--bearish) !important; }

/* ── CHART SHELL ── */
.qt-chart-shell {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1rem .5rem 1rem;
    margin-top: 1rem;
    animation: fade-up .5s ease-out both;
}
.qt-chart-toolbar {
    display:flex; align-items:center; justify-content:space-between;
    gap:.75rem; flex-wrap:wrap;
    padding-bottom: .8rem; margin-bottom: .8rem;
    border-bottom: 1px solid var(--border);
}
.qt-toolbar-group { display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; }
.qt-pill {
    display:inline-flex; align-items:center; gap:.4rem;
    padding:.36rem .75rem; border-radius:999px;
    background: var(--bg-primary); border:1px solid var(--border);
    font-family:'JetBrains Mono', monospace; font-size:.7rem; font-weight:600;
    color: var(--text-secondary); letter-spacing:.04em;
}
.qt-pill.on { color: var(--accent); border-color: var(--accent-dim); background: rgba(0,229,180,.06); }
.qt-pill.off { opacity:.55; }
.qt-pill .swatch { width:8px; height:8px; border-radius:2px; }
.qt-tool {
    width:32px; height:32px; border-radius:8px;
    background: var(--bg-primary); border:1px solid var(--border);
    display:inline-grid; place-items:center; color: var(--text-secondary);
    cursor: not-allowed; transition: all .15s;
}
.qt-tool:hover { color: var(--accent); border-color: var(--accent-dim); }

/* ── POPULAR TICKER GRID ── */
.qt-pop-grid {
    display:grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap:.5rem; margin-top:.5rem;
}

/* ── FOOTER ── */
.qt-footer {
    margin-top: 1.5rem; padding-top: 1rem;
    border-top: 1px solid var(--border);
    display:flex; justify-content:space-between; align-items:center;
    flex-wrap:wrap; gap:.5rem;
    color: var(--text-tertiary); font-size: .7rem;
    font-family: 'JetBrains Mono', monospace; letter-spacing:.06em;
}

/* ── ALERTS / SPINNER ── */
[data-testid="stSpinner"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .75rem !important;
    color: var(--accent) !important;
}
[data-testid="stInfo"], [data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .8rem !important;
    color: var(--text-secondary) !important;
}
[data-testid="stHorizontalBlock"] { gap: .65rem !important; }

/* Section title above metric rows */
.qt-section-title {
    display:flex; align-items:center; gap:.6rem;
    font-size: .68rem; font-weight: 600; letter-spacing:.16em;
    text-transform: uppercase; color: var(--text-tertiary);
    margin: 1rem 0 .55rem 0;
}
.qt-section-title::after {
    content:''; flex:1; height:1px; background: var(--border);
}

/* Responsive */
@media (max-width: 900px) {
    .qt-hero-grid { grid-template-columns: 1fr; }
    .qt-hero-right { text-align:left; }
    .qt-header-search { display:none; }
    .qt-price { font-size: 1.9rem; }
    .qt-ticker { font-size: 1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def compute_rsi(series, period=14):
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def fmt_indian(n):
    """Format number in Indian system: 1,00,000 style."""
    if n is None:
        return "—"
    n = int(n)
    if n >= 10_000_000:
        return f"{n/10_000_000:.2f} Cr"
    if n >= 100_000:
        return f"{n/100_000:.2f} L"
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest  = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    return ",".join(reversed(parts)) + "," + last3


def is_nse_open():
    """Returns (is_open: bool, status_str: str)."""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    market_open  = dtime(9, 15)
    market_close = dtime(15, 30)
    if now.weekday() >= 5:
        return False, "CLOSED · Weekend"
    t = now.time()
    if market_open <= t <= market_close:
        return True, "OPEN"
    if t < market_open:
        opens_in = datetime.combine(now.date(), market_open)
        opens_in = ist.localize(opens_in)
        diff = opens_in - now
        m = int(diff.seconds / 60)
        return False, f"PRE-MARKET · Opens in {m}m"
    return False, "CLOSED · After Hours"


def rsi_label(v):
    if v is None: return "—", "#5B6473"
    if v >= 70:   return f"{v:.1f} OVERBOUGHT", "#FF5252"
    if v <= 30:   return f"{v:.1f} OVERSOLD",   "#00E5B4"
    return f"{v:.1f} NEUTRAL", "#9BA3AF"


# ── DATA FETCH ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=False)
    if df.empty:
        return None
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df = df.reset_index()
    date_col = "Datetime" if "Datetime" in df.columns else "Date"
    df = df.rename(columns={date_col: "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    df["time"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"]  = compute_rsi(df["Close"])
    df["TP"]   = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (df["TP"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df


@st.cache_data(ttl=86400)
def fetch_52w(ticker):
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=False)
    if df.empty:
        return None, None
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return float(df["High"].max()), float(df["Low"].min())


@st.cache_data(ttl=86400)
def fetch_avg_vol(ticker):
    df = yf.download(ticker, period="2mo", interval="1d", auto_adjust=False)
    if df.empty:
        return None
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return int(df["Volume"].tail(20).mean())


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "recent" not in st.session_state:
    st.session_state.recent = []


def add_recent(t):
    if t not in st.session_state.recent:
        st.session_state.recent.insert(0, t)
        st.session_state.recent = st.session_state.recent[:5]


# ── ICONS (inline SVG) ────────────────────────────────────────────────────────
ICON_SEARCH  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
ICON_CLOCK   = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></svg>'
ICON_GEAR    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82c.16.39.5.7.93.84H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
ICON_BELL    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>'
ICON_CANDLE  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3M8 18v3"/><rect x="6" y="6" width="4" height="12" rx="1"/><path d="M16 3v5M16 16v5"/><rect x="14" y="8" width="4" height="8" rx="1"/></svg>'
ICON_MARKET  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m7 14 4-4 4 4 5-6"/></svg>'
ICON_LAYERS  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 2 9 5-9 5-9-5 9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/></svg>'
ICON_TIME    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
ICON_STAR    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15 9 22 9.3 17 14 18.5 21 12 17.3 5.5 21 7 14 2 9.3 9 9 12 2"/></svg>'
ICON_REFRESH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg>'
ICON_TOOL    = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19 7-7 3 3-7 7-3-3z"/><path d="m18 13-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/></svg>'

# ── TOP HEADER ────────────────────────────────────────────────────────────────
market_open, market_status = is_nse_open()
ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
dot_class = "live" if market_open else "closed"

st.markdown(f"""
<div class="qt-header">
  <div class="qt-brand">
    <div class="qt-logo">Q</div>
    <div>
      <div class="qt-title">Quant Terminal</div>
      <div class="qt-subtitle">Institutional · Equity Research</div>
    </div>
  </div>
  <div class="qt-header-search">
    <span style="width:14px;height:14px;display:inline-block;">{ICON_SEARCH}</span>
    <span>Search symbols, indices, sectors…</span>
    <kbd>⌘ K</kbd>
  </div>
  <div class="qt-header-right">
    <div class="qt-chip"><span class="qt-dot {dot_class}"></span> NSE · {market_status}</div>
    <div class="qt-chip"><span style="width:12px;height:12px;display:inline-block;color:var(--text-tertiary)">{ICON_CLOCK}</span> {ist_now.strftime('%H:%M:%S')} IST</div>
    <div class="qt-icon-btn" title="Alerts">{ICON_BELL}</div>
    <div class="qt-icon-btn" title="Settings">{ICON_GEAR}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
POPULAR = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS","ICICIBANK.NS","^NSEI","^NSEBANK"]

with st.sidebar:
    # Brand block
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.6rem;padding:.25rem .25rem 1rem .25rem;">
      <div class="qt-logo" style="width:30px;height:30px;font-size:.85rem;">Q</div>
      <div>
        <div style="font-size:.78rem;font-weight:700;letter-spacing:.16em;color:#fff;text-transform:uppercase;">Controls</div>
        <div style="font-size:.6rem;letter-spacing:.16em;color:var(--text-tertiary);text-transform:uppercase;">Workspace</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SEARCH SECTION
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_SEARCH}<span>Search Symbol</span></div>', unsafe_allow_html=True)
    ticker_raw = st.text_input("Symbol", "RELIANCE.NS", label_visibility="collapsed",
                               help="NSE: .NS  |  BSE: .BO")
    ticker = ticker_raw.strip().upper()
    st.markdown('<div style="font-size:.65rem;color:var(--text-tertiary);margin-top:.45rem;letter-spacing:.04em;">e.g. INFY.NS · TCS.NS · HDFCBANK.NS · ^NSEI</div></div>', unsafe_allow_html=True)

    # POPULAR
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_STAR}<span>Popular · NSE</span></div>', unsafe_allow_html=True)
    pop_cols = st.columns(2)
    for i, sym in enumerate(POPULAR):
        if pop_cols[i % 2].button(sym.replace("^NSEI","NIFTY50").replace("^NSEBANK","BANKNIFTY").replace(".NS",""),
                                  key=f"pop_{sym}", use_container_width=True):
            st.session_state["_jump"] = sym
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # RECENTS
    if st.session_state.recent:
        st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CLOCK}<span>Recent Searches</span></div>', unsafe_allow_html=True)
        cols = st.columns(min(len(st.session_state.recent), 3))
        for i, sym in enumerate(st.session_state.recent):
            if cols[i % len(cols)].button(sym.replace(".NS",""), key=f"rec_{sym}", use_container_width=True):
                st.session_state["_jump"] = sym
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "_jump" in st.session_state:
        ticker = st.session_state.pop("_jump")

    # MARKET / TIMEFRAME
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_TIME}<span>Time Frame</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.62rem;color:var(--text-tertiary);letter-spacing:.14em;text-transform:uppercase;margin-bottom:.3rem;">Period</div>', unsafe_allow_html=True)
    period = st.radio("Period", ["1mo","3mo","6mo","1y","2y","5y","max"], index=3, label_visibility="collapsed")
    st.markdown('<div style="font-size:.62rem;color:var(--text-tertiary);letter-spacing:.14em;text-transform:uppercase;margin:.55rem 0 .3rem 0;">Interval</div>', unsafe_allow_html=True)
    interval_map = {"Daily":"1d","Weekly":"1wk","Monthly":"1mo"}
    interval_label = st.radio("Interval", list(interval_map.keys()), index=0, label_visibility="collapsed")
    interval = interval_map[interval_label]
    st.markdown('</div>', unsafe_allow_html=True)

    # CHART SETTINGS / INDICATORS
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_LAYERS}<span>Indicators · Overlays</span></div>', unsafe_allow_html=True)
    show_ma20  = st.checkbox("MA 20",  True)
    show_ma50  = st.checkbox("MA 50",  True)
    show_vwap  = st.checkbox("VWAP",   False)
    show_prevc = st.checkbox("Previous Close", True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_CANDLE}<span>Sub-Panels</span></div>', unsafe_allow_html=True)
    show_volume = st.checkbox("Volume",   True)
    show_rsi    = st.checkbox("RSI (14)", True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ACTIONS / MARKET STATUS
    st.markdown(f'<div class="qt-side-section"><div class="qt-side-head">{ICON_GEAR}<span>Actions</span></div>', unsafe_allow_html=True)
    if st.button("↺  Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"""
    <div style="margin-top:.7rem;display:flex;flex-direction:column;gap:.4rem;">
      <div class="qt-chip" style="justify-content:center;width:100%;">
        <span class="qt-dot {dot_class}"></span> NSE · {market_status}
      </div>
      <div style="font-size:.62rem;color:var(--text-tertiary);text-align:center;letter-spacing:.1em;text-transform:uppercase;">
        Data · Yahoo Finance · Delayed 15m
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ── FETCH DATA ────────────────────────────────────────────────────────────────
with st.spinner(f"Loading {ticker}  ·  {period}  ·  {interval_label}…"):
    df         = fetch_data(ticker, period, interval)
    w52_h, w52_l = fetch_52w(ticker)
    true_avg_vol = fetch_avg_vol(ticker)

if df is None:
    st.error(f"No data found for '{ticker}'")
    st.info("Try: RELIANCE.NS  ·  INFY.NS  ·  TCS.NS  ·  HDFCBANK.NS  ·  ^NSEI")
    st.stop()

if len(df) < 55:
    st.warning("Limited history — MA50 / RSI readings may be inaccurate. Try a longer period.")

add_recent(ticker)

last  = df.iloc[-1]
prev  = df.iloc[-2]
close      = float(last["Close"])
prev_close = float(prev["Close"])
change     = ((close - prev_close) / prev_close) * 100
change_abs = close - prev_close

if w52_h is None:
    w52_h = float(df["High"].max())
if w52_l is None:
    w52_l = float(df["Low"].min())

pct_from_high = ((close - w52_h) / w52_h) * 100
pct_from_low  = ((close - w52_l) / w52_l) * 100

last_ma20  = float(df["MA20"].dropna().iloc[-1])  if not df["MA20"].dropna().empty  else None
last_ma50  = float(df["MA50"].dropna().iloc[-1])  if not df["MA50"].dropna().empty  else None
last_rsi   = float(df["RSI"].dropna().iloc[-1])   if not df["RSI"].dropna().empty   else None
last_vwap  = float(df["VWAP"].dropna().iloc[-1])  if not df["VWAP"].dropna().empty  else None
avg_vol20  = true_avg_vol if true_avg_vol else (int(df["Volume"].tail(20).mean()) if "Volume" in df.columns else None)

rsi_txt, rsi_color = rsi_label(last_rsi)
date_str = last["Date"].strftime("%d %b %Y") if hasattr(last["Date"], "strftime") else ""

# ── HERO CARD ─────────────────────────────────────────────────────────────────
change_class = "up" if change >= 0 else "down"
arrow = "▲" if change >= 0 else "▼"
exchange = "NSE" if ticker.endswith(".NS") else ("BSE" if ticker.endswith(".BO") else "INDEX")

st.markdown(f"""
<div class="qt-hero">
  <div class="qt-hero-grid">
    <div class="qt-hero-left">
      <div class="qt-hero-tags">
        <span class="qt-tag accent">● {exchange}</span>
        <span class="qt-tag">{interval_label} · {period}</span>
        <span class="qt-tag">RSI {rsi_txt}</span>
        <span class="qt-tag">Updated {date_str}</span>
      </div>
      <div class="qt-ticker">{ticker}<span class="sep">/</span><span style="color:var(--text-secondary);font-size:1.1rem;">EQUITY</span></div>
      <div class="qt-meta">Live institutional view · Yahoo Finance feed · IST {ist_now.strftime('%H:%M')}</div>
    </div>
    <div class="qt-hero-right">
      <div class="qt-price">₹{close:,.2f}</div>
      <div class="qt-change {change_class}">{arrow} {abs(change):.2f}%  ·  {'+' if change_abs>=0 else ''}{change_abs:,.2f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── METRIC ROW 1 ──────────────────────────────────────────────────────────────
st.markdown('<div class="qt-section-title">Market Snapshot</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Last Price", f"₹{close:,.2f}",        f"{change:+.2f}%")
c2.metric("Day High",   f"₹{float(last['High']):,.2f}")
c3.metric("Day Low",    f"₹{float(last['Low']):,.2f}")
c4.metric("Volume",     fmt_indian(float(last["Volume"])) if "Volume" in df.columns else "—")
c5.metric("52W High",   f"₹{w52_h:,.2f}",         f"{abs(pct_from_high):.1f}% below ATH")
c6.metric("52W Low",    f"₹{w52_l:,.2f}",          f"{pct_from_low:.1f}% above")

# ── METRIC ROW 2 ──────────────────────────────────────────────────────────────
st.markdown('<div class="qt-section-title">Technical Indicators</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

if last_ma20:
    above20 = close > last_ma20
    m1.metric("MA 20", f"₹{last_ma20:,.2f}", "▲ Above" if above20 else "▼ Below")
else:
    m1.metric("MA 20", "—")

if last_ma50:
    above50 = close > last_ma50
    m2.metric("MA 50", f"₹{last_ma50:,.2f}", "▲ Above" if above50 else "▼ Below")
else:
    m2.metric("MA 50", "—")

m3.metric("RSI 14",      f"{last_rsi:.1f}" if last_rsi else "—")
m4.metric("Avg Vol 20d", fmt_indian(avg_vol20))


# ── CHART HELPERS ─────────────────────────────────────────────────────────────
def base_opts(show_time=True):
    return {
        "layout": {
            "background": {"type": "solid", "color": "#171C26"},
            "textColor": "#9BA3AF", "fontSize": 11,
            "fontFamily": "'JetBrains Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(255,255,255,0.03)"},
            "horzLines": {"color": "rgba(255,255,255,0.03)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(0,229,180,0.4)", "labelBackgroundColor": "#00E5B4"},
            "horzLine": {"color": "rgba(0,229,180,0.4)", "labelBackgroundColor": "#00E5B4"},
        },
        "rightPriceScale": {
            "borderColor": "rgba(255,255,255,0.06)", "textColor": "#9BA3AF",
            "autoScale": True, "minValue": 0,
        },
        "timeScale": {
            "borderColor": "rgba(255,255,255,0.06)", "timeVisible": show_time,
            "secondsVisible": False, "visible": show_time,
        },
    }


# ── CANDLE DATA ───────────────────────────────────────────────────────────────
candles = (
    df[["time","Open","High","Low","Close"]]
    .rename(columns={"Open":"open","High":"high","Low":"low","Close":"close"})
    .to_dict("records")
)
for r in candles:
    r["open"]  = float(r["open"])
    r["high"]  = float(r["high"])
    r["low"]   = float(r["low"])
    r["close"] = float(r["close"])

price_series = [{
    "type": "Candlestick", "data": candles,
    "options": {
        "upColor": "#00C853", "downColor": "#FF5252",
        "borderVisible": False,
        "wickUpColor": "#00C853", "wickDownColor": "#FF5252",
    }
}]

if show_ma20 and last_ma20:
    ma20d = df[["time","MA20"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
        "options": {"color": "#F5A623", "lineWidth": 1}
    })

if show_ma50 and last_ma50:
    ma50d = df[["time","MA50"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
        "options": {"color": "#4D9FFF", "lineWidth": 1}
    })

if show_vwap and last_vwap:
    vwapd = df[["time","VWAP"]].dropna()
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
        "options": {"color": "#E879F9", "lineWidth": 1, "lineStyle": 2}
    })

if show_prevc:
    price_series.append({
        "type": "Line",
        "data": [{"time": r["time"], "value": prev_close} for r in candles],
        "options": {"color": "rgba(200,208,220,0.25)", "lineWidth": 1, "lineStyle": 2}
    })

price_opts = base_opts(show_time=not (show_volume or show_rsi))
price_opts["watermark"] = {
    "visible": True, "fontSize": 60,
    "horzAlign": "center", "vertAlign": "center",
    "color": "rgba(255,255,255,0.022)", "text": ticker,
}

charts_to_render = [{"chart": price_opts, "series": price_series}]

if show_volume and "Volume" in df.columns:
    vol_data = []
    for _, row in df.iterrows():
        c = "#00C853" if float(row["Close"]) >= float(row["Open"]) else "#FF5252"
        vol_data.append({"time": row["time"], "value": float(row["Volume"]), "color": c + "77"})
    vol_opts = base_opts(show_time=not show_rsi)
    vol_opts["rightPriceScale"]["minValue"] = 0
    charts_to_render.append({
        "chart": vol_opts,
        "series": [{"type": "Histogram", "data": vol_data,
                    "options": {"priceFormat": {"type": "volume"}, "priceScaleId": ""}}]
    })

if show_rsi:
    rsi_df   = df[["time","RSI"]].dropna()
    rsi_data = [{"time": r["time"], "value": float(r["RSI"])} for _, r in rsi_df.iterrows()]
    ob_line  = [{"time": r["time"], "value": 70.0} for _, r in rsi_df.iterrows()]
    os_line  = [{"time": r["time"], "value": 30.0} for _, r in rsi_df.iterrows()]
    rsi_opts = base_opts(show_time=True)
    rsi_opts["rightPriceScale"]["autoScale"] = False
    rsi_opts["rightPriceScale"]["minValue"]  = 0
    rsi_opts["rightPriceScale"]["maxValue"]  = 100
    charts_to_render.append({
        "chart": rsi_opts,
        "series": [
            {"type": "Line", "data": rsi_data, "options": {"color": "#A78BFA", "lineWidth": 1}},
            {"type": "Line", "data": ob_line,  "options": {"color": "rgba(255,82,82,0.45)",  "lineWidth": 1, "lineStyle": 2}},
            {"type": "Line", "data": os_line,  "options": {"color": "rgba(0,229,180,0.45)",  "lineWidth": 1, "lineStyle": 2}},
        ]
    })

total_h = 620
num_panels = len(charts_to_render)
if num_panels == 1:
    heights = [total_h]
elif num_panels == 2:
    heights = [int(total_h * 0.65), int(total_h * 0.35)]
else:
    heights = [int(total_h * 0.55), int(total_h * 0.22), int(total_h * 0.23)]

for i, h in enumerate(heights):
    charts_to_render[i]["chart"]["height"] = h


# ── CHART SHELL + TOOLBAR ─────────────────────────────────────────────────────
def pill(on, label, swatch=None):
    cls = "qt-pill on" if on else "qt-pill off"
    sw = f'<span class="swatch" style="background:{swatch};"></span>' if swatch else ''
    return f'<span class="{cls}">{sw}{label}</span>'

pills_html = "".join([
    pill(True,  "Candles", "#00C853"),
    pill(show_ma20,  "MA 20",  "#F5A623"),
    pill(show_ma50,  "MA 50",  "#4D9FFF"),
    pill(show_vwap,  "VWAP",   "#E879F9"),
    pill(show_prevc, "Prev Close", "rgba(200,208,220,.5)"),
    pill(show_volume,"Volume", "#9BA3AF"),
    pill(show_rsi,   "RSI 14", "#A78BFA"),
])

tools_html = "".join([
    f'<div class="qt-tool" title="Draw (coming soon)">{ICON_TOOL}</div>',
    f'<div class="qt-tool" title="Compare (coming soon)">{ICON_MARKET}</div>',
    f'<div class="qt-tool" title="Indicators (coming soon)">{ICON_LAYERS}</div>',
    f'<div class="qt-tool" title="Screenshot (coming soon)">{ICON_REFRESH}</div>',
])

st.markdown(f"""
<div class="qt-chart-shell">
  <div class="qt-chart-toolbar">
    <div class="qt-toolbar-group">{pills_html}</div>
    <div class="qt-toolbar-group">{tools_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── RENDER ────────────────────────────────────────────────────────────────────
try:
    renderLightweightCharts(charts_to_render, key="quant_charts")
except Exception:
    renderLightweightCharts(charts_to_render)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qt-footer">
  <div>QUANT TERMINAL · v1.0 · Institutional Build</div>
  <div>Powered by Yahoo Finance · Updated {ist_now.strftime('%d %b %Y · %H:%M:%S')} IST</div>
</div>
""", unsafe_allow_html=True)
