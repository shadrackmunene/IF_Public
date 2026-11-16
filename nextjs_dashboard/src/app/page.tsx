"use client";

import Link from "next/link";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { SegmentImage } from "@/components/SegmentBlocks";
import { cardGroups } from "@/lib/overviewCards";
import { segmentShareDonut } from "@/lib/plots";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

const HOW_TO: [string, string, string][] = [
  ["/segments/", "Segments overview", "Meet the six segments: who they are, what drives them, and what could help them."],
  ["/profiles/", "Segments data", "Compare the segments side by side, or look at one segment's data in detail."],
  ["/deep-dives/", "Deep dives", "Explore every survey question by segment."],
  ["/self-assessment/", "Self assessment", "Answer 12 questions to see which segment you are most like."],
  ["/methodology/", "Methodology", "How the study was done, definitions and caveats."],
];

export default function OverviewPage() {
  const d = useDashboard();
  const o = d.overview;
  return (
    <main className="page">
      <div className="hero">
        <div className="eyebrow">Imaginable Futures · Youth livelihood segmentation and pathways</div>
        <h1>Real Livelihoods of Kenyan Youth</h1>
        <p className="lead">{d.study.what}</p>
      </div>

      <h4>Why this study</h4>
      <div className="why-grid">
        {d.study.why.map(([t, desc]) => <div key={t} className="why-card"><h6>{t}</h6><p>{desc}</p></div>)}
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
                <div className="mini-tag">{d.profiles[s].tagline}</div>
              </div>
              <div className="mini-pop">{d.profiles[s].stats.population}</div>
            </Link>
          ))}
        </div>
      </div>

      <h4>How to use this dashboard</h4>
      <div className="howto">
        {HOW_TO.map(([href, label, desc]) => (
          <div key={href} className="howto-row"><Link href={href} className="btn btn-outline-primary">{label}</Link><span>{desc}</span></div>
        ))}
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
                    <div className="stat-value" style={{ color: dark }}>{c.value}</div>
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
        national population. See <Link href="/methodology/">Methodology</Link>.
      </p>
    </main>
  );
}
