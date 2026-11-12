"""Youth Livelihoods dashboard (Streamlit).

Same four pages, content and model as shiny_dashboard/; only the UI layer differs. data.py, plots.py,
questionnaire.py, theme.py, pathway_content.py, overview_cards.py, precomputed/ and model/ are copies of the
Shiny app's framework-independent modules, so this folder deploys on its own.

Run with:  streamlit run streamlit_dashboard/app.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import data
import overview_cards
import plots
import questionnaire
from pathway_content import SEGMENT_CONTENT
from theme import SEGMENT_NAMES, SEGMENT_PILL_COLORS

st.set_page_config(page_title="Youth Livelihoods", layout="wide")

SEGMENTS = data.SEGMENTS
NAMES = data.segment_names() or SEGMENT_NAMES
OVERVIEW = data.overview_stats()
SIZES = data.segment_sizes()
DRIVER_TABLE = data.segment_driver_table()
STAGE_TABLE = data.pathway_stage_table()
DISTS = data.question_distributions()
NUMS = data.numeric_summary()
N_BY_SEGMENT = {r.segment: int(r.n) for r in SIZES.itertuples()}
N_BY_SEGMENT["All"] = int(SIZES["n"].sum())

AGE_MIN, AGE_MAX = 18, 30
AGE_MESSAGE = (f"This tool is meant for young people aged {AGE_MIN} to {AGE_MAX}. "
               f"Please enter an age between {AGE_MIN} and {AGE_MAX}.")

_SEG_DOT = ["#D3618F", "#4EC2BC", "#FAA62E", "#2E9462", "#665FF7", "#F94B4B"]  # same as the chart colours


def _dot_css(key: str, first_is_all: bool) -> str:
    """Colour dot before each segment option so the choices match the charts."""
    rules = []
    offset = 2 if first_is_all else 1
    if first_is_all:
        rules.append(f'.st-key-{key} [role="radiogroup"] > label:nth-of-type(1) [data-testid="stMarkdownContainer"] p::before'
                     '{content:"";display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:7px;'
                     'border:2px solid #9AA0A6;vertical-align:middle}')
    for i, c in enumerate(_SEG_DOT):
        rules.append(f'.st-key-{key} [role="radiogroup"] > label:nth-of-type({i + offset}) '
                     '[data-testid="stMarkdownContainer"] p::before'
                     f'{{content:"";display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:7px;'
                     f'background:{c};vertical-align:middle}}')
    return "\n".join(rules)


st.markdown(
    """
    <style>
      /* Theme lives here (not only in .streamlit/config.toml) because Streamlit reads that file
         from the launch directory, so running from the repo root would silently drop the colours. */
      :root { --brand: #0F6B52; --dark-text: #1F2A24; --light-bg: #F6F7F5; --border: #E2E5E0; --brand-light: #E6F2EE;
              --muted: #5C6B62; }
      .stApp, [data-testid="stAppViewContainer"] { background-color: var(--light-bg); color: var(--dark-text); }
      /* Top bar: white, fixed, title on the left, ALL-CAPS page links. */
      [data-testid="stHeader"] { background-color: #FFFFFF; border-bottom: 1px solid var(--border); position: fixed; top: 0; z-index: 1000; }
      [data-testid="stHeader"]::before { content: "YOUTH LIVELIHOODS"; position: absolute; left: 1.4rem; top: 50%;
          transform: translateY(-50%); font-weight: 800; letter-spacing: .08em; color: var(--brand); font-size: 15px; }
      [data-testid="stHeader"] a, [data-testid="stHeader"] button, [data-testid="stHeader"] span,
      [data-testid="stHeader"] p, [data-testid="stHeader"] svg { color: var(--muted) !important; fill: var(--muted) !important;
          font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
      [data-testid="stHeader"] a[aria-current="page"], [data-testid="stHeader"] a[aria-current="page"] span {
          color: var(--brand) !important; border-bottom: 2px solid var(--brand); border-radius: 0; }
      [data-testid="stHeader"] a:hover { background-color: var(--brand-light) !important; }
      h1, h2, h3, h4, h5 { color: var(--dark-text); }
      .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background-color: var(--brand); border-color: var(--brand); color: #FFFFFF; }
      .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { background-color: #0B5440; border-color: #0B5440; }
      [data-testid="stRadio"] [role="radiogroup"] label > div:first-child { border-color: var(--brand); }
      /* Tab bar (Demographic / Behavioural / ...): pinned under the top bar while charts scroll, active tab filled */
      [data-baseweb="tab-list"] { position: sticky; top: 3.75rem; z-index: 99; background: var(--light-bg);
          padding-top: 6px; gap: 4px; }
      [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
      [data-baseweb="tab"] { background: #FFFFFF; border-radius: 8px 8px 0 0; padding: 10px 18px; font-weight: 700;
          color: var(--muted); }
      [data-baseweb="tab"]:hover { background: var(--brand-light); color: var(--brand); }
      [data-baseweb="tab"][aria-selected="true"] { background: var(--brand) !important; color: #FFFFFF !important; }
      [data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF !important; }
      [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; }
      .segment-pill { display: inline-block; padding: 4px 14px; border-radius: 999px; color: white; font-weight: 600; font-size: 1.1rem; }
      .pathway-bullet-list { padding-left: 1.1rem; }
      .pathway-bullet-list li { margin-bottom: 0.4rem; }
      .result-card { background: #FFFFFF; border-radius: 12px; padding: 1.5rem; border: 1px solid var(--border); box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
      .muted { color: var(--muted); }
      /* Overview stat cards: tinted background + icon */
      .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 6px 0 22px; }
      .stat-card { display: flex; align-items: center; gap: 14px; padding: 16px 18px; border: 1px solid; border-radius: 12px; }
      .stat-icon { flex: 0 0 auto; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; }
      .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); font-weight: 600; }
      .stat-value { font-size: 26px; font-weight: 700; line-height: 1.2; }
      .stat-sub { font-size: 12px; color: var(--muted); }
      /* Selector column that stays put while the charts scroll */
      [data-testid="stColumn"]:has(.sticky-anchor) { position: sticky; top: 4.6rem; align-self: flex-start;
          max-height: calc(100vh - 6rem); overflow-y: auto; }
    """ + _dot_css("profile_seg", False) + _dot_css("ex_seg", True) + """
    </style>
    """,
    unsafe_allow_html=True,
)


def segment_pill(segment: str) -> str:
    return (f'<span class="segment-pill" style="background-color:{SEGMENT_PILL_COLORS[segment]}">'
            f'{NAMES.get(segment, segment)}</span>')


def bullets(items: list[str]) -> str:
    return '<ul class="pathway-bullet-list">' + "".join(f"<li>{b}</li>" for b in items) + "</ul>"


def show_figure(fig, key: str | None = None) -> None:
    st.plotly_chart(fig, width="stretch", config=plots.PLOTLY_CONFIG, key=key)


def sticky_anchor() -> None:
    st.markdown('<span class="sticky-anchor"></span>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def overview_page() -> None:
    st.header("Real Livelihoods Youth Segmentation Study")
    st.write(
        f"Descriptive findings across all {OVERVIEW['n_respondents']:,} respondents (Kenyan youth, 9 counties). "
        "Six youth segments were identified from their demographics, behaviours and mindsets - "
        "see the Segment Profiles tab."
    )
    for g in overview_cards.groups(OVERVIEW):
        st.subheader(g["title"])
        st.markdown(overview_cards.cards_html(g["cards"], g["palette"]), unsafe_allow_html=True)
    st.subheader("Six segments at a glance")
    show_figure(plots.segment_size_chart(SIZES), key="ov_sizes")
    counts = data.county_counts()
    if not counts.empty:
        st.subheader("Where respondents are")
        st.caption("Bubble size shows the number of respondents in each county.")
        show_figure(plots.county_map(counts), key="ov_county")
        st.caption(f"Counties with fewer than {data.MIN_COUNTY_N} respondents are excluded from the map.")
        missed = plots.unmatched_counties(counts)
        if missed:
            st.caption("Not shown on the map (name not recognised): " + ", ".join(missed))


def segment_profiles_page() -> None:
    left, right = st.columns([1, 3.4])
    with left:
        sticky_anchor()
        st.subheader("Choose a segment")
        seg = st.radio(
            "Segment", SEGMENTS, label_visibility="collapsed", key="profile_seg",
            format_func=lambda s: f"{NAMES[s]} ({SIZES.loc[SIZES.segment == s, 'pct'].iloc[0]}%)",
        )
    content = SEGMENT_CONTENT[seg]
    size_row = SIZES[SIZES.segment == seg].iloc[0]
    with right:
        st.markdown(f"### {segment_pill(seg)} &nbsp; {size_row['pct']}% of respondents (n={size_row['n']})",
                    unsafe_allow_html=True)
        st.markdown(f"**{content['headline']}**")
        pop = data.population_estimate(seg)
        if pop:
            st.caption(f"Estimated {pop['n']:,} young people nationwide ({pop['pct']}% of {pop['total']:,}). "
                       "Directional sizing only: these are approximate values, modelled from census "
                       "records and predicted segments, not a headcount.", help=pop["note"])
        where = data.county_summary(seg)
        if where:
            st.caption(where)
        demo, behav, psycho, pathway = st.tabs(["Demographic", "Behavioural", "Psychographic", "Livelihood pathway"])
        for tab, category in ((demo, "Demographic"), (behav, "Behavioral"), (psycho, "Psychographic")):
            with tab:
                for kind, title in (("pct", "Share of the segment"), ("score", "Average scores")):
                    fig = plots.driver_bar_chart(DRIVER_TABLE, category, seg, kind, N_BY_SEGMENT)
                    if fig is not None:
                        with st.container(border=True):
                            st.markdown(f"**{title}**")
                            show_figure(fig, key=f"drv_{category}_{kind}_{seg}")
        with pathway:
            show_figure(plots.pathway_stage_chart(STAGE_TABLE, seg, N_BY_SEGMENT.get(seg)), key=f"path_{seg}")
            st.markdown("##### Where they sit")
            st.markdown(bullets(content["where_they_sit"]), unsafe_allow_html=True)
            st.markdown("##### What the survey says would help them move on")
            st.markdown(bullets(content["what_would_help"]), unsafe_allow_html=True)
            st.caption(content["hcd_link"])


def deep_dives_page() -> None:
    dims = [d for d in data.DIMENSION_ORDER if data.sections_for(d)]
    left, right = st.columns([1, 3.4])
    with left:
        sticky_anchor()
        dim = st.radio("Dimension", dims, key="ex_dim")
        section = st.selectbox("Section", data.sections_for(dim), key=f"ex_section_{dim}")
        topics = data.topics_for(dim, section)
        topic = st.selectbox("Topic (specific area)", [data.ALL_TOPICS] + [t for t, _ in topics],
                             key=f"ex_topic_{dim}_{section}",
                             format_func=lambda t: "All topics" if t == data.ALL_TOPICS
                             else f"{t} ({dict(topics)[t]})")
        search = st.text_input("Search questions", key="ex_search", placeholder="e.g. saving, training, AI")
        kind = st.radio("Question type", ["All questions", "Rating scales (Likert)", "Choices & other"], key="ex_kind")
        seg = st.radio("Segment", ["all"] + list(SEGMENTS), key="ex_seg",
                       format_func=lambda s: "All segments" if s == "all" else NAMES[s])
    names = dict(NAMES) if seg == "all" else {seg: NAMES[seg]}
    qs = data.questions_for(dim, section)
    if topic != data.ALL_TOPICS:
        qs = [q for q in qs if data.topic_of(q) == topic]
    if search.strip():
        qs = [q for q in qs if search.strip().lower() in plots.question_title(q).lower()]
    if kind.startswith("Rating"):
        qs = [q for q in qs if plots.is_likert(q)]
    elif kind.startswith("Choices"):
        qs = [q for q in qs if not plots.is_likert(q)]
    with right:
        if dim == "Context" and section == data.sections_for("Context")[0] and not kind.startswith("Rating"):
            radar = plots.radar_chart(NUMS, names)
            if radar is not None:
                with st.container(border=True):
                    st.markdown("**Age, income and household profile by segment (highest segment = 100)**")
                    show_figure(radar, key=f"radar_{seg}")
        if not qs:
            st.info("No questions match these choices.")
        for q in qs:  # every question in the section, one after another down the page
            with st.container(border=True):
                st.markdown(f"**{plots.question_title(q)}**")
                show_figure(plots.question_chart(q, DISTS, NUMS, names), key=f"q_{q['code']}_{seg}")


def render_result(result: dict) -> None:
    seg = result["segment"]
    content = SEGMENT_CONTENT[seg]
    st.markdown(f"### You match {segment_pill(seg)}", unsafe_allow_html=True)
    st.markdown(f"**{content['headline']}**")
    show_figure(plots.probability_chart(result["probabilities"]), key="res_prob")
    st.markdown("##### Where you likely sit")
    st.markdown(bullets(content["where_they_sit"]), unsafe_allow_html=True)
    st.markdown("##### Your growth pathway - what would help you move on")
    st.markdown(bullets(content["what_would_help"]), unsafe_allow_html=True)
    show_figure(plots.pathway_stage_chart(STAGE_TABLE, seg, N_BY_SEGMENT.get(seg)), key="res_path")


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
    qs = questionnaire.QUESTIONS
    n = len(qs)
    st.header("Instructions to self assessment")
    st.markdown(
        f"1. This tool is for young people aged {AGE_MIN} to {AGE_MAX}.\n"
        f"2. You will answer {n} short questions, one at a time. Pick the answer that fits you best, then press **Next**.\n"
        "3. Made a mistake? Press **Back** to change an earlier answer. The progress bar shows how far along you are.\n"
        "4. On the last question, press **See my results**. A window opens showing the segment you most resemble, what "
        "that means and what could help you move forward. Press **Close** when you have finished reading.\n"
        "5. To read your result again, press **View my last result**."
    )
    st.session_state.setdefault("wiz_step", 0)
    st.session_state.setdefault("wiz_raw", {})  # question id -> numeric value, or option position for radios
    step = min(st.session_state["wiz_step"], n - 1)
    q = qs[step]
    raw = st.session_state["wiz_raw"]

    st.progress(step / n, text=f"{round(step / n * 100)}% complete ({step} of {n} answered)")
    st.caption(f"Question {step + 1} of {n}")
    if q["widget"] == "numeric":
        is_age = q["id"] == "A101"
        raw[q["id"]] = st.number_input(
            q["text"], min_value=0 if is_age else q.get("min"), max_value=120 if is_age else q.get("max"),
            value=int(raw.get(q["id"], q.get("value", 20))), step=1, key=f"w_{q['id']}")
        if is_age:
            st.caption(f"Ages {AGE_MIN}-{AGE_MAX} only.")
            if not AGE_MIN <= raw[q["id"]] <= AGE_MAX:
                st.error(AGE_MESSAGE)
    else:
        # Options are addressed by position: several questions map different answer labels to the same
        # model code, so a code-keyed dict would silently drop all but one of those labels.
        raw[q["id"]] = st.radio(q["text"], range(len(q["options"])), index=int(raw.get(q["id"], 0)),
                                format_func=lambda i, q=q: q["options"][i][0], key=f"w_{q['id']}")

    age_ok = AGE_MIN <= raw.get("A101", questionnaire.QUESTIONS[0].get("value", 23)) <= AGE_MAX
    back, nxt, _ = st.columns([1, 1, 4])
    if step > 0 and back.button("Back", key="wiz_back"):
        st.session_state["wiz_step"] = step - 1
        st.rerun()
    if step < n - 1:
        if nxt.button("Next", type="primary", key="wiz_next"):
            if q["id"] == "A101" and not age_ok:
                st.error(AGE_MESSAGE)
            else:
                st.session_state["wiz_step"] = step + 1
                st.rerun()
    elif nxt.button("See my results", type="primary", key="wiz_submit"):
        if not age_ok:
            st.error(AGE_MESSAGE)
        else:
            answers = {qq["id"]: (raw[qq["id"]] if qq["widget"] == "numeric"
                                  else qq["options"][int(raw.get(qq["id"], 0))][1]) for qq in qs}
            results_dialog(answers)
    if step == n - 1 and "assessment_result" in st.session_state and st.button("View my last result"):
        results_dialog(None)


pages = st.navigation(
    [
        st.Page(overview_page, title="OVERVIEW", url_path="overview", default=True),
        st.Page(segment_profiles_page, title="SEGMENT PROFILES", url_path="segment-profiles"),
        *([st.Page(deep_dives_page, title="DEEP DIVES", url_path="deep-dives")] if data.has_question_data() else []),
        st.Page(self_assessment_page, title="SELF ASSESSMENT", url_path="self-assessment"),
    ],
    position="top",
)
pages.run()
