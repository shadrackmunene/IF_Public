# IF Public: Real Livelihoods Youth Segmentation dashboards

Public dashboards for the Real Livelihoods youth segmentation study (Kenya): six livelihood segments, each
with a profile and a growth pathway, plus a 12-question self-assessment that predicts which segment a person
most resembles.

| Folder | What it is | Run it |
|---|---|---|
| [`shiny_dashboard/`](shiny_dashboard) | Python Shiny version | `pip install -r shiny_dashboard/requirements.txt` then `shiny run shiny_dashboard/app.py` |
| [`nextjs_dashboard/`](nextjs_dashboard) | Static Next.js version (same content, no server) | `cd nextjs_dashboard && npm install && npm run dev` |

Both show the same six tabs:

- **Overview**: why the study was done, what was done, how to use the dashboard, the six segments in one picture
  and a few headline figures.
- **Segments overview**: one card per segment (illustration, traits, size, key figures); click a card for the
  segment's story, quote, enablers and barriers, pathway and opportunity areas.
- **Segments data**: "All segments" compares the six side by side (profile table, pathway, shaded driver table);
  choosing one segment shows its drivers and pathway against all young people surveyed in one scroll.
- **Deep dives**: every survey question by segment.
- **Self assessment**: 12 questions scored by a logistic-regression model.
- **Methodology**: study design, sample, segmentation and sizing method, definitions, caveats.

Segment codes in the data files are the analysis codes, which differ from the report's numbering:
1 Survival Workers, 2 Income Pragmatists, 3 Skill Investors, 4 Stability Seekers, 5 Credentialed Aspirants,
6 Career Pursuers. The written content (from the client report) lives in `shiny_dashboard/segment_content.py` and
`shiny_dashboard/methodology.py`; `scripts/export_nextjs_data.py` copies it, the data and the segment illustrations
into the Next.js app.

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

- The segment descriptions, pathways and opportunity areas come from the client report
  ("IF - Real Livelihoods Project Segmentation Report - V1", Nov 2026).
- `shiny_dashboard/.env` holds deployment credentials; it is git-ignored and must never be committed.
- No license has been chosen yet; until one is added, all rights are reserved by default.

## Data files the dashboards read (aggregate-only, safe to publish)

Each app reads its own `precomputed/` folder, so the folder deploys on its own with no extra steps:
`overview_stats`, `segment_sizes`, `segment_driver_table`, `pathway_stage_table`, `question_catalog`,
`question_distributions`, `numeric_summary`, `segment_names`, `question_short_labels` and `county_counts` (all `.json`).

- `overview_stats`, `segment_sizes`, `segment_driver_table` and `pathway_stage_table` are built in the private
  analysis repository by `scripts/precompute_dashboard_data.py`, which now writes straight into
  `shiny_dashboard/precomputed/` here.
- `scripts/aggregate_for_dashboard.py` builds the question, segment and county files from the segmented survey
  file (run it where that file is held; it never writes respondent rows, IDs or sub-county locations).
- `scripts/build_short_labels.py` rebuilds the short question titles from `question_catalog.json`.
- Never commit the respondent-level file (`data/` and `*.csv|*.sav|*.parquet` are in `.gitignore`).
