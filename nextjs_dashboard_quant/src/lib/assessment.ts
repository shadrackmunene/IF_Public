/** Self-assessment scoring, run entirely in the browser. Mirrors questionnaire.py: each answer is converted to
 *  the exact code the model was trained on, one-hot encoded where the model was, and passed through the saved
 *  multinomial logistic regression (coefficients exported to model.json by scripts/export_nextjs_data.py). */
import type { Model } from "./types";

export const AGE_MIN = 18;
export const AGE_MAX = 30;
export const AGE_MESSAGE =
  `This tool is meant for young people aged ${AGE_MIN} to ${AGE_MAX}. Please enter an age between ${AGE_MIN} and ${AGE_MAX}.`;

type Raw = string | number;

/** Per-question conversion from the chosen option to the model's input value. */
const TRANSFORMS: Record<string, (raw: Raw) => Raw> = {
  I904: (r) => 6 - Number(r), // reverse-coded
  G711: (r) => 6 - Number(r), // reverse-coded
  networking_formal_methods: (r) => (r === "family" || r === "friend" ? 0 : 1),
  attended_college_university: (r) => (r === "university" ? 1 : 0),
  family_accommodation_support: (r) => (r === "family_household" ? 1 : 0),
  E504: (r) => String(r), // the model's encoder was fit on '1'..'4' as strings
};

export function toModelRow(answers: Record<string, Raw>): Record<string, Raw> {
  const row: Record<string, Raw> = {};
  for (const [id, raw] of Object.entries(answers)) row[id] = TRANSFORMS[id] ? TRANSFORMS[id](raw) : raw;
  return row;
}

export function score(model: Model, answers: Record<string, Raw>): { segment: string; probabilities: Record<string, number> } {
  const row = toModelRow(answers);
  const x = model.features.map((f) => {
    if (f.startsWith("num__")) return Number(row[f.slice(5)]);
    const body = f.slice(5); // "<column>_<category>"
    const cut = body.lastIndexOf("_");
    const col = body.slice(0, cut);
    const cat = body.slice(cut + 1);
    const v = row[col];
    const s = typeof v === "number" ? v.toFixed(1) : v; // one-hot categories for 0/1 columns are "0.0"/"1.0"
    return s === cat ? 1 : 0;
  });
  const logits = model.coef.map((w, k) => w.reduce((a, wi, i) => a + wi * x[i], model.intercept[k]));
  const m = Math.max(...logits);
  const exps = logits.map((l) => Math.exp(l - m));
  const z = exps.reduce((a, b) => a + b, 0);
  const probabilities: Record<string, number> = {};
  model.classes.forEach((c, k) => (probabilities[c] = exps[k] / z));
  const segment = Object.keys(probabilities).reduce((a, b) => (probabilities[a] >= probabilities[b] ? a : b));
  return { segment, probabilities };
}
