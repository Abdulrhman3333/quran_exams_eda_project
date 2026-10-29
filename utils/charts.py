"""Reusable Plotly charts and computed insight text."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .style import GRADE_COLORS, configure_plot


def grade_bar(frame: pd.DataFrame, x: str = "grade", color: str = "grade", **kwargs):
    counts = frame[x].value_counts().reindex(["Excellent", "Very Good", "Good", "Acceptable", "Fail"], fill_value=0)
    fig = px.bar(x=counts.index, y=counts.values, labels={"x": "Grade", "y": "Exams"}, color=counts.index,
                 color_discrete_map=GRADE_COLORS, **kwargs)
    return configure_plot(fig)


def caption(text: str, insight: str) -> None:
    import streamlit as st
    st.caption(text)
    st.markdown(f'<div class="insight">Insight: {insight}</div>', unsafe_allow_html=True)


def pass_insight(table: pd.DataFrame, label: str, rate_col: str = "pass_rate") -> str:
    if table.empty:
        return "There is not enough data for an insight."
    row = table.loc[table[rate_col].idxmin()]
    return f"{label} {row.iloc[0]} has the lowest pass rate at {row[rate_col] * 100:.1f}%."
