# Youth Livelihoods dashboard (Next.js)

The same four pages as the Shiny and Streamlit dashboards, built as a **static site**: no Python server runs when
someone opens it, so it loads fast, never "sleeps", and can be hosted free.

| Tab | What it shows |
|---|---|
| OVERVIEW | Headline figures, the six segments at a glance, a county respondents map |
| SEGMENT PROFILES | Pick a segment: demographic / behavioural / psychographic drivers, livelihood pathway, estimated national size, where it is most prevalent |
| DEEP DIVES | Every survey question by segment (dimension, section, topic, search, segment filters) |
| SELF ASSESSMENT | 12 questions, one at a time; scored in the browser against the saved model |

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
