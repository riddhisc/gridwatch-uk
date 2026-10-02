export type HealthCheck = {
  database: "ok" | "error" | "skipped";
  redis: "ok" | "error" | "skipped";
  carbon_intensity?: "ok" | "error" | "skipped";
};

export type HealthResponse = {
  status: "ok" | "degraded";
  service: string;
  version: string;
  checks: HealthCheck;
  timestamp: string;
};

export async function fetchBackendHealth(): Promise<HealthResponse> {
  const base =
    process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${base.replace(/\/$/, "")}/health`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json() as Promise<HealthResponse>;
}
