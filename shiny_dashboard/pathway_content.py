"""Authored per-segment pathway narrative content, taken from the study deliverable's "Pathways" section.
This is qualitative synthesis (HCD research + analyst interpretation of the survey) that cannot be
recomputed from the data, so it is reproduced as written rather than regenerated. The stage percentages
shown in the charts come from the pre-computed files.

The five pathway stages and their survey proxies (as documented in the deliverable):
  1. Educational Preparation - finished secondary or beyond (C303)
  2. Opportunity Access       - earning from work (E504 != "Not earning yet")
  3. Livelihood Establishment - in paid employment or running a business (E501)
  4. Upward Investment        - any training beyond school (C304)
  5. Livelihood Advancement   - skills fully used at work (E510)
"""

from __future__ import annotations

PATHWAY_STAGES = [
    "Educational Preparation",
    "Opportunity Access",
    "Livelihood Establishment",
    "Upward Investment",
    "Livelihood Advancement",
]

SEGMENT_CONTENT: dict[str, dict] = {
    "1": {
        "headline": "Still at the start, with one in three schooled to secondary and almost none trained further",
        "hcd_persona": "Work Drifter",
        "hcd_fit": 79,
        "hcd_runner_up": "Livelihood Sampler",
        "hcd_runner_up_fit": 52,
        "where_they_sit": [
            "34% finished secondary or beyond; 45% stopped at primary or earlier.",
            "44% are not earning: 16% are looking for work, 15% are neither working nor looking and 13% do unpaid family work.",
            "98% have had no training beyond school; 56% earn, but only 30% are in a paid job or business.",
        ],
        "what_would_help": [
            "Cost comes first: 50% name affordable cost or financing as the missing support.",
            "Re-entry: 48% stopped an E2E pathway after a shock and have not returned, the most of any segment.",
            "Direction is unclear: 19% are not sure of their next step, the most of any segment; 29% plan further training and 23% a business.",
            "Their own ask: jobs (42%) and access to skills training (23%); 28% regret dropping out of school.",
        ],
        "hcd_link": (
            "HCD places Work Drifters between Opportunity Access and Establishment; the survey agrees on "
            "Opportunity Access (56% earn) but only 30% have reached Establishment."
        ),
    },
    "2": {
        "headline": "Schooled and earning; Livelihood Establishment is the open step",
        "hcd_persona": None,
        "hcd_fit": None,
        "hcd_note": "No single persona leads - Livelihood Sampler (fit 70) and Purposeful Pivoter (66) are closest.",
        "where_they_sit": [
            "87% finished secondary or beyond, including 40% with a TVET qualification.",
            "81% are earning, but 39% have mixed or unpredictable income; 45% are in a paid job or business (24% self-employed, 21% paid) and 17% in casual labour.",
            "40% trained beyond school (21% formal TVET, 16% professional courses); 23% use their skills fully.",
        ],
        "what_would_help": [
            "Missing support: cost (50%) and job placement after training (29%).",
            "Resilience: 59% never had to stop a pathway; 62% feel equipped to respond to shocks.",
            "Ambition points two ways: 34% plan to start or expand a business, 23% to seek formal employment and 23% more training.",
            "Their own ask: jobs (53%) and grants or capital (16%); 46% of pathway-takers call it clearly worthwhile.",
        ],
        "hcd_link": (
            "HCD places the Sampler at Establishment and Upward Investment; the survey puts most of Segment 2 "
            "at Opportunity Access, with Establishment at 45%."
        ),
    },
    "3": {
        "headline": "Most are earning, but income is unstable and fewer than half are in a paid job or business",
        "hcd_persona": "Livelihood Sampler",
        "hcd_fit": 79,
        "hcd_runner_up": "Purposeful Pivoter",
        "hcd_runner_up_fit": 68,
        "where_they_sit": [
            "71% are earning: 39% in a paid job or business (19% self-employed, 21% paid), 15% in casual labour; 17% are still studying.",
            "37% have mixed or unpredictable income and 18% seasonal; 17% are salaried.",
            "49% trained beyond school, 28% through informal apprenticeship. Work is part of their identity for 100%.",
        ],
        "what_would_help": [
            "Shock recovery: 35% stopped an E2E pathway after a shock and have not returned; 49% never had to stop.",
            "Missing support: cost (48%) and job placement (25%).",
            "Plans: 37% more training, the most of any segment, and 23% a business.",
            "Their own ask: jobs (53%) and access to skills training (27%, the most of any segment); 28% regret dropping out of school.",
        ],
        "hcd_link": (
            "HCD places the Sampler at Establishment and Upward Investment; the survey puts most of Segment 3 "
            "at Opportunity Access, with 49% trained beyond school."
        ),
    },
    "4": {
        "headline": "Apprenticeship-trained and earning, but under half finished secondary and a quarter are in a paid job or business",
        "hcd_persona": "Work Drifter",
        "hcd_fit": 77,
        "hcd_runner_up": "Livelihood Sampler",
        "hcd_runner_up_fit": 71,
        "where_they_sit": [
            "100% trained beyond school, 96% through informal apprenticeship; 33% are in an apprenticeship now. 47% finished secondary.",
            "82% are earning, 51% on mixed or unpredictable income; 22% are in casual labour.",
            "25% are in a paid job or business and 37% use their skills fully.",
        ],
        "what_would_help": [
            "Recognition: 17% want informally learned skills recognised, the most of any segment; cost (43%) and placement (24%) also rank.",
            "Re-entry: 43% stopped a pathway after a shock and have not returned.",
            "Plans: 33% a business and 30% more training; only 10% plan to seek formal employment, the least of any segment.",
            "Their own ask: jobs (52%) and access to skills training (21%); 59% of pathway-takers call it clearly worthwhile.",
        ],
        "hcd_link": (
            "HCD places Drifters between Opportunity Access and Establishment; the survey agrees on "
            "Opportunity Access (82% earn), with 25% in a paid job or business."
        ),
    },
    "5": {
        "headline": "All hold a degree and most have reached Upward Investment; Advancement is the open step",
        "hcd_persona": "Progression Planner",
        "hcd_fit": 77,
        "hcd_runner_up": "Skill Investor",
        "hcd_runner_up_fit": 64,
        "where_they_sit": [
            "100% finished secondary or beyond (100% degree-level); 83% are earning.",
            "63% are in a paid job or business (36% self-employed, 27% paid); 51% of those working are in formal work, the most of any segment.",
            "54% trained beyond school (33% professional courses, 17% self-taught online); 35% use their skills fully.",
        ],
        "what_would_help": [
            "Missing support: job placement after training (41%, the most of any segment) and cost (36%).",
            "Resilience: 79% never had to stop a pathway, the most of any segment; 69% have a mentor.",
            "Plans: 33% seek formal employment, the most of any segment, and 28% a business.",
            "Their own ask: jobs (56%) and grants or capital (24%, the most of any segment). Base is small (n=78).",
        ],
        "hcd_link": (
            "HCD places the Planner from Establishment through Upward Investment toward Advancement; the "
            "survey agrees (63% in a paid job or business, 54% trained further, 35% skills fully used)."
        ),
    },
    "6": {
        "headline": "Formally networked and earning, but 41% are in a paid job or business despite 55% trained beyond school",
        "hcd_persona": "Purposeful Pivoter",
        "hcd_fit": 73,
        "hcd_runner_up": "Livelihood Sampler",
        "hcd_runner_up_fit": 66,
        "where_they_sit": [
            "76% finished secondary or beyond (27% TVET); 82% are earning, 43% on mixed or unpredictable income.",
            "41% are in a paid job or business (15% self-employed, 26% paid) and 25% in casual labour; everyone who found their current activity did so through formal channels.",
            "55% trained beyond school (20% informal apprenticeship, 15% formal TVET, 14% professional); 35% use their skills fully.",
        ],
        "what_would_help": [
            "Missing support: cost (46%) and job placement after training (26%).",
            "Resilience: 56% never had to stop a pathway; 24% stopped and have not returned.",
            "Plans: 31% a business, 23% more training and 19% formal employment.",
            "Their own ask: jobs (54%) and access to skills training (21%); 66% of pathway-takers call it clearly worthwhile, the most of any segment.",
        ],
        "hcd_link": (
            "HCD has Pivoters cycling at Opportunity Access on unstable work; the survey agrees (82% earn, "
            "43% on mixed income, 41% in a paid job or business)."
        ),
    },
}

# The five HCD personas' own emerging-pathway taglines (deck slides 62-66),
# shown alongside a segment's closest-fit persona for context - NOT a claim
# that the segment IS that persona (the deck is explicit this is an
# "exploratory resemblance check, not a statistical crosswalk").
PERSONA_TAGLINES: dict[str, str] = {
    "Work Drifter": "Resource-constrained · Reactive · Survival-oriented",
    "Livelihood Sampler": "Practical · Adaptive · Lifestyle-oriented",
    "Purposeful Pivoter": "Aspirational · Persistent · Stability-oriented",
    "Skill Investor": "Curious · Self-driven · Craft-oriented",
    "Progression Planner": "Focused · Self-directed · Career-oriented",
}
