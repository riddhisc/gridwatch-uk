"use client";

import { Suspense, useMemo } from "react";
import {
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { RegionPicker } from "@/components/RegionPicker";
import type { CombinedPoint, FuelShare, OverviewResponse, PlaceOption } from "@/lib/overview";
import { formatLondon, formatPrice } from "@/lib/overview";

const FUEL_COLORS: Record<string, string> = {
  wind: "#15803d",
  solar: "#ca8a04",
  nuclear: "#7c3aed",
  hydro: "#1d4ed8",
  gas: "#2563eb",
  coal: "#57534e",
  biomass: "#65a30d",
  imports: "#64748b",
  other: "#94a3b8",
};

const AXIS = { fill: "#475569", fontSize: 12 };
const GRID = "#e2e8f0";
const TOOLTIP = {
  background: "#ffffff",
  border: "1px solid #cbd5e1",
  color: "#0f172a",
  borderRadius: 8,
};

export function MixDonut({ mix }: { mix: FuelShare[] }) {
  const data = mix
    .filter((item) => item.perc > 0)
    .sort((a, b) => b.perc - a.perc)
    .map((item) => ({ ...item, fill: FUEL_COLORS[item.fuel] || "#64748b" }));
  const total = data.reduce((sum, item) => sum + item.perc, 0) || 1;

  return (
    <div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="perc" nameKey="fuel" innerRadius={58} outerRadius={88} paddingAngle={1}>
              {data.map((item) => (
                <Cell key={item.fuel} fill={item.fill} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={TOOLTIP}
              formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, name]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="mt-2 flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm text-slate-600">
        {data.slice(0, 5).map((item) => (
          <li key={item.fuel} className="flex items-center gap-1.5 capitalize">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: item.fill }} />
            {item.fuel} {Math.round((item.perc / total) * 100)}%
          </li>
        ))}
      </ul>
    </div>
  );
}

export function CombinedChart({ points }: { points: CombinedPoint[] }) {
  const data = points.map((point) => ({
    time: formatLondon(point.period_from, true),
    carbon: point.carbon,
    price: point.price_inc_vat,
  }));
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 12, right: 12, left: 4, bottom: 8 }}>
          <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
          <XAxis dataKey="time" tick={{ ...AXIS, fontSize: 11 }} minTickGap={28} />
          <YAxis yAxisId="carbon" tick={AXIS} unit=" g" width={48} />
          <YAxis yAxisId="price" orientation="right" tick={AXIS} unit="p" width={40} />
          <Tooltip contentStyle={TOOLTIP} />
          <Legend />
          <Line
            yAxisId="carbon"
            type="monotone"
            dataKey="carbon"
            name="Carbon intensity"
            stroke="#1d4ed8"
            dot={false}
            strokeWidth={2}
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="price"
            name="Price"
            stroke="#ea580c"
            strokeDasharray="6 4"
            dot={false}
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ChartsView({ data, places }: { data: OverviewResponse; places?: PlaceOption[] }) {
  const nextDay = useMemo(() => {
    const start = new Date(data.as_of).getTime();
    const horizon = start + 24 * 60 * 60 * 1000;
    return data.combined.filter((point) => {
      const t = new Date(point.period_from).getTime();
      return t >= start && t <= horizon;
    });
  }, [data.as_of, data.combined]);

  const placeName = data.location.scope === "regional" ? data.location.label : "Great Britain";
  const region = data.location.neso_region;
  const selectedId =
    data.location.city_id && places?.some((place) => place.id === data.location.city_id)
      ? data.location.city_id
      : places?.some((place) => place.id === data.location.id)
        ? data.location.id
        : "gb";

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {places ? (
        <Suspense fallback={null}>
          <RegionPicker
            places={places}
            selectedId={selectedId}
            selectedAreaId={data.location.area_id}
            compactLabel={placeName}
          />
        </Suspense>
      ) : null}
      <section className="card overflow-hidden p-5 sm:p-6">
        <h3 className="text-lg font-semibold text-slate-900">What’s making GB power</h3>
        <p className="mb-2 text-sm text-slate-600">
          This donut is the national generation mix. It is the same for Manchester, Bristol, or any other
          city — NESO does not publish a city-level mix.
        </p>
        <MixDonut mix={data.generation.mix} />
      </section>
      <section className="card overflow-hidden p-5 sm:p-6">
        <h3 className="text-lg font-semibold text-slate-900">Carbon and price for {placeName}</h3>
        <p className="mb-2 text-sm text-slate-600">
          These lines follow your selected location’s grid region
          {region ? ` (${region})` : ""}, not a single street.
          {data.best_window
            ? ` Best window shown: ${formatLondon(data.best_window.period_from, true)}.`
            : ""}
        </p>
        <div className="min-h-80 w-full min-w-0">
          <CombinedChart points={nextDay.length ? nextDay : data.combined} />
        </div>
      </section>
      {data.location.grid_note ? <p className="text-sm text-slate-600">{data.location.grid_note}</p> : null}
      <p className="text-xs text-slate-500">
        Price {formatPrice(data.current_price?.value_inc_vat)} · Updated {formatLondon(data.as_of, true)}
      </p>
    </div>
  );
}
