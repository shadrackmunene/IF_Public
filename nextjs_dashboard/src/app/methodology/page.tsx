"use client";

import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import CountyMap from "@/components/CountyMap";
import { segmentSizeChart, unmatchedCounties } from "@/lib/plots";
import { BRAND } from "@/lib/theme";

/** Technical documentation: study design, sample, segmentation and sizing method, definitions and caveats. */
export default function MethodologyPage() {
  const d = useDashboard();
  const missed = unmatchedCounties(d.counties);
  return (
    <main className="page">
      <h2>Methodology and technical notes</h2>
      <p className="lead-sm">
        How the study was designed, how the segments and size estimates were produced, and how to read the figures on this dashboard.
      </p>

      {d.methodology.sections.map((sec) => (
        <div key={sec.title} className="method-section">
          <h4>{sec.title}</h4>
          {sec.paras?.map((p) => <p key={p.slice(0, 40)}>{p}</p>)}
          {sec.bullets && <ul>{sec.bullets.map((b) => <li key={b.slice(0, 40)}>{b}</li>)}</ul>}
        </div>
      ))}

      <div className="method-section">
        <h4>Driver definitions</h4>
        <div className="table-scroll">
          <table className="cmp-table defs">
            <thead><tr><th>Group</th><th>Driver</th><th>Definition</th><th>Measure</th></tr></thead>
            <tbody>
              {d.methodology.drivers.map(([g, n, def, t]) => (
                <tr key={g + n}><td>{g}</td><th scope="row">{n}</th><td>{def}</td><td>{t}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="footnote">Direct: the survey question matches the HCD definition. Proxy: the closest available question.</p>
      </div>

      <h4>Survey sample</h4>
      <div className="two-col">
        <ChartCard title="Young people surveyed, by segment" build={() => segmentSizeChart(d.sizes)} height={320} deps={[d]} />
        {d.counties.length > 0 && (
          <div className="card chart-card">
            <h6>Where the young people surveyed live</h6>
            <p className="card-sub">Darker counties had more young people surveyed; grey counties were not surveyed.</p>
            <CountyMap rows={d.counties.map((c) => ({ county: c.county, value: c.n,
              hover: `<b>${c.county}</b><br>${c.n} young people surveyed (${c.pct}% of all surveyed)` }))}
              colors={["#D7ECE3", BRAND]} title="Surveyed" deps={[d]} />
            {missed.length > 0 && <p className="footnote">Not shown on the map (name not recognised): {missed.join(", ")}</p>}
          </div>
        )}
      </div>
    </main>
  );
}
