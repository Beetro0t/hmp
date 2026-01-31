type TierCardProps = {
  tier: string;
  pointEstimate: number;
  interval50: number[];
  interval80: number[];
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
    maximumFractionDigits: 0
  }).format(value);

export function TierCard({
  tier,
  pointEstimate,
  interval50,
  interval80
}: TierCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-800">{tier}</h3>
      <p className="mt-2 text-2xl font-semibold text-emerald-600">
        {formatCurrency(pointEstimate)}
      </p>
      <div className="mt-4 space-y-2 text-sm text-slate-600">
        <div>
          <span className="font-medium text-slate-700">50% range:</span>{" "}
          {formatCurrency(interval50[0])} - {formatCurrency(interval50[1])}
        </div>
        <div>
          <span className="font-medium text-slate-700">80% range:</span>{" "}
          {formatCurrency(interval80[0])} - {formatCurrency(interval80[1])}
        </div>
      </div>
    </div>
  );
}
