"use client";

import { useEffect, useState } from "react";

import { TierCard } from "../../components/TierCard";

type Tier = {
  tier: string;
  point_estimate: number;
  interval_50: number[];
  interval_80: number[];
};

type Explanation = {
  top_drivers: string[];
  comparable_sales: Array<Record<string, any>>;
  sensitivity: string[];
  confidence_notes: string[];
};

type ValuationResult = {
  tiers: Tier[];
  explanation: Explanation;
  disclaimer: string;
  data_sources: string[];
};

export default function ResultsPage() {
  const [result, setResult] = useState<ValuationResult | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("valuationResult");
    if (stored) {
      setResult(JSON.parse(stored));
    }
  }, []);

  if (!result) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Run a valuation first to see results.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-semibold text-slate-800">Valuation results</h2>
        <p className="mt-2 text-sm text-slate-600">
          Tiered valuation spectrum for Central Coast, NSW.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {result.tiers.map((tier) => (
            <TierCard
              key={tier.tier}
              tier={tier.tier}
              pointEstimate={tier.point_estimate}
              interval50={tier.interval_50}
              interval80={tier.interval_80}
            />
          ))}
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-700">Top drivers</h3>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">
            {result.explanation.top_drivers.map((driver) => (
              <li key={driver}>{driver}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="text-base font-semibold text-slate-700">
            What moves the estimate most
          </h3>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">
            {result.explanation.sensitivity.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-base font-semibold text-slate-700">Comparable sales</h3>
        {result.explanation.comparable_sales.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">
            No comparable sales available yet. Train with more sales data for
            richer comps.
          </p>
        ) : (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {result.explanation.comparable_sales.map((comp: any) => (
              <div
                key={comp.sale_id}
                className="rounded-lg border border-slate-200 p-3 text-sm"
              >
                <p className="font-semibold text-slate-700">{comp.address}</p>
                <p className="text-slate-500">
                  {comp.suburb} • {comp.sale_date}
                </p>
                <p className="mt-1 text-emerald-600">
                  ${comp.price.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
        <p className="font-semibold text-slate-700">Confidence notes</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          {result.explanation.confidence_notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
        <div className="mt-4 space-y-2 text-xs text-slate-500">
          <p>{result.disclaimer}</p>
          <p>Data sources: {result.data_sources.join(\" • \")}</p>
        </div>
      </section>
    </div>
  );
}
