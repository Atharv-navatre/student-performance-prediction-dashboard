import json
import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import API_BASE_URL, CACHE_TTL
from dashboard.auth import is_logged_in
from dashboard.components.charts import score_gauge_chart
from dashboard.components.footer import render_footer

st.set_page_config(
    page_title="Predict — SPP Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg,
    #0f1117 0%, #1a1f2e 50%, #0f1117 100%);
}
[data-testid="stHeader"] {
    background: transparent;}
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03)
    !important;
    border-right: 1px solid
    rgba(255,255,255,0.08) !important;}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {
    visibility: hidden;}
.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 24px;
    margin-top: 16px;}
.score-display {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(
    135deg, #4f8ef7, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;}
.score-display-danger {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(
    135deg, #f7506e, #ff8c69);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;}
.category-badge {
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
    padding: 8px 20px;
    border-radius: 20px;
    margin: 8px auto;
    display: inline-block;}
.form-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;}
label {color: rgba(255,255,255,0.75)
    !important;}
.stSlider > div > div {
    background: rgba(79,142,247,0.3);}
</style>""",
    unsafe_allow_html=True,
)

if not is_logged_in():
    st.switch_page("app.py")

_ = CACHE_TTL

with st.sidebar:
    st.markdown(
        """<div style='padding:8px 0 16px'>
<div style='font-size:1.2rem;font-weight:700;
color:#fff'>📊 SPP Dashboard</div>
<div style='font-size:0.75rem;
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
        """<div style='font-size:0.72rem;
color:rgba(255,255,255,0.30)'>
XGBoost · MAE 1.68 · R² 0.504</div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    """<div style='padding:8px 0 20px'>
<h1 style='font-size:1.8rem;font-weight:700;
color:#fff;margin:0'>
🎯 Predict Student Performance
</h1>
<p style='color:rgba(255,255,255,0.45);
margin:4px 0 0;font-size:0.92rem'>
Enter student details below to get an
instant AI-powered performance prediction
</p></div>""",
    unsafe_allow_html=True,
)

form_col, result_col = st.columns([55, 45])

with form_col:
    with st.form("predict_form"):
        st.markdown(
            """<div class='form-section'>
<div style='font-size:0.85rem;font-weight:600;
color:rgba(255,255,255,0.60);
text-transform:uppercase;
letter-spacing:0.08em;
margin-bottom:14px'>
Academic Indicators</div>""",
            unsafe_allow_html=True,
        )

        student_id = st.text_input(
            "Student ID / Roll No. (optional)",
            placeholder="e.g. STU001 or Roll No. 42"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            attendance = st.slider("Attendance %", min_value=0, max_value=100, value=75, step=1)
            study_hours = st.slider("Study Hours / Day", min_value=1, max_value=12, value=5, step=1)
            previous_score = st.slider("Previous Score", min_value=0, max_value=100, value=65, step=1)
        with col_b:
            tutoring = st.slider("Tutoring Sessions", min_value=0, max_value=10, value=2, step=1)
            sleep_hours = st.slider("Sleep Hours", min_value=3, max_value=10, value=7, step=1)
            extracurricular = st.slider(
                "Extracurricular Activities", min_value=0, max_value=7, value=2, step=1
            )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """<div class='form-section'
style='margin-top:12px'>
<div style='font-size:0.85rem;font-weight:600;
color:rgba(255,255,255,0.60);
text-transform:uppercase;
letter-spacing:0.08em;
margin-bottom:14px'>
Background Factors</div>""",
            unsafe_allow_html=True,
        )

        col_c, col_d = st.columns(2)
        with col_c:
            motivation = st.selectbox("Motivation Level", options=["Low", "Medium", "High"], index=1)
            internet = st.selectbox("Internet Access", options=["No", "Yes"], index=1)
            family_income = st.selectbox("Family Income Level", options=["Low", "Medium", "High"], index=1)
        with col_d:
            parent_edu = st.selectbox(
                "Parental Education",
                options=["None", "High School", "College", "Postgraduate"],
                index=1,
            )
            teacher_quality = st.selectbox("Teacher Quality", options=["Low", "Medium", "High"], index=1)
            distance = st.selectbox("Distance from Home", options=["Near", "Moderate", "Far"], index=0)

        st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🔮 Predict Performance",
            use_container_width=True,
            type="primary",
        )

motivation_map = {"Low": 0, "Medium": 1, "High": 2}
internet_map = {"No": 0, "Yes": 1}
income_map = {"Low": 0, "Medium": 1, "High": 2}
parent_map = {"None": 0, "High School": 1, "College": 2, "Postgraduate": 3}
teacher_map = {"Low": 0, "Medium": 1, "High": 2}
distance_map = {"Near": 0, "Moderate": 1, "Far": 2}

with result_col:
    if not submitted:
        st.markdown(
            """<div style='
    text-align:center;
    padding:60px 20px;
    color:rgba(255,255,255,0.25);'>
    <div style='font-size:4rem;
    margin-bottom:16px'>🎯</div>
    <div style='font-size:1rem;
    font-weight:500'>
    Fill in the form and click<br>
    Predict Performance</div>
    <div style='font-size:0.82rem;
    margin-top:8px;
    color:rgba(255,255,255,0.15)'>
    AI prediction in under 1 second
    </div></div>""",
            unsafe_allow_html=True,
        )
    else:
        payload = {
            "attendance_pct": attendance,
            "study_hours_per_day": study_hours,
            "previous_score": previous_score,
            "motivation_level": motivation_map[motivation],
            "tutoring_sessions": tutoring,
            "sleep_hours": sleep_hours,
            "extracurricular_activities": extracurricular,
            "internet_access": internet_map[internet],
            "family_income_level": income_map[family_income],
            "parental_education_level": parent_map[parent_edu],
            "teacher_quality": teacher_map[teacher_quality],
            "distance_from_home": distance_map[distance],
        }

        try:
            with st.spinner("Predicting..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/predict",
                    json=payload,
                    timeout=15,
                )
                response.raise_for_status()
                result = response.json()

            score = result["predicted_score"]
            category = result["performance_category"]
            at_risk = result["is_at_risk"]

            badge_colors = {
                "Excellent": "#00d4aa",
                "Good": "#4f8ef7",
                "Average": "#f7a94f",
                "At Risk": "#f7506e",
            }
            badge_color = badge_colors.get(category, "#888")
            score_class = "score-display-danger" if at_risk else "score-display"

            st.markdown(
                f"<div class='{score_class}'>{score:.1f}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;margin:8px 0'>"
                f"<span style='background:{badge_color}22;"
                f"border:1px solid {badge_color};"
                f"color:{badge_color};padding:6px 18px;"
                f"border-radius:20px;font-weight:600;"
                f"font-size:0.95rem'>{category}</span></div>",
                unsafe_allow_html=True,
            )

            fig = score_gauge_chart(score, category)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)

            if student_id.strip():
                result["student_id"] = student_id.strip()

            if at_risk or category == "Average":
                tips = [
                    "📚 Increase study hours by 1-2 hours daily — strongest impact",
                    "🏫 Improve attendance above 80% — top predictor of performance",
                    "👨‍🏫 Attend tutoring sessions — significant positive effect"
                ]
            elif category == "Good":
                tips = [
                    "⭐ Push attendance to 90%+ to reach Excellent tier",
                    "📖 Add 30 min focused review of previous weak topics",
                    "💤 Maintain 7-8 hours sleep for optimal retention"
                ]
            else:
                tips = [
                    "🎯 Maintain current study habits — performance is excellent",
                    "🤝 Consider peer tutoring to reinforce knowledge",
                    "📊 Track weekly progress to sustain momentum"
                ]

            tips_html = "<div style='margin-top:16px'>"
            tips_html += "<div style='font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.60);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px'>Improvement Tips</div>"
            for tip in tips:
                tips_html += f"<div style='padding:8px 12px;margin-bottom:6px;background:rgba(79,142,247,0.08);border-left:3px solid #4f8ef7;border-radius:0 8px 8px 0;color:rgba(255,255,255,0.80);font-size:0.85rem'>{tip}</div>"
            tips_html += "</div>"
            st.markdown(tips_html, unsafe_allow_html=True)

            if at_risk:
                st.error("⚠️ This student is at risk. Immediate academic support recommended.")
            elif category == "Excellent":
                st.success("Excellent performance predicted. Keep up the great work!")
            elif category == "Good":
                st.info("Good performance. Minor improvements can push to Excellent.")
            else:
                st.warning("Average performance. Academic support advised.")

            with st.expander("View Full Details"):
                st.json(result)

            st.download_button(
                label="⬇ Download Prediction JSON",
                data=json.dumps(result, indent=2),
                file_name=f"prediction_{score:.0f}.json",
                mime="application/json",
                use_container_width=True,
            )

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure Flask is running: python api/app.py")
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")

render_footer()
