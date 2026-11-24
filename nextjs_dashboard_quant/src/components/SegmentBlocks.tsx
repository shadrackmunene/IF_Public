/** Segment storytelling and comparison blocks shared by the Segments overview, Segments data and Self assessment
 *  pages (same markup and class names as the Shiny dashboard). */
import type { Dashboard, DriverRow } from "@/lib/types";
import { assetUrl } from "@/lib/data";
import { CATEGORY_TITLES, definingDrivers, driverRows, fmtValue } from "@/lib/compare";
import { SEGMENT_COLORS, SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

export function SegmentImage({ d, seg, className }: { d: Dashboard; seg: string; className?: string }) {
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={assetUrl(d.profiles[seg].image)} alt="" className={className} />;
}

/** Data-focused header: name, number and headline figures only (the segment's story lives on the website). */
export function SegmentHeader({ d, seg, compact = false }: { d: Dashboard; seg: string; compact?: boolean }) {
  const c = d.profiles[seg];
  const [dark] = SEGMENT_PALETTES[seg];
  const st = c.stats;
  const size = d.sizes.find((s) => s.segment === seg);
  const chips: [string, string][] = [
    [st.population, `young people in Kenya (${st.share})`], [st.median_age, "median age"], [st.women, "women"],
    [st.rural, "live in rural areas"], [st.median_income, "median monthly income"],
  ];
  if (size) chips.push([size.n.toLocaleString("en-US"), "young people surveyed"]);
  return (
    <div className="seg-header" style={{ borderLeft: `6px solid ${dark}` }}>
      <SegmentImage d={d} seg={seg} className="hdr-img" />
      <div>
        <div className="seg-num" style={{ color: dark }}>Segment {c.number}</div>
        <h3 style={{ color: dark }}>{segName(seg)}</h3>
        {!compact && (
          <div className="chip-stats">
            {chips.map(([v, l]) => <div key={l} className="chip-stat"><b>{v}</b><span>{l}</span></div>)}
          </div>
        )}
      </div>
    </div>
  );
}

/** Headline figures for the six segments, segments as columns (numeric rows only). */
export function CompareTable({ d }: { d: Dashboard }) {
  return (
    <div className="table-scroll">
      <table className="cmp-table profile">
        <thead>
          <tr>
            <th />
            {SEGMENT_IDS.map((s) => (
              <th key={s}>
                <SegmentImage d={d} seg={s} className="cmp-img" />
                <span className="cmp-name" style={{ color: SEGMENT_PALETTES[s][0] }}>{segName(s)}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {d.compare_rows.filter(([key]) => key in d.profiles["1"].stats).map(([key, title]) => (
            <tr key={key}>
              <th scope="row">{title}</th>
              {SEGMENT_IDS.map((s) => {
                const p = d.profiles[s];
                return <td key={s} className="num">{p.stats[key as keyof typeof p.stats]}</td>;
              })}
            </tr>
          ))}
          <tr>
            <th scope="row">Young people surveyed (n)</th>
            {SEGMENT_IDS.map((s) => <td key={s} className="num">{d.sizes.find((x) => x.segment === s)?.n ?? "–"}</td>)}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

/** Every segmentation driver across the six segments; each row shaded from its lowest to its highest value. */
export function DriverHeatmap({ drivers }: { drivers: DriverRow[] }) {
  const { segs, groups } = driverRows(drivers);
  return (
    <div className="table-scroll">
      <table className="cmp-table heat">
        <thead>
          <tr>
            <th />
            {segs.map((s) => <th key={s}><span className="dot" style={{ background: SEGMENT_COLORS[s] }} />{segName(s)}</th>)}
            <th className="all-col">All surveyed</th>
          </tr>
        </thead>
        <tbody>
          {groups.flatMap((g) => [
            <tr key={g.cat} className="cat-row"><td colSpan={segs.length + 2}>{CATEGORY_TITLES[g.cat]}</td></tr>,
            ...g.rows.map((row) => {
              const present = segs.map((s) => row.vals[s]).filter((v): v is number => v !== undefined);
              const lo = Math.min(...present);
              const hi = Math.max(...present);
              return (
                <tr key={g.cat + row.label}>
                  <th scope="row">{row.label}</th>
                  {segs.map((s) => {
                    const v = row.vals[s];
                    if (v === undefined) return <td key={s}>–</td>;
                    const t = hi > lo ? (v - lo) / (hi - lo) : 0;
                    const alpha = 0.08 + 0.62 * t;
                    const mark = hi > lo ? (v === hi ? " ▲" : v === lo ? " ▼" : "") : "";
                    return (
                      <td key={s} style={{ background: `rgba(15,107,82,${alpha.toFixed(2)})`, color: alpha > 0.5 ? "#fff" : undefined }}>
                        {fmtValue(v, row.isPct)}<span className="mk">{mark}</span>
                      </td>
                    );
                  })}
                  <td className="all-col">{fmtValue(row.vals["All"], row.isPct)}</td>
                </tr>
              );
            }),
          ])}
        </tbody>
      </table>
    </div>
  );
}

export function DefiningList({ drivers, seg }: { drivers: DriverRow[]; seg: string }) {
  const items = definingDrivers(drivers, seg);
  if (!items.length) return null;
  return (
    <div className="defining">
      {(["highest", "lowest"] as const).map((w) => {
        const group = items.filter((i) => i.which === w);
        if (!group.length) return null;
        return (
          <div key={w} className="def-col">
            <div className="def-title">{w === "highest" ? "▲ Highest of the six segments" : "▼ Lowest of the six segments"}</div>
            <ul>
              {group.map((i) => (
                <li key={i.label}><span>{i.label}</span> <b>{i.value}</b> <span className="text-muted">(all surveyed: {i.all})</span></li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
