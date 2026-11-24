"use client";

import { useCallback, useEffect, useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { DistinctLegend, DistinctList } from "@/components/Distinct";
import Modal from "@/components/Modal";
import { DefiningList, SegmentHeader, SegmentImage } from "@/components/SegmentBlocks";
import { countySummary, populationEstimate } from "@/lib/data";
import { driverBarChart, pathwayStageChart } from "@/lib/plots";
import { SEGMENT_IDS, SEGMENT_PALETTES, r0, segName } from "@/lib/theme";

const CATS: [string, string][] = [["Demographic", "Demographic"], ["Behavioral", "Behavioural"], ["Psychographic", "Psychometric"]];

/** One card per segment with its size and the two to four drivers that set it apart; click a card to open the
 *  segment's full data (drivers, pathway, technical notes) in a pop-up window. /segments/?seg=3 opens it directly. */
export default function SegmentsPage() {
  const d = useDashboard();
  const [seg, setSeg] = useState<string>(SEGMENT_IDS[0]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const want = new URLSearchParams(window.location.search).get("seg");
    if (want && (SEGMENT_IDS as readonly string[]).includes(want)) {
      setSeg(want);
      setOpen(true);
    }
  }, []);

  const pick = (s: string) => {
    setSeg(s);
    setOpen(true);
    window.history.replaceState(null, "", `?seg=${s}`);
  };
  const close = useCallback(() => {
    setOpen(false);
    window.history.replaceState(null, "", window.location.pathname);
  }, []);

  const nBySeg: Record<string, number> = Object.fromEntries(d.sizes.map((s) => [s.segment, s.n]));
  nBySeg["All"] = d.sizes.reduce((a, s) => a + s.n, 0);

  return (
    <main className="page">
      <h2>Six segments: what sets each apart</h2>
      <p className="lead-sm">
        Each card shows the two to four segmentation drivers on which that segment differs most from the other five. Click a
        segment for its full data.
      </p>
      <DistinctLegend />

      <div className="seg-grid">
        {SEGMENT_IDS.map((s) => {
          const p = d.profiles[s];
          const [pdark, mid, , light] = SEGMENT_PALETTES[s];
          return (
            <div key={s} role="button" tabIndex={0} aria-label={`Show data for ${segName(s)}`} aria-haspopup="dialog"
              className={"seg-card" + (open && seg === s ? " selected" : "")} style={{ ["--seg" as any]: mid }}
              onClick={() => pick(s)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(s); } }}>
              <div className="seg-card-top" style={{ background: light }}>
                <SegmentImage d={d} seg={s} className="seg-card-thumb" />
                <div>
                  <div className="seg-num" style={{ color: pdark }}>Segment {p.number}</div>
                  <h5 style={{ color: pdark }}>{segName(s)}</h5>
                  <div className="seg-size"><b>{p.stats.population}</b> young people ({p.stats.share})</div>
                </div>
              </div>
              <div className="seg-card-body">
                <div className="dv-title">What sets them apart</div>
                <DistinctList drivers={d.drivers} seg={s} compact />
                <div className="seg-more" style={{ color: pdark }}>See all their data →</div>
              </div>
            </div>
          );
        })}
      </div>

      {open && (
        <Modal title={`Segment ${d.profiles[seg].number}: ${segName(seg)}`} onClose={close} wide>
          <div className="segment-detail"><SegmentView seg={seg} nBySeg={nBySeg} /></div>
        </Modal>
      )}
    </main>
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
      <h5>Where they are highest or lowest of the six segments</h5>
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
        </div>
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
        <p>“What sets them apart” ranks the segmentation drivers by how far the segment sits from the other five, on each driver&apos;s
          full scale. See Methodology.</p>
      </div>
    </>
  );
}
