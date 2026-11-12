/** Helpers over the dashboard data bundle: sections, topics, county summary, national estimates. */
import type { Dashboard, Question } from "./types";
import { questionTitle } from "./plots";

export const DIMENSION_ORDER = ["Behaviour", "Context", "Psychology"];
export const ALL_TOPICS = "__all__";
export const INDIVIDUAL = "Individual questions";
export const MIN_COUNTY_N = 10; // must match scripts/aggregate_for_dashboard.py

export const dataUrl = (file: string) => `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/data/${file}`;

export const dimensions = (d: Dashboard) =>
  DIMENSION_ORDER.filter((dim) => d.catalog.some((q) => q.dimension === dim));

export function sectionsFor(d: Dashboard, dimension: string): string[] {
  const seen: string[] = [];
  for (const q of d.catalog) if (q.dimension === dimension && !seen.includes(q.section)) seen.push(q.section);
  return seen;
}

export const questionsFor = (d: Dashboard, dimension: string, section: string): Question[] =>
  d.catalog.filter((q) => q.dimension === dimension && q.section === section);

/** The group a question belongs to: text before ':' for multi-part items, the prefix before the '(1st ...)'
 *  marker for repeated items, otherwise 'Individual questions'. */
export function topicOf(q: Question): string {
  const t = q.short || q.label;
  if (t.includes(": ")) return t.split(": ")[0];
  const m = /^(.*?) \(\d+(?:st|nd|rd|th) [a-z ]+\)$/.exec(t);
  return m ? m[1] : INDIVIDUAL;
}

/** [topic, number of questions] in first-appearance order, 'Individual questions' last. */
export function topicsFor(d: Dashboard, dimension: string, section: string): [string, number][] {
  const counts = new Map<string, number>();
  for (const q of questionsFor(d, dimension, section)) counts.set(topicOf(q), (counts.get(topicOf(q)) ?? 0) + 1);
  const out = [...counts].filter(([t]) => t !== INDIVIDUAL);
  if (counts.has(INDIVIDUAL)) out.push([INDIVIDUAL, counts.get(INDIVIDUAL)!]);
  return out;
}

export function filterQuestions(
  d: Dashboard, dimension: string, section: string, topic: string, search: string, kind: string,
  isLikert: (q: Question) => boolean,
): Question[] {
  let qs = questionsFor(d, dimension, section);
  if (topic && topic !== ALL_TOPICS && topicsFor(d, dimension, section).some(([t]) => t === topic)) {
    qs = qs.filter((q) => topicOf(q) === topic);
  }
  const term = search.trim().toLowerCase();
  if (term) qs = qs.filter((q) => questionTitle(q).toLowerCase().includes(term));
  if (kind === "likert") qs = qs.filter(isLikert);
  if (kind === "other") qs = qs.filter((q) => !isLikert(q));
  return qs;
}

/** Short text on where a segment is most prevalent, ranked by its share of respondents in each county. */
export function countySummary(d: Dashboard, segment: string, top = 3): string | null {
  const sub = d.prevalence.filter((r) => r.segment === segment && r.n_county >= 15)
    .sort((a, b) => b.pct_of_county - a.pct_of_county).slice(0, top);
  if (!sub.length) return null;
  return "Most prevalent in " + sub.map((r) => `${r.county} (${r.pct_of_county.toFixed(0)}% of respondents there)`).join(", ") + ".";
}

export function populationEstimate(d: Dashboard, segment: string) {
  const row = d.population?.national.find((r) => r.segment === segment);
  return row && d.population ? { n: row.count, pct: row.pct, total: d.population.total_youth, note: d.population.note ?? "" } : null;
}
