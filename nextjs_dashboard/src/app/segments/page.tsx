"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import { Opportunities, PathwayBlock, SegmentHeader, SegmentImage } from "@/components/SegmentBlocks";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

/** One card per segment (illustration, traits, size, key figures); click a card for the segment's story,
 *  pathway and opportunity areas. /segments/?seg=3 opens on that segment. */
export default function SegmentsPage() {
  const d = useDashboard();
  const [seg, setSeg] = useState<string>(SEGMENT_IDS[0]);
  const detail = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const want = new URLSearchParams(window.location.search).get("seg");
    if (want && (SEGMENT_IDS as readonly string[]).includes(want)) {
      setSeg(want);
      setTimeout(() => detail.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
    }
  }, []);

  const pick = (s: string) => {
    setSeg(s);
    window.history.replaceState(null, "", `?seg=${s}`);
    setTimeout(() => detail.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  };

  const c = d.profiles[seg];
  const dark = SEGMENT_PALETTES[seg][0];
  return (
    <main className="page">
      <h2>Six segments of Kenyan youth</h2>
      <p className="lead-sm">
        Each segment is a group of young people who share circumstances, behaviours and mindsets. They are numbered as in the study
        report, broadly from those who most need help to establish a livelihood to those who most need help to progress. Click a
        segment to read its story, its pathway and what could help.
      </p>

      <div className="seg-grid">
        {SEGMENT_IDS.map((s) => {
          const p = d.profiles[s];
          const [pdark, mid, , light] = SEGMENT_PALETTES[s];
          return (
            <div key={s} role="button" tabIndex={0} aria-label={`Show ${segName(s)}`} aria-pressed={seg === s}
              className={"seg-card" + (seg === s ? " selected" : "")} style={{ ["--seg" as any]: mid }}
              onClick={() => pick(s)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(s); } }}>
              <div className="seg-card-img" style={{ background: light }}><SegmentImage d={d} seg={s} /></div>
              <div className="seg-card-body">
                <div className="seg-num" style={{ color: pdark }}>Segment {p.number}</div>
                <h5 style={{ color: pdark }}>{segName(s)}</h5>
                <div className="traits">
                  {p.traits.map((t) => <span key={t} className="trait" style={{ background: light, color: pdark }}>{t}</span>)}
                </div>
                <p className="seg-tagline">{p.tagline}</p>
                <div className="kv-grid">
                  <div className="kv"><b>{p.stats.population}</b><span>young people ({p.stats.share})</span></div>
                  <div className="kv"><b>{p.stats.median_age}</b><span>median age</span></div>
                  <div className="kv"><b>{p.stats.women}</b><span>women</span></div>
                  <div className="kv"><b>{p.stats.median_income}</b><span>median monthly income</span></div>
                </div>
                <div className="seg-more" style={{ color: pdark }}>Read their story →</div>
              </div>
            </div>
          );
        })}
      </div>

      <div ref={detail} className="segment-detail card">
        <SegmentHeader d={d} seg={seg} />
        <div className="two-col wide-left">
          <div>
            <h5>Who they are</h5>
            {c.narrative.map((p) => <p key={p.slice(0, 30)}>{p}</p>)}
            <blockquote className="quote" style={{ borderColor: dark }}>“{c.quote}”</blockquote>
          </div>
          <div>
            <div className="eb enablers"><h6>What helps them</h6><ul>{c.enablers.map((e) => <li key={e}>{e}</li>)}</ul></div>
            <div className="eb barriers"><h6>What holds them back</h6><ul>{c.barriers.map((b) => <li key={b}>{b}</li>)}</ul></div>
          </div>
        </div>
        <h5>Their livelihood pathway</h5>
        <PathwayBlock d={d} seg={seg} />
        <h5>Opportunity areas</h5>
        <p className="text-muted">Where programmes and partners could make the most difference for this segment.</p>
        <Opportunities d={d} seg={seg} />
        <div className="detail-actions">
          <Link className="btn" href={`/profiles/?seg=${seg}`}>See the data for {segName(seg)} →</Link>
        </div>
      </div>
    </main>
  );
}
