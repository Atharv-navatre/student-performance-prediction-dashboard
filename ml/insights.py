"""Rule-based insight generation for batch student predictions."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (  # noqa: E402
    CATEGORY_COLORS,
    EXPORTS_DIR,
    FEATURE_COLUMNS,
    PERFORMANCE_CATEGORIES,
    TARGET_COLUMN,
)


def _safe_print(message: str) -> None:
    """Print safely when the terminal cannot encode Unicode status symbols."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


def _get_priority_action(weak_features: list[str]) -> str:
    """Return the highest-priority action based on weak features."""

    priority_map = {
        "attendance_pct": "Improve attendance immediately — this is the top performance driver",
        "study_hours_per_day": "Increase daily study time by at least 1-2 hours",
        "motivation_level": "Work with counselor to address motivation and engagement",
        "tutoring_sessions": "Enroll in additional tutoring sessions",
        "sleep_hours": "Establish consistent sleep schedule of 7-8 hours",
        "internet_access": "Connect student with school internet access program",
    }

    for feature_name in weak_features:
        if feature_name in priority_map:
            return priority_map[feature_name]

    return "Schedule general academic review with advisor"


class InsightGenerator:
    """Generate batch insights and per-student recommendations from predictions."""

    def __init__(self) -> None:
        """Initialize the insight generator state."""

        self.insights: dict[str, object] = {}
        self.df: pd.DataFrame | None = None

    def __repr__(self) -> str:
        """Return a concise debug representation of the current insight state."""

        student_count = len(self.df) if self.df is not None else 0
        at_risk_count = int(self.df["is_at_risk"].sum()) if self.df is not None and "is_at_risk" in self.df else 0
        return f"InsightGenerator(students={student_count}, at_risk={at_risk_count})"

    def analyze_batch(self, df: pd.DataFrame) -> dict[str, object]:
        """Analyze a batch-predicted DataFrame and return structured insights dict matching INSIGHTS_JSON_KEYS schema."""

        self.df = df.copy()

        total = len(self.df)
        at_risk = int(self.df["is_at_risk"].sum()) if "is_at_risk" in self.df.columns else 0
        at_risk_pct = round((at_risk / total) * 100, 2) if total > 0 else 0.0
        avg_score = round(float(self.df["predicted_score"].mean()), 2) if total > 0 else 0.0

        category_distribution = {
            category_name: 0
            for category_name in CATEGORY_COLORS
        }
        if "performance_category" in self.df.columns:
            observed_counts = self.df["performance_category"].value_counts().to_dict()
            for category_name, count in observed_counts.items():
                category_distribution[category_name] = int(count)

        top_risk_factors: list[str] = []
        if "is_at_risk" in self.df.columns:
            at_risk_df = self.df[self.df["is_at_risk"] == True]
            safe_df = self.df[self.df["is_at_risk"] == False]

            if not at_risk_df.empty and not safe_df.empty:
                risk_diffs: list[tuple[str, float]] = []
                for feature_name in FEATURE_COLUMNS:
                    if feature_name in self.df.columns:
                        diff = safe_df[feature_name].mean() - at_risk_df[feature_name].mean()
                        if not np.isnan(diff):
                            risk_diffs.append((feature_name, float(diff)))

                risk_diffs.sort(key=lambda item: item[1], reverse=True)
                top_risk_factors = [feature_name for feature_name, _ in risk_diffs[:5]]

        recommendations = [
            "Monitor attendance closely — it is the strongest predictor of performance",
            "Encourage consistent daily study habits — study hours show strong correlation with scores",
        ]

        if at_risk_pct > 30:
            recommendations.append(
                "URGENT: Over 30% of students are at risk. Immediate intervention recommended."
            )

        if at_risk_pct > 10:
            recommendations.append(
                "Schedule one-on-one sessions with at-risk students this week."
            )

        if "tutoring_sessions" in top_risk_factors:
            recommendations.append(
                "Increase tutoring availability — at-risk students have significantly fewer tutoring sessions."
            )

        if "motivation_level" in top_risk_factors:
            recommendations.append(
                "Address student motivation through engagement activities and goal setting."
            )

        if "sleep_hours" in top_risk_factors:
            recommendations.append(
                "Educate students on sleep hygiene — sleep hours correlate with performance."
            )

        if "internet_access" in top_risk_factors:
            recommendations.append(
                "Provide internet access support for students lacking home connectivity."
            )

        self.insights = {
            "total_students": total,
            "at_risk_count": int(at_risk),
            "at_risk_pct": at_risk_pct,
            "avg_score": avg_score,
            "category_distribution": category_distribution,
            "top_risk_factors": top_risk_factors,
            "recommendations": recommendations,
            "generated_at": datetime.datetime.now().isoformat(),
        }

        top_factor = top_risk_factors[0] if top_risk_factors else "None"
        _safe_print(f"[✓] Insights generated for {total} students")
        print(f"    At risk      : {at_risk} ({at_risk_pct}%)")
        print(f"    Avg score    : {avg_score}")
        print(f"    Top factor   : {top_factor}")
        return self.insights

    def get_student_insight(
        self,
        student_row: dict[str, object],
        cohort_means: dict[str, float] | None = None,
    ) -> dict[str, object]:
        """Generate per-student insight comparing their features to cohort averages."""

        if cohort_means is None and self.df is not None:
            numeric_means = self.df.select_dtypes(include=[np.number]).mean(numeric_only=True)
            cohort_means = {column_name: float(value) for column_name, value in numeric_means.items()}

        cohort_means = cohort_means or {}
        weak_features: list[str] = []
        strong_features: list[str] = []

        for feature_name in FEATURE_COLUMNS:
            if feature_name in student_row and feature_name in cohort_means:
                student_val = student_row[feature_name]
                cohort_val = cohort_means[feature_name]

                if pd.isna(student_val) or pd.isna(cohort_val):
                    continue

                if student_val < cohort_val * 0.85:
                    weak_features.append(feature_name)
                elif student_val > cohort_val * 1.10:
                    strong_features.append(feature_name)

        return {
            "weak_features": weak_features[:3],
            "strong_features": strong_features[:3],
            "priority_action": _get_priority_action(weak_features),
        }

    def export_insights_json(self, filename: str = "insights.json") -> Path:
        """Export insights dict to EXPORTS_DIR."""

        if not self.insights:
            raise RuntimeError("No insights generated yet.\nCall analyze_batch() first.")

        path = EXPORTS_DIR / filename
        with path.open("w", encoding="utf-8") as json_file:
            json.dump(self.insights, json_file, indent=2, default=str)
        _safe_print(f"[✓] Insights exported: {path}")
        return path


if __name__ == "__main__":
    from config import MODELS_DIR
    from ml.data_loader import load_processed
    from ml.model import StudentPerformanceModel
    from ml.preprocessor import StudentPreprocessor

    df = load_processed()
    prep = StudentPreprocessor()
    result = prep.run(df)

    model_files = sorted(
        MODELS_DIR.glob("xgboost_*.joblib"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not model_files:
        raise FileNotFoundError(
            "No trained model found. Run ml/model.py first."
        )

    model = StudentPerformanceModel("xgboost")
    model.load(model_files[0])

    df_pred = model.predict_batch(df)

    ig = InsightGenerator()
    insights = ig.analyze_batch(df_pred)
    ig.export_insights_json()

    sample_row = df_pred.iloc[0].to_dict()
    student_insight = ig.get_student_insight(sample_row)

    print("=== Insights Summary ===")
    print(f"Total students     : {insights['total_students']}")
    print(f"At risk            : {insights['at_risk_count']} ({insights['at_risk_pct']}%)")
    print(f"Average score      : {insights['avg_score']}")
    print(f"Category breakdown : {insights['category_distribution']}")
    print(f"Top risk factors   : {insights['top_risk_factors']}")
    print(f"Recommendations    : {len(insights['recommendations'])} generated")
    print("========================")
    print("Sample student insight:")
    print(f"Weak features  : {student_insight['weak_features']}")
    print(f"Strong features: {student_insight['strong_features']}")
    print(f"Priority action: {student_insight['priority_action']}")
    print("========================")
    print("=== insights.py verified ===")
