# Youth Livelihoods data dashboard (Next.js, quant version)

A trimmed, data-focused sample of `nextjs_dashboard/`, made so the team can compare the two versions before deciding.
It is meant to sit on a subdomain of the study website. The website carries the qualitative content (segment stories,
quotes, enablers and barriers, opportunity areas, why the study was done), so this version leaves it out.

## What changed from `nextjs_dashboard/`

| Tab | Route | What it shows |
|---|---|---|
| OVERVIEW | `/` | Segment sizes (donut) with each segment's two strongest distinguishing drivers, then headline figures for everyone surveyed. "Why this study" and "How to use" are removed |
| SEGMENTS | `/segments/` | One card per segment with its size and the **2-4 drivers that set it apart** (dot strips against the other five segments and all surveyed); click a card for that segment's driver charts, pathway chart and technical notes (`?seg=3`). This replaces the old Segments overview and single-segment Segments data views |
| COMPARE | `/compare/` | The six side by side: numeric headline table, pathway comparison, shaded driver table. The descriptive table rows and the insight paragraph are removed |
| COUNTIES | `/counties/` | **New.** Segment mix by county (100% stacked bars), county × segment table, respondent map |
| DEEP DIVES | `/deep-dives/` | Unchanged |
| SELF ASSESSMENT | `/self-assessment/` | The results show "What sets this segment apart" and the pathway chart in place of the aspirations and opportunity text |
| METHODOLOGY | `/methodology/` | Adds how "What sets them apart" is chosen |

The "what sets them apart" selection is in `src/lib/distinct.ts` and is documented on the Methodology tab.

## Run, build, data

These work the same way as in `nextjs_dashboard/` (see its README), but run them from this folder:

```bash
cd nextjs_dashboard_quant
npm install
npm run dev          # http://localhost:3000
npm run build        # static site in ./out
```

`public/data/` is a copy of the original's data. After re-running `scripts/export_nextjs_data.py`, copy
`nextjs_dashboard/public/data/*.json` here as well.
