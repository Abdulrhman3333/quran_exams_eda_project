import plotly.express as px
import streamlit as st

from app import page_context
from utils.charts import caption
from utils.style import GRADE_COLORS, configure_plot

st.title("Exam Branches")
_, df, _, _ = page_context()
summary = df.groupby("exam_branch", observed=True).agg(exams=("exam_id", "size"), pass_rate=("passed", "mean")).reset_index()
left, right = st.columns(2)
with left:
    fig = px.bar(summary, x="exam_branch", y="exams", labels={"exam_branch": "Juz branch", "exams": "Exams"}, title="Exams per branch")
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("This chart shows exam volume for each Quran branch.", "The tallest bar identifies the most examined branch.")
with right:
    fig = px.bar(summary, x="exam_branch", y=summary.pass_rate * 100, labels={"exam_branch": "Juz branch", "y": "Pass rate (%)"}, title="Pass rate per branch")
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    row = summary.loc[summary.pass_rate.idxmin()]
    caption("This chart compares the share of non-failed exams by branch.", f"Branch {int(row.exam_branch)} has the lowest pass rate at {row.pass_rate * 100:.1f}%.")
st.subheader("Passed degree distribution")
fig = px.box(df.dropna(subset=["degree_passed"]), x="exam_branch", y="degree_passed", labels={"exam_branch": "Juz branch", "degree_passed": "Degree (passed exams)"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Each box shows the distribution of marks among passed exams, excluding fail placeholders.", "The box with the highest median indicates the strongest typical passed mark.")
st.subheader("Grade mix by branch")
mix = df.pivot_table(index="exam_branch", columns="grade", values="exam_id", aggfunc="size", fill_value=0, observed=True)
mix = mix.div(mix.sum(axis=1), axis=0).reset_index().melt("exam_branch", var_name="grade", value_name="share")
fig = px.bar(mix, x="exam_branch", y="share", color="grade", barmode="stack", color_discrete_map=GRADE_COLORS, labels={"share": "Share", "exam_branch": "Juz branch"})
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Each branch bar is normalized to 100% so grade composition is comparable.", "The largest colored segment shows the dominant grade mix.")
