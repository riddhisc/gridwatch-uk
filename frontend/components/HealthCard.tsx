import type { HealthResponse } from "@/lib/api";

function statusTone(value: string) {
  if (value === "ok") return "text-green-700";
  if (value === "skipped") return "text-slate-600";
  return "text-amber-700";
}

export function HealthCard({ health, error }: { health: HealthResponse; error?: string }) {
  return (
    <section className="card p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">API smoke test</h3>
          <p className="text-sm text-slate-600">GET /health from the FastAPI backend</p>
        </div>
        <span className={`text-sm font-semibold uppercase ${statusTone(health.status)}`}>
          {health.status}
        </span>
      </div>
      {error ? <p className="mt-4 text-sm text-red-700">{error}</p> : null}
      <dl className="mt-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 p-4">
          <dt className="text-sm font-medium text-slate-600">Service</dt>
          <dd className="mt-1 text-sm text-slate-900">{health.service}</dd>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <dt className="text-sm font-medium text-slate-600">Database</dt>
          <dd className={`mt-1 text-sm ${statusTone(health.checks.database)}`}>{health.checks.database}</dd>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <dt className="text-sm font-medium text-slate-600">Redis</dt>
          <dd className={`mt-1 text-sm ${statusTone(health.checks.redis)}`}>{health.checks.redis}</dd>
        </div>
      </dl>
      <p className="mt-4 text-xs text-slate-500">
        Version {health.version} · {health.timestamp}
      </p>
    </section>
  );
}
