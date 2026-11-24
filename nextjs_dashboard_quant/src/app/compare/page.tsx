"use client";

import Link from "next/link";
import { useDashboard } from "@/components/DataProvider";
import ChartCard from "@/components/ChartCard";
import { CompareTable, DriverHeatmap } from "@/components/SegmentBlocks";
import { pathwayCompareChart } from "@/lib/plots";

/** The six segments side by side: headline figures, pathway stages and every segmentation driver. */
export default function ComparePage() {
  const d = useDashboard();
  const nBySeg: Record<string, number> = Object.fromEntries(d.sizes.map((s) => [s.segment, s.n]));
  nBySeg["All"] = d.sizes.reduce((a, s) => a + s.n, 0);
  return (
    <main className="page">
      <h2>Compare the six segments</h2>
      <h5>Headline figures</h5>
      <CompareTable d={d} />
      <h5>Livelihood pathway</h5>
      <ChartCard title="Share of each segment that has reached each stage of the pathway"
        subtitle={<>The grey line shows all young people surveyed. Stage definitions are on the <Link href="/methodology/">Methodology tab</Link>.</>}
        build={() => pathwayCompareChart(d.stages, d.stage_order, nBySeg)} height={400} deps={[d]} />
      <h5>Segmentation drivers across the six segments</h5>
      <p className="text-muted">Darker cells are higher values within each row. ▲ marks the highest segment, ▼ the lowest.</p>
      <DriverHeatmap drivers={d.drivers} />
      <p className="footnote">
        Estimates of national size are directional, census-based model estimates; all other figures describe the young people surveyed
        and are not weighted. See <Link href="/methodology/">Methodology</Link>.
      </p>
    </main>
  );
}
