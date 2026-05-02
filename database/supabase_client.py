"""Supabase database client for the Student Performance project."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from supabase import Client, create_client

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SUPABASE_KEY, SUPABASE_URL  # noqa: E402


def _safe_print(message: str) -> None:
    """Print status messages safely on limited Windows terminals."""

    try:
        print(message)
    except UnicodeEncodeError:
        print(message.replace("✓", "OK"))


def _to_native_value(value: object) -> object:
    """Convert numpy-like scalar values to native Python types."""

    if hasattr(value, "item"):
        native_value = value.item()
        if isinstance(native_value, bool):
            return native_value
        if isinstance(native_value, int):
            return int(native_value)
        if isinstance(native_value, float):
            return float(native_value)
        return native_value

    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()

    return value


class SupabaseClient:
    """Single gateway for all Supabase interactions in the project."""

    def __init__(self) -> None:
        """Initialize the Supabase client from environment credentials."""

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set\nin .env file")

        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.connected = True
        _safe_print(f"[✓] Supabase connected: {SUPABASE_URL}")

    def __repr__(self) -> str:
        """Return a concise debug representation of the client state."""

        return (
            "SupabaseClient("
            f"connected={self.connected}, "
            f"url={SUPABASE_URL})"
        )

    def insert_student(self, student_data: dict) -> Optional[dict]:
        """Insert one student record. Returns inserted row or None on error."""

        try:
            allowed_keys = [
                "student_code",
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
            ]
            payload = {
                key: _to_native_value(student_data[key])
                for key in allowed_keys
                if key in student_data
            }
            response = self.client.table("students").insert(payload).execute()
            return response.data[0] if response.data else None
        except Exception as error:
            print(f"[!] insert_student error: {error}")
            return None

    def get_student_by_code(self, student_code: str) -> Optional[dict]:
        """Fetch student record by student_name or student_code depending on DB version."""

        try:
            # Check student_name first since Supabase schema has it
            response = (
                self.client.table("students")
                .select("*")
                .eq("student_name", student_code)
                .execute()
            )
            if response.data:
                return response.data[0]
            
            # Fallback to student_code
            response2 = (
                self.client.table("students")
                .select("*")
                .eq("student_code", student_code)
                .execute()
            )
            return response2.data[0] if response2.data else None
            
        except Exception as error:
            # We silently fail on code mismatch (like column doesn't exist) 
            # and try the fallback if it was a Schema Error.
            if "student_name" in str(error) or "42703" in str(error):
                try:
                    response2 = (
                        self.client.table("students")
                        .select("*")
                        .eq("student_code", student_code)
                        .execute()
                    )
                    return response2.data[0] if response2.data else None
                except Exception as inner_error:
                    print(f"[!] get_student_by_code inner error: {inner_error}")
            else:
                print(f"[!] get_student_by_code error: {error}")
            return None

    def insert_prediction(
        self,
        student_id: str,
        prediction: dict,
        model_version: str = "",
    ) -> Optional[dict]:
        """Insert one prediction record linked to a student."""

        try:
            payload = {
                "student_id": student_id,
                "predicted_score": _to_native_value(prediction["predicted_score"]),
                "performance_category": prediction["performance_category"],
                "is_at_risk": _to_native_value(prediction["is_at_risk"]),
                "model_used": prediction.get("model_used", "xgboost"),
                "model_version": model_version,
            }
            response = self.client.table("predictions").insert(payload).execute()
            return response.data[0] if response.data else None
        except Exception as error:
            print(f"[!] insert_prediction error: {error}")
            return None

    def get_predictions(self, limit: int = 500) -> list[dict]:
        """Fetch latest predictions with student_code joined from students table."""

        try:
            response = (
                self.client.table("predictions")
                .select("*, students(student_code)")
                .order("predicted_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as error:
            print(f"[!] get_predictions error: {error}")
            return []

    def get_at_risk_students(self) -> list[dict]:
        """Fetch all predictions where is_at_risk is True, with student details."""

        try:
            response = (
                self.client.table("predictions")
                .select(
                    "*, students(student_code,attendance_pct,study_hours_per_day,previous_score)"
                )
                .eq("is_at_risk", True)
                .order("predicted_score", desc=False)
                .execute()
            )
            return response.data if response.data else []
        except Exception as error:
            print(f"[!] get_at_risk_students error: {error}")
            return []

    def insert_insight(self, insight: dict) -> Optional[dict]:
        """Insert one insight record into insights_log."""

        try:
            payload = {
                "total_students": _to_native_value(insight["total_students"]),
                "at_risk_count": _to_native_value(insight["at_risk_count"]),
                "at_risk_pct": _to_native_value(insight["at_risk_pct"]),
                "avg_score": _to_native_value(insight["avg_score"]),
                "category_distribution": insight["category_distribution"],
                "top_risk_factors": insight["top_risk_factors"],
                "recommendations": insight["recommendations"],
            }
            payload = json.loads(json.dumps(payload, default=str))
            response = self.client.table("insights_log").insert(payload).execute()
            return response.data[0] if response.data else None
        except Exception as error:
            print(f"[!] insert_insight error: {error}")
            return None

    def get_latest_insight(self) -> Optional[dict]:
        """Fetch the most recent insight from insights_log."""

        try:
            response = (
                self.client.table("insights_log")
                .select("*")
                .order("generated_at", desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as error:
            print(f"[!] get_latest_insight error: {error}")
            return None

    def bulk_insert_students(self, df: pd.DataFrame, batch_size: int = 500) -> int:
        """Insert all students from DataFrame in batches. Returns count of inserted rows."""

        student_cols = [
            "student_code",
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
        ]

        available_cols = [column_name for column_name in student_cols if column_name in df.columns]
        records = df[available_cols].to_dict(orient="records")

        inserted = 0
        for index in range(0, len(records), batch_size):
            batch = records[index:index + batch_size]
            try:
                clean_batch: list[dict[str, object]] = []
                for row in batch:
                    clean_row = {
                        key: _to_native_value(value)
                        for key, value in row.items()
                    }
                    if "student_code" in clean_row:
                        clean_row["student_name"] = clean_row.pop("student_code")
                    clean_batch.append(clean_row)

                self.client.table("students").insert(clean_batch).execute()
                inserted += len(batch)
                _safe_print(
                    f"[✓] Inserted batch: {index // batch_size + 1} ({inserted}/{len(records)})"
                )
            except Exception as error:
                print(f"[!] Batch insert error: {error}")
                continue

        _safe_print(f"[✓] Total inserted: {inserted} students")
        return inserted

    def get_dashboard_stats(self) -> dict:
        """Fetch aggregate stats for the dashboard overview cards."""

        try:
            preds = self.get_predictions(limit=10000)
            if not preds:
                return {
                    "total": 0,
                    "at_risk": 0,
                    "avg_score": 0,
                    "categories": {},
                }

            total = len(preds)
            at_risk = sum(1 for prediction in preds if prediction.get("is_at_risk"))
            avg_score = round(
                sum(float(prediction["predicted_score"]) for prediction in preds) / total,
                2,
            )
            categories: dict[str, int] = {}
            for prediction in preds:
                category = prediction.get("performance_category", "Unknown")
                categories[category] = categories.get(category, 0) + 1

            return {
                "total": total,
                "at_risk": at_risk,
                "avg_score": avg_score,
                "categories": categories,
            }
        except Exception as error:
            print(f"[!] get_dashboard_stats error: {error}")
            return {
                "total": 0,
                "at_risk": 0,
                "avg_score": 0,
                "categories": {},
            }


try:
    db = SupabaseClient()
except Exception as error:
    print(f"[!] Supabase init failed: {error}")
    db = None


if __name__ == "__main__":
    client = SupabaseClient()

    print("=== Testing Supabase Connection ===")

    results = client.get_predictions(limit=5)
    print(f"Predictions fetched: {len(results)}")

    at_risk = client.get_at_risk_students()
    print(f"At-risk students: {len(at_risk)}")

    insight = client.get_latest_insight()
    print(f"Latest insight: {'found' if insight else 'none yet'}")

    stats = client.get_dashboard_stats()
    print(f"Dashboard stats: {stats}")

    print("=== supabase_client.py verified ===")
