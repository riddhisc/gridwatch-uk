"use client";

import { useEffect, useState } from "react";
import type { MlForecast } from "@/lib/overview";
import { formatLondon } from "@/lib/overview";

export function MlGuess({ initial }: { initial?: MlForecast }) {
  const [ml, setMl] = useState<MlForecast | undefined>(initial);

  useEffect(() => {
    if (initial?.available) return;
    let cancelled = false;
    fetch("/backend/v1/forecast/ml", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: MlForecast | null) => {
        if (!cancelled && payload) setMl(payload);
      })
      .catch(() => {
        if (!cancelled) setMl({ available: false, message: "Could not reach the guess endpoint." });
      });
    return () => {
      cancelled = true;
    };
  }, [initial]);

  if (!ml) {
    return <p className="mt-3 text-sm text-slate-500">Loading our 1-hour guess…</p>;
  }

  if (ml.available && ml.prediction != null) {
    return (
      <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
        <span className="font-medium text-amber-800">Our guess only · not official.</span> About{" "}
        <strong>{ml.prediction} gCO₂/kWh</strong>
        {ml.predicted_for ? ` around ${formatLondon(ml.predicted_for)}` : ""}. That figure is our model on
        saved snapshots. Carbon, price, and the best window are live NESO and Octopus data
        {ml.limited_history ? " — this guess still has a short history." : "."}
      </p>
    );
  }

  return (
    <p className="mt-3 text-sm text-slate-500">
      Carbon and price on this page are live NESO and Octopus data. Our own 1-hour guess is not showing
      yet{ml.message ? `: ${ml.message}` : "."}
    </p>
  );
}
