"""Interactive Plotly chart builders shared by every page of the Shiny and Streamlit dashboards.
Segments are always shown by their agreed names (never "Segment 1, 2, 3"). Every tooltip carries both the
percentage and its sample size, e.g. "59% (n=124)"."""

from __future__ import annotations

import re as _re
import textwrap

import pandas as pd
import plotly.graph_objects as go

from theme import BRAND, DARK_TEXT, SEGMENT_COLORS, SEGMENT_NAMES, SEGMENT_PALETTES

PLOTLY_CONFIG = {
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d",
                               "autoScale2d", "resetScale2d"],
}
_REF_GREY = "#4B5563"
_NON_ANSWER_GREY = "#C8C8C8"


def seg_name(segment) -> str:
    return SEGMENT_NAMES.get(str(segment), str(segment))


def _base_layout(fig: go.Figure, height: int, **kw) -> go.Figure:
    kw.setdefault("margin", dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="sans-serif", color=DARK_TEXT, size=12),
        hoverlabel=dict(font_size=13),
        dragmode=False,
        **kw,
    )
    fig.update_xaxes(showline=True, linecolor="#CCCCCC", gridcolor="#EEF0F4")
    fig.update_yaxes(showline=True, linecolor="#CCCCCC", gridcolor="#EEF0F4")
    return fig


def _wrap(label: str, width: int = 16) -> str:
    return "<br>".join(textwrap.wrap(str(label), width)) or str(label)


# ---------------------------------------------------------------------------
# Overview / Segment Profiles charts
# ---------------------------------------------------------------------------
def segment_size_chart(sizes: pd.DataFrame) -> go.Figure:
    segs = sizes["segment"].tolist()
    fig = go.Figure(go.Bar(
        x=[seg_name(s) for s in segs],
        y=sizes["pct"],
        marker_color=[SEGMENT_COLORS[s] for s in segs],
        customdata=sizes["n"],
        text=[f"{p}%" for p in sizes["pct"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y}% of respondents (n=%{customdata})<extra></extra>",
    ))
    _base_layout(fig, 340)
    fig.update_yaxes(title_text="% of respondents", range=[0, max(sizes["pct"]) * 1.25])
    fig.update_xaxes(showgrid=False)
    return fig


def driver_bar_chart(driver_table: pd.DataFrame, category: str, highlight_segment: str | None = None,
                     kind: str = "pct", n_by_segment: dict | None = None) -> go.Figure | None:
    """Vertical grouped bars, one group per driver: the selected segment vs all respondents.
    kind='pct' shows share-of-segment drivers (%); kind='score' shows average-score drivers (age, 1-5 scales).
    Splitting the two keeps their very different units off a shared axis."""
    want_pct = kind == "pct"
    sub = driver_table[(driver_table["category"] == category) & (driver_table["is_pct"] == want_pct)]
    labels = sub["label"].unique().tolist()
    if not labels:
        return None
    n_by_segment = n_by_segment or {}

    def _val(lbl, seg):
        s = sub[(sub["label"] == lbl) & (sub["segment"] == seg)]["value"]
        return None if s.empty else float(s.iloc[0])

    fmt = (lambda v: "" if v is None else f"{v:.0f}%") if want_pct else (lambda v: "" if v is None else f"{v:.2f}")
    unit = "%" if want_pct else ""
    wrapped = [_wrap(l, 15) for l in labels]
    fig = go.Figure()
    all_vals = [_val(l, "All") for l in labels]
    fig.add_bar(x=wrapped, y=all_vals, name="All respondents", marker_color="#C9CDD6",
                text=[fmt(v) for v in all_vals], textposition="outside", textfont=dict(size=10),
                customdata=[[l, fmt(v), n_by_segment.get("All", "")] for l, v in zip(labels, all_vals)],
                hovertemplate="<b>%{customdata[0]}</b><br>All respondents: %{customdata[1]} (n=%{customdata[2]})"
                              "<extra></extra>")
    cands = [v for v in all_vals if v is not None]
    if highlight_segment:
        seg_vals = [_val(l, highlight_segment) for l in labels]
        fig.add_bar(x=wrapped, y=seg_vals, name=seg_name(highlight_segment),
                    marker_color=SEGMENT_COLORS.get(highlight_segment, BRAND),
                    text=[fmt(v) for v in seg_vals], textposition="outside", textfont=dict(size=10),
                    customdata=[[l, fmt(v), n_by_segment.get(highlight_segment, "")]
                                for l, v in zip(labels, seg_vals)],
                    hovertemplate=f"<b>%{{customdata[0]}}</b><br>{seg_name(highlight_segment)}: %{{customdata[1]}} "
                                  "(n=%{customdata[2]})<extra></extra>")
        cands += [v for v in seg_vals if v is not None]
    top = max(cands, default=1)
    _base_layout(fig, 380, barmode="group", legend=dict(orientation="h", y=1.12, x=0),
                 margin=dict(l=10, r=10, t=40, b=10))
    fig.update_yaxes(range=[0, top * 1.25], ticksuffix=unit, title_text="% of segment" if want_pct else "Average")
    fig.update_xaxes(showgrid=False, tickfont=dict(size=10))
    return fig


def pathway_stage_chart(stage_table: pd.DataFrame, segment: str, n: int | None = None) -> go.Figure:
    from pathway_content import PATHWAY_STAGES

    sub = stage_table[stage_table["segment"] == segment].set_index("stage").loc[PATHWAY_STAGES]
    fig = go.Figure(go.Bar(
        x=[s.replace(" ", "<br>") for s in PATHWAY_STAGES],
        y=sub["pct"],
        marker_color=SEGMENT_COLORS.get(segment, BRAND),
        text=[f"{p}%" for p in sub["pct"]],
        textposition="outside",
        customdata=[[s, "" if n is None else n] for s in PATHWAY_STAGES],
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>%{{y}}% of {seg_name(segment)} meet this stage proxy "
                      "(n=%{customdata[1]})<extra></extra>",
    ))
    _base_layout(fig, 320)
    fig.update_yaxes(title_text="% of segment meeting stage proxy", range=[0, 110])
    return fig


def probability_chart(probabilities: dict[str, float]) -> go.Figure:
    segs = sorted(probabilities.keys(), key=int)
    vals = [100 * probabilities[s] for s in segs]
    fig = go.Figure(go.Bar(
        x=[seg_name(s) for s in segs],
        y=vals,
        marker_color=[SEGMENT_COLORS[s] for s in segs],
        text=[f"{v:.0f}%" for v in vals],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Match probability: %{y:.1f}%<extra></extra>",
    ))
    _base_layout(fig, 280)
    fig.update_yaxes(title_text="Match probability (%)", range=[0, 112])
    fig.update_xaxes(showgrid=False)
    return fig


def to_html(fig: go.Figure) -> str:
    """Embeddable HTML fragment (Plotly.js is loaded once by the host page)."""
    return fig.to_html(full_html=False, include_plotlyjs=False, config=PLOTLY_CONFIG, default_width="100%")


# ---------------------------------------------------------------------------
# Deep-dive question charts (built from the aggregate-only question files)
# ---------------------------------------------------------------------------
def _tint(hex_color: str, t: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * t) for c in (r, g, b))


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def clean_question_label(label: str) -> str:
    """Drop the leading question code ('A101. ') from a survey label."""
    return _re.sub(r"^[A-Z]\d{3,4}(_\d+)*[.:]?\s*", "", label).strip()


def question_title(q: dict) -> str:
    """Short, number-free title for a question (falls back to a cleaned label)."""
    return q.get("short") or clean_question_label(q["label"])


def _text_color(hex_color: str) -> str:
    """White text on dark fills, dark text on light fills."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#FFFFFF" if 0.299 * r + 0.587 * g + 0.114 * b < 140 else DARK_TEXT


# (first, last) answer labels that mark a genuine ordered rating / Likert scale.
_SCALE_ENDS = [
    ("strongly disagree", "strongly agree"), ("very low respect", "very high respect"),
    ("very poorly paid", "very well paid"), ("not at all", "extremely"),
    ("clearly a worthwhile", "clearly a missed"), ("not knowledgeable at all", "very knowledgeable"),
    ("never", "very frequently"), ("no freedom at all", "a lot of freedom"),
    ("very unlikely", "very likely"), ("very good", "very bad"), ("improve a lot", "get much worse"),
    ("very easy", "very difficult"),
]


def is_likert(q: dict) -> bool:
    if q.get("type") != "categorical":
        return False
    valid = [o["label"].lower() for o in q["options"] if not o["non_answer"]]
    if len(valid) not in (4, 5):
        return False
    return any(valid[0].startswith(a) and valid[-1].startswith(b) for a, b in _SCALE_ENDS)


def _seg_rows(sub: pd.DataFrame, names: dict[str, str]):
    """pct[segment_or_All][option_value] and n[segment_or_All] lookups for one question."""
    pct, n = {}, {}
    for s in list(sorted(names, key=int)) + ["All"]:
        part = sub[sub["segment"] == s]
        pct[s] = {float(r.option): float(r.pct) for r in part.itertuples()}
        n[s] = int(part["n_valid"].iloc[0]) if not part.empty else 0
    return pct, n


_HOVER_HEAD = "<span style='color:#777'>{dim}: {sec}</span><br>"

# 13-step diverging scheme (green = high/positive ... grey = neutral ... red = low/negative)
DIVERGING = ["#00876C", "#42977F", "#66A793", "#87B6A7", "#A6C6BB", "#C6D6D0", "#E5E5E5",
             "#E8CBCB", "#E8B1B1", "#E69798", "#E27B7F", "#DC5F68", "#D43D51"]
_DIV_PICK = {5: [12, 9, 6, 3, 0], 4: [12, 9, 3, 0]}
_POSITIVE_FIRST = ("very good", "improve a lot", "very easy", "clearly a worthwhile")


def _likert_valid(q: dict) -> list[dict]:
    valid = [o for o in q["options"] if not o["non_answer"]]
    return valid[::-1] if valid and valid[0]["label"].lower().startswith(_POSITIVE_FIRST) else valid


def likert_question_chart(q: dict, dists: pd.DataFrame, names: dict[str, str]) -> go.Figure:
    """Diverging bars for a rating / Likert scale, centred on the midpoint. Colour encodes the ANSWER on a
    red (low) -> grey (neutral) -> green (high) scheme; segments are the rows. Dashed lines mark the
    all-respondent share on each side."""
    sub = dists[dists["code"] == q["code"]]
    segs = sorted(names, key=int)
    pct, nn = _seg_rows(sub, names)
    valid = _likert_valid(q)
    n = len(valid)
    half, odd = n // 2, n % 2 == 1
    rstart = half + 1 if odd else half
    colors = [DIVERGING[i] for i in _DIV_PICK[n]]
    vals = {s: [pct[s].get(o["value"], 0.0) for o in valid] for s in segs + ["All"]}

    def mid_half(s):
        return vals[s][half] / 2 if odd else 0.0

    labels = [seg_name(s) for s in segs]
    fig = go.Figure()
    for p, o in enumerate(valid):
        base = []
        for s in segs:
            v = vals[s]
            if p < half:
                base.append(-(sum(v[p + 1:half]) + mid_half(s) + v[p]))
            elif odd and p == half:
                base.append(-v[p] / 2)
            else:
                base.append(sum(v[rstart:p]) + mid_half(s))
        xs = [vals[s][p] for s in segs]
        fig.add_bar(
            y=labels, x=xs, base=base, orientation="h", name=o["label"], showlegend=False,
            marker=dict(color=colors[p], line=dict(color="white", width=0.8)),
            customdata=[[o["label"], f"{vals['All'][p]:.1f}", nn[s], nn["All"]] for s in segs],
            text=[o["label"] if x >= 16 else "" for x in xs], textposition="inside", insidetextanchor="middle",
            textfont=dict(size=10, color=_text_color(colors[p])),
            hovertemplate=(_HOVER_HEAD.format(dim=q["dimension"], sec=q["section"]) +
                           "<b>%{y}</b><br>%{customdata[0]}: <b>%{x:.0f}% (n=%{customdata[2]})</b><br>"
                           "All respondents: %{customdata[1]}% (n=%{customdata[3]})<extra></extra>"),
        )
    a = vals["All"]
    all_high = sum(a[rstart:]) + (a[half] / 2 if odd else 0.0)
    all_low = sum(a[:half]) + (a[half] / 2 if odd else 0.0)
    for x, txt in ((all_high, f"All: {all_high:.0f}%"), (-all_low, f"All: {all_low:.0f}%")):
        fig.add_vline(x=x, line_dash="dash", line_color=_REF_GREY, line_width=1.2,
                      annotation_text=txt, annotation_position="top", annotation_font=dict(size=10, color=_REF_GREY))
    fig.add_vline(x=0, line_color="#9AA0A6", line_width=1)
    right_max = max([all_high] + [sum(vals[s][rstart:]) + mid_half(s) for s in segs])
    left_max = max([all_low] + [sum(vals[s][:half]) + mid_half(s) for s in segs])
    hi_lim, lo_lim = min(100, right_max + 12), min(100, max(left_max + 12, 22))
    ticks = [t for t in range(-100, 101, 25) if -lo_lim <= t <= hi_lim]
    _base_layout(fig, 110 + 34 * len(segs), barmode="overlay", margin=dict(l=10, r=10, t=26, b=58))
    fig.update_xaxes(range=[-lo_lim, hi_lim], tickvals=ticks, ticktext=[f"{abs(t)}%" for t in ticks], zeroline=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    cap = dict(xref="paper", yref="paper", y=0, yshift=-36, showarrow=False, font=dict(size=11, color="#5C6B62"))
    fig.add_annotation(x=0, xanchor="left", text=f"◀ {valid[0]['label']}", **cap)
    fig.add_annotation(x=1, xanchor="right", text=f"{valid[-1]['label']} ▶", **cap)
    return fig


def _vertical_segment_bars(names, segs, values, texts, hover_label, all_value, all_text, y_title, q, nn,
                           ymax=None, pct=False):
    fig = go.Figure(go.Bar(
        x=[seg_name(s) for s in segs], y=values, marker_color=[SEGMENT_COLORS[s] for s in segs],
        text=texts, textposition="outside",
        customdata=[[hover_label, nn.get(s, ""), nn.get("All", "")] for s in segs],
        hovertemplate=(_HOVER_HEAD.format(dim=q["dimension"], sec=q["section"]) +
                       "<b>%{x}</b><br>%{customdata[0]}: <b>%{text} (n=%{customdata[1]})</b><extra></extra>"),
    ))
    if all_value is not None:
        fig.add_hline(y=all_value, line_dash="dash", line_color=_REF_GREY, line_width=1.2,
                      annotation_text=f"{all_text} (n={nn.get('All', '')})", annotation_position="top left",
                      annotation_font=dict(size=11, color=_REF_GREY))
    _base_layout(fig, 340, margin=dict(l=10, r=10, t=24, b=10))
    top = max([v for v in values if v is not None] + [all_value or 0]) if values else 1
    fig.update_yaxes(title_text=y_title, range=[0, (ymax or top) * 1.22], ticksuffix="%" if pct else "")
    fig.update_xaxes(showgrid=False)
    return fig


def binary_question_chart(q: dict, dists: pd.DataFrame, names: dict[str, str]) -> go.Figure:
    """Yes/No style question: vertical bar per segment = % choosing the 'yes' option, dashed line = all."""
    sub = dists[dists["code"] == q["code"]]
    segs = sorted(names, key=int)
    pct, nn = _seg_rows(sub, names)
    valid = [o for o in q["options"] if not o["non_answer"]]
    pos = next((o for o in valid if _re.match(r"(?i)^(yes|selected|checked|mentioned)", o["label"])), valid[-1])
    vals = [pct[s].get(pos["value"], 0.0) for s in segs]
    overall = pct["All"].get(pos["value"])
    return _vertical_segment_bars(
        names, segs, vals, [f"{v:.0f}%" for v in vals], pos["label"], overall,
        f"All: {overall:.0f}%" if overall is not None else "", f"% {pos['label']}", q, nn,
        ymax=100 if max(vals, default=0) > 60 else None, pct=True)


def columns_question_chart(q: dict, dists: pd.DataFrame, names: dict[str, str]) -> go.Figure:
    """Faceted small multiples: one panel per segment, answer options inside each panel, and a short grey
    marker on every option showing the all-respondent share. Short option lists use vertical bars; long
    lists switch to horizontal bars so labels stay readable instead of piling into one colourful stack."""
    from plotly.subplots import make_subplots

    sub = dists[dists["code"] == q["code"]]
    segs = sorted(names, key=int)
    pct, nn = _seg_rows(sub, names)
    valid = [o for o in q["options"] if not o["non_answer"]]
    horizontal = len(valid) > 6
    short = [o["label"] if len(o["label"]) <= (34 if horizontal else 16)
             else o["label"][:(33 if horizontal else 15)].rstrip() + "…" for o in valid]
    ncols = max(1, min(3, len(segs)))
    nrows = -(-len(segs) // ncols)
    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=[seg_name(s) for s in segs],
                        vertical_spacing=0.18 if nrows > 1 else 0.1, horizontal_spacing=0.04,
                        shared_yaxes=True)
    ymax = max((pct[s].get(o["value"], 0.0) for s in segs + ["All"] for o in valid), default=1)
    pos = list(range(len(valid)))
    for i, s in enumerate(segs):
        r, c = i // ncols + 1, i % ncols + 1
        vals = [pct[s].get(o["value"], 0.0) for o in valid]
        allv = [pct["All"].get(o["value"], 0.0) for o in valid]
        cd = [[o["label"], f"{a:.1f}", nn[s], nn["All"]] for o, a in zip(valid, allv)]
        hov = (_HOVER_HEAD.format(dim=q["dimension"], sec=q["section"]) + f"<b>{seg_name(s)}</b><br>"
               "%{customdata[0]}: <b>%{" + ("x" if horizontal else "y") + ":.0f}% (n=%{customdata[2]})</b><br>"
               "All respondents: %{customdata[1]}% (n=%{customdata[3]})<extra></extra>")
        txt = [f"{v:.0f}%" if v >= 3 else "" for v in vals]
        if horizontal:
            fig.add_bar(y=pos, x=vals, orientation="h", row=r, col=c, marker_color=SEGMENT_COLORS[s],
                        showlegend=False, text=txt, textposition="outside", textfont=dict(size=9),
                        customdata=cd, hovertemplate=hov)
            fig.add_scatter(y=pos, x=allv, row=r, col=c, mode="markers", showlegend=False, hoverinfo="skip",
                            marker=dict(symbol="line-ns", size=14, color=_REF_GREY, line=dict(color=_REF_GREY, width=2)))
            fig.update_yaxes(tickvals=pos, ticktext=short, tickfont=dict(size=9), autorange="reversed",
                             showticklabels=(c == 1), row=r, col=c)
        else:
            fig.add_bar(x=pos, y=vals, row=r, col=c, marker_color=SEGMENT_COLORS[s], showlegend=False,
                        text=txt, textposition="outside", textfont=dict(size=9), customdata=cd, hovertemplate=hov)
            fig.add_scatter(x=pos, y=allv, row=r, col=c, mode="markers", showlegend=False, hoverinfo="skip",
                            marker=dict(symbol="line-ew", size=22, color=_REF_GREY, line=dict(color=_REF_GREY, width=2.2)))
            fig.update_xaxes(tickvals=pos, ticktext=short, tickangle=-40, tickfont=dict(size=9), row=r, col=c)
    if horizontal:
        _base_layout(fig, 150 + (19 * len(valid) + 60) * nrows, margin=dict(l=200, r=10, t=64, b=10))
        fig.update_xaxes(range=[0, ymax * 1.3], ticksuffix="%", showgrid=True)
    else:
        _base_layout(fig, 170 + 210 * nrows, margin=dict(l=40, r=10, t=64, b=10))
        fig.update_yaxes(range=[0, ymax * 1.28], ticksuffix="%", showgrid=True)
        fig.update_xaxes(showgrid=False)
    fig.update_annotations(font=dict(size=12, color=DARK_TEXT))
    fig.add_annotation(xref="paper", yref="paper", x=1, y=1, yshift=30, xanchor="right", yanchor="bottom",
                       showarrow=False, font=dict(size=11, color=_REF_GREY), text="▬ all respondents")
    return fig


def numeric_question_chart(q: dict, nums: pd.DataFrame, names: dict[str, str]) -> go.Figure:
    """Vertical bar per segment = average; dashed line = all respondents."""
    sub = nums[nums["code"] == q["code"]]
    segs = [s for s in sorted(names, key=int) if not sub[sub["segment"] == s].empty]
    vals = [float(sub[sub["segment"] == s]["mean"].iloc[0]) for s in segs]
    nn = {s: int(sub[sub["segment"] == s]["n_valid"].iloc[0]) for s in segs}
    allrow = sub[sub["segment"] == "All"]
    avg = float(allrow["mean"].iloc[0]) if not allrow.empty else None
    nn["All"] = int(allrow["n_valid"].iloc[0]) if not allrow.empty else 0
    return _vertical_segment_bars(names, segs, vals, [f"{v:.1f}" for v in vals], "Average", avg,
                                  f"All: {avg:.1f}" if avg is not None else "", "Average", q, nn)


RADAR_AXES = [("A101", "Age"), ("F606", "Personal income"), ("E506", "Weekly work hours"),
              ("B207", "Household size"), ("L1203", "Income sent to family")]


def radar_chart(nums: pd.DataFrame, names: dict[str, str]) -> go.Figure | None:
    """Spider web comparing segments on age, income and other numeric profile measures. Each axis is scaled
    so the highest-scoring segment is 100; hover shows the real average and sample size."""
    axes = [(c, l) for c, l in RADAR_AXES if not nums[nums["code"] == c].empty]
    if len(axes) < 3:
        return None
    segs = sorted(names, key=int)

    def _get(code, seg):
        r = nums[(nums["code"] == code) & (nums["segment"] == seg)]
        return (None, 0) if r.empty else (float(r["mean"].iloc[0]), int(r["n_valid"].iloc[0]))

    top = {c: max((_get(c, s)[0] or 0) for s in segs) or 1 for c, _ in axes}
    labels = [l for _, l in axes]
    fig = go.Figure()
    for s in segs + ["All"]:
        vals = [_get(c, s) for c, _ in axes]
        r = [(v[0] or 0) / top[c] * 100 for v, (c, _) in zip(vals, axes)]
        hover = [f"{l}: {v[0]:,.1f} (n={v[1]})" if v[0] is not None else l for v, l in zip(vals, labels)]
        is_all = s == "All"
        color = _REF_GREY if is_all else SEGMENT_COLORS[s]
        fig.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=labels + labels[:1], name="All respondents" if is_all else seg_name(s),
            mode="lines+markers", fill="none" if is_all else "toself",
            line=dict(color=color, width=2.4 if is_all else 2, dash="dash" if is_all else "solid"),
            fillcolor=None if is_all else _rgba(color, 0.16),
            marker=dict(size=5), text=hover + hover[:1], hovertemplate="<b>" + ("All respondents" if is_all else seg_name(s)) +
            "</b><br>%{text}<extra></extra>"))
    fig.update_layout(
        height=520, margin=dict(l=60, r=60, t=30, b=30), paper_bgcolor="white", dragmode=False,
        font=dict(family="sans-serif", color=DARK_TEXT, size=12),
        polar=dict(bgcolor="white", radialaxis=dict(range=[0, 110], showticklabels=False, gridcolor="#E2E5E0"),
                   angularaxis=dict(gridcolor="#E2E5E0")),
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
    return fig


def chart_kind(q: dict) -> str:
    if q["type"] == "numeric":
        return "numeric"
    if is_likert(q):
        return "likert"
    return "binary" if sum(1 for o in q["options"] if not o["non_answer"]) == 2 else "columns"


def question_chart(q: dict, dists: pd.DataFrame, nums: pd.DataFrame, names: dict[str, str]) -> go.Figure:
    """Vertical bars for numeric / yes-no, diverging bars for Likert scales, faceted panels per segment for
    everything else (vertical bars for short lists, horizontal bars for long ones)."""
    kind = chart_kind(q)
    if kind == "numeric":
        return numeric_question_chart(q, nums, names)
    return {"likert": likert_question_chart, "binary": binary_question_chart,
            "columns": columns_question_chart}[kind](q, dists, names)


# ---------------------------------------------------------------------------
# Respondents by county: bubble map (concentrations only, no drill-down)
# ---------------------------------------------------------------------------
# Approximate county centroids (lat, lon) - used only to place bubbles, not to draw boundaries.
COUNTY_CENTROIDS = {
    "mombasa": (-4.04, 39.67), "kwale": (-4.17, 39.45), "kilifi": (-3.51, 39.91), "tanariver": (-1.65, 39.65),
    "lamu": (-2.27, 40.90), "taitataveta": (-3.40, 38.36), "garissa": (-0.45, 39.65), "wajir": (1.75, 40.06),
    "mandera": (3.94, 41.86), "marsabit": (2.33, 37.99), "isiolo": (0.35, 37.58), "meru": (0.05, 37.65),
    "tharakanithi": (-0.30, 37.97), "embu": (-0.53, 37.46), "kitui": (-1.37, 38.01), "machakos": (-1.52, 37.26),
    "makueni": (-2.25, 37.62), "nyandarua": (-0.18, 36.52), "nyeri": (-0.42, 36.95), "kirinyaga": (-0.50, 37.28),
    "muranga": (-0.72, 37.15), "kiambu": (-1.03, 36.83), "turkana": (3.12, 35.60), "westpokot": (1.62, 35.12),
    "samburu": (1.17, 36.95), "transnzoia": (1.02, 34.95), "uasingishu": (0.55, 35.30),
    "elgeyomarakwet": (0.78, 35.51), "nandi": (0.18, 35.13), "baringo": (0.65, 35.97), "laikipia": (0.40, 36.78),
    "nakuru": (-0.30, 36.07), "narok": (-1.08, 35.87), "kajiado": (-2.10, 36.78), "kericho": (-0.37, 35.28),
    "bomet": (-0.78, 35.34), "kakamega": (0.28, 34.75), "vihiga": (0.07, 34.72), "bungoma": (0.57, 34.56),
    "busia": (0.43, 34.11), "siaya": (0.06, 34.29), "kisumu": (-0.09, 34.77), "homabay": (-0.53, 34.45),
    "migori": (-1.06, 34.47), "kisii": (-0.68, 34.77), "nyamira": (-0.57, 34.95), "nairobi": (-1.29, 36.82),
}


def _county_key(name: str) -> str:
    return _re.sub(r"[^a-z]", "", str(name).lower().replace("county", ""))


def unmatched_counties(counts: pd.DataFrame) -> list[str]:
    return [c for c in counts["county"] if _county_key(c) not in COUNTY_CENTROIDS]


def county_map(counts: pd.DataFrame) -> go.Figure:
    """Bubble map of respondents per county: bubble area = number of respondents."""
    df = counts[counts["county"].map(lambda c: _county_key(c) in COUNTY_CENTROIDS)].copy()
    df["lat"] = df["county"].map(lambda c: COUNTY_CENTROIDS[_county_key(c)][0])
    df["lon"] = df["county"].map(lambda c: COUNTY_CENTROIDS[_county_key(c)][1])
    top = float(df["n"].max()) if len(df) else 1.0
    fig = go.Figure(go.Scattergeo(
        lat=df["lat"], lon=df["lon"], mode="markers+text",
        text=df["county"].str.replace(" County", "", regex=False), textposition="top center",
        textfont=dict(size=11, color=DARK_TEXT),
        marker=dict(size=14 + 46 * (df["n"] / top) ** 0.5, color=BRAND, opacity=0.62,
                    line=dict(color="white", width=1.5)),
        customdata=df[["n", "pct"]].to_numpy(),
        hovertemplate="<b>%{text}</b><br>%{customdata[0]} respondents (%{customdata[1]}%)<extra></extra>",
    ))
    fig.update_geos(
        scope="africa", resolution=50, showcountries=True, countrycolor="#C9CDD6", showland=True,
        landcolor="#F6F7F5", showocean=True, oceancolor="#E6F2EE", showlakes=True, lakecolor="#E6F2EE",
        lataxis_range=[-5.2, 5.6], lonaxis_range=[33.4, 42.4], projection_type="mercator",
    )
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white", dragmode=False,
                      font=dict(family="sans-serif", color=DARK_TEXT))
    return fig
