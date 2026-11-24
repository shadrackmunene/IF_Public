/** Kenya county map: all 47 county boundaries (geoBoundaries gbOpen KEN ADM1, public domain), counties not
 *  surveyed in light grey, surveyed counties shaded by a value and labelled. The boundary file is fetched once
 *  from public/geo/ and shared by every map on the site. */
import type { PlotSpec } from "./types";
import { assetUrl } from "./data";
import { DARK_TEXT } from "./theme";

let geoPromise: Promise<any> | null = null;
export const loadCounties = (): Promise<any> =>
  (geoPromise ??= fetch(assetUrl("geo/kenya-counties.geojson")).then((r) => {
    if (!r.ok) throw new Error(`county boundaries: HTTP ${r.status}`);
    return r.json();
  }));

/** Match survey county names to boundary names ("Nairobi County", "Murang'a" -> "nairobi", "muranga"). */
export const countyKey = (name: string) => String(name).toLowerCase().replace("county", "").replace(/[^a-z]/g, "");

/** Nairobi is small and sits next to Machakos: push the two labels apart. */
const LABEL_POSITION: Record<string, string> = { Nairobi: "middle left", Machakos: "middle right" };

export interface CountyValue { county: string; value: number; hover: string }

/** Rough label position: the middle of the county's bounding box (largest polygon). */
function labelPoint(geom: any): [number, number] {
  const polys: number[][][][] = geom.type === "Polygon" ? [geom.coordinates] : geom.coordinates;
  const biggest = polys.reduce((a, b) => (b[0].length > a[0].length ? b : a));
  const xs = biggest[0].map((p) => p[0]);
  const ys = biggest[0].map((p) => p[1]);
  return [(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2];
}

export function countyChoropleth(
  geo: any, rows: CountyValue[], opts: { colors: [string, string]; title: string; suffix?: string; height?: number; greyHover?: string },
): PlotSpec {
  const feats: any[] = geo.features;
  const byKey = new Map(feats.map((f) => [countyKey(f.id), f]));
  const matched = rows.filter((r) => byKey.has(countyKey(r.county)));
  const ids = matched.map((r) => byKey.get(countyKey(r.county)).id);
  const vals = matched.map((r) => r.value);
  const lo = Math.min(...vals);
  const hi = Math.max(...vals);
  const labels = matched.map((r) => labelPoint(byKey.get(countyKey(r.county)).geometry));
  const font = { family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color: DARK_TEXT, size: 12 };
  return {
    data: [
      { // every county, so the whole country and its boundaries show
        type: "choropleth", geojson: geo, featureidkey: "id", locations: feats.map((f) => f.id), z: feats.map(() => 0),
        colorscale: [[0, "#EEF0EC"], [1, "#EEF0EC"]], showscale: false, marker: { line: { color: "#A7AFAB", width: 0.6 } },
        text: feats.map((f) => f.id), hovertemplate: `<b>%{text}</b><br>${opts.greyHover ?? "Not surveyed"}<extra></extra>`,
      },
      {
        type: "choropleth", geojson: geo, featureidkey: "id", locations: ids, z: vals,
        zmin: lo === hi ? 0 : lo, zmax: hi, colorscale: [[0, opts.colors[0]], [1, opts.colors[1]]],
        marker: { line: { color: "#FFFFFF", width: 1.2 } },
        colorbar: { title: { text: opts.title, side: "right" }, thickness: 12, len: 0.6, ticksuffix: opts.suffix ?? "", outlinewidth: 0 },
        text: matched.map((r) => r.hover), hovertemplate: "%{text}<extra></extra>",
      },
      { // county names on the surveyed counties
        type: "scattergeo", mode: "text", lon: labels.map((p) => p[0]), lat: labels.map((p) => p[1]),
        text: ids, textposition: ids.map((id) => LABEL_POSITION[id] ?? "middle center"),
        textfont: { size: 11, color: DARK_TEXT }, hoverinfo: "skip", showlegend: false,
      },
    ],
    layout: {
      height: opts.height ?? 560, margin: { l: 0, r: 0, t: 0, b: 0 }, paper_bgcolor: "white", dragmode: false, autosize: true, font,
      geo: { visible: false, fitbounds: "locations", projection: { type: "mercator" }, bgcolor: "white" },
    },
  };
}
