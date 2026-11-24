"use client";

import Plot from "./Plot";
import type { PlotSpec } from "@/lib/types";

/** A chart in a card. `bare` drops the card frame (for a chart placed inside another card). */
export default function ChartCard({ title, subtitle, build, height, deps, bare = false }: {
  title?: string; subtitle?: string; build: () => PlotSpec | null; height: number; deps: unknown[]; bare?: boolean;
}) {
  const body = (
    <>
      {title && <h6>{title}</h6>}
      {subtitle && <p className="card-sub">{subtitle}</p>}
      <Plot build={build} height={height} deps={deps} />
    </>
  );
  return bare ? body : <div className="card chart-card">{body}</div>;
}
