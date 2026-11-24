/** The two to four drivers that set a segment apart, each drawn as a strip: the segment's dot in its colour, the
 *  other five segments as grey dots and all young people surveyed as a dark tick, on the driver's full scale. */
import type { DriverRow } from "@/lib/types";
import { fmtValue } from "@/lib/compare";
import { distinguishing } from "@/lib/distinct";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

const RANK_TEXT = { highest: "Highest of the six", lowest: "Lowest of the six", above: "Above average", below: "Below average" };

export function DistinctList({ drivers, seg, compact = false }: { drivers: DriverRow[]; seg: string; compact?: boolean }) {
  const items = distinguishing(drivers, seg);
  const [dark, mid] = SEGMENT_PALETTES[seg];
  return (
    <div className={"dv-list" + (compact ? " compact" : "")}>
      {items.map((i) => {
        const [lo, hi] = i.axis;
        const pos = (x: number) => `${Math.min(100, Math.max(0, ((x - lo) / (hi - lo)) * 100))}%`;
        return (
          <div key={i.label} className="dv">
            <div className="dv-head">
              <span className="dv-label">{i.label}</span>
              <b className="dv-val" style={{ color: dark }}>{fmtValue(i.value, i.isPct)}</b>
            </div>
            <div className="dv-track" role="img"
              aria-label={`${segName(seg)} ${fmtValue(i.value, i.isPct)}; all young people surveyed ${fmtValue(i.all, i.isPct)}`}>
              {SEGMENT_IDS.filter((s) => s !== seg && i.vals[s] !== undefined).map((s) => (
                <span key={s} className="dv-other" style={{ left: pos(i.vals[s]) }} title={`${segName(s)}: ${fmtValue(i.vals[s], i.isPct)}`} />
              ))}
              {i.all !== undefined && <span className="dv-all" style={{ left: pos(i.all) }} title={`All surveyed: ${fmtValue(i.all, i.isPct)}`} />}
              <span className="dv-dot" style={{ left: pos(i.value), background: mid, borderColor: dark }}
                title={`${segName(seg)}: ${fmtValue(i.value, i.isPct)}`} />
            </div>
            <div className="dv-foot">
              <span>{RANK_TEXT[i.rank]}</span>
              <span>All surveyed: {fmtValue(i.all, i.isPct)}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function DistinctLegend() {
  return (
    <p className="dv-legend">
      <span className="dv-key dot-seg" /> this segment <span className="dv-key dot-other" /> other segments{" "}
      <span className="dv-key tick-all" /> all young people surveyed
    </p>
  );
}
