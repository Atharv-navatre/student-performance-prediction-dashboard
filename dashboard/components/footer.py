import streamlit as st


def render_footer() -> None:
    """Render the shared footer across all dashboard pages."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """<div style='
  border-top:1px solid rgba(255,255,255,0.08);
  padding:20px 0;margin-top:20px;
  display:flex;justify-content:space-between;
  align-items:center;flex-wrap:wrap;gap:12px'>
  <div style='font-size:0.80rem;
  color:rgba(255,255,255,0.30)'>
  📊 SPP Dashboard &nbsp;·&nbsp;
  Student Performance Prediction System
  </div>
  <div style='font-size:0.78rem;
  color:rgba(255,255,255,0.25)'>
  XGBoost Model &nbsp;·&nbsp;
  MAE: 1.68 &nbsp;·&nbsp;
  6,607 Students &nbsp;·&nbsp;
  Supabase + Flask + Streamlit
  </div></div>""",
        unsafe_allow_html=True,
    )
