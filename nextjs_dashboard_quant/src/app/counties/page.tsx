"use client";

import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { MIN_COUNTY_N } from "@/lib/data";
import { countyMap, countySegmentMix } from "@/lib/plots";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

/** Where the segments are found: segment mix by county and each segment's most common counties. */
export default function CountiesPage() {
  const d = useDashboard();
  const counties = [...new Set(d.prevalence.map((r) => r.county))]
    .map((c) => ({ county: c, n: d.prevalence.find((r) => r.county === c)!.n_county }))
    .sort((a, b) => b.n - a.n);
  return (
    <main className="page">
      <h2>Segments by county</h2>
      <p className="lead-sm">
        The mix of segments among the young people surveyed in each of the nine counties. Counties were sampled, not
        nationally representative, so compare the mix between counties rather than reading each bar as the county&apos;s population.
      </p>

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

      <div className="card chart-card" style={{ marginTop: 18 }}>
        <h6>Where the young people surveyed live</h6>
        <p className="card-sub">Bubble size shows the number of young people surveyed in each county.</p>
        <ChartCard build={() => countyMap(d.counties)} height={520} deps={[d]} bare />
      </div>
    </main>
  );
}
