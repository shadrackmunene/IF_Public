"""Headline statistic cards for the Overview page, shared logic with the Next.js port (lib/overviewCards.ts):
a tinted background per group and an icon on every card, so the figures scan quickly.

Kept deliberately short (feedback of 16.11.2026): whole-number percentages, and figures that need method
context (household arrangement, enrolment, banking and daily-use measures) are left to the Deep dives tab.
"""

from __future__ import annotations

from html import escape

from theme import SEGMENT_PALETTES, r0


def groups(o: dict) -> list[dict]:
    """Four overview groups. Each card is (title, value, subtitle, icon)."""
    pct = lambda k: f"{r0(o[k])}%"  # noqa: E731
    return [
        {"title": "Who they are", "palette": SEGMENT_PALETTES["5"], "cards": [
            ("Median age", f"{r0(o['median_age'])}", "years", "🎂"),
            ("Women", pct("pct_female"), "of young people surveyed", "👩"),
            ("Median income", f"KES {r0(o['median_income'] / 1000)}K", "per month, own income", "💰"),
        ]},
        {"title": "Education & skills", "palette": SEGMENT_PALETTES["3"], "cards": [
            ("Secondary", pct("pct_secondary_highest"), "secondary school is their highest level", "🏫"),
            ("TVET", pct("pct_tvet"), "completed TVET or vocational training", "🛠️"),
            ("University", pct("pct_university"), "completed a university degree", "🎓"),
        ]},
        {"title": "Work & money", "palette": SEGMENT_PALETTES["2"], "cards": [
            ("Informal work", pct("pct_informal_main"), "of those working are in informal work", "🧰"),
            ("Side income", pct("pct_side_activity"), "have a second income activity", "➕"),
            ("Saving", pct("pct_saving"), "are saving money in any form", "🐖"),
        ]},
        {"title": "Digital & AI", "palette": SEGMENT_PALETTES["6"], "cards": [
            ("Smartphone", pct("pct_smartphone"), "own a smartphone", "📱"),
            ("AI tools", pct("pct_used_ai"), "have used an AI tool", "🤖"),
        ]},
    ]


def cards_html(cards: list[tuple], palette: list[str]) -> str:
    dark, mid, _, light = palette
    out = []
    for title, value, subtitle, icon in cards:
        out.append(
            f'<div class="stat-card" style="background:{light};border-color:{mid}55">'
            f'<div class="stat-icon" style="background:{mid}33;color:{dark}">{icon}</div>'
            f'<div class="stat-body"><div class="stat-label">{escape(title)}</div>'
            f'<div class="stat-value" style="color:{dark}">{escape(str(value))}</div>'
            f'<div class="stat-sub">{escape(subtitle)}</div></div></div>'
        )
    return '<div class="stat-grid">' + "".join(out) + "</div>"
