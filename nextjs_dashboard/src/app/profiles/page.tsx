"use client";

import { useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import SegmentPill from "@/components/SegmentPill";
import { countySummary, populationEstimate } from "@/lib/data";
import { driverBarChart, pathwayStageChart } from "@/lib/plots";
import { SEGMENT_COLORS, SEGMENT_IDS, segName } from "@/lib/theme";

const TABS = [
  { label: "Demographic", category: "Demographic" },
  { label: "Behavioural", category: "Behavioral" },
  { label: "Psychographic", category: "Psychographic" },
  { label: "Livelihood pathway", category: null },
] as const;

export default function ProfilesPage() {
  const d = useDashboard();
  const [seg, setSeg] = useState("1");
  const [tab, setTab] = useState(0);

  const size = d.sizes.find((s) => s.segment === seg)!;
  const nBySeg: Record<string, number> = Object.fromEntries(d.sizes.map((s) => [s.segment, s.n]));
  nBySeg["All"] = d.sizes.reduce((a, s) => a + s.n, 0);
  const content = d.content[seg];
  const pop = populationEstimate(d, seg);
  const where = countySummary(d, seg);
  const cat = TABS[tab].category;

  return (
    <main className="page">
      <div className="layout">
        <aside className="card sticky-side">
          <h4 style={{ marginTop: 0 }}>Choose a segment</h4>
          {SEGMENT_IDS.map((s) => (
            <label key={s} className="radio">
              <input type="radio" name="segment" checked={seg === s} onChange={() => setSeg(s)} />
              <span className="dot" style={{ background: SEGMENT_COLORS[s] }} />
              {segName(s)} ({d.sizes.find((x) => x.segment === s)!.pct}%)
            </label>
          ))}
        </aside>

        <section>
          <h3><SegmentPill seg={seg} /> &nbsp;{size.pct}% of respondents (n={size.n})</h3>
          <p><strong>{content.headline}</strong></p>
          {pop && (
            <p className="text-muted" title={pop.note}>
              Estimated {pop.n.toLocaleString("en-US")} young people nationwide ({pop.pct}% of {pop.total.toLocaleString("en-US")}).
              Directional sizing only: these are approximate values, modelled from census records and predicted segments, not a headcount.
            </p>
          )}
          {where && <p className="text-muted">{where}</p>}

          <div className="tabs" role="tablist">
            {TABS.map((t, i) => (
              <button key={t.label} role="tab" aria-selected={tab === i} className={"tab" + (tab === i ? " active" : "")} onClick={() => setTab(i)}>
                {t.label}
              </button>
            ))}
          </div>

          {cat ? (
            (["pct", "score"] as const).map((kind) => {
              const title = kind === "pct" ? "Share of the segment" : "Average scores";
              const build = () => driverBarChart(d.drivers, cat, seg, kind, nBySeg);
              return build() ? <ChartCard key={`${cat}-${kind}`} title={title} build={build} height={380} deps={[d, seg, cat, kind]} /> : null;
            })
          ) : (
            <>
              <ChartCard build={() => pathwayStageChart(d.stages, d.stage_order, seg, nBySeg[seg])} height={320} deps={[d, seg]} />
              <h5>Where they sit</h5>
              <ul className="pathway-bullet-list">{content.where_they_sit.map((b) => <li key={b}>{b}</li>)}</ul>
              <h5>What the survey says would help them move on</h5>
              <ul className="pathway-bullet-list">{content.what_would_help.map((b) => <li key={b}>{b}</li>)}</ul>
              <p className="text-muted"><em>{content.hcd_link}</em></p>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
