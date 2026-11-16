# Youth Livelihoods dashboard (Next.js)

The same six pages as the Shiny dashboard, built as a **static site**: no Python server runs when someone opens
it, so it loads fast, never "sleeps", and can be hosted free.

| Tab | Route | What it shows |
|---|---|---|
| OVERVIEW | `/` | Why and how the study was done, how to use the dashboard, the six segments (donut + list), headline figures |
| SEGMENTS OVERVIEW | `/segments/` | A card per segment; click for its story, quote, enablers/barriers, pathway and opportunity areas (`?seg=3` opens one) |
| SEGMENTS DATA | `/profiles/` | "All segments" comparison (profile table, pathway, shaded driver table) or one segment's drivers and pathway vs all surveyed (`?seg=3`) |
| DEEP DIVES | `/deep-dives/` | Every survey question by segment; single-choice questions with up to six answers are shown as pies |
| SELF ASSESSMENT | `/self-assessment/` | 12 questions, one at a time; scored in the browser against the saved model |
| METHODOLOGY | `/methodology/` | Study design, sample, segmentation and sizing method, driver definitions, caveats |

Segment illustrations live in `public/images/segments/` (copied from `shiny_dashboard/www/` by the export script).

## Run it

```bash
cd nextjs_dashboard
npm install
npm run dev          # http://localhost:3000
```

## Build and publish

```bash
npm run build        # writes the static site to ./out
```

Any static host works. On Vercel or Netlify, set the **root directory** to `nextjs_dashboard`; the build command is
`npm run build` and the output folder is `out`. For GitHub Pages under a sub-path, build with
`NEXT_PUBLIC_BASE_PATH=/<repo-name>` set.

## Data

The site reads two files from `public/data/`, both aggregate-only (no respondent-level records):

- `dashboard.json`: overview figures, segment sizes, driver table, pathway stages, the question catalog with answer
  shares per segment, county counts, county prevalence and national estimates.
- `model.json`: the self-assessment logistic regression as plain numbers (3 KB).

They are built from `shiny_dashboard/precomputed/` and `shiny_dashboard/model/`. After **either** of those changes
(for example after re-running `scripts/aggregate_for_dashboard.py`), regenerate them from the repository root:

```bash
python scripts/export_nextjs_data.py
```

then rebuild. (The root `.gitignore` normally blocks any folder called `data/`; `public/data/` is explicitly allowed.)

## How it is organised

- `src/lib/plots.ts`: the chart builders (a one-for-one port of `plots.py`), returning Plotly.js figures.
- `src/lib/assessment.ts`: self-assessment scoring (matches the Python model to 1e-15 on 300 random answer sets).
- `src/lib/theme.ts`: colours and the six agreed segment names.
- `src/components/Plot.tsx`: draws a chart only when it scrolls into view, so Deep dives opens instantly.
- `src/app/*`: the four pages.

Sizing caveat shown on Segment Profiles: national figures are directional, approximate values modelled from census
records and predicted segments, not a headcount.
