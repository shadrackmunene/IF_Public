# Real Livelihoods Youth Segmentation Dashboard (Python Shiny)

Three pages:

1. **Overview**: descriptive findings across all 1,221 survey respondents.
2. **Segment Profiles**: pick any of the 6 segments; see its demographic, behavioural and psychographic driver
   profile and its position on the 5-stage livelihood pathway.
3. **Self-Assessment**: the 12-item questionnaire, scored by the saved logistic-regression model, with the matching
   segment's profile and growth-pathway narrative shown back to the respondent.

## Run it

```bash
*Create a virtual Environment first
python -m venv venv
Activate the virtual environment
*Powershell
venv\Scripts\Activate.ps1
*Windows
venv\Scripts\Activate.bat
*MacOS
source venv/bin/activate
*Install the packages
pip install -r requirements.txt
shiny run app.py
```

Then open the URL it prints (defaults to `http://127.0.0.1:8000`).

## What is in this folder

- `precomputed/`: aggregate-only summary statistics the charts are drawn from (no respondent-level data).
- `model/mini_questionnaire_model.joblib`: the fitted self-assessment model. Data and model are loaded once at
  start-up, so restart the app after replacing either.
- `pathway_content.py`: segment narratives and pathway text, reproduced from the study deliverable.
- `theme.py`, `www/styles.css`: colours matching the deliverable deck.
