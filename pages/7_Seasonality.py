import calendar

import plotly.express as px
import streamlit as st

from app import page_context
from utils.charts import caption
from utils.style import configure_plot

st.title("Seasonality")
_, df, _, _ = page_context()
hijri_names = ["Muharram", "Safar", "Rabi I", "Rabi II", "Jumada I", "Jumada II", "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"]
hijri = df.groupby("h_month", observed=True).agg(exams=("exam_id", "size"), pass_rate=("passed", "mean")).reset_index()
hijri["month_name"] = hijri.h_month.astype(int).map(dict(enumerate(hijri_names, 1)))
left, right = st.columns(2)
with left:
    fig = px.bar(hijri, x="month_name", y="exams", labels={"month_name": "Hijri month", "exams": "Exams"})
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("Exam volume is grouped by Hijri month.", f"{hijri.loc[hijri.exams.idxmax(), 'month_name']} has the most exams.")
with right:
    fig = px.line(hijri, x="month_name", y=hijri.pass_rate * 100, markers=True, labels={"month_name": "Hijri month", "y": "Pass rate (%)"})
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("Pass rates are compared across Hijri months.", "The highest point is the strongest monthly pass rate.")
weekday_order = list(calendar.day_name)
weekday = df.groupby("weekday", observed=True).agg(exams=("exam_id", "size"), pass_rate=("passed", "mean")).reindex(weekday_order).reset_index()
fig = px.bar(weekday, x="weekday", y="exams", labels={"weekday": "Weekday", "exams": "Exams"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("This chart shows exam volume by Gregorian weekday.", "The tallest bar identifies the busiest weekday.")
