"""Loads the dashboard's pre-computed, aggregate-only data files from precomputed/.

The files hold segment-level summary statistics only - no respondent-level records or identifiers are
included in this repository. Restart the app after replacing any of them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PRECOMPUTED_DIR = Path(__file__).resolve().parent / "precomputed"
SEGMENTS = ["1", "2", "3", "4", "5", "6"]

_overview = json.loads((PRECOMPUTED_DIR / "overview_stats.json").read_text())
_sizes = pd.read_json(PRECOMPUTED_DIR / "segment_sizes.json", dtype={"segment": str})
_drivers = pd.read_json(PRECOMPUTED_DIR / "segment_driver_table.json", dtype={"segment": str})
_stages = pd.read_json(PRECOMPUTED_DIR / "pathway_stage_table.json", dtype={"segment": str})

N_TOTAL = _overview["n_respondents"]


def overview_stats() -> dict:
    return _overview


def segment_sizes() -> pd.DataFrame:
    return _sizes


def segment_driver_table() -> pd.DataFrame:
    return _drivers


def pathway_stage_table() -> pd.DataFrame:
    return _stages


# ---------------------------------------------------------------------------
# Question explorer data (aggregate-only; produced by scripts/aggregate_for_dashboard.py)
# ---------------------------------------------------------------------------
_HAVE_QUESTIONS = (PRECOMPUTED_DIR / "question_catalog.json").exists()
if _HAVE_QUESTIONS:
    _catalog = json.loads((PRECOMPUTED_DIR / "question_catalog.json").read_text(encoding="utf-8"))
    _dists = pd.read_json(PRECOMPUTED_DIR / "question_distributions.json", dtype={"segment": str, "code": str})
    _nums = pd.read_json(PRECOMPUTED_DIR / "numeric_summary.json", dtype={"segment": str, "code": str})
    _seg_names = json.loads((PRECOMPUTED_DIR / "segment_names.json").read_text(encoding="utf-8"))
else:
    _catalog, _dists, _nums, _seg_names = [], pd.DataFrame(), pd.DataFrame(), {}

_short = {"labels": {}, "hidden": []}
if (PRECOMPUTED_DIR / "question_short_labels.json").exists():
    _short = json.loads((PRECOMPUTED_DIR / "question_short_labels.json").read_text(encoding="utf-8"))
_hidden = set(_short.get("hidden", []))
for _q in _catalog:
    _q["short"] = _short["labels"].get(_q["code"])
# Hidden items (consent script, unlabelled numeric codes) never reach the Explore page.
_catalog = [q for q in _catalog if q["code"] not in _hidden]

DIMENSION_ORDER = ["Behaviour", "Context", "Psychology"]


def has_question_data() -> bool:
    return _HAVE_QUESTIONS


def question_catalog() -> list:
    return _catalog


def question_distributions() -> pd.DataFrame:
    return _dists


def numeric_summary() -> pd.DataFrame:
    return _nums


def segment_names() -> dict:
    return _seg_names


def sections_for(dimension: str) -> list[str]:
    seen: list[str] = []
    for q in _catalog:
        if q["dimension"] == dimension and q["section"] not in seen:
            seen.append(q["section"])
    return seen


def questions_for(dimension: str, section: str) -> list:
    return [q for q in _catalog if q["dimension"] == dimension and q["section"] == section]


_county_path = PRECOMPUTED_DIR / "county_counts.json"
_county = pd.read_json(_county_path) if _county_path.exists() else pd.DataFrame(columns=["county", "n", "pct"])


def county_counts() -> pd.DataFrame:
    return _county


# ---------------------------------------------------------------------------
# Profile / location deep-dive charts, county prevalence, optional national population estimates
# ---------------------------------------------------------------------------
def _opt_json(name):
    p = PRECOMPUTED_DIR / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


_profile_cat = _opt_json("profile_catalog.json") or []
_profile_dist = _opt_json("profile_distributions.json") or []
if _profile_cat:
    for _q in _profile_cat:
        _q.setdefault("short", _q["label"])
    _catalog = _profile_cat + _catalog  # location & household charts come first in the Context tab
    _dists = pd.concat([_dists, pd.DataFrame(_profile_dist).astype({"segment": str, "code": str})],
                       ignore_index=True)

# Charts with nothing to plot (no segment has enough answers) are dropped rather than shown empty.
_with_dists = set(_dists.loc[_dists["segment"] != "All", "code"]) if len(_dists) else set()
_with_nums = set(_nums.loc[_nums["segment"] != "All", "code"]) if len(_nums) else set()
_catalog = [q for q in _catalog if q["code"] in (_with_nums if q["type"] == "numeric" else _with_dists)]

_prevalence = pd.DataFrame(_opt_json("county_segment_prevalence.json") or [],
                           columns=["segment", "county", "n", "n_county", "pct_of_county"])
_prevalence["segment"] = _prevalence["segment"].astype(str)
_population = _opt_json("segment_population.json")  # optional: {"source": "...", "segments": {"1": 123456, ...}}


def county_summary(segment: str, top: int = 3) -> str | None:
    """Short text on where a segment is most prevalent, ranked by its share of respondents in each county."""
    sub = _prevalence[(_prevalence["segment"] == str(segment)) & (_prevalence["n_county"] >= 15)]
    if sub.empty:
        return None
    best = sub.sort_values("pct_of_county", ascending=False).head(top)
    parts = [f"{r.county} ({r.pct_of_county:.0f}% of respondents there)" for r in best.itertuples()]
    return "Most prevalent in " + ", ".join(parts) + "."


MIN_COUNTY_N = 10  # must match scripts/aggregate_for_dashboard.py: smaller counties are dropped from county_counts.json


def population_estimate(segment: str) -> dict | None:
    """National estimate for a segment, if a six-segment sizing file has been supplied."""
    if not _population:
        return None
    for row in _population.get("national") or []:
        if str(row.get("segment")) == str(segment):
            return {"n": int(row["count"]), "pct": row.get("pct"), "total": _population.get("total_youth"),
                    "note": _population.get("note", "")}
    return None


# ---------------------------------------------------------------------------
# Topics: related questions within a section (e.g. every "Aware of: ..." item), for the Deep dives drill-down
# ---------------------------------------------------------------------------
import re as _re

ALL_TOPICS = "__all__"
INDIVIDUAL = "Individual questions"


def topic_of(q: dict) -> str:
    """The group a question belongs to: the text before ':' for multi-part items, the prefix before the
    '(1st ...)' marker for repeated items, otherwise 'Individual questions'."""
    t = q.get("short") or q["label"]
    if ": " in t:
        return t.split(": ", 1)[0]
    m = _re.match(r"^(.*?) \(\d+(?:st|nd|rd|th) [a-z ]+\)$", t)
    return m.group(1) if m else INDIVIDUAL


def topics_for(dimension: str, section: str) -> list[tuple[str, int]]:
    """(topic, number of questions) in first-appearance order, with 'Individual questions' last."""
    counts: dict[str, int] = {}
    for q in questions_for(dimension, section):
        counts[topic_of(q)] = counts.get(topic_of(q), 0) + 1
    ordered = [(t, n) for t, n in counts.items() if t != INDIVIDUAL]
    if INDIVIDUAL in counts:
        ordered.append((INDIVIDUAL, counts[INDIVIDUAL]))
    return ordered
