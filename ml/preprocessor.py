"""Preprocessing pipeline for student performance model training."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FEATURE_COLUMNS, MODELS_DIR, TARGET_COLUMN  # noqa: E402


CLIP_RANGES: dict[str, tuple[float, float]] = {
    "attendance_pct": (0, 100),
    "study_hours_per_day": (1, 12),
    "previous_score": (0, 100),
    "sleep_hours": (3, 10),
    "tutoring_sessions": (0, 10),
    "extracurricular_activities": (0, 7),
}


def _safe_print(message: str) -> None:
    """Print a message while tolerating limited console encodings."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


class StudentPreprocessor:
    """Clean, split, scale, and persist preprocessing artifacts."""

    def __init__(self) -> None:
        """Initialize the preprocessor state and scaling utilities."""

        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_columns = FEATURE_COLUMNS
        self.target_column = TARGET_COLUMN

    def __repr__(self) -> str:
        """Return a concise representation of the preprocessor state."""

        return (
            f"StudentPreprocessor(fitted={self.is_fitted}, "
            f"features={len(self.feature_columns)})"
        )

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove nulls and clip features to valid ranges."""

        cleaned_df = df.copy()
        cleaned_df = cleaned_df.dropna(subset=[self.target_column])

        for column_name, (lower_bound, upper_bound) in CLIP_RANGES.items():
            if column_name in cleaned_df.columns:
                cleaned_df[column_name] = cleaned_df[column_name].clip(lower_bound, upper_bound)

        numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
        for column_name in numeric_columns:
            median_value = cleaned_df[column_name].median()
            cleaned_df[column_name] = cleaned_df[column_name].fillna(median_value)

        _safe_print(f"[✓] Cleaned: {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns")
        return cleaned_df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features to improve model signal on compressed score distributions."""

        engineered_df = df.copy()

        if {"study_hours_per_day", "motivation_level"}.issubset(engineered_df.columns):
            engineered_df["study_x_motivation"] = (
                engineered_df["study_hours_per_day"] * (engineered_df["motivation_level"] + 1)
            )

        if {"previous_score", "attendance_pct"}.issubset(engineered_df.columns):
            engineered_df["academic_foundation"] = (
                engineered_df["previous_score"] * 0.6
                + engineered_df["attendance_pct"] * 0.4
            )

        if {
            "tutoring_sessions",
            "internet_access",
            "teacher_quality",
        }.issubset(engineered_df.columns):
            engineered_df["support_index"] = (
                engineered_df["tutoring_sessions"] * 0.4
                + engineered_df["internet_access"] * 2.0
                + engineered_df["teacher_quality"] * 1.5
            )

        _safe_print("[✓] Engineered 3 interaction features")
        return engineered_df

    def get_features_target(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Extract feature matrix X and target vector y."""

        available = [column_name for column_name in self.feature_columns if column_name in df]
        X = df[available].copy()
        y = df[self.target_column].copy()
        return X, y

    def split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split into train and test sets."""

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
        )
        _safe_print(f"[✓] Split: {len(X_train)} train, {len(X_test)} test")
        return X_train, X_test, y_train, y_test

    def fit_transform(self, X_train: pd.DataFrame) -> pd.DataFrame:
        """Fit scaler on training data and transform it."""

        scaled_array = self.scaler.fit_transform(X_train)
        self.is_fitted = True
        scaled_df = pd.DataFrame(scaled_array, columns=X_train.columns, index=X_train.index)
        _safe_print("[✓] Scaler fitted and training data transformed")
        return scaled_df

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data using fitted scaler."""

        if not self.is_fitted:
            raise RuntimeError("Preprocessor not fitted. Call fit_transform first.")

        scaled_array = self.scaler.transform(X)
        return pd.DataFrame(scaled_array, columns=X.columns, index=X.index)

    def save_scaler(self, filename: str = "scaler.joblib") -> Path:
        """Save fitted scaler to MODELS_DIR."""

        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted scaler.")

        path = MODELS_DIR / filename
        joblib.dump(self.scaler, path)
        _safe_print(f"[✓] Scaler saved: {path}")
        return path

    def load_scaler(self, filename: str = "scaler.joblib") -> None:
        """Load scaler from MODELS_DIR."""

        path = MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Scaler not found at {path}")

        self.scaler = joblib.load(path)
        self.is_fitted = True
        _safe_print(f"[✓] Scaler loaded: {path}")

    def run(self, df: pd.DataFrame, test_size: float = 0.2) -> dict[str, object]:
        """Full preprocessing pipeline. Returns dict with X_train, X_test, y_train, y_test keys."""

        cleaned_df = self.clean(df)
        engineered_df = self.engineer_features(cleaned_df)
        X, y = self.get_features_target(engineered_df)
        X_train, X_test, y_train, y_test = self.split(X, y, test_size=test_size)
        X_train_scaled = self.fit_transform(X_train)
        X_test_scaled = self.transform(X_test)
        self.save_scaler()

        return {
            "X_train": X_train_scaled,
            "X_test": X_test_scaled,
            "y_train": y_train,
            "y_test": y_test,
            "feature_columns": list(X_train.columns),
        }


if __name__ == "__main__":
    from ml.data_loader import load_processed

    df = load_processed()
    prep = StudentPreprocessor()
    result = prep.run(df)

    print("=== Preprocessor Summary ===")
    print(f"X_train shape : {result['X_train'].shape}")
    print(f"X_test shape  : {result['X_test'].shape}")
    print(f"y_train shape : {result['y_train'].shape}")
    print(f"y_test shape  : {result['y_test'].shape}")
    print(f"Features used : {result['feature_columns']}")
    print(f"Scaler type   : {prep.scaler.__class__.__name__}")
    print("============================")
    print("=== preprocessor.py verified ===")
