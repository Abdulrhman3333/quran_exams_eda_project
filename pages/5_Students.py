import plotly.express as px
import streamlit as st

from app import page_context
from utils.charts import caption
from utils.data import student_aggregates
from utils.style import configure_plot

st.title("Students")
_, df, stats, _ = page_context()
aggregates = stats["student_aggregates"]
attempts = aggregates["attempts"]
fig = px.histogram(attempts, x="attempts", color="exam_branch", barmode="overlay", labels={"attempts": "Attempts for a branch", "count": "Students"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("This aggregate view shows how many attempts students made for each branch, without exposing identities.", "The tallest bin represents the most common attempt count.")
retake = aggregates["retake"]
if retake.empty:
    st.info("There are no first-attempt failures with later observations in this filtered data.")
else:
    retake_summary = retake.groupby("exam_branch", observed=True).agg(first_failures=("passed_later", "size"), passed_later=("passed_later", "sum")).reset_index()
    retake_summary["share_passed_later"] = retake_summary.passed_later / retake_summary.first_failures
    fig = px.bar(retake_summary, x="exam_branch", y="share_passed_later", labels={"exam_branch": "Juz branch", "share_passed_later": "Passed later"})
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("This chart shows the share of students who failed on their first try and later passed the same branch.", "The tallest bar has the strongest observed return-and-pass result.")
branches = aggregates["branches"]
fig = px.histogram(branches, x="branches", labels={"branches": "Number of branches attempted", "count": "Students"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("This distribution counts how many distinct branches each student attempted.", "The tallest bar shows the most common breadth of study.")
