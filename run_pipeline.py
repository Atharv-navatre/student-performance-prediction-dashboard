"""Master orchestrator for the student performance ML pipeline."""

from __future__ import annotations

import datetime
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import EXPORTS_DIR, MODELS_DIR, PROCESSED_DATASET_PATH
from ml.data_loader import DataLoader, load_processed
from ml.insights import InsightGenerator
from ml.model import StudentPerformanceModel, select_best_model, train_all_models
from ml.preprocessor import StudentPreprocessor


def run_pipeline(retrain: bool = True) -> dict[str, object]:
    """Run the full ML pipeline end to end. Returns a summary dict with all key results. If retrain=False, loads latest saved model instead of retraining."""

    pipeline_start = time.time()

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")

        print("============================================")
        print("STUDENT PERFORMANCE PREDICTION PIPELINE")
        print(f"Started: {datetime.datetime.now()}")
        print("============================================")

        print("[STAGE 1/5] Loading and cleaning data...")
        loader = DataLoader()
        loader.run()
        df = load_processed()
        total_students = len(df)
        feature_count = len(
            [
                column_name
                for column_name in df.columns
                if column_name not in {"student_code", "final_score"}
            ]
        )
        print(f"Data ready: {total_students} students, {feature_count} features")

        print("[STAGE 2/5] Preprocessing...")
        prep = StudentPreprocessor()
        prep_result = prep.run(df)
        X_train = prep_result["X_train"]
        X_test = prep_result["X_test"]
        y_train = prep_result["y_train"]
        y_test = prep_result["y_test"]
        used_features = prep_result["feature_columns"]
        print(f"Train: {len(X_train)} | Test: {len(X_test)} | Features: {len(used_features)}")

        print("[STAGE 3/5] Model training...")
        model: StudentPerformanceModel
        best_model_name = ""
        best_mae = 0.0
        best_r2 = 0.0

        if retrain:
            comparison = train_all_models(X_train, y_train, X_test, y_test)
            best_model_name = select_best_model(comparison)
            model = StudentPerformanceModel(best_model_name)
            metrics = model.train(X_train, y_train, X_test, y_test)
            model.save()
            best_mae = float(metrics["mae"])
            best_r2 = float(metrics["r2"])
            print(f"Best model: {best_model_name}")
            print(f"MAE: {best_mae} | R²: {best_r2}")
        else:
            model_files = sorted(
                MODELS_DIR.glob("xgboost_*.joblib"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if not model_files:
                print("[!] No saved xgboost model found. Retraining instead.")
                comparison = train_all_models(X_train, y_train, X_test, y_test)
                best_model_name = select_best_model(comparison)
                model = StudentPerformanceModel(best_model_name)
                metrics = model.train(X_train, y_train, X_test, y_test)
                model.save()
                best_mae = float(metrics["mae"])
                best_r2 = float(metrics["r2"])
                print(f"Best model: {best_model_name}")
                print(f"MAE: {best_mae} | R²: {best_r2}")
            else:
                latest_model_path = model_files[0]
                model = StudentPerformanceModel("xgboost")
                model.load(latest_model_path)
                best_model_name = model.model_name
                print(f"Loaded model: {latest_model_path.name}")

        print("[STAGE 4/5] Generating predictions and insights...")
        df_predicted = model.predict_batch(df)
        insight_generator = InsightGenerator()
        insights = insight_generator.analyze_batch(df_predicted)
        insight_generator.export_insights_json()
        print(f"Predictions: {len(df_predicted)} students")
        print(f"At risk: {insights['at_risk_count']} ({insights['at_risk_pct']}%)")
        print("Insights exported")

        print("[STAGE 5/5] Running sample prediction...")
        sample_student = {
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
        sample_prediction = model.predict(sample_student)
        model.export_prediction_json(sample_prediction)
        print(f"Sample score: {sample_prediction['predicted_score']}")
        print(f"Category: {sample_prediction['performance_category']}")
        print(f"At risk: {sample_prediction['is_at_risk']}")

        elapsed = time.time() - pipeline_start
        summary = {
            "status": "success",
            "total_students": total_students,
            "best_model": best_model_name,
            "mae": best_mae,
            "r2": best_r2,
            "at_risk_count": int(insights["at_risk_count"]),
            "at_risk_pct": float(insights["at_risk_pct"]),
            "sample_score": float(sample_prediction["predicted_score"]),
            "sample_category": str(sample_prediction["performance_category"]),
            "exports": {
                "prediction": str(EXPORTS_DIR / "prediction.json"),
                "insights": str(EXPORTS_DIR / "insights.json"),
            },
            "elapsed_seconds": round(elapsed, 2),
            "completed_at": datetime.datetime.now().isoformat(),
        }

        _ = json.dumps(summary, default=str)
        _ = PROCESSED_DATASET_PATH
        return summary
    except Exception as error:
        print(f"[ERROR] Pipeline failed: {error}")
        return {"status": "failed", "error": str(error)}


if __name__ == "__main__":
    summary = run_pipeline(retrain=True)

    print("============================================")
    print("PIPELINE COMPLETE")
    print("============================================")
    print(f"Status          : {summary.get('status')}")
    print(f"Total students  : {summary.get('total_students', 'N/A')}")
    print(f"Best model      : {summary.get('best_model', 'N/A')}")
    print(f"MAE             : {summary.get('mae', 'N/A')}")
    print(f"R²              : {summary.get('r2', 'N/A')}")
    if summary.get("status") == "success":
        print(
            f"At risk         : {summary.get('at_risk_count')} "
            f"({summary.get('at_risk_pct')}%)"
        )
        print(f"Sample score    : {summary.get('sample_score')}")
        print(f"Sample category : {summary.get('sample_category')}")
        print(f"Elapsed         : {summary.get('elapsed_seconds')}s")
        print("--------------------------------------------")
        print("Exports:")
        print(f"  {summary['exports']['prediction']}")
        print(f"  {summary['exports']['insights']}")
    else:
        print(f"Error           : {summary.get('error', 'Unknown error')}")
    print("============================================")

    raise SystemExit(0)
