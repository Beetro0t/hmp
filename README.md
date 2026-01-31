# Central Coast Housing Market Wizard (MVP)

## Architecture diagram (text)

```
[Next.js UI]
    |  POST /value, GET /metrics, POST /train
    v
[FastAPI Service] ----> [Model Artifacts + Metrics JSON]
    |                           |
    | read/write                v
    |                    models/model.joblib
    |
    +--> [Optional Domain API Integration (stub)]
    |
    +--> [Postgres (sales data ingestion)]
```

## Repo file tree

```
.
├── README.md
├── docker-compose.yml
├── backend
│   ├── Dockerfile
│   ├── app
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── domain.py
│   │   ├── ingest.py
│   │   ├── main.py
│   │   ├── metrics_store.py
│   │   ├── ml.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── train.py
│   ├── data
│   │   └── schema.yaml
│   ├── models
│   ├── requirements.txt
│   └── scripts
│       ├── ingest_sales.py
│       └── seed_synthetic_data.py
└── frontend
    ├── Dockerfile
    ├── app
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── metrics
    │   │   └── page.tsx
    │   └── results
    │       └── page.tsx
    ├── components
    │   └── TierCard.tsx
    ├── lib
    │   └── api.ts
    ├── next-env.d.ts
    ├── next.config.mjs
    ├── package.json
    ├── postcss.config.js
    ├── styles
    │   └── globals.css
    ├── tailwind.config.ts
    └── tsconfig.json
```

## Local quickstart (thin-slice)

1) Start services:

```
docker compose up --build
```

2) Create synthetic data:

```
cd backend
python scripts/seed_synthetic_data.py --rows 500 --out ./data/synthetic_sales.csv
```

3) Train model:

```
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"data_path":"./data/synthetic_sales.csv"}'
```

4) Run a valuation (example input):

```
curl -X POST http://localhost:8000/value \
  -H "Content-Type: application/json" \
  -d '{
    "address":"10 Example St",
    "suburb":"Gosford",
    "beds":3,
    "baths":2,
    "parking":1,
    "land_size_sqm":560,
    "internal_size_sqm":170,
    "property_type":"house",
    "condition_tier":"Typical",
    "condition_checklist":{"renovated_kitchen":true,"renovated_bathrooms":false,"new_roof":false,"needs_structural_repairs":false,"landscaping_complete":true},
    "notable_features":["pool","solar"]
  }'
```

## Example runs (shape)

### Example 1: Typical

```
Input:
  suburb: Gosford
  beds: 3
  baths: 2
  land_size_sqm: 560

Output shape:
  tiers: [
    {tier, point_estimate, interval_50, interval_80},
    {tier, point_estimate, interval_50, interval_80},
    {tier, point_estimate, interval_50, interval_80}
  ]
  explanation: {top_drivers, comparable_sales, sensitivity, confidence_notes}
```

### Example 2: As-is

```
Input:
  suburb: Umina Beach
  beds: 2
  baths: 1
  land_size_sqm: 420
  condition_tier: As-is

Output shape:
  tiers: [ ... ]
  explanation: { ... }
```

## Data ingestion

- Bulk CSV ingestion is supported via `backend/scripts/ingest_sales.py` and a configurable schema in `backend/data/schema.yaml`.
- Domain API integration is stubbed in `backend/app/domain.py` and enabled when `DOMAIN_API_KEY` and `DOMAIN_ENABLED=true` are set.

## Model notes

- Base model: LightGBM regression on log price with winsorized targets.
- Intervals: quantile LightGBM at 10/90 (80% interval) and 25/75 (50% interval).
- Condition tiers: As-is discount, Typical base, Premium uplift; checklist applies multiplicative adjustments.
- Backtesting: time-aware split (earliest 80% train, latest 20% test).

## Guardrails

- Not financial advice.
- Data-source attribution included in API response.
- Uncertainty notes returned for each valuation.
