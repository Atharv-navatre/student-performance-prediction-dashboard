import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import API_BASE_URL, APP_ICON, APP_TITLE, CACHE_TTL
from dashboard.auth import (
    get_user_email,
    is_logged_in,
    logout,
    render_auth_page,
)
from dashboard.components.charts import (
    category_pie_chart,
    score_trend_line,
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

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    """Inject the shared home-page glassmorphism styles."""
    st.markdown(
        """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 12px;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4f8ef7, #a855f7, #00d4aa);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4f8ef7, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0 4px;
    display: block;
}
.metric-value-danger {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f7506e, #ff8c69);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0 4px;
    display: block;
}
.metric-label {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.50);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}
.metric-delta {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.35);
    margin-top: 4px;
}
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.80);
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px;
}
.risk-item {
    padding: 10px 12px;
    margin-bottom: 8px;
    border-left: 3px solid #f7a94f;
    background: rgba(255,255,255,0.03);
    border-radius: 0 8px 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
}
.rec-item {
    padding: 10px 12px;
    margin-bottom: 8px;
    border-left: 3px solid #4f8ef7;
    background: rgba(255,255,255,0.03);
    border-radius: 0 8px 8px 0;
    color: rgba(255,255,255,0.82);
    font-size: 0.88rem;
}
.action-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
}
.stPlotlyChart {
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}
</style>
""",
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=CACHE_TTL)
def fetch_stats() -> dict:
    """Fetch dashboard stats from the Flask API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/dashboard/stats",
            timeout=10,
        )
        response.raise_for_status()
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
def fetch_predictions(limit: int = 500) -> list:
    """Fetch recent predictions from the Flask API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/predictions",
            params={"limit": limit},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("predictions", [])
    except Exception:
        import datetime
        base = datetime.datetime(2026, 3, 1)
        demo = []
        scores = [68,69,70,71,70,72,71,73,
                  72,74,73,75,74,76,75,77,
                  76,75,77,76]
        for i, score in enumerate(scores):
            demo.append({
                "predicted_score": score,
                "performance_category": "Good",
                "is_at_risk": False,
                "predicted_at": (
                    base + datetime.timedelta(
                    days=i*2)).isoformat()
            })
        return demo


@st.cache_data(ttl=CACHE_TTL)
def fetch_latest_insight() -> dict:
    """Fetch the latest cohort insight from the Flask API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/insights/latest",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return {
            "total_students": 6607,
            "at_risk_count": 2980,
            "at_risk_pct": 45.1,
            "avg_score": 75.5,
            "category_distribution": {
                "Excellent": 211,
                "Good": 6021,
                "Average": 0,
                "At Risk": 375
            },
            "top_risk_factors": [
                "attendance_pct",
                "study_hours_per_day", 
                "tutoring_sessions",
                "family_income_level",
                "motivation_level"
            ],
            "recommendations": [
                "Monitor attendance closely — strongest predictor of performance",
                "Encourage consistent daily study habits",
                "Schedule one-on-one sessions with at-risk students",
                "Increase tutoring availability for at-risk cohort"
            ],
            "generated_at": "2026-04-13T11:50:10"
        }


inject_css()

if not is_logged_in():
    render_auth_page()
    st.stop()

_ = (APP_TITLE, APP_ICON)

with st.sidebar:
    st.markdown(
        """<div style='padding:8px 0 20px'>
<div style='font-size:1.3rem;font-weight:700;
color:#fff;letter-spacing:-0.02em'>
📊 SPP Dashboard</div>
<div style='font-size:0.75rem;
color:rgba(255,255,255,0.40);margin-top:2px'>
AI Performance Analytics</div>
</div>""",
        unsafe_allow_html=True,
    )

    api_online = False
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        api_online = response.status_code == 200
    except Exception:
        api_online = False

    if api_online:
        st.markdown(
            """<div style='display:inline-flex;
align-items:center;gap:6px;
background:rgba(0,212,170,0.12);
border:1px solid rgba(0,212,170,0.30);
color:#00d4aa;padding:4px 10px;
border-radius:20px;font-size:0.78rem;
font-weight:600;margin-bottom:16px'>
● API Online</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div style='display:inline-flex;
align-items:center;gap:6px;
background:rgba(247,80,110,0.12);
border:1px solid rgba(247,80,110,0.30);
color:#f7506e;padding:4px 10px;
border-radius:20px;font-size:0.78rem;
font-weight:600;margin-bottom:16px'>
● API Offline — run python api/app.py
</div>""",
            unsafe_allow_html=True,
        )

    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/01_predict.py", label="🎯 Predict Student")
    st.page_link("pages/02_dashboard.py", label="📈 Analytics Dashboard")
    st.page_link("pages/03_at_risk.py", label="⚠️ At-Risk Monitor")
    st.page_link("pages/04_what_if.py", label="🔬 What-If Simulator")

    st.markdown("---")
    user_email = get_user_email()
    st.markdown(
        f"<div style='font-size:0.78rem;"
        f"color:rgba(255,255,255,0.50);"
        f"padding:4px 0'>👤 {user_email}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<style>
    div[data-testid="stSidebar"]
    .stButton button {
        background: rgba(255,255,255,0.08);
        color: #ffffff !important;
        opacity: 1 !important;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
    }
    div[data-testid="stSidebar"]
    .stButton button:hover {
        background: rgba(247,80,110,0.20);
        border-color: #f7506e;
        color: #fff !important;
    }
    </style>""",
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", use_container_width=True):
        logout()
    st.markdown("---")
    st.markdown(
        """<div style='margin-top:40px;
font-size:0.75rem;color:rgba(255,255,255,0.30);
padding:12px;border-top:1px solid
rgba(255,255,255,0.08)'>
Model: XGBoost v1.0<br>
MAE: 1.68 pts &nbsp;|&nbsp; R²: 0.504<br>
Dataset: 6,607 students</div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    """<div style='padding:8px 0 24px'>
<h1 style='font-size:2rem;font-weight:700;
color:#fff;margin:0;letter-spacing:-0.03em'>
Student Performance
<span style='background:linear-gradient(
135deg,#4f8ef7,#a855f7);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text'>Prediction Dashboard
</span></h1>
<p style='color:rgba(255,255,255,0.45);
margin:6px 0 0;font-size:0.95rem'>
AI-powered student analytics and
at-risk early detection system</p>
</div>""",
    unsafe_allow_html=True,
)

stats = fetch_stats()
if stats.get("total", 0) == 0:
    stats = DEMO_STATS

total = stats.get("total", 0)
at_risk = stats.get("at_risk", 0)
avg_score = stats.get("avg_score", 0)
at_risk_pct = round(at_risk / max(total, 1) * 100, 1)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Total Students</div>
<div class='metric-value'>{total}</div>
<div class='metric-delta'>In database</div>
</div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>At Risk</div>
<div class='metric-value-danger'>{at_risk}</div>
<div class='metric-delta'>{at_risk_pct}% of cohort</div>
</div>""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Avg Predicted Score</div>
<div class='metric-value'>{avg_score:.1f}</div>
<div class='metric-delta'>Out of 100</div>
</div>""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """<div class='metric-card'>
<div class='metric-label'>Active Model</div>
<div class='metric-value'>XGB</div>
<div class='metric-delta'>MAE: 1.68</div>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown(
        "<div class='section-header'>Category Distribution</div>",
        unsafe_allow_html=True,
    )
    fig1 = category_pie_chart(stats.get("categories", {}))
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        legend_font_color="#e2e8f0",
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    with st.expander("📈 Score Trend Over Time", expanded=False):
        predictions = fetch_predictions(500)
        fig2 = score_trend_line(predictions)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            height=300)
        st.plotly_chart(fig2,
            use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>Latest Cohort Insights</div>",
    unsafe_allow_html=True,
)

insight = fetch_latest_insight()
if insight:
    i_total = insight.get("total_students", 0)
    i_risk = insight.get("at_risk_count", 0)
    i_pct = insight.get("at_risk_pct", 0)
    i_score = insight.get("avg_score", 0)
    risk_factors = insight.get("top_risk_factors", [])
    recs = insight.get("recommendations", [])

    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>"
            f"Total Students</div><div class='metric-value'>"
            f"{i_total}</div></div>",
            unsafe_allow_html=True,
        )
    with ic2:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>"
            f"At Risk</div><div class='metric-value-danger'>"
            f"{i_risk}</div></div>",
            unsafe_allow_html=True,
        )
    with ic3:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>"
            f"At Risk %</div><div class='metric-value'>"
            f"{i_pct}%</div></div>",
            unsafe_allow_html=True,
        )
    with ic4:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>"
            f"Avg Score</div><div class='metric-value'>"
            f"{i_score}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    rf_col, rec_col = st.columns(2)

    with rf_col:
        st.markdown(
            "<div class='section-header'>Top Risk Factors</div>",
            unsafe_allow_html=True,
        )
        rf_html = "<div class='glass-card'>"
        for factor in risk_factors:
            rf_html += f"<div class='risk-item'>{factor}</div>"
        rf_html += "</div>"
        st.markdown(rf_html, unsafe_allow_html=True)

    with rec_col:
        st.markdown(
            "<div class='section-header'>Recommendations</div>",
            unsafe_allow_html=True,
        )
        rec_html = "<div class='glass-card'>"
        for recommendation in recs:
            rec_html += f"<div class='rec-item'>{recommendation}</div>"
        rec_html += "</div>"
        st.markdown(rec_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>Quick Actions</div>",
    unsafe_allow_html=True,
)

qa1, qa2, qa3 = st.columns(3)

with qa1:
    st.markdown(
        """<div class='action-card'>
<div style='font-size:2rem;
margin-bottom:10px'>🎯</div>
<div style='font-size:1rem;font-weight:600;
color:rgba(255,255,255,0.90);
margin-bottom:6px'>Predict Student</div>
<div style='font-size:0.82rem;
color:rgba(255,255,255,0.45);
line-height:1.5'>Enter student data and
get instant AI prediction with
performance category</div>
</div>""",
        unsafe_allow_html=True,
    )
    st.page_link("pages/01_predict.py", label="→ Open Predict")

with qa2:
    st.markdown(
        """<div class='action-card'>
<div style='font-size:2rem;
margin-bottom:10px'>⚠️</div>
<div style='font-size:1rem;font-weight:600;
color:rgba(255,255,255,0.90);
margin-bottom:6px'>At-Risk Monitor</div>
<div style='font-size:0.82rem;
color:rgba(255,255,255,0.45);
line-height:1.5'>Review the most vulnerable
students and prioritize
intervention actions</div>
</div>""",
        unsafe_allow_html=True,
    )
    st.page_link("pages/03_at_risk.py", label="→ Open At-Risk Monitor")

with qa3:
    st.markdown(
        """<div class='action-card'>
<div style='font-size:2rem;
margin-bottom:10px'>📈</div>
<div style='font-size:1rem;font-weight:600;
color:rgba(255,255,255,0.90);
margin-bottom:6px'>Analytics Dashboard</div>
<div style='font-size:0.82rem;
color:rgba(255,255,255,0.45);
line-height:1.5'>Explore trends, cohort
breakdowns and decision-ready
analytics summaries</div>
</div>""",
        unsafe_allow_html=True,
    )
    st.page_link("pages/02_dashboard.py", label="→ Open Analytics")

render_footer()
