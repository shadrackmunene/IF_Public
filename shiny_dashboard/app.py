"""Real Livelihoods Youth Segmentation dashboard (Python Shiny).

Three pages:
  1. Overview        - descriptive findings for the full sample (mirrors
                        Part 1 of the project's own deliverable deck).
  2. Segment Profiles - pick any of the 6 forced-drivers segments and see
                        its demographic/behavioural/psychographic profile
                        and where it sits on the HCD livelihood pathway.
  3. Self-Assessment  - answer the 12-item mini-questionnaire and see your
                        predicted segment, its profile, and the pathway
                        narrative that goes with it (same content segment
                        profiles uses, so a user and an analyst see the
                        same thing).

Run with:  shiny run --reload dashboard/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shiny import App, reactive, render, ui

import data
import plots
import questionnaire
from pathway_content import PERSONA_TAGLINES, SEGMENT_CONTENT
from theme import SEGMENT_COLORS

SEGMENTS = data.SEGMENTS
OVERVIEW = data.overview_stats()
SIZES = data.segment_sizes()
DRIVER_TABLE = data.segment_driver_table()
STAGE_TABLE = data.pathway_stage_table()


def _segment_pill(segment: str) -> ui.Tag:
    return ui.span(f"Segment {segment}", class_="segment-pill",
                   style=f"background-color:{SEGMENT_COLORS[segment]}")


def _value_box(title: str, value, subtitle: str = ""):
    return ui.value_box(title, value, subtitle, theme="text-dark", style="background-color:white;")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
overview_panel = ui.nav_panel(
    "Overview",
    ui.h2("Real Livelihoods Youth Segmentation Study"),
    ui.p(
        f"Descriptive findings across all {OVERVIEW['n_respondents']:,} respondents (Kenyan youth, 9 counties). "
        "Six segments identified via forced-drivers k-means clustering on 28 HCD-defined demographic, "
        "behavioural and psychographic drivers - see the Segment Profiles tab."
    ),
    ui.h4("Youth & household profile"),
    ui.layout_columns(
        _value_box("Median age", f"{OVERVIEW['median_age']:.0f}", "years (16-30 range)"),
        _value_box("Female", f"{OVERVIEW['pct_female']}%", f"Male: {100 - OVERVIEW['pct_female']:.1f}%"),
        _value_box("Independent household", f"{OVERVIEW['pct_own_household']}%", "live in own/rented household"),
        fill=False,
    ),
    ui.h4("Education & skills pathway"),
    ui.layout_columns(
        _value_box("Not currently enrolled", f"{OVERVIEW['pct_not_enrolled']}%", "in any education/training"),
        _value_box("Secondary (highest)", f"{OVERVIEW['pct_secondary_highest']}%", "completed KCSE as highest level"),
        _value_box("TVET/vocational", f"{OVERVIEW['pct_tvet']}%", "completed TVET training"),
        _value_box("University", f"{OVERVIEW['pct_university']}%", "completed a university degree"),
        fill=False,
    ),
    ui.h4("Current livelihoods"),
    ui.layout_columns(
        _value_box("Informal work", f"{OVERVIEW['pct_informal_main']}%", "of those currently working"),
        _value_box("Side activity", f"{OVERVIEW['pct_side_activity']}%", "have a supplementary income activity"),
        _value_box("Self-employed", f"{OVERVIEW['pct_self_employed']}%", "main activity is running a business"),
        fill=False,
    ),
    ui.h4("Income & financial security"),
    ui.layout_columns(
        _value_box("Median income", f"KES {OVERVIEW['median_income']:,.0f}", "per month, personal income"),
        _value_box("Currently saving", f"{OVERVIEW['pct_saving']}%", "saving money in any form"),
        _value_box("Bank account", f"{OVERVIEW['pct_bank_account']}%", "have a personal bank/financial account"),
        fill=False,
    ),
    ui.h4("Digital economy & AI"),
    ui.layout_columns(
        _value_box("Smartphone", f"{OVERVIEW['pct_smartphone']}%", "own a smartphone"),
        _value_box("Internet daily", f"{OVERVIEW['pct_internet_daily']}%", "access the internet daily"),
        _value_box("Mobile money daily", f"{OVERVIEW['pct_mobile_money_daily']}%", "use mobile money daily"),
        _value_box("Used an AI tool", f"{OVERVIEW['pct_used_ai']}%", "have ever used an AI tool"),
        fill=False,
    ),
    ui.h4("Six segments at a glance"),
    ui.output_plot("overview_segment_sizes", height="320px"),
)

segment_profiles_panel = ui.nav_panel(
    "Segment Profiles",
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Choose a segment"),
            ui.input_radio_buttons(
                "profile_segment", None,
                {s: f"Segment {s} ({SIZES.loc[SIZES.segment == s, 'pct'].iloc[0]}%)" for s in SEGMENTS},
                selected="1",
            ),
            width=280,
        ),
        ui.output_ui("segment_profile_header"),
        ui.navset_tab(
            ui.nav_panel("Demographic", ui.output_plot("profile_demographic_chart", height="420px")),
            ui.nav_panel("Behavioural", ui.output_plot("profile_behavioral_chart", height="420px")),
            ui.nav_panel("Psychographic", ui.output_plot("profile_psychographic_chart", height="420px")),
            ui.nav_panel(
                "Livelihood pathway",
                ui.output_plot("profile_pathway_chart", height="320px"),
                ui.output_ui("profile_pathway_text"),
            ),
        ),
    ),
)

_question_inputs = []
for q in questionnaire.QUESTIONS:
    if q["widget"] == "numeric":
        _question_inputs.append(ui.input_numeric(q["id"], q["text"], value=q.get("value", 20),
                                                  min=q.get("min"), max=q.get("max")))
    else:
        # Keyed by option position, not by model code: several questions map different
        # answer labels to the same code, and a code-keyed dict silently drops all but one.
        _question_inputs.append(
            ui.input_radio_buttons(q["id"], q["text"], {str(i): lbl for i, (lbl, _) in enumerate(q["options"])})
        )
    _question_inputs.append(ui.br())

self_assessment_panel = ui.nav_panel(
    "Self-Assessment",
    ui.row(
        ui.column(
            6,
            ui.h2("Find your segment"),
            ui.p(
                "Answer these 12 questions as honestly as you can. This uses the same statistical model "
                "built from the full survey's 28 drivers, reduced via LASSO regression to the most "
                "predictive short set (held-out accuracy 76.7%, 6 segments - see the Segment Profiles tab "
                "for what each one means)."
            ),
            *_question_inputs,
            ui.input_action_button("submit_assessment", "See my results", class_="btn-primary"),
        ),
        ui.column(6, ui.output_ui("assessment_results")),
    ),
)

_scroll_to_results_js = """
Shiny.addCustomMessageHandler("scroll_to_results", function(message) {
  // Small delay so this runs after Shiny finishes re-rendering the results
  // panel (the same button click that sends this message also triggers the
  // render.ui update) - scrolling immediately can race ahead of the new
  // content being in the DOM.
  setTimeout(function() {
    var el = document.getElementById("assessment_results");
    if (el) { el.scrollIntoView({behavior: "smooth", block: "start"}); }
  }, 150);
});
"""

app_ui = ui.page_navbar(
    overview_panel,
    segment_profiles_panel,
    self_assessment_panel,
    title="IF Real Livelihoods",
    header=ui.TagList(
        ui.include_css(Path(__file__).parent / "www" / "styles.css"),
        ui.tags.script(_scroll_to_results_js),
    ),
    fillable=False,
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):

    @render.plot
    def overview_segment_sizes():
        return plots.segment_size_chart(SIZES)

    @render.ui
    def segment_profile_header():
        seg = input.profile_segment()
        content = SEGMENT_CONTENT[seg]
        size_row = SIZES[SIZES.segment == seg].iloc[0]
        persona_line = (
            f"Closest HCD persona: <b>{content['hcd_persona']}</b> (fit {content['hcd_fit']}/100)"
            if content.get("hcd_persona")
            else content.get("hcd_note", "")
        )
        return ui.div(
            ui.h3(_segment_pill(seg), f"  {size_row['pct']}% of respondents (n={size_row['n']})"),
            ui.p(ui.strong(content["headline"])),
            ui.p(ui.HTML(persona_line), class_="text-muted"),
        )

    @render.plot
    def profile_demographic_chart():
        return plots.driver_bar_chart(DRIVER_TABLE, "Demographic", input.profile_segment())

    @render.plot
    def profile_behavioral_chart():
        return plots.driver_bar_chart(DRIVER_TABLE, "Behavioral", input.profile_segment())

    @render.plot
    def profile_psychographic_chart():
        return plots.driver_bar_chart(DRIVER_TABLE, "Psychographic", input.profile_segment())

    @render.plot
    def profile_pathway_chart():
        return plots.pathway_stage_chart(STAGE_TABLE, input.profile_segment())

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
        if input.submit_assessment() == 0:
            return ui.div(
                ui.p("Fill in the questions on the left and click “See my results”.", class_="text-muted"),
            )
        result = assessment_result()
        seg = result["segment"]
        content = SEGMENT_CONTENT[seg]
        persona_line = (
            f"Closest HCD persona: <b>{content['hcd_persona']}</b> "
            f"({PERSONA_TAGLINES.get(content['hcd_persona'], '')})"
            if content.get("hcd_persona")
            else content.get("hcd_note", "")
        )
        return ui.div(
            ui.div(
                ui.h3("You match ", _segment_pill(seg)),
                ui.p(ui.strong(content["headline"])),
                ui.p(ui.HTML(persona_line), class_="text-muted"),
                ui.output_plot("assessment_probability_chart", height="260px"),
                ui.h5("Where you likely sit"),
                ui.tags.ul(*[ui.tags.li(b) for b in content["where_they_sit"]], class_="pathway-bullet-list"),
                ui.h5("Your growth pathway - what would help you move on"),
                ui.tags.ul(*[ui.tags.li(b) for b in content["what_would_help"]], class_="pathway-bullet-list"),
                ui.output_plot("assessment_pathway_chart", height="300px"),
                class_="result-card",
            ),
        )

    @render.plot
    def assessment_probability_chart():
        return plots.probability_chart(assessment_result()["probabilities"])

    @render.plot
    def assessment_pathway_chart():
        return plots.pathway_stage_chart(STAGE_TABLE, assessment_result()["segment"])


app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
