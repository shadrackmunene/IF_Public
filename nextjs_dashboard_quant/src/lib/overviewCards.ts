/** Headline statistic cards for the Overview page (port of overview_cards.py): a tinted background per group and
 *  an icon per card. Kept short, with whole-number percentages; figures that need method context are left to the
 *  Deep dives tab. */
import { shareWords } from "./phrases";
import { SEGMENT_PALETTES, r0 } from "./theme";

/** words: the value is an interpreted share ("About two in five"), drawn smaller than a number. */
export interface Card { title: string; value: string; sub: string; icon: string; words?: boolean }
export interface CardGroup { title: string; palette: string[]; cards: Card[] }

export function cardGroups(o: Record<string, number>): CardGroup[] {
  // A share reads as words, with the exact percentage in brackets after the sentence (none for all / none).
  const share = (title: string, k: string, sub: string, icon: string): Card => {
    const v = o[k];
    const exact = v >= 99.5 || v <= 0.5 ? "" : ` (${r0(v)}%)`;
    return { title, value: shareWords(v, true), sub: sub + exact, icon, words: true };
  };
  return [
    { title: "Who they are", palette: SEGMENT_PALETTES["5"], cards: [
      { title: "Median age", value: `${r0(o.median_age)}`, sub: "years", icon: "🎂" },
      share("Women", "pct_female", "of the young people surveyed are women", "👩"),
      { title: "Median income", value: `KES ${r0(o.median_income / 1000)}K`, sub: "per month, own income", icon: "💰" },
    ] },
    { title: "Education & skills", palette: SEGMENT_PALETTES["3"], cards: [
      share("Secondary", "pct_secondary_highest", "have secondary school as their highest level", "🏫"),
      share("TVET", "pct_tvet", "have completed TVET or vocational training", "🛠️"),
      share("University", "pct_university", "have a university degree", "🎓"),
    ] },
    { title: "Work & money", palette: SEGMENT_PALETTES["2"], cards: [
      share("Informal work", "pct_informal_main", "of those working are in informal work", "🧰"),
      share("Side income", "pct_side_activity", "have a second income activity", "➕"),
      share("Saving", "pct_saving", "are saving money in any form", "🐖"),
    ] },
    { title: "Digital & AI", palette: SEGMENT_PALETTES["6"], cards: [
      share("Smartphone", "pct_smartphone", "own a smartphone", "📱"),
      share("AI tools", "pct_used_ai", "have used an AI tool", "🤖"),
    ] },
  ];
}
