"""Build question_short_labels.json: short, number-free, descriptive labels for the Explore Questions page.

Reads only question_catalog.json (question wording - no respondent data) and writes
question_short_labels.json next to it in both dashboards' precomputed/ folders.

Edit SINGLE / STEMS / ORDINAL_GROUPS below and re-run to change a label:
    python scripts/build_short_labels.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIRS = [ROOT / "shiny_dashboard" / "precomputed", ROOT / "streamlit_dashboard" / "precomputed"]

# Items that are not meaningful as a chart (consent script; coded answers with no labels, where an
# "average" of the codes would mislead).
HIDDEN = {"A107", "A103", "C309_1", "C309_2", "C309_3", "C309_4", "G707"}

SINGLE = {
    "A101": "Age (years)", "A105": "Main activity these days",
    "A107": "Took part in the earlier interview/discussion study",
    "B201": "Gender", "B202": "Age confirmed (years)", "B204": "Marital status",
    "B206": "Children live in the same household", "B207": "People living in the household",
    "B208": "Relationship to household head", "B211": "Household type grown up in",
    "B214": "Where I currently live (household type)", "B216": "Household head's education",
    "B218": "Expected to financially support family ('black tax')", "B219": "Religion",
    "B220": "Long-term disability or health difficulty", "B222": "Main roofing material",
    "B223": "Main drinking-water source", "B224": "Type of shelter", "B225": "Household owns a television",
    "B226": "Main electricity source", "B227": "Post office in the area",
    "B229": "Years living in current place", "B230": "Main reason for moving here",
    "B231": "Household owns agricultural land", "B232": "Age when first living with a partner",
    "B233": "Self-rated health", "B235": "Eldest child or has older siblings",
    "B236": "Has a national ID or birth certificate",
    "B221_1": "Applies to me: lives in an ASAL / pastoralist area",
    "B221_2": "Applies to me: lives in an informal settlement",
    "B221_3": "Applies to me: refugee or asylum-seeker",
    "B221_4": "Applies to me: household hit by recent drought or flood",
    "B221_999": "Applies to me: none of these",
    "C301": "Currently enrolled in school or training", "C302": "Type of institution enrolled in",
    "C303": "Highest formal education completed", "C305": "Main reason stopped studying",
    "C307": "Major change in main activity since age 15",
    "C310": "Main barrier to returning to education or training",
    "C311": "Main reason for leaving past jobs",
    "D405": "Most missing from education and training support",
    "D406": "Paused training or education because of a shock",
    "D407": "Aware of Recognition of Prior Learning (RPL)",
    "E501": "Main activity right now", "E502": "Formal or informal work", "E504": "Income pattern, past 12 months",
    "E505": "Sector of main activity", "E506": "Weekly hours on main activity", "E507": "Has a side hustle",
    "E508": "Type of side hustle", "E509": "Main reason for the side hustle",
    "E510": "Work makes full use of my skills", "E511": "Role in main activity",
    "E512": "Months without any income-generating activity",
    "E513": "Stayed in same type of work or changed at last switch",
    "F601": "Income sources in the last 30 days", "F602": "Main source of income",
    "F603": "How income covers monthly needs", "F604": "Income regular over last six months",
    "F605": "Financial relationship with family", "F606": "Personal income last month (KES)",
    "F607": "Income is my own or shared with household",
    "G705": "Main reason for not taking an available job", "G706": "Expect to grow income in current work",
    "G708": "Too much competition makes work hard to find", "G709": "My own effort can get me dignified work",
    "G710": "Outside forces make dignified work hard to get", "G711": "Freedom to choose my livelihood",
    "G712": "Has own bank or financial account",
    "H802": "Expected change in livelihood over 3-5 years", "H803": "Equipped to cope if main income stopped",
    "H806": "Currently saving", "H807": "How often I save", "H809": "Member of a livelihood or savings group",
    "H810": "Ease of accessing formal financial services", "H811": "Reliable access to childcare",
    "H812": "Weekly hours of unpaid care or household work", "H813": "Priority when money is short",
    "H815": "Main barrier to relocating for an opportunity",
    "I901": "Success comes from hard work", "I902": "Confident I can recover from setbacks",
    "I903": "Confident I could start my own income activity",
    "I904": "Waiting for network tips beats searching myself",
    "I905": "Stop trying as hard after repeated setbacks",
    "I906": "Better to risk failure than not try", "I908": "Plan to achieve my aspiration",
    "I909": "Likelihood of achieving aspiration in 3-5 years", "I910": "Where I realistically expect to be in 3-5 years",
    "I911": "Where I would ideally like to be in 3-5 years", "I912": "Main source of work or livelihood stress",
    "J1002": "How community defines a successful young person", "J1003": "Livelihood improves or worsens wellbeing",
    "J1004": "Work has left me isolated from friends", "J1005": "Main source of support when stressed",
    "J1007": "How I responded to the setback", "J1008": "Willing to share struggles outside close circle",
    "J1009": "Used a public support service (counselling, helpline)",
    "K1101": "Income level of my close network", "K1102": "Better-off friends opened up opportunities",
    "K1103": "How I found my current main activity", "K1104": "Network helped me access opportunities",
    "K1105": "My close network acts in my best interest", "K1106": "Has a mentor for work or education",
    "K1107": "Avoided telling people what work I do", "K1108": "Whose advice matters most for my future",
    "K1109": "Family expectations limit the work I can pursue",
    "K1110": "Adulthood requires being able to provide financially",
    "K1111": "Income affects how attractive I seem as a partner",
    "K1112": "Has done work atypical for my gender", "K1113": "Community reaction to gender-atypical work",
    "K1114": "Pressure to provide led to leaving school early",
    "L1201": "Receives support from family or friends elsewhere", "L1202": "Sends support to family or dependants",
    "L1203": "Share of income sent to family each month (%)", "L1204": "Who decides on large household purchases",
    "L1206": "Most useful support source not yet used", "L1207": "Parental guidance during education-to-work",
    "L1208": "Gives younger people the guidance I wish I had",
    "M1301": "Owns a mobile phone", "M1302": "How often I use the internet",
    "M1303": "How often I use mobile money", "M1306": "Has used an AI tool for study, work or business",
    "M1307": "Main use of AI tools",
    "M1304_1": "AI skill: creating social media content", "M1304_2": "AI skill: learning and upskilling",
    "M1304_3": "AI skill: managing a business social media page", "M1304_4": "AI skill: job search, CV and personal brand",
    "M1304_5": "AI skill: online trading and freelancing",
    "M1305_1": "AI use: creating social media content", "M1305_2": "AI use: learning and upskilling",
    "M1305_3": "AI use: managing a business social media page", "M1305_4": "AI use: job search, CV and personal brand",
    "M1305_5": "AI use: online trading and freelancing",
}

# Multi-select / grid items whose catalog label is just the option text: "<stem>: <item>".
STEMS = {
    "C304": "Additional training", "D401": "Aware of", "D402": "Has used", "F601": "Income source (last 30 days)",
    "G701": "Makes a job dignified", "G702": "Problem experienced at work", "G703": "Community respect for",
    "G704": "Pay level", "H801": "Biggest risk (next 3-5 years)", "H804": "Event in last 2 years",
    "H805": "How we coped", "H808": "Borrowed from (last 6 months)", "I907": "Aspired occupation",
    "J1001": "Success in work means", "J1006": "Biggest regret", "L1205": "Turns to for support",
}
# Repeated slots: "<prefix> (1st)", "(2nd)", ...
ORDINAL_GROUPS = {
    "C308": ("Major change in main activity", "change"),
    "D403": ("How relevant for getting work", "programme used"),
    "D404": ("Worthwhile investment or missed opportunity", "programme used"),
}
ORD = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]


def _clean(label: str) -> str:
    label = re.sub(r"<[^>]+>", "", label)
    label = re.sub(r"\$\{[^}]*\}", "", label)
    paras = [p.strip() for p in re.split(r"\n\s*\n", label) if p.strip()]
    keep = [p for p in paras if not re.match(r"^\[?(ENUMERATOR|INTERVIEWER|NOTE)", p, re.I)]
    p = (keep or paras or [label])[0]
    p = re.sub(r"^[A-Z]\d{3,4}(_\d+)*[.:]?\s*", "", p)
    return re.sub(r"\s+", " ", p).strip()


def _item(label: str) -> str:
    s = _clean(label)
    if ": " in s:
        s = s.rsplit(": ", 1)[1]
    s = s.rstrip("? ").strip()
    if s.count("(") > s.count(")") or (len(s) > 46 and " (" in s):
        s = s.split(" (")[0]
    return s[0].upper() + s[1:] if s else s


def _fallback(label: str) -> str:
    s = _clean(label).rstrip("? ")
    s = s.strip("'\" ")
    return s if len(s) <= 90 else s[:87].rsplit(" ", 1)[0] + "..."


def build(catalog: list[dict]) -> dict:
    labels, fallbacks = {}, []
    for q in catalog:
        code = q["code"]
        if code in HIDDEN:
            continue
        base, _, suffix = code.partition("_")
        if code in SINGLE:
            labels[code] = SINGLE[code]
        elif base in ORDINAL_GROUPS and suffix.isdigit() and 1 <= int(suffix) <= len(ORD):
            prefix, noun = ORDINAL_GROUPS[base]
            labels[code] = f"{prefix} ({ORD[int(suffix) - 1]} {noun})"
        elif base in STEMS and suffix:
            labels[code] = f"{STEMS[base]}: {_item(q['label'])}"
        else:
            labels[code] = _fallback(q["label"])
            fallbacks.append(code)
    return {"labels": labels, "hidden": sorted(HIDDEN), "_fallbacks": fallbacks}


def main() -> None:
    catalog = json.loads((OUT_DIRS[0] / "question_catalog.json").read_text(encoding="utf-8"))
    out = build(catalog)
    for d in OUT_DIRS:
        (d / "question_short_labels.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out['labels'])} labels, {len(out['hidden'])} hidden; auto-fallback used for: {out['_fallbacks']}")


if __name__ == "__main__":
    main()
