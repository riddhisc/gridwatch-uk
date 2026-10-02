"use client";

export type ViewTab = "dashboard" | "charts";

const EVENT = "gph:tab";

export function setViewTab(next: ViewTab) {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.pathname = "/";
  if (next === "charts") url.searchParams.set("tab", "charts");
  else url.searchParams.delete("tab");
  window.history.replaceState(null, "", `${url.pathname}${url.search}`);
  window.dispatchEvent(new CustomEvent<ViewTab>(EVENT, { detail: next }));
}

export function subscribeViewTab(listener: (tab: ViewTab) => void) {
  const handler = (event: Event) => listener((event as CustomEvent<ViewTab>).detail);
  window.addEventListener(EVENT, handler);
  return () => window.removeEventListener(EVENT, handler);
}
