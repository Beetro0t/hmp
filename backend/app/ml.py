from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import NearestNeighbors


@dataclass
class ModelArtifacts:
    point_model: LGBMRegressor
    q10_model: LGBMRegressor
    q90_model: LGBMRegressor
    q25_model: LGBMRegressor
    q75_model: LGBMRegressor
    suburb_encoding: dict[str, float]
    feature_columns: list[str]
    comp_features: np.ndarray
    comp_metadata: pd.DataFrame
    training_region: str


def _haversine_km(lat: pd.Series, lon: pd.Series, ref_lat: float, ref_lon: float) -> pd.Series:
    lat_rad = np.radians(lat.astype(float))
    lon_rad = np.radians(lon.astype(float))
    ref_lat_rad = np.radians(ref_lat)
    ref_lon_rad = np.radians(ref_lon)
    dlat = lat_rad - ref_lat_rad
    dlon = lon_rad - ref_lon_rad
    a = np.sin(dlat / 2) ** 2 + np.cos(lat_rad) * np.cos(ref_lat_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c


def _month_index(sale_date: pd.Series) -> pd.Series:
    return sale_date.dt.year * 12 + sale_date.dt.month


def _build_suburb_encoding(train_df: pd.DataFrame) -> dict[str, float]:
    suburb_stats = train_df.groupby("suburb")
    return (suburb_stats["price_log"].mean()).to_dict()


def _apply_suburb_encoding(df: pd.DataFrame, encoding: dict[str, float]) -> pd.Series:
    global_mean = np.mean(list(encoding.values())) if encoding else 0.0
    return df["suburb"].map(encoding).fillna(global_mean)


def _feature_frame(df: pd.DataFrame, suburb_encoding: dict[str, float]) -> pd.DataFrame:
    distance_to_coast = _haversine_km(df["lat"].fillna(-33.42), df["lon"].fillna(151.32), -33.42, 151.32)
    features = pd.DataFrame(
        {
            "beds": df["beds"],
            "baths": df["baths"],
            "parking": df["parking"],
            "land_size_sqm": df["land_size_sqm"],
            "internal_size_sqm": df["internal_size_sqm"].fillna(df["internal_size_sqm"].median()),
            "property_type_house": (df["property_type"] == "house").astype(int),
            "property_type_townhouse": (df["property_type"] == "townhouse").astype(int),
            "property_type_unit": (df["property_type"] == "unit").astype(int),
            "month_index": _month_index(df["sale_date"]),
            "month_sin": np.sin(2 * np.pi * df["sale_date"].dt.month / 12),
            "month_cos": np.cos(2 * np.pi * df["sale_date"].dt.month / 12),
            "suburb_encoded": _apply_suburb_encoding(df, suburb_encoding),
            "distance_to_coast_km": distance_to_coast,
            "has_pool": df["features"].str.contains("pool", na=False).astype(int),
            "has_solar": df["features"].str.contains("solar", na=False).astype(int),
            "has_view": df["features"].str.contains("view", na=False).astype(int),
            "has_waterfront": df["features"].str.contains("waterfront", na=False).astype(int),
            "has_granny_flat": df["features"].str.contains("granny", na=False).astype(int),
        }
    )
    features = features.replace([np.inf, -np.inf], np.nan)
    return features.fillna(0)


def _winsorize_prices(price_log: pd.Series, lower: float = 0.02, upper: float = 0.98) -> pd.Series:
    lower_q = price_log.quantile(lower)
    upper_q = price_log.quantile(upper)
    return price_log.clip(lower=lower_q, upper=upper_q)


def train_models(df: pd.DataFrame, region: str) -> tuple[ModelArtifacts, dict[str, float], int]:
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["price_log"] = np.log1p(df["price"])
    df["price_log"] = _winsorize_prices(df["price_log"])

    df = df.sort_values("sale_date")
    split_index = int(len(df) * 0.8)
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    suburb_encoding = _build_suburb_encoding(train_df)
    X_train = _feature_frame(train_df, suburb_encoding)
    X_test = _feature_frame(test_df, suburb_encoding)

    y_train = train_df["price_log"]
    y_test = test_df["price_log"]

    point_model = LGBMRegressor(
        n_estimators=250,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    point_model.fit(X_train, y_train)

    q10_model = LGBMRegressor(
        objective="quantile",
        alpha=0.1,
        n_estimators=250,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    q90_model = LGBMRegressor(
        objective="quantile",
        alpha=0.9,
        n_estimators=250,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    q25_model = LGBMRegressor(
        objective="quantile",
        alpha=0.25,
        n_estimators=250,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    q75_model = LGBMRegressor(
        objective="quantile",
        alpha=0.75,
        n_estimators=250,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )

    q10_model.fit(X_train, y_train)
    q90_model.fit(X_train, y_train)
    q25_model.fit(X_train, y_train)
    q75_model.fit(X_train, y_train)

    y_pred = point_model.predict(X_test)
    mae = mean_absolute_error(np.expm1(y_test), np.expm1(y_pred))
    mape = np.mean(np.abs(np.expm1(y_test) - np.expm1(y_pred)) / np.expm1(y_test))

    q10_pred = np.expm1(q10_model.predict(X_test))
    q90_pred = np.expm1(q90_model.predict(X_test))
    q25_pred = np.expm1(q25_model.predict(X_test))
    q75_pred = np.expm1(q75_model.predict(X_test))
    y_true = np.expm1(y_test)

    coverage_80 = np.mean((y_true >= q10_pred) & (y_true <= q90_pred))
    coverage_50 = np.mean((y_true >= q25_pred) & (y_true <= q75_pred))

    metrics = {
        "mae": float(mae),
        "mape": float(mape),
        "coverage_80": float(coverage_80),
        "coverage_50": float(coverage_50),
        "rows": int(len(df)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
    }

    comp_features = X_train.to_numpy()
    comp_metadata = train_df[["sale_id", "sale_date", "price", "suburb", "address"]].copy()

    artifacts = ModelArtifacts(
        point_model=point_model,
        q10_model=q10_model,
        q90_model=q90_model,
        q25_model=q25_model,
        q75_model=q75_model,
        suburb_encoding=suburb_encoding,
        feature_columns=list(X_train.columns),
        comp_features=comp_features,
        comp_metadata=comp_metadata,
        training_region=region,
    )

    return artifacts, metrics, len(df)


def save_artifacts(artifacts: ModelArtifacts, path: str) -> None:
    joblib.dump(artifacts, path)


def load_artifacts(path: str) -> ModelArtifacts:
    return joblib.load(path)


def _condition_multiplier(condition_tier: str, checklist: dict[str, bool] | None) -> float:
    base = {"As-is": 0.93, "Typical": 1.0, "Premium": 1.07}[condition_tier]
    if not checklist:
        return base
    adjustment = 1.0
    if checklist.get("renovated_kitchen"):
        adjustment *= 1.02
    if checklist.get("renovated_bathrooms"):
        adjustment *= 1.02
    if checklist.get("new_roof"):
        adjustment *= 1.01
    if checklist.get("needs_structural_repairs"):
        adjustment *= 0.95
    if checklist.get("landscaping_complete"):
        adjustment *= 1.01
    return base * adjustment


def predict_ranges(
    artifacts: ModelArtifacts,
    payload: dict[str, object],
) -> dict[str, dict[str, float]]:
    df = pd.DataFrame([payload])
    df["sale_date"] = pd.to_datetime(date.today())
    df["features"] = ",".join(payload.get("notable_features", []))
    features = _feature_frame(df, artifacts.suburb_encoding)

    point_log = artifacts.point_model.predict(features)[0]
    q10_log = artifacts.q10_model.predict(features)[0]
    q90_log = artifacts.q90_model.predict(features)[0]
    q25_log = artifacts.q25_model.predict(features)[0]
    q75_log = artifacts.q75_model.predict(features)[0]

    base_point = float(np.expm1(point_log))
    base_80 = [float(np.expm1(q10_log)), float(np.expm1(q90_log))]
    base_50 = [float(np.expm1(q25_log)), float(np.expm1(q75_log))]

    tiers = ["As-is", "Typical", "Premium"]

    results: dict[str, dict[str, float]] = {}
    for tier in tiers:
        adjustment = _condition_multiplier(tier, payload.get("condition_checklist"))
        results[tier] = {
            "point": base_point * adjustment,
            "low50": base_50[0] * adjustment,
            "high50": base_50[1] * adjustment,
            "low80": base_80[0] * adjustment,
            "high80": base_80[1] * adjustment,
        }

    return results


def find_comparables(artifacts: ModelArtifacts, payload: dict[str, object], k: int = 5) -> list[dict[str, object]]:
    df = pd.DataFrame([payload])
    df["sale_date"] = pd.to_datetime(date.today())
    df["features"] = ",".join(payload.get("notable_features", []))
    features = _feature_frame(df, artifacts.suburb_encoding)

    if artifacts.comp_features.size == 0:
        return []

    nn = NearestNeighbors(n_neighbors=min(k, len(artifacts.comp_features)))
    nn.fit(artifacts.comp_features)
    distances, indices = nn.kneighbors(features.to_numpy())

    comps = []
    for idx in indices[0]:
        row = artifacts.comp_metadata.iloc[idx]
        comps.append(
            {
                "sale_id": row["sale_id"],
                "sale_date": row["sale_date"].isoformat(),
                "price": float(row["price"]),
                "suburb": row["suburb"],
                "address": row["address"],
            }
        )
    return comps
