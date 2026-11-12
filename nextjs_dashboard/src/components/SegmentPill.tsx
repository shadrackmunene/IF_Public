import { SEGMENT_PILL_COLORS, segName } from "@/lib/theme";

export default function SegmentPill({ seg }: { seg: string }) {
  return <span className="segment-pill" style={{ backgroundColor: SEGMENT_PILL_COLORS[seg] }}>{segName(seg)}</span>;
}
