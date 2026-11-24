/** The two to four drivers that set a segment apart, each as a plain-language sentence over a strip: the segment's
 *  dot in its colour, the other five segments as grey dots and all young people surveyed as a dark tick, on the
 *  driver's full scale. */
import type { DriverRow } from "@/lib/types";
import { fmtValue } from "@/lib/compare";
import { distinguishing } from "@/lib/distinct";
import { describe } from "@/lib/phrases";
import { SEGMENT_IDS, SEGMENT_PALETTES, segName } from "@/lib/theme";

export function DistinctList({ drivers, seg, compact = false }: { drivers: DriverRow[]; seg: string; compact?: boolean }) {
  const items = distinguishing(drivers, seg);
  const [dark, mid] = SEGMENT_PALETTES[seg];
  return (
    <div className={"dv-list" + (compact ? " compact" : "")}>
      {items.map((i) => {
        const [lo, hi] = i.axis;
        const pos = (x: number) => `${Math.min(100, Math.max(0, ((x - lo) / (hi - lo)) * 100))}%`;
        const ph = describe(i.label, i.isPct, i.value, i.all, i.rank);
        return (
          <div key={i.label} className="dv">
            <p className="dv-sentence"><b style={{ color: dark }}>{ph.lead}</b>{ph.rest}</p>
            <div className="dv-track" role="img"
              aria-label={`${segName(seg)} ${fmtValue(i.value, i.isPct)}; all young people surveyed ${fmtValue(i.all, i.isPct)}`}>
              {SEGMENT_IDS.filter((s) => s !== seg && i.vals[s] !== undefined).map((s) => (
                <span key={s} className="dv-other" style={{ left: pos(i.vals[s]) }} title={`${segName(s)}: ${fmtValue(i.vals[s], i.isPct)}`} />
              ))}
              {i.all !== undefined && <span className="dv-all" style={{ left: pos(i.all) }} title={`All surveyed: ${fmtValue(i.all, i.isPct)}`} />}
              <span className="dv-dot" style={{ left: pos(i.value), background: mid, borderColor: dark }}
                title={`${segName(seg)}: ${fmtValue(i.value, i.isPct)}`} />
            </div>
            {ph.note && <div className="dv-foot">{ph.note}</div>}
          </div>
        );
      })}
    </div>
  );
}

/** One-line versions for compact lists (front page). */
export function distinctSentences(drivers: DriverRow[], seg: string, n = 2) {
  return distinguishing(drivers, seg).slice(0, n).map((i) => ({ key: i.label, ...describe(i.label, i.isPct, i.value, i.all, i.rank) }));
}

export function DistinctLegend() {
  return (
    <p className="dv-legend">
      <span className="dv-key dot-seg" /> this segment <span className="dv-key dot-other" /> other segments{" "}
      <span className="dv-key tick-all" /> all young people surveyed
    </p>
  );
}
