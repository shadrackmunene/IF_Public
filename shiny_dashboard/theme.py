"""Colour theme. UI chrome (brand, text, background) follows the IF dashboard stylesheet. Each of the six
segments has its own 4-shade palette (dark -> light) so Likert and stacked charts can use graded shades of the
segment's hue. Segment colours match the segment illustrations in www/ (and the client report).

Keys are the analysis segment codes used in the data files; see segment_content.py for the code -> report
mapping. Segments are always listed in the report's order (SEGMENT_ORDER), never by code.
"""

from __future__ import annotations

from segment_content import NAMES, ORDER

DARK_TEXT = "#1F2A24"      # text
WHITE = "#FFFFFF"
BRAND = "#0F6B52"          # --brand - headers, key figures
LIGHT_BG = "#F6F7F5"       # --bg - page background

SEGMENT_PALETTES = {
    "1": ["#8E2C5A", "#D3618F", "#EDB2CB", "#F9E4ED"],  # Survival Workers - pink
    "4": ["#990000", "#F94B4B", "#FFA8A7", "#FFE5E4"],  # Stability Seekers - red
    "2": ["#B45F06", "#FAA62E", "#FEDCB2", "#FEF2E2"],  # Income Pragmatists - orange
    "3": ["#38761D", "#2E9462", "#9DC9B2", "#E1EFE7"],  # Skill Investors - green
    "5": ["#134F5C", "#4EC2BC", "#ACE0DE", "#E6F6F5"],  # Credentialed Aspirants - teal
    "6": ["#351C75", "#665FF7", "#C9C7FD", "#E8E7FE"],  # Career Pursuers - purple
}

# Main chart colour per segment (the palette's second shade) and a dark shade for text-on-colour pills.
SEGMENT_COLORS = {s: p[1] for s, p in SEGMENT_PALETTES.items()}
SEGMENT_PILL_COLORS = {s: p[0] for s, p in SEGMENT_PALETTES.items()}

SEGMENT_ORDER = list(ORDER)
SEGMENT_NAMES = dict(NAMES)

CATEGORY_COLORS = {
    "Demographic": "#5073F3",
    "Behavioral": "#46C781",
    "Psychographic": "#D3618F",
}


def order_segments(segments) -> list[str]:
    """Segment codes in the report's order (unknown codes last, by code)."""
    rank = {s: i for i, s in enumerate(SEGMENT_ORDER)}
    return sorted((str(s) for s in segments), key=lambda s: (rank.get(s, 99), s))


def r0(x: float) -> int:
    """Round half away from zero, so Python and the Next.js port (Math.round) agree on .5 cases."""
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)
