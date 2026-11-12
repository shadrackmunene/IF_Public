"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { ALL_TOPICS, dimensions, filterQuestions, sectionsFor, topicsFor } from "@/lib/data";
import { isLikert, questionChart, questionTitle, radarChart } from "@/lib/plots";
import { SEGMENT_COLORS, SEGMENT_IDS, SEGMENT_NAMES } from "@/lib/theme";

export default function DeepDivesPage() {
  const d = useDashboard();
  const dims = useMemo(() => dimensions(d), [d]);
  const [dim, setDim] = useState(dims[0]);
  const [section, setSection] = useState(() => sectionsFor(d, dims[0])[0]);
  const [topic, setTopic] = useState(ALL_TOPICS);
  const [search, setSearch] = useState("");
  const [kind, setKind] = useState("all");
  const [seg, setSeg] = useState("all");

  const sections = useMemo(() => sectionsFor(d, dim), [d, dim]);
  const topics = useMemo(() => topicsFor(d, dim, section), [d, dim, section]);

  // Shareable links: /deep-dives/?dim=Psychology&section=...&topic=...&seg=3 opens that view.
  const pendingTopic = useRef<string | null>(null);
  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const wantDim = p.get("dim");
    if (!wantDim || !dims.includes(wantDim)) return;
    const secs = sectionsFor(d, wantDim);
    const wantSec = p.get("section");
    pendingTopic.current = p.get("topic");
    setDim(wantDim);
    setSection(wantSec && secs.includes(wantSec) ? wantSec : secs[0]);
    if (p.get("seg") && SEGMENT_IDS.includes(p.get("seg") as any)) setSeg(p.get("seg")!);
    if (p.get("kind")) setKind(p.get("kind")!);
    if (p.get("q")) setSearch(p.get("q")!);
  }, [d, dims]);

  // Changing the dimension or section resets the narrower filters, as in the Shiny app.
  useEffect(() => { if (!sections.includes(section)) setSection(sections[0]); }, [sections, section]);
  useEffect(() => { setTopic(pendingTopic.current ?? ALL_TOPICS); pendingTopic.current = null; }, [dim, section]);

  const names = useMemo(() => (seg === "all" ? d.names : { [seg]: d.names[seg] }), [d, seg]);
  const qs = useMemo(() => filterQuestions(d, dim, section, topic, search, kind, isLikert), [d, dim, section, topic, search, kind]);
  const showRadar = dim === "Context" && section === sectionsFor(d, "Context")[0] && kind !== "likert";

  return (
    <main className="page">
      <div className="layout">
        <aside className="card sticky-side">
          <div className="field">
            <div className="label">Dimension</div>
            {dims.map((x) => (
              <label key={x} className="radio"><input type="radio" name="dim" checked={dim === x} onChange={() => setDim(x)} />{x}</label>
            ))}
          </div>
          <div className="field">
            <label htmlFor="section">Section</label>
            <select id="section" value={section} onChange={(e) => setSection(e.target.value)}>
              {sections.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="topic">Topic (specific area)</label>
            <select id="topic" value={topic} onChange={(e) => setTopic(e.target.value)}>
              <option value={ALL_TOPICS}>All topics</option>
              {topics.map(([t, n]) => <option key={t} value={t}>{t} ({n})</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="search">Search questions</label>
            <input id="search" type="text" value={search} placeholder="e.g. saving, training, AI" onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="field">
            <div className="label">Question type</div>
            {[["all", "All questions"], ["likert", "Rating scales (Likert)"], ["other", "Choices & other"]].map(([v, l]) => (
              <label key={v} className="radio"><input type="radio" name="kind" checked={kind === v} onChange={() => setKind(v)} />{l}</label>
            ))}
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <div className="label">Segment</div>
            <label className="radio"><input type="radio" name="seg" checked={seg === "all"} onChange={() => setSeg("all")} />
              <span className="dot all" />All segments</label>
            {SEGMENT_IDS.map((s) => (
              <label key={s} className="radio"><input type="radio" name="seg" checked={seg === s} onChange={() => setSeg(s)} />
                <span className="dot" style={{ background: SEGMENT_COLORS[s] }} />{SEGMENT_NAMES[s]}</label>
            ))}
          </div>
        </aside>

        <section>
          {showRadar && (
            <ChartCard title="Age, income and household profile by segment (highest segment = 100)"
              build={() => radarChart(d.nums, names)} height={520} deps={[d, names]} />
          )}
          {qs.map((q) => (
            <ChartCard key={`${dim}-${section}-${q.code}`} title={questionTitle(q)}
              build={() => questionChart(q, d.dists, d.nums, names)} height={340} deps={[d, names, q]} />
          ))}
          {!qs.length && <p className="text-muted">No questions match these choices.</p>}
        </section>
      </div>
    </main>
  );
}
