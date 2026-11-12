/** Colour theme, matching the Python dashboards (theme.py): UI chrome from the IF dashboard stylesheet and a
 *  4-shade palette per segment (dark -> light). Segments are always shown by their agreed names. */
export const DARK_TEXT = "#1F2A24";
export const BRAND = "#0F6B52";
export const REF_GREY = "#4B5563";

export const SEGMENT_IDS = ["1", "2", "3", "4", "5", "6"] as const;

export const SEGMENT_PALETTES: Record<string, string[]> = {
  "1": ["#8E2C5A", "#D3618F", "#EDB2CB", "#F9E4ED"],
  "2": ["#134F5C", "#4EC2BC", "#ACE0DE", "#E6F6F5"],
  "3": ["#B45F06", "#FAA62E", "#FEDCB2", "#FEF2E2"],
  "4": ["#38761D", "#2E9462", "#9DC9B2", "#E1EFE7"],
  "5": ["#351C75", "#665FF7", "#C9C7FD", "#E8E7FE"],
  "6": ["#990000", "#F94B4B", "#FFA8A7", "#FFE5E4"],
};

export const SEGMENT_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SEGMENT_PALETTES).map(([s, p]) => [s, p[1]]),
);
export const SEGMENT_PILL_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(SEGMENT_PALETTES).map(([s, p]) => [s, p[0]]),
);

export const SEGMENT_NAMES: Record<string, string> = {
  "1": "Survival workers",
  "2": "Stability Seekers",
  "3": "Income Pragmatists",
  "4": "Skill Investors",
  "5": "Credentialed Aspirants",
  "6": "Career Pursuers",
};

/** 13-step diverging scheme (green = high/positive ... grey = neutral ... red = low/negative). */
export const DIVERGING = [
  "#00876C", "#42977F", "#66A793", "#87B6A7", "#A6C6BB", "#C6D6D0", "#E5E5E5",
  "#E8CBCB", "#E8B1B1", "#E69798", "#E27B7F", "#DC5F68", "#D43D51",
];

export const segName = (s: string | number): string => SEGMENT_NAMES[String(s)] ?? String(s);
