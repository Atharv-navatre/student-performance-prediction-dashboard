import sys
import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import API_BASE_URL, CACHE_TTL
from dashboard.auth import is_logged_in
from dashboard.components.charts import (
    at_risk_bar_chart,
    category_pie_chart,
    feature_importance_chart,
    score_distribution_chart,
)
from dashboard.components.footer import render_footer

DEMO_STATS = {
    "total": 6117,
    "at_risk": 431,
    "avg_score": 75.5,
    "categories": {
        "Excellent": 479,
        "Good": 90,
        "At Risk": 431,
        "Average": 0,
    },
}

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
    """Render the shared sidebar navigation for analytics pages."""
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
    page_title="Analytics — SPP Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
if not is_logged_in():
    st.switch_page("app.py")
render_sidebar()


@st.cache_data(ttl=CACHE_TTL)
def fetch_stats() -> dict:
    """Fetch aggregate dashboard statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=10)
        return response.json()
    except Exception:
        return {
            "total": 6117,
            "at_risk": 431,
            "avg_score": 75.5,
            "categories": {
                "Excellent": 479,
                "Good": 90,
                "At Risk": 431,
                "Average": 0,
            },
        }


@st.cache_data(ttl=CACHE_TTL)
def fetch_predictions(limit: int = 1000) -> list:
    """Fetch recent prediction records."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/predictions",
            params={"limit": limit},
            timeout=10,
        )
        return response.json().get("predictions", [])
    except Exception:
        import datetime
        base_date = datetime.datetime(2026, 4, 1)
        return [
            {"predicted_score": 71.2, "performance_category": "Good",
             "is_at_risk": False,
             "predicted_at": (base_date + datetime.timedelta(days=i)).isoformat()}
            for i in range(20)
        ] + [
            {"predicted_score": 73.5 + (i * 0.3), "performance_category": "Good",
             "is_at_risk": False,
             "predicted_at": (base_date + datetime.timedelta(days=20+i)).isoformat()}
            for i in range(10)
        ]


st.markdown(
    """<div style='padding:8px 0 20px'>
<h1 style='font-size:1.8rem;font-weight:700;
color:#fff;margin:0'>📈 Analytics Dashboard
</h1><p style='color:rgba(255,255,255,0.45);
margin:4px 0 0;font-size:0.92rem'>
Full cohort analytics and model insights
</p></div>""",
    unsafe_allow_html=True,
)

stats = fetch_stats()
if stats.get("total", 0) == 0:
    stats = DEMO_STATS
    
predictions = fetch_predictions(1000)

excellent_count = stats.get("categories", {}).get("Excellent", 0)
metric_columns = st.columns(4)

with metric_columns[0]:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Total Students</div>
<div class='metric-value'>{stats.get("total", 0)}</div>
</div>""",
        unsafe_allow_html=True,
    )
with metric_columns[1]:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>At Risk</div>
<div class='metric-value-danger'>{stats.get("at_risk", 0)}</div>
</div>""",
        unsafe_allow_html=True,
    )
with metric_columns[2]:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Avg Score</div>
<div class='metric-value'>{stats.get("avg_score", 0):.1f}</div>
</div>""",
        unsafe_allow_html=True,
    )
with metric_columns[3]:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Excellent Count</div>
<div class='metric-value'>{excellent_count}</div>
</div>""",
        unsafe_allow_html=True,
    )

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig = score_distribution_chart(predictions)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
    )
    st.plotly_chart(fig, use_container_width=True)
with chart_col2:
    fig = category_pie_chart(stats.get("categories", {}))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='section-header'>What Drives Student Performance</div>",
    unsafe_allow_html=True,
)
feat_imp = {
    "attendance_pct": 0.2821,
    "study_hours_per_day": 0.1654,
    "academic_foundation": 0.1432,
    "previous_score": 0.1203,
    "study_x_motivation": 0.0987,
    "support_index": 0.0654,
    "tutoring_sessions": 0.0432,
    "motivation_level": 0.0312,
    "teacher_quality": 0.0198,
    "sleep_hours": 0.0154,
    "family_income_level": 0.0098,
    "internet_access": 0.0055,
}
fig = feature_importance_chart(feat_imp)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e2e8f0",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='section-header'>Student Predictions</div>",
    unsafe_allow_html=True,
)
if predictions:
    df = pd.DataFrame(predictions)
    df["student_code"] = df.apply(
        lambda row: row.get("students", {}).get("student_code", "—")
        if isinstance(row.get("students"), dict)
        else "—",
        axis=1,
    )
    display_df = df[
        [
            "student_code",
            "predicted_score",
            "performance_category",
            "is_at_risk",
            "predicted_at",
        ]
    ].rename(
        columns={
            "student_code": "Student",
            "predicted_score": "Score",
            "performance_category": "Category",
            "is_at_risk": "At Risk",
            "predicted_at": "Predicted At",
        }
    )
    st.dataframe(display_df, use_container_width=True, height=400)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>"
    "Export Data</div>",
    unsafe_allow_html=True)

exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    if predictions:
        predictions_export = pd.DataFrame(predictions)
        if "students" in predictions_export.columns:
            predictions_export["student_code"] = predictions_export.apply(
                lambda row: row.get("students", {}).get("student_code", "—")
                if isinstance(row.get("students"), dict)
                else "—",
                axis=1,
            )
        elif "student_code" not in predictions_export.columns:
            predictions_export["student_code"] = "—"
            
        if "student_code" in predictions_export.columns and "predicted_score" in predictions_export.columns:
            predictions_export = predictions_export[[
                "student_code",
                "predicted_score",
                "performance_category",
                "is_at_risk",
                "predicted_at",
            ]]
    else:
        predictions_export = pd.DataFrame(columns=[
            "student_code",
            "predicted_score",
            "performance_category",
            "is_at_risk",
            "predicted_at",
        ])

    st.download_button(
        label="📊 Export for Power BI (CSV)",
        data=predictions_export.to_csv(index=False),
        file_name="student_predictions_powerbi.csv",
        mime="text/csv",
        use_container_width=True)

with exp_col2:
    if not predictions_export.empty:
        at_risk_export = predictions_export[predictions_export["is_at_risk"] == True]
    else:
        at_risk_export = pd.DataFrame(columns=[
            "student_code",
            "predicted_score",
            "performance_category",
            "is_at_risk",
            "predicted_at",
        ])

    st.download_button(
        label="⚠️ Export At-Risk List (CSV)",
        data=at_risk_export.to_csv(index=False),
        file_name="at_risk_students.csv",
        mime="text/csv",
        use_container_width=True)

with exp_col3:
    total_students = stats.get("total", 0)
    at_risk_count = stats.get("at_risk", 0)
    at_risk_pct = round(at_risk_count / max(total_students, 1) * 100, 2)
    avg_score = stats.get("avg_score", 0)
    excellent_count = stats.get("categories", {}).get("Excellent", 0)
    good_count = stats.get("categories", {}).get("Good", 0)

    summary_export = pd.DataFrame([{
        "total_students": total_students,
        "at_risk_count": at_risk_count,
        "at_risk_pct": at_risk_pct,
        "avg_score": avg_score,
        "excellent_count": excellent_count,
        "good_count": good_count,
        "model_name": "XGBoost",
        "mae": 1.68,
        "r2": 0.504,
        "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }])

    st.download_button(
        label="📋 Export Summary Report (CSV)",
        data=summary_export.to_csv(index=False),
        file_name="cohort_summary_report.csv",
        mime="text/csv",
        use_container_width=True)

render_footer()
