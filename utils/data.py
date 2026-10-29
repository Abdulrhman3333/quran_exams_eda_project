"""Data loading, cleaning, derived metrics, and shared filter state."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

VALID_BRANCHES = [1, 2, 3, 5, 8, 10, 13, 15, 20, 25, 30]
GRADE_ORDER = ["Excellent", "Very Good", "Good", "Acceptable", "Fail"]
PERIOD_ORDER = ["Before COVID", "During COVID", "After COVID"]
COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2021-08-31")
REQUIRED_COLUMNS = {
    "exam_id", "student_id", "student_name", "exam_branch", "exam_degree",
    "exam_date", "grade", "teacher_id", "teacher_name", "mosque_name",
    "halaqa_name", "sector_name", "sector_manager", "data_source",
    "h_year", "h_month", "h_day",
}


def _period(value: pd.Timestamp) -> str:
    if value < COVID_START:
        return "Before COVID"
    if value <= COVID_END:
        return "During COVID"
    return "After COVID"


def _normalise_grade(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    return values.replace({
        "ممتاز": "Excellent",
        "جيدجداً": "Very Good",
        "جيد جداً": "Very Good",
        "جيد": "Good",
        "مقبول": "Acceptable",
        "راسب": "Fail",
        "لم يجتز": "Fail",
    })


@st.cache_data(show_spinner="Loading and preparing exam data...")
def load_data(path: str = "exams_clean.csv") -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load the clean CSV, validate rows, and calculate display-safe metrics."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source.resolve()}")
    raw = pd.read_csv(source, encoding="utf-8-sig", low_memory=False)
    missing = sorted(REQUIRED_COLUMNS - set(raw.columns))
    if missing:
        raise ValueError(f"exams_clean.csv is missing required columns: {', '.join(missing)}")
    frame = raw.copy()
    frame["exam_date"] = pd.to_datetime(frame["exam_date"], errors="coerce")
    frame["exam_branch"] = pd.to_numeric(frame["exam_branch"], errors="coerce")
    frame["exam_degree"] = pd.to_numeric(frame["exam_degree"], errors="coerce")
    frame["grade"] = _normalise_grade(frame["grade"])
    frame["sector_name"] = frame["sector_name"].fillna("Unknown").astype("string").replace("", "Unknown")
    frame["sector_manager"] = frame["sector_manager"].fillna("Unknown").astype("string").replace("", "Unknown")
    for column in ["teacher_name", "mosque_name", "halaqa_name", "teacher_id", "data_source"]:
        frame[column] = frame[column].fillna("Unknown").astype("string").replace("", "Unknown")
    before = len(frame)
    duplicate_count = int(frame.duplicated(subset=["exam_id"], keep="first").sum())
    frame = frame.drop_duplicates(subset=["exam_id"], keep="first")
    invalid_branch = ~frame["exam_branch"].isin(VALID_BRANCHES)
    invalid_date = frame["exam_date"].isna()
    invalid_count = int((invalid_branch | invalid_date).sum())
    frame = frame.loc[~(invalid_branch | invalid_date)].copy()
    frame["exam_branch"] = frame["exam_branch"].astype("int16")
    frame["exam_year"] = frame["exam_date"].dt.year.astype("int16")
    frame["exam_month"] = frame["exam_date"].dt.month.astype("int8")
    frame["passed"] = frame["grade"].map(
        lambda value: np.nan if pd.isna(value) else int(value != "Fail")
    ).astype("float32")
    frame["is_excellent"] = frame["grade"].map(
        lambda value: int(value == "Excellent") if not pd.isna(value) else 0
    ).astype("int8")
    frame["degree_passed"] = frame["exam_degree"].where(frame["passed"] == 1)
    frame["period"] = frame["exam_date"].map(_period)
    branch_rates = frame.groupby("exam_branch", observed=True)["passed"].mean()
    frame["expected_pass_rate"] = frame["exam_branch"].map(branch_rates)
    frame["weekday"] = frame["exam_date"].dt.day_name()
    frame["month_date"] = frame["exam_date"].dt.to_period("M").dt.to_timestamp()
    for column in ["grade", "period", "data_source", "sector_name", "sector_manager", "weekday"]:
        frame[column] = frame[column].astype("category")
    frame["exam_branch"] = pd.Categorical(frame["exam_branch"], categories=VALID_BRANCHES, ordered=True)
    privacy_aggregates = student_aggregates(frame)
    unique_students = int(frame["student_id"].nunique())
    frame = frame.drop(columns=["student_id", "student_name"])
    stats: dict[str, Any] = {
        "input_rows": before,
        "duplicate_rows_removed": duplicate_count,
        "invalid_rows_removed": invalid_count,
        "valid_rows": len(frame),
        "unique_students": unique_students,
        "student_aggregates": privacy_aggregates,
    }
    return frame, stats


def student_aggregates(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return privacy-safe student-level tables without exposing identifiers."""
    work = frame.copy()
    attempts = work.groupby(["student_id", "exam_branch"], observed=True).size().reset_index(name="attempts")
    first = work.sort_values(["student_id", "exam_branch", "exam_date"]).copy()
    first["attempt_no"] = first.groupby(["student_id", "exam_branch"], observed=True).cumcount() + 1
    first_attempt = first[first["attempt_no"] == 1]
    later_pass = first.groupby(["student_id", "exam_branch"], observed=True)["passed"].max().reset_index(name="passed_later")
    failures = first_attempt[first_attempt["grade"] == "Fail"].merge(
        later_pass, on=["student_id", "exam_branch"], how="left"
    )
    return {
        "attempts": attempts.drop(columns="student_id"),
        "retake": failures.assign(passed_later=failures["passed_later"].fillna(0))[["exam_branch", "passed_later"]],
        "branches": work.groupby("student_id", observed=True)["exam_branch"].nunique().reset_index(name="branches").drop(columns="student_id"),
    }


def apply_filters(frame: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    """Apply the shared sidebar filters."""
    mask = frame["exam_year"].between(filters["years"][0], filters["years"][1])
    if filters["branches"]:
        mask &= frame["exam_branch"].isin(filters["branches"])
    if filters["sectors"]:
        mask &= frame["sector_name"].isin(filters["sectors"])
    if filters["mosques"]:
        mask &= frame["mosque_name"].isin(filters["mosques"])
    if filters["grades"]:
        mask &= frame["grade"].isin(filters["grades"])
    if filters["sources"]:
        mask &= frame["data_source"].isin(filters["sources"])
    if filters["periods"]:
        mask &= frame["period"].isin(filters["periods"])
    return frame.loc[mask].copy()
