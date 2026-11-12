"use client";

import { useEffect, useRef, useState } from "react";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import SegmentPill from "@/components/SegmentPill";
import { AGE_MAX, AGE_MESSAGE, AGE_MIN, score } from "@/lib/assessment";
import { dataUrl } from "@/lib/data";
import { pathwayStageChart, probabilityChart } from "@/lib/plots";
import type { Model } from "@/lib/types";

type Result = { segment: string; probabilities: Record<string, number> };

export default function SelfAssessmentPage() {
  const d = useDashboard();
  const qs = d.questionnaire;
  const n = qs.length;
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | number>>({ A101: qs.find((q) => q.id === "A101")?.value ?? 23 });
  const [ageError, setAgeError] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [open, setOpen] = useState(false);
  const model = useRef<Promise<Model> | null>(null);

  // Start loading the (3 KB) model as soon as the page opens.
  useEffect(() => { model.current = fetch(dataUrl("model.json")).then((r) => r.json()); }, []);

  const q = qs[step];
  const age = Number(answers["A101"]);
  const ageOk = Number.isFinite(age) && age >= AGE_MIN && age <= AGE_MAX;
  const answered = q.widget === "numeric" ? answers[q.id] !== undefined && answers[q.id] !== "" : answers[q.id] !== undefined;
  const pct = Math.round((step / n) * 100);

  const next = () => {
    if (q.id === "A101" && !ageOk) { setAgeError(true); return; }
    setStep((s) => Math.min(s + 1, n - 1));
  };

  const submit = async () => {
    if (!ageOk) { setAgeError(true); setStep(qs.findIndex((x) => x.id === "A101")); return; }
    setProcessing(true);
    const started = Date.now();
    try {
      const m = await model.current!;
      const r = score(m, Object.fromEntries(qs.map((x) => [x.id, answers[x.id]])));
      await new Promise((res) => setTimeout(res, Math.max(0, 1200 - (Date.now() - started)))); // never just flashes
      setResult(r);
      setOpen(true);
    } finally {
      setProcessing(false);
    }
  };

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const nBySeg = (s: string) => d.sizes.find((x) => x.segment === s)?.n;
  const content = result ? d.content[result.segment] : null;

  return (
    <main className="page">
      <div className="layout" style={{ gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)" }}>
        <section>
          <h2>Instructions to self assessment</h2>
          <ol className="instruction-list">
            <li>This tool is for young people aged {AGE_MIN} to {AGE_MAX}.</li>
            <li>You will answer {n} short questions, one at a time. Pick the answer that fits you best, then press Next.</li>
            <li>Made a mistake? Press Back to change an earlier answer. The progress bar shows how far along you are.</li>
            <li>On the last question, press See my results. A window opens showing the segment you most resemble, what that means and what
              could help you move forward. Press Close when you have finished reading.</li>
            <li>To read your result again, press View my results again.</li>
          </ol>

          <div className="card pad-lg">
            <div className="progress"><div style={{ width: `${pct}%` }} /></div>
            <div className="wiz-pct">{pct}% complete ({step} of {n} answered)</div>
            <div className="q-step">
              <div className="q-counter">Question {step + 1} of {n}</div>
              <div className="q-text">{q.text}</div>
              {q.widget === "numeric" ? (
                <>
                  <input type="number" min={q.min} max={q.max} value={String(answers[q.id] ?? "")}
                    onChange={(e) => { setAnswers({ ...answers, [q.id]: e.target.value === "" ? "" : Number(e.target.value) }); setAgeError(false); }} />
                  {ageError && <div className="alert-danger" role="alert">{AGE_MESSAGE}</div>}
                </>
              ) : (
                q.options!.map((o, i) => (
                  <label key={i} className="radio">
                    <input type="radio" name={q.id} checked={answers[q.id + "_i"] === i}
                      onChange={() => setAnswers({ ...answers, [q.id]: o.value, [q.id + "_i"]: i })} />
                    {o.label}
                  </label>
                ))
              )}
            </div>
            <div className="wiz-nav">
              <button className="btn secondary" style={{ visibility: step === 0 ? "hidden" : "visible" }} onClick={() => setStep(step - 1)}>Back</button>
              {step < n - 1 ? (
                <button className="btn" disabled={!answered} onClick={next}>Next</button>
              ) : (
                <button className="btn" disabled={!answered} onClick={submit}>See my results</button>
              )}
            </div>
          </div>
        </section>

        <section>
          {result ? (
            <div className="card pad-lg">
              <h4 style={{ marginTop: 0 }}>You match <SegmentPill seg={result.segment} /></h4>
              <button className="btn" onClick={() => setOpen(true)}>View my results again</button>
            </div>
          ) : (
            <p className="text-muted">Answer the questions on the left and press See my results.</p>
          )}
        </section>
      </div>

      {processing && (
        <div className="overlay" role="status">
          <div className="spinner" />
          <div className="processing-text">Analysing your answers…</div>
        </div>
      )}

      {open && result && content && (
        <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && setOpen(false)}>
          <div className="modal" role="dialog" aria-modal="true" aria-label="Your segment">
            <div className="modal-head"><h3>Your segment</h3><button className="modal-x" aria-label="Close" onClick={() => setOpen(false)}>×</button></div>
            <div className="modal-body">
              <h3>You match <SegmentPill seg={result.segment} /></h3>
              <p><strong>{content.headline}</strong></p>
              <ChartCard build={() => probabilityChart(result.probabilities)} height={280} deps={[result]} />
              <h5>Where you likely sit</h5>
              <ul className="pathway-bullet-list">{content.where_they_sit.map((b) => <li key={b}>{b}</li>)}</ul>
              <h5>Your growth pathway - what would help you move on</h5>
              <ul className="pathway-bullet-list">{content.what_would_help.map((b) => <li key={b}>{b}</li>)}</ul>
              <ChartCard build={() => pathwayStageChart(d.stages, d.stage_order, result.segment, nBySeg(result.segment))} height={320} deps={[result, d]} />
            </div>
            <div className="modal-foot"><button className="btn" onClick={() => setOpen(false)}>Close</button></div>
          </div>
        </div>
      )}
    </main>
  );
}
