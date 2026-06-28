from datetime import datetime, time as dtime
import pytz

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