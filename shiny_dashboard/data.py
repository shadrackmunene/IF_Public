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
