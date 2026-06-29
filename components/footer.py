import streamlit as st
from datetime import datetime
import pytz


def render_footer():
    ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))

    st.markdown(
        f"""
<div class="qt-footer">
    <div>
        QUANT TERMINAL · v1.0 · Institutional Build
    </div>

    <div>
        Powered by Yahoo Finance · Updated {ist_now.strftime('%d %b %Y · %H:%M:%S')} IST
    </div>
</div>
""",
        unsafe_allow_html=True,
    )