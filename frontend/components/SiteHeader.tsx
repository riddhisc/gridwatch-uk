"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { setViewTab, type ViewTab } from "@/lib/view-tab";

function locationQuery(params: URLSearchParams) {
  const next = new URLSearchParams();
  const city = params.get("city");
  const area = params.get("area");
  const postcode = params.get("postcode");
  if (city) next.set("city", city);
  if (area) next.set("area", area);
  if (postcode) next.set("postcode", postcode);
  return next;
}

function NavLinks() {
  const path = usePathname();
  const params = useSearchParams();
  const [tab, setTab] = useState<ViewTab>(params.get("tab") === "charts" ? "charts" : "dashboard");

  useEffect(() => {
    setTab(params.get("tab") === "charts" ? "charts" : "dashboard");
    const handler = (event: Event) => setTab((event as CustomEvent<ViewTab>).detail);
    window.addEventListener("gph:tab", handler);
    return () => window.removeEventListener("gph:tab", handler);
  }, [params]);

  const loc = locationQuery(params);
  const dashHref = loc.toString() ? `/?${loc}` : "/";
  loc.set("tab", "charts");
  const chartsHref = `/?${loc}`;

  const onHelp = path === "/help";
  const onCharts = !onHelp && tab === "charts";
  const onDashboard = !onHelp && tab !== "charts";

  const linkClass = (active: boolean) =>
    `rounded-md px-3 py-2 text-sm font-medium ${
      active ? "bg-white text-black" : "text-zinc-300 hover:bg-white/10 hover:text-white"
    }`;

  return (
    <nav aria-label="Main" className="flex shrink-0 items-center gap-1">
      <Link
        href={dashHref}
        className={linkClass(onDashboard)}
        aria-current={onDashboard ? "page" : undefined}
        onClick={(event) => {
          if (onHelp) return;
          event.preventDefault();
          setViewTab("dashboard");
        }}
      >
        Dashboard
      </Link>
      <Link
        href={chartsHref}
        className={linkClass(onCharts)}
        aria-current={onCharts ? "page" : undefined}
        onClick={(event) => {
          if (onHelp) return;
          event.preventDefault();
          setViewTab("charts");
        }}
      >
        Charts
      </Link>
      <Link href="/help" className={linkClass(onHelp)} aria-current={onHelp ? "page" : undefined}>
        Help
      </Link>
    </nav>
  );
}

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 bg-black text-white">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-30 focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-black"
      >
        Skip to content
      </a>
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="min-w-0">
          <p className="text-[11px] uppercase tracking-[0.16em] text-zinc-400">UK electricity</p>
          <p className="text-base font-medium text-white">Green Power Hours</p>
        </Link>
        <Suspense fallback={<nav aria-label="Main" className="h-9 w-48" />}>
          <NavLinks />
        </Suspense>
      </div>
      <div className="h-1 bg-gradient-to-r from-blue-600 via-indigo-500 to-orange-400" />
    </header>
  );
}
