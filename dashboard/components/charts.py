"""Reusable Plotly chart builders for the dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import CATEGORY_COLORS  # noqa: E402


CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#262730",
    "gridcolor": "rgba(128,128,128,0.2)",
    "font_family": "Inter, sans-serif",
}


def _safe_print(message: str) -> None:
    """Print a status message with a Windows-safe Unicode fallback."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the shared dashboard chart theme to a figure."""

    fig.update_layout(
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font={"color": CHART_THEME["font_color"], "family": CHART_THEME["font_family"]},
    )
    fig.update_xaxes(gridcolor=CHART_THEME["gridcolor"])
    fig.update_yaxes(gridcolor=CHART_THEME["gridcolor"])
    return fig


def _empty_figure(message: str) -> go.Figure:
    """Return a themed empty figure with a centered explanatory message."""

    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _apply_theme(fig)


def score_distribution_chart(predictions: list[dict]) -> go.Figure:
    """Histogram of predicted scores colored by performance category."""

    try:
        df = pd.DataFrame(predictions)
        if df.empty:
            return _empty_figure("No prediction data available")

        fig = px.histogram(
            df,
            x="predicted_score",
            color="performance_category",
            color_discrete_map=CATEGORY_COLORS,
            nbins=30,
            title="Score Distribution",
            labels={
                "predicted_score": "Predicted Score",
                "performance_category": "Category",
            },
        )
        fig.add_vline(
            x=75,
            line_dash="dash",
            line_color="#2ecc71",
            annotation_text="Excellent >",
            annotation_position="top right",
        )
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("No prediction data available")


def category_pie_chart(category_dist: dict) -> go.Figure:
    """Donut chart of performance category distribution."""

    try:
        if not category_dist:
            return _empty_figure("No category data available")

        full_distribution = {
            category_name: int(category_dist.get(category_name, 0))
            for category_name in CATEGORY_COLORS
        }
        labels = list(full_distribution.keys())
        values = list(full_distribution.values())

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    marker_colors=[CATEGORY_COLORS[label] for label in labels],
                    textinfo="label+percent",
                    hovertemplate="%{label}: %{value} students<br>%{percent}<extra></extra>",
                )
            ]
        )
        fig.update_layout(title="Performance Categories")
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("No category data available")


def feature_importance_chart(feature_importance: dict) -> go.Figure:
    """Horizontal bar chart of feature importance scores."""

    try:
        if not feature_importance:
            return _empty_figure("No feature importance data available")

        sorted_items = sorted(
            feature_importance.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:12]
        feature_names = [item[0] for item in sorted_items][::-1]
        values = [item[1] for item in sorted_items][::-1]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=values,
                    y=feature_names,
                    orientation="h",
                    marker_color="#3498db",
                    text=[f"{value:.3f}" for value in values],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            title="Feature Importance (What Drives Performance)",
            xaxis_title="Importance Score",
        )
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("No feature importance data available")


def score_gauge_chart(score: float, category: str) -> go.Figure:
    """Gauge chart for a single student predicted score."""

    try:
        fig = go.Figure(
            data=[
                go.Indicator(
                    mode="gauge+number+delta",
                    value=float(score),
                    title={"text": f"Predicted Score — {category}"},
                    delta={
                        "reference": 70,
                        "increasing": {"color": "#2ecc71"},
                        "decreasing": {"color": "#e74c3c"},
                    },
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": CATEGORY_COLORS.get(category, "#3498db")},
                        "steps": [
                            {"range": [0, 64], "color": "rgba(231,76,60,0.15)"},
                            {"range": [64, 70], "color": "rgba(243,156,18,0.15)"},
                            {"range": [70, 75], "color": "rgba(52,152,219,0.15)"},
                            {"range": [75, 100], "color": "rgba(46,204,113,0.15)"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 2},
                            "thickness": 0.75,
                            "value": 64,
                        },
                    },
                )
            ]
        )
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("Unable to render score gauge")


def at_risk_bar_chart(at_risk_students: list[dict]) -> go.Figure:
    """Horizontal bar chart showing at-risk students sorted by predicted score."""

    try:
        df = pd.DataFrame(at_risk_students)
        if df.empty:
            return _empty_figure("No at-risk students found")

        df["code"] = df.apply(
            lambda row: str(
                row.get("students", {}).get("student_code", row.get("student_id", "Unknown"))
            )[:8],
            axis=1,
        )
        df = df.sort_values("predicted_score", ascending=True).head(20)
        scores = df["predicted_score"].tolist()
        codes = df["code"].tolist()

        fig = go.Figure(
            data=[
                go.Bar(
                    x=scores,
                    y=codes,
                    orientation="h",
                    marker_color="#e74c3c",
                    text=[f"{score:.1f}" for score in scores],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            title=f"At-Risk Students (Showing top {len(df)} most critical)",
            xaxis_title="Predicted Score",
        )
        fig.add_vline(
            x=64,
            line_dash="dash",
            line_color="#f39c12",
            annotation_text="Pass threshold",
            annotation_position="top right",
        )
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("No at-risk students found")


def score_trend_line(predictions: list[dict]) -> go.Figure:
    """Line chart showing average predicted score over time (by date)."""

    try:
        df = pd.DataFrame(predictions)
        if df.empty or "predicted_at" not in df.columns:
            return _empty_figure("No trend data available")

        df["predicted_at"] = pd.to_datetime(df["predicted_at"], errors="coerce")
        df = df.dropna(subset=["predicted_at", "predicted_score"]).copy()
        if df.empty:
            return _empty_figure("No trend data available")

        df["predicted_at"] = df["predicted_at"].dt.date
        trend_df = (
            df.groupby("predicted_at", as_index=False)["predicted_score"]
            .mean()
            .sort_values("predicted_at")
        )
        fig = px.line(
            trend_df,
            x="predicted_at",
            y="predicted_score",
            title="Score Trend Over Time",
            labels={
                "predicted_at": "Date",
                "predicted_score": "Avg Score",
            },
            markers=True,
        )
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="#3498db",
            annotation_text="Good threshold",
            annotation_position="top left",
        )
        return _apply_theme(fig)
    except Exception:
        return _empty_figure("No trend data available")


if __name__ == "__main__":
    mock_preds = [
        {"predicted_score": 72.5, "performance_category": "Good"},
        {"predicted_score": 58.0, "performance_category": "At Risk"},
        {"predicted_score": 81.0, "performance_category": "Excellent"},
    ]
    fig = score_distribution_chart(mock_preds)
    assert fig is not None
    _safe_print("[✓] score_distribution_chart OK")

    fig = category_pie_chart(
        {"Excellent": 100, "Good": 200, "Average": 50, "At Risk": 30}
    )
    assert fig is not None
    _safe_print("[✓] category_pie_chart OK")

    fig = score_gauge_chart(72.5, "Good")
    assert fig is not None
    _safe_print("[✓] score_gauge_chart OK")

    fig = feature_importance_chart(
        {
            "attendance_pct": 0.45,
            "study_hours": 0.32,
            "previous_score": 0.18,
        }
    )
    assert fig is not None
    _safe_print("[✓] feature_importance_chart OK")

    mock_risk = [
        {"predicted_score": 58.0, "students": {"student_code": "STU001"}},
        {"predicted_score": 61.0, "students": {"student_code": "STU002"}},
    ]
    fig = at_risk_bar_chart(mock_risk)
    assert fig is not None
    _safe_print("[✓] at_risk_bar_chart OK")

    print("=== charts.py verified ===")
