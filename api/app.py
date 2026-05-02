"""Thin Flask API for student performance predictions and analytics."""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT, MODELS_DIR  # noqa: E402
from database.supabase_client import SupabaseClient  # noqa: E402
from ml.insights import InsightGenerator  # noqa: F401,E402
from ml.model import StudentPerformanceModel  # noqa: E402
from ml.preprocessor import StudentPreprocessor  # noqa: F401,E402


app = Flask(__name__)
CORS(app)

_model: StudentPerformanceModel | None = None


def get_model() -> StudentPerformanceModel:
    """Lazy-load the latest XGBoost model. Cached in module-level _model variable."""

    global _model

    if _model is not None:
        return _model

    model_files = sorted(
        MODELS_DIR.glob("xgboost_*.joblib"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not model_files:
        raise FileNotFoundError(
            "No trained model found. Run python run_pipeline.py first."
        )

    _model = StudentPerformanceModel("xgboost")
    _model.load(model_files[0])
    return _model


def _load_local_predictions(limit: int | None = None) -> list[dict]:
    """Build prediction records from the local processed CSV as a fallback."""

    import pandas as pd

    from config import PROCESSED_DATASET_PATH

    if not PROCESSED_DATASET_PATH.exists():
        return []

    df = pd.read_csv(PROCESSED_DATASET_PATH)
    if limit is not None:
        df = df.head(limit)

    prep = StudentPreprocessor()
    df_features = prep.clean(df)
    df_features = prep.engineer_features(df_features)

    model = get_model()
    df_pred = model.predict_batch(df_features)

    predictions: list[dict] = []
    for _, row in df_pred.iterrows():
        predictions.append(
            {
                "student_id": str(row.get("student_code", "")),
                "predicted_score": float(row["predicted_score"]),
                "performance_category": str(row["performance_category"]),
                "is_at_risk": bool(row["is_at_risk"]),
                "model_used": "xgboost",
                "predicted_at": "2026-04-13T12:00:00",
                "students": {
                    "student_code": str(row.get("student_code", "")),
                    "attendance_pct": float(row.get("attendance_pct", 0)),
                    "study_hours_per_day": float(row.get("study_hours_per_day", 0)),
                    "previous_score": float(row.get("previous_score", 0)),
                },
            }
        )
    return predictions


def error_response(message: str, status: int = 400) -> tuple:
    """Return a JSON API error response."""

    return jsonify({"error": message, "status": status}), status


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""

    try:
        return jsonify(
            {
                "status": "ok",
                "service": "Student Performance API",
                "model": "xgboost",
                "version": "1.0.0",
            }
        ), 200
    except Exception as error:
        return error_response(str(error), 500)


@app.route("/api/predict", methods=["POST"])
def predict():
    """Predict performance for one student. Body: JSON dict of feature values. Returns prediction dict."""

    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Request body must be JSON", 400)

        model = get_model()
        result = model.predict(data)

        if "student_code" in data:
            try:
                db = SupabaseClient()
                student = db.get_student_by_code(str(data["student_code"]))
                if student:
                    db.insert_prediction(student["id"], result)
            except Exception:
                pass

        return jsonify(result), 200
    except FileNotFoundError as error:
        return error_response(str(error), 503)
    except Exception as error:
        return error_response(str(error), 500)


@app.route("/api/students/at-risk", methods=["GET"])
def at_risk_students():
    """Fetch all at-risk students with their latest predictions."""

    try:
        db = SupabaseClient()
        students = db.get_at_risk_students()
        if not students:
            predictions = _load_local_predictions(limit=None)
            students = [prediction for prediction in predictions if prediction.get("is_at_risk") is True]
        return jsonify({"count": len(students), "students": students}), 200
    except Exception as error:
        return error_response(str(error), 500)


@app.route("/api/insights/latest", methods=["GET"])
def latest_insight():
    """Fetch the most recent insight from insights_log."""

    try:
        db = SupabaseClient()
        insight = db.get_latest_insight()
        if not insight:
            return jsonify({"error": "No insights found", "hint": "Run seed.py first"}), 404
        return jsonify(insight), 200
    except Exception as error:
        return error_response(str(error), 500)


@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    """Fetch aggregate stats for dashboard overview cards."""

    try:
        db = SupabaseClient()
        stats = db.get_dashboard_stats()
        return jsonify(stats), 200
    except Exception as error:
        return error_response(str(error), 500)


@app.route("/api/predictions", methods=["GET"])
def get_predictions():
    """Fetch latest predictions. Optional query param: limit (default 100)."""

    try:
        limit = request.args.get("limit", 100, type=int)
        limit = min(limit, 2000)
        db = SupabaseClient()
        predictions = db.get_predictions(limit=limit)
        if not predictions:
            predictions = _load_local_predictions(limit=limit)
        return jsonify({"count": len(predictions), "predictions": predictions}), 200
    except Exception as error:
        return error_response(str(error), 500)


@app.errorhandler(404)
def not_found(error):
    """Return a JSON 404 response."""

    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Return a JSON 405 response."""

    return jsonify({"error": "Method not allowed", "status": 405}), 405


if __name__ == "__main__":
    # Local development only.
    # Production uses Gunicorn via Docker.
    print("=" * 44)
    print("Starting Student Performance API")
    print(f"Host : {FLASK_HOST}")
    print(f"Port : {FLASK_PORT}")
    print(f"Debug: {FLASK_DEBUG}")
    print("=" * 44)
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )
