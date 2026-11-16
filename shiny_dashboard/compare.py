"""HTML builders for the segment comparison views: the report's side-by-side segment table, a shaded table of
every segmentation driver across the six segments, and the list of drivers on which one segment is the highest
or lowest of the six. All values come from segment_content.py (report) or the aggregate driver table."""

from __future__ import annotations

from html import escape

import pandas as pd

from segment_content import COMPARE_ROWS, SEGMENTS
from theme import SEGMENT_COLORS, SEGMENT_PALETTES, order_segments, r0, SEGMENT_NAMES

CATEGORY_TITLES = {"Demographic": "Demographic: what circumstances do they start with?",
                   "Behavioral": "Behavioural: what do they do to earn and get ahead?",
                   "Psychographic": "Psychometric: how do they think about work and the future?"}


def fmt_value(v: float | None, is_pct: bool) -> str:
    if v is None or pd.isna(v):
        return "–"
    return f"{r0(v)}%" if is_pct else f"{v:.1f}"


def _driver_rows(driver_table: pd.DataFrame):
    segs = order_segments(s for s in driver_table["segment"].unique() if s != "All")
    for cat in CATEGORY_TITLES:
        sub = driver_table[driver_table["category"] == cat]
        rows = []
        for label in sub["label"].unique():
            part = sub[sub["label"] == label]
            vals = {r.segment: float(r.value) for r in part.itertuples()}
            rows.append((label, bool(part["is_pct"].iloc[0]), vals))
        yield cat, segs, rows


def driver_heatmap_html(driver_table: pd.DataFrame) -> str:
    """One table, drivers as rows and segments as columns. Each row is shaded from its lowest value (light) to
    its highest (dark), so the defining differences jump out; ▲/▼ mark the highest/lowest segment."""
    out = ['<div class="table-scroll"><table class="cmp-table heat">']
    first = True
    for cat, segs, rows in _driver_rows(driver_table):
        if first:
            out.append("<thead><tr><th></th>" + "".join(
                f'<th><span class="dot" style="background:{SEGMENT_COLORS[s]}"></span>{escape(SEGMENT_NAMES[s])}</th>'
                for s in segs) + '<th class="all-col">All surveyed</th></tr></thead><tbody>')
            first = False
        out.append(f'<tr class="cat-row"><td colspan="{len(segs) + 2}">{escape(CATEGORY_TITLES[cat])}</td></tr>')
        for label, is_pct, vals in rows:
            seg_vals = [vals.get(s) for s in segs]
            present = [v for v in seg_vals if v is not None]
            lo, hi = (min(present), max(present)) if present else (0, 0)
            cells = []
            for v in seg_vals:
                if v is None:
                    cells.append("<td>–</td>")
                    continue
                t = (v - lo) / (hi - lo) if hi > lo else 0.0
                alpha = 0.08 + 0.62 * t
                mark = " ▲" if v == hi and hi > lo else " ▼" if v == lo and hi > lo else ""
                color = "#fff" if alpha > 0.5 else "inherit"
                cells.append(f'<td style="background:rgba(15,107,82,{alpha:.2f});color:{color}">'
                             f'{fmt_value(v, is_pct)}<span class="mk">{mark}</span></td>')
            out.append(f"<tr><th scope=\"row\">{escape(label)}</th>{''.join(cells)}"
                       f'<td class="all-col">{fmt_value(vals.get("All"), is_pct)}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def segment_compare_html(image_url) -> str:
    """The report's segments-overview table: size, profile, education route, how they find work, what work
    means and what each segment stands out on. image_url(segment) gives the illustration's URL."""
    from segment_content import ORDER

    head = "".join(
        f'<th><img src="{image_url(s)}" alt="" class="cmp-img">'
        f'<span class="cmp-name" style="color:{SEGMENT_PALETTES[s][0]}">{escape(SEGMENT_NAMES[s])}</span></th>'
        for s in ORDER)
    body = []
    for key, title in COMPARE_ROWS:
        cells = []
        for s in ORDER:
            c = SEGMENTS[s]
            v = c["stats"].get(key) or c["compare"].get(key, "")
            cls = ' class="num"' if key in c["stats"] else ""
            cells.append(f"<td{cls}>{escape(v)}</td>")
        body.append(f'<tr><th scope="row">{escape(title)}</th>{"".join(cells)}</tr>')
    return (f'<div class="table-scroll"><table class="cmp-table profile"><thead><tr><th></th>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


MAX_DEFINING = 6  # per side; the most distinctive first


def defining_drivers(driver_table: pd.DataFrame, segment: str) -> list[dict]:
    """Drivers on which the segment is clearly the highest or lowest of the six (ties excluded), most
    distinctive first: ranked by the gap to the next segment as a share of the driver's range."""
    found = []
    for _cat, segs, rows in _driver_rows(driver_table):
        for label, is_pct, vals in rows:
            seg_vals = {s: vals[s] for s in segs if s in vals}
            v = seg_vals.get(segment)
            others = [x for s, x in seg_vals.items() if s != segment]
            if v is None or not others:
                continue
            spread = max(seg_vals.values()) - min(seg_vals.values())
            if v > max(others):
                which, gap = "highest", v - max(others)
            elif v < min(others):
                which, gap = "lowest", min(others) - v
            else:
                continue
            found.append({"label": label, "which": which, "value": fmt_value(v, is_pct),
                          "all": fmt_value(vals.get("All"), is_pct), "score": gap / spread if spread else 0})
    out = []
    for which in ("highest", "lowest"):
        side = sorted((f for f in found if f["which"] == which), key=lambda f: -f["score"])
        out += side[:MAX_DEFINING]
    return out


def defining_drivers_html(driver_table: pd.DataFrame, segment: str) -> str:
    items = defining_drivers(driver_table, segment)
    if not items:
        return ""
    chips = []
    for which, title in (("highest", "Highest of the six segments"), ("lowest", "Lowest of the six segments")):
        group = [i for i in items if i["which"] == which]
        if not group:
            continue
        lis = "".join(f'<li><span class="chip-label">{escape(i["label"])}</span> <b>{i["value"]}</b> '
                      f'<span class="text-muted">(all surveyed: {i["all"]})</span></li>' for i in group)
        arrow = "▲" if which == "highest" else "▼"
        chips.append(f'<div class="def-col"><div class="def-title">{arrow} {title}</div><ul>{lis}</ul></div>')
    return f'<div class="defining">{"".join(chips)}</div>'
