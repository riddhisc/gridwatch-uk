import { Suspense } from "react";
import { MlGuess } from "@/components/MlGuess";
import { RegionPicker } from "@/components/RegionPicker";
import type { OverviewResponse, PlaceOption } from "@/lib/overview";
import { carbonLabel, formatLondon, formatPrice } from "@/lib/overview";

function isGood(action: OverviewResponse["advice"]["action"]) {
  return action === "charge_now" || action === "use_now";
}

function verdictTitle(action: OverviewResponse["advice"]["action"]) {
  if (action === "wait") return "Wait if you can";
  if (action === "ok") return "Fine to use";
  return "Good time";
}

export function Dashboard({
  data,
  places,
}: {
  data: OverviewResponse;
  places: PlaceOption[];
}) {
  const intensity = data.current.actual ?? data.current.forecast;
  const good = isGood(data.advice.action);
  const where = data.location.scope === "regional" ? data.location.label : "Great Britain";
  const price = data.current_price?.value_inc_vat;
  const paid = price !== null && price !== undefined && price < 0;
  const wait = data.advice.action === "wait";
  const badge = good
    ? "bg-blue-600 text-white"
    : wait
      ? "bg-orange-500 text-white"
      : "bg-indigo-600 text-white";
  const selectedId =
    data.location.city_id && places.some((place) => place.id === data.location.city_id)
      ? data.location.city_id
      : places.some((place) => place.id === data.location.id)
        ? data.location.id
        : "gb";

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg shadow-indigo-900/10">
        <div className={`h-1.5 ${good ? "bg-blue-500" : wait ? "bg-orange-400" : "bg-indigo-500"}`} />
        <div className="p-5 sm:p-8">
          <Suspense fallback={null}>
            <RegionPicker places={places} selectedId={selectedId} selectedAreaId={data.location.area_id} compactLabel={where} />
          </Suspense>
          <div className="mt-6 flex flex-wrap items-center gap-2">
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
              {verdictTitle(data.advice.action)}
            </h2>
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge}`}>
              {good ? "low carbon" : data.advice.action === "wait" ? "wait" : "average"}
            </span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-indigo-100 bg-indigo-50 px-3 py-3">
              <p className="text-xs font-medium uppercase tracking-wide text-indigo-700">Carbon now</p>
              <p className="mt-1 text-lg font-semibold text-indigo-950">{carbonLabel(intensity)}</p>
            </div>
            <div className="rounded-xl border border-orange-100 bg-orange-50 px-3 py-3">
              <p className="text-xs font-medium uppercase tracking-wide text-orange-700">Price now</p>
              <p className="mt-1 text-lg font-semibold text-orange-950">
                {price !== null && price !== undefined ? formatPrice(price) : "—"}
              </p>
            </div>
          </div>
          <MlGuess />

          {data.best_window ? (
            <div className="mt-6 rounded-xl border border-indigo-200 bg-indigo-50 p-4">
              <p className="text-sm font-medium text-indigo-800">Best window in next 24h</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">
                {formatLondon(data.best_window.period_from)}–{formatLondon(data.best_window.period_to)}{" "}
                <span className="font-medium text-indigo-600">
                  {new Date(data.best_window.period_from).toDateString() === new Date().toDateString()
                    ? "today"
                    : "tomorrow"}
                </span>
              </p>
              <p className="mt-1 text-sm text-slate-600">
                {data.best_window.carbon !== null ? `${carbonLabel(data.best_window.carbon)}` : ""}
                {data.best_window.price_inc_vat !== null && data.best_window.price_inc_vat < 0
                  ? " · you get paid to use power"
                  : paid
                    ? " · you get paid to use power later too"
                    : data.best_window.price_inc_vat !== null
                      ? ` · ${formatPrice(data.best_window.price_inc_vat)}`
                      : ""}
              </p>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
