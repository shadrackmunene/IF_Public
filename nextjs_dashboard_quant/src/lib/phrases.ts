/** Plain-language versions of the segmentation drivers: "About one in three have finished secondary school or
 *  higher (34%)" instead of "Finished secondary or higher 34%". Shares are read as the nearest simple fraction;
 *  100% and 0% read as "All" / "None" with no number. Scores read as a comparison ("Use AI for learning less often
 *  than any other segment"), with the number in brackets. */
import { r0 } from "./theme";

export type Rank = "highest" | "lowest" | "above" | "below";

const FRACTIONS: [number, string][] = [
  [10, "one in ten"], [20, "one in five"], [25, "one in four"], [100 / 3, "one in three"], [40, "two in five"],
  [50, "half"], [60, "three in five"], [200 / 3, "two in three"], [75, "three in four"], [80, "four in five"], [90, "nine in ten"],
];

/** "All", "Almost all", "About two in three", "Few", "Almost none", "None". */
export function shareWords(v: number, capital = false): string {
  let w: string;
  if (v >= 99.5) w = "all";
  else if (v >= 94.5) w = "almost all";
  else if (v <= 0.5) w = "none";
  else if (v < 5) w = "almost none";
  else if (v < 8) w = "few";
  else w = "about " + FRACTIONS.reduce((best, f) => (Math.abs(f[0] - v) < Math.abs(best[0] - v) ? f : best))[1];
  return capital ? w[0].toUpperCase() + w.slice(1) : w;
}

/** Percentage in brackets, or nothing when the words already say it exactly (all / none). */
const pctNote = (v: number) => (v >= 99.5 || v <= 0.5 ? "" : ` (${r0(v)}%)`);

/** What the share of the segment does, as a predicate after "About one in three ...". */
const PCT_PREDICATE: Record<string, string> = {
  "Gender (% women)": "are women",
  "Finished secondary or higher": "have finished secondary school or higher",
  "Attended apprenticeship": "have done an apprenticeship",
  "Attended TVET": "have attended TVET",
  "Attended college/university": "have been to college or university",
  "Living in family member's household": "live in a family member's household",
  "Switched livelihood focus at least once": "have switched livelihood at least once",
  "Formal upskilling": "build skills through formal training",
  "Informal-only upskilling": "build skills only informally",
  "Networks via friends/family only": "find work only through family and friends",
  "Networks via formal methods": "find work through formal channels",
  "Currently saving": "are saving",
  "Work is identity": "see work as part of who they are",
  "Work is a means to an end": "see work mainly as a means to an end",
  "Gender-atypical work (men)": "of the men work in jobs usually done by women",
  "Left a past job over poor working conditions": "have left a job over poor working conditions",
};

/** [higher, lower] comparisons for scores and counts. */
const SCORE_PHRASE: Record<string, [string, string]> = {
  "Age (years)": ["Older", "Younger"],
  "Number of income streams": ["Have more income streams", "Have fewer income streams"],
  "Number of financial dependants": ["Support more dependants", "Support fewer dependants"],
  "Livelihood selection autonomy (1-5)": ["Feel freer to choose their livelihood", "Feel less free to choose their livelihood"],
  "Opportunity searching (1-5, active)": ["Look for opportunities more actively", "Look for opportunities less actively"],
  "AI skill: learning (1-5)": ["Rate their skill at using AI for learning higher", "Rate their skill at using AI for learning lower"],
  "AI use frequency: learning (1-5)": ["Use AI for learning more often", "Use AI for learning less often"],
  "Aspirational clarity (1-5)": ["Are clearer about their goals", "Are less clear about their goals"],
  "Sense of agency (1-5)": ["Feel more in control of their future", "Feel less in control of their future"],
  "Wellbeing from livelihood (0-3)": ["Get more wellbeing from their livelihood", "Get less wellbeing from their livelihood"],
  "Risk appetite (1-5)": ["Are more willing to take risks", "Are less willing to take risks"],
  "Childcare access (among parents)": ["Have better access to childcare", "Have less access to childcare"],
};

const RANK_NOTE: Record<Rank, string> = {
  highest: "Highest of the six segments", lowest: "Lowest of the six segments", above: "Above average", below: "Below average",
};

export interface Phrase {
  lead: string; // the interpreted part, shown in bold ("About one in three", "Younger")
  rest: string; // the rest of the sentence, numbers in brackets
  note: string; // comparison line ("Lowest of the six segments; about two in three overall (65%)")
}

export function describe(label: string, isPct: boolean, value: number, all: number | undefined, rank: Rank): Phrase {
  if (isPct) {
    const pred = PCT_PREDICATE[label] ?? label.toLowerCase();
    const overall = all === undefined ? "" : `; ${shareWords(all)} of all young people surveyed${pctNote(all)}`;
    return { lead: shareWords(value, true), rest: ` ${pred}${pctNote(value)}`, note: RANK_NOTE[rank] + overall };
  }
  const [more, less] = SCORE_PHRASE[label] ?? [`Higher on ${label.toLowerCase()}`, `Lower on ${label.toLowerCase()}`];
  const up = rank === "highest" || rank === "above";
  const than = rank === "highest" || rank === "lowest" ? " than any other segment" : " than average";
  const scale = /\((\d)-(\d)/.exec(label);
  const fmt = (x: number) => x.toFixed(1);
  const nums = label.startsWith("Age")
    ? ` (average age ${fmt(value)}${all !== undefined ? `; overall ${fmt(all)}` : ""})`
    : ` (${fmt(value)}${scale ? ` out of ${scale[2]}` : " on average"}${all !== undefined ? `; overall ${fmt(all)}` : ""})`;
  return { lead: up ? more : less, rest: than + nums, note: "" };
}
