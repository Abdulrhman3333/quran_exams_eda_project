import plotly.express as px
import streamlit as st

from app import kpi, page_context
from utils.charts import caption, grade_bar
from utils.data import GRADE_ORDER
from utils.style import configure_plot

st.title("Overview")
frame, df, stats, _ = page_context()
passed = df["passed"].mean()
excellent = df["is_excellent"].mean()
cols = st.columns(7)
values = [
    ("Total exams", f"{len(df):,}"), ("Unique students", f"{stats['unique_students']:,}"),
    ("Pass rate", f"{passed * 100:.1f}%" if passed == passed else "—"),
    ("Excellent rate", f"{excellent * 100:.1f}%"), ("Mosques", f"{df.mosque_name.nunique():,}"),
    ("Teachers", f"{df.teacher_name.nunique():,}"),
    ("Date range", f"{df.exam_date.min():%Y}–{df.exam_date.max():%Y}"),
]
for col, (label, value) in zip(cols, values):
    with col:
        kpi(label, value)
st.subheader("Exams and pass rate by year")
year = df.groupby("exam_year", observed=True).agg(exams=("exam_id", "size"), pass_rate=("passed", "mean")).reset_index()
fig = px.line(year, x="exam_year", y="exams", markers=True, labels={"exam_year": "Year", "exams": "Exams"})
fig.add_scatter(x=year.exam_year, y=year.pass_rate * 100, name="Pass rate (%)", yaxis="y2", mode="lines+markers")
fig.update_layout(yaxis2={"overlaying": "y", "side": "right", "title": "Pass rate (%)"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Bars/left axis show annual exam volume; the line/right axis shows pass rate.", f"{year.loc[year.exams.idxmax(), 'exam_year']:.0f} has the highest exam volume.")
left, right = st.columns(2)
with left:
    st.subheader("Grade distribution")
    st.plotly_chart(grade_bar(df), use_container_width=True)
    caption("This chart shows the number of exams in each reported grade.", f"{df.grade.value_counts().index[0]} is the most common reported grade.")
with right:
    st.subheader("Exam counts by year and month")
    heat = df.pivot_table(index="exam_year", columns="exam_month", values="exam_id", aggfunc="size", fill_value=0, observed=True)
    fig = px.imshow(heat, labels={"x": "Month", "y": "Year", "color": "Exams"}, aspect="auto", color_continuous_scale="Teal")
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("Darker cells indicate months with more exams.", "The busiest month is visible as the darkest cell.")
