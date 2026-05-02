"""Central configuration for the Student Performance Prediction Dashboard."""

# SECTION 1 — IMPORTS
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


# SECTION 2 — BASE PATHS
BASE_DIR = Path(__file__).parent.resolve()
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPORTS_DIR = BASE_DIR / "exports"
MODELS_DIR = BASE_DIR / "ml" / "saved_models"

for directory_path in (
    BASE_DIR,
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    EXPORTS_DIR,
    MODELS_DIR,
):
    directory_path.mkdir(parents=True, exist_ok=True)


# SECTION 3 — DATA FILES
RAW_DATASET_PATH = DATA_RAW_DIR / "StudentPerformanceFactors.csv"
PROCESSED_DATASET_PATH = DATA_PROCESSED_DIR / "students_clean.csv"


# SECTION 4 — FEATURE COLUMNS
TARGET_COLUMN = "final_score"

FEATURE_COLUMNS = [
    "attendance_pct",
    "study_hours_per_day",
    "previous_score",
    "motivation_level",
    "tutoring_sessions",
    "sleep_hours",
    "extracurricular_activities",
    "internet_access",
    "family_income_level",
    "parental_education_level",
    "teacher_quality",
    "distance_from_home",
    "study_x_motivation",
    "academic_foundation",
    "support_index",
]


# SECTION 5 — KAGGLE COLUMN MAP
KAGGLE_COLUMN_MAP = {
    "Hours_Studied": "study_hours_per_day",
    "Attendance": "attendance_pct",
    "Sleep_Hours": "sleep_hours",
    "Previous_Scores": "previous_score",
    "Motivation_Level": "motivation_level",
    "Internet_Access": "internet_access",
    "Tutoring_Sessions": "tutoring_sessions",
    "Family_Income": "family_income_level",
    "Teacher_Quality": "teacher_quality",
    "School_Type": "school_type",
    "Peer_Influence": "peer_influence",
    "Physical_Activity": "extracurricular_activities",
    "Learning_Disabilities": "learning_disabilities",
    "Parental_Education_Level": "parental_education_level",
    "Distance_from_Home": "distance_from_home",
    "Gender": "gender",
    "Exam_Score": "final_score",
}


# SECTION 6 — CATEGORICAL ENCODING
CATEGORICAL_COLUMNS = {
    "motivation_level": {"Low": 0, "Medium": 1, "High": 2},
    "internet_access": {"No": 0, "Yes": 1},
    "family_income_level": {"Low": 0, "Medium": 1, "High": 2},
    "teacher_quality": {"Low": 0, "Medium": 1, "High": 2},
    "parental_education_level": {
        "None": 0,
        "High School": 1,
        "College": 2,
        "Postgraduate": 3,
    },
    "distance_from_home": {"Near": 0, "Moderate": 1, "Far": 2},
    "peer_influence": {"Negative": 0, "Neutral": 1, "Positive": 2},
    "school_type": {"Public": 0, "Private": 1},
    "gender": {"Male": 0, "Female": 1},
    "learning_disabilities": {"No": 0, "Yes": 1},
}


# SECTION 7 — PERFORMANCE CATEGORIES
PERFORMANCE_CATEGORIES = {
    "Excellent": (75, 100),
    "Good": (70, 74),
    "Average": (65, 69),
    "At Risk": (0, 64),
}

CATEGORY_COLORS = {
    "Excellent": "#2ecc71",
    "Good": "#3498db",
    "Average": "#f39c12",
    "At Risk": "#e74c3c",
}


# SECTION 8 — MODEL SETTINGS
MODEL_NAMES = ["random_forest", "xgboost", "decision_tree"]
TARGET_R2 = 0.50
TARGET_MAE = 2.0


# SECTION 9 — SUPABASE
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


# SECTION 10 — FLASK
FLASK_PORT = 5001
FLASK_HOST = "0.0.0.0"
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")


# SECTION 11 — JSON EXPORT SCHEMAS
PREDICTION_JSON_KEYS = {
    "predicted_score",
    "performance_category",
    "is_at_risk",
    "input_features",
    "model_used",
    "predicted_at",
}

INSIGHTS_JSON_KEYS = {
    "total_students",
    "at_risk_count",
    "at_risk_pct",
    "avg_score",
    "category_distribution",
    "top_risk_factors",
    "recommendations",
    "generated_at",
}


# SECTION 12 — STREAMLIT
STREAMLIT_PORT = 8501
APP_TITLE = "Student Performance Prediction Dashboard"
APP_ICON = "📊"
CACHE_TTL = 300


# SECTION 13 — SELF CHECK
if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_RAW_DIR: {DATA_RAW_DIR}")
    print(f"DATA_PROCESSED_DIR: {DATA_PROCESSED_DIR}")
    print(f"EXPORTS_DIR: {EXPORTS_DIR}")
    print(f"MODELS_DIR: {MODELS_DIR}")
    print(f"RAW_DATASET_PATH exists: {'Yes' if RAW_DATASET_PATH.exists() else 'No'}")
    print(f"FEATURE_COLUMNS count: {len(FEATURE_COLUMNS)}")
    print(f"KAGGLE_COLUMN_MAP count: {len(KAGGLE_COLUMN_MAP)}")
    print(f"CATEGORICAL_COLUMNS count: {len(CATEGORICAL_COLUMNS)}")
    print(
        "SUPABASE_URL set: "
        f"{'Yes' if SUPABASE_URL else 'No — add to .env'}"
    )
    print("=== config.py verified ===")
