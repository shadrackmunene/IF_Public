"""Real Livelihoods Youth Segmentation dashboard (Streamlit).

Same three pages, content and model as shiny_dashboard/ (which is kept as the
baseline); only the UI layer is rewritten. data.py, plots.py, questionnaire.py,
theme.py, pathway_content.py, precomputed/ and model/ are copies of the Shiny
app's framework-independent modules, so this folder deploys on its own.

Run with:  streamlit run streamlit_dashboard/app.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import streamlit as st

import data
import plots
import questionnaire
from pathway_content import PERSONA_TAGLINES, SEGMENT_CONTENT
from theme import SEGMENT_COLORS

st.set_page_config(page_title="IF Real Livelihoods", layout="wide")

SEGMENTS = data.SEGMENTS
OVERVIEW = data.overview_stats()
SIZES = data.segment_sizes()
DRIVER_TABLE = data.segment_driver_table()
STAGE_TABLE = data.pathway_stage_table()

st.markdown(
    """
    <style>
      /* Theme lives here (not only in .streamlit/config.toml) because Streamlit reads that file
         from the launch directory, so running from the repo root would silently drop the colours. */
      :root { --brand: #881946; --dark-text: #414144; --light-bg: #F1F3F9; }
      .stApp, [data-testid="stAppViewContainer"] { background-color: var(--light-bg); color: var(--dark-text); }
      /* Top navigation bar: fixed in the header, brand coloured, never scrolls away. */
      [data-testid="stHeader"] { background-color: var(--brand); position: fixed; top: 0; z-index: 1000; }
      [data-testid="stHeader"] a, [data-testid="stHeader"] button, [data-testid="stHeader"] span,
      [data-testid="stHeader"] p, [data-testid="stHeader"] svg { color: #FFFFFF !important; fill: #FFFFFF !important; font-weight: 600; }
      [data-testid="stHeader"] a[aria-current="page"], [data-testid="stHeader"] a:hover { background-color: rgba(255,255,255,0.18) !important; border-radius: 6px; }
      h1, h2, h3, h4, h5 { color: var(--brand); }
      .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background-color: var(--brand); border-color: var(--brand); color: #FFFFFF; }
      .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { background-color: #6E1438; border-color: #6E1438; }
      [data-testid="stRadio"] [role="radiogroup"] label > div:first-child { border-color: var(--brand); }
      [data-baseweb="tab-highlight"] { background-color: var(--brand) !important; }
      [data-baseweb="tab"][aria-selected="true"] { color: var(--brand) !important; }
      [data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #E3E6EE; border-radius: 10px; padding: 0.8rem 1rem; }
      [data-testid="stMetricValue"] { color: var(--brand); }
      [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; }
      .segment-pill { display: inline-block; padding: 4px 14px; border-radius: 999px; color: white; font-weight: 600; font-size: 1.1rem; }
      .pathway-bullet-list { padding-left: 1.1rem; }
      .pathway-bullet-list li { margin-bottom: 0.4rem; }
      .result-card { background: #FFFFFF; border-radius: 12px; padding: 1.5rem; border: 1px solid #E3E6EE; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    </style>
    """,
    unsafe_allow_html=True,
)


def segment_pill(segment: str) -> str:
    return f'<span class="segment-pill" style="background-color:{SEGMENT_COLORS[segment]}">Segment {segment}</span>'


def bullets(items: list[str]) -> str:
    return '<ul class="pathway-bullet-list">' + "".join(f"<li>{b}</li>" for b in items) + "</ul>"


def show_figure(fig) -> None:
    st.pyplot(fig)
    plt.close(fig)


def metric_row(items: list[tuple[str, str, str]]) -> None:
    for col, (title, value, caption) in zip(st.columns(len(items)), items):
        with col:
            st.metric(title, value, help=caption)
            st.caption(caption)


def persona_line(content: dict, *, with_fit: bool) -> str:
    if not content.get("hcd_persona"):
        return content.get("hcd_note", "")
    if with_fit:
        return f"Closest HCD persona: <b>{content['hcd_persona']}</b> (fit {content['hcd_fit']}/100)"
    return f"Closest HCD persona: <b>{content['hcd_persona']}</b> ({PERSONA_TAGLINES.get(content['hcd_persona'], '')})"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def overview_page() -> None:
    st.header("Real Livelihoods Youth Segmentation Study")
    st.write(
        f"Descriptive findings across all {OVERVIEW['n_respondents']:,} respondents (Kenyan youth, 9 counties). "
        "Six segments identified via forced-drivers k-means clustering on 28 HCD-defined demographic, "
        "behavioural and psychographic drivers - see the Segment Profiles tab."
    )
    o = OVERVIEW
    st.subheader("Youth & household profile")
    metric_row([
        ("Median age", f"{o['median_age']:.0f}", "years (16-30 range)"),
        ("Female", f"{o['pct_female']}%", f"Male: {100 - o['pct_female']:.1f}%"),
        ("Independent household", f"{o['pct_own_household']}%", "live in own/rented household"),
    ])
    st.subheader("Education & skills pathway")
    metric_row([
        ("Not currently enrolled", f"{o['pct_not_enrolled']}%", "in any education/training"),
        ("Secondary (highest)", f"{o['pct_secondary_highest']}%", "completed KCSE as highest level"),
        ("TVET/vocational", f"{o['pct_tvet']}%", "completed TVET training"),
        ("University", f"{o['pct_university']}%", "completed a university degree"),
    ])
    st.subheader("Current livelihoods")
    metric_row([
        ("Informal work", f"{o['pct_informal_main']}%", "of those currently working"),
        ("Side activity", f"{o['pct_side_activity']}%", "have a supplementary income activity"),
        ("Self-employed", f"{o['pct_self_employed']}%", "main activity is running a business"),
    ])
    st.subheader("Income & financial security")
    metric_row([
        ("Median income", f"KES {o['median_income']:,.0f}", "per month, personal income"),
        ("Currently saving", f"{o['pct_saving']}%", "saving money in any form"),
        ("Bank account", f"{o['pct_bank_account']}%", "have a personal bank/financial account"),
    ])
    st.subheader("Digital economy & AI")
    metric_row([
        ("Smartphone", f"{o['pct_smartphone']}%", "own a smartphone"),
        ("Internet daily", f"{o['pct_internet_daily']}%", "access the internet daily"),
        ("Mobile money daily", f"{o['pct_mobile_money_daily']}%", "use mobile money daily"),
        ("Used an AI tool", f"{o['pct_used_ai']}%", "have ever used an AI tool"),
    ])
    st.subheader("Six segments at a glance")
    show_figure(plots.segment_size_chart(SIZES))


def segment_profiles_page() -> None:
    left, right = st.columns([1, 4])
    with left:
        st.subheader("Choose a segment")
        seg = st.radio(
            "Segment", SEGMENTS, label_visibility="collapsed",
            format_func=lambda s: f"Segment {s} ({SIZES.loc[SIZES.segment == s, 'pct'].iloc[0]}%)",
        )
    content = SEGMENT_CONTENT[seg]
    size_row = SIZES[SIZES.segment == seg].iloc[0]
    with right:
        st.markdown(f"### {segment_pill(seg)} &nbsp; {size_row['pct']}% of respondents (n={size_row['n']})",
                    unsafe_allow_html=True)
        st.markdown(f"**{content['headline']}**")
        st.markdown(persona_line(content, with_fit=True), unsafe_allow_html=True)
        demo, behav, psycho, pathway = st.tabs(["Demographic", "Behavioural", "Psychographic", "Livelihood pathway"])
        with demo:
            show_figure(plots.driver_bar_chart(DRIVER_TABLE, "Demographic", seg))
        with behav:
            show_figure(plots.driver_bar_chart(DRIVER_TABLE, "Behavioral", seg))
        with psycho:
            show_figure(plots.driver_bar_chart(DRIVER_TABLE, "Psychographic", seg))
        with pathway:
            show_figure(plots.pathway_stage_chart(STAGE_TABLE, seg))
            st.markdown("##### Where they sit")
            st.markdown(bullets(content["where_they_sit"]), unsafe_allow_html=True)
            st.markdown("##### What the survey says would help them move on")
            st.markdown(bullets(content["what_would_help"]), unsafe_allow_html=True)
            st.caption(content["hcd_link"])


def render_result(result: dict) -> None:
    seg = result["segment"]
    content = SEGMENT_CONTENT[seg]
    st.markdown(f"### You match {segment_pill(seg)}", unsafe_allow_html=True)
    st.markdown(f"**{content['headline']}**")
    st.markdown(persona_line(content, with_fit=False), unsafe_allow_html=True)
    show_figure(plots.probability_chart(result["probabilities"]))
    st.markdown("##### Where you likely sit")
    st.markdown(bullets(content["where_they_sit"]), unsafe_allow_html=True)
    st.markdown("##### Your growth pathway - what would help you move on")
    st.markdown(bullets(content["what_would_help"]), unsafe_allow_html=True)
    show_figure(plots.pathway_stage_chart(STAGE_TABLE, seg))


@st.dialog("Your result", width="large")
def results_dialog(answers: dict | None) -> None:
    """Floating results window. With `answers` it shows a progress meter while predicting, then the
    result; with None it re-opens the last result. Closing (X, Esc, click outside or the button) returns
    to the questionnaire exactly as the respondent left it."""
    if answers is not None and st.session_state.get("assessment_answers") != answers:
        meter = st.progress(0, text="Reading your answers…")
        time.sleep(0.25)
        questionnaire.answers_to_model_row(answers)  # fails fast on a bad mapping before the model loads
        meter.progress(35, text="Loading the prediction model…")
        result = questionnaire.score(answers)
        meter.progress(80, text="Matching you to a segment…")
        time.sleep(0.25)
        meter.progress(100, text="Preparing your profile…")
        time.sleep(0.2)
        meter.empty()
        st.session_state["assessment_answers"] = answers
        st.session_state["assessment_result"] = result
    render_result(st.session_state["assessment_result"])
    if st.button("Close", type="primary", key="close_results"):
        st.rerun()


def self_assessment_page() -> None:
    st.header("Find your segment")
    st.write(
        "Answer these 12 questions as honestly as you can. This uses the same statistical model "
        "built from the full survey's 28 drivers, reduced via LASSO regression to the most "
        "predictive short set (held-out accuracy 76.7%, 6 segments - see the Segment Profiles tab "
        "for what each one means)."
    )
    with st.form("assessment"):
        answers = {}
        for q in questionnaire.QUESTIONS:
            if q["widget"] == "numeric":
                answers[q["id"]] = st.number_input(
                    q["text"], min_value=q.get("min"), max_value=q.get("max"), value=q.get("value", 20), step=1)
            else:
                # Options are addressed by position: several questions map different
                # answer labels to the same model code, so a code-keyed dict would
                # silently drop all but one of those labels.
                idx = st.radio(q["text"], range(len(q["options"])), format_func=lambda i, q=q: q["options"][i][0])
                answers[q["id"]] = q["options"][idx][1]
        submitted = st.form_submit_button("See my results", type="primary")
    if submitted:
        results_dialog(answers)
    elif "assessment_result" in st.session_state and st.button("View my last result"):
        results_dialog(None)


pages = st.navigation(
    [
        st.Page(overview_page, title="Overview", url_path="overview", default=True),
        st.Page(segment_profiles_page, title="Segment Profiles", url_path="segment-profiles"),
        st.Page(self_assessment_page, title="Self-Assessment", url_path="self-assessment"),
    ],
    position="top",
)
pages.run()
