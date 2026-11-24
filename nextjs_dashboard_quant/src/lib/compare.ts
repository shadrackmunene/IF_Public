/** Segment comparison helpers (port of shiny_dashboard/compare.py): driver rows across segments, value
 *  formatting, and the drivers on which one segment is clearly the highest or lowest of the six. */
import type { DriverRow } from "./types";
import { orderSegments, r0 } from "./theme";

export const CATEGORY_TITLES: Record<string, string> = {
  Demographic: "Demographic: what circumstances do they start with?",
  Behavioral: "Behavioural: what do they do to earn and get ahead?",
  Psychographic: "Psychometric: how do they think about work and the future?",
};

export const fmtValue = (v: number | null | undefined, isPct: boolean): string =>
  v === null || v === undefined || Number.isNaN(v) ? "–" : isPct ? `${r0(v)}%` : v.toFixed(1);

export interface DriverLine { label: string; isPct: boolean; vals: Record<string, number> }

export function driverRows(drivers: DriverRow[]): { segs: string[]; groups: { cat: string; rows: DriverLine[] }[] } {
  const segs = orderSegments(new Set(drivers.map((r) => r.segment).filter((s) => s !== "All")));
  const groups = Object.keys(CATEGORY_TITLES).map((cat) => {
    const sub = drivers.filter((r) => r.category === cat);
    const labels = [...new Set(sub.map((r) => r.label))];
    const rows = labels.map((label) => {
      const part = sub.filter((r) => r.label === label);
      return { label, isPct: part[0].is_pct, vals: Object.fromEntries(part.map((r) => [r.segment, r.value])) };
    });
    return { cat, rows };
  });
  return { segs, groups };
}

const MAX_DEFINING = 6;

export interface Defining {
  label: string; which: "highest" | "lowest"; value: string; all: string; score: number;
  raw: number; rawAll: number | undefined; isPct: boolean;
}

/** Drivers on which the segment is clearly the highest or lowest of the six (ties excluded), most distinctive
 *  first: ranked by the gap to the next segment as a share of the driver's range. */
export function definingDrivers(drivers: DriverRow[], segment: string): Defining[] {
  const { segs, groups } = driverRows(drivers);
  const found: Defining[] = [];
  for (const g of groups) {
    for (const row of g.rows) {
      const v = row.vals[segment];
      const others = segs.filter((s) => s !== segment && row.vals[s] !== undefined).map((s) => row.vals[s]);
      if (v === undefined || !others.length) continue;
      const all = [v, ...others];
      const spread = Math.max(...all) - Math.min(...all);
      let which: "highest" | "lowest" | null = null;
      let gap = 0;
      if (v > Math.max(...others)) { which = "highest"; gap = v - Math.max(...others); }
      else if (v < Math.min(...others)) { which = "lowest"; gap = Math.min(...others) - v; }
      if (!which) continue;
      found.push({ label: row.label, which, value: fmtValue(v, row.isPct), all: fmtValue(row.vals["All"], row.isPct),
        score: spread ? gap / spread : 0, raw: v, rawAll: row.vals["All"], isPct: row.isPct });
    }
  }
  return (["highest", "lowest"] as const).flatMap((w) =>
    found.filter((f) => f.which === w).sort((a, b) => b.score - a.score).slice(0, MAX_DEFINING));
}
