/** "What sets this segment apart": the two to four segmentation drivers on which a segment differs most from the
 *  other five, so each segment introduction shows its own variables rather than the same figures for every segment.
 *
 *  Score for a driver = average of (a) the gap between the segment and the mean of the other five and (b) the gap to
 *  the nearest other segment, both divided by the driver's scale (100 for percentages, the scale width for 1-5 and
 *  0-3 scores, 14 years for age, 4 for counts). (b) stops a value shared with other segments (e.g. 0% at university
 *  for four segments) from counting as distinctive. Drivers scoring at least MIN_SCORE are kept, up to MAX_ITEMS,
 *  with at least MIN_ITEMS shown for every segment. */
import type { DriverRow } from "./types";
import { SEGMENT_IDS } from "./theme";

const MIN_SCORE = 0.12;
const MIN_ITEMS = 2;
const MAX_ITEMS = 4;

/** Complementary drivers: only one of each pair is shown, the one on which the segment's value is higher. */
const PAIRS: [string, string][] = [
  ["Networks via friends/family only", "Networks via formal methods"],
  ["Work is identity", "Work is a means to an end"],
];
/** Too hard to read at a glance (coded access score among parents only). */
const SKIP = new Set(["Childcare access (among parents)"]);

export interface Distinct {
  label: string;
  isPct: boolean;
  value: number;
  all: number | undefined;
  vals: Record<string, number>; // the six segments
  rank: "highest" | "lowest" | "above" | "below";
  score: number;
  axis: [number, number]; // display range
}

function scoreScale(label: string, isPct: boolean): number {
  if (isPct) return 100;
  const m = /\((\d)-(\d)/.exec(label);
  if (m) return Number(m[2]) - Number(m[1]);
  return label.startsWith("Age") ? 14 : 4;
}

function displayAxis(label: string, isPct: boolean, values: number[]): [number, number] {
  if (isPct) return [0, 100];
  const m = /\((\d)-(\d)/.exec(label);
  if (m) return [Number(m[1]), Number(m[2])];
  if (label.startsWith("Age")) return [16, 30];
  return [0, Math.max(1, Math.ceil(Math.max(...values) + 0.5))];
}

export function distinguishing(drivers: DriverRow[], segment: string): Distinct[] {
  const rows = new Map<string, { isPct: boolean; vals: Record<string, number> }>();
  for (const r of drivers) {
    if (SKIP.has(r.label)) continue;
    const row = rows.get(r.label) ?? { isPct: r.is_pct, vals: {} };
    row.vals[r.segment] = r.value;
    rows.set(r.label, row);
  }

  const scored: Distinct[] = [];
  for (const [label, row] of rows) {
    const v = row.vals[segment];
    const others = SEGMENT_IDS.filter((s) => s !== segment && row.vals[s] !== undefined).map((s) => row.vals[s]);
    if (v === undefined || others.length < 2) continue;
    const mean = others.reduce((a, b) => a + b, 0) / others.length;
    const nearest = Math.min(...others.map((o) => Math.abs(o - v)));
    const score = (Math.abs(v - mean) + nearest) / 2 / scoreScale(label, row.isPct);
    const rank = v > Math.max(...others) ? "highest" : v < Math.min(...others) ? "lowest" : v >= mean ? "above" : "below";
    const six = Object.fromEntries(SEGMENT_IDS.filter((s) => row.vals[s] !== undefined).map((s) => [s, row.vals[s]]));
    scored.push({ label, isPct: row.isPct, value: v, all: row.vals["All"], vals: six, rank, score,
      axis: displayAxis(label, row.isPct, Object.values(six)) });
  }
  scored.sort((a, b) => b.score - a.score);

  const kept: Distinct[] = [];
  for (const item of scored) {
    const pair = PAIRS.find((p) => p.includes(item.label));
    if (pair) {
      if (kept.some((k) => pair.includes(k.label))) continue;
      const twin = scored.find((s) => s.label !== item.label && pair.includes(s.label));
      kept.push(twin && twin.value > item.value ? { ...twin, score: item.score } : item);
    } else kept.push(item);
  }
  const strong = kept.filter((k) => k.score >= MIN_SCORE).slice(0, MAX_ITEMS);
  return strong.length >= MIN_ITEMS ? strong : kept.slice(0, MIN_ITEMS);
}
