import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SUBURBS = [
    "Gosford",
    "Terrigal",
    "Woy Woy",
    "Umina Beach",
    "Wyong",
    "The Entrance",
    "Killarney Vale",
    "Bateau Bay",
    "Erina",
    "Avoca Beach",
]

PROPERTY_TYPES = ["house", "townhouse", "unit"]
FEATURES = ["pool", "solar", "view", "waterfront", "granny"]


def generate_rows(count: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start_date = datetime(2018, 1, 1)
    rows = []
    for idx in range(count):
        suburb = rng.choice(SUBURBS)
        property_type = rng.choice(PROPERTY_TYPES, p=[0.6, 0.2, 0.2])
        beds = int(rng.integers(1, 6))
        baths = int(rng.integers(1, 4))
        parking = int(rng.integers(0, 3))
        land_size = float(rng.normal(600, 150))
        internal_size = float(rng.normal(160, 40))
        base_price = 450_000 + beds * 120_000 + land_size * 400
        type_adjust = {"house": 1.1, "townhouse": 0.9, "unit": 0.75}[property_type]
        suburb_adjust = 1.0 + (SUBURBS.index(suburb) * 0.01)
        noise = rng.normal(0, 60_000)
        price = max(250_000, base_price * type_adjust * suburb_adjust + noise)
        sale_date = start_date + timedelta(days=int(rng.integers(0, 2200)))
        features = ",".join(rng.choice(FEATURES, size=rng.integers(0, 3), replace=False))

        rows.append(
            {
                "sale_id": f"SYN-{idx:05d}",
                "sale_date": sale_date.date().isoformat(),
                "price": round(price, 2),
                "address": f"{rng.integers(1, 200)} Example St",
                "suburb": suburb,
                "postcode": str(2000 + SUBURBS.index(suburb)),
                "property_type": property_type,
                "beds": beds,
                "baths": baths,
                "parking": parking,
                "land_size_sqm": round(land_size, 1),
                "internal_size_sqm": round(internal_size, 1),
                "lat": -33.4 + rng.normal(0, 0.2),
                "lon": 151.3 + rng.normal(0, 0.2),
                "condition": rng.choice(["As-is", "Typical", "Premium"]),
                "features": features,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic sales data")
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--out", default="./data/synthetic_sales.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate_rows(args.rows, args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
