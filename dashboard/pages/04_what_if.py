import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import API_BASE_URL
from dashboard.auth import is_logged_in
from dashboard.components.charts import score_gauge_chart
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
    """Render the shared sidebar navigation for simulator pages."""
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
    page_title="What-If — SPP Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)
if not is_logged_in():
    st.switch_page("app.py")
render_sidebar()


def call_predict(payload: dict) -> dict:
    """Call the prediction API and return a prediction payload or empty dict."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/predict",
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


st.markdown(
    """<div style='padding:8px 0 20px'>
<h1 style='font-size:1.8rem;font-weight:700;
color:#fff;margin:0'>🔬 What-If Simulator
</h1><p style='color:rgba(255,255,255,0.45);
margin:4px 0 0;font-size:0.92rem'>
Adjust student factors and see real-time score impact
</p></div>""",
    unsafe_allow_html=True,
)

motivation_map = {"Low": 0, "Medium": 1, "High": 2}
badge_colors = {
    "Excellent": "#00d4aa",
    "Good": "#4f8ef7",
    "Average": "#f7a94f",
    "At Risk": "#f7506e",
}

baseline_payload = {
    "attendance_pct": 75,
    "study_hours_per_day": 5,
    "previous_score": 65,
    "motivation_level": motivation_map["Medium"],
    "tutoring_sessions": 2,
    "sleep_hours": 7,
    "extracurricular_activities": 2,
    "internet_access": 1,
    "family_income_level": 1,
    "parental_education_level": 1,
    "teacher_quality": 1,
    "distance_from_home": 0,
}
baseline_result = call_predict(baseline_payload)
baseline_score = float(baseline_result.get("predicted_score", 0))
baseline_category = baseline_result.get("performance_category", "Average")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown(
        "<div class='section-header'>Baseline Student</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class='glass-card'>
<div style='color:rgba(255,255,255,0.80);line-height:1.8'>
Attendance: 75%<br>
Study Hours: 5/day<br>
Previous Score: 65<br>
Motivation: Medium<br>
Tutoring: 2 sessions<br>
Sleep: 7 hours
</div></div>""",
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        "<div class='section-header'>Adjusted Student</div>",
        unsafe_allow_html=True,
    )
    st.markdown("Move sliders to simulate improvements")

    attendance_adj = st.slider("Attendance %", 0, 100, 75)
    study_adj = st.slider("Study Hours/Day", 1, 12, 5)
    prev_adj = st.slider("Previous Score", 0, 100, 65)
    motivation_adj = st.select_slider(
        "Motivation",
        options=["Low", "Medium", "High"],
        value="Medium",
    )
    tutoring_adj = st.slider("Tutoring Sessions", 0, 10, 2)
    sleep_adj = st.slider("Sleep Hours", 3, 10, 7)

adjusted_payload = {
    "attendance_pct": attendance_adj,
    "study_hours_per_day": study_adj,
    "previous_score": prev_adj,
    "motivation_level": motivation_map[motivation_adj],
    "tutoring_sessions": tutoring_adj,
    "sleep_hours": sleep_adj,
    "extracurricular_activities": 2,
    "internet_access": 1,
    "family_income_level": 1,
    "parental_education_level": 1,
    "teacher_quality": 1,
    "distance_from_home": 0,
}
adjusted_result = call_predict(adjusted_payload)
adjusted_score = float(adjusted_result.get("predicted_score", 0))
adjusted_category = adjusted_result.get("performance_category", "Average")
delta = adjusted_score - baseline_score

score_col1, score_col2 = st.columns(2)
with score_col1:
    st.markdown(
        "<div class='section-header'>Baseline Score</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Baseline Score</div>
<div class='metric-value'>{baseline_score:.1f}</div>
<div style='color:{badge_colors.get(baseline_category, "#888")};font-weight:600'>{baseline_category}</div>
</div>""",
        unsafe_allow_html=True,
    )
with score_col2:
    st.markdown(
        "<div class='section-header'>Adjusted Score</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class='metric-card'>
<div class='metric-label'>Adjusted Score</div>
<div class='metric-value'>{adjusted_score:.1f}</div>
<div style='color:{badge_colors.get(adjusted_category, "#888")};font-weight:600'>{adjusted_category}</div>
</div>""",
        unsafe_allow_html=True,
    )

delta_color = "#00d4aa" if delta > 0 else "#f7506e" if delta < 0 else "#9ca3af"
delta_prefix = "+" if delta > 0 else ""
st.markdown(
    f"<div style='text-align:center;font-size:1.2rem;font-weight:700;color:{delta_color};margin:8px 0 16px'>{delta_prefix}{delta:.1f}</div>",
    unsafe_allow_html=True,
)

gauge_col1, gauge_col2 = st.columns(2)
with gauge_col1:
    fig = score_gauge_chart(baseline_score, baseline_category)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
    )
    st.plotly_chart(fig, use_container_width=True)
with gauge_col2:
    fig = score_gauge_chart(adjusted_score, adjusted_category)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
    )
    st.plotly_chart(fig, use_container_width=True)

changes = {
    "attendance": attendance_adj - 75,
    "study hours": study_adj - 5,
    "previous score": prev_adj - 65,
    "motivation": motivation_map[motivation_adj] - motivation_map["Medium"],
    "tutoring": tutoring_adj - 2,
    "sleep": sleep_adj - 7,
}
biggest_change = max(changes, key=lambda key: abs(changes[key]))

if delta > 3:
    st.success(
        f"Predicted performance improved meaningfully. Biggest contributing change: {biggest_change}."
    )
elif delta < -3:
    st.error("Adjustments decreased predicted performance")
else:
    st.info("Minor change in predicted performance")

changes_dict = {
    "Attendance": (attendance_adj, 75, "%"),
    "Study Hours": (study_adj, 5, "/day"),
    "Previous Score": (prev_adj, 65, " pts"),
    "Tutoring": (tutoring_adj, 2, " sessions"),
}
biggest_change_tup = max(changes_dict.items(),
    key=lambda x: abs(x[1][0] - x[1][1]))

name = biggest_change_tup[0]
new_val = biggest_change_tup[1][0]
base_val = biggest_change_tup[1][1]
unit = biggest_change_tup[1][2]
diff = new_val - base_val

st.markdown(
    f"<div style='background:rgba(79,142,247,0.08);"
    f"border:1px solid rgba(79,142,247,0.20);"
    f"border-radius:12px;padding:16px;"
    f"margin-top:12px;text-align:center'>"
    f"<div style='font-size:0.80rem;"
    f"color:rgba(255,255,255,0.50);"
    f"margin-bottom:6px'>"
    f"Biggest factor changed</div>"
    f"<div style='font-size:1.1rem;"
    f"font-weight:600;color:#4f8ef7'>"
    f"{name}: {base_val}{unit} → "
    f"{new_val}{unit} "
    f"({'+' if diff > 0 else ''}{diff}{unit})"
    f"</div></div>",
    unsafe_allow_html=True)

render_footer()
