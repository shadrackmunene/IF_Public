"""Aggregate the segmented survey file into dashboard-ready, AGGREGATE-ONLY JSON.

Run this on the machine/account that is authorised to hold the respondent-level file.
Nobody else needs to open that file: the outputs contain segment-level percentages and
averages only - no respondent rows, no KEY/UUID, no county/sub-county or other location.

    python scripts/aggregate_for_dashboard.py ^
        --sav "<...>/data/clean/if_real_livelihood_quantitative_survey_field_clean_v005_segmented.sav" ^
        --out shiny_dashboard/precomputed streamlit_dashboard/precomputed

Requires: pandas, pyreadstat   (pip install pyreadstat) - used only for this script, not the apps.

Outputs (written to every --out folder):
  question_catalog.json        one row per question: code, label, section, dimension, type, option order
  question_distributions.json  categorical questions: segment x answer option -> % of valid answers
  numeric_summary.json         numeric questions: segment -> mean / median / n
  segment_names.json           segment number -> agreed segment name

Edit DIMENSIONS / SECTION_NAMES below to curate which sections appear on which tab.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

try:
    import pyreadstat
except ImportError:  # pragma: no cover
    sys.exit("pyreadstat is required: pip install pyreadstat")

MIN_N = 30          # suppress any segment x question cell with fewer valid answers than this
MAX_CATEGORIES = 12  # a labelled variable with more distinct answers than this is treated as numeric
SEGMENT_COL = "segment"
SEGMENT_NAME_COL = "segment_name"

# Questionnaire section letter -> display name (sub-tab). EDIT to match the questionnaire.
SECTION_NAMES = {
    "A": "Respondent profile", "B": "Household", "C": "Education & work history",
    "D": "Skills", "E": "Current work & income", "F": "Enterprise", "G": "Livelihood choices",
    "H": "Finances & savings", "I": "Mindset & aspirations", "J": "Meaning of work & wellbeing",
    "K": "Networks & norms", "L": "Family & transition support", "M": "AI & technology",
}
# Tab -> section letters. Mirrors the Tableau design (Behaviour / Context / Psychology).
DIMENSIONS = {
    "Context": ["A", "B", "C", "L"],
    "Behaviour": ["D", "E", "F", "G", "H", "K", "M"],
    "Psychology": ["I", "J"],
}

QUESTION_CODE = re.compile(r"^([A-Z])\d{3,4}(_\d+)*$")  # e.g. C303, C304_2, M1304_2
# Never aggregate anything that could identify a respondent or a place.
BLOCKED_NAME = re.compile(r"(?i)^(key|uuid|.*_?id|county.*|sub_?county.*|ward.*|village.*|gps.*|lat.*|lon.*|"
                          r".*phone.*|.*name.*|.*address.*|.*email.*|.*photo.*|.*location.*)$")
# Questions whose WORDING mentions a county (the safety net below refuses any payload containing the word).
# B228 asks the county of birth, a location question, so it stays out; the other three only mention "county"
# in the question text and could be re-admitted by narrowing the safety net to answer data.
EXCLUDE_CODES = {"A104", "B228", "G713", "H814", "A107"}
NON_ANSWER = re.compile(r"(?i)don.?t know|refus|not applicable|no answer|prefer not")


def _section(code: str) -> str | None:
    m = QUESTION_CODE.match(code)
    return m.group(1) if m else None


def _dimension(letter: str) -> str | None:
    return next((d for d, letters in DIMENSIONS.items() if letter in letters), None)


def build(df: pd.DataFrame, meta) -> tuple[list, list, list]:
    labels = meta.column_names_to_labels
    value_labels = meta.variable_value_labels
    segs = sorted(int(s) for s in df[SEGMENT_COL].dropna().unique())
    groups = {str(s): df[df[SEGMENT_COL] == s] for s in segs}
    groups["All"] = df

    catalog, dists, nums = [], [], []
    for code in df.columns:
        letter = _section(code)
        dim = _dimension(letter) if letter else None
        if not dim or BLOCKED_NAME.match(code) or code.endswith("_score") or code in EXCLUDE_CODES:
            continue
        s = pd.to_numeric(df[code], errors="coerce")
        if s.notna().sum() == 0:
            continue
        vlabs = value_labels.get(code, {})
        n_unique = s.nunique()
        label = labels.get(code) or code
        base = {"code": code, "label": label, "section": SECTION_NAMES.get(letter, letter), "dimension": dim}

        if vlabs and n_unique <= MAX_CATEGORIES:
            opts = [(float(k), v) for k, v in sorted(vlabs.items(), key=lambda kv: kv[0])]
            catalog.append({**base, "type": "categorical",
                            "options": [{"value": k, "label": v, "non_answer": bool(NON_ANSWER.search(v))}
                                        for k, v in opts]})
            for gname, g in groups.items():
                gs = pd.to_numeric(g[code], errors="coerce").dropna()
                if len(gs) < MIN_N:
                    continue
                for k, v in opts:
                    dists.append({"code": code, "segment": gname, "option": k, "option_label": v,
                                  "pct": round(100 * float((gs == k).mean()), 1), "n_valid": int(len(gs))})
        elif n_unique > MAX_CATEGORIES:
            catalog.append({**base, "type": "numeric"})
            for gname, g in groups.items():
                gs = pd.to_numeric(g[code], errors="coerce").dropna()
                if len(gs) < MIN_N:
                    continue
                nums.append({"code": code, "segment": gname, "mean": round(float(gs.mean()), 2),
                             "median": round(float(gs.median()), 2), "n_valid": int(len(gs))})
    return catalog, dists, nums


MIN_COUNTY_N = 10  # counties with fewer respondents are dropped from the map file
MIN_CELL_N = 5     # segment x county cells below this are dropped
# Derived profile variables (not survey question codes) shown as extra Deep-dive charts.
PROFILE_VARS = {
    "residence_group": ("Settlement type", "Location & household"),
    "has_children": ("Parent or not", "Location & household"),
    "children_band": ("Number of children (parents only)", "Location & household"),
}


def _county_series(df: pd.DataFrame, meta) -> pd.Series | None:
    """Per-respondent county name (COUNTY level only). Used only to aggregate - never written out."""
    # COUNTY (coded, value-labelled) is the main source. COUNTY_S is only the free-text "other" answer, so it
    # is used just to fill the "Other (specify)" code - never as the main column.
    if "COUNTY" in df.columns:
        vlabs = meta.variable_value_labels.get("COUNTY", {})
        names = pd.to_numeric(df["COUNTY"], errors="coerce").map(vlabs)
        if names.isna().all():  # no value labels: fall back to the raw values
            names = df["COUNTY"].astype(str).str.strip()
        if "COUNTY_S" in df.columns:
            other = names.astype(str).str.lower().str.startswith("other")
            names = names.where(~other, df["COUNTY_S"].astype(str).str.strip().str.title())
    elif "COUNTY_S" in df.columns:
        names = df["COUNTY_S"].astype(str).str.strip()
    else:
        return None
    names = names.where(~names.astype(str).str.lower().isin({"", "nan", "none"}))
    return names


def profile_payloads(df: pd.DataFrame, meta, names: dict[str, str]) -> tuple[list, list, list]:
    """Extra Deep-dive 'questions': settlement type, parent or not, and county of residence by segment,
    plus a county x segment prevalence table. Aggregates only; cells under MIN_CELL_N are dropped."""
    segs = sorted(names, key=int)
    groups = {s: df[df[SEGMENT_COL] == int(s)] for s in segs}
    groups["All"] = df
    catalog, dists = [], []
    for code, (title, section) in PROFILE_VARS.items():
        if code not in df.columns:
            continue
        vlabs = meta.variable_value_labels.get(code, {})
        s_all = pd.to_numeric(df[code], errors="coerce")
        opts = [(float(k), v) for k, v in sorted(vlabs.items(), key=lambda kv: kv[0])
                if float(k) in set(s_all.dropna().astype(float))]
        if len(opts) < 2:
            continue
        catalog.append({"code": code, "label": title, "short": title, "section": section, "dimension": "Context",
                        "type": "categorical",
                        "options": [{"value": k, "label": v, "non_answer": False} for k, v in opts]})
        for gname, g in groups.items():
            gs = pd.to_numeric(g[code], errors="coerce").dropna()
            if len(gs) < MIN_N:
                continue
            for k, v in opts:
                dists.append({"code": code, "segment": gname, "option": k, "option_label": v,
                              "pct": round(100 * float((gs == k).mean()), 1), "n_valid": int(len(gs))})
    # County of residence by segment (share of each segment living in each county) + prevalence table.
    county = _county_series(df, meta)
    prevalence = []
    if county is not None:
        valid = county.dropna()
        keep = valid.value_counts()
        keep = [c for c, n in keep.items() if n >= MIN_COUNTY_N]
        if keep:
            catalog.append({"code": "COUNTY_RES", "label": "County of residence", "short": "County of residence",
                            "section": "Location & household", "dimension": "Context", "type": "categorical",
                            "options": [{"value": float(i), "label": str(c).replace(" County", ""),
                                         "non_answer": False} for i, c in enumerate(keep)]})
            for gname, g in groups.items():
                gc = county.loc[g.index].dropna()
                gc = gc[gc.isin(keep)]
                if len(gc) < MIN_N:
                    continue
                for i, c in enumerate(keep):
                    n_cell = int((gc == c).sum())
                    if n_cell < MIN_CELL_N:
                        continue
                    dists.append({"code": "COUNTY_RES", "segment": gname, "option": float(i),
                                  "option_label": str(c).replace(" County", ""),
                                  "pct": round(100 * n_cell / len(gc), 1), "n_valid": int(len(gc))})
            for c in keep:
                in_c = county == c
                n_c = int(in_c.sum())
                for s in segs:
                    n_cell = int((in_c & (df[SEGMENT_COL] == int(s))).sum())
                    if n_cell >= MIN_CELL_N:
                        prevalence.append({"segment": s, "county": str(c).replace(" County", ""), "n": n_cell,
                                           "n_county": n_c, "pct_of_county": round(100 * n_cell / n_c, 1)})
    return catalog, dists, prevalence


def county_counts(df: pd.DataFrame, meta) -> list[dict]:
    """Respondents per county - COUNTY level only (no sub-county, ward or village), counts and share only.
    Deliberately written to its own file, outside the question-payload safety check above."""
    names = _county_series(df, meta)
    if names is None:
        return []
    names = names.dropna()
    vc = names.value_counts()
    total = int(vc.sum())
    return [{"county": str(c), "n": int(n), "pct": round(100 * n / total, 1)}
            for c, n in vc.items() if n >= MIN_COUNTY_N]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sav", required=True, type=Path)
    ap.add_argument("--out", required=True, nargs="+", type=Path)
    args = ap.parse_args()

    df, meta = pyreadstat.read_sav(str(args.sav), apply_value_formats=False)
    names = (df[[SEGMENT_COL, SEGMENT_NAME_COL]].dropna().drop_duplicates()
             .assign(**{SEGMENT_COL: lambda d: d[SEGMENT_COL].astype(int).astype(str)})
             .set_index(SEGMENT_COL)[SEGMENT_NAME_COL].to_dict())
    catalog, dists, nums = build(df, meta)

    payloads = {"question_catalog.json": catalog, "question_distributions.json": dists,
                "numeric_summary.json": nums, "segment_names.json": names}
    # Safety net: refuse to write if anything identifying slipped into the outputs.
    blob = json.dumps(payloads).lower()
    for bad in ("\"key\"", "county", "uuid"):
        if bad in blob:
            sys.exit(f"Refusing to write outputs: found '{bad}' in aggregate payload.")

    counties = county_counts(df, meta)  # aggregate respondent counts per county, for the map
    p_catalog, p_dists, prevalence = profile_payloads(df, meta, names)  # location / household deep-dive charts
    extra = {"county_counts.json": counties, "profile_catalog.json": p_catalog,
             "profile_distributions.json": p_dists, "county_segment_prevalence.json": prevalence}
    for out in args.out:
        out.mkdir(parents=True, exist_ok=True)
        for fname, obj in {**payloads, **extra}.items():
            (out / fname).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"questions: {len(catalog)} | distribution rows: {len(dists)} | numeric rows: {len(nums)}")
    print(f"counties with >= {MIN_COUNTY_N} respondents: {len(counties)}")
    print("segments:", names)
    print("written to:", ", ".join(str(o) for o in args.out))


if __name__ == "__main__":
    main()
