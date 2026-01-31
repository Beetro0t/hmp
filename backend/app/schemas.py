from typing import Any, Literal

from pydantic import BaseModel, Field


class ConditionChecklist(BaseModel):
    renovated_kitchen: bool = False
    renovated_bathrooms: bool = False
    new_roof: bool = False
    needs_structural_repairs: bool = False
    landscaping_complete: bool = False


class ValuationRequest(BaseModel):
    address: str
    suburb: str
    lat: float | None = None
    lon: float | None = None
    beds: int
    baths: int
    parking: int
    land_size_sqm: float
    internal_size_sqm: float | None = None
    property_type: Literal["house", "townhouse", "unit"]
    condition_tier: Literal["As-is", "Typical", "Premium"]
    condition_checklist: ConditionChecklist | None = None
    notable_features: list[str] = Field(default_factory=list)


class TierRange(BaseModel):
    tier: str
    point_estimate: float
    interval_50: list[float]
    interval_80: list[float]


class Explanation(BaseModel):
    top_drivers: list[str]
    comparable_sales: list[dict[str, Any]]
    sensitivity: list[str]
    confidence_notes: list[str]


class ValuationResponse(BaseModel):
    tiers: list[TierRange]
    explanation: Explanation
    disclaimer: str
    data_sources: list[str]


class TrainRequest(BaseModel):
    data_path: str


class TrainResponse(BaseModel):
    status: str
    rows_used: int
    metrics: dict[str, float]


class MetricsResponse(BaseModel):
    metrics: dict[str, float]
