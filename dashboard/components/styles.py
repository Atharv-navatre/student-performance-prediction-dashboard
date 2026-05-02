"""Shared Streamlit styling helpers for the dashboard."""

import streamlit as st


MAIN_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1rem;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    border-color: #3498db;
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(52, 152, 219, 0.08);
}
.stAlert {
    border-radius: 8px;
    background: transparent !important;
    border-left: 4px solid #ced4da;
    box-shadow: none !important;
}
div[data-baseweb="notification"] {
    background: rgba(255, 255, 255, 0.85) !important;
    border-left: 4px solid #ced4da !important;
    border-radius: 8px !important;
}
div[data-baseweb="notification"][kind="error"] {
    border-left-color: #e74c3c !important;
}
div[data-baseweb="notification"][kind="warning"] {
    border-left-color: #f39c12 !important;
}
div[data-baseweb="notification"][kind="success"] {
    border-left-color: #2ecc71 !important;
}
div[data-baseweb="notification"][kind="info"] {
    border-left-color: #3498db !important;
}
section[data-testid="stSidebar"] {
    width: 260px !important;
}
[data-testid="stExpander"] {
    border-radius: 10px !important;
    box-shadow: 0 8px 18px rgba(38, 39, 48, 0.06);
    overflow: hidden;
}
</style>
"""


def apply_styles() -> None:
    """Inject custom CSS into the Streamlit app."""

    st.markdown(MAIN_CSS, unsafe_allow_html=True)


def apply_page_config(
    page_title: str = "Student Performance",
    page_icon: str = "📊",
    layout: str = "wide",
) -> None:
    """Set Streamlit page config. Must be called first in every page file."""

    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )
