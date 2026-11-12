"""Build segment_population.json: estimated national youth population per segment.

Source: segment_sizing_tables.xlsx from the six-segment sizing run (census youth records scored with the
segment classifier, probability-weighted and prior-corrected). Only the aggregate sheets are read - no
census or survey records. Counts are MODELLED ESTIMATES of predicted segment membership, not observed.

Usage (from the repo root):
  python scripts/build_segment_population.py --xlsx <path>/segment_sizing_tables.xlsx \
      --out shiny_dashboard/precomputed streamlit_dashboard/precomputed
"""
import argparse
import json
from pathlib import Path

import pandas as pd

BREAKDOWNS = {  # key -> (sheet, dimension column)
    "by_sex": ("Sex", "Sex"),
    "by_age_group": ("Age Group", "Age group"),
    "by_settlement_type": ("Settlement Type", "Settlement type"),
    "by_county_zone": ("County Zone", "County zone"),
    "by_county": ("County", "County"),
}


def rows(df: pd.DataFrame, dim: str | None) -> list[dict]:
    pct_col = [c for c in df.columns if c.startswith("%")][0]
    out = []
    for _, r in df.iterrows():
        row = {"segment": str(int(r["Segment"])), "count": int(r["Count"]), "pct": float(r[pct_col])}
        if dim:
            row[dim_key(dim)] = str(r[dim])
        out.append(row)
    return out


def dim_key(dim: str) -> str:
    return dim.lower().replace(" ", "_")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--out", required=True, nargs="+", type=Path)
    args = ap.parse_args()

    sheets = pd.read_excel(args.xlsx, sheet_name=None)
    nat = sheets["National"]
    total = int(nat["Count"].sum())
    payload = {
        "note": ("Modelled estimates of the Kenyan youth population by predicted segment (census records scored "
                 "with the survey-trained classifier, probability-weighted, prior-corrected). Segment labels are "
                 "predicted, not observed; treat counts as approximate and read small cells with caution."),
        "total_youth": total,
        "national": [{"segment": str(int(r["Segment"])), "count": int(r["Count"]),
                      "pct": float(r["% of youth population"])} for _, r in nat.iterrows()],
    }
    for key, (sheet, dim) in BREAKDOWNS.items():
        if sheet in sheets:
            payload[key] = rows(sheets[sheet], dim)

    blob = json.dumps(payload).lower()
    for bad in ('"key"', "uuid"):
        if bad in blob:
            raise SystemExit(f"Refusing to write: found {bad} in payload.")
    for out in args.out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "segment_population.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    print("total youth:", total, "| national rows:", len(payload["national"]),
          "| breakdowns:", [k for k in payload if k.startswith("by_")])
    print("written to:", ", ".join(str(o) for o in args.out))


if __name__ == "__main__":
    main()
