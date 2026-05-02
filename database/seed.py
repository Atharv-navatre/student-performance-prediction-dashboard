"""Database seed pipeline for populating Supabase with students and predictions."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EXPORTS_DIR, MODELS_DIR
from database.supabase_client import SupabaseClient
from ml.data_loader import load_processed
from ml.insights import InsightGenerator
from ml.model import StudentPerformanceModel
from ml.preprocessor import StudentPreprocessor


def _safe_print(message: str) -> None:
    """Print safely when the terminal cannot encode Unicode symbols."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


def _to_native(value: object) -> object:
    """Convert pandas or numpy scalar values to native Python types."""

    if hasattr(value, "item"):
        return value.item()
    return value


def get_latest_model() -> StudentPerformanceModel:
    """Load the latest saved XGBoost model from MODELS_DIR. Raises FileNotFoundError if no model exists."""

    model_files = sorted(
        MODELS_DIR.glob("xgboost_*.joblib"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not model_files:
        raise FileNotFoundError(
            "No trained model found in ml/saved_models/. Run python run_pipeline.py first."
        )

    model = StudentPerformanceModel("xgboost")
    model.load(model_files[0])
    return model


def seed_database(limit: int | None = None, batch_size: int = 500) -> dict[str, object]:
    """Full seed pipeline: load data → predict → insert students → insert predictions → log insight. limit: if set, only seed first N students (useful for testing). Returns summary dict."""

    start = time.time()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    print("============================================")
    print("DATABASE SEED PIPELINE")
    print("============================================")

    print("[STAGE 1/4] Loading processed data...")
    df = load_processed()
    if limit is not None:
        df = df.head(limit).copy()
    print(f"Loaded: {len(df)} students")

    print("[STAGE 2/4] Running batch predictions...")
    prep = StudentPreprocessor()
    df_feat = prep.clean(df)
    df_feat = prep.engineer_features(df_feat)
    model = get_latest_model()
    df_pred = model.predict_batch(df_feat)
    at_risk_count = int(df_pred["is_at_risk"].sum()) if "is_at_risk" in df_pred.columns else 0
    print(f"Predicted: {len(df_pred)} students")
    print(f"At risk: {at_risk_count}")

    print("[STAGE 3/4] Inserting to Supabase...")
    client = SupabaseClient()

    students_inserted = client.bulk_insert_students(df_pred, batch_size=batch_size)

    code_to_student_id: dict[str, str] = {}
    student_codes = [str(code) for code in df_pred["student_code"].tolist()]
    for index, student_code in enumerate(student_codes, start=1):
        student = client.get_student_by_code(student_code)
        if student is None:
            print(f"[!] Student not found after insert: {student_code}")
            continue
        code_to_student_id[student_code] = str(student["id"])
        if index % batch_size == 0 or index == len(student_codes):
            print(f"Fetched student IDs: {index}/{len(student_codes)}")

    pred_records: list[dict[str, object]] = []
    for _, row in df_pred.iterrows():
        student_code = str(row["student_code"])
        student_id = code_to_student_id.get(student_code)
        if not student_id:
            print(f"[!] Skipping prediction; no student id for {student_code}")
            continue

        pred_records.append(
            {
                "student_id": student_id,
                "predicted_score": float(_to_native(row["predicted_score"])),
                "performance_category": str(row["performance_category"]),
                "is_at_risk": bool(_to_native(row["is_at_risk"])),
                "model_used": "xgboost",
                "model_version": model.model_version,
            }
        )

    preds_inserted = 0
    for index in range(0, len(pred_records), batch_size):
        batch = pred_records[index:index + batch_size]
        try:
            clean_batch = [
                {key: _to_native(value) for key, value in row.items()}
                for row in batch
            ]
            client.client.table("predictions").insert(clean_batch).execute()
            preds_inserted += len(batch)
            _safe_print(
                f"[✓] Predictions batch {index // batch_size + 1}: {preds_inserted} done"
            )
        except Exception as error:
            print(f"[!] Prediction batch error: {error}")

    print(f"Students inserted  : {students_inserted}")
    print(f"Predictions inserted: {preds_inserted}")

    print("[STAGE 4/4] Logging insight...")
    ig = InsightGenerator()
    insights = ig.analyze_batch(df_pred)
    client.insert_insight(insights)
    print("Insight logged to Supabase")

    elapsed = time.time() - start
    summary = {
        "status": "success",
        "students_inserted": students_inserted,
        "predictions_inserted": preds_inserted,
        "at_risk_count": int(df_pred["is_at_risk"].sum()),
        "elapsed_seconds": round(elapsed, 2),
    }

    _ = json.dumps(summary, default=str)
    _ = EXPORTS_DIR
    return summary


if __name__ == "__main__":
    try:
        print(
            "This will insert data into Supabase.\n"
            "If tables already have data, you may get\n"
            "duplicate student_code errors.\n"
            "Run migrations.sql first to reset if needed."
        )

        summary = seed_database(limit=None)

        print("============================================")
        print("SEED COMPLETE")
        print("============================================")
        print(f"Status              : {summary['status']}")
        print(f"Students inserted   : {summary['students_inserted']}")
        print(f"Predictions inserted: {summary['predictions_inserted']}")
        print(f"At risk             : {summary['at_risk_count']}")
        print(f"Elapsed             : {summary['elapsed_seconds']}s")
        print("============================================")
    except Exception as error:
        print(f"[!] Seed error: {error}")
        print("Run python run_pipeline.py first to train the model")
