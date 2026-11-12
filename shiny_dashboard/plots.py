"""Matplotlib chart builders shared by the Overview, Segment Profiles and
Self-Assessment pages - kept separate from app.py so the same chart code is
reusable across pages without duplicating styling."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from theme import BRAND, DARK_TEXT, LIGHT_BG, SEGMENT_COLORS

plt.rcParams.update({
    "font.family": "sans-serif",
    "text.color": DARK_TEXT,
    "axes.edgecolor": "#CCCCCC",
    "axes.labelcolor": DARK_TEXT,
    "xtick.color": DARK_TEXT,
    "ytick.color": DARK_TEXT,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def segment_size_chart(sizes: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    colors = [SEGMENT_COLORS[s] for s in sizes["segment"]]
    bars = ax.bar(sizes["segment"].map(lambda s: f"Segment {s}"), sizes["pct"], color=colors)
    for bar, pct, n in zip(bars, sizes["pct"], sizes["n"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{pct}%\n(n={n})",
                ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("% of respondents")
    ax.set_ylim(0, max(sizes["pct"]) * 1.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def driver_bar_chart(driver_table: pd.DataFrame, category: str, highlight_segment: str | None = None):
    """Horizontal grouped bars: one row per driver in `category`, segment
    value vs. the 'All' sample value, for the currently-selected segment.

    Value labels are drawn directly on each bar (not a hover tooltip -
    these charts are static matplotlib images, so a label that's always
    visible is the reliable choice over interactive hover, which would
    need a JS charting library this environment has no browser to verify
    actually works)."""
    sub = driver_table[driver_table["category"] == category]
    labels = sub["label"].unique().tolist()
    is_pct_by_label = {lbl: sub[sub["label"] == lbl]["is_pct"].iloc[0] for lbl in labels}

    def _fmt(val) -> str:
        if val is None:
            return ""
        return f"{val:.0f}%" if is_pct_by_label[lbl] else f"{val:.2f}"

    fig, ax = plt.subplots(figsize=(7.5, max(2.2, 0.5 * len(labels))))
    y = range(len(labels))

    all_vals = [sub[(sub["label"] == lbl) & (sub["segment"] == "All")]["value"].iloc[0] for lbl in labels]
    seg_vals = None
    if highlight_segment:
        seg_vals = [
            sub[(sub["label"] == lbl) & (sub["segment"] == highlight_segment)]["value"]
            .pipe(lambda s: s.iloc[0] if not s.empty else None)
            for lbl in labels
        ]

    max_val = max([v for v in all_vals if v is not None] + [v for v in (seg_vals or []) if v is not None], default=1)
    label_offset = max_val * 0.02

    height = 0.32
    ax.barh([yy + height / 2 for yy in y], all_vals, height=height, color="#C9CDD6", label="All respondents")
    for yy, lbl, val in zip(y, labels, all_vals):
        ax.text(val + label_offset, yy + height / 2, _fmt(val), va="center", ha="left", fontsize=8, color=DARK_TEXT)

    if seg_vals is not None:
        color = SEGMENT_COLORS.get(highlight_segment, BRAND)
        ax.barh([yy - height / 2 for yy in y], seg_vals, height=height, color=color,
                label=f"Segment {highlight_segment}")
        for yy, lbl, val in zip(y, labels, seg_vals):
            ax.text((val or 0) + label_offset, yy - height / 2, _fmt(val), va="center", ha="left",
                    fontsize=8, fontweight="bold", color=DARK_TEXT)

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max_val * 1.22)  # headroom for the end-of-bar labels
    ax.legend(fontsize=8, loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def pathway_stage_chart(stage_table: pd.DataFrame, segment: str):
    from pathway_content import PATHWAY_STAGES

    sub = stage_table[stage_table["segment"] == segment].set_index("stage").loc[PATHWAY_STAGES]
    fig, ax = plt.subplots(figsize=(7, 3))
    color = SEGMENT_COLORS.get(segment, BRAND)
    bars = ax.bar(range(len(PATHWAY_STAGES)), sub["pct"], color=color)
    for bar, pct in zip(bars, sub["pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{pct}%", ha="center", fontsize=9)
    ax.set_xticks(range(len(PATHWAY_STAGES)))
    ax.set_xticklabels([s.replace(" ", "\n") for s in PATHWAY_STAGES], fontsize=8)
    ax.set_ylabel("% of segment meeting stage proxy")
    ax.set_ylim(0, 105)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def probability_chart(probabilities: dict[str, float]):
    segs = sorted(probabilities.keys(), key=int)
    vals = [100 * probabilities[s] for s in segs]
    colors = [SEGMENT_COLORS[s] for s in segs]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    bars = ax.bar([f"Segment {s}" for s in segs], vals, color=colors)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{v:.0f}%", ha="center", fontsize=9)
    ax.set_ylabel("Match probability (%)")
    ax.set_ylim(0, 105)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig
