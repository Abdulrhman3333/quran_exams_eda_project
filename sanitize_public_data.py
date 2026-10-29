"""Create a public-safe, deterministic-pseudonym version of the exam export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).parent
SOURCE = ROOT / "exams_clean.csv"
OUTPUT = ROOT / "exams_clean_public.csv"


def _labels(series: pd.Series, prefix: str) -> pd.Series:
    """Map each distinct non-empty value to a stable, readable label."""
    values = series.astype("string").fillna("").str.strip()
    distinct = sorted(value for value in values.unique() if value)
    mapping = {value: f"{prefix} {index:04d}" for index, value in enumerate(distinct, 1)}
    return values.map(mapping).fillna("Unknown")


def create_public_file(source: Path = SOURCE, output: Path = OUTPUT) -> None:
    """Pseudonymize all person, place, and student identifier columns."""
    frame = pd.read_csv(source, encoding="utf-8-sig", low_memory=False)

    student_ids = frame["student_id"].astype("string").fillna("").str.strip()
    student_id_labels = {
        value: f"Student {index:05d}"
        for index, value in enumerate(sorted(value for value in student_ids.unique() if value), 1)
    }
    student_tokens = student_ids.map(student_id_labels).fillna("Student Unknown")
    frame["student_id"] = student_tokens
    frame["student_name"] = student_tokens

    for column, prefix in {
        "teacher_name": "Teacher",
        "mosque_name": "Mosque",
        "supervisor_name": "Supervisor",
        "halaqa_name": "Halaqa",
        "sector_name": "Sector",
        "sector_manager": "Sector Manager",
    }.items():
        frame[column] = _labels(frame[column], prefix)

    frame["teacher_id"] = _labels(frame["teacher_id"], "Teacher ID")
    frame.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(frame):,} rows to {output}")


if __name__ == "__main__":
    create_public_file()
