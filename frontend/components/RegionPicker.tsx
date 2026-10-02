"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import type { PlaceOption } from "@/lib/overview";

export function RegionPicker({
  places,
  selectedId,
  selectedAreaId,
  compactLabel,
}: {
  places: PlaceOption[];
  selectedId: string;
  selectedAreaId?: string | null;
  compactLabel: string;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const [pending, startTransition] = useTransition();
  const [open, setOpen] = useState(false);
  const city = places.find((place) => place.id === selectedId) ?? places[0];
  const areas = city?.areas ?? [];
  const areaGroups = new Map<string, typeof areas>();
  for (const area of areas) {
    const group = area.grid_region || "Other grid";
    const bucket = areaGroups.get(group) ?? [];
    bucket.push(area);
    areaGroups.set(group, bucket);
  }

  const title = compactLabel.replace(/, right now$/i, "").trim() || city?.name || "Great Britain";

  function push(next: URLSearchParams) {
    const query = next.toString();
    startTransition(() => router.push(query ? `/?${query}` : "/"));
  }

  function goCity(nextCity: string) {
    const next = new URLSearchParams(params.toString());
    next.delete("postcode");
    next.delete("area");
    if (!nextCity || nextCity === "gb") {
      next.delete("city");
    } else {
      next.set("city", nextCity);
    }
    push(next);
    setOpen(false);
  }

  function goArea(nextArea: string) {
    const next = new URLSearchParams(params.toString());
    next.delete("postcode");
    if (!nextArea) {
      next.delete("area");
    } else {
      next.set("area", nextArea);
      if (selectedId && selectedId !== "gb") next.set("city", selectedId);
    }
    push(next);
    setOpen(false);
  }

  function submitPostcode(formData: FormData) {
    const postcode = String(formData.get("postcode") || "").trim();
    const next = new URLSearchParams(params.toString());
    next.delete("city");
    next.delete("area");
    if (postcode) next.set("postcode", postcode);
    else next.delete("postcode");
    push(next);
    setOpen(false);
  }

  return (
    <div className="w-full min-w-0">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-3 rounded-2xl border border-indigo-200 bg-indigo-50 px-3 py-3 text-left shadow-sm hover:border-indigo-300 hover:bg-indigo-100 sm:px-4"
        aria-expanded={open}
      >
        <span className="flex min-w-0 items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-white">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
              <path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11z" />
              <circle cx="12" cy="10" r="2.5" />
            </svg>
          </span>
          <span className="min-w-0">
            <span className="block truncate font-semibold text-slate-900">{title}</span>
            <span className="block text-xs text-slate-500">Live reading · city or postcode</span>
          </span>
        </span>
        <span className="shrink-0 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm">
          {open ? "Close" : "Change"}
        </span>
      </button>

      {open ? (
        <section className="mt-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5" aria-labelledby="location-heading">
          <div className="mb-3">
            <h2 id="location-heading" className="text-base font-semibold text-slate-900">
              Where to read the grid
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Great Britain is the default. Pick a city for a regional carbon and Agile price.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block min-w-0">
              <span className="text-sm font-medium text-slate-800">City</span>
              <select className="field" value={selectedId} disabled={pending} onChange={(event) => goCity(event.target.value)}>
                {places.map((place) => (
                  <option key={place.id} value={place.id}>
                    {place.name}
                  </option>
                ))}
              </select>
            </label>
            {areas.length > 0 ? (
              <label className="block min-w-0">
                <span className="text-sm font-medium text-slate-800">Area</span>
                <select
                  className="field"
                  value={selectedAreaId ?? ""}
                  disabled={pending}
                  onChange={(event) => goArea(event.target.value)}
                >
                  <option value="">City-wide / centre</option>
                  {Array.from(areaGroups.entries()).map(([group, groupAreas]) => (
                    <optgroup key={group} label={`${group} grid`}>
                      {groupAreas.map((area) => (
                        <option key={area.id} value={area.id}>
                          {area.name} ({area.postcode})
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </label>
            ) : null}
            <form action={submitPostcode} className="flex min-w-0 items-end gap-2 sm:col-span-2">
              <label className="block min-w-0 flex-1">
                <span className="text-sm font-medium text-slate-800">Postcode</span>
                <input
                  name="postcode"
                  autoComplete="postal-code"
                  placeholder="e.g. CR0"
                  defaultValue={params.get("postcode") ?? ""}
                  className="field"
                />
              </label>
              <button type="submit" className="btn-primary mb-px shrink-0" disabled={pending}>
                Look up
              </button>
            </form>
          </div>
          {pending ? (
            <p className="mt-3 text-sm text-blue-800" role="status">
              Updating live grid data…
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
