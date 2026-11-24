/** Colour theme, matching the Python dashboard (theme.py): UI chrome from the IF dashboard stylesheet and a
 *  4-shade palette per segment (dark -> light) matching the segment illustrations. Keys are the ANALYSIS segment
 *  codes used in the data files; segments are always listed in the client report's order (SEGMENT_IDS), never by
 *  code. Code -> name follows the report (see shiny_dashboard/segment_content.py). */
export const DARK_TEXT = "#1F2A24";
export const BRAND = "#0F6B52";
export const REF_GREY = "#4B5563";

/** Report order: Survival Workers, Stability Seekers, Income Pragmatists, Skill Investors, Credentialed
 *  Aspirants, Career Pursuers. */
export const SEGMENT_IDS = ["1", "4", "2", "3", "5", "6"] as const;

export const SEGMENT_PALETTES: Record<string, string[]> = {
  "1": ["#8E2C5A", "#D3618F", "#EDB2CB", "#F9E4ED"], // Survival Workers - pink
  "4": ["#990000", "#F94B4B", "#FFA8A7", "#FFE5E4"], // Stability Seekers - red
  "2": ["#B45F06", "#FAA62E", "#FEDCB2", "#FEF2E2"], // Income Pragmatists - orange
  "3": ["#38761D", "#2E9462", "#9DC9B2", "#E1EFE7"], // Skill Investors - green
  "5": ["#134F5C", "#4EC2BC", "#ACE0DE", "#E6F6F5"], // Credentialed Aspirants - teal
  "6": ["#351C75", "#665FF7", "#C9C7FD", "#E8E7FE"], // Career Pursuers - purple
};

export const SEGMENT_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SEGMENT_PALETTES).map(([s, p]) => [s, p[1]]),
);
export const SEGMENT_PILL_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SEGMENT_PALETTES).map(([s, p]) => [s, p[0]]),
);

export const SEGMENT_NAMES: Record<string, string> = {
  "1": "Survival Workers",
  "2": "Income Pragmatists",
  "3": "Skill Investors",
  "4": "Stability Seekers",
  "5": "Credentialed Aspirants",
  "6": "Career Pursuers",
};

/** 13-step diverging scheme (green = high/positive ... grey = neutral ... red = low/negative). */
export const DIVERGING = [
  "#00876C", "#42977F", "#66A793", "#87B6A7", "#A6C6BB", "#C6D6D0", "#E5E5E5",
  "#E8CBCB", "#E8B1B1", "#E69798", "#E27B7F", "#DC5F68", "#D43D51",
];

export const segName = (s: string | number): string => SEGMENT_NAMES[String(s)] ?? String(s);

/** Segment codes in the report's order (unknown codes last). */
export function orderSegments(segs: Iterable<string>): string[] {
  const rank = (s: string) => {
    const i = (SEGMENT_IDS as readonly string[]).indexOf(s);
    return i < 0 ? 99 : i;
  };
  return [...segs].map(String).sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
}

/** Round half away from zero: matches theme.r0 in the Python dashboard. */
export const r0 = (x: number): number => (x >= 0 ? Math.floor(x + 0.5) : -Math.floor(-x + 0.5));
