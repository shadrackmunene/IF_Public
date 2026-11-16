"""Builds the data files the Next.js dashboard loads in the browser.

Reads the aggregate-only files in shiny_dashboard/precomputed/ (no respondent-level data) and the fitted
self-assessment model, and writes to nextjs_dashboard/public/data/:

  dashboard.json  one compact bundle: overview, sizes, drivers, pathway stages, question catalog (short labels
                  applied, hidden items removed, location/household questions first), per-question answer
                  shares and numeric averages, county counts, county prevalence and national estimates.
                  Also the written content: segment profiles (segment_content.py) and methodology notes
                  (methodology.py). The segment illustrations are copied to public/images/segments/.
  model.json      the self-assessment logistic regression as plain numbers (coefficients, intercepts, feature
                  order) so scoring runs in the browser with no server.

Run from the repository root (needs joblib + scikit-learn, as the Shiny app does):
    python scripts/export_nextjs_data.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "shiny_dashboard" / "precomputed"
MODEL = ROOT / "shiny_dashboard" / "model" / "mini_questionnaire_model.joblib"
OUT = ROOT / "nextjs_dashboard" / "public" / "data"


def load(name: str, default=None):
    p = SRC / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def key(v: float) -> str:
    """Option value as a stable JSON key: 1.0 -> '1', 2.5 -> '2.5'."""
    return str(int(v)) if float(v) == int(v) else str(v)


def build_bundle() -> dict:
    catalog = load("question_catalog.json", [])
    short = load("question_short_labels.json", {"labels": {}, "hidden": []})
    hidden = set(short.get("hidden", []))
    for q in catalog:
        q["short"] = short["labels"].get(q["code"])
    catalog = [q for q in catalog if q["code"] not in hidden]

    dist_rows = load("question_distributions.json", [])
    profile_cat = load("profile_catalog.json", [])
    if profile_cat:
        for q in profile_cat:
            q.setdefault("short", q["label"])
        catalog = profile_cat + catalog  # location & household charts come first in the Context tab
        dist_rows = dist_rows + load("profile_distributions.json", [])

    # {code: {segment: {"n": n_valid, "p": {option_key: pct}}}}
    dists: dict = {}
    for r in dist_rows:
        seg = dists.setdefault(r["code"], {}).setdefault(str(r["segment"]), {"n": int(r["n_valid"]), "p": {}})
        seg["p"][key(r["option"])] = r["pct"]

    nums: dict = {}
    for r in load("numeric_summary.json", []):
        nums.setdefault(r["code"], {})[str(r["segment"])] = {
            "mean": r["mean"], "median": r["median"], "n": int(r["n_valid"])}

    # Charts with nothing to plot (no segment has enough answers) are dropped rather than shown empty.
    def has_data(q: dict) -> bool:
        src = nums if q["type"] == "numeric" else dists
        return any(s != "All" for s in src.get(q["code"], {}))

    catalog = [q for q in catalog if has_data(q)]

    # Option values stay numeric in the catalog; the chart code looks answers up by key(value).
    slim = []
    for q in catalog:
        item = {k: q[k] for k in ("code", "label", "short", "section", "dimension", "type") if k in q}
        if q.get("options"):
            item["options"] = [{"value": o["value"], "label": o["label"], "non_answer": bool(o["non_answer"])}
                               for o in q["options"]]
        slim.append(item)

    sys.path.insert(0, str(ROOT / "shiny_dashboard"))
    import methodology
    import questionnaire
    import segment_content as sc
    from pathway_content import PATHWAY_STAGES, SEGMENT_CONTENT

    profiles = {}
    for code, c in sc.SEGMENTS.items():
        item = {k: v for k, v in c.items() if k not in ("image", "opportunities")}
        # Content hash in the URL so browsers fetch a replaced illustration instead of a cached copy.
        version = hashlib.md5((ROOT / "shiny_dashboard" / "www" / c["image"]).read_bytes()).hexdigest()[:8]
        item["image"] = f"images/segments/{c['slug']}.png?v={version}"
        item["opportunities"] = [{"theme": t, "title": ti, "desc": d} for t, ti, d in c["opportunities"]]
        profiles[code] = item

    content = {s: {k: c[k] for k in ("headline", "where_they_sit", "what_would_help", "hcd_link")}
               for s, c in SEGMENT_CONTENT.items()}
    questions = [{"id": q["id"], "text": q["text"], "widget": q["widget"],
                  **({k: q[k] for k in ("min", "max", "value")} if q["widget"] == "numeric" else {}),
                  **({"options": [{"label": lbl, "value": val} for lbl, val in q["options"]]}
                     if q["widget"] == "radio" else {})}
                 for q in questionnaire.QUESTIONS]

    return {
        "profiles": profiles,
        "compare_rows": [list(r) for r in sc.COMPARE_ROWS],
        "stage_keys": [list(r) for r in sc.PATHWAY_STAGE_KEYS],
        "study": {"why": [list(r) for r in sc.STUDY["why"]], "what": sc.STUDY["what"]},
        "methodology": {"sections": methodology.SECTIONS,
                        "drivers": [list(r) for r in methodology.DRIVER_DEFINITIONS]},
        "content": content,
        "stage_order": PATHWAY_STAGES,
        "questionnaire": questions,
        "overview": load("overview_stats.json"),
        "sizes": load("segment_sizes.json"),
        "drivers": load("segment_driver_table.json"),
        "stages": load("pathway_stage_table.json"),
        "names": load("segment_names.json", {}),
        "catalog": slim,
        "dists": dists,
        "nums": nums,
        "counties": load("county_counts.json", []),
        "prevalence": load("county_segment_prevalence.json", []),
        "population": load("segment_population.json"),
    }


def build_model() -> dict:
    import joblib

    bundle = joblib.load(MODEL)
    prep, clf = bundle["pipeline"].named_steps["prep"], bundle["pipeline"].named_steps["clf"]
    return {
        "classes": [str(c) for c in bundle["classes"]],
        "features": [str(f) for f in prep.get_feature_names_out()],
        "coef": clf.coef_.tolist(),
        "intercept": clf.intercept_.tolist(),
    }


def copy_images() -> None:
    """Copy the segment illustrations from shiny_dashboard/www/ to the Next.js public folder, under URL-safe
    names (images/segments/<slug>.png)."""
    import shutil

    sys.path.insert(0, str(ROOT / "shiny_dashboard"))
    from segment_content import SEGMENTS

    dest = ROOT / "nextjs_dashboard" / "public" / "images" / "segments"
    dest.mkdir(parents=True, exist_ok=True)
    for c in SEGMENTS.values():
        shutil.copyfile(ROOT / "shiny_dashboard" / "www" / c["image"], dest / f"{c['slug']}.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    copy_images()
    bundle = build_bundle()
    (OUT / "dashboard.json").write_text(json.dumps(bundle, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    (OUT / "model.json").write_text(json.dumps(build_model(), separators=(",", ":")), encoding="utf-8")
    print(f"questions: {len(bundle['catalog'])}, with answer data: {len(bundle['dists'])}, "
          f"numeric: {len(bundle['nums'])}")
    for f in sorted(OUT.glob("*.json")):
        print(f"{f.name}: {f.stat().st_size / 1024:.0f} KB")
