import numpy as np
import plotly.express as px
import streamlit as st

from app import page_context
from utils.charts import caption
from utils.stats import gap_table
from utils.style import configure_plot

st.title("Mosques and Teachers")
_, df, _, _ = page_context()
minimum = st.slider("Minimum exams for rankings", 1, max(100, min(1000, len(df))), 100)
mosques = gap_table(df, "mosque_name")
teachers = gap_table(df, "teacher_name")
left, right = st.columns(2)
with left:
    top = mosques.nlargest(10, "exams")
    fig = px.bar(top.sort_values("exams"), x="exams", y="mosque_name", orientation="h", labels={"mosque_name": "Mosque", "exams": "Exams"})
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("This chart ranks the ten highest-volume mosques.", f"{top.iloc[0].mosque_name} has the highest volume among displayed mosques.")
with right:
    ranked = mosques[mosques.exams >= minimum].sort_values("gap")
    fig = px.bar(ranked, x="gap", y="mosque_name", orientation="h", labels={"gap": "Gap (percentage points)", "mosque_name": "Mosque"}, color="gap", color_continuous_scale="RdYlGn")
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("Only mosques meeting the minimum exam count are ranked by branch-adjusted gap.", "The rightmost bar is furthest above expectation.")
st.subheader("Teacher gap versus volume")
ranked = teachers[teachers.exams >= minimum].copy()
fig = px.scatter(ranked, x="exams", y="gap", hover_name="teacher_name", size="exams", log_x=True, labels={"exams": "Exams (log scale)", "gap": "Gap (percentage points)"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Teacher results are compared with expected pass rates; the x-axis is logarithmic.", "Small samples are noisy, so interpret extreme gaps cautiously.")
halaqa = df.groupby("teacher_name", observed=True)["halaqa_name"].nunique().reset_index(name="halaqat").sort_values("halaqat", ascending=False)
st.subheader("Halaqat per teacher")
st.dataframe(halaqa.head(20), use_container_width=True, hide_index=True)
