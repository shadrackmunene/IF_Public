/** Overview statistic cards (port of overview_cards.py): a tinted background per group and an icon per card. */
import { SEGMENT_PALETTES } from "./theme";

export interface Card { title: string; value: string; sub: string; icon: string }
export interface CardGroup { title: string; palette: string[]; cards: Card[] }

export function cardGroups(o: Record<string, number>): CardGroup[] {
  const kes = (n: number) => `KES ${Math.round(n).toLocaleString("en-US")}`;
  return [
    { title: "Youth & household profile", palette: SEGMENT_PALETTES["2"], cards: [
      { title: "Median age", value: `${Math.round(o.median_age)}`, sub: "years (16-30 range)", icon: "🎂" },
      { title: "Female", value: `${o.pct_female}%`, sub: `Male: ${(100 - o.pct_female).toFixed(1)}%`, icon: "👩" },
      { title: "Independent household", value: `${o.pct_own_household}%`, sub: "live in own/rented household", icon: "🏠" },
    ] },
    { title: "Education & skills pathway", palette: SEGMENT_PALETTES["5"], cards: [
      { title: "Not currently enrolled", value: `${o.pct_not_enrolled}%`, sub: "in any education/training", icon: "📚" },
      { title: "Secondary (highest)", value: `${o.pct_secondary_highest}%`, sub: "completed KCSE as highest level", icon: "🏫" },
      { title: "TVET/vocational", value: `${o.pct_tvet}%`, sub: "completed TVET training", icon: "🛠️" },
      { title: "University", value: `${o.pct_university}%`, sub: "completed a university degree", icon: "🎓" },
    ] },
    { title: "Current livelihoods", palette: SEGMENT_PALETTES["3"], cards: [
      { title: "Informal work", value: `${o.pct_informal_main}%`, sub: "of those currently working", icon: "🧰" },
      { title: "Side activity", value: `${o.pct_side_activity}%`, sub: "have a supplementary income activity", icon: "➕" },
      { title: "Self-employed", value: `${o.pct_self_employed}%`, sub: "main activity is running a business", icon: "🏪" },
    ] },
    { title: "Income & financial security", palette: SEGMENT_PALETTES["4"], cards: [
      { title: "Median income", value: kes(o.median_income), sub: "per month, personal income", icon: "💰" },
      { title: "Currently saving", value: `${o.pct_saving}%`, sub: "saving money in any form", icon: "🐖" },
      { title: "Bank account", value: `${o.pct_bank_account}%`, sub: "have a personal bank/financial account", icon: "🏦" },
    ] },
    { title: "Digital economy & AI", palette: SEGMENT_PALETTES["6"], cards: [
      { title: "Smartphone", value: `${o.pct_smartphone}%`, sub: "own a smartphone", icon: "📱" },
      { title: "Internet daily", value: `${o.pct_internet_daily}%`, sub: "access the internet daily", icon: "🌐" },
      { title: "Mobile money daily", value: `${o.pct_mobile_money_daily}%`, sub: "use mobile money daily", icon: "💸" },
      { title: "Used an AI tool", value: `${o.pct_used_ai}%`, sub: "have ever used an AI tool", icon: "🤖" },
    ] },
  ];
}
