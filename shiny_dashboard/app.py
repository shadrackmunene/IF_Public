"""Youth Livelihoods dashboard (Python Shiny).

Six pages:
  OVERVIEW           - why the study was done, what was done, how to use the dashboard, the six segments in one
                       picture and a few headline figures.
  SEGMENTS OVERVIEW  - one card per segment (illustration, traits, size, key figures); click a card for the
                       segment's story, pathway and opportunity areas.
  SEGMENTS DATA      - "All segments" compares the six side by side; pick one segment to see its drivers and
                       pathway against all young people surveyed, in one scroll.
  DEEP DIVES         - every survey question by segment, by dimension and section.
  SELF ASSESSMENT    - answer 12 short questions and find out which segment you most resemble.
  METHODOLOGY        - study design, sample, segmentation and sizing method, definitions, caveats.

Run with:  shiny run --reload shiny_dashboard/app.py
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hashlib

import pandas as pd
from shiny import App, reactive, render, ui

import compare
import data
import methodology
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
from segment_content import ORDER, PATHWAY_STAGE_KEYS, SEGMENTS, STUDY
from theme import SEGMENT_COLORS, SEGMENT_NAMES, SEGMENT_PALETTES, SEGMENT_PILL_COLORS, r0

NAMES = SEGMENT_NAMES
OVERVIEW = data.overview_stats()
SIZES = data.segment_sizes()
DRIVER_TABLE = data.segment_driver_table()
STAGE_TABLE = data.pathway_stage_table()
N_BY_SEGMENT = {r.segment: int(r.n) for r in SIZES.itertuples()}
N_BY_SEGMENT["All"] = int(SIZES["n"].sum())

AGE_MIN, AGE_MAX = 18, 30
AGE_MESSAGE = (f"This tool is meant for young people aged {AGE_MIN} to {AGE_MAX}. "
               f"Please enter an age between {AGE_MIN} and {AGE_MAX}.")

TAB_OVERVIEW, TAB_SEGMENTS, TAB_DATA = "OVERVIEW", "SEGMENTS OVERVIEW", "SEGMENTS DATA"
TAB_DEEP, TAB_SELF, TAB_METHOD = "DEEP DIVES", "SELF ASSESSMENT", "METHODOLOGY"
TAB_COUNTIES = "COUNTIES"


def image_url(segment: str) -> str:
    """URL of a segment illustration, with a content hash so browsers fetch the new file when it is replaced."""
    name = SEGMENTS[segment]["image"]
    try:
        version = hashlib.md5((Path(__file__).parent / "www" / name).read_bytes()).hexdigest()[:8]
    except OSError:
        return quote(name)
    return f"{quote(name)}?v={version}"


def _segment_pill(segment: str) -> ui.Tag:
    return ui.span(NAMES.get(segment, segment), class_="segment-pill",
                   style=f"background-color:{SEGMENT_PILL_COLORS[segment]}")


def _seg_label(segment: str, suffix: str = "") -> ui.Tag:
    return ui.span(ui.span(class_="dot", style=f"background:{SEGMENT_COLORS[segment]}"), NAMES[segment] + suffix)


def _method_link(text: str = "Methodology") -> ui.Tag:
    """In-text link that switches to the Methodology tab (handled by the nav-jump click script)."""
    return ui.tags.a(text, href="#", class_="nav-jump method-link", **{"data-tab": TAB_METHOD})


def _chart_card(title: str, fig, subtitle=None) -> ui.Tag:
    return ui.div(ui.h6(title), ui.p(subtitle, class_="card-sub") if subtitle else None,
                  ui.HTML(plots.to_html(fig)), class_="result-card chart-card")


# ---------------------------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------------------------
_HOW_TO = [
    (TAB_SEGMENTS, "Meet the six segments: who they are, what drives them, and what could help them."),
    (TAB_DATA, "Compare the segments side by side, or look at one segment's data in detail."),
    (TAB_COUNTIES, "See where the young people surveyed live and the mix of segments in each county."),
    (TAB_DEEP, "Explore every survey question by segment."),
    (TAB_SELF, "Answer 12 questions to see which segment you are most like."),
    (TAB_METHOD, "How the study was done, definitions and caveats."),
]

overview_panel = ui.nav_panel(
    TAB_OVERVIEW,
    ui.div(
        ui.div("Imaginable Futures · Youth livelihood segmentation and pathways", class_="eyebrow"),
        ui.h1("Real Livelihoods of Kenyan Youth"),
        ui.p(STUDY["what"], class_="lead"),
        class_="hero",
    ),
    ui.h4("Six segments of Kenyan youth"),
    ui.row(
        ui.column(5, ui.div(ui.h6("Estimated share of young people aged 16 to 30"),
                            ui.output_ui("overview_donut"), class_="result-card chart-card")),
        ui.column(7, ui.div(
            *[ui.div(
                ui.img(src=image_url(s), alt="", class_="mini-img"),
                ui.div(ui.div(NAMES[s], class_="mini-name", style=f"color:{SEGMENT_PALETTES[s][0]}"),
                       ui.div(SEGMENTS[s]["tagline"], class_="mini-tag")),
                ui.div(SEGMENTS[s]["stats"]["population"], class_="mini-pop"),
                class_="mini-row seg-link", **{"data-seg": s, "role": "button", "tabindex": "0"},
            ) for s in ORDER],
            class_="mini-list",
        )),
    ),
    ui.h4("Why this study"),
    ui.div(*[ui.div(ui.h6(t), ui.p(d), class_="why-card") for t, d in STUDY["why"]], class_="why-grid"),
    ui.h4("How to use this dashboard"),
    ui.div(*[ui.div(ui.tags.button(t.title(), class_="btn btn-outline-primary nav-jump", **{"data-tab": t}),
                    ui.span(d), class_="howto-row") for t, d in _HOW_TO], class_="howto"),
    ui.h4("The young people surveyed at a glance"),
    *[ui.div(ui.h6(g["title"], class_="group-title"), ui.HTML(overview_cards.cards_html(g["cards"], g["palette"])))
      for g in overview_cards.groups(OVERVIEW)],
    ui.p(f"Figures describe the {OVERVIEW['n_respondents']:,} young people surveyed in nine counties and are not "
         "weighted to the national population. See ", _method_link(), ".", class_="footnote"),
)

# ---------------------------------------------------------------------------
# SEGMENTS OVERVIEW
# ---------------------------------------------------------------------------
def _segment_card(s: str) -> ui.Tag:
    c, st = SEGMENTS[s], SEGMENTS[s]["stats"]
    dark, mid, _, light = SEGMENT_PALETTES[s]
    return ui.div(
        ui.div(ui.img(src=image_url(s), alt=f"{NAMES[s]} illustration"), class_="seg-card-img",
               style=f"background:{light}"),
        ui.div(
            ui.div(f"Segment {c['number']}", class_="seg-num", style=f"color:{dark}"),
            ui.h5(NAMES[s], style=f"color:{dark}"),
            ui.div(*[ui.span(t, class_="trait", style=f"background:{light};color:{dark}") for t in c["traits"]],
                   class_="traits"),
            ui.p(c["tagline"], class_="seg-tagline"),
            ui.div(
                ui.div(ui.tags.b(st["population"]), ui.span(f"young people ({st['share']})"), class_="kv"),
                ui.div(ui.tags.b(st["median_age"]), ui.span("median age"), class_="kv"),
                ui.div(ui.tags.b(st["women"]), ui.span("women"), class_="kv"),
                ui.div(ui.tags.b(st["median_income"]), ui.span("median monthly income"), class_="kv"),
                class_="kv-grid",
            ),
            ui.div("Read their story →", class_="seg-more", style=f"color:{dark}"),
            class_="seg-card-body",
        ),
        class_="seg-card",
        style=f"--seg:{mid}",
        **{"data-seg": s, "role": "button", "tabindex": "0", "aria-label": f"Show {NAMES[s]}", "aria-haspopup": "dialog"},
    )


segments_panel = ui.nav_panel(
    TAB_SEGMENTS,
    ui.h2("Six segments of Kenyan youth"),
    ui.p("Each segment is a group of young people who share circumstances, behaviours and mindsets. They are numbered "
         "as in the study report, broadly from those who most need help to establish a livelihood to those who most "
         "need help to progress. Click a segment to read its story, its pathway and what could help.", class_="lead-sm"),
    ui.div(*[_segment_card(s) for s in ORDER], class_="seg-grid"),
)

# ---------------------------------------------------------------------------
# SEGMENTS DATA
# ---------------------------------------------------------------------------
segment_data_panel = ui.nav_panel(
    TAB_DATA,
    ui.row(
        ui.column(
            3,
            ui.div(
                ui.h4("Show"),
                ui.div(
                    ui.input_radio_buttons(
                        "data_seg", None,
                        {"all": ui.span(ui.span(class_="dot all"), ui.tags.b("All segments (compare)")),
                         **{s: _seg_label(s) for s in ORDER}},
                        selected="all",
                    ),
                    class_="seg-choice",
                ),
                ui.p("▲ / ▼ mark where a segment is the highest / lowest of the six.", class_="text-muted small"),
                class_="sticky-side result-card",
            ),
        ),
        ui.column(9, ui.output_ui("data_view")),
    ),
)

# ---------------------------------------------------------------------------
# SELF ASSESSMENT
# ---------------------------------------------------------------------------
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
    TAB_SELF,
    ui.row(
        ui.column(
            6,
            ui.h2("Which segment are you most like?"),
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

# ---------------------------------------------------------------------------
# DEEP DIVES
# ---------------------------------------------------------------------------
_DIMS = [d for d in data.DIMENSION_ORDER if data.sections_for(d)]

deep_dives_panel = ui.nav_panel(
    TAB_DEEP,
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
                        "ex_seg", "Segment",
                        {"all": ui.span(ui.span(class_="dot all"), "All segments"), **{s: _seg_label(s) for s in ORDER}},
                        selected="all"),
                    class_="seg-choice",
                ),
                class_="sticky-side result-card",
            ),
        ),
        ui.column(9, ui.output_ui("explore_charts")),
    ),
) if data.has_question_data() and _DIMS else None

# ---------------------------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------------------------
def _method_sections() -> list[ui.Tag]:
    out = []
    for sec in methodology.SECTIONS:
        out.append(ui.div(
            ui.h4(sec["title"]),
            *[ui.p(p) for p in sec.get("paras", [])],
            ui.tags.ul(*[ui.tags.li(b) for b in sec.get("bullets", [])]) if sec.get("bullets") else None,
            class_="method-section",
        ))
    rows = "".join(f"<tr><td>{escape(c)}</td><th scope='row'>{escape(n)}</th><td>{escape(d)}</td><td>{escape(t)}</td></tr>"
                   for c, n, d, t in methodology.DRIVER_DEFINITIONS)
    out.append(ui.div(
        ui.h4("Driver definitions"),
        ui.HTML('<div class="table-scroll"><table class="cmp-table defs"><thead><tr><th>Group</th><th>Driver</th>'
                f"<th>Definition</th><th>Measure</th></tr></thead><tbody>{rows}</tbody></table></div>"),
        ui.p("Direct: the survey question matches the HCD definition. Proxy: the closest available question.",
             class_="footnote"),
        class_="method-section",
    ))
    return out


# ---------------------------------------------------------------------------
# COUNTIES
# ---------------------------------------------------------------------------
counties_panel = ui.nav_panel(
    TAB_COUNTIES,
    ui.h2("Segments by county"),
    ui.p("Where the young people surveyed live and the mix of segments in each of the nine counties. Counties were "
         "sampled, not nationally representative, so compare counties with each other rather than reading a figure "
         "as the county's population.", class_="lead-sm"),
    ui.div(
        ui.div(
            ui.output_ui("county_map_title"),
            ui.input_select("county_shade", "Shade counties by",
                            {"n": "Number of young people surveyed",
                             **{s: f"{NAMES[s]} (share)" for s in ORDER}}, selected="n"),
            class_="map-head",
        ),
        ui.p("Grey counties were not surveyed. Hover over a county for its figures.", class_="card-sub"),
        ui.output_ui("county_map"),
        ui.p("County boundaries: geoBoundaries (RCMRD GeoPortal, 2020), public domain.", class_="footnote"),
        class_="result-card chart-card",
    ),
    ui.output_ui("county_mix_chart"),
    ui.h5("Share of each county's respondents in each segment"),
    ui.p("Darker cells are higher within each segment (column). ▲ marks the county where the segment is most common.",
         class_="text-muted"),
    ui.output_ui("county_table"),
    ui.p(f"– : fewer than {data.MIN_COUNTY_N} respondents in that county and segment, not shown. Counties with fewer "
         "than 15 respondents are not ranked.", class_="footnote"),
)

method_panel = ui.nav_panel(
    TAB_METHOD,
    ui.h2("Methodology and technical notes"),
    ui.p("How the study was designed, how the segments and size estimates were produced, and how to read the "
         "figures on this dashboard.", class_="lead-sm"),
    *_method_sections(),
    ui.h4("Survey sample"),
    ui.row(
        ui.column(6, ui.output_ui("method_sample_chart")),
        ui.column(6, ui.output_ui("method_county_map")),
    ),
)

# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
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

# Segment cards / links and "jump to tab" buttons: tell the server which segment or tab was chosen.
_nav_js = """
(function () {
  function pickCard(seg) {
    document.querySelectorAll(".seg-card").forEach(function (c) { c.classList.toggle("selected", c.dataset.seg === seg); });
  }
  function act(el) {
    if (!window.Shiny || !Shiny.setInputValue) return;
    if (el.classList.contains("seg-card")) {
      pickCard(el.dataset.seg);
      Shiny.setInputValue("card_seg", el.dataset.seg, {priority: "event"});  // server opens the segment pop-up
    } else if (el.classList.contains("seg-link")) {
      pickCard(el.dataset.seg);
      Shiny.setInputValue("goto_segment", el.dataset.seg, {priority: "event"});
    } else if (el.classList.contains("nav-jump")) {
      Shiny.setInputValue("goto_tab", el.dataset.tab, {priority: "event"});
    } else if (el.classList.contains("data-jump")) {
      Shiny.setInputValue("goto_data", el.dataset.seg, {priority: "event"});
    }
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest(".seg-card, .seg-link, .nav-jump, .data-jump");
    if (el) {
      if (el.tagName === "A") e.preventDefault();  // in-text links such as "See Methodology" switch tabs, not jump to #
      act(el);
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var el = e.target.closest && e.target.closest(".seg-card, .seg-link");
    if (el) { e.preventDefault(); act(el); }
  });
})();
"""

_processing_overlay = ui.div(
    ui.div(class_="spinner-border text-primary", role="status"),
    ui.div("Analysing your answers…", class_="processing-text"),
    id="processing-overlay",
)

app_ui = ui.page_navbar(
    overview_panel,
    segments_panel,
    segment_data_panel,
    counties_panel,
    *([deep_dives_panel] if deep_dives_panel is not None else []),
    self_assessment_panel,
    method_panel,
    id="main_nav",
    title="YOUTH LIVELIHOODS",
    header=ui.TagList(
        ui.include_css(Path(__file__).parent / "www" / "styles.css"),
        ui.tags.script(**_PLOTLY_SCRIPT),
        ui.tags.script(_wizard_js),
        ui.tags.script(_nav_js),
        _processing_overlay,
    ),
    fillable=False,
)


# ---------------------------------------------------------------------------
# Shared segment blocks
# ---------------------------------------------------------------------------
def _stat_chips(s: str) -> ui.Tag:
    st = SEGMENTS[s]["stats"]
    items = [(st["population"], f"young people in Kenya ({st['share']})"), (st["median_age"], "median age"),
             (st["women"], "women"), (st["rural"], "live in rural areas"),
             (st["median_income"], "median monthly income")]
    return ui.div(*[ui.div(ui.tags.b(v), ui.span(l), class_="chip-stat") for v, l in items], class_="chip-stats")


def _segment_header(s: str, compact: bool = False) -> ui.Tag:
    c = SEGMENTS[s]
    dark, _, _, light = SEGMENT_PALETTES[s]
    return ui.div(
        ui.img(src=image_url(s), alt="", class_="hdr-img"),
        ui.div(
            ui.div(f"Segment {c['number']}", class_="seg-num", style=f"color:{dark}"),
            ui.h3(NAMES[s], style=f"color:{dark}"),
            ui.div(*[ui.span(t, class_="trait", style=f"background:{light};color:{dark}") for t in c["traits"]],
                   class_="traits"),
            ui.p(c["insight"], class_="insight"),
            _stat_chips(s) if not compact else None,
        ),
        class_="seg-header",
        style=f"border-left:6px solid {dark}",
    )


def _pathway_block(s: str) -> ui.Tag:
    c = SEGMENTS[s]
    steps = [ui.div(ui.div(label, class_="stage-name"), ui.div(c["aspirations"][k], class_="stage-asp"),
                    class_="stage")
             for k, label in PATHWAY_STAGE_KEYS if k in c["aspirations"]]
    return ui.div(ui.p(c["pathway_summary"]), ui.div(*steps, class_="stages"))


def _opportunities_block(s: str) -> ui.Tag:
    themes: dict[str, list] = {}
    for theme, title, desc in SEGMENTS[s]["opportunities"]:
        themes.setdefault(theme, []).append((title, desc))
    return ui.div(*[ui.div(ui.div(theme, class_="opp-theme"),
                           *[ui.div(ui.tags.b(t), ui.p(d), class_="opp") for t, d in items], class_="opp-col")
                    for theme, items in themes.items()], class_="opp-grid")


def _technical_footnote(s: str) -> ui.Tag:
    size = SIZES[SIZES.segment == s].iloc[0]
    lines = [f"Survey: {int(size['n'])} of the {N_BY_SEGMENT['All']:,} young people surveyed "
             f"({r0(size['pct'])}%) are in this segment."]
    pop = data.population_estimate(s)
    if pop:
        lines.append(f"National estimate: about {pop['n'] / 1e6:.1f} million young people ({r0(pop['pct'])}% of "
                     f"about {pop['total'] / 1e6:.1f} million aged 16-30), "
                     "a directional, census-based model estimate, not a headcount.")
    where = data.county_summary(s)
    if where:
        lines.append(where.replace("Most prevalent in", "Among the counties surveyed, most common in"))
    return ui.div(ui.h6("Technical notes"), *[ui.p(l) for l in lines], class_="footnote-box")


def _card(title: str, html: str, **style) -> ui.Tag:
    return ui.div(ui.h6(title), ui.HTML(html), class_="result-card", style="margin-bottom:14px;padding:1rem")


# ---------------------------------------------------------------------------
# Counties tab builders
# ---------------------------------------------------------------------------
def _county_map_fig(shade: str):
    """County map shaded by respondents ("n") or by one segment's share of each county's respondents."""
    if shade not in SEGMENTS:
        return plots.county_map(data.county_counts())
    prev = data.county_prevalence()
    sub = prev[prev["segment"] == shade]
    rows = pd.DataFrame({
        "county": sub["county"], "value": sub["pct_of_county"],
        "hover": [f"<b>{r.county}</b><br>{NAMES[shade]}: {r.pct_of_county:.0f}% of the young people surveyed "
                  f"here ({r.n} of {r.n_county})" for r in sub.itertuples()],
    })
    dark, _, _, light = SEGMENT_PALETTES[shade]
    return plots.county_choropleth(
        rows, colors=(light, dark), title="% of county", suffix="%",
        grey_hover=f"Not surveyed, or fewer than {data.MIN_COUNTY_N} {NAMES[shade]} respondents")


def _county_table() -> ui.Tag:
    """County x segment shares, shaded within each segment's column; ▲ marks the county where it is most common."""
    prev = data.county_prevalence()
    totals = prev.groupby("county")["n_county"].first().sort_values(ascending=False)
    ranked = prev[prev["n_county"] >= 15]
    head = ui.tags.tr(ui.tags.th("County"), ui.tags.th("n", class_="num"), *[ui.tags.th(_seg_label(s)) for s in ORDER])
    body = []
    for county, n in totals.items():
        cells = []
        for s in ORDER:
            col = ranked[ranked["segment"] == s]["pct_of_county"]
            row = prev[(prev["county"] == county) & (prev["segment"] == s)]
            if row.empty:
                cells.append(ui.tags.td("–", class_="text-muted"))
                continue
            v = float(row["pct_of_county"].iloc[0])
            lo, hi = (float(col.min()), float(col.max())) if len(col) else (v, v)
            t = (v - lo) / (hi - lo) if hi > lo else 0.0
            alpha = 0.06 + 0.6 * max(0.0, min(1.0, t))
            mark = ui.span(" ▲", class_="mk") if v == hi and n >= 15 else None
            cells.append(ui.tags.td(f"{v:.0f}%", mark, style=f"background:rgba(15,107,82,{alpha:.2f});"
                                    + ("color:#fff;" if alpha > 0.5 else "")))
        body.append(ui.tags.tr(ui.tags.th(county, scope="row"), ui.tags.td(int(n), class_="num"), *cells))
    return ui.div(ui.tags.table(ui.tags.thead(head), ui.tags.tbody(*body), class_="cmp-table heat"),
                  class_="table-scroll")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):

    # ---- Navigation between tabs -------------------------------------------
    @reactive.effect
    @reactive.event(input.card_seg)
    def _pick_card():
        _show_segment_modal(input.card_seg())

    @reactive.effect
    @reactive.event(input.goto_segment)
    def _goto_segment():
        ui.update_navset("main_nav", selected=TAB_SEGMENTS)
        _show_segment_modal(input.goto_segment())

    @reactive.effect
    @reactive.event(input.goto_tab)
    def _goto_tab():
        ui.modal_remove()  # in case the link was clicked inside a pop-up
        ui.update_navset("main_nav", selected=input.goto_tab())

    @reactive.effect
    @reactive.event(input.goto_data)
    def _goto_data():
        ui.modal_remove()  # the "See the data" button sits inside the segment pop-up
        ui.update_radio_buttons("data_seg", selected=input.goto_data())
        ui.update_navset("main_nav", selected=TAB_DATA)

    # ---- Overview ----------------------------------------------------------
    @render.ui
    def overview_donut():
        return ui.HTML(plots.to_html(plots.segment_share_donut(data.population(), SIZES)))

    # ---- Segments overview -------------------------------------------------
    def _show_segment_modal(s: str):
        """The segment's story, pathway and opportunity areas in a pop-up window (× and Close), like the
        self-assessment results."""
        if s not in SEGMENTS:
            return
        ui.modal_show(
            ui.modal(
                _segment_detail(s),
                title=ui.TagList(
                    ui.span(f"Segment {SEGMENTS[s]['number']}: {NAMES[s]}"),
                    ui.tags.button("×", type="button", class_="modal-x", data_bs_dismiss="modal", aria_label="Close"),
                ),
                size="xl",
                easy_close=True,
                footer=ui.modal_button("Close"),
            )
        )

    def _segment_detail(s: str) -> ui.Tag:
        c = SEGMENTS[s]
        dark = SEGMENT_PALETTES[s][0]
        return ui.div(
            _segment_header(s),
            ui.row(
                ui.column(7,
                          ui.h5("Who they are"), *[ui.p(p) for p in c["narrative"]],
                          ui.tags.blockquote(f"“{c['quote']}”", class_="quote", style=f"border-color:{dark}")),
                ui.column(5,
                          ui.div(ui.h6("What helps them"), ui.tags.ul(*[ui.tags.li(e) for e in c["enablers"]]),
                                 class_="eb enablers"),
                          ui.div(ui.h6("What holds them back"), ui.tags.ul(*[ui.tags.li(b) for b in c["barriers"]]),
                                 class_="eb barriers")),
            ),
            ui.h5("Their livelihood pathway"),
            _pathway_block(s),
            ui.h5("Opportunity areas"),
            ui.p("Where programmes and partners could make the most difference for this segment.", class_="text-muted"),
            _opportunities_block(s),
            ui.div(ui.tags.button(f"See the data for {NAMES[s]} →", class_="btn btn-primary data-jump",
                                  **{"data-seg": s}), class_="detail-actions"),
            class_="segment-detail in-modal",
        )

    # ---- Segments data -----------------------------------------------------
    def _all_view() -> ui.Tag:
        return ui.div(
            ui.h3("All segments compared"),
            ui.p("The segments differ most in how they learned their skills, how they find work and what work means "
                 "to them. Survival Workers and Stability Seekers rely almost entirely on family and friends for work; "
                 "Career Pursuers find work through applications and professional contacts; Skill Investors are the "
                 "only group for whom work is mainly part of who they are rather than a means to an end.", class_="insight"),
            ui.h5("At a glance"),
            ui.HTML(compare.segment_compare_html(image_url)),
            ui.h5("Livelihood pathway"),
            _chart_card("Share of each segment that has reached each stage of the pathway",
                        plots.pathway_compare_chart(STAGE_TABLE, N_BY_SEGMENT),
                        ui.TagList("The grey line shows all young people surveyed. Stage definitions are on the ",
                                   _method_link("Methodology tab"), ".")),
            ui.h5("Segmentation drivers across the six segments"),
            ui.p("Darker cells are higher values within each row. ▲ marks the highest segment, ▼ the lowest.",
                 class_="text-muted"),
            ui.HTML(compare.driver_heatmap_html(DRIVER_TABLE)),
            ui.p("Estimates of national size are directional, census-based model estimates; all other figures "
                 "describe the young people surveyed and are not weighted. See ", _method_link(), ".", class_="footnote"),
        )

    def _segment_view(s: str) -> ui.Tag:
        cards = []
        for cat, title in (("Demographic", "Demographic"), ("Behavioral", "Behavioural"),
                           ("Psychographic", "Psychometric")):
            for kind, sub in (("pct", "share of the segment"), ("score", "averages")):
                fig = plots.driver_bar_chart(DRIVER_TABLE, cat, s, kind, N_BY_SEGMENT)
                if fig is not None:
                    cards.append(_chart_card(f"{title}: {sub}", fig))
        pathway_card = ui.div(
            ui.h6("Livelihood pathway: share who have reached each stage"),
            ui.HTML(plots.to_html(plots.pathway_stage_chart(STAGE_TABLE, s, N_BY_SEGMENT))),
            ui.p(SEGMENTS[s]["pathway_summary"], class_="small"),
            class_="result-card chart-card wide",
        )
        survey = SEGMENT_CONTENT[s]
        return ui.div(
            _segment_header(s),
            ui.h5("What sets them apart in the data"),
            ui.HTML(compare.defining_drivers_html(DRIVER_TABLE, s)),
            ui.div(*cards, pathway_card, class_="chart-grid"),
            ui.div(
                ui.h5("What the survey says about their next step"),
                ui.tags.ul(*[ui.tags.li(b) for b in survey["what_would_help"]], class_="pathway-bullet-list"),
                class_="result-card",
            ),
            _technical_footnote(s),
        )

    @render.ui
    def data_view():
        s = input.data_seg()
        return _all_view() if s == "all" else _segment_view(s)

    # ---- Counties ----------------------------------------------------------
    @render.ui
    def county_map_title():
        s = input.county_shade()
        what = "young people surveyed" if s == "n" else f"share of respondents who are {NAMES[s]}"
        return ui.h6(f"Kenya's counties: {what}")

    @render.ui
    def county_map():
        return ui.HTML(plots.to_html(_county_map_fig(input.county_shade())))

    @render.ui
    def county_mix_chart():
        return _chart_card("Segment mix of the young people surveyed, by county",
                           plots.county_segment_mix(data.county_prevalence(), SIZES))

    @render.ui
    def county_table():
        return _county_table()

    # ---- Methodology -------------------------------------------------------
    @render.ui
    def method_sample_chart():
        return _chart_card("Young people surveyed, by segment", plots.segment_size_chart(SIZES))

    @render.ui
    def method_county_map():
        counts = data.county_counts()
        if counts.empty:
            return ui.div()
        missed = plots.unmatched_counties(counts)
        return ui.div(
            ui.h6("Where the young people surveyed live"),
            ui.p("Darker counties had more young people surveyed; grey counties were not surveyed.", class_="card-sub"),
            ui.HTML(plots.to_html(plots.county_map(counts))),
            ui.p("Not shown on the map (name not recognised): " + ", ".join(missed), class_="footnote")
            if missed else None,
            class_="result-card chart-card",
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
        ui.modal_show(
            ui.modal(
                _segment_header(seg, compact=True),
                ui.h5("How closely you match each segment"),
                ui.output_ui("assessment_probability_chart"),
                ui.h5("The pathway for young people like you"),
                _pathway_block(seg),
                ui.h5("What could help you move forward"),
                ui.tags.ul(*[ui.tags.li(ui.tags.b(t), f": {d}") for _, t, d in SEGMENTS[seg]["opportunities"][:5]],
                           class_="pathway-bullet-list"),
                ui.output_ui("assessment_pathway_chart"),
                # Title row with a top-right close (x) button, as on the Next.js dashboard.
                title=ui.TagList(
                    ui.span("Your segment"),
                    ui.tags.button("×", type="button", class_="modal-x", data_bs_dismiss="modal",
                                   aria_label="Close"),
                ),
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
        return ui.HTML(plots.to_html(plots.pathway_stage_chart(STAGE_TABLE, seg, N_BY_SEGMENT)))


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
