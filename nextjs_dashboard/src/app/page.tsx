"use client";

import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { cardGroups } from "@/lib/overviewCards";
import { countyMap, segmentSizeChart, unmatchedCounties } from "@/lib/plots";
import { MIN_COUNTY_N } from "@/lib/data";

export default function OverviewPage() {
  const d = useDashboard();
  const o = d.overview;
  const missed = unmatchedCounties(d.counties);
  return (
    <main className="page">
      <h2>Real Livelihoods Youth Segmentation Study</h2>
      <p>
        Descriptive findings across all {o.n_respondents.toLocaleString("en-US")} respondents (Kenyan youth, 9 counties).
        Six youth segments were identified from their demographics, behaviours and mindsets - see the Segment Profiles tab.
      </p>

      {cardGroups(o).map((g) => {
        const [dark, mid, , light] = g.palette;
        return (
          <section key={g.title}>
            <h4>{g.title}</h4>
            <div className="stat-grid">
              {g.cards.map((c) => (
                <div key={c.title} className="stat-card" style={{ background: light, borderColor: `${mid}55` }}>
                  <div className="stat-icon" style={{ background: `${mid}33`, color: dark }}>{c.icon}</div>
                  <div>
                    <div className="stat-label">{c.title}</div>
                    <div className="stat-value" style={{ color: dark }}>{c.value}</div>
                    <div className="stat-sub">{c.sub}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}

      <h4>Six segments at a glance</h4>
      <ChartCard build={() => segmentSizeChart(d.sizes)} height={340} deps={[d]} />

      {d.counties.length > 0 && (
        <>
          <h4>Where respondents are</h4>
          <p className="text-muted">Bubble size shows the number of respondents in each county.</p>
          <ChartCard build={() => countyMap(d.counties)} height={520} deps={[d]} />
          <p className="text-muted">Counties with fewer than {MIN_COUNTY_N} respondents are excluded from the map.</p>
          {missed.length > 0 && <p className="text-muted">Not shown on the map (name not recognised): {missed.join(", ")}</p>}
        </>
      )}
    </main>
  );
}
