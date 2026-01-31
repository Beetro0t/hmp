"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { submitValuation, type ValuationPayload } from "../lib/api";

const defaultPayload: ValuationPayload = {
  address: "",
  suburb: "",
  lat: null,
  lon: null,
  beds: 3,
  baths: 2,
  parking: 1,
  land_size_sqm: 550,
  internal_size_sqm: 160,
  property_type: "house",
  condition_tier: "Typical",
  condition_checklist: {
    renovated_kitchen: false,
    renovated_bathrooms: false,
    new_roof: false,
    needs_structural_repairs: false,
    landscaping_complete: false
  },
  notable_features: []
};

export default function WizardPage() {
  const [form, setForm] = useState<ValuationPayload>(defaultPayload);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const updateField = (field: keyof ValuationPayload, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateChecklist = (field: keyof NonNullable<ValuationPayload["condition_checklist"]>) => {
    setForm((prev) => ({
      ...prev,
      condition_checklist: {
        ...prev.condition_checklist,
        [field]: !prev.condition_checklist?.[field]
      }
    }));
  };

  const toggleFeature = (feature: string) => {
    setForm((prev) => {
      const existing = prev.notable_features.includes(feature);
      return {
        ...prev,
        notable_features: existing
          ? prev.notable_features.filter((item) => item !== feature)
          : [...prev.notable_features, feature]
      };
    });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await submitValuation(form);
      sessionStorage.setItem("valuationResult", JSON.stringify(result));
      sessionStorage.setItem("valuationInput", JSON.stringify(form));
      router.push("/results");
    } catch (err: any) {
      setError(err.message ?? "Unable to value property.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-800">Valuation wizard</h2>
        <p className="mt-2 text-sm text-slate-600">
          Enter property details for Central Coast, NSW. The model returns tiered
          price ranges with uncertainty.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm">
              Address
              <input
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.address}
                onChange={(event) => updateField("address", event.target.value)}
                required
              />
            </label>
            <label className="text-sm">
              Suburb
              <input
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.suburb}
                onChange={(event) => updateField("suburb", event.target.value)}
                required
              />
            </label>
            <label className="text-sm">
              Latitude (optional)
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.lat ?? ""}
                onChange={(event) => {
                  const value = event.target.value;
                  updateField("lat", value === "" ? null : Number(value));
                }}
              />
            </label>
            <label className="text-sm">
              Longitude (optional)
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.lon ?? ""}
                onChange={(event) => {
                  const value = event.target.value;
                  updateField("lon", value === "" ? null : Number(value));
                }}
              />
            </label>
            <label className="text-sm">
              Property type
              <select
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.property_type}
                onChange={(event) => updateField("property_type", event.target.value)}
              >
                <option value="house">House</option>
                <option value="townhouse">Townhouse</option>
                <option value="unit">Unit</option>
              </select>
            </label>
            <label className="text-sm">
              Condition tier
              <select
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.condition_tier}
                onChange={(event) =>
                  updateField("condition_tier", event.target.value)
                }
              >
                <option value="As-is">As-is</option>
                <option value="Typical">Typical</option>
                <option value="Premium">Premium</option>
              </select>
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="text-sm">
              Beds
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.beds}
                onChange={(event) => updateField("beds", Number(event.target.value))}
              />
            </label>
            <label className="text-sm">
              Baths
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.baths}
                onChange={(event) => updateField("baths", Number(event.target.value))}
              />
            </label>
            <label className="text-sm">
              Parking
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.parking}
                onChange={(event) => updateField("parking", Number(event.target.value))}
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm">
              Land size (sqm)
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.land_size_sqm}
                onChange={(event) =>
                  updateField("land_size_sqm", Number(event.target.value))
                }
              />
            </label>
            <label className="text-sm">
              Internal size (sqm)
              <input
                type="number"
                className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={form.internal_size_sqm ?? ""}
                onChange={(event) => {
                  const value = event.target.value;
                  updateField(
                    "internal_size_sqm",
                    value === "" ? null : Number(value)
                  );
                }}
              />
            </label>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-700">Condition checklist</p>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              {[
                { id: "renovated_kitchen", label: "Renovated kitchen" },
                { id: "renovated_bathrooms", label: "Renovated bathrooms" },
                { id: "new_roof", label: "New roof" },
                { id: "needs_structural_repairs", label: "Needs structural repairs" },
                { id: "landscaping_complete", label: "Landscaping complete" }
              ].map((item) => (
                <label key={item.id} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={
                      form.condition_checklist?.[
                        item.id as keyof NonNullable<ValuationPayload["condition_checklist"]>
                      ]
                    }
                    onChange={() =>
                      updateChecklist(
                        item.id as keyof NonNullable<
                          ValuationPayload["condition_checklist"]
                        >
                      )
                    }
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-semibold text-slate-700">Notable features</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {[
                "pool",
                "solar",
                "view",
                "waterfront",
                "granny flat"
              ].map((feature) => (
                <button
                  key={feature}
                  type="button"
                  onClick={() => toggleFeature(feature)}
                  className={`rounded-full border px-3 py-1 text-sm capitalize transition ${
                    form.notable_features.includes(feature)
                      ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                      : "border-slate-200 text-slate-600"
                  }`}
                >
                  {feature}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {loading ? "Valuing..." : "Get valuation"}
          </button>
        </form>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-sm">
        <h3 className="text-base font-semibold text-slate-700">
          Guardrails & data sources
        </h3>
        <ul className="mt-3 list-disc space-y-1 pl-5">
          <li>Not financial advice. Results are uncertain and data-dependent.</li>
          <li>
            Data sources: NSW Valuer General Property Sales Data Files + optional
            Domain APIs.
          </li>
          <li>Intervals represent 50% and 80% prediction ranges.</li>
        </ul>
      </section>
    </div>
  );
}
