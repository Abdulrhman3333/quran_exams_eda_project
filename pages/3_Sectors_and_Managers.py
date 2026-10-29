import plotly.express as px
import streamlit as st

from app import page_context
from utils.charts import caption
from utils.stats import gap_table
from utils.style import configure_plot

st.title("Sectors and Managers")
_, df, _, _ = page_context()
trend = df.groupby(["month_date", "sector_name"], observed=True).size().reset_index(name="exams")
fig = px.line(trend, x="month_date", y="exams", color="sector_name", labels={"month_date": "Month", "exams": "Exams", "sector_name": "Sector"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("This timeline compares exam volume across sectors over time.", "The highest line at the right edge identifies the current volume leader.")
table = gap_table(df, "sector_name")
fig = px.bar(table.sort_values("gap"), x="gap", y="sector_name", orientation="h", labels={"gap": "Gap vs expected (percentage points)", "sector_name": "Sector"}, color="gap", color_continuous_scale="RdYlGn")
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Positive values mean a sector's observed pass rate is above the branch-mix expectation.", "The longest positive bar is furthest above expectation.")
st.dataframe(table.style.format({"pass_rate": "{:.1%}", "expected": "{:.1%}", "gap": "{:.1f}"}), use_container_width=True, hide_index=True)
