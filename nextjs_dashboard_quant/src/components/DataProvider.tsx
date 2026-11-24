"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Dashboard } from "@/lib/types";
import { dataUrl } from "@/lib/data";

const Ctx = createContext<Dashboard | null>(null);

/** Loads the aggregate data bundle once (about 365 KB, ~60 KB gzipped) and shares it with every page. */
export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch(dataUrl("dashboard.json"))
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);
  if (error) return <div className="page"><p>Could not load the dashboard data ({error}).</p></div>;
  if (!data) return <div className="page"><p className="text-muted">Loading…</p></div>;
  return <Ctx.Provider value={data}>{children}</Ctx.Provider>;
}

export function useDashboard(): Dashboard {
  const d = useContext(Ctx);
  if (!d) throw new Error("useDashboard must be used inside <DataProvider>");
  return d;
}
