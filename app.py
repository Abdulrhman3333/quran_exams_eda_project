"""Quran Exams in Jeddah: Results Explorer."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.data import GRADE_ORDER, PERIOD_ORDER, VALID_BRANCHES, apply_filters, load_data
from utils.style import PRIMARY, inject_css

st.set_page_config(page_title="Quran Exams in Jeddah", page_icon=None, layout="wide")
inject_css()


@st.cache_data
def load_cached() -> tuple[pd.DataFrame, dict]:
    return load_data(str(Path(__file__).with_name("exams_clean_public.csv")))


def initialise_filters(frame: pd.DataFrame) -> None:
    years = (int(frame["exam_year"].min()), int(frame["exam_year"].max()))
    defaults = {
        "filter_years": years, "filter_branches": VALID_BRANCHES.copy(), "filter_sectors": [],
        "filter_mosques": [], "filter_grades": GRADE_ORDER.copy(), "filter_sources": ["old", "new"],
        "filter_periods": PERIOD_ORDER.copy(),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def sidebar_filters(frame: pd.DataFrame) -> dict:
    initialise_filters(frame)
    st.sidebar.header("Filters")
    if st.sidebar.button("Reset filters", use_container_width=True):
        for key in ["filter_years", "filter_branches", "filter_sectors", "filter_mosques", "filter_grades", "filter_sources", "filter_periods"]:
            st.session_state.pop(key, None)
        st.rerun()
    years = st.sidebar.slider("Year range", min_value=int(frame.exam_year.min()), max_value=int(frame.exam_year.max()),
                              value=st.session_state["filter_years"], key="filter_years")
    branches = st.sidebar.multiselect("Exam branch", VALID_BRANCHES, key="filter_branches")
    sectors = st.sidebar.multiselect("Sector", sorted(frame.sector_name.dropna().unique()), key="filter_sectors")
    mosque_options = sorted(frame.loc[frame.sector_name.isin(sectors), "mosque_name"].dropna().unique()) if sectors else sorted(frame.mosque_name.dropna().unique())
    mosques = st.sidebar.multiselect("Mosque", mosque_options, key="filter_mosques")
    grades = st.sidebar.multiselect("Grade", GRADE_ORDER, key="filter_grades")
    sources = st.sidebar.multiselect("Data source", ["old", "new"], key="filter_sources")
    periods = st.sidebar.multiselect("Period", PERIOD_ORDER, key="filter_periods")
    return {"years": years, "branches": branches, "sectors": sectors, "mosques": mosques,
            "grades": grades, "sources": sources, "periods": periods}


def page_context() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int], dict]:
    try:
        frame, stats = load_cached()
    except (FileNotFoundError, ValueError) as exc:
        st.error(str(exc))
        st.stop()
    filters = sidebar_filters(frame)
    filtered = apply_filters(frame, filters)
    st.caption(f"{len(filtered):,} rows match the current filters.")
    if filtered.empty:
        st.info("No exams match these filters. Try widening the year range or selecting more options.")
    return frame, filtered, stats, filters


def kpi(label: str, value: str) -> None:
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)


def download_button(frame: pd.DataFrame) -> None:
    export = frame.drop(columns=["student_id", "student_name"], errors="ignore")
    data = io.BytesIO()
    export.to_csv(data, index=False, encoding="utf-8-sig")
    st.download_button("Download current filtered data", data.getvalue(), "quran_exams_filtered.csv", "text/csv")


if __name__ == "__main__":
    frame, filtered, stats, filters = page_context()
    st.title("Quran Exams in Jeddah: Results Explorer")
    st.write("Explore exam volume, outcomes, branches, sectors, mosques, teachers, and seasonality while keeping student identities private.")
    st.info("Use the pages in the left navigation to explore the filtered dataset.")
