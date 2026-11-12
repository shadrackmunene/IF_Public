"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "OVERVIEW" },
  { href: "/profiles/", label: "SEGMENT PROFILES" },
  { href: "/deep-dives/", label: "DEEP DIVES" },
  { href: "/self-assessment/", label: "SELF ASSESSMENT" },
];

export default function TopBar() {
  const path = (usePathname() || "/").replace(/\/?$/, "/");
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link href="/" className="brand">YOUTH LIVELIHOODS</Link>
        <nav className="topnav">
          {TABS.map((t) => (
            <Link key={t.href} href={t.href} prefetch={false} className={path === t.href ? "active" : ""}>{t.label}</Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
