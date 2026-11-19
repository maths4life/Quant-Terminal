import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from utils.helpers import render_html


def base_opts(show_time=True):
    """Institutional dark mode configuration for TradingView Lightweight Charts.
    Adheres strictly to the design system:
    - Surface/Primary #181818 background
    - Border/Primary #313131 scale borders
    - Text/Secondary #A1A1AA scale typography
    - Geist Mono typography for numeric axis labels
    """
    return {
        "layout": {
            "background": {"type": "solid", "color": "#181818"},
            "textColor": "#A1A1AA",
            "fontSize": 11,
            "fontFamily": "'Geist Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(255, 255, 255, 0.04)"},
            "horzLines": {"color": "rgba(255, 255, 255, 0.04)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(37, 99, 235, 0.5)", "labelBackgroundColor": "#2563EB"},
            "horzLine": {"color": "rgba(37, 99, 235, 0.5)", "labelBackgroundColor": "#2563EB"},
        },
        "rightPriceScale": {
            "borderColor": "#313131",
            "textColor": "#A1A1AA",
            "autoScale": True,
            "minValue": 0,
        },
        "timeScale": {
            "borderColor": "#313131",
            "timeVisible": show_time,
            "secondsVisible": False,
            "visible": show_time,
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
            "upColor": "#22C55E", "downColor": "#EF4444",
            "borderVisible": False,
            "wickUpColor": "#22C55E", "wickDownColor": "#EF4444",
        }
    }]

    if show_ma20 and last_ma20:
        ma20d = df[["time", "MA20"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
            "options": {"color": "#EAB308", "lineWidth": 2}
        })

    if show_ma50 and last_ma50:
        ma50d = df[["time", "MA50"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
            "options": {"color": "#3B82F6", "lineWidth": 2}
        })

    if show_vwap and last_vwap:
        vwapd = df[["time", "VWAP"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
            "options": {"color": "#A855F7", "lineWidth": 2}
        })

    if show_prevc and prev_close == prev_close:
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": prev_close} for r in candles],
            "options": {"color": "rgba(161, 161, 170, 0.5)", "lineWidth": 1, "lineStyle": 2}
        })

    price_opts = base_opts(show_time=not (show_volume or show_rsi))
    price_opts["watermark"] = {
        "visible": True, "fontSize": 64,
        "horzAlign": "center", "vertAlign": "center",
        "color": "rgba(255, 255, 255, 0.03)", "text": ticker,
    }

    charts_to_render = [{"chart": price_opts, "series": price_series}]

    if show_volume and "Volume" in df.columns:
        vol_src = df[["time", "Open", "Close", "Volume"]].dropna()
        vol_data = []
        for _, row in vol_src.iterrows():
            c = "#22C55E" if float(row["Close"]) >= float(row["Open"]) else "#EF4444"
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
                {"type": "Line", "data": rsi_data, "options": {"color": "#3B82F6", "lineWidth": 1.5}},
                {"type": "Line", "data": ob_line, "options": {"color": "rgba(239, 68, 68, 0.45)", "lineWidth": 1, "lineStyle": 2}},
                {"type": "Line", "data": os_line, "options": {"color": "rgba(34, 197, 94, 0.45)", "lineWidth": 1, "lineStyle": 2}},
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
        pill(True, "Candles", "#22C55E"),
        pill(show_ma20, "MA 20", "#EAB308"),
        pill(show_ma50, "MA 50", "#3B82F6"),
        pill(show_vwap, "VWAP", "#A855F7"),
        pill(show_prevc, "Prev Close", "rgba(161,161,170,.6)"),
        pill(show_volume, "Volume", "#71717A"),
        pill(show_rsi, "RSI 14", "#3B82F6"),
    ])

    tools_html = "".join([
        f'<div class="qt-tool" title="Draw tools">{ICON_TOOL}</div>',
        f'<div class="qt-tool" title="Market compare">{ICON_MARKET}</div>',
        f'<div class="qt-tool" title="Technical overlays">{ICON_LAYERS}</div>',
        f'<div class="qt-tool" title="Refresh feed">{ICON_REFRESH}</div>',
    ])

    render_html(f"""
    <div class="qt-chart-shell">
    <div class="qt-chart-toolbar">
        <div class="qt-toolbar-group">{pills_html}</div>
        <div class="qt-toolbar-group">{tools_html}</div>
    </div>
    </div>
    """)

    try:
        renderLightweightCharts(charts_to_render, key="quant_charts")
    except Exception:
        renderLightweightCharts(charts_to_render)
