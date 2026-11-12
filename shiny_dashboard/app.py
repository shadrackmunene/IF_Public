"""Youth Livelihoods dashboard (Python Shiny).

Four pages:
  OVERVIEW          - headline figures for all respondents, segment sizes and where respondents live.
  SEGMENT PROFILES  - pick a segment and see its profile, where it sits on the livelihood pathway, how many
                      young people it represents and where it is most prevalent.
  DEEP DIVES        - compare how the six segments answered survey questions, by dimension and section.
  SELF ASSESSMENT   - answer 12 short questions and find out which segment you most resemble.

Run with:  shiny run --reload shiny_dashboard/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shiny import App, reactive, render, ui

import data
import overview_cards
import plots

# Serve the Plotly.js build that matches the installed plotly package (generated at
# startup so it is never committed and the versions can't drift apart).
_plotly_js = Path(__file__).parent / "www" / "plotly.min.js"
_PLOTLY_SCRIPT = {"src": "plotly.min.js"}
if not _plotly_js.exists():
    try:
        from plotly.offline import get_plotlyjs
        _plotly_js.write_text(get_plotlyjs(), encoding="utf-8")
    except OSError:  # read-only deployment filesystem: load Plotly.js from a CDN instead
        _PLOTLY_SCRIPT = {"src": "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@3.0.1/plotly.min.js"}
import questionnaire
from pathway_content import SEGMENT_CONTENT
from theme import SEGMENT_NAMES, SEGMENT_PILL_COLORS

SEGMENTS = data.SEGMENTS
NAMES = data.segment_names() or SEGMENT_NAMES
OVERVIEW = data.overview_stats()
SIZES = data.segment_sizes()
DRIVER_TABLE = data.segment_driver_table()
STAGE_TABLE = data.pathway_stage_table()
N_BY_SEGMENT = {r.segment: int(r.n) for r in SIZES.itertuples()}
N_BY_SEGMENT["All"] = int(SIZES["n"].sum())

AGE_MIN, AGE_MAX = 18, 30
AGE_MESSAGE = (f"This tool is meant for young people aged {AGE_MIN} to {AGE_MAX}. "
               f"Please enter an age between {AGE_MIN} and {AGE_MAX}.")


def _segment_pill(segment: str) -> ui.Tag:
    return ui.span(NAMES.get(segment, segment), class_="segment-pill",
                   style=f"background-color:{SEGMENT_PILL_COLORS[segment]}")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
overview_panel = ui.nav_panel(
    "OVERVIEW",
    ui.h2("Real Livelihoods Youth Segmentation Study"),
    ui.p(
        f"Descriptive findings across all {OVERVIEW['n_respondents']:,} respondents (Kenyan youth, 9 counties). "
        "Six youth segments were identified from their demographics, behaviours and mindsets - "
        "see the Segment Profiles tab."
    ),
    *[ui.div(ui.h4(g["title"]), ui.HTML(overview_cards.cards_html(g["cards"], g["palette"])))
      for g in overview_cards.groups(OVERVIEW)],
    ui.h4("Six segments at a glance"),
    ui.output_ui("overview_segment_sizes"),
    ui.output_ui("overview_county_map"),
)

segment_profiles_panel = ui.nav_panel(
    "SEGMENT PROFILES",
    ui.row(
        ui.column(
            3,
            ui.div(
                ui.h4("Choose a segment"),
                ui.div(
                    ui.input_radio_buttons(
                        "profile_segment", None,
                        {s: f"{NAMES[s]} ({SIZES.loc[SIZES.segment == s, 'pct'].iloc[0]}%)" for s in SEGMENTS},
                        selected="1",
                    ),
                    class_="seg-choice",
                ),
                class_="sticky-side result-card",
            ),
        ),
        ui.column(
            9,
            ui.output_ui("segment_profile_header"),
            ui.div(
                ui.navset_tab(
                    ui.nav_panel("Demographic", ui.output_ui("profile_demographic_chart")),
                    ui.nav_panel("Behavioural", ui.output_ui("profile_behavioral_chart")),
                    ui.nav_panel("Psychographic", ui.output_ui("profile_psychographic_chart")),
                    ui.nav_panel(
                        "Livelihood pathway",
                        ui.output_ui("profile_pathway_chart"),
                        ui.output_ui("profile_pathway_text"),
                    ),
                ),
                class_="profile-tabs",
            ),
        ),
    ),
)

_question_steps = []
_N_Q = len(questionnaire.QUESTIONS)
for _i, q in enumerate(questionnaire.QUESTIONS):
    if q["widget"] == "numeric":
        _w = ui.TagList(
            ui.input_numeric(q["id"], q["text"], value=q.get("value", 20), min=q.get("min"), max=q.get("max")),
            ui.div(AGE_MESSAGE, id="age-error", class_="alert alert-danger", style="display:none")
            if q["id"] == "A101" else ui.div(),
        )
    else:
        # Keyed by option position, not by model code: several questions map different
        # answer labels to the same code, and a code-keyed dict silently drops all but one.
        _w = ui.input_radio_buttons(q["id"], q["text"], {str(i): lbl for i, (lbl, _) in enumerate(q["options"])})
    _question_steps.append(
        ui.div(
            ui.div(f"Question {_i + 1} of {_N_Q}", class_="q-counter"),
            _w,
            class_="q-step" + (" active" if _i == 0 else ""),
            **{"data-step": str(_i), "data-qid": q["id"]},
        )
    )

_wizard = ui.div(
    ui.div(
        ui.div(class_="progress-bar", id="wiz-bar", style="width: 0%"),
        class_="progress wiz-progress",
    ),
    ui.div("0% complete", id="wiz-pct", class_="wiz-pct"),
    ui.div(*_question_steps, class_="q-steps"),
    ui.div(
        ui.tags.button("Back", id="wiz-back", type="button", class_="btn btn-outline-secondary"),
        ui.tags.button("Next", id="wiz-next", type="button", class_="btn btn-primary"),
        ui.input_action_button("submit_assessment", "See my results", class_="btn-primary"),
        class_="wiz-nav",
    ),
    id="wizard",
    **{"data-total": str(_N_Q)},
)

self_assessment_panel = ui.nav_panel(
    "SELF ASSESSMENT",
    ui.row(
        ui.column(
            6,
            ui.h2("Instructions to self assessment"),
            ui.tags.ol(
                ui.tags.li(f"This tool is for young people aged {AGE_MIN} to {AGE_MAX}."),
                ui.tags.li(f"You will answer {_N_Q} short questions, one at a time. "
                           "Pick the answer that fits you best, then press Next."),
                ui.tags.li("Made a mistake? Press Back to change an earlier answer. "
                           "The progress bar shows how far along you are."),
                ui.tags.li("On the last question, press See my results. A window opens showing the segment you "
                           "most resemble, what that means and what could help you move forward. "
                           "Press Close when you have finished reading."),
                ui.tags.li("To read your result again, press View my results again."),
                class_="instruction-list",
            ),
            _wizard,
        ),
        ui.column(6, ui.output_ui("assessment_results")),
    ),
)

_DIMS = [d for d in data.DIMENSION_ORDER if data.sections_for(d)]

deep_dives_panel = ui.nav_panel(
    "DEEP DIVES",
    ui.row(
        ui.column(
            3,
            ui.div(
                ui.input_radio_buttons("ex_dim", "Dimension", _DIMS, selected=_DIMS[0] if _DIMS else None),
                ui.input_select("ex_section", "Section", data.sections_for(_DIMS[0]) if _DIMS else []),
                ui.input_select("ex_topic", "Topic (specific area)", {data.ALL_TOPICS: "All topics"}),
                ui.input_text("ex_search", "Search questions", placeholder="e.g. saving, training, AI"),
                ui.input_radio_buttons(
                    "ex_kind", "Question type",
                    {"all": "All questions", "likert": "Rating scales (Likert)", "other": "Choices & other"}),
                ui.div(
                    ui.input_radio_buttons(
                        "ex_seg", "Segment", {"all": "All segments", **{s: NAMES[s] for s in SEGMENTS}},
                        selected="all"),
                    class_="seg-choice seg-choice-all",
                ),
                class_="sticky-side result-card",
            ),
        ),
        ui.column(9, ui.output_ui("explore_charts")),
    ),
) if data.has_question_data() and _DIMS else None

_wizard_js = """
(function () {
  var cur = 0, shownAt = 0;
  var AGE_MIN = %(age_min)d, AGE_MAX = %(age_max)d;
  function steps() { return document.querySelectorAll("#wizard .q-step"); }
  function ageStepIndex() {
    var s = steps();
    for (var i = 0; i < s.length; i++) { if (s[i].dataset.qid === "A101") return i; }
    return -1;
  }
  function ageOk() {
    var el = document.getElementById("A101");
    if (!el) return true;
    var v = parseFloat(el.value);
    return !isNaN(v) && v >= AGE_MIN && v <= AGE_MAX;
  }
  function showAgeError(show) {
    var e = document.getElementById("age-error");
    if (e) e.style.display = show ? "block" : "none";
  }
  function render() {
    var s = steps(), n = s.length;
    if (!n) return;
    s.forEach(function (el, i) { el.classList.toggle("active", i === cur); });
    var pct = Math.round(cur / n * 100);
    document.getElementById("wiz-bar").style.width = pct + "%%";
    document.getElementById("wiz-pct").textContent = pct + "%% complete (" + cur + " of " + n + " answered)";
    document.getElementById("wiz-back").style.visibility = cur === 0 ? "hidden" : "visible";
    document.getElementById("wiz-next").style.display = cur === n - 1 ? "none" : "inline-block";
    document.getElementById("submit_assessment").style.display = cur === n - 1 ? "inline-block" : "none";
  }
  // Capture phase: runs before Shiny's own handler, so an out-of-range age never reaches the server.
  document.addEventListener("click", function (e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.id === "submit_assessment" && !ageOk()) {
      e.stopImmediatePropagation(); e.preventDefault();
      cur = Math.max(ageStepIndex(), 0); render(); showAgeError(true);
    }
  }, true);
  document.addEventListener("input", function (e) {
    if (e.target && e.target.id === "A101") showAgeError(!ageOk());
  });
  document.addEventListener("click", function (e) {
    var t = e.target.closest("button");
    if (!t) return;
    if (t.id === "wiz-next") {
      if (steps()[cur] && steps()[cur].dataset.qid === "A101" && !ageOk()) { showAgeError(true); return; }
      cur = Math.min(cur + 1, steps().length - 1); render();
    }
    else if (t.id === "wiz-back") { cur = Math.max(cur - 1, 0); render(); }
    else if (t.id === "submit_assessment") {
      document.getElementById("wiz-bar").style.width = "100%%";
      document.getElementById("wiz-pct").textContent = "100%% complete";
      shownAt = Date.now();
      document.getElementById("processing-overlay").classList.add("show");
    }
  });
  // Hide the overlay (after a ~1.2s minimum so it never just flashes).
  var hideTimer = null;
  function hideProcessing() {
    if (hideTimer) return;
    var wait = Math.max(0, 1200 - (Date.now() - shownAt));
    hideTimer = setTimeout(function () {
      document.getElementById("processing-overlay").classList.remove("show");
      hideTimer = null;
    }, wait);
  }
  // Primary signal: the results modal appears in the DOM. This does not depend
  // on a server message, so the overlay can never get stuck above the results.
  new MutationObserver(function (muts) {
    var ov = document.getElementById("processing-overlay");
    if (!ov || !ov.classList.contains("show")) return;
    if (document.querySelector(".modal.show, .modal.in, #shiny-modal")) hideProcessing();
  }).observe(document.body || document.documentElement, {childList: true, subtree: true, attributes: true, attributeFilter: ["class"]});
  // Failsafe: never keep the overlay up longer than 15s (e.g. if scoring errors).
  document.addEventListener("click", function (e) {
    if (e.target.closest("#submit_assessment")) {
      setTimeout(function () {
        document.getElementById("processing-overlay").classList.remove("show");
      }, 15000);
    }
  });
  // Secondary signal from the server (registered once Shiny exists).
  document.addEventListener("shiny:connected", function () {
    if (window.Shiny && Shiny.addCustomMessageHandler) {
      Shiny.addCustomMessageHandler("hide_processing", hideProcessing);
    }
    render();
  });
  document.addEventListener("DOMContentLoaded", render);
})();
""" % {"age_min": AGE_MIN, "age_max": AGE_MAX}

_processing_overlay = ui.div(
    ui.div(class_="spinner-border text-primary", role="status"),
    ui.div("Analysing your answers…", class_="processing-text"),
    id="processing-overlay",
)

app_ui = ui.page_navbar(
    overview_panel,
    segment_profiles_panel,
    *([deep_dives_panel] if deep_dives_panel is not None else []),
    self_assessment_panel,
    title="YOUTH LIVELIHOODS",
    header=ui.TagList(
        ui.include_css(Path(__file__).parent / "www" / "styles.css"),
        ui.tags.script(**_PLOTLY_SCRIPT),
        ui.tags.script(_wizard_js),
        _processing_overlay,
    ),
    fillable=False,
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def _card(title: str, html: str, **style) -> ui.Tag:
    return ui.div(ui.h6(title), ui.HTML(html), class_="result-card", style="margin-bottom:14px;padding:1rem")


def server(input, output, session):

    @render.ui
    def overview_segment_sizes():
        return ui.HTML(plots.to_html(plots.segment_size_chart(SIZES)))

    @render.ui
    def overview_county_map():
        counts = data.county_counts()
        if counts.empty:
            return ui.div()
        missed = plots.unmatched_counties(counts)
        return ui.div(
            ui.h4("Where respondents are"),
            ui.p("Bubble size shows the number of respondents in each county.", class_="text-muted"),
            ui.HTML(plots.to_html(plots.county_map(counts))),
            ui.p(f"Counties with fewer than {data.MIN_COUNTY_N} respondents are excluded from the map.",
                 class_="text-muted"),
            ui.p("Not shown on the map (name not recognised): " + ", ".join(missed), class_="text-muted")
            if missed else ui.div(),
        )

    # ---- Segment Profiles --------------------------------------------------
    @render.ui
    def segment_profile_header():
        seg = input.profile_segment()
        content = SEGMENT_CONTENT[seg]
        size_row = SIZES[SIZES.segment == seg].iloc[0]
        lines = [ui.p(ui.strong(content["headline"]))]
        pop = data.population_estimate(seg)
        if pop:
            lines.append(ui.p(f"Estimated {pop['n']:,} young people nationwide ({pop['pct']}% of {pop['total']:,}). "
                              "Directional sizing only: these are approximate values, modelled from census "
                              "records and predicted segments, not a headcount.", class_="text-muted",
                              title=pop["note"]))
        where = data.county_summary(seg)
        if where:
            lines.append(ui.p(where, class_="text-muted"))
        return ui.div(
            ui.h3(_segment_pill(seg), f"  {size_row['pct']}% of respondents (n={size_row['n']})"),
            *lines,
        )

    def _driver_block(category: str):
        seg = input.profile_segment()
        blocks = []
        for kind, title in (("pct", "Share of the segment"), ("score", "Average scores")):
            fig = plots.driver_bar_chart(DRIVER_TABLE, category, seg, kind, N_BY_SEGMENT)
            if fig is not None:
                blocks.append(_card(title, plots.to_html(fig)))
        return ui.div(*blocks)

    @render.ui
    def profile_demographic_chart():
        return _driver_block("Demographic")

    @render.ui
    def profile_behavioral_chart():
        return _driver_block("Behavioral")

    @render.ui
    def profile_psychographic_chart():
        return _driver_block("Psychographic")

    @render.ui
    def profile_pathway_chart():
        seg = input.profile_segment()
        return ui.HTML(plots.to_html(plots.pathway_stage_chart(STAGE_TABLE, seg, N_BY_SEGMENT.get(seg))))

    @render.ui
    def profile_pathway_text():
        content = SEGMENT_CONTENT[input.profile_segment()]
        return ui.div(
            ui.h5("Where they sit"),
            ui.tags.ul(*[ui.tags.li(b) for b in content["where_they_sit"]], class_="pathway-bullet-list"),
            ui.h5("What the survey says would help them move on"),
            ui.tags.ul(*[ui.tags.li(b) for b in content["what_would_help"]], class_="pathway-bullet-list"),
            ui.p(ui.em(content["hcd_link"]), class_="text-muted"),
        )

    # ---- Deep dives --------------------------------------------------------
    def _section():
        dim = input.ex_dim()
        secs = data.sections_for(dim)
        sec = input.ex_section()
        return dim, (sec if sec in secs else secs[0])  # input may still hold the previous dimension's section

    def _current_questions():
        dim, sec = _section()
        qs = data.questions_for(dim, sec)
        topic = input.ex_topic()
        if topic and topic != data.ALL_TOPICS and topic in [t for t, _ in data.topics_for(dim, sec)]:
            qs = [q for q in qs if data.topic_of(q) == topic]
        term = (input.ex_search() or "").strip().lower()
        if term:
            qs = [q for q in qs if term in plots.question_title(q).lower()]
        kind = input.ex_kind()
        if kind == "likert":
            return sec, [q for q in qs if plots.is_likert(q)]
        if kind == "other":
            return sec, [q for q in qs if not plots.is_likert(q)]
        return sec, qs

    @reactive.effect
    def _ex_update_sections():
        if not _DIMS:
            return
        ui.update_select("ex_section", choices=data.sections_for(input.ex_dim()))

    @reactive.effect
    def _ex_update_topics():
        if not _DIMS:
            return
        dim, sec = _section()
        ui.update_select("ex_topic", choices={
            data.ALL_TOPICS: "All topics", **{t: f"{t} ({n})" for t, n in data.topics_for(dim, sec)}})

    @render.ui
    def explore_charts():
        sec, qs = _current_questions()
        seg = input.ex_seg()
        names = dict(NAMES) if seg == "all" else {seg: NAMES[seg]}
        dists, nums = data.question_distributions(), data.numeric_summary()
        blocks = []
        # Spider web of the numeric profile measures (age, income, hours...) at the top of the first Context section
        if input.ex_dim() == "Context" and sec == data.sections_for("Context")[0] and input.ex_kind() != "likert":
            radar = plots.radar_chart(nums, names)
            if radar is not None:
                blocks.append(_card("Age, income and household profile by segment (highest segment = 100)",
                                    plots.to_html(radar)))
        for q in qs:  # every question in the section, one after another down the page
            blocks.append(_card(plots.question_title(q), plots.to_html(plots.question_chart(q, dists, nums, names))))
        if not qs:
            return ui.p("No questions match these choices.", class_="text-muted")
        return ui.div(*blocks)

    # ---- Self assessment ---------------------------------------------------
    def _age_ok() -> bool:
        age = input["A101"]()
        return age is not None and AGE_MIN <= age <= AGE_MAX

    @reactive.calc
    @reactive.event(input.submit_assessment)
    def assessment_result():
        answers = {}
        for q in questionnaire.QUESTIONS:
            raw = input[q["id"]]()
            if q["widget"] == "numeric":
                answers[q["id"]] = raw
            else:
                # radio buttons carry the option's position as a string - map back to
                # the typed option value (int/str/float as the question defines it).
                answers[q["id"]] = q["options"][int(raw)][1]
        return questionnaire.score(answers)

    @render.ui
    def assessment_results():
        if input.submit_assessment() == 0 or not _age_ok():
            return ui.div(
                ui.p("Answer the questions on the left and press See my results.", class_="text-muted"),
            )
        seg = assessment_result()["segment"]
        return ui.div(
            ui.h4("You match ", _segment_pill(seg)),
            ui.input_action_button("reopen_results", "View my results again", class_="btn-primary"),
            class_="result-card",
        )

    def _show_results_modal():
        result = assessment_result()
        seg = result["segment"]
        content = SEGMENT_CONTENT[seg]
        ui.modal_show(
            ui.modal(
                ui.h3("You match ", _segment_pill(seg)),
                ui.p(ui.strong(content["headline"])),
                ui.output_ui("assessment_probability_chart"),
                ui.h5("Where you likely sit"),
                ui.tags.ul(*[ui.tags.li(b) for b in content["where_they_sit"]], class_="pathway-bullet-list"),
                ui.h5("Your growth pathway - what would help you move on"),
                ui.tags.ul(*[ui.tags.li(b) for b in content["what_would_help"]], class_="pathway-bullet-list"),
                ui.output_ui("assessment_pathway_chart"),
                title="Your segment",
                size="l",
                easy_close=True,
                footer=ui.modal_button("Close"),
            )
        )

    @reactive.effect
    @reactive.event(input.submit_assessment)
    async def _open_results_modal():
        if not _age_ok():  # server-side guard in case the browser check was bypassed
            ui.notification_show(AGE_MESSAGE, type="error", duration=8)
            await session.send_custom_message("hide_processing", {})
            return
        _show_results_modal()
        await session.send_custom_message("hide_processing", {})

    @reactive.effect
    @reactive.event(input.reopen_results)
    def _reopen_results_modal():
        _show_results_modal()

    @render.ui
    def assessment_probability_chart():
        return ui.HTML(plots.to_html(plots.probability_chart(assessment_result()["probabilities"])))

    @render.ui
    def assessment_pathway_chart():
        seg = assessment_result()["segment"]
        return ui.HTML(plots.to_html(plots.pathway_stage_chart(STAGE_TABLE, seg, N_BY_SEGMENT.get(seg))))


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
