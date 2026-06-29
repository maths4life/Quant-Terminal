import streamlit as st

def render_navbar(
    market_open,
    market_status,
    icon_search,
    icon_clock,
    icon_bell,
    icon_gear,
):
    st.markdown(
        """
        <div style="background:red;padding:20px;color:white">
            <h1>Navbar Works!</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )