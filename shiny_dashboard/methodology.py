"""Technical documentation shown on the Methodology page of both dashboards (exported to Next.js by
scripts/export_nextjs_data.py). Sources: the client report (project overview, segmentation model, driver
definitions, sizing notes) and how the aggregate files in precomputed/ were built.

Each section is {"title", "paras": [...], "bullets": [...]} ; DRIVER_DEFINITIONS is a table.
"""

from __future__ import annotations

SECTIONS = [
    {
        "title": "Study design",
        "paras": [
            "One mixed-methods study with two connected parts that shared one learning agenda and one set of drivers.",
        ],
        "bullets": [
            "Human-centred design (HCD) research: in-depth interviews and small group discussions with 51 young "
            "people in four locations (Nairobi, Kilifi, Kisumu and Narok). It identified the drivers that shape "
            "young people's livelihoods and produced draft personas and pathways.",
            "Survey: 1,221 young people in nine counties, August to September 2026. The questionnaire was built on "
            "the HCD findings, in young people's own words, and measured the drivers HCD identified.",
            "The two fed each other: HCD shaped which drivers the survey measured and how questions were worded; "
            "the survey tested the HCD personas, which were matched to the final segments.",
        ],
    },
    {
        "title": "How the segments were built",
        "bullets": [
            "Drivers: demographic, behavioural and psychometric measures were assessed with the HCD insights to find "
            "those that best separate young people's livelihood experiences (definitions below).",
            "Preparation: indicators were standardised or encoded, and measures with little power to tell groups "
            "apart were dropped. Highly correlated measures were reduced while keeping 90% of the information.",
            "Grouping: k-means clustering grouped young people with similar characteristics. Solutions with three "
            "to eight groups were tested and compared with latent class and hierarchical clustering, which gave less "
            "distinct groups. Six segments gave the clearest, most stable and most usable split.",
            "Survey sample by segment: Survival Workers 262, Stability Seekers 162, Income Pragmatists 304, Skill "
            "Investors 204, Credentialed Aspirants 78, Career Pursuers 211.",
        ],
    },
    {
        "title": "National size estimates",
        "paras": [
            "The number of young people in each segment nationally is a directional, model-based estimate, not a "
            "headcount. A classifier trained on the survey was applied to 2019 Kenya Population and Housing Census "
            "records for youth aged 16 to 30 (about 13.2 million) using characteristics both sources share: age, "
            "sex, education, economic activity, assets, living arrangement and migration. Each census record "
            "contributes its probability of belonging to each segment, with a correction so the predicted mix "
            "matches the survey. County is not a model input, and only nine counties were surveyed, so county "
            "figures are extrapolated.",
            "Because they are directional, estimates are shown rounded to the nearest 0.1 million: Survival "
            "Workers 4.3M (32%); Stability Seekers 1.3M (10%); Income Pragmatists 2.7M (20%); Skill Investors "
            "2.7M (21%); Credentialed Aspirants 0.5M (4%); Career Pursuers 1.8M (14%).",
        ],
    },
    {
        "title": "Weighting and representativeness",
        "paras": [
            "Survey results on this dashboard are not weighted. They describe the 1,221 young people interviewed. "
            "The nine counties were chosen by design, so results are not representative of each county or of Kenya "
            "as a whole, and some figures (for example living arrangements) may differ from official KNBS "
            "statistics. National segment sizes are the only population-level figures, and they come from the "
            "census-based model above.",
        ],
    },
    {
        "title": "Livelihood pathway stages",
        "paras": ["The pathway charts show the share of each segment that has reached each stage, using these survey "
                  "measures as proxies:"],
        "bullets": [
            "Educational preparation: finished secondary school or higher.",
            "Opportunity access: earning from work.",
            "Livelihood establishment: in paid employment or running a business.",
            "Upward investment: any training beyond school.",
            "Livelihood advancement: skills fully used at work.",
        ],
    },
    {
        "title": "Reading the figures",
        "bullets": [
            "Percentages are rounded to whole numbers on the dashboard; hover over a chart to see the number of "
            "people behind each figure.",
            "Answer shares for a segment are hidden when fewer than 30 people in that segment answered a question.",
            "Credentialed Aspirants is a small group in the survey (78 people), so read their figures with care.",
            "Some driver values on this dashboard use slightly different survey measures from the report's driver "
            "tables (see definitions below), so a few figures differ by a few points.",
        ],
    },
    {
        "title": "Self-assessment model",
        "paras": [
            "The 12-question self-assessment uses a multinomial logistic regression trained on the full labelled "
            "survey, using a short set of items selected with LASSO regularisation. It gives the segment a person "
            "most resembles, with a probability for each segment. Answers are scored in the browser or app and are "
            "not stored.",
        ],
    },
    {
        "title": "Tools and data",
        "bullets": [
            "Instruments: HCD discussion guides and the survey questionnaire. Every survey question and its answer "
            "options, by segment, is on the Deep dives tab.",
            "This dashboard holds only aggregate figures (shares, averages and counts by segment). It contains no "
            "respondent-level records or identifiers.",
            "Requests for the anonymised survey data can be directed to Imaginable Futures.",
        ],
    },
]

# Driver definitions (report: Segment driver definitions, slides 11-12). Type: Direct = the survey question
# matches the HCD definition; Proxy = the closest available question.
DRIVER_DEFINITIONS = [
    ("Demographic", "Gender", "Share of youth who are women.", "Direct"),
    ("Demographic", "Secondary completion", "Completed secondary school or a higher level.", "Direct"),
    ("Demographic", "Apprenticeship", "Main learning route was an informal apprenticeship or on-the-job learning.",
     "Proxy"),
    ("Demographic", "TVET", "Highest level is a TVET or vocational diploma (a lower bound on attendance).", "Proxy"),
    ("Demographic", "University", "Highest level is university or postgraduate.", "Proxy"),
    ("Demographic", "Family accommodation", "Lives in a parent's, relative's or spouse's household.", "Direct"),
    ("Demographic", "Family childcare support", "Among parents, has reliable childcare from any source.", "Proxy"),
    ("Demographic", "Dependants", "Number of people supported financially.", "Proxy"),
    ("Behavioural", "Work focus switching", "Number of changes in main livelihood focus.", "Proxy"),
    ("Behavioural", "Income diversification", "Number of income streams in the last 30 days.", "Direct"),
    ("Behavioural", "Informal upskilling", "Learned through an informal apprenticeship or self-teaching.", "Proxy"),
    ("Behavioural", "Formal upskilling", "Took formal TVET, short NGO or professional courses.", "Proxy"),
    ("Behavioural", "Friends/family networking", "Found current activity through family or friends.", "Proxy"),
    ("Behavioural", "Formal networking", "Found current activity by applying formally, online, or through a mentor, "
     "advert or agency.", "Proxy"),
    ("Behavioural", "Digital tool use", "Self-rated AI skill and how often AI is used for learning.", "Proxy"),
    ("Behavioural", "Savings", "Currently saving.", "Direct"),
    ("Psychometric", "Aspirational clarity", "Thinks they are likely to achieve their aspiration.", "Direct"),
    ("Psychometric", "Sense of agency", "Agrees success comes from hard work, not luck.", "Direct"),
    ("Psychometric", "Work is identity", "Draws identity from work (meaningful or enjoyable), rather than seeing it "
     "as a means to an end.", "Direct"),
    ("Psychometric", "Work supports wellbeing", "Among earners, says their main activity mostly supports their "
     "wellbeing.", "Direct"),
    ("Psychometric", "Gender-atypical work", "Does work seen as atypical for their gender (model uses men only).",
     "Proxy"),
    ("Psychometric", "Left work over mistreatment", "Has left a job over harsh conditions or harassment.", "Proxy"),
    ("Psychometric", "E2E pathway outcome", "Among those who pursued an education-to-earning pathway, calls it "
     "clearly worthwhile. Describes segments; not a model input.", "Proxy"),
]
