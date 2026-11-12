export type SegId = "1" | "2" | "3" | "4" | "5" | "6";

export interface Option {
  value: number;
  label: string;
  non_answer: boolean;
}

export interface Question {
  code: string;
  label: string;
  short?: string | null;
  section: string;
  dimension: string;
  type: "numeric" | "categorical" | string;
  options?: Option[];
}

/** {segment or "All": {n valid answers, p: {option value -> % of valid answers}}} */
export type SegmentDist = Record<string, { n: number; p: Record<string, number> }>;
export type NumSummary = Record<string, { mean: number; median: number; n: number }>;

export interface DriverRow {
  driver: string;
  label: string;
  category: string;
  segment: string;
  value: number;
  is_pct: boolean;
}

export interface SegmentContent {
  headline: string;
  where_they_sit: string[];
  what_would_help: string[];
  hcd_link: string;
}

export interface AssessmentQuestion {
  id: string;
  text: string;
  widget: "numeric" | "radio";
  min?: number;
  max?: number;
  value?: number;
  options?: { label: string; value: string | number }[];
}

export interface Dashboard {
  content: Record<string, SegmentContent>;
  stage_order: string[];
  questionnaire: AssessmentQuestion[];
  overview: Record<string, number>;
  sizes: { segment: string; n: number; pct: number }[];
  drivers: DriverRow[];
  stages: { segment: string; stage: string; pct: number }[];
  names: Record<string, string>;
  catalog: Question[];
  dists: Record<string, SegmentDist>;
  nums: Record<string, NumSummary>;
  counties: { county: string; n: number; pct: number }[];
  prevalence: { segment: string; county: string; n: number; n_county: number; pct_of_county: number }[];
  population: {
    note?: string;
    total_youth: number;
    national: { segment: string; count: number; pct: number }[];
  } | null;
}

export interface Model {
  classes: string[];
  features: string[];
  coef: number[][];
  intercept: number[];
}

export interface PlotSpec {
  data: any[];
  layout: any;
}
