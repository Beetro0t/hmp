"use client";

import { useEffect, useState } from "react";

import { fetchMetrics } from "../../lib/api";

type Metrics = Record<string, number>;

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics()
      .then((data) => setMetrics(data.metrics))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        {error}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600">
        Loading metrics...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-xl font-semibold text-slate-800">Model metrics</h2>
        <p className="mt-2 text-sm text-slate-600">
          Walk-forward time split evaluation for Central Coast sales.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key} className="rounded-lg border border-slate-200 p-4">
              <p className="text-sm font-semibold text-slate-700">{key}</p>
              <p className="mt-2 text-lg text-emerald-600">
                {Number.isFinite(value) ? value.toFixed(3) : value}
              </p>
            </div>
          ))}
        </div>
      </section>
      <section className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
        <p className="font-semibold text-slate-700">Evaluation notes</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>MAE and MAPE use the latest 20% of sales as a holdout.</li>
          <li>Coverage metrics report the share of sales within intervals.</li>
          <li>All metrics are scoped to Central Coast, NSW.</li>
        </ul>
      </section>
    </div>
  );
}
