"use client";

import { useEffect, useRef, useState } from "react";
import type { PlotSpec } from "@/lib/types";
import { PLOTLY_CONFIG } from "@/lib/plots";

/** Renders a Plotly chart. The chart is only built and drawn once it scrolls near the viewport, so a page with
 *  dozens of charts (Deep dives) opens instantly and draws each chart as it is reached. Plotly.js itself is
 *  loaded on demand, in one shared chunk. */
export default function Plot({ build, height, deps }: { build: () => PlotSpec | null; height: number; deps: unknown[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") { setVisible(true); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { setVisible(true); io.disconnect(); }
    }, { rootMargin: "600px 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!visible || !ref.current) return;
    let cancelled = false;
    const el = ref.current;
    import("plotly.js-dist-min").then((m) => {
      if (cancelled) return;
      const Plotly = (m as any).default ?? m;
      const spec = build();
      if (spec) Plotly.react(el, spec.data, spec.layout, PLOTLY_CONFIG);
    });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible, ...deps]);

  useEffect(() => {
    const el = ref.current;
    return () => {
      if (el) import("plotly.js-dist-min").then((m) => ((m as any).default ?? m).purge(el)).catch(() => {});
    };
  }, []);

  return <div ref={ref} className={visible ? "plot" : "plot plot-skeleton"} style={{ minHeight: height }} />;
}
