"use client";

import { useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import CountyMap from "@/components/CountyMap";
import { MIN_COUNTY_N } from "@/lib/data";
import { shareWords } from "@/lib/phrases";
import { countySegmentMix } from "@/lib/plots";
import { BRAND, SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

/** Where the segments are found: a county map (shaded by respondents or by one segment's share), the segment mix
 *  by county and each segment's most common counties. */
export default function CountiesPage() {
  const d = useDashboard();
  const [shade, setShade] = useState<string>("n");
  const counties = [...new Set(d.prevalence.map((r) => r.county))]
    .map((c) => ({ county: c, n: d.prevalence.find((r) => r.county === c)!.n_county }))
    .sort((a, b) => b.n - a.n);

  const mapRows = shade === "n"
    ? d.counties.map((c) => ({ county: c.county, value: c.n,
        hover: `<b>${c.county}</b><br>${c.n} young people surveyed (${c.pct}% of all surveyed)` }))
    : d.prevalence.filter((r) => r.segment === shade).map((r) => ({ county: r.county, value: r.pct_of_county,
        hover: `<b>${r.county}</b><br>${segName(shade)}: ${shareWords(r.pct_of_county)} of the young people surveyed here ` +
          `(${r.pct_of_county.toFixed(0)}%, ${r.n} of ${r.n_county})` }));
  const colors: [string, string] = shade === "n" ? ["#D7ECE3", BRAND] : [SEGMENT_PALETTES[shade][3], SEGMENT_PALETTES[shade][0]];

  return (
    <main className="page">
      <h2>Segments by county</h2>
      <p className="lead-sm">
        Where the young people surveyed live and the mix of segments in each of the nine counties. Counties were sampled, not
        nationally representative, so compare counties with each other rather than reading a figure as the county&apos;s population.
      </p>

      <div className="card chart-card">
        <div className="map-head">
          <h6>Kenya&apos;s counties: {shade === "n" ? "young people surveyed" : `share of respondents who are ${segName(shade)}`}</h6>
          <label className="map-pick">Shade counties by{" "}
            <select value={shade} onChange={(e) => setShade(e.target.value)}>
              <option value="n">Number of young people surveyed</option>
              {SEGMENT_IDS.map((s) => <option key={s} value={s}>{segName(s)} (share)</option>)}
            </select>
          </label>
        </div>
        <p className="card-sub">Grey counties were not surveyed. Hover over a county for its figures.</p>
        <CountyMap rows={mapRows} colors={colors} title={shade === "n" ? "Surveyed" : "% of county"} suffix={shade === "n" ? "" : "%"}
          greyHover={shade === "n" ? "Not surveyed" : `Not surveyed, or fewer than ${MIN_COUNTY_N} ${segName(shade)} respondents`}
          deps={[shade, d]} />
        <p className="footnote">County boundaries: geoBoundaries (RCMRD GeoPortal, 2020), public domain.</p>
      </div>

      <ChartCard title="Segment mix of the young people surveyed, by county" build={() => countySegmentMix(d.prevalence, d.sizes)}
        height={60 + 44 * (counties.length + 1)} deps={[d]} />

      <h5>Share of each county&apos;s respondents in each segment</h5>
      <p className="text-muted">Darker cells are higher within each segment (column). ▲ marks the county where the segment is most common.</p>
      <div className="table-scroll">
        <table className="cmp-table heat">
          <thead>
            <tr>
              <th>County</th>
              <th className="num">n</th>
              {SEGMENT_IDS.map((s) => <th key={s}><span className="dot" style={{ background: SEGMENT_PALETTES[s][1] }} />{segName(s)}</th>)}
            </tr>
          </thead>
          <tbody>
            {counties.map(({ county, n }) => (
              <tr key={county}>
                <th scope="row">{county}</th>
                <td className="num">{n}</td>
                {SEGMENT_IDS.map((s) => {
                  const col = d.prevalence.filter((r) => r.segment === s && r.n_county >= 15).map((r) => r.pct_of_county);
                  const hi = Math.max(...col);
                  const lo = Math.min(...col);
                  const v = d.prevalence.find((r) => r.county === county && r.segment === s)?.pct_of_county;
                  if (v === undefined) return <td key={s} className="text-muted">–</td>;
                  const t = hi > lo ? (v - lo) / (hi - lo) : 0;
                  const alpha = 0.06 + 0.6 * Math.max(0, Math.min(1, t));
                  return (
                    <td key={s} style={{ background: `rgba(15,107,82,${alpha.toFixed(2)})`, color: alpha > 0.5 ? "#fff" : undefined }}>
                      {v.toFixed(0)}%{v === hi && n >= 15 ? <span className="mk"> ▲</span> : null}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="footnote">
        – : fewer than {MIN_COUNTY_N} respondents in that county and segment, not shown. Counties with fewer than 15 respondents are not
        ranked.
      </p>
    </main>
  );
}
