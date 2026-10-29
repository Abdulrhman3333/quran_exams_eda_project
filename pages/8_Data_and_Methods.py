import streamlit as st

from app import download_button, page_context

st.title("Data and Methods")
frame, df, stats, _ = page_context()
st.subheader("Data dictionary")
dictionary = {
    "exam_id": "Unique exam sitting identifier", "exam_date": "Gregorian exam date",
    "exam_branch": "Quran juz examined", "exam_degree": "Numeric mark from 0 to 100",
    "grade": "Normalized English grade label", "passed": "1 for non-fail grade; missing grade excluded from pass metrics",
    "degree_passed": "Degree retained only for passed exams", "period": "Before, during, or after COVID window",
    "expected_pass_rate": "Overall pass rate for the exam branch", "data_source": "Old or new export",
}
st.table([{"Field": key, "Meaning": value} for key, value in dictionary.items()])
st.subheader("Cleaning notes")
st.write(f"Input rows: {stats['input_rows']:,}. Duplicate exam IDs removed: {stats['duplicate_rows_removed']:,}. Invalid branch/date rows excluded: {stats['invalid_rows_removed']:,}. Valid rows: {stats['valid_rows']:,}.")
st.write("The app reads UTF-8 with BOM, validates the requested branch list, coerces malformed dates/degrees to missing, fills missing sector and manager values as Unknown, and keeps missing-grade rows for volume metrics.")
st.subheader("Limits")
st.write("Pass-rate comparisons are descriptive and branch-adjusted, not causal. Small samples can produce unstable mosque and teacher gaps. Student names and IDs are never shown or included in downloads. COVID periods differ in duration, so volume should be compared using monthly rates where appropriate.")
st.subheader("Current filtered data")
download_button(df)
