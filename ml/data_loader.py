"""Dataset loading and schema normalization utilities."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (  # noqa: E402
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    KAGGLE_COLUMN_MAP,
    PROCESSED_DATASET_PATH,
    RAW_DATASET_PATH,
    TARGET_COLUMN,
)


STUDENT_CODE_COLUMN = "student_code"


class DataLoader:
    """Load, normalize, and persist the project dataset."""

    def __init__(self, raw_path: Path = RAW_DATASET_PATH) -> None:
        """Initialize the loader with the source dataset path."""

        self.raw_path = raw_path
        self.df_raw: pd.DataFrame | None = None
        self.df_clean: pd.DataFrame | None = None

    def __repr__(self) -> str:
        """Return a concise debug representation of the loader state."""

        row_count = len(self.df_clean) if self.df_clean is not None else 0
        return f"DataLoader(source={self.raw_path.name}, rows={row_count})"

    def load_raw(self) -> pd.DataFrame:
        """Load the raw Kaggle dataset from disk."""

        if not self.raw_path.exists():
            raise FileNotFoundError(
                f"Dataset not found at: {self.raw_path}\n"
                "Download 'Student Performance Factors' from Kaggle\n"
                f"and save as: {self.raw_path.name}"
            )

        self.df_raw = pd.read_csv(self.raw_path)
        rows, cols = self.df_raw.shape
        print(f"[✓] Raw dataset loaded: {rows} rows, {cols} columns")
        return self.df_raw

    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename known Kaggle columns into the project's internal schema."""

        filtered_map = {
            raw_name: internal_name
            for raw_name, internal_name in KAGGLE_COLUMN_MAP.items()
            if raw_name in df.columns
        }
        renamed_df = df.rename(columns=filtered_map).copy()
        print(f"[✓] Renamed {len(filtered_map)} columns to internal schema")
        return renamed_df

    def encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode configured categorical columns with safe fallback values."""

        encoded_df = df.copy()
        encoded_count = 0

        for column_name, encoding_map in CATEGORICAL_COLUMNS.items():
            if column_name in encoded_df.columns:
                encoded_df[column_name] = (
                    encoded_df[column_name].map(encoding_map).fillna(-1).astype(int)
                )
                encoded_count += 1

        print(f"[✓] Encoded {encoded_count} categorical columns")
        return encoded_df

    def drop_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows without targets and impute remaining numeric nulls."""

        cleaned_df = df.copy()
        before_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=[TARGET_COLUMN])
        dropped_count = before_rows - len(cleaned_df)
        if dropped_count > 0:
            print(f"[!] Dropped {dropped_count} rows with null target")

        numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
        for column_name in numeric_columns:
            median_value = cleaned_df[column_name].median()
            cleaned_df[column_name] = cleaned_df[column_name].fillna(median_value)

        return cleaned_df

    def select_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep only required columns and report any missing inputs."""

        all_needed = FEATURE_COLUMNS + [TARGET_COLUMN]
        available = [column_name for column_name in all_needed if column_name in df.columns]
        missing = [column_name for column_name in all_needed if column_name not in df.columns]

        if missing:
            print(f"[!] Missing columns: {missing}")

        selected_df = df.loc[:, available].copy()
        feature_count = sum(1 for column_name in available if column_name != TARGET_COLUMN)
        print(f"[✓] Selected {len(available)} columns")
        print(f"    ({feature_count} features + 1 target)")
        return selected_df

    def add_student_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add stable project student identifiers to the cleaned dataset."""

        identified_df = df.reset_index(drop=True).copy()
        student_codes = [f"STU{index:05d}" for index in range(1, len(identified_df) + 1)]
        identified_df.insert(0, STUDENT_CODE_COLUMN, student_codes)
        return identified_df

    def run(self) -> pd.DataFrame:
        """Execute the full dataset loading and cleaning pipeline."""

        loaded_df = self.load_raw()
        renamed_df = self.rename_columns(loaded_df)
        encoded_df = self.encode_categoricals(renamed_df)
        cleaned_df = self.drop_missing(encoded_df)
        selected_df = self.select_and_validate(cleaned_df)
        identified_df = self.add_student_ids(selected_df)
        self.df_clean = identified_df.reset_index(drop=True)
        self._save()
        self._print_summary()
        return self.df_clean

    def _save(self) -> None:
        """Persist the cleaned dataset to the configured processed path."""

        if self.df_clean is None:
            raise ValueError("No cleaned dataset available to save.")

        self.df_clean.to_csv(PROCESSED_DATASET_PATH, index=False)
        print(f"[✓] Saved clean dataset: {PROCESSED_DATASET_PATH}")

    def _print_summary(self) -> None:
        """Print a concise summary of the cleaned dataset."""

        if self.df_clean is None:
            raise ValueError("No cleaned dataset available for summary.")

        total_students = len(self.df_clean)
        feature_count = len(
            [
                column_name
                for column_name in self.df_clean.columns
                if column_name not in {STUDENT_CODE_COLUMN, TARGET_COLUMN}
            ]
        )
        target_min = self.df_clean[TARGET_COLUMN].min()
        target_max = self.df_clean[TARGET_COLUMN].max()
        target_mean = self.df_clean[TARGET_COLUMN].mean()
        null_count = int(self.df_clean.isna().sum().sum())

        print(
            f"\n=== Dataset Summary ===\n"
            f"  Total students  : {total_students}\n"
            f"  Features        : {feature_count} (excluding {STUDENT_CODE_COLUMN} and target)\n"
            f"  Target range    : {target_min:.1f} – {target_max:.1f}\n"
            f"  Target mean     : {target_mean:.2f}\n"
            f"  Null values     : {null_count}\n"
            "=======================\n"
        )


def load_processed() -> pd.DataFrame:
    """Load the processed dataset from disk."""

    if not PROCESSED_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {PROCESSED_DATASET_PATH}.\n"
            "Run DataLoader().run() first."
        )

    return pd.read_csv(PROCESSED_DATASET_PATH)


if __name__ == "__main__":
    loader = DataLoader()
    try:
        df = loader.run()
        print(df.head(3).to_string())
        print(f"\nData types:\n{df.dtypes}")
        print("\n=== data_loader.py verified ===")
    except FileNotFoundError as error:
        print(f"\n[!] {error}")
        print("\nTo fix: download the dataset from Kaggle and")
        print(f"place it at: {RAW_DATASET_PATH}")
        print("\n=== data_loader.py ready — awaiting dataset ===")
