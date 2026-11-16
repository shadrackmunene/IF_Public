"use client";

import { useEffect, useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { CompareTable, DefiningList, DriverHeatmap, SegmentHeader } from "@/components/SegmentBlocks";
import { countySummary, populationEstimate } from "@/lib/data";
import { driverBarChart, pathwayCompareChart, pathwayStageChart } from "@/lib/plots";
import { SEGMENT_COLORS, SEGMENT_IDS, r0, segName } from "@/lib/theme";

const CATS: [string, string][] = [["Demographic", "Demographic"], ["Behavioral", "Behavioural"], ["Psychographic", "Psychometric"]];

/** SEGMENTS DATA: "All segments" compares the six side by side (default); one segment shows its drivers and
 *  pathway against all young people surveyed, in a single two-column scroll. /profiles/?seg=3 opens a segment. */
export default function SegmentDataPage() {
  const d = useDashboard();
  const [seg, setSeg] = useState("all");

  useEffect(() => {
    const want = new URLSearchParams(window.location.search).get("seg");
    if (want && (want === "all" || (SEGMENT_IDS as readonly string[]).includes(want))) setSeg(want);
  }, []);

  const choose = (s: string) => {
    setSeg(s);
    window.history.replaceState(null, "", `?seg=${s}`);
  };

  const nBySeg: Record<string, number> = Object.fromEntries(d.sizes.map((s) => [s.segment, s.n]));
  nBySeg["All"] = d.sizes.reduce((a, s) => a + s.n, 0);

  return (
    <main className="page">
      <div className="layout">
        <aside className="card sticky-side">
          <h4 style={{ marginTop: 0 }}>Show</h4>
          <label className="radio">
            <input type="radio" name="segment" checked={seg === "all"} onChange={() => choose("all")} />
            <span className="dot all" /><b>All segments (compare)</b>
          </label>
          {SEGMENT_IDS.map((s) => (
            <label key={s} className="radio">
              <input type="radio" name="segment" checked={seg === s} onChange={() => choose(s)} />
              <span className="dot" style={{ background: SEGMENT_COLORS[s] }} />{segName(s)}
            </label>
          ))}
          <p className="text-muted small" style={{ marginTop: 10 }}>▲ / ▼ mark where a segment is the highest / lowest of the six.</p>
        </aside>

        <section>{seg === "all" ? <AllView nBySeg={nBySeg} /> : <SegmentView seg={seg} nBySeg={nBySeg} />}</section>
      </div>
    </main>
  );
}

function AllView({ nBySeg }: { nBySeg: Record<string, number> }) {
  const d = useDashboard();
  return (
    <>
      <h3>All segments compared</h3>
      <p className="insight">
        The segments differ most in how they learned their skills, how they find work and what work means to them. Survival Workers
        and Stability Seekers rely almost entirely on family and friends for work; Career Pursuers find work through applications and
        professional contacts; Skill Investors are the only group for whom work is mainly part of who they are rather than a means to an end.
      </p>
      <h5>At a glance</h5>
      <CompareTable d={d} />
      <h5>Livelihood pathway</h5>
      <ChartCard title="Share of each segment that has reached each stage of the pathway"
        subtitle="The grey line shows all young people surveyed. Stage definitions are on the Methodology tab."
        build={() => pathwayCompareChart(d.stages, d.stage_order, nBySeg)} height={400} deps={[d]} />
      <h5>Segmentation drivers across the six segments</h5>
      <p className="text-muted">Darker cells are higher values within each row. ▲ marks the highest segment, ▼ the lowest.</p>
      <DriverHeatmap drivers={d.drivers} />
      <p className="footnote">
        Estimates of national size are directional, census-based model estimates; all other figures describe the young people surveyed
        and are not weighted. See Methodology.
      </p>
    </>
  );
}

function SegmentView({ seg, nBySeg }: { seg: string; nBySeg: Record<string, number> }) {
  const d = useDashboard();
  const size = d.sizes.find((s) => s.segment === seg)!;
  const pop = populationEstimate(d, seg);
  const where = countySummary(d, seg);
  return (
    <>
      <SegmentHeader d={d} seg={seg} />
      <h5>What sets them apart in the data</h5>
      <DefiningList drivers={d.drivers} seg={seg} />
      <div className="chart-grid">
        {CATS.flatMap(([cat, title]) =>
          (["pct", "score"] as const).map((kind) => {
            const build = () => driverBarChart(d.drivers, cat, seg, kind, nBySeg);
            return build() ? (
              <ChartCard key={`${seg}-${cat}-${kind}`} title={`${title}: ${kind === "pct" ? "share of the segment" : "averages"}`}
                build={build} height={360} deps={[d, seg, cat, kind]} />
            ) : null;
          }))}
        <div className="card chart-card wide">
          <h6>Livelihood pathway: share who have reached each stage</h6>
          <ChartCard build={() => pathwayStageChart(d.stages, d.stage_order, seg, nBySeg)} height={340} deps={[d, seg]} bare />
          <p className="small">{d.profiles[seg].pathway_summary}</p>
        </div>
      </div>
      <div className="card pad-lg">
        <h5 style={{ marginTop: 0 }}>What the survey says about their next step</h5>
        <ul className="pathway-bullet-list">{d.content[seg].what_would_help.map((b) => <li key={b}>{b}</li>)}</ul>
      </div>
      <div className="footnote-box">
        <h6>Technical notes</h6>
        <p>Survey: {size.n} of the {nBySeg["All"].toLocaleString("en-US")} young people surveyed ({r0(size.pct)}%) are in this segment.</p>
        {pop && (
          <p>National estimate: about {(pop.n / 1e6).toFixed(1)} million young people ({r0(pop.pct)}% of about{" "}
            {(pop.total / 1e6).toFixed(1)} million aged 16-30), a
            directional, census-based model estimate, not a headcount.</p>
        )}
        {where && <p>{where.replace("Most prevalent in", "Among the counties surveyed, most common in")}</p>}
      </div>
    </>
  );
}
