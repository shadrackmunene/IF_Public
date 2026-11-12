"""Overview statistic cards shared by the Shiny and Streamlit apps: a tinted background per group and an icon
on every card, so the figures scan quickly. Colours come from the segment palettes in theme.py."""

from __future__ import annotations

from html import escape

from theme import SEGMENT_PALETTES


def groups(o: dict) -> list[dict]:
    """The five overview groups. Each card is (title, value, subtitle, icon)."""
    return [
        {"title": "Youth & household profile", "palette": SEGMENT_PALETTES["2"], "cards": [
            ("Median age", f"{o['median_age']:.0f}", "years (16-30 range)", "🎂"),
            ("Female", f"{o['pct_female']}%", f"Male: {100 - o['pct_female']:.1f}%", "👩"),
            ("Independent household", f"{o['pct_own_household']}%", "live in own/rented household", "🏠"),
        ]},
        {"title": "Education & skills pathway", "palette": SEGMENT_PALETTES["5"], "cards": [
            ("Not currently enrolled", f"{o['pct_not_enrolled']}%", "in any education/training", "📚"),
            ("Secondary (highest)", f"{o['pct_secondary_highest']}%", "completed KCSE as highest level", "🏫"),
            ("TVET/vocational", f"{o['pct_tvet']}%", "completed TVET training", "🛠️"),
            ("University", f"{o['pct_university']}%", "completed a university degree", "🎓"),
        ]},
        {"title": "Current livelihoods", "palette": SEGMENT_PALETTES["3"], "cards": [
            ("Informal work", f"{o['pct_informal_main']}%", "of those currently working", "🧰"),
            ("Side activity", f"{o['pct_side_activity']}%", "have a supplementary income activity", "➕"),
            ("Self-employed", f"{o['pct_self_employed']}%", "main activity is running a business", "🏪"),
        ]},
        {"title": "Income & financial security", "palette": SEGMENT_PALETTES["4"], "cards": [
            ("Median income", f"KES {o['median_income']:,.0f}", "per month, personal income", "💰"),
            ("Currently saving", f"{o['pct_saving']}%", "saving money in any form", "🐖"),
            ("Bank account", f"{o['pct_bank_account']}%", "have a personal bank/financial account", "🏦"),
        ]},
        {"title": "Digital economy & AI", "palette": SEGMENT_PALETTES["6"], "cards": [
            ("Smartphone", f"{o['pct_smartphone']}%", "own a smartphone", "📱"),
            ("Internet daily", f"{o['pct_internet_daily']}%", "access the internet daily", "🌐"),
            ("Mobile money daily", f"{o['pct_mobile_money_daily']}%", "use mobile money daily", "💸"),
            ("Used an AI tool", f"{o['pct_used_ai']}%", "have ever used an AI tool", "🤖"),
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
