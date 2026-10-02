export type FuelShare = { fuel: string; perc: number };

export type CarbonPoint = {
  period_from: string;
  period_to: string;
  forecast: number | null;
  actual: number | null;
  index: string | null;
  generation_mix: FuelShare[];
};

export type PricePoint = {
  period_from: string;
  period_to: string;
  value_exc_vat: number;
  value_inc_vat: number;
  product_code: string;
  tariff_code: string;
  gsp_region: string;
};

export type CombinedPoint = {
  period_from: string;
  period_to: string;
  carbon: number | null;
  price_inc_vat: number | null;
  index: string | null;
};

export type PlaceAreaOption = { id: string; name: string; postcode: string; grid_region?: string | null };

export type PlaceOption = {
  id: string;
  name: string;
  postcode: string;
  areas?: PlaceAreaOption[];
};

export type OverviewResponse = {
  advice: { action: "charge_now" | "use_now" | "wait" | "ok"; headline: string; detail: string };
  location: {
    id: string;
    label: string;
    postcode: string | null;
    neso_region: string | null;
    neso_region_id: number | null;
    gsp_region: string | null;
    gsp_name: string | null;
    city_id?: string | null;
    area_id?: string | null;
    shared_with?: string[];
    grid_note?: string | null;
    scope: "national" | "regional";
  };
  current: {
    period_from: string;
    period_to: string;
    forecast: number | null;
    actual: number | null;
    index: string | null;
    region_code: string;
    region_name?: string | null;
  };
  generation: { mix: FuelShare[] };
  current_price: PricePoint | null;
  forecast: CarbonPoint[];
  history: CarbonPoint[];
  prices: PricePoint[];
  combined: CombinedPoint[];
  best_window: {
    period_from: string;
    period_to: string;
    carbon: number | null;
    price_inc_vat: number | null;
    reason: string;
  } | null;
  recommendations: { available: boolean; feature: string; message: string };
  as_of: string;
};

export async function fetchOverview(query?: {
  city?: string;
  area?: string;
  postcode?: string;
}): Promise<OverviewResponse> {
  const base =
    process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const params = new URLSearchParams();
  if (query?.city) params.set("city", query.city);
  if (query?.area) params.set("area", query.area);
  if (query?.postcode) params.set("postcode", query.postcode);
  const suffix = params.toString() ? `?${params}` : "";
  const response = await fetch(`${base.replace(/\/$/, "")}/v1/overview${suffix}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Dashboard data failed with status ${response.status}`);
  }
  return response.json() as Promise<OverviewResponse>;
}

export type MlForecast = {
  available: boolean;
  reason?: string | null;
  message?: string | null;
  prediction?: number | null;
  predicted_for?: string | null;
  model_version?: string | null;
  mae?: number | null;
  naive_mae?: number | null;
  history_days?: number | null;
  limited_history?: boolean;
};

export async function fetchMlForecast(): Promise<MlForecast> {
  const base =
    process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const response = await fetch(`${base.replace(/\/$/, "")}/v1/forecast/ml`, { cache: "no-store" });
    if (!response.ok) {
      return { available: false, reason: "http_error", message: `Forecast failed (${response.status})` };
    }
    return (await response.json()) as MlForecast;
  } catch {
    return { available: false, reason: "network_error", message: "Could not reach the ML forecast endpoint." };
  }
}

export async function fetchPlaces(): Promise<PlaceOption[]> {
  const base =
    process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${base.replace(/\/$/, "")}/v1/locations`, { cache: "no-store" });
  if (!response.ok) {
    return [{ id: "gb", name: "Great Britain (national)", postcode: "" }];
  }
  return response.json() as Promise<PlaceOption[]>;
}

export function formatLondon(iso: string, withDate = false): string {
  return new Date(iso).toLocaleString("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
    ...(withDate ? { day: "numeric", month: "short" } : {}),
  });
}

export function formatPrice(pence: number | null | undefined): string {
  if (pence === null || pence === undefined) return "—";
  const value = pence.toFixed(1);
  if (pence < 0) return `${value}p/kWh (paid to use)`;
  return `${value}p/kWh`;
}

export function carbonLabel(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return `${value} gCO₂/kWh`;
}
