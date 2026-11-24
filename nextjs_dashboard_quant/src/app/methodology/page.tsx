"use client";

import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import CountyMap from "@/components/CountyMap";
import { MIN_COUNTY_N } from "@/lib/data";
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

      <div className="method-section">
        <h4>How “What sets them apart” is chosen</h4>
        <p>
          For each segment, every segmentation driver is scored by how far the segment sits from the other five: the average of its gap
          to the mean of the other five and its gap to the nearest other segment, each divided by the driver&apos;s full scale (100
          percentage points for shares, the scale width for 1-5 and 0-3 scores, 14 years for age, 4 for counts). Using the nearest
          segment stops a value that several segments share from counting as distinctive. Drivers scoring at least 0.12 are shown, up to
          four per segment and never fewer than two. Where two drivers are mirror images (for example finding work only through family
          and friends versus through formal methods), only one is shown. The selection is automatic and reruns if the data change.
        </p>
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
            <p className="footnote">Counties with fewer than {MIN_COUNTY_N} respondents are not shown. County boundaries: geoBoundaries
              (RCMRD GeoPortal, 2020), public domain.</p>
            {missed.length > 0 && <p className="footnote">Not shown on the map (name not recognised): {missed.join(", ")}</p>}
          </div>
        )}
      </div>
    </main>
  );
}
