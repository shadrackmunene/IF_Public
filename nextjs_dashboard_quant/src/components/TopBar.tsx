"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "OVERVIEW" },
  { href: "/segments/", label: "SEGMENTS" },
  { href: "/compare/", label: "COMPARE" },
  { href: "/counties/", label: "COUNTIES" },
  { href: "/deep-dives/", label: "DEEP DIVES" },
  { href: "/self-assessment/", label: "SELF ASSESSMENT" },
  { href: "/methodology/", label: "METHODOLOGY" },
];

export default function TopBar() {
  const path = (usePathname() || "/").replace(/\/?$/, "/");
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link href="/" className="brand">YOUTH LIVELIHOODS · DATA</Link>
        <nav className="topnav">
          {TABS.map((t) => (
            <Link key={t.href} href={t.href} prefetch={false} className={path === t.href ? "active" : ""}>{t.label}</Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
