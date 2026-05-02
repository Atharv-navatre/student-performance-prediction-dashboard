"""Reusable Streamlit card components for the dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import CATEGORY_COLORS  # noqa: E402


def metric_card(
    label: str,
    value: str | int | float,
    delta: str | None = None,
    color: str = "#3498db",
) -> None:
    """Render a styled metric card using st.metric with optional delta."""

    _ = color
    st.metric(label=label, value=value, delta=delta)


def category_badge(category: str) -> None:
    """Render a colored badge for a performance category using st.markdown."""

    color = CATEGORY_COLORS.get(category, "#888888")
    st.markdown(
        f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 14px;
            display: inline-block;
        ">{category}</span>
        """,
        unsafe_allow_html=True,
    )


def prediction_result_card(prediction: dict) -> None:
    """Render a full prediction result card with score, category, at-risk status and model info."""

    score = prediction.get("predicted_score", 0)
    category = prediction.get("performance_category", "Unknown")
    is_at_risk = bool(prediction.get("is_at_risk", False))
    model_used = prediction.get("model_used", "Unknown")
    predicted_at = prediction.get("predicted_at", "Unknown")

    st.subheader("Prediction Result")
    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Predicted Score", score)
    with col2:
        st.metric("Category", category)
    with col3:
        st.metric("At Risk", "YES" if is_at_risk else "NO")

    if is_at_risk:
        st.error(
            "⚠ This student is at risk of underperforming. Immediate attention recommended."
        )
    elif category == "Excellent":
        st.success("This student is performing excellently. Keep up the good work!")
    elif category == "Good":
        st.info("This student is performing well. Minor improvements possible.")
    else:
        st.warning("This student needs academic support.")

    st.caption(f"Model: {model_used} | Predicted at: {predicted_at}")


def at_risk_student_card(student: dict) -> None:
    """Render a card for one at-risk student with their details."""

    student_info = student.get("students", {})
    code = student_info.get("student_code", "Unknown")
    score = float(student.get("predicted_score", 0) or 0)
    category = student.get("performance_category", "At Risk")

    with st.container():
        st.markdown(f"**{code}**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{score:.1f}")
        with col2:
            category_badge(category)
        st.divider()


def insight_card(insight: dict) -> None:
    """Render the latest insight summary card."""

    if not insight:
        st.info("No insights available yet.")
        return

    st.subheader("Latest Cohort Insights")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Students", insight.get("total_students", 0))
    with col2:
        st.metric("At Risk", insight.get("at_risk_count", 0))
    with col3:
        st.metric("At Risk %", f"{insight.get('at_risk_pct', 0)}%")
    with col4:
        st.metric("Avg Score", insight.get("avg_score", 0))

    st.markdown("### Top Risk Factors")
    for factor in insight.get("top_risk_factors", []):
        st.markdown(f"- {factor}")

    st.markdown("### Recommendations")
    for recommendation in insight.get("recommendations", []):
        st.info(recommendation)
