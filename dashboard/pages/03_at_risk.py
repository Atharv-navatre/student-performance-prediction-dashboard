import json
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import API_BASE_URL, CACHE_TTL
from dashboard.auth import is_logged_in
from dashboard.components.charts import at_risk_bar_chart
from dashboard.components.footer import render_footer

SHARED_CSS = """<style>
[data-testid="stAppViewContainer"]{
background:linear-gradient(135deg,
#0f1117 0%,#1a1f2e 50%,#0f1117 100%);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{
background:rgba(255,255,255,0.03)!important;
border-right:1px solid
rgba(255,255,255,0.08)!important;}
[data-testid="stSidebar"] *{
color:#e2e8f0!important;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
[data-testid="stToolbar"]{visibility:hidden;}
.metric-card{
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.10);
border-radius:16px;padding:20px 24px;
text-align:center;position:relative;
overflow:hidden;margin-bottom:12px;}
.metric-card::before{content:'';
position:absolute;top:0;left:0;right:0;
height:2px;background:linear-gradient(
90deg,#4f8ef7,#a855f7,#00d4aa);}
.metric-value{font-size:2rem;font-weight:700;
background:linear-gradient(135deg,
#4f8ef7,#a855f7);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;display:block;
margin:8px 0 4px;}
.metric-value-danger{font-size:2rem;
font-weight:700;background:linear-gradient(
135deg,#f7506e,#ff8c69);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;display:block;
margin:8px 0 4px;}
.metric-label{font-size:0.80rem;
color:rgba(255,255,255,0.50);
text-transform:uppercase;
letter-spacing:0.08em;font-weight:500;}
.section-header{font-size:1rem;
font-weight:600;color:rgba(255,255,255,0.80);
margin:20px 0 12px;padding-bottom:8px;
border-bottom:1px solid
rgba(255,255,255,0.08);}
.glass-card{background:rgba(255,255,255,0.04);
border:1px solid rgba(255,255,255,0.08);
border-radius:14px;padding:18px;}
.risk-item{padding:10px 12px;
margin-bottom:8px;
border-left:3px solid #f7a94f;
background:rgba(255,255,255,0.03);
border-radius:0 8px 8px 0;
color:rgba(255,255,255,0.82);
font-size:0.88rem;}
.stDataFrame{background:rgba(255,255,255,0.03)
!important;border-radius:12px!important;}
</style>"""


def render_sidebar() -> None:
    """Render the shared sidebar navigation for dashboard pages."""
    with st.sidebar:
        st.markdown(
            """<div style='padding:
8px 0 16px'><div style='font-size:1.2rem;
font-weight:700;color:#fff'>
📊 SPP Dashboard</div>
<div style='font-size:0.72rem;
color:rgba(255,255,255,0.40)'>
AI Performance Analytics</div></div>""",
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/01_predict.py", label="🎯 Predict Student")
        st.page_link("pages/02_dashboard.py", label="📈 Analytics Dashboard")
        st.page_link("pages/03_at_risk.py", label="⚠️ At-Risk Monitor")
        st.page_link("pages/04_what_if.py", label="🔬 What-If Simulator")
        st.markdown("---")
        st.markdown(
            """<div style=
'font-size:0.72rem;
color:rgba(255,255,255,0.30)'>
XGBoost · MAE 1.68 · R² 0.504
</div>""",
            unsafe_allow_html=True,
        )


st.set_page_config(
    page_title="At-Risk — SPP Dashboard",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
if not is_logged_in():
    st.switch_page("app.py")
render_sidebar()


@st.cache_data(ttl=CACHE_TTL)
def fetch_at_risk() -> list:
    """Fetch at-risk students from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/students/at-risk", timeout=10)
        return response.json().get("students", [])
    except Exception:
        return []


@st.cache_data(ttl=CACHE_TTL)
def fetch_insight() -> dict:
    """Fetch the latest insight payload from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/insights/latest", timeout=10)
        return response.json()
    except Exception:
        return {}


st.markdown(
    """<div style='padding:8px 0 20px'>
<h1 style='font-size:1.8rem;font-weight:700;
color:#fff;margin:0'>⚠️ At-Risk Monitor
</h1><p style='color:rgba(255,255,255,0.45);
margin:4px 0 0;font-size:0.92rem'>
Students requiring immediate academic intervention
</p></div>""",
    unsafe_allow_html=True,
)

at_risk = fetch_at_risk()


# Demo fallback when Supabase unavailable
if not at_risk:
    at_risk = [
        {"predicted_score": 58.2, "performance_category": "At Risk", 
         "is_at_risk": True, "students": {"student_code": "STU00042",
         "attendance_pct": 45, "study_hours_per_day": 2, "previous_score": 52}},
        {"predicted_score": 61.5, "performance_category": "At Risk",
         "is_at_risk": True, "students": {"student_code": "STU00138",
         "attendance_pct": 52, "study_hours_per_day": 3, "previous_score": 58}},
        {"predicted_score": 63.1, "performance_category": "At Risk",
         "is_at_risk": True, "students": {"student_code": "STU00271",
         "attendance_pct": 48, "study_hours_per_day": 2, "previous_score": 61}},
        {"predicted_score": 62.0, "performance_category": "At Risk",
         "is_at_risk": True, "students": {"student_code": "STU00389",
         "attendance_pct": 55, "study_hours_per_day": 3, "previous_score": 55}},
        {"predicted_score": 59.8, "performance_category": "At Risk",
         "is_at_risk": True, "students": {"student_code": "STU00512",
         "attendance_pct": 41, "study_hours_per_day": 2, "previous_score": 49}},
    ]
    st.info("📡 Showing demo at-risk data — live connection unavailable")

insight = fetch_insight()

avg_score = (
    round(sum(float(student.get("predicted_score", 0)) for student in at_risk) / max(len(at_risk), 1), 2)
    if at_risk
    else 0.0
)
priority = "HIGH" if len(at_risk) > 100 else "MEDIUM"

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Total At Risk</div>
<div class='metric-value-danger'>{len(at_risk)}</div>
</div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Avg Score (At Risk)</div>
<div class='metric-value'>{avg_score:.1f}</div>
</div>""",
        unsafe_allow_html=True,
    )
with col3:
    value_class = "metric-value-danger" if priority == "HIGH" else "metric-value"
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Intervention Priority</div>
<div class='{value_class}'>{priority}</div>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div class='section-header'>At-Risk Students by Score</div>",
    unsafe_allow_html=True,
)
fig = at_risk_bar_chart(at_risk)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0",
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='section-header'>At-Risk Student Details</div>",
    unsafe_allow_html=True,
)

if at_risk:
    display_df = pd.DataFrame(at_risk)
    display_df["Student"] = display_df.apply(
        lambda row: row.get("students", {}).get("student_code", "—")
        if isinstance(row.get("students"), dict)
        else "—",
        axis=1,
    )
    display_df["Score"] = display_df["predicted_score"]
    display_df["Category"] = display_df["performance_category"]
    display_df["At Risk"] = display_df["is_at_risk"]
    st.dataframe(
        display_df[["Student", "Score", "Category", "At Risk"]],
        use_container_width=True,
        height=350,
    )

    df_download = pd.DataFrame(at_risk)
    st.download_button(
        "⬇ Export At-Risk List (CSV)",
        data=df_download.to_csv(index=False),
        file_name="at_risk_students.csv",
        mime="text/csv",
        use_container_width=True,
    )

recs = insight.get("recommendations", [])
if recs:
    st.markdown(
        "<div class='section-header'>Intervention Recommendations</div>",
        unsafe_allow_html=True,
    )
    rec_html = "<div class='glass-card'>"
    for recommendation in recs:
        rec_html += f"<div class='risk-item'>{recommendation}</div>"
    rec_html += "</div>"
    st.markdown(rec_html, unsafe_allow_html=True)

_ = json.dumps({"count": len(at_risk)})

render_footer()
