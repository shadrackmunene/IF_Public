"""Colour theme taken from the Real Livelihoods Youth Segmentation Study deliverable deck's own PowerPoint
theme colour scheme, so the dashboard matches the deck.
"""

from __future__ import annotations

DARK_TEXT = "#414144"      # dk1
WHITE = "#FFFFFF"          # lt1
BRAND = "#881946"          # dk2 - primary brand colour (headers, key figures)
LIGHT_BG = "#F1F3F9"       # lt2 - panel/card backgrounds

# Six-colour categorical palette (accent1-6) - used for the six segments, in
# this fixed order, consistently across every chart so "Segment 3" is always
# the same colour everywhere in the app.
SEGMENT_COLORS = {
    "1": "#D3618F",  # accent1
    "2": "#00A7CC",  # accent2
    "3": "#FFAB15",  # accent3
    "4": "#46C781",  # accent4
    "5": "#5073F3",  # accent5
    "6": "#FF801F",  # accent6
}
SEGMENT_COLOR_LIST = [SEGMENT_COLORS[str(i)] for i in range(1, 7)]

CATEGORY_COLORS = {
    "Demographic": "#5073F3",
    "Behavioral": "#46C781",
    "Psychographic": "#D3618F",
}
