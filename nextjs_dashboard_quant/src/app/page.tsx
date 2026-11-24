"use client";

import Link from "next/link";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { SegmentImage } from "@/components/SegmentBlocks";
import { distinctSentences } from "@/components/Distinct";
import { cardGroups } from "@/lib/overviewCards";
import { segmentShareDonut } from "@/lib/plots";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

/** Data-focused front page: segment sizes with each segment's two strongest distinguishing drivers, then the
 *  headline figures for everyone surveyed. Background and segment stories are on the study website. */
export default function OverviewPage() {
  const d = useDashboard();
  const o = d.overview;
  return (
    <main className="page">
      <div className="hero compact">
        <div className="eyebrow">Imaginable Futures · Youth livelihood segmentation · Data dashboard</div>
        <h1>Real Livelihoods of Kenyan Youth: the data</h1>
        <p className="lead">
          Survey results for {o.n_respondents.toLocaleString("en-US")} young people aged 16 to 30 in nine Kenyan counties, grouped
          into six segments. Explore how the segments differ, where they are found and every survey question by segment.
        </p>
      </div>

      <h4>Six segments of Kenyan youth</h4>
      <div className="two-col">
        <ChartCard title="Estimated share of young people aged 16 to 30" build={() => segmentShareDonut(d.population, d.sizes)} height={340} deps={[d]} />
        <div className="mini-list">
          {SEGMENT_IDS.map((s) => (
            <Link key={s} href={`/segments/?seg=${s}`} className="mini-row">
              <SegmentImage d={d} seg={s} className="mini-img" />
              <div>
                <div className="mini-name" style={{ color: SEGMENT_PALETTES[s][0] }}>{segName(s)}</div>
                <div className="mini-tag">
                  {distinctSentences(d.drivers, s).map((p) => (
                    <span key={p.key} className="mini-fact"><b>{p.lead}</b>{p.rest}</span>
                  ))}
                </div>
              </div>
              <div className="mini-pop">{d.profiles[s].stats.population}</div>
            </Link>
          ))}
        </div>
      </div>

      <h4>The young people surveyed at a glance</h4>
      {cardGroups(o).map((g) => {
        const [dark, mid, , light] = g.palette;
        return (
          <section key={g.title}>
            <h6 className="group-title">{g.title}</h6>
            <div className="stat-grid">
              {g.cards.map((c) => (
                <div key={c.title} className="stat-card" style={{ background: light, borderColor: `${mid}55` }}>
                  <div className="stat-icon" style={{ background: `${mid}33`, color: dark }}>{c.icon}</div>
                  <div>
                    <div className="stat-label">{c.title}</div>
                    <div className={"stat-value" + (c.words ? " words" : "")} style={{ color: dark }}>{c.value}</div>
                    <div className="stat-sub">{c.sub}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      })}
      <p className="footnote">
        Figures describe the {o.n_respondents.toLocaleString("en-US")} young people surveyed in nine counties and are not weighted to the
        national population; segment sizes are directional, census-based estimates. See <Link href="/methodology/">Methodology</Link>.
      </p>
    </main>
  );
}
