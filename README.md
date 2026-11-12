# IF Public: Real Livelihoods Youth Segmentation dashboards

Public dashboards for the Real Livelihoods youth segmentation study (Kenya): six livelihood segments, each
with a profile and a growth pathway, plus a 12-question self-assessment that predicts which segment a person
most resembles.

| Folder | What it is | Run it |
|---|---|---|
| [`streamlit_dashboard/`](streamlit_dashboard) | Streamlit version (top navigation bar, results pop-up with a progress meter) | `pip install -r streamlit_dashboard/requirements.txt` then `streamlit run streamlit_dashboard/app.py` |
| [`shiny_dashboard/`](shiny_dashboard) | Python Shiny version (same content) | `pip install -r shiny_dashboard/requirements.txt` then `shiny run shiny_dashboard/app.py` |

Both pages show the same three views: **Overview** (headline statistics), **Segment Profiles** (demographic,
behavioural, psychographic drivers and the livelihood pathway for each segment) and **Self-Assessment**
(12 questions scored by a logistic-regression model).

## Data and models included

Each dashboard folder is self-contained, so either can be deployed on its own.

- `precomputed/*.json`: **aggregate-only** summary statistics (segment sizes, per-segment driver values,
  pathway-stage percentages, overview figures). These are what the charts are drawn from.
- `model/mini_questionnaire_model.joblib`: the fitted self-assessment model (a scikit-learn pipeline: encoder plus
  logistic regression, with its item list and class labels). It was fitted on the full labelled survey; the file
  holds model parameters, not survey records. Only load `.joblib` files from sources you trust.

## What is deliberately not here

- Respondent-level survey data, in any form (raw, clean, or segment assignments), and anything containing
  respondent identifiers.
- The 2019 Kenya Population and Housing Census 10% sample and anything derived record-by-record from it.
- The analysis pipeline that produced the aggregates (it lives in a private repository).

## Notes

- The pathway narratives and segment descriptions come from the study's deliverable deck.
- No license has been chosen yet; until one is added, all rights are reserved by default.
