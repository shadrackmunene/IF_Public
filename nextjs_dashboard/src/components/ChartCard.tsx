"use client";

import Plot from "./Plot";
import type { PlotSpec } from "@/lib/types";

export default function ChartCard({ title, build, height, deps }: {
  title?: string; build: () => PlotSpec | null; height: number; deps: unknown[];
}) {
  return (
    <div className="card">
      {title && <h6>{title}</h6>}
      <Plot build={build} height={height} deps={deps} />
    </div>
  );
}
