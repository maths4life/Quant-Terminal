"""Pure display-formatting helpers. No data fetching, no indicator math —
keeps this module trivially testable and reusable."""


def fmt_indian(n):
    """Format an integer using the Indian digit-grouping system (1,00,000)."""
    if n is None:
        return "—"
    n = int(n)
    if n >= 10_000_000:
        return f"{n / 10_000_000:.2f} Cr"
    if n >= 100_000:
        return f"{n / 100_000:.2f} L"
    s = str(n)
    if len(s) <= 3:
        return s
    last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    return ",".join(reversed(parts)) + "," + last3


def fmt_mcap(n):
    """Format market cap (raw currency units) using Indian Cr / Lakh."""
    if n is None:
        return "—"
    n = float(n)
    if n >= 1_00_00_000:
        return f"₹{n / 1_00_00_000:,.0f} Cr"
    if n >= 1_00_000:
        return f"₹{n / 1_00_000:,.1f} L"
    return f"₹{n:,.0f}"


def fmt_ratio(v, suffix="", decimals=2):
    if v is None:
        return "—"
    try:
        return f"{float(v):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "—"


def fmt_pct_val(v, decimals=2):
    if v is None:
        return "—"
    try:
        val = float(v)
        if val < 1:  # yfinance sometimes returns dividend yield as a fraction
            val *= 100
        return f"{val:.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"
