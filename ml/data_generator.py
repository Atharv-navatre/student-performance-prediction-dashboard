"""Synthetic dataset generation for offline testing only."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (  # noqa: E402
    DATA_RAW_DIR,
    FEATURE_COLUMNS,
    PERFORMANCE_CATEGORIES,
    TARGET_COLUMN,
)

np.random.seed(42)


STUDENT_CODE_COLUMN = "student_code"
PERFORMANCE_CATEGORY_COLUMN = "performance_category"
(
    ATTENDANCE_COLUMN,
    STUDY_HOURS_COLUMN,
    PREVIOUS_SCORE_COLUMN,
    MOTIVATION_COLUMN,
    TUTORING_COLUMN,
    SLEEP_COLUMN,
    EXTRACURRICULAR_COLUMN,
    INTERNET_COLUMN,
    FAMILY_INCOME_COLUMN,
    PARENTAL_EDUCATION_COLUMN,
    TEACHER_QUALITY_COLUMN,
    DISTANCE_COLUMN,
) = FEATURE_COLUMNS


def _categorize(score: float) -> str:
    """Return the configured performance category for a score."""

    for category_name, (low, high) in PERFORMANCE_CATEGORIES.items():
        if low <= score <= high:
            return category_name
    return "At Risk"


def _print_status(message: str) -> None:
    """Print a status message with a safe fallback for limited Windows encodings."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


def generate_student_data(n: int = 1000) -> pd.DataFrame:
    """Generate n synthetic student records for offline testing only. Target is a weighted function of features so ML models can learn real patterns."""

    attendance = np.clip(np.random.normal(75, 15, n), 0, 100).round(2)
    study_hours = np.clip(np.random.normal(5, 2, n), 1, 12).round(0).astype(int)
    previous_score = np.clip(np.random.normal(65, 15, n), 0, 100).round(0).astype(int)
    motivation = np.random.randint(0, 3, n)
    tutoring_sessions = np.random.randint(0, 8, n)
    sleep_hours = np.clip(np.random.normal(6.5, 1.2, n), 3, 10).round(0).astype(int)
    extracurricular = np.random.randint(0, 6, n)
    internet_access = np.random.randint(0, 2, n)
    family_income = np.random.randint(0, 3, n)
    parental_education = np.random.randint(0, 4, n)
    teacher_quality = np.random.randint(0, 3, n)
    distance_from_home = np.random.randint(0, 3, n)

    final_score = (
        attendance * 0.18
        + study_hours * 3.20
        + previous_score * 0.28
        + motivation * 4.00
        + tutoring_sessions * 1.50
        + internet_access * 3.00
        + parental_education * 1.20
        + teacher_quality * 2.00
        + np.random.normal(0, 4, n)
    )
    final_score = (
        (final_score - final_score.min())
        / (final_score.max() - final_score.min())
        * 100
    )
    final_score = np.clip(final_score, 0, 100).round(2)

    feature_values = {
        ATTENDANCE_COLUMN: attendance,
        STUDY_HOURS_COLUMN: study_hours,
        PREVIOUS_SCORE_COLUMN: previous_score,
        MOTIVATION_COLUMN: motivation,
        TUTORING_COLUMN: tutoring_sessions,
        SLEEP_COLUMN: sleep_hours,
        EXTRACURRICULAR_COLUMN: extracurricular,
        INTERNET_COLUMN: internet_access,
        FAMILY_INCOME_COLUMN: family_income,
        PARENTAL_EDUCATION_COLUMN: parental_education,
        TEACHER_QUALITY_COLUMN: teacher_quality,
        DISTANCE_COLUMN: distance_from_home,
    }

    ordered_data: dict[str, object] = {
        STUDENT_CODE_COLUMN: [f"SYN{index:05d}" for index in range(1, n + 1)]
    }
    for column_name in FEATURE_COLUMNS:
        ordered_data[column_name] = feature_values[column_name]
    ordered_data[TARGET_COLUMN] = final_score

    df = pd.DataFrame(ordered_data)
    df[PERFORMANCE_CATEGORY_COLUMN] = df[TARGET_COLUMN].apply(_categorize)
    return df


def save_synthetic(
    df: pd.DataFrame,
    filename: str = "synthetic_students.csv",
) -> Path:
    """Save a synthetic dataset into the configured raw data directory."""

    output_path = DATA_RAW_DIR / filename
    df.to_csv(output_path, index=False)
    _print_status(f"[✓] Synthetic dataset saved: {output_path} ({len(df)} rows)")
    return output_path


if __name__ == "__main__":
    df = generate_student_data(1000)
    save_synthetic(df)

    print("=== Synthetic Dataset Summary ===")
    print(f"Rows       : {len(df)}")
    print(f"Columns    : {len(df.columns)}")
    print(f"Score range: {df[TARGET_COLUMN].min():.1f} – {df[TARGET_COLUMN].max():.1f}")
    print(f"Score mean : {df[TARGET_COLUMN].mean():.2f}")
    print()
    print("Category distribution:")
    print(df[PERFORMANCE_CATEGORY_COLUMN].value_counts().to_string())
    print("=== data_generator.py verified ===")
