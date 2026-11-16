/** Headline statistic cards for the Overview page (port of overview_cards.py): a tinted background per group and
 *  an icon per card. Kept short, with whole-number percentages; figures that need method context are left to the
 *  Deep dives tab. */
import { SEGMENT_PALETTES, r0 } from "./theme";

export interface Card { title: string; value: string; sub: string; icon: string }
export interface CardGroup { title: string; palette: string[]; cards: Card[] }

export function cardGroups(o: Record<string, number>): CardGroup[] {
  const pct = (k: string) => `${r0(o[k])}%`;
  return [
    { title: "Who they are", palette: SEGMENT_PALETTES["5"], cards: [
      { title: "Median age", value: `${r0(o.median_age)}`, sub: "years", icon: "🎂" },
      { title: "Women", value: pct("pct_female"), sub: "of young people surveyed", icon: "👩" },
      { title: "Median income", value: `KES ${r0(o.median_income / 1000)}K`, sub: "per month, own income", icon: "💰" },
    ] },
    { title: "Education & skills", palette: SEGMENT_PALETTES["3"], cards: [
      { title: "Secondary", value: pct("pct_secondary_highest"), sub: "secondary school is their highest level", icon: "🏫" },
      { title: "TVET", value: pct("pct_tvet"), sub: "completed TVET or vocational training", icon: "🛠️" },
      { title: "University", value: pct("pct_university"), sub: "completed a university degree", icon: "🎓" },
    ] },
    { title: "Work & money", palette: SEGMENT_PALETTES["2"], cards: [
      { title: "Informal work", value: pct("pct_informal_main"), sub: "of those working are in informal work", icon: "🧰" },
      { title: "Side income", value: pct("pct_side_activity"), sub: "have a second income activity", icon: "➕" },
      { title: "Saving", value: pct("pct_saving"), sub: "are saving money in any form", icon: "🐖" },
    ] },
    { title: "Digital & AI", palette: SEGMENT_PALETTES["6"], cards: [
      { title: "Smartphone", value: pct("pct_smartphone"), sub: "own a smartphone", icon: "📱" },
      { title: "AI tools", value: pct("pct_used_ai"), sub: "have used an AI tool", icon: "🤖" },
    ] },
  ];
}
