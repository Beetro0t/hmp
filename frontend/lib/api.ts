const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type ValuationPayload = {
  address: string;
  suburb: string;
  lat?: number | null;
  lon?: number | null;
  beds: number;
  baths: number;
  parking: number;
  land_size_sqm: number;
  internal_size_sqm?: number | null;
  property_type: "house" | "townhouse" | "unit";
  condition_tier: "As-is" | "Typical" | "Premium";
  condition_checklist?: {
    renovated_kitchen: boolean;
    renovated_bathrooms: boolean;
    new_roof: boolean;
    needs_structural_repairs: boolean;
    landscaping_complete: boolean;
  };
  notable_features: string[];
};

export async function submitValuation(payload: ValuationPayload) {
  const res = await fetch(`${API_BASE}/value`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function triggerTraining(dataPath: string) {
  const res = await fetch(`${API_BASE}/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data_path: dataPath })
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}
