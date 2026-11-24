"use client";

import { useEffect, useState } from "react";
import ChartCard from "./ChartCard";
import { countyChoropleth, loadCounties, type CountyValue } from "@/lib/countyMap";

/** Kenya county map in a chart card; draws once the boundary file has loaded. */
export default function CountyMap({ rows, colors, title, suffix, greyHover, deps }: {
  rows: CountyValue[]; colors: [string, string]; title: string; suffix?: string; greyHover?: string; deps: unknown[];
}) {
  const [geo, setGeo] = useState<any>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => { loadCounties().then(setGeo).catch(() => setFailed(true)); }, []);
  if (failed) return <p className="text-muted small">The county map could not be loaded.</p>;
  return (
    <ChartCard bare height={560} deps={[geo, ...deps]}
      build={() => (geo ? countyChoropleth(geo, rows, { colors, title, suffix, greyHover }) : null)} />
  );
}
