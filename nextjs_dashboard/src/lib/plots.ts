/** Plotly chart builders: a one-for-one port of plots.py. Each function returns {data, layout} for Plotly.js.
 *  Segments are always shown by their agreed names; every tooltip carries both the percentage and its
 *  sample size, e.g. "59% (n=124)". */
import type { DriverRow, NumSummary, PlotSpec, Question, SegmentDist } from "./types";
import { BRAND, DARK_TEXT, DIVERGING, REF_GREY, SEGMENT_COLORS, SEGMENT_IDS, segName } from "./theme";

export const PLOTLY_CONFIG = {
  displaylogo: false,
  scrollZoom: false,
  responsive: true,
  modeBarButtonsToRemove: ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
};

type Names = Record<string, string>;

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
// automargin: plotly.py's default template grows the margins to fit tick labels; plotly.js needs it switched on.
const axis = (extra: object = {}) => ({ showline: true, linecolor: "#CCCCCC", gridcolor: "#EEF0F4", automargin: true, ...extra });

function baseLayout(height: number, extra: Record<string, any> = {}): any {
  return {
    height,
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    font: { family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color: DARK_TEXT, size: 12 },
    hoverlabel: { font: { size: 13 } },
    dragmode: false,
    margin: { l: 10, r: 10, t: 10, b: 10 },
    autosize: true,
    ...extra,
  };
}

function wrap(label: string, width = 16): string {
  const words = String(label).split(/\s+/);
  const lines: string[] = [];
  let cur = "";
  for (const w of words) {
    if (cur && (cur + " " + w).length > width) {
      lines.push(cur);
      cur = w;
    } else cur = cur ? cur + " " + w : w;
  }
  if (cur) lines.push(cur);
  return lines.join("<br>") || String(label);
}

const key = (v: number): string => (Number.isInteger(v) ? String(v) : String(v));
const rgba = (hex: string, a: number): string => {
  const h = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return `rgba(${r},${g},${b},${a})`;
};

function textColor(hex: string): string {
  const h = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return 0.299 * r + 0.587 * g + 0.114 * b < 140 ? "#FFFFFF" : DARK_TEXT;
}

const sortedSegs = (names: Names) => Object.keys(names).sort((a, b) => Number(a) - Number(b));

const pctOf = (d: SegmentDist | undefined, seg: string, value: number): number => d?.[seg]?.p[key(value)] ?? 0;
const nOf = (d: SegmentDist | undefined, seg: string): number => d?.[seg]?.n ?? 0;

const hoverHead = (q: Question) => `<span style='color:#777'>${q.dimension}: ${q.section}</span><br>`;

// ---------------------------------------------------------------------------
// Overview / Segment Profiles
// ---------------------------------------------------------------------------
export function segmentSizeChart(sizes: { segment: string; n: number; pct: number }[]): PlotSpec {
  const top = Math.max(...sizes.map((s) => s.pct));
  return {
    data: [{
      type: "bar",
      x: sizes.map((s) => segName(s.segment)),
      y: sizes.map((s) => s.pct),
      marker: { color: sizes.map((s) => SEGMENT_COLORS[s.segment]) },
      customdata: sizes.map((s) => s.n),
      text: sizes.map((s) => `${s.pct}%`),
      textposition: "outside",
      cliponaxis: false,
      hovertemplate: "<b>%{x}</b><br>%{y}% of respondents (n=%{customdata})<extra></extra>",
    }],
    layout: baseLayout(340, {
      xaxis: axis({ showgrid: false }),
      yaxis: axis({ title: { text: "% of respondents" }, range: [0, top * 1.25] }),
    }),
  };
}

export function driverBarChart(
  drivers: DriverRow[], category: string, highlight: string | null, kind: "pct" | "score",
  nBySegment: Record<string, number>,
): PlotSpec | null {
  const wantPct = kind === "pct";
  const sub = drivers.filter((r) => r.category === category && r.is_pct === wantPct);
  const labels = [...new Set(sub.map((r) => r.label))];
  if (!labels.length) return null;
  const val = (lbl: string, seg: string): number | null => {
    const r = sub.find((x) => x.label === lbl && x.segment === seg);
    return r ? r.value : null;
  };
  const fmt = (v: number | null) => (v === null ? "" : wantPct ? `${v.toFixed(0)}%` : v.toFixed(2));
  const wrapped = labels.map((l) => wrap(l, 15));
  const allVals = labels.map((l) => val(l, "All"));
  const traces: any[] = [{
    type: "bar", x: wrapped, y: allVals, name: "All respondents", marker: { color: "#C9CDD6" },
    text: allVals.map(fmt), textposition: "outside", textfont: { size: 10 }, cliponaxis: false,
    customdata: labels.map((l, i) => [l, fmt(allVals[i]), nBySegment["All"] ?? ""]),
    hovertemplate: "<b>%{customdata[0]}</b><br>All respondents: %{customdata[1]} (n=%{customdata[2]})<extra></extra>",
  }];
  const cands = allVals.filter((v): v is number => v !== null);
  if (highlight) {
    const segVals = labels.map((l) => val(l, highlight));
    traces.push({
      type: "bar", x: wrapped, y: segVals, name: segName(highlight), marker: { color: SEGMENT_COLORS[highlight] ?? BRAND },
      text: segVals.map(fmt), textposition: "outside", textfont: { size: 10 }, cliponaxis: false,
      customdata: labels.map((l, i) => [l, fmt(segVals[i]), nBySegment[highlight] ?? ""]),
      hovertemplate: `<b>%{customdata[0]}</b><br>${segName(highlight)}: %{customdata[1]} (n=%{customdata[2]})<extra></extra>`,
    });
    cands.push(...segVals.filter((v): v is number => v !== null));
  }
  const top = Math.max(1, ...cands);
  return {
    data: traces,
    layout: baseLayout(380, {
      barmode: "group", legend: { orientation: "h", y: 1.12, x: 0 }, margin: { l: 10, r: 10, t: 40, b: 10 },
      yaxis: axis({ range: [0, top * 1.25], ticksuffix: wantPct ? "%" : "", title: { text: wantPct ? "% of segment" : "Average" } }),
      xaxis: axis({ showgrid: false, tickfont: { size: 10 } }),
    }),
  };
}

export function pathwayStageChart(
  stages: { segment: string; stage: string; pct: number }[], order: string[], segment: string, n?: number,
): PlotSpec {
  const vals = order.map((s) => stages.find((r) => r.segment === segment && r.stage === s)?.pct ?? 0);
  return {
    data: [{
      type: "bar", x: order.map((s) => s.replace(" ", "<br>")), y: vals,
      marker: { color: SEGMENT_COLORS[segment] ?? BRAND }, text: vals.map((p) => `${p}%`), textposition: "outside",
      cliponaxis: false, customdata: order.map((s) => [s, n ?? ""]),
      hovertemplate: `<b>%{customdata[0]}</b><br>%{y}% of ${segName(segment)} meet this stage proxy (n=%{customdata[1]})<extra></extra>`,
    }],
    layout: baseLayout(320, {
      yaxis: axis({ title: { text: "% of segment meeting stage proxy" }, range: [0, 110] }),
      xaxis: axis(),
    }),
  };
}

export function probabilityChart(prob: Record<string, number>): PlotSpec {
  const segs = Object.keys(prob).sort((a, b) => Number(a) - Number(b));
  const vals = segs.map((s) => 100 * prob[s]);
  return {
    data: [{
      type: "bar", x: segs.map(segName), y: vals, marker: { color: segs.map((s) => SEGMENT_COLORS[s]) },
      text: vals.map((v) => `${v.toFixed(0)}%`), textposition: "outside", cliponaxis: false,
      hovertemplate: "<b>%{x}</b><br>Match probability: %{y:.1f}%<extra></extra>",
    }],
    layout: baseLayout(280, {
      yaxis: axis({ title: { text: "Match probability (%)" }, range: [0, 112] }),
      xaxis: axis({ showgrid: false }),
    }),
  };
}

// ---------------------------------------------------------------------------
// Deep-dive question charts
// ---------------------------------------------------------------------------
export const cleanQuestionLabel = (label: string): string =>
  label.replace(/^[A-Z]\d{3,4}(_\d+)*[.:]?\s*/, "").trim();

export const questionTitle = (q: Question): string => q.short || cleanQuestionLabel(q.label);

const SCALE_ENDS: [string, string][] = [
  ["strongly disagree", "strongly agree"], ["very low respect", "very high respect"],
  ["very poorly paid", "very well paid"], ["not at all", "extremely"],
  ["clearly a worthwhile", "clearly a missed"], ["not knowledgeable at all", "very knowledgeable"],
  ["never", "very frequently"], ["no freedom at all", "a lot of freedom"],
  ["very unlikely", "very likely"], ["very good", "very bad"], ["improve a lot", "get much worse"],
  ["very easy", "very difficult"],
];

const validOptions = (q: Question) => (q.options ?? []).filter((o) => !o.non_answer);

export function isLikert(q: Question): boolean {
  if (q.type !== "categorical") return false;
  const valid = validOptions(q).map((o) => o.label.toLowerCase());
  if (valid.length !== 4 && valid.length !== 5) return false;
  return SCALE_ENDS.some(([a, b]) => valid[0].startsWith(a) && valid[valid.length - 1].startsWith(b));
}

const POSITIVE_FIRST = ["very good", "improve a lot", "very easy", "clearly a worthwhile"];
const DIV_PICK: Record<number, number[]> = { 5: [12, 9, 6, 3, 0], 4: [12, 9, 3, 0] };

function likertValid(q: Question) {
  const valid = validOptions(q);
  return valid.length && POSITIVE_FIRST.some((p) => valid[0].label.toLowerCase().startsWith(p))
    ? [...valid].reverse() : valid;
}

const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0);

/** Diverging bars for a rating scale, centred on the midpoint. Colour encodes the ANSWER; segments are the rows.
 *  Dashed lines mark the all-respondent share on each side. */
export function likertQuestionChart(q: Question, dist: SegmentDist | undefined, names: Names): PlotSpec {
  const segs = sortedSegs(names);
  const valid = likertValid(q);
  const n = valid.length;
  const half = Math.floor(n / 2);
  const odd = n % 2 === 1;
  const rstart = odd ? half + 1 : half;
  const colors = DIV_PICK[n].map((i) => DIVERGING[i]);
  const vals: Record<string, number[]> = {};
  for (const s of [...segs, "All"]) vals[s] = valid.map((o) => pctOf(dist, s, o.value));
  const midHalf = (s: string) => (odd ? vals[s][half] / 2 : 0);
  const labels = segs.map(segName);

  const data = valid.map((o, p) => {
    const base = segs.map((s) => {
      const v = vals[s];
      if (p < half) return -(sum(v.slice(p + 1, half)) + midHalf(s) + v[p]);
      if (odd && p === half) return -v[p] / 2;
      return sum(v.slice(rstart, p)) + midHalf(s);
    });
    const xs = segs.map((s) => vals[s][p]);
    return {
      type: "bar", orientation: "h", y: labels, x: xs, base, name: o.label, showlegend: false,
      marker: { color: colors[p], line: { color: "white", width: 0.8 } },
      customdata: segs.map((s) => [o.label, vals["All"][p].toFixed(1), nOf(dist, s), nOf(dist, "All")]),
      text: xs.map((x) => (x >= 16 ? o.label : "")), textposition: "inside", insidetextanchor: "middle",
      textfont: { size: 10, color: textColor(colors[p]) },
      hovertemplate: hoverHead(q) + "<b>%{y}</b><br>%{customdata[0]}: <b>%{x:.0f}% (n=%{customdata[2]})</b><br>" +
        "All respondents: %{customdata[1]}% (n=%{customdata[3]})<extra></extra>",
    };
  });

  const a = vals["All"];
  const allHigh = sum(a.slice(rstart)) + (odd ? a[half] / 2 : 0);
  const allLow = sum(a.slice(0, half)) + (odd ? a[half] / 2 : 0);
  const shapes: any[] = [];
  const annotations: any[] = [];
  for (const [x, txt] of [[allHigh, `All: ${allHigh.toFixed(0)}%`], [-allLow, `All: ${allLow.toFixed(0)}%`]] as [number, string][]) {
    shapes.push({ type: "line", xref: "x", yref: "paper", x0: x, x1: x, y0: 0, y1: 1,
      line: { color: REF_GREY, width: 1.2, dash: "dash" } });
    annotations.push({ xref: "x", yref: "paper", x, y: 1, yanchor: "bottom", xanchor: "center", text: txt,
      showarrow: false, font: { size: 10, color: REF_GREY } });
  }
  shapes.push({ type: "line", xref: "x", yref: "paper", x0: 0, x1: 0, y0: 0, y1: 1, line: { color: "#9AA0A6", width: 1 } });
  const rightMax = Math.max(allHigh, ...segs.map((s) => sum(vals[s].slice(rstart)) + midHalf(s)));
  const leftMax = Math.max(allLow, ...segs.map((s) => sum(vals[s].slice(0, half)) + midHalf(s)));
  const hiLim = Math.min(100, rightMax + 12);
  const loLim = Math.min(100, Math.max(leftMax + 12, 22));
  const ticks: number[] = [];
  for (let t = -100; t <= 100; t += 25) if (t >= -loLim && t <= hiLim) ticks.push(t);
  const cap = { xref: "paper", yref: "paper", y: 0, yshift: -36, showarrow: false, font: { size: 11, color: "#5C6B62" } };
  annotations.push({ ...cap, x: 0, xanchor: "left", text: `◀ ${valid[0].label}` });
  annotations.push({ ...cap, x: 1, xanchor: "right", text: `${valid[n - 1].label} ▶` });
  return {
    data,
    layout: baseLayout(110 + 34 * segs.length, {
      barmode: "overlay", margin: { l: 10, r: 10, t: 26, b: 58 }, shapes, annotations,
      xaxis: axis({ range: [-loLim, hiLim], tickvals: ticks, ticktext: ticks.map((t) => `${Math.abs(t)}%`), zeroline: false }),
      yaxis: axis({ autorange: "reversed", showgrid: false }),
    }),
  };
}

function verticalSegmentBars(
  segs: string[], values: number[], texts: string[], hoverLabel: string, allValue: number | null, allText: string,
  yTitle: string, q: Question, nn: Record<string, number>, ymax?: number, pct = false,
): PlotSpec {
  const shapes: any[] = [];
  const annotations: any[] = [];
  if (allValue !== null) {
    shapes.push({ type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: allValue, y1: allValue,
      line: { color: REF_GREY, width: 1.2, dash: "dash" } });
    annotations.push({ xref: "paper", yref: "y", x: 0, y: allValue, xanchor: "left", yanchor: "bottom",
      text: `${allText} (n=${nn["All"] ?? ""})`, showarrow: false, font: { size: 11, color: REF_GREY } });
  }
  const top = values.length ? Math.max(...values, allValue ?? 0) : 1;
  return {
    data: [{
      type: "bar", x: segs.map(segName), y: values, marker: { color: segs.map((s) => SEGMENT_COLORS[s]) },
      text: texts, textposition: "outside", cliponaxis: false,
      customdata: segs.map((s) => [hoverLabel, nn[s] ?? "", nn["All"] ?? ""]),
      hovertemplate: hoverHead(q) + "<b>%{x}</b><br>%{customdata[0]}: <b>%{text} (n=%{customdata[1]})</b><extra></extra>",
    }],
    layout: baseLayout(340, {
      margin: { l: 10, r: 10, t: 24, b: 10 }, shapes, annotations,
      yaxis: axis({ title: { text: yTitle }, range: [0, pct ? Math.min((ymax ?? top) * 1.22, 112) : (ymax ?? top) * 1.22], ticksuffix: pct ? "%" : "" }),
      xaxis: axis({ showgrid: false }),
    }),
  };
}

/** Yes/No style question: vertical bar per segment = % choosing the 'yes' option, dashed line = all. */
export function binaryQuestionChart(q: Question, dist: SegmentDist | undefined, names: Names): PlotSpec {
  const segs = sortedSegs(names);
  const valid = validOptions(q);
  const pos = valid.find((o) => /^(yes|selected|checked|mentioned)/i.test(o.label)) ?? valid[valid.length - 1];
  const vals = segs.map((s) => pctOf(dist, s, pos.value));
  const overall = dist?.["All"]?.p[key(pos.value)];
  const nn: Record<string, number> = {};
  for (const s of [...segs, "All"]) nn[s] = nOf(dist, s);
  return verticalSegmentBars(segs, vals, vals.map((v) => `${v.toFixed(0)}%`), pos.label, overall ?? null,
    overall !== undefined ? `All: ${overall.toFixed(0)}%` : "", `% ${pos.label}`, q, nn,
    Math.max(0, ...vals) > 60 ? 100 : undefined, true);
}

/** Faceted small multiples: one panel per segment, answer options inside each panel, and a short grey marker
 *  on every option showing the all-respondent share. Long option lists switch to horizontal bars. */
export function columnsQuestionChart(q: Question, dist: SegmentDist | undefined, names: Names): PlotSpec {
  const segs = sortedSegs(names);
  const valid = validOptions(q);
  const horizontal = valid.length > 6;
  const lim = horizontal ? 34 : 16;
  const short = valid.map((o) => (o.label.length <= lim ? o.label : o.label.slice(0, lim - 1).trimEnd() + "…"));
  const ncols = Math.max(1, Math.min(3, segs.length));
  const nrows = Math.ceil(segs.length / ncols);
  const vs = nrows > 1 ? 0.18 : 0.1;
  const hs = 0.04;
  const w = (1 - (ncols - 1) * hs) / ncols;
  const h = (1 - (nrows - 1) * vs) / nrows;
  const pos = valid.map((_, i) => i);
  let ymax = 1;
  for (const s of [...segs, "All"]) for (const o of valid) ymax = Math.max(ymax, pctOf(dist, s, o.value));

  const data: any[] = [];
  const layout: Record<string, any> = {};
  const annotations: any[] = [];
  segs.forEach((s, i) => {
    const r = Math.floor(i / ncols);
    const c = i % ncols;
    const n = i + 1;
    const x0 = c * (w + hs);
    const y1 = 1 - r * (h + vs);
    const y0 = y1 - h;
    const xa = n === 1 ? "x" : `x${n}`;
    const ya = n === 1 ? "y" : `y${n}`;
    const vals = valid.map((o) => pctOf(dist, s, o.value));
    const allv = valid.map((o) => pctOf(dist, "All", o.value));
    const cd = valid.map((o, k) => [o.label, allv[k].toFixed(1), nOf(dist, s), nOf(dist, "All")]);
    const hov = hoverHead(q) + `<b>${segName(s)}</b><br>%{customdata[0]}: <b>%{${horizontal ? "x" : "y"}:.0f}% (n=%{customdata[2]})</b><br>` +
      "All respondents: %{customdata[1]}% (n=%{customdata[3]})<extra></extra>";
    const txt = vals.map((v) => (v >= 3 ? `${v.toFixed(0)}%` : ""));
    if (horizontal) {
      data.push({ type: "bar", orientation: "h", y: pos, x: vals, xaxis: xa, yaxis: ya, marker: { color: SEGMENT_COLORS[s] },
        showlegend: false, text: txt, textposition: "outside", textfont: { size: 9 }, cliponaxis: false, customdata: cd, hovertemplate: hov });
      data.push({ type: "scatter", mode: "markers", y: pos, x: allv, xaxis: xa, yaxis: ya, showlegend: false, hoverinfo: "skip",
        marker: { symbol: "line-ns", size: 14, color: REF_GREY, line: { color: REF_GREY, width: 2 } } });
      layout[`xaxis${n === 1 ? "" : n}`] = axis({ domain: [x0, x0 + w], anchor: ya, range: [0, ymax * 1.3], ticksuffix: "%", showgrid: true });
      layout[`yaxis${n === 1 ? "" : n}`] = axis({ domain: [y0, y1], anchor: xa, tickvals: pos, ticktext: short, tickfont: { size: 9 },
        autorange: "reversed", showticklabels: c === 0 });
    } else {
      data.push({ type: "bar", x: pos, y: vals, xaxis: xa, yaxis: ya, marker: { color: SEGMENT_COLORS[s] }, showlegend: false,
        text: txt, textposition: "outside", textfont: { size: 9 }, cliponaxis: false, customdata: cd, hovertemplate: hov });
      data.push({ type: "scatter", mode: "markers", x: pos, y: allv, xaxis: xa, yaxis: ya, showlegend: false, hoverinfo: "skip",
        marker: { symbol: "line-ew", size: 22, color: REF_GREY, line: { color: REF_GREY, width: 2.2 } } });
      layout[`xaxis${n === 1 ? "" : n}`] = axis({ domain: [x0, x0 + w], anchor: ya, tickvals: pos, ticktext: short, tickangle: -40,
        tickfont: { size: 9 }, showgrid: false });
      layout[`yaxis${n === 1 ? "" : n}`] = axis({ domain: [y0, y1], anchor: xa, range: [0, ymax * 1.28], ticksuffix: "%", showgrid: true,
        showticklabels: c === 0 });
    }
    annotations.push({ text: segName(s), x: x0 + w / 2, y: y1, xref: "paper", yref: "paper", xanchor: "center", yanchor: "bottom",
      showarrow: false, font: { size: 12, color: DARK_TEXT } });
  });
  annotations.push({ xref: "paper", yref: "paper", x: 1, y: 1, yshift: 30, xanchor: "right", yanchor: "bottom", showarrow: false,
    font: { size: 11, color: REF_GREY }, text: "▬ all respondents" });
  return {
    data,
    layout: baseLayout(horizontal ? 150 + (19 * valid.length + 60) * nrows : 170 + 210 * nrows, {
      margin: horizontal ? { l: 200, r: 10, t: 64, b: 10 } : { l: 40, r: 10, t: 64, b: 10 }, annotations, ...layout,
    }),
  };
}

export function numericQuestionChart(q: Question, nums: NumSummary | undefined, names: Names): PlotSpec {
  const segs = sortedSegs(names).filter((s) => nums?.[s]);
  const vals = segs.map((s) => nums![s].mean);
  const nn: Record<string, number> = {};
  for (const s of segs) nn[s] = nums![s].n;
  const all = nums?.["All"];
  nn["All"] = all?.n ?? 0;
  return verticalSegmentBars(segs, vals, vals.map((v) => v.toFixed(1)), "Average", all ? all.mean : null,
    all ? `All: ${all.mean.toFixed(1)}` : "", "Average", q, nn);
}

export const RADAR_AXES: [string, string][] = [
  ["A101", "Age"], ["F606", "Personal income"], ["E506", "Weekly work hours"],
  ["B207", "Household size"], ["L1203", "Income sent to family"],
];

/** Spider web comparing segments on age, income and other numeric profile measures. Each axis is scaled so the
 *  highest-scoring segment is 100; hover shows the real average and sample size. */
export function radarChart(nums: Record<string, NumSummary>, names: Names): PlotSpec | null {
  const axes = RADAR_AXES.filter(([c]) => nums[c]);
  if (axes.length < 3) return null;
  const segs = sortedSegs(names);
  const get = (code: string, seg: string): [number | null, number] => {
    const r = nums[code]?.[seg];
    return r ? [r.mean, r.n] : [null, 0];
  };
  const top: Record<string, number> = {};
  for (const [c] of axes) top[c] = Math.max(...segs.map((s) => get(c, s)[0] ?? 0)) || 1;
  const labels = axes.map(([, l]) => l);
  const data = [...segs, "All"].map((s) => {
    const vals = axes.map(([c]) => get(c, s));
    const r = vals.map((v, i) => ((v[0] ?? 0) / top[axes[i][0]]) * 100);
    const hover = vals.map((v, i) => (v[0] !== null ? `${labels[i]}: ${v[0].toLocaleString(undefined, { maximumFractionDigits: 1 })} (n=${v[1]})` : labels[i]));
    const isAll = s === "All";
    const color = isAll ? REF_GREY : SEGMENT_COLORS[s];
    const nm = isAll ? "All respondents" : segName(s);
    return {
      type: "scatterpolar", r: [...r, r[0]], theta: [...labels, labels[0]], name: nm, mode: "lines+markers",
      fill: isAll ? "none" : "toself", fillcolor: isAll ? undefined : rgba(color, 0.16),
      line: { color, width: isAll ? 2.4 : 2, dash: isAll ? "dash" : "solid" }, marker: { size: 5 },
      text: [...hover, hover[0]], hovertemplate: `<b>${nm}</b><br>%{text}<extra></extra>`,
    };
  });
  return {
    data,
    layout: {
      height: 520, margin: { l: 60, r: 60, t: 30, b: 30 }, paper_bgcolor: "white", dragmode: false, autosize: true,
      font: { family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color: DARK_TEXT, size: 12 },
      polar: { bgcolor: "white", radialaxis: { range: [0, 110], showticklabels: false, gridcolor: "#E2E5E0" },
        angularaxis: { gridcolor: "#E2E5E0" } },
      legend: { orientation: "h", y: -0.08, x: 0.5, xanchor: "center" },
    },
  };
}

export type ChartKind = "numeric" | "likert" | "binary" | "columns";

export function chartKind(q: Question): ChartKind {
  if (q.type === "numeric") return "numeric";
  if (isLikert(q)) return "likert";
  return validOptions(q).length === 2 ? "binary" : "columns";
}

export function questionChart(
  q: Question, dists: Record<string, SegmentDist>, nums: Record<string, NumSummary>, names: Names,
): PlotSpec {
  const kind = chartKind(q);
  if (kind === "numeric") return numericQuestionChart(q, nums[q.code], names);
  const d = dists[q.code];
  return { likert: likertQuestionChart, binary: binaryQuestionChart, columns: columnsQuestionChart }[kind](q, d, names);
}

// ---------------------------------------------------------------------------
// Respondents by county: bubble map (concentrations only, no drill-down)
// ---------------------------------------------------------------------------
const COUNTY_CENTROIDS: Record<string, [number, number]> = {
  mombasa: [-4.04, 39.67], kwale: [-4.17, 39.45], kilifi: [-3.51, 39.91], tanariver: [-1.65, 39.65],
  lamu: [-2.27, 40.9], taitataveta: [-3.4, 38.36], garissa: [-0.45, 39.65], wajir: [1.75, 40.06],
  mandera: [3.94, 41.86], marsabit: [2.33, 37.99], isiolo: [0.35, 37.58], meru: [0.05, 37.65],
  tharakanithi: [-0.3, 37.97], embu: [-0.53, 37.46], kitui: [-1.37, 38.01], machakos: [-1.52, 37.26],
  makueni: [-2.25, 37.62], nyandarua: [-0.18, 36.52], nyeri: [-0.42, 36.95], kirinyaga: [-0.5, 37.28],
  muranga: [-0.72, 37.15], kiambu: [-1.03, 36.83], turkana: [3.12, 35.6], westpokot: [1.62, 35.12],
  samburu: [1.17, 36.95], transnzoia: [1.02, 34.95], uasingishu: [0.55, 35.3],
  elgeyomarakwet: [0.78, 35.51], nandi: [0.18, 35.13], baringo: [0.65, 35.97], laikipia: [0.4, 36.78],
  nakuru: [-0.3, 36.07], narok: [-1.08, 35.87], kajiado: [-2.1, 36.78], kericho: [-0.37, 35.28],
  bomet: [-0.78, 35.34], kakamega: [0.28, 34.75], vihiga: [0.07, 34.72], bungoma: [0.57, 34.56],
  busia: [0.43, 34.11], siaya: [0.06, 34.29], kisumu: [-0.09, 34.77], homabay: [-0.53, 34.45],
  migori: [-1.06, 34.47], kisii: [-0.68, 34.77], nyamira: [-0.57, 34.95], nairobi: [-1.29, 36.82],
};

const countyKey = (name: string) => String(name).toLowerCase().replace("county", "").replace(/[^a-z]/g, "");

export const unmatchedCounties = (counts: { county: string }[]) =>
  counts.filter((c) => !COUNTY_CENTROIDS[countyKey(c.county)]).map((c) => c.county);

/** Bubble map of respondents per county: bubble area = number of respondents. */
export function countyMap(counts: { county: string; n: number; pct: number }[]): PlotSpec {
  const df = counts.filter((c) => COUNTY_CENTROIDS[countyKey(c.county)]);
  const top = Math.max(1, ...df.map((d) => d.n));
  return {
    data: [{
      type: "scattergeo", mode: "markers+text",
      lat: df.map((d) => COUNTY_CENTROIDS[countyKey(d.county)][0]),
      lon: df.map((d) => COUNTY_CENTROIDS[countyKey(d.county)][1]),
      text: df.map((d) => d.county.replace(" County", "")), textposition: "top center", textfont: { size: 11, color: DARK_TEXT },
      marker: { size: df.map((d) => 14 + 46 * Math.sqrt(d.n / top)), color: BRAND, opacity: 0.62, line: { color: "white", width: 1.5 } },
      customdata: df.map((d) => [d.n, d.pct]),
      hovertemplate: "<b>%{text}</b><br>%{customdata[0]} respondents (%{customdata[1]}%)<extra></extra>",
    }],
    layout: {
      height: 520, margin: { l: 0, r: 0, t: 0, b: 0 }, paper_bgcolor: "white", dragmode: false, autosize: true,
      font: { family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color: DARK_TEXT },
      geo: { scope: "africa", resolution: 50, showcountries: true, countrycolor: "#C9CDD6", showland: true, landcolor: "#F6F7F5",
        showocean: true, oceancolor: "#E6F2EE", showlakes: true, lakecolor: "#E6F2EE", projection: { type: "mercator" },
        lataxis: { range: [-5.2, 5.6] }, lonaxis: { range: [33.4, 42.4] } },
    },
  };
}

export { SEGMENT_IDS };
