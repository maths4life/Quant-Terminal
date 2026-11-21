import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from utils.helpers import render_html


def base_opts(show_time=True):
    """UI/UX Pro Max instrument configuration for Lightweight Charts.
    - Neutral Obsidian surface: #0B0F19
    - Hairline border: #1E293B
    - High-contrast secondary text: #94A3B8
    - JetBrains Mono typography for numeric axis labels
    """
    return {
        "layout": {
            "background": {"type": "solid", "color": "#0b0f19"},
            "textColor": "#94a3b8",
            "fontSize": 11,
            "fontFamily": "'JetBrains Mono', 'Fira Code', 'Geist Mono', monospace",
        },
        "grid": {
            "vertLines": {"color": "rgba(255, 255, 255, 0.03)"},
            "horzLines": {"color": "rgba(255, 255, 255, 0.03)"},
        },
        "crosshair": {
            "mode": 1,
            "vertLine": {"color": "rgba(59, 130, 246, 0.5)", "labelBackgroundColor": "#3b82f6"},
            "horzLine": {"color": "rgba(59, 130, 246, 0.5)", "labelBackgroundColor": "#3b82f6"},
        },
        "rightPriceScale": {
            "borderColor": "#1e293b",
            "textColor": "#94a3b8",
            "autoScale": True,
            "minValue": 0,
        },
        "timeScale": {
            "borderColor": "#1e293b",
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
            "upColor": "#22c55e", "downColor": "#ef4444",
            "borderVisible": False,
            "wickUpColor": "#22c55e", "wickDownColor": "#ef4444",
        }
    }]

    if show_ma20 and last_ma20:
        ma20d = df[["time", "MA20"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA20"])} for _, r in ma20d.iterrows()],
            "options": {"color": "#eab308", "lineWidth": 1.5}
        })

    if show_ma50 and last_ma50:
        ma50d = df[["time", "MA50"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["MA50"])} for _, r in ma50d.iterrows()],
            "options": {"color": "#3b82f6", "lineWidth": 1.5}
        })

    if show_vwap and last_vwap:
        vwapd = df[["time", "VWAP"]].dropna()
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": float(r["VWAP"])} for _, r in vwapd.iterrows()],
            "options": {"color": "#a855f7", "lineWidth": 1.5}
        })

    if show_prevc and prev_close == prev_close:
        price_series.append({
            "type": "Line",
            "data": [{"time": r["time"], "value": prev_close} for r in candles],
            "options": {"color": "rgba(148, 163, 184, 0.4)", "lineWidth": 1, "lineStyle": 2}
        })

    price_opts = base_opts(show_time=not (show_volume or show_rsi))
    price_opts["watermark"] = {
        "visible": True, "fontSize": 56,
        "horzAlign": "center", "vertAlign": "center",
        "color": "rgba(255, 255, 255, 0.025)", "text": ticker,
    }

    charts_to_render = [{"chart": price_opts, "series": price_series}]

    if show_volume and "Volume" in df.columns:
        vol_src = df[["time", "Open", "Close", "Volume"]].dropna()
        vol_data = []
        for _, row in vol_src.iterrows():
            c = "#22c55e" if float(row["Close"]) >= float(row["Open"]) else "#ef4444"
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
                {"type": "Line", "data": ob_line, "options": {"color": "rgba(239, 68, 68, 0.4)", "lineWidth": 1, "lineStyle": 2}},
                {"type": "Line", "data": os_line, "options": {"color": "rgba(34, 197, 94, 0.4)", "lineWidth": 1, "lineStyle": 2}},
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

    # ── TOOLBAR (PRO MAX) ────────────────────────────────────────────
    def pill(on, label, swatch=None):
        cls = "qt-chart-pill on" if on else "qt-chart-pill off"
        sw = f'<span class="qt-chart-swatch" style="background:{swatch};"></span>' if swatch else ""
        return f'<span class="{cls}">{sw}{label}</span>'

    pills_html = "".join([
        pill(True, "Candles", "#22c55e"),
        pill(show_ma20, "20D MA", "#eab308"),
        pill(show_ma50, "50D MA", "#3b82f6"),
        pill(show_vwap, "VWAP", "#a855f7"),
        pill(show_prevc, "Prev Close", "#94a3b8"),
        pill(show_volume, "Volume", "#64748b"),
        pill(show_rsi, "RSI (14)", "#3b82f6"),
    ])

    tools_html = "".join([
        f'<button type="button" class="qt-tool-btn" title="Drawing Tools" aria-label="Drawing Tools">{ICON_TOOL}</button>',
        f'<button type="button" class="qt-tool-btn" title="Compare Instrument" aria-label="Compare">{ICON_MARKET}</button>',
        f'<button type="button" class="qt-tool-btn" title="Indicators Overlay" aria-label="Indicators">{ICON_LAYERS}</button>',
        f'<button type="button" class="qt-tool-btn" title="Reset Chart Zoom" aria-label="Reset">{ICON_REFRESH}</button>',
    ])

    render_html(f"""
    <div class="qt-chart-frame">
        <div class="qt-chart-header">
            <div class="qt-pill-cluster">{pills_html}</div>
            <div class="qt-tool-cluster">{tools_html}</div>
        </div>
    </div>
    """)

    try:
        renderLightweightCharts(charts_to_render, key="quant_charts")
    except Exception:
        renderLightweightCharts(charts_to_render)
