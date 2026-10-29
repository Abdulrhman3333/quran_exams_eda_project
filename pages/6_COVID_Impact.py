import plotly.express as px
import streamlit as st

from app import page_context
from utils.data import PERIOD_ORDER
from utils.stats import covid_test
from utils.style import configure_plot
from utils.charts import caption

st.title("COVID Impact")
_, df, _, _ = page_context()
monthly = df.groupby("month_date", observed=True).size().reset_index(name="exams")
fig = px.line(monthly, x="month_date", y="exams", labels={"month_date": "Month", "exams": "Exams"})
fig.add_vrect(x0="2020-03-01", x1="2021-08-31", fillcolor="#f4a261", opacity=.18, line_width=0, annotation_text="COVID window")
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Monthly exam volume is shown with the COVID window shaded.", "The lowest point in the timeline marks the sharpest volume reduction.")
period = df.groupby("period", observed=True).agg(
    exams=("exam_id", "size"), months=("month_date", "nunique"), pass_rate=("passed", "mean")
).reindex(PERIOD_ORDER).reset_index()
period["monthly_exams"] = period["exams"] / period["months"].replace(0, float("nan"))
left, right = st.columns(2)
with left:
    fig = px.bar(period, x="period", y="monthly_exams", labels={"period": "Period", "monthly_exams": "Average exams per month"})
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("This chart uses average exams per month because the three periods have different lengths.", "The tallest bar has the highest monthly volume.")
with right:
    fig = px.bar(period, x="period", y=period.pass_rate * 100, labels={"period": "Period", "y": "Pass rate (%)"})
    st.plotly_chart(configure_plot(fig), use_container_width=True)
    caption("This chart compares pass rates across the three periods.", "The tallest bar has the highest pass rate.")
heat = df.pivot_table(index="exam_branch", columns="period", values="passed", aggfunc="mean", observed=True).reindex(columns=PERIOD_ORDER)
fig = px.imshow(heat, labels={"x": "Period", "y": "Branch", "color": "Pass rate"}, zmin=0, zmax=1, aspect="auto", color_continuous_scale="Teal")
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("This heatmap compares branch pass rates across periods.", "The darkest cell is the highest branch-period pass rate.")
same = df[df.exam_year.between(2018, 2023)].groupby(["exam_year", "exam_month"], observed=True).size().reset_index(name="exams")
fig = px.line(same, x="exam_month", y="exams", color="exam_year", markers=True, labels={"exam_month": "Calendar month", "exams": "Exams"})
st.plotly_chart(configure_plot(fig), use_container_width=True)
caption("Same-month volume patterns are compared across 2018–2023.", "Lines that repeatedly peak in the same months indicate recurring seasonality.")
test = covid_test(df)
st.info(f"Chi-square test of period versus pass/fail: χ²={test['chi2']:.2f}, p={test['p_value']:.4g}, Cramer's V={test['cramers_v']:.3f} (n={test['n']:,}).")
