import streamlit as st


def is_logged_in() -> bool:
    """Return True if a session access token is present."""
    return bool(st.session_state.get("access_token"))


def get_user_email() -> str:
    """Return the current user email or a default label."""
    return st.session_state.get("user_email", "User")


def logout() -> None:
    """Clear auth state and rerun the app."""
    for key in ("access_token", "user_email", "logged_in"):
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def render_auth_page() -> None:
    """Render the demo-only landing page for the dashboard."""
    st.markdown(
        """<style>
[data-testid="stAppViewContainer"]{
background:linear-gradient(135deg,
#0a0e1a 0%,#0f1117 50%,#1a0a2e 100%);}
[data-testid="stSidebar"]{display:none;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
[data-testid="stToolbar"]{visibility:hidden;}
@keyframes gradientShift{
0%{background-position:0% 50%}
50%{background-position:100% 50%}
100%{background-position:0% 50%}}
@keyframes fadeInUp{
from{opacity:0;transform:translateY(24px)}
to{opacity:1;transform:translateY(0)}}
@keyframes pulse{
0%,100%{transform:scale(1)}
50%{transform:scale(1.08)}}
.hero-title{
background:linear-gradient(135deg,
#4f8ef7,#a855f7,#00d4aa);
background-size:200% 200%;
animation:gradientShift 4s ease infinite;
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;
font-size:2.6rem;font-weight:800;
letter-spacing:-0.03em;
line-height:1.15;text-align:center;}
.stat-pill{
display:inline-flex;align-items:center;
gap:6px;
background:rgba(255,255,255,0.06);
border:1px solid rgba(255,255,255,0.10);
border-radius:20px;padding:5px 14px;
font-size:0.80rem;
color:rgba(255,255,255,0.65);margin:4px;}
.feature-card{
background:rgba(255,255,255,0.04);
border:1px solid rgba(255,255,255,0.08);
border-radius:14px;padding:18px 16px;
text-align:center;margin-bottom:8px;}
</style>""",
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.8, 1])

    with center:
        st.markdown(
            """<div style='text-align:center;
  padding:32px 0 16px'>
  <div style='font-size:4rem;
  animation:pulse 2s ease infinite;
  display:inline-block'>📊</div>
  </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """<div class='hero-title'>
  Student Performance<br>
  Prediction Dashboard</div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """<div style='text-align:center;
  color:rgba(255,255,255,0.45);
  font-size:0.95rem;margin:10px 0 20px'>
  AI-powered analytics and at-risk
  early detection system</div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """<div style='text-align:center;
  margin-bottom:28px'>
  <span class='stat-pill'>⚡ XGBoost Model</span>
  <span class='stat-pill'>👥 6,607 Students</span>
  <span class='stat-pill'>📈 MAE: 1.68</span>
  <span class='stat-pill'>🎯 R²: 0.504</span>
  </div>""",
            unsafe_allow_html=True,
        )

        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown(
                """<div class='feature-card'>
    <div style='font-size:1.6rem'>🎯</div>
    <div style='color:rgba(255,255,255,0.85);
    font-weight:600;font-size:0.88rem;
    margin-top:6px'>Predict</div>
    <div style='color:rgba(255,255,255,0.40);
    font-size:0.76rem;margin-top:4px'>
    Instant score prediction</div>
    </div>""",
                unsafe_allow_html=True,
            )
        with f2:
            st.markdown(
                """<div class='feature-card'>
    <div style='font-size:1.6rem'>⚠️</div>
    <div style='color:rgba(255,255,255,0.85);
    font-weight:600;font-size:0.88rem;
    margin-top:6px'>At-Risk</div>
    <div style='color:rgba(255,255,255,0.40);
    font-size:0.76rem;margin-top:4px'>
    Early detection alerts</div>
    </div>""",
                unsafe_allow_html=True,
            )
        with f3:
            st.markdown(
                """<div class='feature-card'>
    <div style='font-size:1.6rem'>🔬</div>
    <div style='color:rgba(255,255,255,0.85);
    font-weight:600;font-size:0.88rem;
    margin-top:6px'>Simulate</div>
    <div style='color:rgba(255,255,255,0.40);
    font-size:0.76rem;margin-top:4px'>
    What-if analysis</div>
    </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        demo_btn = st.button(
            "🚀  Enter Dashboard",
            use_container_width=True,
            type="primary",
        )

        if demo_btn:
            st.session_state["access_token"] = "demo"
            st.session_state["user_email"] = "demo@spp.ai"
            st.session_state["logged_in"] = True
            st.rerun()

        st.markdown(
            """<div style='text-align:center;
  margin-top:20px;font-size:0.72rem;
  color:rgba(255,255,255,0.22)'>
  Python · XGBoost · Streamlit · Supabase
  &nbsp;·&nbsp; 2026</div>""",
            unsafe_allow_html=True,
        )
