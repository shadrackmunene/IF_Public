"""The 12-item self-assessment questionnaire: natural-language question
text + response options for each of the mini-questionnaire's LASSO-selected
items, and a scoring
function that loads the saved model and predicts a segment from a
respondent's answers.

Each question's `code_map` translates the UI's chosen option (a short,
human string) to the EXACT numeric/categorical code the model was trained
on (src/segmentation/features.py's raw-field and derived-column
conventions) - getting this translation wrong would silently make the
self-assessment tool score against different inputs than the model learned
from, so every mapping here is a value already verified against this
survey's own choice lists, not re-guessed.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

# The fitted model ships with the app (deployed apps are self-contained).
MODEL_PATH = Path(__file__).resolve().parent / "model" / "mini_questionnaire_model.joblib"

_LIKERT_AGREE_OPTIONS = [
    ("Strongly disagree", 1), ("Disagree", 2), ("Neutral", 3), ("Agree", 4), ("Strongly agree", 5),
]

QUESTIONS = [
    {
        "id": "A101",
        "text": "What is your age in completed years?",
        "widget": "numeric",
        "min": 16, "max": 35, "value": 23,
    },
    {
        "id": "I904",
        "text": "“Waiting for my friends and family to tell me about available work is a better "
                "strategy for finding work than searching for it myself.”",
        "widget": "radio",
        "options": _LIKERT_AGREE_OPTIONS,
        # Model trained on the reverse-coded value (this item is scored so
        # that AGREEING with the statement above means LESS active
        # opportunity-searching) - reverse here: reverse_code = 6 - raw.
        "transform": lambda raw: 6 - raw,
    },
    {
        "id": "G711",
        "text": "On a scale of 1 (no freedom at all) to 5 (a lot of freedom), how much freedom do you have "
                "to decide what type of work you do, or what work opportunities you pursue?",
        "widget": "radio",
        "options": [
            ("No freedom at all", 1), ("Little freedom", 2), ("Neither a lot nor little freedom", 3),
            ("Some freedom", 4), ("A lot of freedom", 5),
        ],
        # Model trained on the reverse-coded value (lo+hi-raw = 6-raw, scale 1-5).
        "transform": lambda raw: 6 - raw,
    },
    {
        "id": "M1304_2",
        "text": "How knowledgeable do you consider yourself at using AI and social media to learn new "
                "skills or support upskilling?",
        "widget": "radio",
        "options": [
            ("Not knowledgeable at all", 1), ("Not knowledgeable", 2), ("Neutral", 3),
            ("Knowledgeable", 4), ("Very knowledgeable", 5),
        ],
    },
    {
        "id": "H806",
        "text": "Are you currently saving any money, in any form?",
        "widget": "radio",
        "options": [("Yes", 1), ("No", 0)],
    },
    {
        "id": "networking_formal_methods",
        "text": "How did you mainly find out about or access your current main activity (job, training, "
                "or business opportunity)?",
        "widget": "radio",
        "options": [
            ("Through a family member", "family"),
            ("Through a friend or peer", "friend"),
            ("Advertisement, noticeboard, or cold application", "formal_other"),
            ("Recruitment agency", "formal_other"),
            ("Social media or an online platform", "formal_other"),
            ("Government or NGO programme referral", "formal_other"),
            ("A mentor, teacher, or professional contact", "formal_other"),
        ],
        # Derived feature: 1 if found via a formal method (not family/friend), else 0.
        "transform": lambda raw: 0 if raw in ("family", "friend") else 1,
    },
    {
        "id": "attended_college_university",
        "text": "What is the highest level of formal education you have completed?",
        "widget": "radio",
        "options": [
            ("No formal education / primary", "below_secondary"),
            ("Secondary school", "secondary"),
            ("TVET / vocational certificate or diploma", "tvet"),
            ("University degree or postgraduate", "university"),
        ],
        "transform": lambda raw: 1 if raw == "university" else 0,
    },
    {
        "id": "family_accommodation_support",
        "text": "What is your relationship to the head of the household you currently live in?",
        "widget": "radio",
        "options": [
            ("I am the household head, or the spouse/partner of the head", "own_household"),
            ("Son/daughter, sibling, or other relative of the head", "family_household"),
            ("Not related to the head of household", "own_household"),
        ],
        "transform": lambda raw: 1 if raw == "family_household" else 0,
    },
    {
        "id": "E504",
        "text": "How would you best describe your income over the past 12 months?",
        "widget": "radio",
        "options": [
            ("Salaried/regular - similar amount at regular intervals", 1),
            ("Seasonal - depends heavily on time of year", 2),
            ("Mixed/unpredictable - varies a lot, hard to predict", 3),
            ("I'm not earning yet", 4),
        ],
        # The saved model's one-hot encoder was fit on this field as plain
        # strings ('1'..'4', confirmed directly against the fitted
        # OneHotEncoder's .categories_) - passing an int here would silently
        # encode as "unknown" (all-zero, handle_unknown="ignore") instead of
        # erroring, corrupting the prediction with no visible sign anything
        # was wrong.
        "transform": lambda raw: str(raw),
    },
    {
        "id": "I909",
        "text": "Think of a job or livelihood activity you'd ideally like to have. How likely do you think "
                "it is that you will actually achieve this in the next 3-5 years?",
        "widget": "radio",
        "options": [
            ("Very unlikely", 1), ("Unlikely", 2), ("Unsure", 3), ("Likely", 4), ("Very likely", 5),
        ],
    },
    {
        "id": "J1003",
        "text": "Thinking about your main livelihood activity, does it mostly improve or mostly worsen "
                "your overall wellbeing?",
        "widget": "radio",
        "options": [
            ("Mostly supports my wellbeing", 1), ("Mixed - some of both", 2),
            ("Mostly undermines my wellbeing", 3), ("I don't have an income-generating activity", 0),
        ],
    },
    {
        "id": "work_is_identity",
        "text": "What does ‘success’ in your work/livelihood mean to YOU personally? (choose the "
                "one that fits best)",
        "widget": "radio",
        "options": [
            ("Doing work I enjoy or find meaningful", 1),
            ("Earning enough / financial independence / stability / providing for family", 0),
            ("Social status or respect", 0),
        ],
    },
]

_QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}


def answers_to_model_row(answers: dict[str, object]) -> pd.DataFrame:
    """Convert {question_id: chosen_option_value} into the single-row,
    model-ready DataFrame the saved pipeline expects (same column names/
    dtypes build_feature_matrix produced during training)."""
    row = {}
    for qid, raw_value in answers.items():
        question = _QUESTION_BY_ID[qid]
        transform = question.get("transform")
        row[qid] = transform(raw_value) if transform else raw_value
    return pd.DataFrame([row])


def score(answers: dict[str, object]) -> dict:
    """Returns {"segment": predicted label, "probabilities": {segment: prob}}."""
    bundle = joblib.load(MODEL_PATH)
    pipeline = bundle["pipeline"]
    row = answers_to_model_row(answers)[bundle["item_names"]]
    proba = pipeline.predict_proba(row)[0]
    classes = bundle["classes"]
    probabilities = {str(c): float(p) for c, p in zip(classes, proba)}
    predicted = max(probabilities, key=probabilities.get)
    return {"segment": predicted, "probabilities": probabilities}
