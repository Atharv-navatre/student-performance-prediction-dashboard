"""Model training, selection, prediction, and export utilities."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (  # noqa: E402
    EXPORTS_DIR,
    FEATURE_COLUMNS,
    MODEL_NAMES,
    MODELS_DIR,
    PERFORMANCE_CATEGORIES,
    TARGET_COLUMN,
    TARGET_MAE,
    TARGET_R2,
)


MODEL_REGISTRY = {
    "random_forest": RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_split=8,
        min_samples_leaf=4,
        max_features=0.6,
        random_state=42,
        n_jobs=1,
    ),
    "xgboost": XGBRegressor(
        n_estimators=500,
        learning_rate=0.02,
        max_depth=4,
        subsample=0.7,
        colsample_bytree=0.6,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.5,
        random_state=42,
        verbosity=0,
    ),
    "decision_tree": DecisionTreeRegressor(
        max_depth=6,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
    ),
}


def _safe_print(message: str) -> None:
    """Print messages safely when the console cannot encode Unicode symbols."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK").replace("→", "->").replace("²", "^2"))


class StudentPerformanceModel:
    """Train, evaluate, persist, and serve student performance models."""

    def __init__(self, model_name: str = "xgboost") -> None:
        """Initialize the model wrapper with a configured regressor."""

        if model_name not in MODEL_REGISTRY:
            available_models = list(MODEL_REGISTRY.keys())
            raise ValueError(f"Unknown model '{model_name}'. Choose from: {available_models}")

        self.model_name = model_name
        self.model = clone(MODEL_REGISTRY[model_name])
        self.is_trained = False
        self.metrics: dict[str, object] = {}
        self.feature_importance: dict[str, float] = {}
        self.feature_columns = FEATURE_COLUMNS
        self.model_version = ""

    def __repr__(self) -> str:
        """Return a compact representation of the model state."""

        r2_value = float(self.metrics.get("r2", 0.0))
        return (
            "StudentPerformanceModel("
            f"model={self.model_name}, "
            f"trained={self.is_trained}, "
            f"R2={r2_value:.4f})"
        )

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> dict[str, object]:
        """Train model and compute evaluation metrics."""

        _safe_print(f"[→] Training {self.model_name}...")
        try:
            self.model.fit(X_train, y_train)
        except PermissionError:
            if hasattr(self.model, "get_params") and "n_jobs" in self.model.get_params():
                self.model.set_params(n_jobs=1)
                print("    [!] Retrying with n_jobs=1 due to local process restrictions")
                self.model.fit(X_train, y_train)
            else:
                raise

        predictions = self.model.predict(X_test)
        predictions = np.clip(predictions, 0, 100)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        self.metrics = {
            "model": self.model_name,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "meets_r2_target": r2 >= TARGET_R2,
            "meets_mae_target": mae <= TARGET_MAE,
        }

        importances = getattr(self.model, "feature_importances_", np.zeros(len(self.feature_columns)))
        importance_pairs = zip(self.feature_columns, importances.tolist(), strict=False)
        self.feature_importance = dict(
            sorted(importance_pairs, key=lambda item: item[1], reverse=True)
        )

        self.is_trained = True
        self.model_version = (
            f"{self.model_name}_"
            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        _safe_print(f"[✓] {self.model_name} trained")
        print(f"    MAE  : {mae:.4f}")
        print(f"    RMSE : {rmse:.4f}")
        print(f"    R²   : {r2:.4f}")
        print(f"    R² target met  : {'Yes' if r2 >= TARGET_R2 else 'No'}")
        print(f"    MAE target met : {'Yes' if mae <= TARGET_MAE else 'No'}")
        return self.metrics

    def predict(self, student_data: dict[str, object]) -> dict[str, object]:
        """Predict score for one student. Input: dict of feature values. Output: prediction dict matching PREDICTION_JSON_KEYS."""

        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        available_features = {
            column_name: student_data[column_name]
            for column_name in self.feature_columns
            if column_name in student_data
        }
        ordered_row = {
            column_name: available_features.get(column_name, 0)
            for column_name in self.feature_columns
        }
        input_df = pd.DataFrame([ordered_row], columns=self.feature_columns)
        prediction = np.clip(self.model.predict(input_df), 0, 100)
        score = float(prediction[0])
        category = self._categorize(score)

        return {
            "predicted_score": round(score, 2),
            "performance_category": category,
            "is_at_risk": category == "At Risk",
            "input_features": student_data,
            "model_used": self.model_name,
            "predicted_at": datetime.datetime.now().isoformat(),
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict for all rows in a DataFrame. Adds predicted_score, performance_category, is_at_risk columns. Returns augmented DataFrame."""

        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        available_features = [column_name for column_name in self.feature_columns if column_name in df.columns]
        features_df = df.loc[:, available_features].copy()
        for column_name in self.feature_columns:
            if column_name not in features_df.columns:
                features_df[column_name] = 0
        features_df = features_df[self.feature_columns]

        predictions = np.clip(self.model.predict(features_df), 0, 100)
        result_df = df.copy()
        result_df["predicted_score"] = np.round(predictions, 2)
        result_df["performance_category"] = result_df["predicted_score"].apply(self._categorize)
        result_df["is_at_risk"] = result_df["performance_category"] == "At Risk"
        _safe_print(f"[✓] Batch predicted: {len(result_df)} students")
        return result_df

    def _categorize(self, score: float) -> str:
        """Map a numeric score to the configured performance category."""

        for category_name, (low, high) in PERFORMANCE_CATEGORIES.items():
            if low <= score <= high:
                return category_name
        return "At Risk"

    def save(self, filename: str | None = None) -> Path:
        """Save trained model to MODELS_DIR."""

        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        filename = filename or f"{self.model_version}.joblib"
        path = MODELS_DIR / filename
        joblib.dump(self.model, path)
        _safe_print(f"[✓] Model saved: {path}")
        return path

    def load(self, path: Path) -> None:
        """Load a saved model from path."""

        if not path.exists():
            raise FileNotFoundError(f"Model not found at {path}")

        self.model = joblib.load(path)
        self.is_trained = True

        path_parts = path.stem.split("_")
        inferred_name = (
            f"{path_parts[0]}_{path_parts[1]}"
            if len(path_parts) >= 2
            else path_parts[0]
        )
        self.model_name = inferred_name if inferred_name in MODEL_REGISTRY else path_parts[0]
        self.model_version = path.stem
        _safe_print(f"[✓] Model loaded: {path}")

    def export_prediction_json(
        self,
        result: dict[str, object],
        filename: str = "prediction.json",
    ) -> Path:
        """Export single prediction dict to EXPORTS_DIR as JSON."""

        path = EXPORTS_DIR / filename
        with path.open("w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=2, default=str)
        _safe_print(f"[✓] Prediction exported: {path}")
        return path


def train_all_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, dict[str, object]]:
    """Train all three models, return comparison dict with metrics for each."""

    results: dict[str, dict[str, object]] = {}

    for model_name in MODEL_NAMES:
        model = StudentPerformanceModel(model_name)
        results[model_name] = model.train(X_train, y_train, X_test, y_test)

    print("=== Model Comparison ===")
    print("Model            MAE     RMSE    R²      R² OK  MAE OK")
    for model_name in MODEL_NAMES:
        metrics = results[model_name]
        print(
            f"{model_name:<16} "
            f"{metrics['mae']:<7.4f} "
            f"{metrics['rmse']:<7.4f} "
            f"{metrics['r2']:<7.4f} "
            f"{'Yes' if metrics['meets_r2_target'] else 'No':<6} "
            f"{'Yes' if metrics['meets_mae_target'] else 'No'}"
        )
    print("========================")
    return results


def select_best_model(comparison: dict[str, dict[str, object]]) -> str:
    """Return name of model with highest R²."""

    best_name = max(comparison, key=lambda model_name: float(comparison[model_name]["r2"]))
    best_r2 = comparison[best_name]["r2"]
    _safe_print(f"[✓] Best model: {best_name} (R²={best_r2})")
    return best_name


if __name__ == "__main__":
    from ml.data_loader import load_processed
    from ml.preprocessor import StudentPreprocessor

    df = load_processed()
    prep = StudentPreprocessor()
    result = prep.run(df)

    X_train = result["X_train"]
    X_test = result["X_test"]
    y_train = result["y_train"]
    y_test = result["y_test"]

    comparison = train_all_models(X_train, y_train, X_test, y_test)
    best_name = select_best_model(comparison)

    best_model = StudentPerformanceModel(best_name)
    best_model.train(X_train, y_train, X_test, y_test)
    best_model.save()

    sample = {
        "attendance_pct": 84,
        "study_hours_per_day": 6,
        "previous_score": 72,
        "motivation_level": 2,
        "tutoring_sessions": 3,
        "sleep_hours": 7,
        "extracurricular_activities": 2,
        "internet_access": 1,
        "family_income_level": 1,
        "parental_education_level": 2,
        "teacher_quality": 2,
        "distance_from_home": 0,
    }
    prediction = best_model.predict(sample)
    best_model.export_prediction_json(prediction)

    print("=== Single Prediction Result ===")
    print(f"Predicted score    : {prediction['predicted_score']}")
    print(f"Performance category: {prediction['performance_category']}")
    print(f"Is at risk         : {prediction['is_at_risk']}")
    print(f"Model used         : {prediction['model_used']}")
    print("JSON exported to   : exports/prediction.json")
    print("================================")
    print("=== model.py verified ===")
