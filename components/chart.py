import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from utils.helpers import render_html


def base_opts(show_time=True):
    """Hallmark v2.0.0 instrument configuration for Lightweight Charts.
    - Neutral graphite surface: #141519
    - Hairline border: #23252b
    - Untracked secondary text: #9ca3af
    - Geist Mono typography for numeric axis labels
    """
    return {
        "layout": {
            "background": {"type": "solid", "color": "#141519"},
            "textColor": "#9ca3af",
            "fontSize": 11,
            "fontFamily": "'Geist Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(255, 255, 255, 0.025)"},
            "horzLines": {"color": "rgba(255, 255, 255, 0.025)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(59, 130, 246, 0.4)", "labelBackgroundColor": "#2563eb"},
            "horzLine": {"color": "rgba(59, 130, 246, 0.4)", "labelBackgroundColor": "#2563eb"},
        },
        "rightPriceScale": {
            "borderColor": "#23252b",
            "textColor": "#9ca3af",
            "autoScale": True,
            "minValue": 0,
        },
        "timeScale": {
            "borderColor": "#23252b",
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
            "upColor": "#16a34a", "downColor": "#dc2626",
            "borderVisible": False,
            "wickUpColor": "#16a34a", "wickDownColor": "#dc2626",
        }
    }]

    if show_ma20 and last_ma20:
        ma20d = df[["time", "MA20"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
            "options": {"color": "#ca8a04", "lineWidth": 1.5}
        })

    if show_ma50 and last_ma50:
        ma50d = df[["time", "MA50"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
            "options": {"color": "#2563eb", "lineWidth": 1.5}
        })

    if show_vwap and last_vwap:
        vwapd = df[["time", "VWAP"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
            "options": {"color": "#9333ea", "lineWidth": 1.5}
        })

    if show_prevc and prev_close == prev_close:
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": prev_close} for r in candles],
            "options": {"color": "rgba(156, 163, 175, 0.4)", "lineWidth": 1, "lineStyle": 2}
        })

    price_opts = base_opts(show_time=not (show_volume or show_rsi))
    price_opts["watermark"] = {
        "visible": True, "fontSize": 56,
        "horzAlign": "center", "vertAlign": "center",
        "color": "rgba(255, 255, 255, 0.02)", "text": ticker,
    }

    charts_to_render = [{"chart": price_opts, "series": price_series}]

    if show_volume and "Volume" in df.columns:
        vol_src = df[["time", "Open", "Close", "Volume"]].dropna()
        vol_data = []
        for _, row in vol_src.iterrows():
            c = "#16a34a" if float(row["Close"]) >= float(row["Open"]) else "#dc2626"
            vol_data.append({"time": row["time"], "value": float(row["Volume"]), "color": c + "55"})
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
                {"type": "Line", "data": rsi_data, "options": {"color": "#3b82f6", "lineWidth": 1.5}},
                {"type": "Line", "data": ob_line, "options": {"color": "rgba(220, 38, 38, 0.35)", "lineWidth": 1, "lineStyle": 2}},
                {"type": "Line", "data": os_line, "options": {"color": "rgba(22, 163, 74, 0.35)", "lineWidth": 1, "lineStyle": 2}},
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
        cls = "hm-pill on" if on else "hm-pill off"
        sw = f'<span class="hm-swatch" style="background:{swatch};"></span>' if swatch else ""
        return f'<span class="{cls}">{sw}{label}</span>'

    pills_html = "".join([
        pill(True, "Candles", "#16a34a"),
        pill(show_ma20, "20-day MA", "#ca8a04"),
        pill(show_ma50, "50-day MA", "#2563eb"),
        pill(show_vwap, "VWAP", "#9333ea"),
        pill(show_prevc, "Previous close", "#9ca3af"),
        pill(show_volume, "Volume", "#6b7280"),
        pill(show_rsi, "RSI 14", "#3b82f6"),
    ])

    tools_html = "".join([
        f'<button type="button" class="hm-tool-btn" title="Draw tools" aria-label="Draw tools">{ICON_TOOL}</button>',
        f'<button type="button" class="hm-tool-btn" title="Compare" aria-label="Compare">{ICON_MARKET}</button>',
        f'<button type="button" class="hm-tool-btn" title="Indicators" aria-label="Indicators">{ICON_LAYERS}</button>',
        f'<button type="button" class="hm-tool-btn" title="Refresh" aria-label="Refresh">{ICON_REFRESH}</button>',
    ])

    render_html(f"""
    <div class="hm-chart-frame">
        <div class="hm-chart-header">
            <div class="hm-pill-cluster">{pills_html}</div>
            <div class="hm-tool-cluster">{tools_html}</div>
        </div>
    </div>
    """)

    try:
        renderLightweightCharts(charts_to_render, key="quant_charts")
    except Exception:
        renderLightweightCharts(charts_to_render)
