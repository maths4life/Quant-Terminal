import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts


def base_opts(show_time=True):
    return {
        "layout": {
            "background": {"type": "solid", "color": "#FFFFFF"},
            "textColor": "#64748B", "fontSize": 11,
            "fontFamily": "'JetBrains Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(15,23,42,0.04)"},
            "horzLines": {"color": "rgba(15,23,42,0.04)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(37,99,235,0.4)", "labelBackgroundColor": "#2563EB"},
            "horzLine": {"color": "rgba(37,99,235,0.4)", "labelBackgroundColor": "#2563EB"},
        },
        "rightPriceScale": {
            "borderColor": "rgba(15,23,42,0.08)", "textColor": "#64748B",
            "autoScale": True, "minValue": 0,
        },
        "timeScale": {
            "borderColor": "rgba(15,23,42,0.08)", "timeVisible": show_time,
            "secondsVisible": False, "visible": show_time,
        },
    }


def render_chart(
    df,
    ticker,
    prev_close,
    show_ma20,
    show_ma50,
    show_vwap,
    show_prevc,
    show_volume,
    show_rsi,
    last_ma20,
    last_ma50,
    last_vwap,
    ICON_TOOL,
    ICON_MARKET,
    ICON_LAYERS,
    ICON_REFRESH,
):
    # ── CANDLE DATA ──────────────────────────────────────────────────
    # BUG FIX: rows with any missing OHLC value (common on weekly/monthly
    # intervals or thinly-traded tickers) must be dropped before building
    # the payload. NaN has no JSON representation — a single NaN anywhere
    # in the series makes the whole component payload fail to parse,
    # which is what was breaking every panel, not just the gappy row.
    candle_src = df[["time", "Open", "High", "Low", "Close"]].dropna()
    candles = (
        candle_src
        .rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
        .to_dict("records")
    )
    for r in candles:
        r["open"] = float(r["open"])
        r["high"] = float(r["high"])
        r["low"] = float(r["low"])
        r["close"] = float(r["close"])

    price_series = [{
        "type": "Candlestick", "data": candles,
        "options": {
            "upColor": "#16A34A", "downColor": "#DC2626",
            "borderVisible": False,
            "wickUpColor": "#16A34A", "wickDownColor": "#DC2626",
        }
    }]

    if show_ma20 and last_ma20:
        ma20d = df[["time", "MA20"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
            "options": {"color": "#F59E0B", "lineWidth": 1}
        })

    if show_ma50 and last_ma50:
        ma50d = df[["time", "MA50"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
            "options": {"color": "#2563EB", "lineWidth": 1}
        })

    if show_vwap and last_vwap:
        vwapd = df[["time", "VWAP"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
            "options": {"color": "#C026D3", "lineWidth": 1, "lineStyle": 2}
        })

    if show_prevc and prev_close == prev_close:  # NaN-safe check (NaN != NaN)
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": prev_close} for r in candles],
            "options": {"color": "rgba(100,116,139,0.5)", "lineWidth": 1, "lineStyle": 2}
        })

    price_opts = base_opts(show_time=not (show_volume or show_rsi))
    price_opts["watermark"] = {
        "visible": True, "fontSize": 60,
        "horzAlign": "center", "vertAlign": "center",
        "color": "rgba(15,23,42,0.03)", "text": ticker,
    }

    charts_to_render = [{"chart": price_opts, "series": price_series}]

    if show_volume and "Volume" in df.columns:
        vol_src = df[["time", "Open", "Close", "Volume"]].dropna()
        vol_data = []
        for _, row in vol_src.iterrows():
            c = "#16A34A" if float(row["Close"]) >= float(row["Open"]) else "#DC2626"
            vol_data.append({"time": row["time"], "value": float(row["Volume"]), "color": c + "66"})
        vol_opts = base_opts(show_time=not show_rsi)
        vol_opts["rightPriceScale"]["minValue"] = 0
        charts_to_render.append({
            "chart": vol_opts,
            "series": [{"type": "Histogram", "data": vol_data,
                        "options": {"priceFormat": {"type": "volume"}, "priceScaleId": ""}}]
        })

    if show_rsi:
        rsi_df = df[["time", "RSI"]].dropna()
        rsi_data = [{"time": r["time"], "value": float(r["RSI"])} for _, r in rsi_df.iterrows()]
        ob_line = [{"time": r["time"], "value": 70.0} for _, r in rsi_df.iterrows()]
        os_line = [{"time": r["time"], "value": 30.0} for _, r in rsi_df.iterrows()]
        rsi_opts = base_opts(show_time=True)
        rsi_opts["rightPriceScale"]["autoScale"] = False
        rsi_opts["rightPriceScale"]["minValue"] = 0
        rsi_opts["rightPriceScale"]["maxValue"] = 100
        charts_to_render.append({
            "chart": rsi_opts,
            "series": [
                {"type": "Line", "data": rsi_data, "options": {"color": "#7C3AED", "lineWidth": 1}},
                {"type": "Line", "data": ob_line, "options": {"color": "rgba(220,38,38,0.45)", "lineWidth": 1, "lineStyle": 2}},
                {"type": "Line", "data": os_line, "options": {"color": "rgba(22,163,74,0.45)", "lineWidth": 1, "lineStyle": 2}},
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

    # ── TOOLBAR ──────────────────────────────────────────────────────
    def pill(on, label, swatch=None):
        cls = "qt-pill on" if on else "qt-pill off"
        sw = f'<span class="swatch" style="background:{swatch};"></span>' if swatch else ""
        return f'<span class="{cls}">{sw}{label}</span>'

    pills_html = "".join([
        pill(True, "Candles", "#16A34A"),
        pill(show_ma20, "MA 20", "#F59E0B"),
        pill(show_ma50, "MA 50", "#2563EB"),
        pill(show_vwap, "VWAP", "#C026D3"),
        pill(show_prevc, "Prev Close", "rgba(100,116,139,.6)"),
        pill(show_volume, "Volume", "#94A3B8"),
        pill(show_rsi, "RSI 14", "#7C3AED"),
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

    try:
        renderLightweightCharts(charts_to_render, key="quant_charts")
    except Exception:
        renderLightweightCharts(charts_to_render)
