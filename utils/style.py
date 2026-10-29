"""Theme, colors, and shared visual styling."""

import streamlit as st

PRIMARY = "#0f766e"
GRADE_COLORS = {
    "Excellent": "#2a9d8f",
    "Very Good": "#8ab17d",
    "Good": "#e9c46a",
    "Acceptable": "#f4a261",
    "Fail": "#e76f51",
}
PLOTLY_FONT = "Cairo, Tajawal, Arial"


def inject_css() -> None:
    """Apply the shared visual system."""
    st.markdown(
        """<style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: Cairo, Tajawal, Arial, sans-serif; }
        .block-container { padding-top: 2rem; max-width: 1500px; }
        .kpi { background: white; border-radius: 14px; padding: 1rem 1.1rem;
               box-shadow: 0 2px 12px rgba(15,118,110,.10); border: 1px solid #e6efee; }
        .kpi-label { color: #64748b; font-size: .82rem; }
        .kpi-value { color: #0f766e; font-weight: 700; font-size: 1.55rem; }
        .arabic-table td, .arabic-table th { direction: rtl; text-align: right; }
        .insight { color: #0f766e; font-weight: 600; padding: .2rem 0 .8rem; }
        </style>""",
        unsafe_allow_html=True,
    )


def configure_plot(fig):
    fig.update_layout(
        template="plotly_white",
        font={"family": PLOTLY_FONT, "color": "#24323d"},
        margin={"l": 30, "r": 20, "t": 55, "b": 35},
        legend_title_text="",
    )
    return fig
