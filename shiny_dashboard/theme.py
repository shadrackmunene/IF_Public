"""Colour theme. UI chrome (brand, text, background) follows the IF dashboard stylesheet
(IF Analysis/dashboard/styles.css). Each of the six segments has its own 4-shade palette
(dark -> light) so Likert and stacked charts can use graded shades of the segment's hue.
"""

from __future__ import annotations

DARK_TEXT = "#1F2A24"      # text
WHITE = "#FFFFFF"
BRAND = "#0F6B52"          # --brand - headers, key figures
LIGHT_BG = "#F6F7F5"       # --bg - page background

# Per-segment palettes, darkest -> lightest. Segments 2-5 and 6 use the supplied palettes; segment 1
# keeps its original pink family (extended to four shades in the same style).
SEGMENT_PALETTES = {
    "1": ["#8E2C5A", "#D3618F", "#EDB2CB", "#F9E4ED"],  # pink (original hue)
    "2": ["#134F5C", "#4EC2BC", "#ACE0DE", "#E6F6F5"],  # teal
    "3": ["#B45F06", "#FAA62E", "#FEDCB2", "#FEF2E2"],  # orange
    "4": ["#38761D", "#2E9462", "#9DC9B2", "#E1EFE7"],  # green
    "5": ["#351C75", "#665FF7", "#C9C7FD", "#E8E7FE"],  # purple
    "6": ["#990000", "#F94B4B", "#FFA8A7", "#FFE5E4"],  # red
}

# Main chart colour per segment (the palette's second shade) and a dark shade for text-on-colour pills.
SEGMENT_COLORS = {s: p[1] for s, p in SEGMENT_PALETTES.items()}
SEGMENT_PILL_COLORS = {s: p[0] for s, p in SEGMENT_PALETTES.items()}
SEGMENT_COLOR_LIST = [SEGMENT_COLORS[str(i)] for i in range(1, 7)]

CATEGORY_COLORS = {
    "Demographic": "#5073F3",
    "Behavioral": "#46C781",
    "Psychographic": "#D3618F",
}

# Agreed segment names - used wherever a segment is shown (never "Segment 1, 2, 3...").
SEGMENT_NAMES = {
    "1": "Survival workers", "2": "Stability Seekers", "3": "Income Pragmatists",
    "4": "Skill Investors", "5": "Credentialed Aspirants", "6": "Career Pursuers",
}
